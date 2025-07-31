#!/usr/bin/env python3
"""
SSE-based MCP Client for Aras Innovator
Created by D. Theoden
Date: July 31, 2025
"""

import asyncio
import json
import os
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class ArasMCPClient:
    """MCP Client for connecting to SSE-based Aras MCP Server."""
    
    def __init__(self):
        """Initialize the client."""
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Initialize Anthropic client if API key is available
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.anthropic = Anthropic(api_key=anthropic_key)
        else:
            self.anthropic = None
            print("Warning: ANTHROPIC_API_KEY not found. Claude integration will not be available.")

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport."""
        try:
            # Store the context managers so they stay alive
            self._streams_context = sse_client(url=server_url)
            streams = await self._streams_context.__aenter__()

            self._session_context = ClientSession(*streams)
            self.session: ClientSession = await self._session_context.__aenter__()

            # Initialize
            await self.session.initialize()

            # List available tools to verify connection
            print("Initialized SSE client...")
            print("Listing tools...")
            response = await self.session.list_tools()
            tools = response.tools
            print(f"\nConnected to server with tools: {[tool.name for tool in tools]}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to SSE server: {str(e)}")
            return False

    async def cleanup(self):
        """Properly clean up the session and streams."""
        try:
            if hasattr(self, '_session_context') and self._session_context:
                await self._session_context.__aexit__(None, None, None)
            if hasattr(self, '_streams_context') and self._streams_context:
                await self._streams_context.__aexit__(None, None, None)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_sse_server first.")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return "\n".join([content.text for content in result.content if hasattr(content, 'text')])
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"

    async def list_tools(self) -> list:
        """List available tools from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_sse_server first.")
        
        response = await self.session.list_tools()
        return [{"name": tool.name, "description": tool.description} for tool in response.tools]

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools (if Anthropic is configured)."""
        if not self.anthropic:
            return "Claude integration not available. Please set ANTHROPIC_API_KEY environment variable."
        
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_sse_server first.")

        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                    "role": "assistant",
                    "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content[0].text if result.content else "No result"
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def interactive_session(self):
        """Run an interactive session with the MCP server."""
        print("\n=== Aras MCP Client Interactive Session ===")
        print("Available commands:")
        print("  - 'tools' or 'list' : List available tools")
        print("  - 'test' : Test API connection")
        print("  - 'query <your question>' : Use Claude to process queries (requires ANTHROPIC_API_KEY)")
        print("  - 'call <tool_name> <json_args>' : Call a tool directly")
        print("  - 'quit' or 'exit' : Exit the session")
        print()
        
        while True:
            try:
                user_input = input("Aras MCP> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() in ['tools', 'list']:
                    tools = await self.list_tools()
                    print("\nAvailable tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                elif user_input.lower() == 'test':
                    result = await self.call_tool("test_api_connection", {})
                    print(f"\n{result}")
                elif user_input.startswith('query '):
                    query = user_input[6:].strip()
                    if query:
                        result = await self.process_query(query)
                        print(f"\n{result}")
                    else:
                        print("Please provide a query after 'query'")
                elif user_input.startswith('call '):
                    parts = user_input[5:].strip().split(' ', 1)
                    if len(parts) >= 1:
                        tool_name = parts[0]
                        try:
                            args = json.loads(parts[1]) if len(parts) > 1 and parts[1].strip() else {}
                            result = await self.call_tool(tool_name, args)
                            print(f"\n{result}")
                        except json.JSONDecodeError:
                            print("Invalid JSON arguments. Example: call test_api_connection {}")
                    else:
                        print("Usage: call <tool_name> <json_args>")
                elif user_input == '':
                    continue
                else:
                    print("Unknown command. Type 'quit' to exit or 'tools' to list available tools.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def chat_loop(self):
        """Run an interactive chat loop (legacy method for compatibility)."""
        await self.interactive_session()

async def main():
    """Main entry point for the client."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.sse_client <SSE_SERVER_URL>")
        print("Example: python -m src.sse_client http://localhost:8080/sse")
        sys.exit(1)

    server_url = sys.argv[1]
    client = ArasMCPClient()
    
    try:
        print(f"Connecting to Aras MCP Server at: {server_url}")
        
        if await client.connect_to_sse_server(server_url):
            await client.interactive_session()
        else:
            print("Failed to connect to server. Please check the server URL and ensure the server is running.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
