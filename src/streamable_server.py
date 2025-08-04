#!/usr/bin/env python3
"""
Aras MCP Streamable HTTP Server
A Model Context Protocol HTTP Streamable server for integrating Aras Innovator API with Claude Desktop.

Created by D. Theoden
Date: August 4, 2025

Based on the original Aras MCP server and the mcp-streamable-http example.
Learn more about Aras development at: https://www.arasdeveloper.com
"""

import argparse
import asyncio
import json
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from mcp.server.fastmcp import FastMCP
from .api_client import APIClient
from .config import URL

# Initialize FastMCP server for Aras API tools
# json_response=False enables Server-Sent Events streaming
# stateless_http=False enables session management for better performance
mcp = FastMCP(name="aras-api-server", json_response=False, stateless_http=False)

# Global API client instance
api_client = APIClient()

@mcp.tool()
async def test_api_connection() -> str:
    """Test connection and authentication with Aras Innovator API server."""
    try:
        authenticated = api_client.authenticate()
        if authenticated:
            return f"✅ Successfully authenticated with Aras API!\nBearer token obtained and ready for API calls.\nServer URL: {api_client.url}"
        else:
            return "❌ Failed to authenticate with Aras API. Please check your credentials."
    except Exception as error:
        return f"❌ Authentication error: {str(error)}"

@mcp.tool()
async def api_get_items(
    endpoint: str,
    expand: Optional[str] = None,
    filter: Optional[str] = None,
    select: Optional[str] = None
) -> str:
    """GET operation - Retrieve items from Aras API using OData.
    
    Args:
        endpoint: The API endpoint/ItemType to retrieve data from (e.g., 'Part', 'Document', 'User')
        expand: Optional expand parameter for related data
        filter: Optional filter parameter for filtering results (OData $filter syntax)
        select: Optional select parameter for specific fields
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        item_data = api_client.get_items(
            endpoint,
            expand=expand,
            filter_param=filter,
            select=select
        )
        return f"✅ Retrieved items from {endpoint}:\n{json.dumps(item_data, indent=2)}"
    
    except Exception as error:
        return f"❌ Error retrieving items from {endpoint}: {str(error)}"

@mcp.tool()
async def api_create_item(endpoint: str, data: Dict[str, Any]) -> str:
    """POST operation - Create new items using Aras API.
    
    Args:
        endpoint: The API endpoint/ItemType to create data at (e.g., 'Part', 'Document')
        data: The item data as JSON object
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        result = api_client.create_item(endpoint, data)
        return f"✅ Successfully created item at {endpoint}:\n{json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error creating item at {endpoint}: {str(error)}"

@mcp.tool()
async def api_call_method(method_name: str, data: Dict[str, Any]) -> str:
    """Call Aras API server methods.
    
    Args:
        method_name: The method name to call
        data: The method parameters as JSON object
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        result = api_client.call_method(method_name, data)
        return f"✅ Method {method_name} result:\n{json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error calling method {method_name}: {str(error)}"

@mcp.tool()
async def api_get_list(list_id: str, expand: Optional[str] = None) -> str:
    """Get list items from Aras API.
    
    Args:
        list_id: The list ID to retrieve values from
        expand: Optional expand parameter for list values
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        list_data = api_client.get_list(list_id, expand=expand)
        return f"✅ List {list_id} data:\n{json.dumps(list_data, indent=2)}"
    
    except Exception as error:
        return f"❌ Error retrieving list {list_id}: {str(error)}"

@mcp.tool()
async def api_create_relationship(
    source_item_id: str,
    related_item_id: str, 
    relationship_type: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Create a relationship between two items in Aras.
    
    Args:
        source_item_id: The ID of the source item
        related_item_id: The ID of the related/target item
        relationship_type: The relationship ItemType (e.g., 'Part BOM', 'Document File', 'Part Supersedure')
        data: Optional additional relationship properties (quantity, sort_order, etc.)
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        result = api_client.create_relationship(source_item_id, related_item_id, relationship_type, data)
        return f"✅ Successfully created {relationship_type} relationship:\nSource: {source_item_id}\nTarget: {related_item_id}\nResult: {json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error creating relationship: {str(error)}"

@mcp.tool()
async def api_upload_file(file_path: str, filename: Optional[str] = None) -> str:
    """Upload a file to the Aras Innovator database.
    
    Args:
        file_path: The absolute path to the file to upload
        filename: Optional custom filename for the uploaded file
    """
    return "❌ File upload functionality not yet implemented in the base API client. This tool is reserved for future implementation."

@mcp.tool()
async def api_create_document_with_file(
    document_data: Dict[str, Any],
    file_path: str,
    filename: Optional[str] = None
) -> str:
    """Create a Document item, upload a file, and link them together with 'Document File' relationship.
    
    Args:
        document_data: Document item data (item_number, name, description, etc.)
        file_path: The absolute path to the file to upload
        filename: Optional custom filename for the uploaded file
    """
    return "❌ Document with file creation functionality not yet implemented in the base API client. This tool is reserved for future implementation."

# Health check endpoint
@mcp.get("/health")
async def health_check():
    """Health check endpoint for the Aras MCP server."""
    return {
        "status": "healthy",
        "service": "aras-mcp-streamable-server",
        "version": "1.0.0",
        "aras_server": URL
    }

# Server status endpoint
@mcp.get("/status")
async def server_status():
    """Get detailed server status including Aras connection status."""
    try:
        # Test authentication without storing token
        test_client = APIClient()
        auth_status = test_client.authenticate()
        
        return {
            "service": "aras-mcp-streamable-server",
            "version": "1.0.0",
            "aras_server": URL,
            "authentication": "connected" if auth_status else "failed",
            "available_tools": [
                "test_api_connection",
                "api_get_items", 
                "api_create_item",
                "api_call_method",
                "api_get_list",
                "api_create_relationship",
                "api_upload_file (placeholder)",
                "api_create_document_with_file (placeholder)"
            ]
        }
    except Exception as error:
        return {
            "service": "aras-mcp-streamable-server",
            "version": "1.0.0",
            "aras_server": URL,
            "authentication": "error",
            "error": str(error)
        }

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan manager."""
        print(f"🚀 Starting Aras MCP Streamable HTTP Server")
        print(f"📡 Aras Server: {URL}")
        print(f"🔧 Available tools: 8 (6 active + 2 placeholders)")
        yield
        print("🛑 Shutting down Aras MCP Streamable HTTP Server")
    
    # Create FastAPI app with the MCP streamable HTTP application
    app = FastAPI(
        title="Aras MCP Streamable HTTP Server",
        description="A Model Context Protocol HTTP Streamable server for Aras Innovator API integration",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Mount the MCP streamable HTTP app at the root
    app.mount("/", mcp.streamable_http_app)
    
    return app

def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Run Aras MCP Streamable HTTP Server")
    parser.add_argument("--port", type=int, default=8123, help="Localhost port to listen on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    # Create the FastAPI app
    app = create_app()
    
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print(f"📋 Health check: http://{args.host}:{args.port}/health")
    print(f"📊 Status: http://{args.host}:{args.port}/status")
    print(f"🔗 MCP Endpoint: http://{args.host}:{args.port}/mcp")

    # Start the server with Streamable HTTP transport
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
