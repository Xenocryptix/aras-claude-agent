#!/usr/bin/env python3
"""
Aras Innovator MCP Server
Created by D. Theoden (www.arasdeveloper.com)
Date: June 12, 2025
"""

import asyncio
import json
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from .aras_client import ArasClient

server = Server("aras-mcp-server")
aras_client = ArasClient()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for Aras Innovator integration."""
    return [
        types.Tool(
            name="test_aras_connection",
            description="Test connection and authentication with Aras Innovator server",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="aras_get_item",
            description="GET operation - Retrieve items from Aras using OData API",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_type": {
                        "type": "string",
                        "description": "The item type to retrieve (e.g., aer_dcm_data, Part, Document)",
                    },
                    "expand": {
                        "type": "string",
                        "description": "Optional: OData $expand parameter for related data",
                    },
                    "filter": {
                        "type": "string", 
                        "description": "Optional: OData $filter parameter for filtering results",
                    },
                    "select": {
                        "type": "string",
                        "description": "Optional: OData $select parameter for specific fields",
                    }
                },
                "required": ["item_type"],
            },
        ),
        types.Tool(
            name="aras_create_item",
            description="POST operation - Create new items in Aras using OData API",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_type": {
                        "type": "string",
                        "description": "The item type to create (e.g., aer_dcm_data, Part, Document)",
                    },
                    "data": {
                        "type": "object",
                        "description": "The item data as JSON object",
                    }
                },
                "required": ["item_type", "data"],
            },
        ),
        types.Tool(
            name="aras_call_method",
            description="Call Aras server methods using OData API",
            inputSchema={
                "type": "object",
                "properties": {
                    "method_name": {
                        "type": "string",
                        "description": "The method name to call (e.g., aer_dcm_fetchBOMStructure, aer_dcm_createSuccessorEco)",
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
            name="aras_get_list",
            description="Get list items from Aras (e.g., dropdown values, document types)",
            inputSchema={
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "The list ID to retrieve values from",
                    },
                    "expand": {
                        "type": "string",
                        "description": "Optional: OData $expand parameter (e.g., 'Value' for list values)",
                    }
                },
                "required": ["list_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for Aras Innovator operations."""
    
    try:
        if name == "test_aras_connection":
            # Test authentication and get bearer token
            authenticated = aras_client.authenticate()
            if authenticated:
                return [types.TextContent(
                    type="text", 
                    text=f"✅ Successfully authenticated with Aras Innovator!\nBearer token obtained and ready for API calls.\nServer URL: {aras_client.url}"
                )]
            else:
                return [types.TextContent(
                    type="text", 
                    text="❌ Failed to authenticate with Aras Innovator. Please check your credentials."
                )]
        
        elif name == "aras_get_item":
            if not arguments or "item_type" not in arguments:
                raise ValueError("Item type is required")
            
            item_data = aras_client.get_items(
                arguments["item_type"],
                expand=arguments.get("expand"),
                filter_param=arguments.get("filter"),
                select=arguments.get("select")
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved {arguments['item_type']} items:\n{json.dumps(item_data, indent=2)}"
                )
            ]
        
        elif name == "aras_create_item":
            if not arguments or "item_type" not in arguments or "data" not in arguments:
                raise ValueError("Item type and data are required")
            
            result = aras_client.create_item(arguments["item_type"], arguments["data"])
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully created {arguments['item_type']}:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        elif name == "aras_call_method":
            if not arguments or "method_name" not in arguments or "data" not in arguments:
                raise ValueError("Method name and data are required")
            
            result = aras_client.call_method(arguments["method_name"], arguments["data"])
            return [
                types.TextContent(
                    type="text",
                    text=f"Method {arguments['method_name']} result:\n{json.dumps(result, indent=2)}"
                )
            ]
        
        elif name == "aras_get_list":
            if not arguments or "list_id" not in arguments:
                raise ValueError("List ID is required")
            
            list_data = aras_client.get_list(
                arguments["list_id"],
                expand=arguments.get("expand")
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"List {arguments['list_id']} data:\n{json.dumps(list_data, indent=2)}"
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

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aras-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 