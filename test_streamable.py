#!/usr/bin/env python3
"""
Test script for Aras MCP Streamable HTTP implementation

This script performs basic validation of the server and client components.

Usage:
    python test_streamable.py

Created by D. Theoden
Date: August 4, 2025
"""

import asyncio
import sys
import os
import subprocess
import time
import httpx

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_server_health():
    """Test if the server is running and healthy."""
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get("http://localhost:8123/health", timeout=10.0)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

async def test_server_status():
    """Test the server status endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8123/status", timeout=10.0)
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ Status check passed")
                print(f"   Service: {status_data.get('service', 'unknown')}")
                print(f"   Version: {status_data.get('version', 'unknown')}")
                print(f"   Aras Server: {status_data.get('aras_server', 'unknown')}")
                print(f"   Authentication: {status_data.get('authentication', 'unknown')}")
                return True
            else:
                print(f"❌ Status check failed with status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False

async def test_mcp_client():
    """Test the MCP client connection."""
    try:
        from src.streamable_client import ArasMCPClient
        
        client = ArasMCPClient()
        
        # Test connection
        await client.connect_to_server("http://localhost:8123/mcp")
        print("✅ MCP client connected successfully")
        
        # Test basic operation
        result = await client.test_connection()
        if "Successfully authenticated" in result:
            print("✅ Aras authentication test passed")
        elif "Failed to authenticate" in result:
            print("⚠️  Aras authentication failed (check credentials)")
        else:
            print(f"❓ Unexpected authentication result: {result[:100]}...")
        
        await client.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False

def start_server_process():
    """Start the server in a subprocess."""
    try:
        print("🚀 Starting Aras MCP server...")
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, "streamable_server.py", "--port", "8123"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__)
        )
        
        # Give server time to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server process started")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

async def run_tests():
    """Run all tests."""
    print("🧪 Aras MCP Streamable HTTP - Test Suite")
    print("=" * 50)
    
    # Check if server is already running
    server_running = await test_server_health()
    server_process = None
    
    if not server_running:
        print("\n📡 Server not running, attempting to start...")
        server_process = start_server_process()
        if server_process:
            # Wait a bit more and test again
            await asyncio.sleep(2)
            server_running = await test_server_health()
    
    if not server_running:
        print("❌ Cannot proceed without a running server")
        print("   Please start manually: python streamable_server.py")
        return False
    
    print("\n🔍 Testing server endpoints...")
    print("-" * 30)
    
    # Test health endpoint
    health_ok = await test_server_health()
    
    # Test status endpoint  
    status_ok = await test_server_status()
    
    print("\n🔗 Testing MCP client...")
    print("-" * 30)
    
    # Test MCP client
    client_ok = await test_mcp_client()
    
    print("\n📋 Test Results Summary")
    print("-" * 30)
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Status endpoint: {'✅ PASS' if status_ok else '❌ FAIL'}")
    print(f"MCP client:      {'✅ PASS' if client_ok else '❌ FAIL'}")
    
    # Cleanup
    if server_process:
        print("\n🛑 Stopping test server...")
        server_process.terminate()
        server_process.wait()
    
    all_passed = health_ok and status_ok and client_ok
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("- Start server: python streamable_server.py")
        print("- Run client: python streamable_client.py")
        print("- Try examples: python example_usage.py")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\nTroubleshooting:")
        print("- Verify Aras server is accessible")
        print("- Check .env configuration")
        print("- Ensure all dependencies are installed: pip install -r requirements.txt")
    
    return all_passed

async def main():
    """Main execution."""
    try:
        success = await run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
