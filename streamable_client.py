#!/usr/bin/env python3
"""
Aras MCP Streamable HTTP Client Entry Point
A standalone script to run the Aras MCP Streamable HTTP client.

Usage:
    python streamable_client.py
    python streamable_client.py --server-url http://localhost:8123/mcp
    python streamable_client.py --anthropic-key your_api_key_here
    python streamable_client.py --non-interactive

Created by D. Theoden
Date: August 4, 2025
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.streamable_client import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
