# Aras MCP Server - SSE Implementation

This document provides setup and usage instructions for the SSE (Server-Sent Events) based MCP (Model Context Protocol) server for Aras Innovator integration.

## Overview

The SSE implementation allows the MCP server to run as a standalone service that n8n and other clients can connect to over HTTP. This is different from the STDIO-based approach where the client spawns the server as a subprocess.

### Architecture

```
┌─────────────┐    HTTP/SSE    ┌─────────────────┐    REST API    ┌──────────────────┐
│   n8n       │ ─────────────→ │ Aras MCP Server │ ─────────────→ │ Aras Innovator   │
│   Client    │                │ (Docker)        │                │ Server           │
└─────────────┘                └─────────────────┘                └──────────────────┘
```

## Quick Start

### 1. Configuration

Copy the environment template and configure your Aras server settings:

```bash
cp .env.example .env
```

Edit `.env` file with your Aras Innovator server details:

```env
API_URL=http://your-aras-server/InnovatorServer
API_USERNAME=your_username
API_PASSWORD=your_password
ARAS_DATABASE=InnovatorSolutions
```

### 2. Start the Server

Using Docker Compose (recommended):

```bash
# Linux/macOS
./scripts/manage.sh start

# Windows
scripts\manage.bat start
```

Or manually:

```bash
docker compose up -d aras-mcp-server
```

### 3. Test the Server

The SSE endpoint will be available at: `http://localhost:8080/sse`

Test the connection:

```bash
# Linux/macOS
./scripts/manage.sh status

# Windows
scripts\manage.bat status
```

### 4. Connect from n8n

In n8n, use the HTTP Request node to connect to the SSE endpoint:

- **Method**: GET
- **URL**: `http://localhost:8080/sse`
- **Headers**: 
  - `Accept`: `text/event-stream`
  - `Cache-Control`: `no-cache`

## Available Tools

The MCP server provides the following tools for Aras Innovator integration:

### 1. test_api_connection
Test connection and authentication with Aras Innovator server.

**Parameters**: None

### 2. api_get_items
Retrieve items from Aras Innovator using OData API.

**Parameters**:
- `endpoint` (required): ItemType name (e.g., 'Part', 'Document')
- `expand` (optional): Expand related data
- `filter` (optional): OData filter expression
- `select` (optional): Select specific fields

### 3. api_create_item
Create new items in Aras Innovator.

**Parameters**:
- `endpoint` (required): ItemType name
- `data` (required): Item data as JSON object

### 4. api_call_method
Call Aras Innovator server methods.

**Parameters**:
- `method_name` (required): Method name to call
- `data` (required): Method parameters as JSON object

### 5. api_get_list
Get list data from Aras Innovator.

**Parameters**:
- `list_id` (required): List ID to retrieve
- `expand` (optional): Expand parameter for list values

### 6. api_upload_file
Upload a file to Aras Innovator database.

**Parameters**:
- `file_path` (required): Absolute path to file
- `filename` (optional): Custom filename

### 7. api_create_document_with_file
Create a Document item and upload a file with relationship.

**Parameters**:
- `document_data` (required): Document metadata
- `file_path` (required): Path to file
- `filename` (optional): Custom filename

## Client Usage

### Interactive Client

Start the interactive client:

```bash
# Linux/macOS
./scripts/manage.sh client

# Windows
scripts\manage.bat client

# Or connect to remote server
python -m src.sse_client http://remote-server:8080/sse
```

Available client commands:

- `tools` or `list`: List available tools
- `test`: Test API connection
- `query <your question>`: Use Claude to process queries (requires ANTHROPIC_API_KEY)
- `call <tool_name> <json_args>`: Call a tool directly
- `quit` or `exit`: Exit the session

### Example Client Usage

```bash
Aras MCP> test
✅ Successfully authenticated with Aras Innovator!

Aras MCP> call api_get_items {"endpoint": "Part", "select": "item_number,name", "filter": "name eq 'Example Part'"}
Retrieved items from Part:
{
  "value": [
    {
      "item_number": "PART-001",
      "name": "Example Part"
    }
  ]
}
```

