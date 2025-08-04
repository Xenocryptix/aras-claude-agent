#!/usr/bin/env python3
"""
Aras MCP Streamable HTTP Client
A Model Context Protocol HTTP Streamable client for interacting with Aras Innovator API.

Created by D. Theoden  
Date: August 4, 2025

Based on the original Aras MCP server and the mcp-streamable-http example.
Learn more about Aras development at: https://www.arasdeveloper.com
"""

import argparse
import asyncio
import json
from typing import Optional, Dict, Any, List
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Optional: Anthropic integration for AI-powered queries
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not available. Install with: pip install anthropic")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available. Install with: pip install python-dotenv")

class ArasMCPClient:
    """MCP Client for interacting with Aras MCP Streamable HTTP server."""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize the Aras MCP client.
        
        Args:
            anthropic_api_key: Optional Anthropic API key for AI-powered queries
        """
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._session_context = None
        self._streams_context = None
        
        # Initialize Anthropic client if available and API key provided
        self.anthropic = None
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            self.anthropic = Anthropic(api_key=anthropic_api_key)
            print("🤖 Anthropic AI integration enabled")

    async def connect_to_server(
        self, server_url: str, headers: Optional[Dict[str, str]] = None
    ) -> None:
        """Connect to an Aras MCP server running with HTTP Streamable transport.
        
        Args:
            server_url: The MCP server URL (e.g., http://localhost:8123/mcp)
            headers: Optional HTTP headers to include in requests
        """
        try:
            print(f"🔗 Connecting to Aras MCP server: {server_url}")
            
            self._streams_context = streamablehttp_client(
                url=server_url,
                headers=headers or {},
            )
            read_stream, write_stream, _ = await self._streams_context.__aenter__()

            self._session_context = ClientSession(read_stream, write_stream)
            self.session: ClientSession = await self._session_context.__aenter__()

            await self.session.initialize()
            print("✅ Successfully connected to Aras MCP server")
            
            # List available tools
            tools_response = await self.session.list_tools()
            available_tools = [tool.name for tool in tools_response.tools]
            print(f"🔧 Available tools: {', '.join(available_tools)}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Aras MCP server: {e}")
            raise

    async def test_connection(self) -> str:
        """Test the connection to the Aras server."""
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            result = await self.session.call_tool("test_api_connection", {})
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Connection test failed: {e}"

    async def get_items(
        self,
        endpoint: str,
        expand: Optional[str] = None,
        filter_param: Optional[str] = None,
        select: Optional[str] = None
    ) -> str:
        """Retrieve items from Aras API using OData.
        
        Args:
            endpoint: The API endpoint/ItemType (e.g., 'Part', 'Document', 'User')
            expand: Optional expand parameter for related data
            filter_param: Optional filter parameter (OData $filter syntax)
            select: Optional select parameter for specific fields
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            args = {"endpoint": endpoint}
            if expand:
                args["expand"] = expand
            if filter_param:
                args["filter"] = filter_param
            if select:
                args["select"] = select
                
            result = await self.session.call_tool("api_get_items", args)
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error getting items: {e}"

    async def create_item(self, endpoint: str, data: Dict[str, Any]) -> str:
        """Create a new item in Aras.
        
        Args:
            endpoint: The API endpoint/ItemType (e.g., 'Part', 'Document')
            data: The item data as dictionary
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            result = await self.session.call_tool("api_create_item", {
                "endpoint": endpoint,
                "data": data
            })
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error creating item: {e}"

    async def call_method(self, method_name: str, data: Dict[str, Any]) -> str:
        """Call an Aras server method.
        
        Args:
            method_name: The method name to call
            data: The method parameters
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            result = await self.session.call_tool("api_call_method", {
                "method_name": method_name,
                "data": data
            })
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error calling method: {e}"

    async def get_list(self, list_id: str, expand: Optional[str] = None) -> str:
        """Get list items from Aras.
        
        Args:
            list_id: The list ID to retrieve
            expand: Optional expand parameter
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            args = {"list_id": list_id}
            if expand:
                args["expand"] = expand
                
            result = await self.session.call_tool("api_get_list", args)
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error getting list: {e}"

    async def create_relationship(
        self,
        source_item_id: str,
        related_item_id: str,
        relationship_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a relationship between two items in Aras.
        
        Args:
            source_item_id: The ID of the source item
            related_item_id: The ID of the related/target item  
            relationship_type: The relationship ItemType (e.g., 'Part BOM', 'Document File')
            data: Optional additional relationship properties
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            args = {
                "source_item_id": source_item_id,
                "related_item_id": related_item_id,
                "relationship_type": relationship_type
            }
            if data:
                args["data"] = data
                
            result = await self.session.call_tool("api_create_relationship", args)
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error creating relationship: {e}"

    async def upload_file(self, file_path: str, filename: Optional[str] = None) -> str:
        """Upload a file to Aras (placeholder - not yet implemented).
        
        Args:
            file_path: Path to the file to upload
            filename: Optional custom filename
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            args = {"file_path": file_path}
            if filename:
                args["filename"] = filename
                
            result = await self.session.call_tool("api_upload_file", args)
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error uploading file: {e}"

    async def create_document_with_file(
        self,
        document_data: Dict[str, Any],
        file_path: str,
        filename: Optional[str] = None
    ) -> str:
        """Create a document and upload an associated file (placeholder - not yet implemented).
        
        Args:
            document_data: Document metadata
            file_path: Path to the file to upload
            filename: Optional custom filename
        """
        if not self.session:
            return "❌ Not connected to MCP server"
        
        try:
            args = {
                "document_data": document_data,
                "file_path": file_path
            }
            if filename:
                args["filename"] = filename
                
            result = await self.session.call_tool("api_create_document_with_file", args)
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            return f"❌ Error creating document with file: {e}"

    async def process_ai_query(self, query: str) -> str:
        """Process a query using Claude AI and available Aras tools.
        
        Args:
            query: The user's natural language query
        """
        if not self.anthropic:
            return "❌ Anthropic AI not available. Set ANTHROPIC_API_KEY environment variable."
        
        if not self.session:
            return "❌ Not connected to MCP server"

        try:
            # Get available tools
            tools_response = await self.session.list_tools()
            available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in tools_response.tools
            ]

            messages = [{"role": "user", "content": query}]

            # Initial Claude API call
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=messages,
                tools=available_tools,
            )

            # Process response and handle tool calls
            final_text = []

            for content in response.content:
                if content.type == "text":
                    final_text.append(content.text)
                elif content.type == "tool_use":
                    tool_name = content.name
                    tool_args = content.input

                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                    # Continue conversation with tool results  
                    if hasattr(content, "text") and content.text:
                        messages.append({"role": "assistant", "content": content.text})
                    messages.append({"role": "user", "content": result.content[0].text})

                    # Get next response from Claude
                    response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=messages,
                    )

                    final_text.append(response.content[0].text)

            return "\n".join(final_text)

        except Exception as e:
            return f"❌ Error processing AI query: {e}"

    async def interactive_mode(self) -> None:
        """Run an interactive command-line interface."""
        print("\n🎯 Aras MCP Client - Interactive Mode")
        print("Commands:")
        print("  test           - Test connection to Aras server")
        print("  get <endpoint> - Get items from endpoint (e.g., 'get Part')")
        print("  list <id>      - Get list by ID")
        print("  relate <src_id> <target_id> <type> - Create relationship between items")
        print("  ai <query>     - Process query with AI (requires Anthropic API key)")
        print("  help           - Show this help")
        print("  quit           - Exit")
        print()

        while True:
            try:
                command = input("aras-mcp> ").strip()

                if command.lower() in ["quit", "exit", "q"]:
                    break
                elif command.lower() == "help":
                    print("Available commands: test, get, list, relate, ai, help, quit")
                elif command.lower() == "test":
                    response = await self.test_connection()
                    print(response)
                elif command.startswith("get "):
                    endpoint = command[4:].strip()
                    if endpoint:
                        response = await self.get_items(endpoint)
                        print(response)
                    else:
                        print("❌ Usage: get <endpoint>")
                elif command.startswith("list "):
                    list_id = command[5:].strip()
                    if list_id:
                        response = await self.get_list(list_id)
                        print(response)
                    else:
                        print("❌ Usage: list <list_id>")
                elif command.startswith("relate "):
                    parts = command[7:].strip().split()
                    if len(parts) >= 3:
                        source_id, target_id, rel_type = parts[0], parts[1], parts[2]
                        response = await self.create_relationship(source_id, target_id, rel_type)
                        print(response)
                    else:
                        print("❌ Usage: relate <source_id> <target_id> <relationship_type>")
                        print("   Example: relate ABC123 DEF456 'Part BOM'")
                elif command.startswith("ai "):
                    query = command[3:].strip()
                    if query:
                        print("🤖 Processing with AI...")
                        response = await self.process_ai_query(query)
                        print(response)
                    else:
                        print("❌ Usage: ai <your question>")
                elif command:
                    print(f"❌ Unknown command: {command}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def cleanup(self) -> None:
        """Properly clean up the session and streams."""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
            if self._streams_context:
                await self._streams_context.__aexit__(None, None, None)
            print("✅ Connection closed")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")

async def main():
    """Main function to run the Aras MCP client."""
    parser = argparse.ArgumentParser(description="Run Aras MCP Streamable HTTP Client")
    parser.add_argument(
        "--server-url", 
        type=str, 
        default="http://localhost:8123/mcp",
        help="MCP server URL (default: http://localhost:8123/mcp)"
    )
    parser.add_argument(
        "--anthropic-key",
        type=str,
        help="Anthropic API key for AI-powered queries (or set ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run a single test instead of interactive mode"
    )
    args = parser.parse_args()

    # Get Anthropic API key from args or environment
    anthropic_key = args.anthropic_key
    if not anthropic_key:
        import os
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    client = ArasMCPClient(anthropic_api_key=anthropic_key)

    try:
        # Connect to the server
        await client.connect_to_server(args.server_url)
        
        if args.non_interactive:
            # Run a simple test
            print("\n🧪 Running connection test...")
            result = await client.test_connection()
            print(result)
            print("\n📋 Getting available ItemTypes...")
            # This might fail if the endpoint doesn't exist, but it's just a demo
            result = await client.get_items("ItemType", select="name")
            print(result)
        else:
            # Run interactive mode
            await client.interactive_mode()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
