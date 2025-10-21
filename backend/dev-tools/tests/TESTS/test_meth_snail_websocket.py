"""
Test script for Meth Snail WebSocket integration
"""
import asyncio
import json
import websockets
import pytest
from datetime import datetime, timedelta

# Test configuration
WS_URI = "ws://localhost:8000/ws/system-metrics"
TEST_TIMEOUT = 10  # seconds

async def test_meth_snail_websocket():
    """Test Meth Snail WebSocket connection and message handling"""
    async with websockets.connect(WS_URI) as websocket:
        print("✅ Connected to WebSocket server")
        
        # Wait for connection message
        response = await asyncio.wait_for(websocket.recv(), timeout=TEST_TIMEOUT)
        response_data = json.loads(response)
        print(f"📨 Received initial message: {response_data}")
        
        # Send authentication (simplified for testing)
        auth_msg = {
            "type": "auth",
            "token": "test-token",
            "client_type": "test_client"
        }
        await websocket.send(json.dumps(auth_msg))
        print("🔑 Sent authentication")
        
        # Wait for auth confirmation
        response = await asyncio.wait_for(websocket.recv(), timeout=TEST_TIMEOUT)
        response_data = json.loads(response)
        print(f"🔑 Auth response: {response_data}")
        
        # Listen for updates
        print("👂 Listening for updates...")
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time) < timedelta(seconds=10):
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📊 Update received: {json.dumps(response_data, indent=2)}")
                
                # Verify message structure
                assert "type" in response_data
                assert "data" in response_data
                assert "timestamp" in response_data
                
                if response_data["type"] == "jitter_update":
                    assert "current_jitter_level" in response_data["data"]
                    assert "shell_spin_probability" in response_data["data"]
                elif response_data["type"] == "metrics_update":
                    assert "shell_spins_executed" in response_data["data"]
                
            except asyncio.TimeoutError:
                print("⏱️  No message received in the last 5 seconds")
                break

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(test_meth_snail_websocket())
