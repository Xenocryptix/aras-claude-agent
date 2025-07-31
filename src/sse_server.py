#!/usr/bin/env python3
"""
SSE-based MCP Server for Aras Innovator
Created by D. Theoden
Date: July 31, 2025
"""

import asyncio
import json
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn
import argparse
from .api_client import APIClient

# Initialize the MCP server
server = Server("aras-mcp-server")
api_client = APIClient()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for Aras Innovator API integration."""
    return [
        types.Tool(
            name="test_api_connection",
            description="Test connection and authentication with Aras Innovator server",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="api_get_items",
            description="GET operation - Retrieve items from Aras Innovator API",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "The API endpoint to retrieve data from (e.g., 'Part', 'Document')",
                    },
                    "expand": {
                        "type": "string",
                        "description": "Optional: expand parameter for related data",
                    },
                    "filter": {
                        "type": "string", 
                        "description": "Optional: filter parameter for filtering results",
                    },
                    "select": {
                        "type": "string",
                        "description": "Optional: select parameter for specific fields",
                    }
                },
                "required": ["endpoint"],
            },
        ),
        types.Tool(
            name="api_create_item",
            description="POST operation - Create new items using Aras Innovator API",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "The API endpoint to create data at (e.g., 'Part', 'Document')",
                    },
                    "data": {
                        "type": "object",
                        "description": "The item data as JSON object",
                    }
                },
                "required": ["endpoint", "data"],
            },
        ),
        types.Tool(
            name="api_call_method",
            description="Call Aras Innovator server methods",
            inputSchema={
                "type": "object",
                "properties": {
                    "method_name": {
                        "type": "string",
                        "description": "The method name to call",
                    },
                    "data": {
                        "type": "object",
                        "description": "The method parameters as JSON object",
                    }
                },
                "required": ["method_name", "data"],
            },
        ),
        types.Tool(
            name="api_get_list",
            description="Get list items from Aras Innovator API",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "The list ID to retrieve values from",
                    },
                    "expand": {
                        "type": "string",
                        "description": "Optional: expand parameter for list values",
                    }
                },
                "required": ["list_id"],
            },
        ),
        types.Tool(
            name="api_upload_file",
            description="Upload a file to the Aras Innovator database",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to upload",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional: custom filename for the uploaded file (if not provided, uses the original filename)",
                    }
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="api_create_document_with_file",
            description="Create a Document item, upload a file, and link them together with 'Document File' relationship",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_data": {
                        "type": "object",
                        "description": "Document item data (item_number, name, description, etc.)",
                        "properties": {
                            "item_number": {
                                "type": "string",
                                "description": "Document number",
                            },
                            "name": {
                                "type": "string",
                                "description": "Document name",
                            },
                            "description": {
                                "type": "string",
                                "description": "Document description",
                            },
                            "state": {
                                "type": "string",
                                "description": "Document state (e.g., 'In Work', 'Released')",
                            }
                        },
                        "required": ["name"],
                    },
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to upload",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional: custom filename for the uploaded file",
                    }
                },
                "required": ["document_data", "file_path"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for Aras Innovator API operations."""
    
    try:
        if name == "test_api_connection":
            # Test authentication and get bearer token
            authenticated = api_client.authenticate()
            if authenticated:
                return [types.TextContent(
                    type="text", 
                    text=f"✅ Successfully authenticated with Aras Innovator!\nBearer token obtained and ready for API calls.\nServer URL: {api_client.url}"
                )]
            else:
                return [types.TextContent(
                    type="text", 
                    text="❌ Failed to authenticate with Aras Innovator. Please check your credentials."
                )]
        
        elif name == "api_get_items":
            if not arguments or "endpoint" not in arguments:
                raise ValueError("Endpoint is required")
            
            item_data = api_client.get_items(
                arguments["endpoint"],
                expand=arguments.get("expand"),
                filter_param=arguments.get("filter"),
                select=arguments.get("select")
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved items from {arguments['endpoint']}:\n{json.dumps(item_data, indent=2)}"
                )
            ]
        
        elif name == "api_create_item":
            if not arguments or "endpoint" not in arguments or "data" not in arguments:
                raise ValueError("Endpoint and data are required")
            
            result = api_client.create_item(arguments["endpoint"], arguments["data"])
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully created item at {arguments['endpoint']}:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        elif name == "api_call_method":
            if not arguments or "method_name" not in arguments or "data" not in arguments:
                raise ValueError("Method name and data are required")
            
            result = api_client.call_method(arguments["method_name"], arguments["data"])
            return [
                types.TextContent(
                    type="text",
                    text=f"Method {arguments['method_name']} result:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        elif name == "api_get_list":
            if not arguments or "list_id" not in arguments:
                raise ValueError("List ID is required")
            
            list_data = api_client.get_list(
                arguments["list_id"],
                expand=arguments.get("expand")
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"List {arguments['list_id']} data:\n{json.dumps(list_data, indent=2)}"
                )
            ]
        
        elif name == "api_upload_file":
            if not arguments or "file_path" not in arguments:
                raise ValueError("File path is required")
            
            # Note: This would need to be implemented in api_client.py
            result = {"message": "File upload functionality needs to be implemented in api_client.py"}
            return [
                types.TextContent(
                    type="text",
                    text=f"File upload result:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        elif name == "api_create_document_with_file":
            if not arguments or "document_data" not in arguments or "file_path" not in arguments:
                raise ValueError("Document data and file path are required")
            
            # Note: This would need to be implemented as a combined operation in api_client.py
            result = {"message": "Document with file creation functionality needs to be implemented in api_client.py"}
            return [
                types.TextContent(
                    type="text",
                    text=f"Document with file creation result:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as error:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(error)}"
            )
        ]

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def main():
    """Main entry point for the SSE server."""
    parser = argparse.ArgumentParser(description='Run Aras MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    print(f"Starting Aras MCP SSE Server on {args.host}:{args.port}")
    print(f"SSE endpoint: http://{args.host}:{args.port}/sse")
    
    # Create Starlette app with SSE support
    starlette_app = create_starlette_app(server, debug=args.debug)

    # Run the server
    uvicorn.run(starlette_app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
