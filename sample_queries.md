# Sample Queries for Infinity Events MCP Server

This document provides examples of natural language queries you can use with the Infinity Events MCP Server.

## Security Analysis Queries

### Critical Events
```
Query: "Show me all critical security events on Harmony SASE"
Timeframe: "last 24 hours"
Result: Gets all critical severity events from Harmony SASE in the last day
```

### Multi-Severity Analysis
```
Query: "Generate report of high and critical events on Harmony Endpoint"
Timeframe: "last 7 days"
Result: Gets both high and critical severity events from Harmony Endpoint over the past week
```

### Product-Specific Investigations
```
Query: "Show security incidents on Quantum Smart-1 Cloud"
Timeframe: "last 30 days"
Result: Gets all security events from Quantum Smart-1 Cloud in the last month
```

## Network Investigation Queries

### Source IP Analysis
```
Query: "Show events from source 192.168.1.100 on Harmony Connect"
Timeframe: "last 48 hours"
Result: Gets all events originating from specific IP address
```

### Destination IP Tracking
```
Query: "Find traffic to destination 10.0.0.1 with critical severity"
Timeframe: "last 12 hours"
Result: Gets critical events targeting specific destination IP
```

### Combined IP and Severity
```
Query: "Show high severity events from source 172.16.0.0/16 on Harmony Browse"
Timeframe: "last 6 hours"
Result: Gets high severity events from specific IP range
```

## Threat Hunting Queries

### Email Security
```
Query: "Show critical email threats on Harmony Email & Collaboration"
Timeframe: "last 3 days"
Result: Gets critical email security events
```

### Mobile Security
```
Query: "Find mobile security incidents with high severity on Harmony Mobile"
Timeframe: "last 1 week"
Result: Gets high severity mobile security events
```

### Endpoint Protection
```
Query: "Show malware detection events on Harmony Endpoint"
Timeframe: "last 24 hours"
Result: Gets malware-related security events from endpoints
```

## Time-Based Analysis

### Recent Activity
```
Query: "Show all security events on Quantum Spark Management"
Timeframe: "last 2 hours"
Result: Gets very recent security activity
```

### Weekly Reports
```
Query: "Generate weekly security report for Harmony SASE with critical events"
Timeframe: "last 7 days"
Result: Gets comprehensive weekly critical events report
```

### Monthly Trends
```
Query: "Show security trends on all Harmony products"
Timeframe: "last 30 days"
Result: Gets monthly security event trends across products
```

## Advanced Filtering Examples

### Combined Filters
```
Query: "Show critical events from source 192.168.1.0/24 on Harmony SASE"
Timeframe: "last 12 hours"
Result: Combines IP range filtering with severity and product filtering
```

### Multi-Product Analysis
```
Query: "Compare security events between Harmony Connect and Harmony Endpoint"
Timeframe: "last 24 hours"
Result: Gets events from multiple products for comparison
```

## Report Generation Prompts

After getting the logs, you can ask Claude to generate various reports:

### Executive Summary
```
"Create an executive summary of the security events focusing on:
- Total number of events by severity
- Top threat types
- Affected systems
- Recommended actions"
```

### Technical Analysis
```
"Generate a technical analysis report including:
- Event timeline visualization
- Source IP analysis
- Attack pattern identification
- Detailed remediation steps"
```

### Compliance Report
```
"Create a compliance-focused report showing:
- Security event categories
- Response times
- Coverage across products
- Audit trail summary"
```

## Tips for Effective Queries

1. **Be Specific**: Include the exact product name (e.g., "Harmony SASE" not just "SASE")

2. **Use Clear Timeframes**: Be explicit about time periods ("last 24 hours" vs "yesterday")

3. **Combine Filters**: You can combine severity, IPs, and products in one query

4. **Follow Up**: After getting logs, ask Claude for specific analysis or visualizations

5. **Save Important Results**: Use `save_locally: true` for critical investigations

## Regional Endpoints

Remember to use the correct base URL for your region:

- **Global**: `https://cloudinfra-gw.portal.checkpoint.com`
- **India**: `https://cloudinfra-gw.in.portal.checkpoint.com`  
- **Australia**: `https://cloudinfra-gw.ap.portal.checkpoint.com`

## Query Troubleshooting

If queries don't return expected results:

1. Check product name spelling
2. Verify timeframe is reasonable
3. Ensure API credentials are correct
4. Check if account filtering is needed
5. Try broader queries first, then narrow down