# Sample Queries for Infinity Events MCP Server

This document provides examples of natural language queries you can use with the Infinity Events MCP Server for comprehensive security analysis and automated report generation.

## Universal Security Analysis

### All Security Events
```
Query: "Show all security events"
Timeframe: "last 24 hours"
Result: Gets all security events across all products with comprehensive analysis
```

### Product-Specific All Events
```
Query: "All security events on Harmony SASE"
Timeframe: "last 7 days"
Result: Gets all events from Harmony SASE with automated threat intelligence
```

### Multi-Product Overview
```
Query: "Security events from all products"
Timeframe: "last 30 days"
Result: Comprehensive overview across all products
```

## Severity-Based Analysis

### Critical Events Focus
```
Query: "Show critical security events on Harmony Endpoint"
Timeframe: "last 48 hours"
Result: Gets critical events with incident response playbook generation
```

### Multi-Severity Analysis
```
Query: "High and critical events across all products"
Timeframe: "last 7 days"
Result: Executive dashboard with risk scoring and priority matrix
```

## Network Investigation Queries

### Source IP Analysis
```
Query: "Show events from source 192.168.1.100"
Timeframe: "last 24 hours"
Result: Network flow analysis with IOC extraction and geolocation
```

### Destination Tracking
```
Query: "Find traffic to destination 10.0.0.1"
Timeframe: "last 12 hours"
Result: Target analysis with attack pattern identification
```

### Network Overview
```
Query: "All network security events"
Timeframe: "last 6 hours"
Result: Network topology analysis with flow diagrams
```

## Product-Specific Deep Dives

### Email Security
```
Query: "All security events on Harmony Email & Collaboration"
Timeframe: "last 3 days"
Result: Email threat landscape with phishing and malware analysis
```

### Endpoint Protection
```
Query: "Security events on Harmony Endpoint"
Timeframe: "last 1 week"
Result: Endpoint security posture with MITRE ATT&CK mapping
```

### Cloud Security
```
Query: "All events on Quantum Smart-1 Cloud"
Timeframe: "last 30 days"
Result: Cloud security assessment with compliance mapping
```

## Time-Based Investigations

### Real-Time Monitoring
```
Query: "All security events"
Timeframe: "last 2 hours"
Result: Real-time threat monitoring with immediate response recommendations
```

### Weekly Security Review
```
Query: "Security events across all products"
Timeframe: "last 7 days"
Result: Weekly security report with trend analysis and executive summary
```

### Monthly Compliance Report
```
Query: "All security events"
Timeframe: "last 30 days"
Result: Comprehensive compliance report with regulatory mapping
```

## Advanced Analysis Examples

### Threat Hunting
```
Query: "High severity events with suspicious source IPs"
Timeframe: "last 24 hours"
Result: Threat hunting report with IOC correlation and attribution
```

### Incident Investigation
```
Query: "Critical events on Harmony SASE"
Timeframe: "last 6 hours"
Result: Incident timeline with kill chain analysis and containment steps
```

### Baseline Analysis
```
Query: "All security events"
Timeframe: "last 7 days"
Result: Security baseline establishment with normal vs. anomalous activity
```

## Report Generation Prompts

After getting the logs, Claude automatically generates reports. You can also request specific analyses:

### Executive Briefing
```
"Create an executive security briefing focusing on:
- Business impact assessment
- Risk scoring and trends
- Resource allocation recommendations
- Strategic security improvements"
```

### Technical Deep Dive
```
"Generate a technical analysis including:
- MITRE ATT&CK technique breakdown
- IOC extraction and correlation
- Attack timeline reconstruction  
- Detailed remediation procedures"
```

### Compliance Assessment
```
"Produce a compliance report covering:
- SOX, GDPR, HIPAA, PCI-DSS requirements
- Control effectiveness measurement
- Audit trail completeness
- Regulatory risk assessment"
```

### Incident Response Plan
```
"Create an incident response plan with:
- Priority-based event classification
- Response team assignments
- Escalation procedures
- Communication templates"
```

## Visualization Requests

### Risk Visualization
```
"Create interactive visualizations showing:
- Risk heatmap by product and severity
- Timeline of security events with clustering
- Network flow diagram with threat indicators
- MITRE ATT&CK coverage matrix"
```

### Executive Dashboard
```
"Build an executive dashboard featuring:
- Real-time security metrics
- Trend analysis charts
- KPI scorecards
- Actionable recommendations"
```

## Tips for Effective Analysis

1. **Start Broad**: Begin with "all security events" to understand the overall landscape

2. **Use Natural Language**: The system understands conversational queries

3. **Leverage Timeframes**: Adjust time periods based on investigation needs

4. **Combine with Claude**: Ask for specific report formats and visualizations

5. **Save Critical Data**: Use `save_locally: true` for important investigations

6. **Follow Up**: Use the generated metadata to ask targeted follow-up questions

## Automated Report Features

The system automatically provides:

- **Executive Summaries** with business impact
- **Threat Intelligence** with IOC extraction
- **Incident Response** playbooks
- **Compliance Mapping** to regulations
- **Visualization Suggestions** for Claude
- **MITRE ATT&CK** technique identification
- **Risk Scoring** and prioritization

## Query Troubleshooting

If queries don't return expected results:

1. Check product name spelling in logs
2. Verify timeframe is reasonable for data volume
3. Ensure API credentials are correctly configured
4. Try broader queries first, then narrow down
5. Use the `check_credentials` tool to verify connectivity
