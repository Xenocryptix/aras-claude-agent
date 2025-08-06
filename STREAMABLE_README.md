# Aras MCP Streamable HTTP Implementation

This directory contains HTTP Streamable implementations of the Aras Model Context Protocol (MCP) server and client, based on the [MCP Streamable HTTP specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Aras Innovator server** accessible
3. **Valid Aras credentials** configured
4. **Optional: Anthropic API key** for AI-powered queries

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install with optional Anthropic support
pip install -r requirements.txt anthropic
```

### Configuration

1. Copy `env_example.txt` to `.env` and configure your settings:
```env
# Aras Server Configuration
API_URL=http://your-aras-server/Server
API_USERNAME=your_username
API_PASSWORD=your_password
ARAS_DATABASE=InnovatorSolutions

# Optional: For AI-powered queries
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 🖥️ Running the Server

### Basic Usage
```bash
# Start with default settings (port 8123)
python streamable_server.py

# Specify custom port
python streamable_server.py --port 9000

# Bind to all interfaces
python streamable_server.py --host 0.0.0.0 --port 8123

# Enable development mode with auto-reload
python streamable_server.py --reload
```

### Server Endpoints

Once running, the server provides:

- **MCP Endpoint**: `http://localhost:8123/mcp` (main MCP communication)
- **Health Check**: `http://localhost:8123/health` 
- **Server Status**: `http://localhost:8123/status`

## 📱 Running the Client

### Interactive Mode (Default)
```bash
# Connect to local server
python streamable_client.py

# Connect to custom server
python streamable_client.py --server-url http://localhost:9000/mcp

# With Anthropic AI support
python streamable_client.py --anthropic-key your_api_key_here
```

### Non-Interactive Mode
```bash
# Run automated tests
python streamable_client.py --non-interactive
```

### Client Commands

In interactive mode, you can use these commands:

```
aras-mcp> test                           # Test Aras connection
aras-mcp> get Part                       # Get all Parts
aras-mcp> get User --select name,login   # Get Users with specific fields
aras-mcp> list Part State                # Get Part State list
aras-mcp> relate ABC123 DEF456 "Part BOM" # Create relationship between items
aras-mcp> ai "Show me all documents"     # AI-powered query (requires Anthropic)
aras-mcp> help                           # Show available commands
aras-mcp> quit                           # Exit
```

## 🔧 Available Tools

The server exposes these MCP tools for Aras integration:

### Core Tools (Active)
- **`test_api_connection`** - Test authentication with Aras server
- **`api_get_items`** - Retrieve items using OData (GET operations)
- **`api_create_item`** - Create new items (POST operations)
- **`api_call_method`** - Call Aras server methods
- **`api_get_list`** - Retrieve list values
- **`api_create_relationship`** - Create relationships between items

### File Management Tools (Placeholders)
- **`api_upload_file`** - Reserved for future file upload implementation
- **`api_create_document_with_file`** - Reserved for future document+file creation

## 📊 Example Usage

### Basic Item Retrieval
```python
# Get all Parts with basic fields
await client.get_items("Part", select="item_number,name,state")

# Get Documents with relationships
await client.get_items("Document", expand="Files,CreatedBy")

# Filtered query
await client.get_items("Part", filter="state eq 'Released'")
```

### Creating Items
```python
# Create a new Part
part_data = {
    "item_number": "PART-001",
    "name": "New Component",
    "description": "Sample part description"
}
await client.create_item("Part", part_data)
```

### Creating Relationships
```python
# Create a Part BOM relationship
await client.create_relationship(
    source_item_id="PARENT_PART_ID",
    related_item_id="CHILD_PART_ID", 
    relationship_type="Part BOM",
    data={"quantity": 2, "sort_order": 1}
)

# Create a Document File relationship
await client.create_relationship(
    source_item_id="DOCUMENT_ID",
    related_item_id="FILE_ID",
    relationship_type="Document File"
)
```

### File Operations (Future)
```python
# These will be implemented when file handling is added to the base API client
# await client.upload_file("/path/to/file.pdf", "specification.pdf")
# await client.create_document_with_file(doc_data, "/path/to/spec.pdf")
```

### AI-Powered Queries
```python
# Natural language queries (requires Anthropic API key)
await client.process_ai_query("Show me all parts that are in Released state")
await client.process_ai_query("Create a new document for the latest design")
await client.process_ai_query("What users have admin privileges?")
```

## 🔄 Transport Comparison

| Feature | STDIO Transport | HTTP Streamable |
|---------|----------------|-----------------|
| **Deployment** | Desktop only | Web-accessible |
| **Scalability** | Single session | Multiple clients |
| **Debugging** | Limited | HTTP tools |
| **Streaming** | Bidirectional | Server-Sent Events |
| **Firewall** | Local only | HTTP/HTTPS |

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/SSE     ┌─────────────────┐    REST/OData    ┌─────────────────┐
│   MCP Client    │ ◄──────────────► │  MCP Server     │ ◄──────────────► │  Aras Innovator │
│                 │                  │                 │                  │     Server      │
│ • Interactive   │                  │ • FastMCP       │                  │ • Items/Users   │
│ • AI-Powered    │                  │ • Tool Handlers │                  │ • Files/Lists   │
│ • Programmable  │                  │ • Auth Manager  │                  │ • Methods       │
└─────────────────┘                  └─────────────────┘                  └─────────────────┘
```

## 🛠️ Development

### Project Structure
```
src/
├── streamable_server.py    # HTTP Streamable MCP server
├── streamable_client.py    # HTTP Streamable MCP client  
├── server.py              # Original STDIO MCP server
├── api_client.py          # Aras API client
├── auth.py               # Authentication logic
└── config.py             # Configuration management

# Standalone entry points
streamable_server.py       # Server launcher
streamable_client.py       # Client launcher
main.py                   # Original STDIO launcher
```

### Adding New Tools

1. **Add tool to server** (`src/streamable_server.py`):
```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int) -> str:
    """Description of what the tool does."""
    # Implementation here
    return result
```

2. **Add client method** (`src/streamable_client.py`):
```python
async def my_new_action(self, param1: str, param2: int) -> str:
    """Client wrapper for the new tool."""
    if not self.session:
        return "❌ Not connected to MCP server"
    
    result = await self.session.call_tool("my_new_tool", {
        "param1": param1,
        "param2": param2
    })
    return result.content[0].text if result.content else "No response"
```

### Testing

```bash
# Start server in one terminal
python streamable_server.py --port 8123

# Test with client in another terminal  
python streamable_client.py --non-interactive

# Or use curl for HTTP testing
curl http://localhost:8123/health
curl http://localhost:8123/status
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure server is running on the correct port
   - Check firewall settings
   - Verify URL format: `http://localhost:8123/mcp`

2. **Authentication Failed**
   - Verify Aras credentials in `.env` file
   - Check Aras server accessibility
   - Confirm database name is correct

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **AI Features Not Working**
   - Install Anthropic: `pip install anthropic`
   - Set `ANTHROPIC_API_KEY` environment variable

### Debug Mode

Enable detailed logging:
```bash
# Server with reload and verbose logging
python streamable_server.py --reload --port 8123

# Client with error details  
python streamable_client.py --server-url http://localhost:8123/mcp
```

## 📝 License

This project is licensed under the same terms as the original Aras Claude Agent.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test with both server and client
5. Submit a pull request

## 📞 Support

- **Aras Developer Community**: https://www.arasdeveloper.com
- **MCP Documentation**: https://modelcontextprotocol.io
- **Issues**: Create an issue in the repository
