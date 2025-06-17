# Changelog

All notable changes to this project will be documented in this file.

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