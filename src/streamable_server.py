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
import logging
import os
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from .api_client import APIClient
from .config import URL
from .sync_service import ArasQdrantSyncService

# Initialize FastMCP server for Aras API tools
# FastMCP 2.0 handles HTTP transport natively
mcp = FastMCP(
    name="aras-api-server",
    version="1.0.0",
    instructions="A Model Context Protocol server for Aras Innovator API integration"
)

# Global API client instance
api_client = APIClient()

# Global sync service instance (will be initialized if needed)
sync_service = None

def get_sync_service():
    """Get or initialize the sync service if environment variables are available."""
    global sync_service
    if sync_service is None:
        try:
            # Check if required environment variables are present
            if os.getenv('GEMINI_API_KEY') and os.getenv('QDRANT_HOST'):
                sync_service = ArasQdrantSyncService()
                logging.info("Sync service initialized - automatic Part syncing enabled")
            else:
                logging.info("Sync service not initialized - missing required environment variables (GEMINI_API_KEY, QDRANT_HOST)")
        except Exception as e:
            logging.warning(f"Failed to initialize sync service: {e}")
            sync_service = None
    return sync_service

async def trigger_part_sync_if_enabled():
    """Trigger Part sync to Qdrant if sync service is available."""
    service = get_sync_service()
    if service:
        try:
            logging.info("Triggering automatic Part sync to Qdrant...")
            await service.run_sync()
            logging.info("Part sync completed successfully")
        except Exception as e:
            logging.error(f"Failed to sync Parts to Qdrant: {e}")
    else:
        logging.debug("Sync service not available - skipping Part sync")

@mcp.tool()
async def get_sync_service_status() -> str:
    """Get the status of the Qdrant sync service and its configuration.
    
    This tool shows whether the sync service is available and configured properly.
    """
    service = get_sync_service()
    
    if not service:
        return """❌ Sync service not available.

            Required environment variables:
            - GEMINI_API_KEY: Google Gemini API key for embeddings
            - QDRANT_HOST: Qdrant vector database host
            - QDRANT_PORT: Qdrant port (optional, defaults to 6333)
            - QDRANT_COLLECTION: Collection name (optional, defaults to 'aras_parts')
            - QDRANT_API_KEY: Qdrant API key (optional)"""
    
    try:
        # Test Qdrant connection
        collections = service.qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        status = f"""✅ Sync service is available and configured.

            Configuration:
            - Qdrant Host: {service.qdrant_host}:{service.qdrant_port}
            - Collection: {service.qdrant_collection}
            - Embedding Model: {service.embedding_model}

            Qdrant Status:
            - Connection: ✅ Connected
            - Available Collections: {', '.join(collection_names)}
            - Target Collection Exists: {'✅ Yes' if service.qdrant_collection in collection_names else '❌ No (will be created on first sync)'}

            Note: Parts are automatically synced to Qdrant when created or updated."""
        
        return status
        
    except Exception as e:
        return f"""⚠️ Sync service configured but Qdrant connection failed.

            Configuration:
            - Qdrant Host: {service.qdrant_host}:{service.qdrant_port}
            - Collection: {service.qdrant_collection}

            Error: {str(e)}

            Please check Qdrant server status and network connectivity."""

@mcp.tool()
async def sync_parts_to_qdrant() -> str:
    """Manually trigger sync of Part data from Aras Innovator to Qdrant vector database.
    
    This tool syncs all Part items from Aras to Qdrant for semantic search capabilities.
    Requires GEMINI_API_KEY and QDRANT_HOST environment variables to be configured.
    """
    service = get_sync_service()
    if not service:
        return "❌ Sync service not available. Please ensure GEMINI_API_KEY and QDRANT_HOST environment variables are set."
    
    try:
        await service.run_sync()
        return "✅ Successfully synced Part data to Qdrant vector database. Parts are now available for semantic search."
    except Exception as error:
        logging.error(f"Manual sync failed: {error}")
        return f"❌ Failed to sync Parts to Qdrant: {str(error)}"

@mcp.tool()
async def test_api_connection() -> str:
    """Test connection and authentication with Aras Innovator API server."""
    try:
        authenticated = api_client.authenticate()
        if authenticated:
            logging.info("API connection test successful")
            return f"✅ Successfully authenticated with Aras API!\nBearer token obtained and ready for API calls.\nServer URL: {api_client.url}"
        else:
            logging.warning("API connection test failed - authentication unsuccessful")
            return "❌ Failed to authenticate with Aras API. Please check your credentials."
    except Exception as error:
        logging.error(f"API connection test failed with exception: {error}")
        return f"❌ Authentication error: {str(error)}"

