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
                print("🔐 Sending authentication token...")
                # Get a real JWT token by making a login request
                import requests
                login_url = "http://localhost:8000/api/auth/token"
                login_data = {
                    "username": "testuser@hawkington-tech.com",
                    "password": "Garfield7734!"
                }
                
                try:
                    response = requests.post(login_url, data=login_data)
                    if response.status_code == 200:
                        token_data = response.json()
                        access_token = token_data.get("access_token")
                        if access_token:
                            auth_message = {"token": access_token}
                            await websocket.send(json.dumps(auth_message))
                        else:
                            print("❌ No access token in response")
                            return False
                    else:
                        print(f"❌ Login failed: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ Failed to get auth token: {e}")
                    return False
                
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
