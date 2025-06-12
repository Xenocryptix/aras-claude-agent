# 🚀 Aras Innovator MCP Server

> **Connect Claude Desktop to your Aras Innovator instance!**

This Model Context Protocol (MCP) server enables Claude Desktop to interact with Aras Innovator, allowing you to query data, create items, and call methods directly from your AI assistant.

## ✨ What Can You Do?

- 🔐 **Test your Aras connection** with secure OAuth authentication
- 📊 **Query Aras data** using OData API (Parts, Documents, BOMs, etc.)
- ✍️ **Create new items** directly from Claude
- 🔧 **Call Aras methods** (BOM structures, workflows, etc.)
- 📋 **Access dropdown lists** and configuration data

## 🎯 Quick Start

### 1️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd aras-mcp-server
pip install -r requirements.txt
```

### 2️⃣ Configure Your Aras Connection
Create a `.env` file in the project root:
```env
ARAS_URL=https://your-aras-server.com/InnovatorServer
ARAS_DATABASE=YourDatabase
ARAS_USERNAME=your-username
ARAS_PASSWORD=your-password
```
> 💡 Copy from `env_example.txt` and update with your credentials

### 3️⃣ Add to Claude Desktop
Edit your Claude Desktop config file:

**📁 Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**📁 macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aras-innovator": {
      "command": "python",
      "args": ["C:/path/to/your/aras-mcp-server/main.py"]
    }
  }
}
```

### 4️⃣ Test It Out!
Restart Claude Desktop and try:
- *"Test my Aras connection"*
- *"Get all Part items from Aras"*
- *"Show me the document types list"*

## 🛠️ Available Tools

| Tool | Description | What You Can Ask |
|------|-------------|------------------|
| **`test_aras_connection`** | Test authentication & connection | *"Test my Aras connection"* |
| **`aras_get_item`** | Query Aras data using OData | *"Get all Part items"* |
| **`aras_create_item`** | Create new items | *"Create a new Part with number P001"* |
| **`aras_call_method`** | Call Aras server methods | *"Get BOM structure for item X"* |
| **`aras_get_list`** | Get dropdown/list values | *"Show document types"* |

## 💬 Example Conversations

```
You: "Test my Aras connection"
Claude: ✅ Successfully authenticated with Aras Innovator!

You: "Get all Part items where item_number starts with 'P001'"
Claude: Retrieved 15 Part items matching your criteria...

You: "Create a new document with title 'User Manual v2'"
Claude: Successfully created aer_dcm_data item with ID 12345...
```

## 🔧 Troubleshooting

- **Connection issues?** Check your `.env` file credentials
- **Permission errors?** Verify your Aras user has API access
- **Claude not finding tools?** Restart Claude Desktop after config changes

## 📚 Learn More

Want to master Aras development? Visit **[www.arasdeveloper.com](https://www.arasdeveloper.com)** for tutorials, best practices, and expert guidance!

## 🤝 Contributing

Found a bug or want to add features? We welcome contributions! Please check our issues or submit a pull request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details. 