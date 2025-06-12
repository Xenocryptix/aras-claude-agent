# 🚀 Aras Innovator MCP Server

> **Connect Claude Desktop to your Aras Innovator instance!**

This Model Context Protocol (MCP) server enables Claude Desktop to interact with Aras Innovator, allowing you to query data, create items, and call methods directly from your AI assistant.

🎥 **[Watch the demo in action on LinkedIn!](https://www.linkedin.com/posts/daan-theoden-254a8b96_plm-arasinnovator-mcp-activity-7337137605119000577-yCdq)** See how the AI agent retrieves PLM data, adds users, and creates BOM structures autonomously.

## ✨ What can you do?

- 🔐 **Test your Aras connection** with secure OAuth authentication
- 📊 **Query Aras data** using OData API (Parts, Documents, BOMs, etc.)
- ✍️ **Create new items** directly from Claude
- 🔧 **Call Aras methods** (BOM structures, workflows, etc.)
- 📋 **Access dropdown lists** and configuration data

## 📋 Prerequisites

### 🐍 Python 3.8+
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS/Linux:** `brew install python` or `sudo apt install python3 python3-pip`

### 🤖 Claude Desktop (free!)
- Download from [claude.ai](https://claude.ai/download) - no subscription required!

### 🏢 Aras Innovator access
- Server URL, database name, username, and password with API permissions

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
You should see: `Aras MCP Server running on stdio`

**Test in Claude Desktop:**
Restart Claude Desktop and try:
- *"Test my Aras connection"*
- *"Get all Part items from Aras"*
- *"Show me the document types list"*

## 🛠️ Available tools

| Tool | Description | What You Can Ask |
|------|-------------|------------------|
| **`test_aras_connection`** | Test authentication & connection | *"Test my Aras connection"* |
| **`aras_get_item`** | Query Aras data using OData | *"Get all Part items"* |
| **`aras_create_item`** | Create new items | *"Create a new Part with number P001"* |
| **`aras_call_method`** | Call Aras server methods | *"Get BOM structure for item X"* |
| **`aras_get_list`** | Get dropdown/list values | *"Show document types"* |

## 💬 Example conversations

```
You: "Test my Aras connection"
Claude: ✅ Successfully authenticated with Aras Innovator!

You: "Get all Part items where item_number starts with 'P001'"
Claude: Retrieved 15 Part items matching your criteria...

You: "Create a new document with title 'User Manual v2'"
Claude: Successfully created aer_dcm_data item with ID 12345...
```

## 🔧 Troubleshooting

### Common issues & solutions

**🔗 Connection issues?** Check your `.env` credentials and Aras server accessibility

**🔐 Permission errors?** Verify your Aras user has API access permissions

**🤖 Claude not finding tools?** Restart Claude Desktop and check file paths

**🐍 Python issues?** Ensure Python 3.8+ is installed: `python --version`

**❓ Still need help?** Check [GitHub Issues](https://github.com/DaanTheoden/aras-claude-agent/issues) or visit [www.arasdeveloper.com](https://www.arasdeveloper.com)

## 📚 Learn more

Want to master Aras development? Visit **[www.arasdeveloper.com](https://www.arasdeveloper.com)** for tutorials, best practices, and expert guidance!

## 🤝 Contributing

Found a bug or want to add features? We welcome contributions! Please check our issues or submit a pull request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details. 