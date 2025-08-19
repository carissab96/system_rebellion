# backend/test_real_websocket_endpoint.py
"""
REAL WEBSOCKET ENDPOINT TEST
Tests the ACTUAL WebSocket handler with LIVE psutil data flowing through
Sir Hawkington's triage engine to the frontend.

NO SIMULATIONS. NO FAKE DATA. REAL TESTING OF REAL ENDPOINTS.
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

class RealWebSocketTester:
    """Tests the actual live WebSocket endpoint"""
    
    def __init__(self, server_url="ws://localhost:8000"):
        self.server_url = server_url
        self.messages_received = 0
        self.triage_decisions_seen = 0
        self.agent_processing_seen = 0
        self.real_metrics_seen = 0
        self.errors = []
        
    async def test_real_websocket_flow(self, duration=30):
        """
        Test the REAL WebSocket endpoint for the specified duration
        This hits the actual /ws/system-metrics endpoint
        """
        print(f"🔌 TESTING REAL WEBSOCKET ENDPOINT: {self.server_url}/ws/system-metrics")
        print(f"⏰ Duration: {duration} seconds")
        print("="*80)
        
        websocket_url = f"{self.server_url}/ws/system-metrics"
        
        try:
            async with websockets.connect(websocket_url) as websocket:
                print("✅ CONNECTED to real WebSocket endpoint")
                
                # Send authentication if needed
                # (Check your websocket_routes.py for auth requirements)
                
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Receive REAL message from REAL endpoint
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        await self._analyze_real_message(message)
                        
                    except asyncio.TimeoutError:
                        print("⏰ No message in 5 seconds - endpoint might be down")
                        
                    except websockets.exceptions.ConnectionClosed:
                        print("🔌 WebSocket connection closed by server")
                        break
                        
                    except Exception as e:
                        error_msg = f"Error receiving message: {str(e)}"
                        self.errors.append(error_msg)
                        print(f"❌ {error_msg}")
                
                await self._print_real_test_results()
                
        except websockets.exceptions.InvalidURI:
            print(f"❌ INVALID WEBSOCKET URI: {websocket_url}")
            print("   Make sure server is running: uvicorn main:app --reload")
            
        except websockets.exceptions.ConnectionFailure as e:
            print(f"❌ CANNOT CONNECT TO WEBSOCKET: {e}")
            print(f"   Server URL: {websocket_url}")
            print("   1. Is the server running?")
            print("   2. Is the WebSocket route correct?")
            print("   3. Check websocket_routes.py")
            
        except Exception as e:
            print(f"💥 WEBSOCKET TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    async def _analyze_real_message(self, raw_message):
        """Analyze a real message from the real WebSocket endpoint"""
        self.messages_received += 1
        
        try:
            data = json.loads(raw_message)
            
            # Check for real psutil metrics
            has_cpu = 'cpu_usage' in data
            has_memory = 'memory_usage' in data  
            has_disk = 'disk_usage' in data
            
            if has_cpu and has_memory and has_disk:
                self.real_metrics_seen += 1
                cpu = data['cpu_usage']
                memory = data['memory_usage']
                disk = data['disk_usage']
                
                print(f"\n📊 Message #{self.messages_received}: REAL PSUTIL DATA")
                print(f"   CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")
                
                # Check if Sir Hawkington's triage processed this
                if 'triage_decision' in data:
                    self.triage_decisions_seen += 1
                    triage = data['triage_decision']
                    
                    print(f"   🧐 TRIAGE: {triage['severity']} → {triage['routing']}")
                    print(f"   🎯 TARGET: {triage['target_agents']}")
                    print(f"   🧐 MONOCLE: {'YEETED' if triage.get('monocle_yeeted') else 'Polished'}")
                    print(f"   ✅ SIR HAWKINGTON'S TRIAGE ENGINE IS WORKING!")
                else:
                    print(f"   ❌ NO TRIAGE DECISION - TRIAGE ENGINE NOT WORKING!")
                
                # Check agent processing
                if 'agent_processing' in data:
                    self.agent_processing_seen += 1
                    agents = data['agent_processing']
                    successful = len(agents.get('successful_agents', []))
                    failed = len(agents.get('failed_agents', []))
                    
                    print(f"   🤖 AGENTS: {successful} successful, {failed} failed")
                    print(f"   ✅ AGENT PROCESSING IS WORKING!")
                else:
                    print(f"   ❌ NO AGENT PROCESSING DATA!")
                    
            else:
                print(f"\n📨 Message #{self.messages_received}: NOT METRICS DATA")
                print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
        
        except json.JSONDecodeError:
            print(f"\n❌ Message #{self.messages_received}: INVALID JSON")
            print(f"   Raw: {raw_message[:100]}...")
            self.errors.append("Invalid JSON received")
        
        except Exception as e:
            print(f"\n❌ Message #{self.messages_received}: ANALYSIS ERROR")
            print(f"   Error: {str(e)}")
            self.errors.append(f"Message analysis error: {str(e)}")
    
    async def _print_real_test_results(self):
        """Print results of real WebSocket testing"""
        print(f"\n" + "="*80)
        print(f" 🎯 REAL WEBSOCKET ENDPOINT TEST RESULTS")
        print(f"="*80)
        
        print(f"📊 MESSAGES:")
        print(f"   Total Received: {self.messages_received}")
        print(f"   Real Metrics: {self.real_metrics_seen}")
        print(f"   Triage Decisions: {self.triage_decisions_seen}")
        print(f"   Agent Processing: {self.agent_processing_seen}")
        
        print(f"\n🧐 SIR HAWKINGTON'S TRIAGE:")
        if self.triage_decisions_seen > 0:
            triage_rate = (self.triage_decisions_seen / self.real_metrics_seen) * 100
            print(f"   ✅ WORKING: {triage_rate:.1f}% of metrics processed through triage")
        else:
            print(f"   ❌ BROKEN: No triage decisions seen!")
        
        print(f"\n🤖 AGENT PROCESSING:")
        if self.agent_processing_seen > 0:
            agent_rate = (self.agent_processing_seen / self.real_metrics_seen) * 100
            print(f"   ✅ WORKING: {agent_rate:.1f}% of metrics processed through agents")
        else:
            print(f"   ❌ BROKEN: No agent processing seen!")
        
        print(f"\n❌ ERRORS:")
        if self.errors:
            for error in self.errors:
                print(f"   • {error}")
        else:
            print(f"   ✅ No errors!")
        
        # FINAL VERDICT
        if (self.real_metrics_seen > 0 and 
            self.triage_decisions_seen > 0 and 
            self.agent_processing_seen > 0):
            print(f"\n🎉 WEBSOCKET ENDPOINT IS WORKING!")
            print(f"✅ Real psutil data → Triage → Agents → WebSocket → Frontend CONFIRMED!")
        else:
            print(f"\n🚨 WEBSOCKET ENDPOINT HAS ISSUES!")
            if self.real_metrics_seen == 0:
                print(f"   • No real metrics data flowing")
            if self.triage_decisions_seen == 0:
                print(f"   • Triage engine not processing data")
            if self.agent_processing_seen == 0:
                print(f"   • Agent processing not working")

async def test_websocket_with_different_servers():
    """Test WebSocket on different possible server URLs"""
    possible_urls = [
        "ws://localhost:8000",
        "ws://127.0.0.1:8000", 
        "ws://0.0.0.0:8000"
    ]
    
    for url in possible_urls:
        print(f"\n🔍 TRYING SERVER: {url}")
        tester = RealWebSocketTester(url)
        
        try:
            await tester.test_real_websocket_flow(duration=15)
            
            if tester.messages_received > 0:
                print(f"✅ FOUND WORKING SERVER: {url}")
                break
            else:
                print(f"❌ No data from: {url}")
                
        except Exception as e:
            print(f"❌ Failed to connect to: {url}")
            print(f"   Error: {str(e)}")

async def main():
    """Main test function"""
    print("🧐⚡ REAL WEBSOCKET ENDPOINT TESTING")
    print("Tests the ACTUAL WebSocket with LIVE psutil data!")
    print("No simulations, no fake data - just REAL TESTING!")
    
    # Test the standard server first
    tester = RealWebSocketTester()
    await tester.test_real_websocket_flow(duration=30)
    
    # If that didn't work, try different URLs
    if tester.messages_received == 0:
        print(f"\n🔍 Standard server didn't respond, trying alternatives...")
        await test_websocket_with_different_servers()

if __name__ == "__main__":
    asyncio.run(main())