## Docker Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | Aras Innovator server URL | Required |
| `API_USERNAME` | Aras username | Required |
| `API_PASSWORD` | Aras password | Required |
| `ARAS_DATABASE` | Aras database name | InnovatorSolutions |
| `API_TIMEOUT` | API request timeout (seconds) | 30 |
| `API_RETRY_COUNT` | Number of retry attempts | 3 |
| `API_RETRY_DELAY` | Delay between retries (seconds) | 1 |
| `LOG_LEVEL` | Logging level | INFO |
| `ANTHROPIC_API_KEY` | Claude API key (optional) | - |

### Docker Compose Services

#### aras-mcp-server
Main MCP server container.

- **Port**: 8080
- **Health Check**: HTTP GET to `/sse`
- **Restart Policy**: unless-stopped

#### nginx (optional)
Reverse proxy with SSL termination and rate limiting.

- **Ports**: 80, 443
- **Profile**: nginx
- **Features**: Rate limiting, SSL support, load balancing

### Starting with Nginx

```bash
# Start with reverse proxy
docker compose --profile nginx up -d

# Or using management script
./scripts/manage.sh start-nginx
```

## n8n Integration

### Using HTTP Request Node

1. **Add HTTP Request Node**
2. **Configure Connection**:
   - Method: GET
   - URL: `http://localhost:8080/sse`
   - Headers:
     ```json
     {
       "Accept": "text/event-stream",
       "Cache-Control": "no-cache"
     }
     ```

3. **Handle SSE Messages**:
   The server sends JSON-RPC messages over SSE. Parse the event data to extract MCP responses.

### Example n8n Workflow

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8080/messages/",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "jsonrpc",
              "value": "2.0"
            },
            {
              "name": "method",
              "value": "tools/call"
            },
            {
              "name": "params",
              "value": {
                "name": "test_api_connection",
                "arguments": {}
              }
            },
            {
              "name": "id",
              "value": "1"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [740, 240],
      "name": "Call MCP Tool"
    }
  ]
}
```

## Development

### Running in Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run server directly
python main_sse.py --debug

# Run client
python -m src.sse_client http://localhost:8080/sse
```

### Adding New Tools

1. **Update `src/sse_server.py`**:
   - Add tool definition in `handle_list_tools()`
   - Add tool handler in `handle_call_tool()`

2. **Implement in `src/api_client.py`**:
   - Add corresponding API method

3. **Test the tool**:
   ```bash
   python -m src.sse_client http://localhost:8080/sse
   ```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
- Check if Docker is running
- Verify port 8080 is not in use
- Check firewall settings

```bash
# Check if server is running
curl -f http://localhost:8080/sse

# Check Docker logs
docker compose logs aras-mcp-server
```

#### 2. Authentication Failures
- Verify Aras server URL in `.env`
- Check username/password credentials
- Ensure Aras server is accessible

#### 3. SSL/TLS Issues
- For HTTPS, configure SSL certificates in `nginx.conf`
- Update client URL to use `https://`

### Debugging

#### Server Logs
```bash
# Follow logs
docker compose logs -f aras-mcp-server

# Or using management script
./scripts/manage.sh logs
```

#### Health Check
```bash
# Check server status
./scripts/manage.sh status

# Manual health check
curl -v http://localhost:8080/sse
```

#### Client Debugging
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python -m src.sse_client http://localhost:8080/sse
```

## Security Considerations

### Production Deployment

1. **Use HTTPS**: Enable SSL in nginx configuration
2. **Authentication**: Implement API key authentication
3. **Rate Limiting**: Configure appropriate limits in nginx
4. **Network Security**: Use Docker networks and firewalls
5. **Secrets Management**: Use Docker secrets or external secret stores

### Network Configuration

```yaml
# docker compose.override.yml for production
version: '3.8'
services:
  aras-mcp-server:
    environment:
      - API_PASSWORD_FILE=/run/secrets/aras_password
    secrets:
      - aras_password

secrets:
  aras_password:
    external: true
```

## Performance Tuning

### Server Configuration

- **Timeout Settings**: Adjust `API_TIMEOUT` for slow networks
- **Retry Logic**: Configure `API_RETRY_COUNT` and `API_RETRY_DELAY`
- **Connection Pooling**: Implement in `api_client.py`

### Docker Resource Limits

```yaml
services:
  aras-mcp-server:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Support

For issues and questions:

1. Check the logs: `./scripts/manage.sh logs`
2. Verify configuration: `./scripts/manage.sh status`
3. Test connection: `./scripts/manage.sh client`
4. Review environment variables in `.env`

## License

This project is part of the Aras MCP Server implementation.
Learn more about Aras development at: https://www.arasdeveloper.com
