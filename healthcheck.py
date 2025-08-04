#!/usr/bin/env python3
"""
Simple health check script for Docker containers
This script checks if the MCP server is responding properly
"""

import sys
import requests
import json

def check_health():
    """Check if the server is healthy."""
    try:
        # Check health endpoint
        response = requests.get("http://localhost:8123/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("status") == "healthy":
                print("✅ Health check passed")
                return True
        
        print(f"❌ Health check failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def check_status():
    """Check server status including Aras connection."""
    try:
        response = requests.get("http://localhost:8123/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            auth_status = status_data.get("authentication", "unknown")
            print(f"📊 Server status: {status_data.get('service', 'unknown')}")
            print(f"🔐 Authentication: {auth_status}")
            return auth_status in ["connected", "failed"]  # Any definitive status is good
        
        print(f"❌ Status check failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

if __name__ == "__main__":
    # For Docker health checks, we only need basic health
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
