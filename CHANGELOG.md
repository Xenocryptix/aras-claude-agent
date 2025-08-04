# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-08-01

### ✨ Added
- **NEW TOOL**: `api_create_relationship` - Create relationships between two existing items in Aras Innovator
- Support for common relationship types like 'Part BOM', 'Document File', 'Part Document'
- Optional additional properties for relationships (quantity, sort_order, etc.)
- Comprehensive documentation and examples for relationship creation
- Enhanced API client with dedicated `create_relationship()` method

### 🔧 Enhanced
- Updated both SSE and STDIO server implementations with relationship support
- Added relationship tool to available tools list in both deployment modes
- Updated README documentation with relationship examples
- Enhanced error handling for relationship creation

### 📚 Documentation
- Added relationship tool documentation to README.md and README_SSE.md
- Updated tool comparison table with new relationship functionality
- Added example conversations showing relationship creation

## [1.1.0] - 2025-06-17

### 🔧 Fixed
- **CRITICAL**: Resolved "Unexpected token 'A', 'API MCP Se'... is not valid JSON" error
- Fixed stdout contamination by removing print statements from MCP server output
- All debug/error messages now properly redirected to stderr
- Added missing `database` parameter requirement for Aras OAuth 2.0 authentication

### ✨ Added
- Proper OAuth 2.0 authentication using `requests-oauthlib` library
- Support for Aras Innovator 14+ OAuth 2.0 endpoints
- Database parameter validation for authentication
- Enhanced error handling with detailed OAuth responses
- Fallback authentication mechanism for robustness

### 🔄 Changed
- Updated tool names to be more descriptive and Aras-specific
- Improved API client to use correct Aras OData endpoints (`/Server/Odata`)
- Enhanced authentication flow with proper OAuth 2.0 scope and client ID
- Updated HTTP headers for better Aras REST API compatibility

### 📚 Documentation
- Comprehensive README update with OAuth 2.0 setup instructions
- Updated environment configuration examples
- Added troubleshooting section for common OAuth issues
- Included architecture diagram and authentication flow details

## [1.0.0] - 2025-06-12

### Added
- Initial release of Aras Innovator MCP Server
- OAuth authentication with Aras Innovator
- RESTful API integration using OData endpoints
- Five core tools:
  - `test_api_connection` - Test authentication
  - `api_get_items` - Query Aras data
  - `api_create_item` - Create new items
  - `api_call_method` - Call server methods
  - `api_get_list` - Get dropdown/list values
- Python-based implementation for easy deployment
- Comprehensive documentation and examples

### Features
- Secure credential management via .env files
- Support for all major Aras operations (CRUD)
- Integration with Claude Desktop via MCP protocol
- Error handling and connection validation 