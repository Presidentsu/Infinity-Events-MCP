# Setup Guide for Infinity Events MCP Server

This guide walks you through setting up the Infinity Events MCP Server with Claude Desktop.

## Prerequisites

- Python 3.7 or higher
- Claude Desktop application
- Check Point Infinity Portal access with API key creation permissions

## Step 1: Python Setup

### Windows
1. Download Python from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Open Command Prompt and verify: `python --version`

### macOS
```bash
# Install using Homebrew (recommended)
brew install python

# Or download from python.org
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

## Step 2: Download and Install MCP Server

1. **Clone or Download**:
```bash
git clone https://github.com/your-username/infinity-events-mcp.git
cd infinity-events-mcp
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Test the Server**:
```bash
python infinity_mcp.py
```
   - If it starts without errors, press `Ctrl+C` to stop

## Step 3: Get Check Point API Credentials

1. **Log into Infinity Portal**:
   - EU: https://portal.checkpoint.com
   - India: https://in.portal.checkpoint.com
   - Australia: https://au.portal.checkpoint.com

2. **Navigate to API Keys**:
   - Go to **GLOBAL SETTINGS** → **API Keys**

3. **Create New API Key**:
   - Click **"Add API Key"**
   - **Name**: `Infinity Events MCP Server`
   - **Service**: Select **"Logs as a Service"**
   - **Expiration**: Set as needed (recommend 1 weel)
   - Click **"Generate"**

4. **Save Credentials**:
   - **Client ID**: Copy and save securely
   - **Secret Key**: Copy and save securely (shown only once!)

## Step 4: Configure Claude Desktop

### Locate Configuration File

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS**:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux**:
```
~/.config/Claude/claude_desktop_config.json
```

### Edit Configuration

1. **Create/Edit the file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "python",
      "args": ["C:\\path\\to\\infinity_mcp.py"]
    }
  }
}
```

2. **Update the path**:
   - **Windows**: `"C:\\Users\\YourName\\infinity-events-mcp\\infinity_mcp.py"`
   - **macOS/Linux**: `"/Users/YourName/infinity-events-mcp/infinity_mcp.py"`

### Full Configuration Example

```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "python",
      "args": ["/full/path/to/infinity_events_mcp_server.py"],
      "env": {
        "CHECKPOINT_CLIENT_ID": "your_client_ID_here", 
        "CHECKPOINT_ACCESS_KEY": "your_Secret_Key_here", 
        "CHECKPOINT_BASE_URL": "https://cloudinfra-gw.portal.checkpoint.com"
	  }
    }
  }
}
```
**Reminder** - Here the config base url is pointed to EU, see which gateway is in use your organization, if its in it will be "cloudinfra-gw.in.portal.checkpoint.com".
## Step 5: Test the Integration

1. **Restart Claude Desktop** completely

2. **Check Server Status**:
   - Look for "infinity-events" in available tools
   - Should see `search_infinity_events` tool

3. **Test Query**:
```
Use the infinity events tool to search for "critical events on Harmony SASE" in the "last 24 hours"
```
OR
```
Use the infinity events tool to search for all the critical events in the last 24 hours
```
The tool will automatically:
- Use credentials from your configuration securely
- Parse your natural language query  
- Generate comprehensive cybersecurity reports
- Provide Claude with rich metadata for visualizations

## Troubleshooting

### Common Issues

**1. "Server not found" or "Connection failed"**
- Check the file path in configuration
- Ensure Python is in PATH
- Verify file permissions

**2. "Authentication failed"**
- Verify Client ID and Secret Key
- Check API key permissions in Infinity Portal
- Ensure correct base URL for your region

**3. "No results returned"**
- Try broader queries first
- Check if account filtering is needed
- Verify timeframe is reasonable

**4. "Rate limit exceeded"**
- Wait a few minutes before retrying
- Consider using shorter timeframes
- Check if multiple users are using same API key

### Debug Steps

1. **Test Python directly**:
```bash
cd /path/to/infinity-events-mcp-server
python infinity_events_mcp_server.py
```

2. **Check dependencies**:
```bash
pip list | grep requests
```

3. **Verify file paths**:
```bash
# Windows
dir "C:\path\to\infinity_events_mcp_server.py"

# macOS/Linux  
ls -la /path/to/infinity_events_mcp_server.py
```

4. **Test API connection**:
   Use a simple test query with verbose error messages

### Advanced Configuration

**Custom Python Environment**:
```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "/path/to/custom/python",
      "args": ["/path/to/infinity_events_mcp_server.py"],
      "cwd": "/path/to/infinity-events-mcp-server"
    }
  }
}
```

**Environment Variables**:
```json
{
  "mcpServers": {
    "infinity-events": {
      "command": "python",
      "args": ["/path/to/infinity_events_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/custom/python/path",
        "REQUESTS_CA_BUNDLE": "/path/to/ca-bundle.crt"
      }
    }
  }
}
```

## Regional Setup Notes

### India Region
- Base URL: `https://cloudinfra-gw.in.portal.checkpoint.com`
- Portal: https://portal.checkpoint.com (same login)

### Australia Region  
- Base URL: `https://cloudinfra-gw.ap.portal.checkpoint.com`
- Portal: https://portal.checkpoint.com (same login)

### EU Region
- Base URL: `https://cloudinfra-gw.portal.checkpoint.com`
- Portal: https://portal.checkpoint.com

## Security Best Practices

1. **Protect API Credentials**:
   - Never commit credentials to version control
   - Use environment variables for production
   - Rotate keys regularly

2. **Network Security**:
   - Ensure HTTPS connections
   - Use firewall rules if needed
   - Monitor API usage

3. **Access Control**:
   - Use separate keys for different environments
   - Monitor API key usage in Infinity Portal

## Next Steps

After successful setup:
1. Try the sample queries from `sample_queries.md`
2. Experiment with different timeframes and products
3. Ask Claude to create visualizations and reports
4. Set up local file saving for important investigations

## Support

If you encounter issues:
1. Check this setup guide first
2. Review the main README.md
3. Check the GitHub Issues page
4. Verify Check Point API documentation
