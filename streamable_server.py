#!/usr/bin/env python3
"""
Aras MCP Streamable HTTP Server Entry Point
A standalone script to run the Aras MCP Streamable HTTP server.

Usage:
    python streamable_server.py --port 8123
    python streamable_server.py --port 9000 --host 0.0.0.0

Created by D. Theoden
Date: August 4, 2025
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.streamable_server import main

if __name__ == "__main__":
    main()
