# Infinity Events MCP Server

A Model Context Protocol (MCP) server that integrates Check Point Infinity Events API with Claude Desktop, enabling natural language queries for security event logs analysis.

## Features

- 🔍 **Natural Language Queries**: Search logs using plain English (e.g., "Show critical events on Harmony SASE")
- 🌍 **Multi-Region Support**: Works with global and regional endpoints (.in.portal.checkpoint.com)
- 📊 **AI-Powered Analysis**: Stream results directly to Claude for interactive reports and visualizations
- 💾 **Flexible Output**: Save locally or stream to Claude for analysis
- 🔄 **Smart Pagination**: Handles large datasets with automatic pagination (pageLimit=100)
- ⚡ **Rate Limit Handling**: Graceful handling of API rate limits with user notifications
- 🛡️ **Comprehensive Error Handling**: Robust error handling for production use

## Supported Check Point Products

- Harmony Connect
- Harmony Endpoint  
- Harmony Mobile
- Harmony Email & Collaboration
- Harmony Browse
- Quantum Smart-1 Cloud
- Quantum Spark Management

## Installation

### Prerequisites

- Python 3.7+
- Claude Desktop
- Check Point Infinity Portal API credentials

### Setup

1. Clone this repository:
```bash
git clone https://github.com/your-username/infinity-events-mcp-server.git
cd infinity-events-mcp-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Claude Desktop by adding to your `claude_desktop_config.json`:

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "python",
      "args": ["path/to/infinity_events_mcp_server.py"]
    }
  }
}
```

## Usage

### Basic Query Examples

1. **Security Events by Severity**:
   ```
   Query: "Show me critical security events on Harmony SASE"
   Timeframe: "last 24 hours"
   ```

2. **Multi-Product Analysis**:
   ```
   Query: "Generate report of high and critical events on Harmony Endpoint" 
   Timeframe: "last 7 days"
   ```

3. **Source IP Investigation**:
   ```
   Query: "Show events from source 192.168.1.100 on Quantum Smart-1 Cloud"
   Timeframe: "last 30 days"
   ```

### Required Parameters

- **query**: Natural language description of what you're looking for
- **timeframe**: Time period (e.g., "last 24 hours", "7 days", "1 week")
- **base_url**: API endpoint URL
  - Global: `https://cloudinfra-gw.portal.checkpoint.com`
  - India: `https://cloudinfra-gw.in.portal.checkpoint.com`
  - Australia: `https://cloudinfra-gw.ap.portal.checkpoint.com`
- **client_id**: Your API Client ID
- **access_key**: Your API Access Key

### Optional Parameters

- **accounts**: Array of account IDs to filter (optional)
- **save_locally**: Boolean to save results to local JSON file (default: false)

## API Credentials Setup

1. Log into [Infinity Portal](https://portal.checkpoint.com)
2. Navigate to **GLOBAL SETTINGS > API Keys**
3. Create a new API Key with **Service** set to **Horizon Logs & Events**
4. Note your Client ID and Secret Key

## Query Language

The server automatically parses natural language queries and converts them to appropriate API filters:

### App Name Detection
- "Harmony SASE" → `ci_app_name:"harmony sase"`
- "Harmony Endpoint" → `ci_app_name:"harmony endpoint"`
- "Quantum Smart-1 Cloud" → `ci_app_name:"quantum smart-1 cloud"`

### Severity Filtering
- "critical events" → `severity:"Critical"`
- "high and critical" → `(severity:"Critical" OR severity:"High")`
- "medium severity" → `severity:"Medium"`

### IP Address Filtering
- "source 1.1.1.1" → `src:"1.1.1.1"`
- "destination 2.2.2.2" → `dst:"2.2.2.2"`

### Timeframe Parsing
- "last 24 hours" → Last 24 hours from now
- "7 days" → Last 7 days from now  
- "1 week" → Last week from now

## Example Response

```json
{
  "success": true,
  "message": "Retrieved 150 records",
  "total_records": 150,
  "query_info": {
    "original_query": "critical security events on Harmony SASE",
    "timeframe": "last 24 hours",
    "app_name": "harmony sase",
    "filter": "ci_app_name:\"harmony sase\" AND severity:\"Critical\""
  },
  "records": [...]
}
```

## Error Handling

The server provides detailed error messages for common issues:

- **Authentication failures**: Invalid credentials or expired tokens
- **Rate limiting**: API quota exceeded notifications
- **Network errors**: Connection timeouts and retry suggestions
- **Query parsing**: Invalid filter syntax corrections

## Development

### Project Structure
```
infinity-events-mcp-server/
├── infinity_events_mcp_server.py    # Main MCP server
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
└── examples/                       # Usage examples
    └── sample_queries.md           # Sample query examples
```

### Dependencies

- `requests`: HTTP client for API calls
- `asyncio`: Async/await support
- `re`: Regular expression parsing
- `datetime`: Time manipulation
- `json`: JSON handling

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Rate Limits

The Infinity Events API has the following rate limits:
- **Search requests**: 100 requests per minute per user
- **Status checks**: 200 requests per minute per user
- **Log retrieval**: 200 requests per minute per user

The server automatically handles these limits and notifies users when limits are exceeded.

## Security Considerations

- API credentials are passed as parameters and not stored
- Authentication tokens expire after 30 minutes for security
- All API communications use HTTPS
- Local file saves are optional and controlled by user

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the [Issues](https://github.com/your-username/infinity-events-mcp-server/issues) page
2. Review the [Check Point API Documentation](https://sc1.checkpoint.com/documents/latest/APIs/index.html)
3. Visit [MCP Documentation](https://modelcontextprotocol.io/docs/) for MCP-specific questions

## Acknowledgments

- Check Point Software Technologies for the Infinity Events API
- Anthropic for the Model Context Protocol
- Claude Desktop integration team

---

**Note**: This is an unofficial tool and is not affiliated with or endorsed by Check Point Software Technologies.
