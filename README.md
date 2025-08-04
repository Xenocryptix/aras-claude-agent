# 🚀 Aras Innovator Claude Agent

> **Connect Claude Desktop to Aras Innovator PLM via OAuth 2.0!**

This Model Context Protocol (MCP) server enables Claude Desktop to interact with Aras Innovator using modern OAuth 2.0 authentication and OData REST APIs, allowing you to query PLM data, create items, and call methods directly from your AI assistant.

**🆕 NEW: HTTP Streamable Transport!** - Now includes both STDIO (desktop) and HTTP Streamable (web-accessible) transport implementations.

## ✨ What can you do?

- 🔐 **Secure OAuth 2.0 authentication** with Aras Innovator 14+
- 📊 **Query PLM data** using OData REST endpoints  
- ✍️ **Create new items** (Parts, Documents, etc.) directly from Claude
- 🔧 **Call Aras server methods** and custom endpoints
- 📋 **Access lists** and configuration data
- 🛡️ **Enterprise-grade security** with bearer token authentication
- 🌐 **HTTP Streamable support** for web-accessible deployments

## 🚀 Choose Your Transport

### 📱 STDIO Transport (Claude Desktop)
- **Perfect for**: Claude Desktop integration
- **Deployment**: Local development, single user
- **Setup**: Follow standard MCP configuration

### 🌐 HTTP Streamable Transport (Web/Server)
- **Perfect for**: Web deployments, multiple users, production
- **Deployment**: Any server environment
- **Setup**: See [STREAMABLE_README.md](STREAMABLE_README.md)

```bash
# STDIO (original)
python main.py

# HTTP Streamable (new)
python streamable_server.py
python streamable_client.py
```

## 📋 Prerequisites

### 🐍 Python 3.8+
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS/Linux:** `brew install python` or `sudo apt install python3 python3-pip`

### 🤖 Claude Desktop (free!)
- Download from [claude.ai](https://claude.ai/download) - no subscription required!

### 🏢 Aras Innovator 14+ with OAuth 2.0
- Aras Innovator server with OAuth 2.0 endpoints enabled
- Valid Aras user credentials with API permissions
- Database access permissions

## 🎯 Quick start

### 1️⃣ Clone & install
```bash
git clone https://github.com/DaanTheoden/aras-claude-agent.git
cd aras-claude-agent
pip install -r requirements.txt
```

### 2️⃣ Configure your Aras connection
Create a `.env` file in the project root:
```env
# Aras Innovator OAuth 2.0 Configuration
API_URL=https://your-aras-server.com/YourDatabase
API_USERNAME=your-aras-username
API_PASSWORD=your-aras-password
ARAS_DATABASE=YourDatabase

# Optional Configuration
API_TIMEOUT=30
API_RETRY_COUNT=3
API_RETRY_DELAY=1
LOG_LEVEL=INFO
```
> 💡 Copy from `env_example.txt` and update with your Aras credentials

### 3️⃣ Add to Claude Desktop
Edit your Claude Desktop config file:

**📁 Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**📁 macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "api-server": {
      "command": "py",
      "args": ["C:/path/to/your/aras-claude-agent/main.py"]
    }
  }
}
```

> 💡 **Replace the path** with your actual installation directory!

### 4️⃣ Test your setup!

**Verify installation:**
```bash
python main.py
```
The server should start without any JSON parsing errors.

**Test in Claude Desktop:**
Restart Claude Desktop and try:
- *"Test my API connection"*
- *"Get all Parts from the database"*
- *"Show me the available Document types"*

## 🛠️ Available tools

| Tool | Description | What You Can Ask | Example Endpoint |
|------|-------------|------------------|------------------|
| **`test_api_connection`** | Test OAuth 2.0 authentication | *"Test my API connection"* | N/A |
| **`api_get_items`** | Query Aras OData | *"Get all Parts"* | `Part`, `Document` |
| **`api_create_item`** | Create new Aras items | *"Create a new Part"* | `Part`, `Document` |
| **`api_call_method`** | Call Aras server methods | *"Call method GetItemsInBOM"* | Method names |
| **`api_get_list`** | Get Aras list values | *"Show Part categories"* | List IDs |

## 🔐 OAuth 2.0 Authentication

This agent uses **OAuth 2.0 Resource Owner Password Credentials Grant** for secure authentication with Aras Innovator 14+. The authentication flow:

1. **Token Request**: `https://your-server/oauthserver/connect/token`
2. **Scope**: `openid Innovator offline_access`  
3. **Client ID**: `IOMApp` (default Aras client)
4. **Grant Type**: `password`
5. **Required**: `username`, `password`, `database`

## 💬 Example conversations

```
You: "Test my API connection"
Claude: ✅ Successfully authenticated with API!
Bearer token obtained and ready for API calls.
Server URL: https://your-server.com/YourDatabase

You: "Get all Parts where item_number starts with 'P-'"
Claude: Retrieved 25 Parts matching your criteria...

You: "Create a new Document with name 'User Manual v2'"
Claude: Successfully created Document with ID A1B2C3D4...
```

## 🔧 Recent Fixes & Updates

### ✅ v1.1.0 - OAuth 2.0 & JSON Parsing Fixes
- **Fixed**: "Unexpected token 'A', 'API MCP Se'... is not valid JSON" error
- **Added**: Proper OAuth 2.0 authentication with `requests-oauthlib`
- **Added**: Database parameter requirement for Aras authentication
- **Fixed**: All print statements redirected to stderr to prevent stdout contamination
- **Updated**: OData endpoint support (`/Server/Odata`)
- **Added**: Proper HTTP headers for Aras REST API

### 🛠️ Troubleshooting

**🔗 OAuth authentication failing?**
- Verify your Aras server supports OAuth 2.0 (Aras 14+)
- Check credentials and database name in `.env`
- Ensure user has API access permissions

**🔐 "Missing database parameter" error?**
- Add `ARAS_DATABASE=YourDatabaseName` to your `.env` file

**🤖 Claude not finding tools?**
- Restart Claude Desktop after config changes
- Check file paths in `claude_desktop_config.json`

**🐍 JSON parsing errors?**
- ✅ Fixed in v1.1.0! Update to latest version

## 🏗️ Architecture

### STDIO Transport (Claude Desktop)
```
Claude Desktop
    ↓ JSON-RPC
MCP Server (stdio)
    ↓ OAuth 2.0
Aras Innovator
    ↓ OData REST API
PLM Database
```

### HTTP Streamable Transport (Web/Server)
```
Client/Browser
    ↓ HTTP/SSE
MCP Server (streamable)
    ↓ OAuth 2.0
Aras Innovator
    ↓ OData REST API
PLM Database
```

## 🆕 HTTP Streamable Implementation

This project now includes a full HTTP Streamable implementation! See [STREAMABLE_README.md](STREAMABLE_README.md) for:

- 🌐 **Web-accessible MCP server** with HTTP/SSE transport
- 🖥️ **Interactive client** with command-line interface
- 🤖 **AI-powered queries** using Anthropic's Claude
- 📊 **Health monitoring** and status endpoints
- 🔧 **Production-ready** deployment options

Quick start with HTTP Streamable:
```bash
# Start server
python streamable_server.py --port 8123

# Run client (new terminal)
python streamable_client.py

# Test everything
python test_streamable.py
```

## 🤝 Contributing

Found a bug or want to add features? We welcome contributions! Please check our issues or submit a pull request.

## 📚 Learn More

- [Aras Developer Documentation](https://www.arasdeveloper.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Aras OAuth 2.0 Guide](https://community.aras.com)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details. 