# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-12

### Added
- Initial release of Aras Innovator MCP Server
- OAuth authentication with Aras Innovator
- RESTful API integration using OData endpoints
- Five core tools:
  - `test_aras_connection` - Test authentication
  - `aras_get_item` - Query Aras data
  - `aras_create_item` - Create new items
  - `aras_call_method` - Call server methods
  - `aras_get_list` - Get dropdown/list values
- Python-based implementation for easy deployment
- Comprehensive documentation and examples

### Features
- Secure credential management via .env files
- Support for all major Aras operations (CRUD)
- Integration with Claude Desktop via MCP protocol
- Error handling and connection validation 