#!/usr/bin/env python3
"""
Infinity Events MCP Server
Integrates Check Point Infinity Events API with Claude Desktop
"""

import asyncio
import json
import sys
import requests
import time
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin


class InfinityEventsMCPServer:
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self.auth_token = None
        self.base_url = None
        self.token_expires_at = None

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
        
        # Build filter components
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

    async def authenticate(self, base_url: str, client_id: str, access_key: str) -> Dict[str, Any]:
        """Authenticate with Infinity Events API."""
        try:
            auth_url = urljoin(base_url, "/auth/external")
            
            payload = {
                "clientId": client_id,
                "accessKey": access_key
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
                    self.base_url = base_url
                    # Token expires in 30 minutes
                    self.token_expires_at = time.time() + (30 * 60)
                    return {"success": True, "message": "Authentication successful"}
                else:
                    return {"success": False, "error": "Authentication failed"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Authentication error: {str(e)}"}

    async def search_logs(self, filter_str: str, timeframe: Dict[str, str], 
                         accounts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Initiate log search query."""
        if not self.auth_token or time.time() > self.token_expires_at:
            return {"success": False, "error": "Authentication token expired or missing"}
        
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

    async def get_all_logs(self, query: str, timeframe_text: str, base_url: str,
                          client_id: str, access_key: str, accounts: Optional[List[str]] = None,
                          save_locally: bool = False) -> Dict[str, Any]:
        """Complete workflow to get all logs matching the query."""
        
        # Step 1: Authenticate
        auth_result = await self.authenticate(base_url, client_id, access_key)
        if not auth_result["success"]:
            return auth_result
        
        # Step 2: Parse query and timeframe
        app_name, filter_str = self.parse_query_to_filter(query)
        timeframe = self.parse_timeframe(timeframe_text)
        
        # Step 3: Initiate search
        search_result = await self.search_logs(filter_str, timeframe, accounts)
        if not search_result["success"]:
            return search_result
        
        task_id = search_result["taskId"]
        
        # Step 4: Wait for completion and get page tokens
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
        
        # Step 5: Retrieve all pages
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
        
        # Step 6: Save locally if requested
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
        
        return {
            "success": True,
            "message": f"Retrieved {total_records} records",
            "total_records": total_records,
            "records": all_records,
            "query_info": {
                "original_query": query,
                "timeframe": timeframe_text,
                "app_name": app_name,
                "filter": filter_str
            }
        }

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
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": self.name,
                            "version": "1.0.0"
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
                                "description": "Search Check Point Infinity Events logs with natural language queries",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Natural language query (e.g., 'critical security events on Harmony SASE')"
                                        },
                                        "timeframe": {
                                            "type": "string",
                                            "description": "Time period (e.g., 'last 24 hours', '7 days', '1 week')"
                                        },
                                        "base_url": {
                                            "type": "string",
                                            "description": "API base URL (e.g., https://cloudinfra-gw.portal.checkpoint.com, https://cloudinfra-gw.in.portal.checkpoint.com)"
                                        },
                                        "client_id": {
                                            "type": "string",
                                            "description": "API Client ID"
                                        },
                                        "access_key": {
                                            "type": "string",
                                            "description": "API Access Key"
                                        },
                                        "accounts": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional: Account IDs to filter"
                                        },
                                        "save_locally": {
                                            "type": "boolean",
                                            "description": "Save results to local file (default: false)"
                                        }
                                    },
                                    "required": ["query", "timeframe", "base_url", "client_id", "access_key"]
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
                        base_url=arguments.get("base_url", ""),
                        client_id=arguments.get("client_id", ""),
                        access_key=arguments.get("access_key", ""),
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
