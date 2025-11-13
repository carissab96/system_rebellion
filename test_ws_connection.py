#!/usr/bin/env python3
"""Quick test to verify WebSocket connection to backend"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/ws/system-metrics"
    print(f"🔌 Attempting to connect to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for a message
            print("⏳ Waiting for messages...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"📨 Received: {data.get('type', 'unknown')}")
            print(f"📊 Data: {json.dumps(data, indent=2)[:200]}...")
            
    except asyncio.TimeoutError:
        print("⏱️ Timeout waiting for message (but connection worked!)")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e}")
        print("   This might mean authentication is required")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
