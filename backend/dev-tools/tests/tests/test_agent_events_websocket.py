#!/usr/bin/env python3
"""
Test client for agent events WebSocket
Run: python test_agent_events_websocket.py
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Test the agent events WebSocket endpoint"""
    
    # You'll need to replace this with a real JWT token
    # Get one by logging in through the API
    token = "your_jwt_token_here"
    
    uri = f"ws://localhost:8000/api/ws/agent-events?token={token}"
    
    print("🔌 Connecting to agent events WebSocket...")
    print(f"   URI: {uri}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            print()
            
            # Wait for connection message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Received: {data}")
            print()
            
            # Request recent events
            print("📤 Requesting recent events...")
            await websocket.send(json.dumps({
                "type": "get_recent",
                "limit": 10
            }))
            
            # Listen for events
            print("👂 Listening for agent events...")
            print("   (Waiting for agents to generate events...)")
            print()
            
            event_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "agent_event":
                        event_count += 1
                        event = data["event"]
                        timestamp = datetime.fromisoformat(event["timestamp"]).strftime("%H:%M:%S")
                        
                        # Format event based on type
                        agent = event["agent_name"]
                        event_type = event["event_type"]
                        severity = event["severity"]
                        
                        print(f"🎭 [{timestamp}] {agent.upper()}")
                        print(f"   Event: {event_type}")
                        print(f"   Severity: {severity}")
                        print(f"   Data: {json.dumps(event['event_data'], indent=2)}")
                        print()
                        
                    elif data.get("type") == "recent_events":
                        events = data.get("events", [])
                        print(f"📜 Received {len(events)} recent events")
                        for event in events:
                            print(f"   - {event['agent_name']}: {event['event_type']}")
                        print()
                        
                    elif data.get("type") == "pong":
                        print(f"💓 Pong received")
                        
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    print("⏰ Timeout - sending ping...")
                    await websocket.send(json.dumps({"type": "ping"}))
                    
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("💡 Tips:")
        print("   1. Make sure the backend server is running")
        print("   2. Get a valid JWT token by logging in:")
        print("      curl -X POST http://localhost:8000/api/auth/login \\")
        print("           -H 'Content-Type: application/json' \\")
        print("           -d '{\"username\":\"your_user\",\"password\":\"your_pass\"}'")
        print("   3. Replace 'your_jwt_token_here' in this script with the token")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Agent Events WebSocket Test Client")
    print("=" * 60)
    print()
    
    asyncio.run(test_websocket())
