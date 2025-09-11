#!/usr/bin/env python3
"""
API Endpoint Extraction Script for System Rebellion Backend
Extracts all FastAPI routes and WebSocket endpoints
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

def extract_api_endpoints(root_dir: str = ".") -> Dict:
    """
    Extract all API endpoints from Python files in the project
    """
    endpoints = {
        "http_routes": [],
        "websocket_routes": [],
        "file_summary": {}
    }
    
    # Patterns to match FastAPI routes
    http_pattern = re.compile(
        r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
    )
    
    websocket_pattern = re.compile(
        r'@(?:app|router)\.websocket\s*\(\s*["\']([^"\']+)["\']'
    )
    
    # Function definition pattern to get handler names
    function_pattern = re.compile(r'def\s+(\w+)\s*\(')
    
    print("🔍 EXTRACTING API ENDPOINTS FROM SYSTEM REBELLION BACKEND...")
    print("=" * 60)
    
    # Walk through all Python files
    for root, dirs, files in os.walk(root_dir):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', 'env']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                    
                    file_endpoints = {
                        "http_routes": [],
                        "websocket_routes": []
                    }
                    
                    # Extract endpoints line by line
                    for i, line in enumerate(lines, 1):
                        # HTTP routes
                        http_match = http_pattern.search(line)
                        if http_match:
                            method = http_match.group(1).upper()
                            path = http_match.group(2)
                            
                            # Try to find the function name in the next few lines
                            handler_name = "unknown"
                            for j in range(i, min(i + 5, len(lines))):
                                func_match = function_pattern.search(lines[j])
                                if func_match:
                                    handler_name = func_match.group(1)
                                    break
                            
                            route_info = {
                                "method": method,
                                "path": path,
                                "handler": handler_name,
                                "file": relative_path,
                                "line": i
                            }
                            
                            endpoints["http_routes"].append(route_info)
                            file_endpoints["http_routes"].append(route_info)
                        
                        # WebSocket routes
                        ws_match = websocket_pattern.search(line)
                        if ws_match:
                            path = ws_match.group(1)
                            
                            # Try to find the function name
                            handler_name = "unknown"
                            for j in range(i, min(i + 5, len(lines))):
                                func_match = function_pattern.search(lines[j])
                                if func_match:
                                    handler_name = func_match.group(1)
                                    break
                            
                            ws_info = {
                                "path": path,
                                "handler": handler_name,
                                "file": relative_path,
                                "line": i
                            }
                            
                            endpoints["websocket_routes"].append(ws_info)
                            file_endpoints["websocket_routes"].append(ws_info)
                    
                    # Only add files that have endpoints
                    if file_endpoints["http_routes"] or file_endpoints["websocket_routes"]:
                        endpoints["file_summary"][relative_path] = file_endpoints
                        
                except Exception as e:
                    print(f"❌ Error reading {relative_path}: {e}")
    
    return endpoints

def print_endpoints_summary(endpoints: Dict):
    """
    Print a formatted summary of all endpoints
    """
    print(f"\n📊 ENDPOINTS SUMMARY")
    print("=" * 40)
    print(f"HTTP Routes Found: {len(endpoints['http_routes'])}")
    print(f"WebSocket Routes Found: {len(endpoints['websocket_routes'])}")
    print(f"Files with Endpoints: {len(endpoints['file_summary'])}")
    
    print(f"\n🌐 HTTP ENDPOINTS:")
    print("-" * 40)
    for route in sorted(endpoints['http_routes'], key=lambda x: x['path']):
        print(f"{route['method']:6} {route['path']:30} → {route['handler']} ({route['file']}:{route['line']})")
    
    print(f"\n🔌 WEBSOCKET ENDPOINTS:")
    print("-" * 40)
    for ws in sorted(endpoints['websocket_routes'], key=lambda x: x['path']):
        print(f"WS     {ws['path']:30} → {ws['handler']} ({ws['file']}:{ws['line']})")

def generate_frontend_config(endpoints: Dict) -> str:
    """
    Generate TypeScript configuration for frontend
    """
    config = {
        "API_BASE_URL": "http://localhost:8000",
        "WS_BASE_URL": "ws://localhost:8000",
        "endpoints": {
            "auth": [],
            "users": [],
            "agents": [],
            "metrics": [],
            "websockets": []
        }
    }
    
    # Categorize endpoints
    for route in endpoints['http_routes']:
        path = route['path']
        if any(keyword in path for keyword in ['auth', 'login', 'register', 'token']):
            config['endpoints']['auth'].append({
                "method": route['method'],
                "path": path,
                "handler": route['handler']
            })
        elif any(keyword in path for keyword in ['user', 'profile']):
            config['endpoints']['users'].append({
                "method": route['method'],
                "path": path,
                "handler": route['handler']
            })
        elif any(keyword in path for keyword in ['agent', 'hawkington', 'snail', 'hamster', 'stick', 'qsp', 'vic20']):
            config['endpoints']['agents'].append({
                "method": route['method'],
                "path": path,
                "handler": route['handler']
            })
        elif any(keyword in path for keyword in ['metric', 'system', 'cpu', 'memory', 'disk', 'network']):
            config['endpoints']['metrics'].append({
                "method": route['method'],
                "path": path,
                "handler": route['handler']
            })
    
    # Add WebSocket endpoints
    for ws in endpoints['websocket_routes']:
        config['endpoints']['websockets'].append({
            "path": ws['path'],
            "handler": ws['handler']
        })
    
    return json.dumps(config, indent=2)

def save_endpoints_to_files(endpoints: Dict, output_dir: str = "./frontend-config"):
    """
    Save endpoint information to files for frontend use
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw endpoints data
    with open(f"{output_dir}/endpoints.json", 'w') as f:
        json.dump(endpoints, f, indent=2)
    
    # Save frontend configuration
    frontend_config = generate_frontend_config(endpoints)
    with open(f"{output_dir}/api-config.json", 'w') as f:
        f.write(frontend_config)
    
    # Generate TypeScript types
    ts_types = generate_typescript_types(endpoints)
    with open(f"{output_dir}/api-types.ts", 'w') as f:
        f.write(ts_types)
    
    print(f"\n💾 FILES SAVED:")
    print(f"   - {output_dir}/endpoints.json")
    print(f"   - {output_dir}/api-config.json") 
    print(f"   - {output_dir}/api-types.ts")

