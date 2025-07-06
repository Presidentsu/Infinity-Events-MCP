#!/usr/bin/env python3
"""
Infinity Events MCP Server
Integrates Check Point Infinity Events API with Claude Desktop
Credentials loaded from environment variables for security
"""

import asyncio
import json
import sys
import requests
import time
import re
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin


class InfinityEventsMCPServer:
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.auth_token = None
        self.token_expires_at = None
        
        # Load credentials from environment variables
        self.client_id = os.getenv('CHECKPOINT_CLIENT_ID')
        self.access_key = os.getenv('CHECKPOINT_ACCESS_KEY')
        self.base_url = os.getenv('CHECKPOINT_BASE_URL', 'https://cloudinfra-gw.portal.checkpoint.com')
        
        # Validate required credentials
        if not self.client_id or not self.access_key:
            print("ERROR: Missing required environment variables:", file=sys.stderr)
            print("Required: CHECKPOINT_CLIENT_ID, CHECKPOINT_ACCESS_KEY", file=sys.stderr)
            print("Optional: CHECKPOINT_BASE_URL (defaults to global endpoint)", file=sys.stderr)

    def parse_timeframe(self, timeframe_text: str) -> Dict[str, str]:
        """Parse natural language timeframe to start/end times."""
        now = datetime.utcnow()
        
        # Parse patterns like "last 24 hours", "30 days", "1 week"
        patterns = [
            (r'last\s+(\d+)\s*h(?:ours?)?', 'hours'),
            (r'last\s+(\d+)\s*d(?:ays?)?', 'days'),
            (r'last\s+(\d+)\s*w(?:eeks?)?', 'weeks'),
            (r'(\d+)\s*h(?:ours?)?', 'hours'),
            (r'(\d+)\s*d(?:ays?)?', 'days'),
            (r'(\d+)\s*w(?:eeks?)?', 'weeks')
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, timeframe_text.lower())
            if match:
                value = int(match.group(1))
                if unit == 'hours':
                    start_time = now - timedelta(hours=value)
                elif unit == 'days':
                    start_time = now - timedelta(days=value)
                elif unit == 'weeks':
                    start_time = now - timedelta(weeks=value)
                
                return {
                    "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "endTime": now.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
        
        # Default to last 24 hours if no pattern matches
        start_time = now - timedelta(hours=24)
        return {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endTime": now.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def parse_query_to_filter(self, query: str) -> tuple[str, str]:
        """Parse natural language query to extract app name and filter."""
        query_lower = query.lower()
        
        # Extract app name patterns
        app_patterns = [
            r'harmony\s+sase',
            r'harmony\s+connect',
            r'harmony\s+endpoint',
            r'harmony\s+mobile',
            r'harmony\s+email',
            r'harmony\s+browse',
            r'quantum\s+smart-1\s+cloud',
            r'quantum\s+spark'
        ]
        
        app_name = None
        for pattern in app_patterns:
            match = re.search(pattern, query_lower)
            if match:
                app_name = match.group(0).replace(' ', ' ')
                break
        
        # Check if user wants all security events (no specific filtering)
        if any(phrase in query_lower for phrase in ['all security events', 'all events', 'security events']):
            if app_name:
                return app_name, f'ci_app_name:"{app_name}"'
            else:
                return "all_products", "*"
        
        # Build filter components for specific queries
        filter_parts = []
        
        # Add app name filter
        if app_name:
            filter_parts.append(f'ci_app_name:"{app_name}"')
        
        # Extract severity
        if 'critical' in query_lower and 'high' in query_lower:
            filter_parts.append('(severity:"Critical" OR severity:"High")')
        elif 'critical' in query_lower:
            filter_parts.append('severity:"Critical"')
        elif 'high' in query_lower:
            filter_parts.append('severity:"High"')
        elif 'medium' in query_lower:
            filter_parts.append('severity:"Medium"')
        elif 'low' in query_lower:
            filter_parts.append('severity:"Low"')
        
        # Extract source IP if mentioned
        ip_match = re.search(r'(?:src|source)\s*[:\s]*([0-9.]+)', query_lower)
        if ip_match:
            filter_parts.append(f'src:"{ip_match.group(1)}"')
        
        # Extract destination IP
        dst_match = re.search(r'(?:dst|dest|destination)\s*[:\s]*([0-9.]+)', query_lower)
        if dst_match:
            filter_parts.append(f'dst:"{dst_match.group(1)}"')
        
        # Join filters with AND
        filter_string = ' AND '.join(filter_parts) if filter_parts else '*'
        
        return app_name or "unknown", filter_string

    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Infinity Events API using environment credentials."""
        if not self.client_id or not self.access_key:
            return {
                "success": False, 
                "error": "Missing credentials. Please set CHECKPOINT_CLIENT_ID and CHECKPOINT_ACCESS_KEY environment variables."
            }
        
        try:
            auth_url = urljoin(self.base_url, "/auth/external")
            
            payload = {
                "clientId": self.client_id,
                "accessKey": self.access_key
            }
            
            response = requests.post(
                auth_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.auth_token = data["data"]["token"]
                    # Token expires in 30 minutes
                    self.token_expires_at = time.time() + (30 * 60)
                    return {"success": True, "message": "Authentication successful"}
                else:
                    return {"success": False, "error": "Authentication failed - invalid credentials"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Authentication error: {str(e)}"}

    async def search_logs(self, filter_str: str, timeframe: Dict[str, str], 
                         accounts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Initiate log search query."""
        if not self.auth_token or time.time() > self.token_expires_at:
            auth_result = await self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
        try:
            search_url = urljoin(self.base_url, "/app/laas-logs-api/api/logs_query")
            
            payload = {
                "filter": filter_str,
                "limit": 10000,  # High limit for comprehensive search
                "pageLimit": 100,  # Keep pagination manageable
                "timeframe": timeframe
            }
            
            if accounts:
                payload["accounts"] = accounts
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(search_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True, "taskId": data["data"]["taskId"]}
                else:
                    return {"success": False, "error": "Search request failed"}
            elif response.status_code == 429:
                return {"success": False, "error": "Rate limit exceeded. Please wait and try again."}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Search error: {str(e)}"}

    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check the status of a search task."""
        if not self.auth_token:
            return {"success": False, "error": "No authentication token"}
        
        try:
            status_url = urljoin(self.base_url, f"/app/laas-logs-api/api/logs_query/{task_id}")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(status_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "success": True,
                        "state": data["data"]["state"],
                        "pageTokens": data["data"].get("pageTokens", []),
                        "errors": data["data"].get("errors", [])
                    }
                else:
                    return {"success": False, "error": "Status check failed"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Status check error: {str(e)}"}

    async def retrieve_logs(self, task_id: str, page_token: str) -> Dict[str, Any]:
        """Retrieve logs for a specific page."""
        if not self.auth_token:
            return {"success": False, "error": "No authentication token"}
        
        try:
            retrieve_url = urljoin(self.base_url, "/app/laas-logs-api/api/logs_query/retrieve")
            
            payload = {
                "taskId": task_id,
                "pageToken": page_token
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(retrieve_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "success": True,
                        "records": data["data"]["records"],
                        "recordsCount": data["data"]["recordsCount"],
                        "nextPageToken": data["data"].get("nextPageToken")
                    }
                else:
                    return {"success": False, "error": "Log retrieval failed"}
            elif response.status_code == 429:
                return {"success": False, "error": "Rate limit exceeded. Please wait and try again."}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Retrieval error: {str(e)}"}

    async def get_all_logs(self, query: str, timeframe_text: str, 
                          accounts: Optional[List[str]] = None,
                          save_locally: bool = False) -> Dict[str, Any]:
        """Complete workflow to get all logs matching the query."""
        
        # Step 1: Parse query and timeframe
        app_name, filter_str = self.parse_query_to_filter(query)
        timeframe = self.parse_timeframe(timeframe_text)
        
        # Step 2: Initiate search (authentication handled automatically)
        search_result = await self.search_logs(filter_str, timeframe, accounts)
        if not search_result["success"]:
            return search_result
        
        task_id = search_result["taskId"]
        
        # Step 3: Wait for completion and get page tokens
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            status_result = await self.check_task_status(task_id)
            if not status_result["success"]:
                return status_result
            
            state = status_result["state"]
            if state in ["Completed", "Ready"]:
                page_tokens = status_result["pageTokens"]
                break
            elif state == "Failed":
                return {"success": False, "error": "Search task failed", "errors": status_result["errors"]}
            elif state in ["Processing", "Pending"]:
                await asyncio.sleep(2)
                attempt += 1
                continue
            else:
                return {"success": False, "error": f"Unknown task state: {state}"}
        
        if attempt >= max_attempts:
            return {"success": False, "error": "Task timed out"}
        
        # Step 4: Retrieve all pages
        all_records = []
        total_records = 0
        
        for page_token in page_tokens:
            retrieve_result = await self.retrieve_logs(task_id, page_token)
            if not retrieve_result["success"]:
                return retrieve_result
            
            all_records.extend(retrieve_result["records"])
            total_records += retrieve_result["recordsCount"]
            
            # Handle pagination within a page
            next_token = retrieve_result.get("nextPageToken")
            while next_token:
                retrieve_result = await self.retrieve_logs(task_id, next_token)
                if not retrieve_result["success"]:
                    break
                
                all_records.extend(retrieve_result["records"])
                total_records += retrieve_result["recordsCount"]
                next_token = retrieve_result.get("nextPageToken")
        
        # Step 5: Save locally if requested
        if save_locally:
            filename = f"infinity_events_{int(time.time())}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        "query": query,
                        "timeframe": timeframe_text,
                        "app_name": app_name,
                        "filter": filter_str,
                        "total_records": total_records,
                        "records": all_records
                    }, f, indent=2)
                
                return {
                    "success": True,
                    "message": f"Retrieved {total_records} records and saved to {filename}",
                    "filename": filename,
                    "total_records": total_records,
                    "sample_records": all_records[:5] if all_records else []
                }
            except Exception as e:
                return {"success": False, "error": f"Failed to save file: {str(e)}"}
        
    def generate_report_metadata(self, records: List[Dict], query_info: Dict) -> Dict[str, Any]:
        """Generate cybersecurity report metadata from log records."""
        if not records:
            return {"report_suggestions": []}
        
        # Analyze the records
        severity_counts = {}
        product_counts = {}
        source_ips = set()
        dest_ips = set()
        event_types = set()
        attack_techniques = set()
        timeline_data = []
        
        for record in records:
            # Severity analysis
            severity = record.get('severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Product analysis
            product = record.get('ci_app_name', record.get('product', 'Unknown'))
            product_counts[product] = product_counts.get(product, 0) + 1
            
            # Network analysis
            if record.get('src'):
                source_ips.add(record['src'])
            if record.get('dst'):
                dest_ips.add(record['dst'])
            
            # Event type analysis
            if record.get('action'):
                event_types.add(record['action'])
            if record.get('rule_name'):
                event_types.add(record['rule_name'])
            
            # Timeline data
            if record.get('time'):
                timeline_data.append({
                    'timestamp': record['time'],
                    'severity': severity,
                    'product': product,
                    'event': record.get('action', 'Event')
                })
            
            # MITRE ATT&CK techniques (common patterns)
            event_text = str(record).lower()
            if 'lateral movement' in event_text or 'privilege escalation' in event_text:
                attack_techniques.add('Lateral Movement')
            if 'data exfiltration' in event_text or 'data transfer' in event_text:
                attack_techniques.add('Exfiltration')
            if 'malware' in event_text or 'virus' in event_text:
                attack_techniques.add('Malware Execution')
            if 'phishing' in event_text or 'social engineering' in event_text:
                attack_techniques.add('Initial Access')
        
        # Generate report metadata
        total_events = len(records)
        critical_events = severity_counts.get('Critical', 0)
        high_events = severity_counts.get('High', 0)
        
        report_metadata = {
            "executive_dashboard": {
                "total_events": total_events,
                "critical_count": critical_events,
                "high_count": high_events,
                "risk_score": min(100, (critical_events * 10 + high_events * 5)),
                "severity_distribution": severity_counts,
                "top_products": dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "timeframe": query_info.get('timeframe', 'Unknown'),
                "chart_suggestions": [
                    "Pie chart of severity distribution",
                    "Bar chart of events by product",
                    "Timeline of critical/high events"
                ]
            },
            
            "threat_intelligence": {
                "unique_source_ips": len(source_ips),
                "unique_dest_ips": len(dest_ips),
                "top_source_ips": list(source_ips)[:10],
                "top_dest_ips": list(dest_ips)[:10],
                "attack_techniques": list(attack_techniques),
                "event_types": list(event_types)[:10],
                "ioc_indicators": {
                    "suspicious_ips": [ip for ip in source_ips if self.is_suspicious_ip(ip)],
                    "high_frequency_events": [evt for evt in event_types if 'block' in evt.lower() or 'deny' in evt.lower()]
                },
                "mitre_mapping": list(attack_techniques),
                "recommendations": [
                    "Block suspicious source IPs",
                    "Investigate high-frequency event sources",
                    "Review MITRE ATT&CK techniques for defense gaps"
                ]
            },
            
            "incident_response": {
                "incidents_requiring_action": critical_events + high_events,
                "affected_systems": list(product_counts.keys()),
                "timeline_analysis": {
                    "total_events": len(timeline_data),
                    "peak_activity": self.find_peak_activity(timeline_data),
                    "event_clustering": "Multiple events detected in short timeframe" if total_events > 50 else "Isolated events"
                },
                "response_priorities": [
                    f"Critical: {critical_events} events requiring immediate attention",
                    f"High: {high_events} events requiring urgent review",
                    f"Medium/Low: {total_events - critical_events - high_events} events for monitoring"
                ],
                "containment_suggestions": [
                    "Isolate affected systems showing critical events",
                    "Block malicious IPs at perimeter",
                    "Enable enhanced monitoring on affected products"
                ]
            },
            
            "compliance_report": {
                "total_events": total_events,
                "security_controls_triggered": len(event_types),
                "coverage_by_product": product_counts,
                "audit_trail": {
                    "events_logged": total_events,
                    "retention_period": query_info.get('timeframe', 'Unknown'),
                    "data_integrity": "Complete" if total_events > 0 else "No events found"
                },
                "regulatory_mapping": {
                    "SOX": f"{critical_events + high_events} material security events",
                    "GDPR": f"Data protection events: {len([r for r in records if 'data' in str(r).lower()])}",
                    "HIPAA": f"Access control events: {len([r for r in records if 'access' in str(r).lower()])}",
                    "PCI-DSS": f"Network security events: {len([r for r in records if 'network' in str(r).lower()])}"
                },
                "compliance_score": max(0, 100 - (critical_events * 5) - (high_events * 2))
            },
            
            "visualization_suggestions": [
                {
                    "type": "risk_heatmap",
                    "title": "Security Risk Heatmap by Product and Severity",
                    "data_source": "severity_distribution + product_counts"
                },
                {
                    "type": "timeline_chart", 
                    "title": "Security Events Timeline",
                    "data_source": "timeline_data"
                },
                {
                    "type": "network_diagram",
                    "title": "Source IP to Destination IP Flow",
                    "data_source": "source_ips + dest_ips"
                },
                {
                    "type": "mitre_attack_matrix",
                    "title": "MITRE ATT&CK Technique Coverage",
                    "data_source": "attack_techniques"
                }
            ],
            
            "report_prompts": {
                "executive": "Create an executive security dashboard showing risk levels, key metrics, and business impact from these security events.",
                "technical": "Generate a detailed technical analysis including attack vectors, IOCs, and specific remediation steps.",
                "compliance": "Produce a compliance report mapping these events to regulatory requirements and control effectiveness.",
                "incident": "Create an incident response playbook based on the detected security events and their severity."
            }
        }
        
        return report_metadata
    
    def is_suspicious_ip(self, ip: str) -> bool:
        """Basic suspicious IP detection (can be enhanced with threat intel)."""
        if not ip or ip == "0.0.0.0":
            return False
        
        # Basic patterns for suspicious IPs
        suspicious_patterns = [
            # Private ranges being used externally (simplified check)
            # Known malicious ranges (example - would use real threat intel)
        ]
        
        # Check for non-RFC1918 IPs (simplified)
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                first_octet = int(parts[0])
                # Very basic check - in real implementation would use threat intel feeds
                return first_octet in [1, 2, 5, 14, 23, 27, 31, 37, 42, 46, 49, 50]  # Example suspicious ranges
            except ValueError:
                return False
        return False
    
    def find_peak_activity(self, timeline_data: List[Dict]) -> str:
        """Find peak activity periods in timeline data."""
        if not timeline_data:
            return "No timeline data available"
        
        # Simple peak detection - count events per hour
        hour_counts = {}
        for event in timeline_data:
            timestamp = event.get('timestamp', '')
            if timestamp:
                # Extract hour from timestamp (simplified)
                hour = timestamp.split('T')[1][:2] if 'T' in timestamp else '00'
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            peak_count = hour_counts[peak_hour]
            return f"Peak activity at {peak_hour}:00 UTC ({peak_count} events)"
        
        return "No clear peak detected"

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Handle notifications (no response needed)
        if request_id is None:
            if method == "notifications/initialized":
                self.initialized = True
            return None
        
        try:
            if method == "initialize":
                # Include credential status in initialization response
                creds_status = "✅ Configured" if self.client_id and self.access_key else "❌ Missing"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": self.name,
                            "version": "1.0.0",
                            "description": f"Check Point Infinity Events API integration. Credentials: {creds_status}. Endpoint: {self.base_url}"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "search_infinity_events",
                                "description": "Search Check Point Infinity Events logs with natural language queries. Credentials loaded from environment variables.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Natural language query (e.g., 'critical security events on Harmony SASE')"
                                        },
                                        "timeframe": {
                                            "type": "string",
                                            "description": "Time period (e.g., 'last 24 hours', '7 days', '1 week')",
                                            "default": "last 24 hours"
                                        },
                                        "accounts": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional: Account IDs to filter"
                                        },
                                        "save_locally": {
                                            "type": "boolean",
                                            "description": "Save results to local file (default: false)",
                                            "default": False
                                        }
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "check_credentials",
                                "description": "Check the status of API credentials and connection",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "search_infinity_events":
                    result = await self.get_all_logs(
                        query=arguments.get("query", ""),
                        timeframe_text=arguments.get("timeframe", "last 24 hours"),
                        accounts=arguments.get("accounts"),
                        save_locally=arguments.get("save_locally", False)
                    )
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }
                
                elif tool_name == "check_credentials":
                    # Test authentication
                    auth_result = await self.authenticate()
                    
                    status = {
                        "client_id_configured": bool(self.client_id),
                        "access_key_configured": bool(self.access_key),
                        "base_url": self.base_url,
                        "authentication_test": auth_result
                    }
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(status, indent=2)
                                }
                            ]
                        }
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


async def main():
    """Main entry point."""
    server = InfinityEventsMCPServer("infinity-events-mcp-server")
    
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                if response is not None:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                continue
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