@mcp.tool()
async def reauthenticate_api() -> str:
    """Force reauthentication with the Aras Innovator API server.
    
    This tool is useful when your current token has expired or become invalid.
    It will get a fresh bearer token and update the API client.
    """
    try:
        # Check current token status first
        token_status = "valid" if api_client.is_token_valid() else "invalid/expired"
        
        # Force reauthentication
        success = api_client.reauthenticate()
        if success:
            logging.info("Manual reauthentication successful")
            return f"✅ Successfully reauthenticated with Aras API!\nPrevious token status: {token_status}\nNew bearer token obtained and ready for API calls.\nServer URL: {api_client.url}"
        else:
            logging.warning("Manual reauthentication failed")
            return "❌ Failed to reauthenticate with Aras API. Please check your credentials and server connectivity."
    except Exception as error:
        logging.error(f"Manual reauthentication failed with exception: {error}")
        return f"❌ Reauthentication error: {str(error)}"

@mcp.tool()
async def check_token_status() -> str:
    """Check the current authentication token status and validity.
    
    This tool helps diagnose authentication issues by testing if the current token
    is still valid without making any changes.
    """
    try:
        if not api_client.token:
            return "❌ No authentication token present. Use test_api_connection or reauthenticate_api to get a token."
        
        is_valid = api_client.is_token_valid()
        if is_valid:
            return f"✅ Current authentication token is valid.\nServer URL: {api_client.url}\nToken present and working correctly."
        else:
            return f"❌ Current authentication token is invalid or expired.\nServer URL: {api_client.url}\nUse reauthenticate_api to get a fresh token."
    except Exception as error:
        logging.error(f"Token status check failed with exception: {error}")
        return f"❌ Error checking token status: {str(error)}"

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
        
        # Trigger Part sync if this is a Part creation
        if endpoint.lower() == 'part':
            await trigger_part_sync_if_enabled()
        
        return f"✅ Successfully created item at {endpoint}:\n{json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error creating item at {endpoint}: {str(error)}"

