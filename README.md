# 🚀 Generic API MCP Server

> **Connect Claude Desktop to any REST API!**

This Model Context Protocol (MCP) server enables Claude Desktop to interact with any REST API, allowing you to query data, create items, and call methods directly from your AI assistant.

## ✨ What can you do?

- 🔐 **Test your API connection** with secure authentication
- 📊 **Query API data** using REST endpoints
- ✍️ **Create new items** directly from Claude
- 🔧 **Call API methods** and custom endpoints
- 📋 **Access lists** and configuration data

## 📋 Prerequisites

### 🐍 Python 3.8+
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS/Linux:** `brew install python` or `sudo apt install python3 python3-pip`

### 🤖 Claude Desktop (free!)
- Download from [claude.ai](https://claude.ai/download) - no subscription required!

### 🏢 API access
- Server URL and authentication credentials with API permissions

## 🎯 Quick start

### 1️⃣ Clone & install
```bash
git clone https://github.com/yourusername/api-mcp-server.git
cd api-mcp-server
pip install -r requirements.txt
```

### 2️⃣ Configure your API connection
Create a `.env` file in the project root:
```env
API_URL=https://your-api-server.com
API_USERNAME=your-username
API_PASSWORD=your-password
```
> 💡 Copy from `env_example.txt` and update with your credentials

### 3️⃣ Add to Claude Desktop
Edit your Claude Desktop config file:

**📁 Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**📁 macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "api-server": {
      "command": "python",
      "args": ["C:/path/to/your/api-mcp-server/main.py"]
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
You should see: `API MCP Server running on stdio`

**Test in Claude Desktop:**
Restart Claude Desktop and try:
- *"Test my API connection"*
- *"Get all items from endpoint /users"*
- *"Show me the available lists"*

## 🛠️ Available tools

| Tool | Description | What You Can Ask |
|------|-------------|------------------|
| **`test_api_connection`** | Test authentication & connection | *"Test my API connection"* |
| **`api_get_items`** | Query API data | *"Get all users"* |
| **`api_create_item`** | Create new items | *"Create a new user"* |
| **`api_call_method`** | Call API methods | *"Call the search endpoint"* |
| **`api_get_list`** | Get list values | *"Show available options"* |

## 💬 Example conversations

```
You: "Test my API connection"
Claude: ✅ Successfully authenticated with API!

You: "Get all users where name starts with 'John'"
Claude: Retrieved 15 users matching your criteria...

You: "Create a new document with title 'User Manual v2'"
<<<<<<< HEAD
Claude: Successfully created item with ID 12345...
=======
Claude: Successfully created Document item with ID 12345...
>>>>>>> c42616bce2e5e41f72dc0fbbc1f1c28b10357a87
```

## 🔧 Troubleshooting

### Common issues & solutions

**🔗 Connection issues?** Check your `.env` credentials and API server accessibility

**🔐 Permission errors?** Verify your API user has proper access permissions

**🤖 Claude not finding tools?** Restart Claude Desktop and check file paths

**🐍 Python issues?** Ensure Python 3.8+ is installed: `python --version`

## 🤝 Contributing

Found a bug or want to add features? We welcome contributions! Please check our issues or submit a pull request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details. 