def generate_typescript_types(endpoints: Dict) -> str:
    """
    Generate TypeScript interface definitions
    """
    ts_content = """// Generated API Types for System Rebellion Frontend
// Auto-generated from backend endpoints

export interface ApiEndpoint {
  method: string;
  path: string;
  handler: string;
  file: string;
  line: number;
}

export interface WebSocketEndpoint {
  path: string;
  handler: string;
  file: string;
  line: number;
}

export interface ApiConfig {
  API_BASE_URL: string;
  WS_BASE_URL: string;
  endpoints: {
    auth: ApiEndpoint[];
    users: ApiEndpoint[];
    agents: ApiEndpoint[];
    metrics: ApiEndpoint[];
    websockets: WebSocketEndpoint[];
  };
}

// API Endpoint Constants
export const API_ENDPOINTS = {
"""
    
    # Add HTTP endpoints as constants
    for route in endpoints['http_routes']:
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', route['path']).upper().strip('_')
        ts_content += f'  {safe_name}: "{route["path"]}",\n'
    
    ts_content += "};\n\n// WebSocket Endpoint Constants\nexport const WS_ENDPOINTS = {\n"
    
    # Add WebSocket endpoints
    for ws in endpoints['websocket_routes']:
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', ws['path']).upper().strip('_')
        ts_content += f'  {safe_name}: "{ws["path"]}",\n'
    
    ts_content += "};\n"
    
    return ts_content

def main():
    """
    Main execution function
    """
    # Extract endpoints
    endpoints = extract_api_endpoints()
    
    # Print summary
    print_endpoints_summary(endpoints)
    
    # Save to files
    save_endpoints_to_files(endpoints)
    
    print(f"\n🚀 ENDPOINT EXTRACTION COMPLETE!")
    print("Use the generated files in your frontend components:")
    print("   import { API_ENDPOINTS, WS_ENDPOINTS } from './frontend-config/api-types';")

if __name__ == "__main__":
    main()