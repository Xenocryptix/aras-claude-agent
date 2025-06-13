#!/usr/bin/env python3
"""
Generic API MCP Server
A Model Context Protocol server for integrating any REST API with Claude Desktop.

Created by D. Theoden
Date: June 12, 2025

Learn more about Aras development at: https://www.arasdeveloper.com
"""

from src.server import main
import asyncio

def run():
    """Entry point for the MCP server."""
    asyncio.run(main())

if __name__ == "__main__":
    run() 