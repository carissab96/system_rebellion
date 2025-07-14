# 🔍 WEBSOCKET DATA FLOW DIAGNOSTIC SUITE
# For System Rebellion - The Great Debug Investigation
# Created by: Sir Hawkington's Detective Agency

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import websockets
import requests
from urllib.parse import urljoin

class WebSocketDiagnostics:
    def __init__(self, base_url: str = "http://localhost:8000", ws_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.test_token = None
        self.connection = None
        self.messages_received = []
        self.connection_events = []
        
    def log_event(self, event_type: str, details: Any = None):
        """Log diagnostic events with timestamps"""
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        self.connection_events.append(event)
        print(f"🔍 [{timestamp}] {event_type}: {details}")
    
    async def authenticate(self, username: str = "carissab", password: str = "Garfield7734"):
        """Step 1: Test authentication and get token"""
        self.log_event("AUTH_START", f"Attempting authentication with username: {username}")
        
        # Test multiple auth endpoints and formats
        auth_attempts = [
            {
                "url": "/auth/login",
                "method": "json",
                "data": {"username": username, "password": password}
            },
            {
                "url": "/auth/token", 
                "method": "json",
                "data": {"username": username, "password": password}
            },
            {
                "url": "/auth/login",
                "method": "form",
                "data": {"username": username, "password": password}
            },
            {
                "url": "/token",
                "method": "form",
                "data": {"username": username, "password": password}
            }
        ]
        
        for attempt in auth_attempts:
            try:
                auth_url = urljoin(self.base_url, attempt["url"])
                self.log_event("AUTH_ATTEMPT", f"Trying {attempt['url']} with {attempt['method']} format")
                
                if attempt["method"] == "json":
                    response = requests.post(auth_url, json=attempt["data"], timeout=10)
                else:  # form
                    response = requests.post(auth_url, data=attempt["data"], timeout=10)
                
                self.log_event("AUTH_RESPONSE", {
                    "url": attempt["url"],
                    "status": response.status_code,
                    "headers": dict(response.headers),
                    "response": response.text[:500]  # First 500 chars
                })
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.test_token = data.get("access_token") or data.get("token")
                        self.log_event("AUTH_SUCCESS", f"Token received from {attempt['url']}: {self.test_token[:20] if self.test_token else 'NO_TOKEN'}...")
                        return True
                    except:
                        self.log_event("AUTH_SUCCESS_NO_JSON", f"Success but couldn't parse JSON from {attempt['url']}")
                        
            except Exception as e:
                self.log_event("AUTH_ERROR", f"{attempt['url']}: {str(e)}")
        
        self.log_event("AUTH_ALL_FAILED", "All authentication attempts failed")
        return False
    
    async def test_websocket_connection(self):
        """Step 2: Test WebSocket connection establishment"""
        if not self.test_token:
            self.log_event("WS_SKIP", "No token available for WebSocket test")
            return False
            
        self.log_event("WS_CONNECT_START", f"Connecting to {self.ws_url}/ws")
        
        try:
            # Connect to WebSocket
            uri = f"{self.ws_url}/ws"
            self.connection = await websockets.connect(uri)
            self.log_event("WS_CONNECT_SUCCESS", "WebSocket connection established")
            
            # Send authentication
            auth_message = {
                "type": "auth",
                "token": self.test_token
            }
            await self.connection.send(json.dumps(auth_message))
            self.log_event("WS_AUTH_SENT", "Authentication message sent")
            
            # Wait for auth response
            try:
                response = await asyncio.wait_for(self.connection.recv(), timeout=5.0)
                auth_response = json.loads(response)
                self.log_event("WS_AUTH_RESPONSE", auth_response)
                
                if auth_response.get("type") == "auth_success":
                    self.log_event("WS_AUTH_SUCCESS", "WebSocket authentication successful")
                    return True
                else:
                    self.log_event("WS_AUTH_FAILED", auth_response)
                    return False
                    
            except asyncio.TimeoutError:
                self.log_event("WS_AUTH_TIMEOUT", "No auth response received within 5 seconds")
                return False
                
        except Exception as e:
            self.log_event("WS_CONNECT_ERROR", str(e))
            return False
    
    async def listen_for_messages(self, duration: int = 30):
        """Step 3: Listen for messages and analyze data flow"""
        if not self.connection:
            self.log_event("LISTEN_SKIP", "No WebSocket connection available")
            return
            
        self.log_event("LISTEN_START", f"Listening for messages for {duration} seconds")
        
        start_time = time.time()
        message_count = 0
        metric_messages = 0
        heartbeat_messages = 0
        other_messages = 0
        
        try:
            while time.time() - start_time < duration:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(self.connection.recv(), timeout=2.0)
                    message_count += 1
                    
                    try:
                        parsed = json.loads(message)
                        msg_type = parsed.get("type", "unknown")
                        
                        if msg_type == "heartbeat":
                            heartbeat_messages += 1
                            if heartbeat_messages <= 3:  # Log first few heartbeats
                                self.log_event("HEARTBEAT_RECEIVED", f"Heartbeat #{heartbeat_messages}")
                        elif msg_type == "metrics" or "cpu" in parsed or "memory" in parsed:
                            metric_messages += 1
                            self.log_event("METRICS_RECEIVED", f"Metric message #{metric_messages}")
                            self.log_event("METRICS_CONTENT", list(parsed.keys()))
                            self.messages_received.append(parsed)
                        else:
                            other_messages += 1
                            self.log_event("OTHER_MESSAGE", {"type": msg_type, "keys": list(parsed.keys())})
                            
                    except json.JSONDecodeError:
                        self.log_event("INVALID_JSON", f"Raw message: {message[:100]}...")
                        
                except asyncio.TimeoutError:
                    # No message received in 2 seconds, continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    self.log_event("CONNECTION_CLOSED", "WebSocket connection closed by server")
                    break
                    
        except Exception as e:
            self.log_event("LISTEN_ERROR", str(e))
        
        # Summary
        self.log_event("LISTEN_SUMMARY", {
            "duration": duration,
            "total_messages": message_count,
            "heartbeats": heartbeat_messages,
            "metrics": metric_messages,
            "other": other_messages
        })
        
        return {
            "total_messages": message_count,
            "heartbeats": heartbeat_messages,
            "metrics": metric_messages,
            "other": other_messages
        }
    
    async def test_backend_endpoints(self):
        """Step 4: Test backend endpoints directly"""
        self.log_event("BACKEND_TEST_START", "Testing backend endpoints")
        
        endpoints_to_test = [
            "/debug/websocket-stats",
            "/metrics",
            "/health",
            "/auth/validate"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                url = urljoin(self.base_url, endpoint)
                headers = {}
                if self.test_token and endpoint == "/auth/validate":
                    headers["Authorization"] = f"Bearer {self.test_token}"
                
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    self.log_event("ENDPOINT_SUCCESS", f"{endpoint}: {response.status_code}")
                    if endpoint == "/debug/websocket-stats":
                        stats = response.json()
                        self.log_event("WS_STATS", stats)
                else:
                    self.log_event("ENDPOINT_FAILED", f"{endpoint}: {response.status_code}")
                    
            except Exception as e:
                self.log_event("ENDPOINT_ERROR", f"{endpoint}: {str(e)}")
    
    async def run_full_diagnostic(self, username: str = "test_user", password: str = "test_password"):
        """Run complete diagnostic suite"""
        print("🔍 STARTING WEBSOCKET DATA FLOW DIAGNOSTIC")
        print("=" * 50)
        
        # Step 1: Authentication
        auth_success = await self.authenticate(username, password)
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with WebSocket tests")
            return self.generate_report()
        
        # Step 2: WebSocket Connection
        ws_success = await self.test_websocket_connection()
        if not ws_success:
            print("❌ WebSocket connection failed - cannot test data flow")
            await self.test_backend_endpoints()
            return self.generate_report()
        
        # Step 3: Listen for messages
        print("🎧 Listening for messages...")
        message_stats = await self.listen_for_messages(30)
        
        # Step 4: Test backend endpoints
        await self.test_backend_endpoints()
        
        # Step 5: Close connection
        if self.connection:
            await self.connection.close()
            self.log_event("WS_DISCONNECT", "WebSocket connection closed")
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate diagnostic report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_events": len(self.connection_events),
                "messages_received": len(self.messages_received),
                "auth_token_present": self.test_token is not None,
                "websocket_connected": self.connection is not None
            },
            "events": self.connection_events,
            "sample_messages": self.messages_received[:5]  # First 5 messages
        }
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNOSTIC REPORT SUMMARY")
        print("=" * 50)
        
        for key, value in report["summary"].items():
            print(f"{key}: {value}")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        metric_messages = len([e for e in self.connection_events if e["type"] == "METRICS_RECEIVED"])
        heartbeat_messages = len([e for e in self.connection_events if e["type"] == "HEARTBEAT_RECEIVED"])
        
        if metric_messages == 0:
            print("❌ NO METRIC MESSAGES RECEIVED - This is the problem!")
        else:
            print(f"✅ {metric_messages} metric messages received")
            
        if heartbeat_messages > 0:
            print(f"💓 {heartbeat_messages} heartbeat messages received (connection alive)")
        
        # Check for auth issues
        auth_events = [e for e in self.connection_events if "AUTH" in e["type"]]
        if any("FAILED" in e["type"] or "ERROR" in e["type"] for e in auth_events):
            print("❌ AUTHENTICATION ISSUES DETECTED")
        
        # Check for connection issues  
        connection_events = [e for e in self.connection_events if "WS_" in e["type"]]
        if any("ERROR" in e["type"] or "FAILED" in e["type"] for e in connection_events):
            print("❌ WEBSOCKET CONNECTION ISSUES DETECTED")
        
        return report

