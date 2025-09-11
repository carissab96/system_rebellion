#!/usr/bin/env python3
"""
Simple WebSocket test client to verify the backend WebSocket endpoint works
"""
import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = "ws://localhost:8000/api/ws/system-metrics"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for connection_established message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Received: {data}")
            
            if data.get('type') == 'connection_established':
                print("🔐 Sending fake authentication token...")
                # Send fake token to test auth flow
                auth_message = {"token": "fake_token_for_testing"}
                await websocket.send(json.dumps(auth_message))
                
                # Wait for response
                response = await websocket.recv()
                response_data = json.loads(response)
                print(f"🔐 Auth response: {response_data}")
                
                if response_data.get('type') == 'error':
                    print("❌ Expected auth error with fake token - this is correct!")
                    return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    sys.exit(0 if result else 1)
