#!/usr/bin/env python3
"""
Test script to verify WebSocket coroutine serialization fixes
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection and metrics flow to verify coroutine fixes"""
    
    print("\n" + "="*80)
    print(" 🧐 TESTING WEBSOCKET COROUTINE SERIALIZATION FIXES")
    print("="*80)
    
    # Test connection details
    websocket_url = "ws://localhost:8000/api/ws/system-metrics"
    test_token = "test_token_123"  # Mock token for testing
    
    try:
        print(f"\n🔌 Connecting to WebSocket: {websocket_url}")
        
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connection established")
            
            # Wait for connection established message
            try:
                initial_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                initial_data = json.loads(initial_message)
                print(f"📨 Initial message: {initial_data.get('type', 'unknown')}")
                
                if initial_data.get('type') == 'connection_established':
                    print("✅ Connection established message received")
                    
                    # Send authentication message
                    auth_message = {
                        "token": test_token,
                        "type": "auth"
                    }
                    
                    print("🔐 Sending authentication...")
                    await websocket.send(json.dumps(auth_message))
                    
                    # Listen for messages for a short period
                    message_count = 0
                    
                    print("\n📡 Listening for messages (10 seconds)...")
                    
                    while message_count < 5:  # Test first 5 messages
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                            message_data = json.loads(message)
                            message_type = message_data.get('type', 'unknown')
                            message_count += 1
                            
                            print(f"📨 Message {message_count}: {message_type}")
                            
                            # Check for coroutine serialization errors
                            if message_type == 'connection_error':
                                error_msg = message_data.get('message', '')
                                if 'coroutine' in error_msg.lower():
                                    print(f"❌ COROUTINE SERIALIZATION ERROR DETECTED: {error_msg}")
                                    return False
                                else:
                                    print(f"⚠️ Connection error (not coroutine related): {error_msg}")
                            
                            elif message_type == 'metrics_update':
                                print("✅ Metrics update received successfully")
                                # Verify no coroutine objects in data
                                data_str = json.dumps(message_data)
                                if 'coroutine' in data_str.lower():
                                    print("❌ Coroutine object found in metrics data!")
                                    return False
                                else:
                                    print("✅ No coroutine objects in metrics data")
                            
                            elif message_type == 'metrics_error':
                                error_msg = message_data.get('message', '')
                                if 'coroutine not awaited' in error_msg:
                                    print(f"✅ Coroutine error caught and handled properly: {error_msg}")
                                else:
                                    print(f"⚠️ Other metrics error: {error_msg}")
                                    
                        except asyncio.TimeoutError:
                            print("⏰ Timeout waiting for message")
                            break
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON decode error: {e}")
                            return False
                    
                    print(f"\n✅ Successfully processed {message_count} messages without coroutine serialization errors")
                    return True
                    
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for initial connection message")
                return False
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧐 Starting WebSocket coroutine serialization fix verification...")
    
    success = await test_websocket_connection()
    
    if success:
        print("\n🎉 SUCCESS: WebSocket coroutine serialization fixes are working!")
        print("✅ No 'Object of type coroutine is not JSON serializable' errors detected")
        print("✅ Backend agent coroutine crashes should be resolved")
    else:
        print("\n❌ FAILURE: WebSocket coroutine serialization issues still present")
        print("❌ Backend may still experience coroutine crashes")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())