@mcp.tool()
async def api_update_item(item_type: str, item_id: str, data: Dict[str, Any]) -> str:
    """PATCH operation - Update an existing item using Aras API.
    
    Args:
        item_type: The ItemType to update (e.g., 'Part', 'Document')
        item_id: The ID of the item to update
        data: The updated item data as JSON object (only include fields to be changed)
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        # Get the latest ID for the item using its config_id
        latest_id = api_client.get_latest_item(item_type, item_id)
        logging.info(f"Resolved config_id '{item_id}' to latest ID: {latest_id}")
        
        result = api_client.update_item(item_type, latest_id, data)
        
        # Trigger Part sync if this is a Part update
        if item_type.lower() == 'part':
            await trigger_part_sync_if_enabled()
        
        return f"✅ Successfully updated item {latest_id} (latest for config_id: {item_id}) at {item_type}:\n{json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error updating item {item_id} at {item_type}: {str(error)}"

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
    source_item_type: str,
    related_item_type: str,
    relationship_type: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Create a relationship between two items in Aras.
    
    Args:
        source_item_id: The ID of the source item
        related_item_id: The ID of the related/target item
        source_item_type: The ItemType for the source item (e.g., 'Part', 'Document')
        related_item_type: The ItemType for the related item (e.g., 'Part', 'Document')
        relationship_type: The relationship ItemType (e.g., 'Part BOM', 'Document File', 'Part Supersedure')
        data: Optional additional relationship properties (quantity, sort_order, etc.)
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        # Always get latest IDs for both source and related items
        final_source_id = api_client.get_latest_item(source_item_type, source_item_id)
        logging.info(f"Resolved source config_id '{source_item_id}' to latest ID: {final_source_id}")
        
        final_related_id = api_client.get_latest_item(related_item_type, related_item_id)
        logging.info(f"Resolved related config_id '{related_item_id}' to latest ID: {final_related_id}")
        
        result = api_client.create_relationship(final_source_id, final_related_id, relationship_type, data)
        
        relationship_info = f"✅ Successfully created {relationship_type} relationship:\n"
        relationship_info += f"Source: {final_source_id} (latest for config_id: {source_item_id})\n"
        relationship_info += f"Target: {final_related_id} (latest for config_id: {related_item_id})\n"
        relationship_info += f"Result: {json.dumps(result, indent=2)}"
        
        return relationship_info
    
    except Exception as error:
        return f"❌ Error creating relationship: {str(error)}"

@mcp.tool()
async def api_delete_relationship(relationship_type: str, relationship_id: str) -> str:
    """Delete a relationship between two items in Aras.
    
    Args:
        relationship_type: The relationship ItemType (e.g., 'Part BOM', 'Document File', 'Part Supersedure')
        relationship_id: The ID of the specific relationship record to delete
    """
    try:
        if not api_client.token:
            authenticated = api_client.authenticate()
            if not authenticated:
                return "❌ Failed to authenticate with Aras API."
        
        result = api_client.delete_relationship(relationship_type, relationship_id)
        return f"✅ Successfully deleted {relationship_type} relationship with ID: {relationship_id}\nResult: {json.dumps(result, indent=2)}"
    
    except Exception as error:
        return f"❌ Error deleting relationship: {str(error)}"

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

# Add health check endpoint using FastMCP's custom routes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for the Aras MCP server."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "service": "aras-mcp-streamable-server",
        "version": "1.0.0",
        "aras_server": URL
    })

# Add server status endpoint
@mcp.custom_route("/status", methods=["GET"])
async def server_status(request):
    """Get detailed server status including Aras connection status."""
    from starlette.responses import JSONResponse
    try:
        # Test authentication without storing token
        test_client = APIClient()
        auth_status = test_client.authenticate()
        
        # Check sync service status
        service = get_sync_service()
        sync_status = "not_configured"
        qdrant_status = "unknown"
        
        if service:
            try:
                collections = service.qdrant_client.get_collections()
                sync_status = "available"
                qdrant_status = "connected"
            except Exception:
                sync_status = "configured_but_failed"
                qdrant_status = "connection_failed"
        
        return JSONResponse({
            "service": "aras-mcp-streamable-server",
            "version": "1.0.0",
            "aras_server": URL,
            "authentication": "connected" if auth_status else "failed",
            "sync_service": {
                "status": sync_status,
                "qdrant_connection": qdrant_status,
                "auto_sync_enabled": service is not None
            },
            "available_tools": [
                "test_api_connection",
                "api_get_items", 
                "api_create_item",
                "api_update_item",
                "api_call_method",
                "api_get_list",
                "api_create_relationship",
                "api_delete_relationship",
                "api_upload_file (placeholder)",
                "api_create_document_with_file (placeholder)",
                "sync_parts_to_qdrant",
                "get_sync_service_status"
            ]
        })
    except Exception as error:
        return JSONResponse({
            "service": "aras-mcp-streamable-server",
            "version": "1.0.0",
            "aras_server": URL,
            "authentication": "error",
            "error": str(error)
        })

def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Run Aras MCP Streamable HTTP Server")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8123)), help="Localhost port to listen on")
    parser.add_argument("--host", type=str, default=os.getenv("HOST", "localhost"), help="Host to bind to")
    parser.add_argument("--log-level", type=str, default=os.getenv("LOG_LEVEL", "info"), 
                       choices=["debug", "info", "warning", "error"], help="Log level")
    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    print(f"🚀 Starting Aras MCP Streamable HTTP Server")
    print(f"📡 Aras Server: {URL}")
    print(f"🔧 Available tools: 12 (10 active + 2 placeholders)")
    print(f"🔄 Sync Service: {'Enabled' if get_sync_service() else 'Disabled'} (automatic Part syncing)")
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print(f"📋 Health check: http://{args.host}:{args.port}/health")
    print(f"📊 Status: http://{args.host}:{args.port}/status")
    print(f"🔗 MCP Endpoint: http://{args.host}:{args.port}/mcp")

    # Log server startup
    logging.info(f"Starting Aras MCP Streamable HTTP Server on {args.host}:{args.port}")
    logging.info(f"Aras Server URL: {URL}")
    logging.info(f"Log level set to: {args.log_level.upper()}")

    # Run using FastMCP 2.0's native HTTP transport
    mcp.run(
        transport="http",
        host=args.host,
        port=args.port,
        log_level=args.log_level.lower(),
        path="/mcp"
    )

if __name__ == "__main__":
    main()