# 🎯 SIMPLE DIAGNOSTIC RUNNER
async def quick_diagnostic():
    """Quick diagnostic for immediate testing"""
    print("🚀 QUICK WEBSOCKET DIAGNOSTIC")
    print("Testing with default credentials...")
    
    diagnostics = WebSocketDiagnostics()
    report = await diagnostics.run_full_diagnostic()
    
    # Save report to file
    with open("websocket_diagnostic_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Full report saved to: websocket_diagnostic_report.json")
    return report

# 🎯 CUSTOM DIAGNOSTIC RUNNER  
async def custom_diagnostic(base_url: str, ws_url: str, username: str, password: str):
    """Custom diagnostic with your specific settings"""
    print(f"🔧 CUSTOM WEBSOCKET DIAGNOSTIC")
    print(f"Base URL: {base_url}")
    print(f"WebSocket URL: {ws_url}")
    print(f"Username: {username}")
    
    diagnostics = WebSocketDiagnostics(base_url, ws_url)
    report = await diagnostics.run_full_diagnostic(username, password)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"websocket_diagnostic_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Full report saved to: {filename}")
    return report

if __name__ == "__main__":
    print("🎭 Sir Hawkington's WebSocket Diagnostic Suite")
    print("Choose your diagnostic adventure:")
    print("1. Quick diagnostic (default settings)")
    print("2. Custom diagnostic (your settings)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        base_url = input("Backend URL (e.g. http://localhost:8000): ").strip()
        ws_url = input("WebSocket URL (e.g. ws://localhost:8000): ").strip()
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        asyncio.run(custom_diagnostic(base_url, ws_url, username, password))
    else:
        asyncio.run(quick_diagnostic())