#!/usr/bin/env python3
"""
Aras Innovator to Qdrant Vector Database Sync Service

This microservice syncs Part data from an Aras Innovator MCP API into a Qdrant vector database
using Google Gemini embeddings for semantic search capabilities.
"""

import os
import sys
import time
import json
import logging
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models

# MCP Client imports
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Part:
    """Data class for Part information"""
    id: str
    item_number: str
    name: str
    description: Optional[str] = None
    classification: Optional[str] = None
    make_buy: Optional[str] = None


class ArasQdrantSyncService:
    """Service to sync Aras Part data to Qdrant vector database"""
    
    def __init__(self):
        """Initialize the sync service with configuration from environment variables"""
        self.mcp_url = os.getenv('MCP_URL', 'https://appserver001.softwerk.digital/mcp')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        self.qdrant_collection = os.getenv('QDRANT_COLLECTION', 'aras_parts')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        # Validate required environment variables
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.embedding_model = "models/embedding-001"
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            host=self.qdrant_host,
            port=self.qdrant_port,
            api_key=self.qdrant_api_key,
            https=False  # Use HTTP since TLS is disabled
        )
        
        # Initialize MCP client (will be connected when needed)
        self.mcp_client = None
        
        logger.info(f"Initialized sync service:")
        logger.info(f"  MCP URL: {self.mcp_url}")
        logger.info(f"  Qdrant: {self.qdrant_host}:{self.qdrant_port}")
        logger.info(f"  Collection: {self.qdrant_collection}")
    
    async def connect_to_mcp(self):
        """Connect to the MCP server"""
        if self.mcp_client is None:
            try:
                logger.info(f"Connecting to MCP server: {self.mcp_url}")
                transport = StreamableHttpTransport(self.mcp_url)
                self.mcp_client = Client(transport=transport)
                await self.mcp_client.__aenter__()
                logger.info("Successfully connected to MCP server")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {e}")
                raise
    
    async def disconnect_from_mcp(self):
        """Disconnect from the MCP server"""
        if self.mcp_client is not None:
            try:
                await self.mcp_client.__aexit__(None, None, None)
                self.mcp_client = None
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.warning(f"Error disconnecting from MCP: {e}")
    
    async def fetch_parts_from_aras(self) -> List[Part]:
        """Fetch Part data from Aras Innovator via MCP API"""
        logger.info("Fetching parts from Aras Innovator...")
        
        await self.connect_to_mcp()
        
        try:
            # Use the MCP client to call the api_get_items tool
            result = await self.mcp_client.call_tool("api_get_items", {
                "endpoint": "Part",
                "select": "id,item_number,name,description,classification,make_buy"
            })
            
            # Extract text result from CallToolResult
            response_text = ""
            if hasattr(result, 'content') and result.content:
                # Handle list of content items
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        response_text += content_item.text
            elif hasattr(result, 'text'):
                response_text = result.text
            else:
                response_text = str(result)
            
            logger.debug(f"Raw MCP response: {response_text[:500]}...")
            
            # Look for JSON data in the response
            try:
                # Extract JSON from the text response
                # The response might contain text like "✅ Retrieved items from Part:\n{...}"
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    logger.debug(f"Extracted JSON: {json_text[:200]}...")
                    
                    data = json.loads(json_text)
                    
                    # Handle OData response format
                    if "value" in data:
                        results = data["value"]  # OData format
                    elif isinstance(data, list):
                        results = data
                    elif isinstance(data, dict) and "Results" in data:
                        results = data["Results"]  # MCP wrapper format
                    else:
                        results = [data] if data else []
                else:
                    # No JSON found, check for empty response indicators
                    if "no items found" in response_text.lower() or "[]" in response_text:
                        results = []
                    else:
                        raise ValueError(f"No valid JSON found in response")
                        
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Problematic text: {response_text[:500]}...")
                # Try to handle as empty result
                if "no items found" in response_text.lower():
                    results = []
                else:
                    raise ValueError(f"Cannot parse JSON response: {e}")
            
            parts = []
            for item in results:
                if isinstance(item, dict):
                    part = Part(
                        id=item.get('id', ''),
                        item_number=item.get('item_number', ''),
                        name=item.get('name', ''),
                        description=item.get('description', ''),
                        classification=item.get('classification', ''),
                        make_buy=item.get('make_buy', '')
                    )
                    parts.append(part)
            
            logger.info(f"Successfully fetched {len(parts)} parts from Aras")
            return parts
            
        except Exception as e:
            logger.error(f"Error fetching parts from Aras: {e}")
            raise
        finally:
            await self.disconnect_from_mcp()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google Gemini"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def create_part_text(self, part: Part) -> str:
        """Create text representation of a Part for embedding"""
        # Combine all non-empty fields into a single text string
        fields = [
            part.item_number,
            part.name,
            part.description or '',
            part.classification or '',
            part.make_buy or ''
        ]
        return ' '.join(field.strip() for field in fields if field and field.strip())
    
    def ensure_collection_exists(self):
        """Ensure the Qdrant collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.qdrant_collection not in collection_names:
                logger.info(f"Creating collection '{self.qdrant_collection}'...")
                
                # Get embedding dimension by generating a test embedding
                test_embedding = self.generate_embedding("test")
                vector_size = len(test_embedding)
                
                self.qdrant_client.create_collection(
                    collection_name=self.qdrant_collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection with vector size: {vector_size}")
            else:
                logger.info(f"Collection '{self.qdrant_collection}' already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def sync_parts_to_qdrant(self, parts: List[Part]):
        """Sync parts to Qdrant vector database"""
        logger.info(f"Syncing {len(parts)} parts to Qdrant...")
        
        points = []
        
        for i, part in enumerate(parts):
            try:
                # Generate text and embedding
                text = self.create_part_text(part)
                if not text.strip():
                    logger.warning(f"Skipping part {part.id} - no text content")
                    continue
                
                embedding = self.generate_embedding(text)
                
                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),  # Generate unique UUID for each point
                    vector=embedding,
                    payload={
                        "aras_id": part.id,
                        "item_number": part.item_number,
                        "name": part.name,
                        "description": part.description or "",
                        "classification": part.classification or "",
                        "make_buy": part.make_buy or "",
                        "text_content": text
                    }
                )
                points.append(point)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(parts)} parts...")
                    
            except Exception as e:
                logger.error(f"Error processing part {part.id}: {e}")
                continue
        
        if points:
            try:
                # Upsert points to Qdrant
                self.qdrant_client.upsert(
                    collection_name=self.qdrant_collection,
                    points=points
                )
                logger.info(f"Successfully synced {len(points)} parts to Qdrant")
            except Exception as e:
                logger.error(f"Error upserting points to Qdrant: {e}")
                raise
        else:
            logger.warning("No valid parts to sync")
    
    async def run_sync(self):
        """Run a complete sync cycle"""
        try:
            logger.info("Starting sync cycle...")
            
            # Ensure collection exists
            self.ensure_collection_exists()
            
            # Fetch parts from Aras
            parts = await self.fetch_parts_from_aras()
            
            if not parts:
                logger.warning("No parts fetched from Aras")
                return
            
            # Sync to Qdrant
            self.sync_parts_to_qdrant(parts)
            
            logger.info("Sync cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Sync cycle failed: {e}")
            raise
    
    async def run_continuous(self, interval_hours: int = 1):
        """Run continuous sync with specified interval"""
        logger.info(f"Starting continuous sync with {interval_hours} hour interval...")
        
        while True:
            try:
                await self.run_sync()
                sleep_seconds = interval_hours * 3600
                logger.info(f"Waiting {interval_hours} hour(s) before next sync...")
                await asyncio.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                break
            except Exception as e:
                logger.error(f"Error in continuous sync: {e}")
                # Wait before retrying
                await asyncio.sleep(300)  # Wait 5 minutes before retry


async def main():
    """Main entry point"""
    try:
        service = ArasQdrantSyncService()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
            # Run continuous sync
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            await service.run_continuous(interval_hours=interval)
        else:
            # Run one-time sync
            await service.run_sync()
            
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
