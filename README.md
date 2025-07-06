# Infinity Events MCP Server

A Model Context Protocol (MCP) server that integrates Check Point Infinity Events API with Claude/Cursor Desktop (MCP client, enabling natural language queries for security event logs analysis and creating custom and out-of-box reports.

## Features

- 🔍 **Natural Language Queries**: Search logs using plain English (e.g., "Show all security events on Harmony SASE")
- 🌍 **Multi-Region Support**: Works with global and regional endpoints (.in.portal.checkpoint.com)
- 🛡️ **Secure Credential Management**: API keys stored safely in MCP configuration, never exposed in chat
- 📊 **Automated Report Generation**: Generates executive dashboards, threat intelligence, incident response, and compliance reports
- 📈 **Interactive Visualizations**: Claude creates charts, heatmaps, and network diagrams from log data
- 💾 **Flexible Output**: Save locally or stream to Claude for analysis
- 🔄 **Smart Pagination**: Handles large datasets with automatic pagination (pageLimit=100)
- ⚡ **Rate Limit Handling**: Graceful handling of API rate limits with user notifications
- 🎯 **MITRE ATT&CK Mapping**: Automatic technique identification and mapping
- 📋 **Compliance Ready**: SOX, GDPR, HIPAA, PCI-DSS regulatory mapping

## Supported Check Point Products

- Harmony SASE
- Harmony Endpoint  
- Harmony Mobile
- Harmony Email & Collaboration
- Harmony Browse
- Quantum Smart-1 Cloud
- Quantum Spark Management
- CloudGuard WAF
- CGNS

## Installation

### Prerequisites

- Python 3.7+
- Claude Desktop
- Check Point Infinity Events (Log-as-a-service) API credentials

### Setup

1. Clone this repository:
```bash
git clone https://github.com/presidentSU/infinity-events-mcp.git
cd infinity-events-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Claude Desktop by adding to your `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "python",
      "args": ["path/to/infinity_events_mcp_server.py"],
      "env": {
        "CHECKPOINT_CLIENT_ID": "your_client_id_here",
        "CHECKPOINT_ACCESS_KEY": "your_access_key_here",
        "CHECKPOINT_BASE_URL": "https://cloudinfra-gw.portal.checkpoint.com"
      }
    }
  }
}
```

- For windows path something similar to "args": ["C:\\Path\\to\\File\\infinity_mcp.py"]
- Fill "Your_client_id_here" & "your_access_key_here" with clientID & access Keys

**Security Note**: Credentials are loaded from environment variables and never exposed in chat conversations.

## Usage

### Basic Query Examples

1. **Security Events by Severity**:
   ```
   Query: "Show me all the critical security events"
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

### Optional Parameters

- **accounts**: Array of account IDs to filter (optional)
- **save_locally**: Boolean to save results to local JSON file (default: false)

## Automated Report Generation

The server automatically analyzes log data and provides metadata for Claude to generate professional cybersecurity reports:

### 📊 **Executive Dashboard**
- Risk scoring and severity distribution
- Timeline analysis with peak activity detection  
- Top affected products and systems
- Business impact assessment

### 🎯 **Threat Intelligence Report**
- IOC extraction (suspicious IPs, domains)
- MITRE ATT&CK technique mapping
- Attack pattern identification
- Geolocation and attribution analysis

### 🚨 **Incident Response Playbook**
- Event correlation and kill chain analysis
- Priority classification and response timelines
- Affected asset identification
- Containment and remediation recommendations

### 📋 **Compliance Report**
- Regulatory mapping (SOX, GDPR, HIPAA, PCI-DSS)
- Audit trail completeness assessment
- Control effectiveness scoring
- Coverage metrics per product

### 📈 **Interactive Visualizations**
- Risk heatmaps by product and severity
- Network flow diagrams
- Timeline charts with event clustering
- MITRE ATT&CK matrix coverage

#### Real world Example that works
- Provide me all the critical security events from Harmony SASE in the last 24 hrs.
- My user with email ID: <user@email.com>, can you generate a detailed report on his activity from H-SASE in the last 15 days.

## API Credentials Setup

1. Log into [Infinity Portal](https://portal.checkpoint.com)
2. Navigate to **GLOBAL SETTINGS > API Keys**
3. Create a new API Key with **Service** set to **Logs as a Service**
4. Note your Client ID and Secret Key

## Query Language

The server automatically parses natural language queries and converts them to appropriate API filters:

### App Name Detection
- "Harmony SASE" → `ci_app_name:"harmony sase"`
- "Harmony Endpoint" → `ci_app_name:"harmony endpoint"`
- "all products or no app name specified" → * (No product filter applied)

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
├── infinity_mcp.py    # Main MCP server
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
└── examples/                       # Usage examples
    └── sample_queries.md           # Sample query examples
    └── setup_guide.md              # Detailed Setup Guide.
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
- Local file saves are optional and controlled by user.

## Support

For issues and documentations:
1. Review the [Check Point API Documentation](https://sc1.checkpoint.com/documents/latest/APIs/index.html)
2. Visit [MCP Documentation](https://modelcontextprotocol.io/docs/) for MCP-specific questions

## Acknowledgments

- Check Point Software Technologies for the Infinity Events API
- Anthropic for the Model Context Protocol
- Made with <3 by leveraging Claude

---

**Note**: This is an unofficial tool and is not affiliated with or endorsed by Check Point Software Technologies.
