#!/usr/bin/env python3
"""
Example: Using Aras MCP Streama        # Example 5: Call a method (get server info)
        print("\n🔍 Calling GetServerInfo method...")
        result = await client.call_method("GetServerInfo", {})
        print(result)
        
        # Example 6: Create a relationship (uncomment if you want to test)
        # print("\n🔗 Creating a relationship...")
        # # This would create a Part BOM relationship between two parts
        # result = await client.create_relationship(
        #     source_item_id="PART123", 
        #     related_item_id="PART456", 
        #     relationship_type="Part BOM",
        #     data={"quantity": 2, "sort_order": 1}
        # )
        # print(result)
        
        # Note: File operations are placeholder implementations
        # print("\n📁 Testing file upload (placeholder)...")
        # result = await client.upload_file("/path/to/file.pdf", "test.pdf")
        # print(result)HTTP Client Programmatically

This script demonstrates how to use the Aras MCP client in your own Python applications.

Created by D. Theoden
Date: August 4, 2025
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.streamable_client import ArasMCPClient

async def demonstrate_aras_operations():
    """Demonstrate various Aras MCP operations."""
    
    # Initialize client (optionally with Anthropic API key)
    client = ArasMCPClient()
    
    try:
        # Connect to the MCP server
        print("🔗 Connecting to Aras MCP server...")
        await client.connect_to_server("http://localhost:8123/mcp")
        
        # Test connection to Aras
        print("\n🧪 Testing Aras connection...")
        result = await client.test_connection()
        print(result)
        
        # Example 1: Get all ItemTypes (shows available item types in Aras)
        print("\n📋 Getting ItemTypes...")
        result = await client.get_items("ItemType", select="name,label")
        print(result)
        
        # Example 2: Get Users with specific fields
        print("\n👥 Getting Users...")
        result = await client.get_items("User", select="login_name,first_name,last_name,email")
        print(result)
        
        # Example 3: Get a specific list (Part States)
        print("\n📝 Getting Part State list...")
        result = await client.get_list("Part State")
        print(result)
        
        # Example 4: Create a new Part (uncomment if you want to test creation)
        # print("\n🔧 Creating a new Part...")
        # part_data = {
        #     "item_number": f"TEST-PART-{int(asyncio.get_event_loop().time())}",
        #     "name": "Test Part from MCP",
        #     "description": "Created via MCP Streamable HTTP"
        # }
        # result = await client.create_item("Part", part_data)
        # print(result)
        
        # Note: File operations are placeholder implementations
        # print("\n� Testing file upload (placeholder)...")
        # result = await client.upload_file("/path/to/file.pdf", "test.pdf")
        # print(result)
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        await client.cleanup()
    
    return True

async def demonstrate_ai_queries():
    """Demonstrate AI-powered queries (requires Anthropic API key)."""
    
    # Get Anthropic API key from environment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("⚠️  Skipping AI examples - ANTHROPIC_API_KEY not set")
        return True
    
    client = ArasMCPClient(anthropic_api_key=anthropic_key)
    
    try:
        print("\n🤖 Connecting for AI-powered queries...")
        await client.connect_to_server("http://localhost:8123/mcp")
        
        # Example AI queries
        queries = [
            "What ItemTypes are available in this Aras system?",
            "Show me information about the current users",
            "What lists are available for Parts?"
        ]
        
        for query in queries:
            print(f"\n🎯 AI Query: {query}")
            result = await client.process_ai_query(query)
            print(result)
        
        print("\n✅ AI examples completed successfully!")
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return False
    
    finally:
        await client.cleanup()
    
    return True

async def main():
    """Main execution function."""
    print("🎯 Aras MCP Streamable HTTP - Example Usage")
    print("=" * 50)
    
    # Check if server is likely running
    import httpx
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("http://localhost:8123/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ MCP server is running")
            else:
                print("⚠️  MCP server responded with unexpected status")
    except:
        print("❌ MCP server not accessible at http://localhost:8123")
        print("   Please start the server first: python streamable_server.py")
        return
    
    # Run basic examples
    print("\n" + "=" * 50)
    print("🔧 Basic Aras Operations")
    print("=" * 50)
    success = await demonstrate_aras_operations()
    
    if success:
        # Run AI examples if API key is available
        print("\n" + "=" * 50)
        print("🤖 AI-Powered Queries")
        print("=" * 50)
        await demonstrate_ai_queries()
    
    print("\n🎉 Example completed!")
    print("\nNext steps:")
    print("- Explore interactive mode: python streamable_client.py")
    print("- Check server status: http://localhost:8123/status")
    print("- Review STREAMABLE_README.md for more details")

if __name__ == "__main__":
    asyncio.run(main())
