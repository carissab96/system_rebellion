#!/usr/bin/env python3
"""
WebSocket Metrics Test Script

This script directly tests the WebSocket metrics route to see what data
is being sent to the frontend. It bypasses the frontend entirely and
connects directly to the WebSocket endpoint.
"""

import sys
import os
import asyncio
import json
import websockets
import time
from datetime import datetime

# Add the parent directory to the path so we can import the necessary modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the necessary modules for authentication
from app.core.security import create_access_token
from app.models.user import User

async def test_websocket_metrics():
    """Test the WebSocket metrics route directly"""
    print("\n" + "="*60)
    print(" WEBSOCKET METRICS TEST - DIRECT CONNECTION")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create a mock user for authentication
    mock_user = User(
        id=1,
        email="test@example.com",
        username="test_user",
        is_active=True,
        is_superuser=True
    )
    
    # Create an access token for the mock user
    token = create_access_token({"sub": "test@example.com"})
    
    # WebSocket URL with token
    ws_url = f"ws://localhost:8000/api/ws/metrics?token={token}"
    
    print(f"\nConnecting to WebSocket at: {ws_url}")
    
    try:
        # Connect to the WebSocket
        async with websockets.connect(ws_url) as websocket:
            print("\nConnection established!")
            
            # Wait for messages for 10 seconds
            print("\nListening for messages for 10 seconds...")
            
            start_time = time.time()
            message_count = 0
            
            while time.time() - start_time < 10:
                try:
                    # Set a timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message_count += 1
                    
                    # Parse the message
                    data = json.loads(message)
                    
                    # Print message info
                    print(f"\nMessage {message_count} received:")
                    print(f"Message type: {data.get('type', 'unknown')}")
                    
                    # Check if it's a metrics message
                    if data.get('type') == 'metrics':
                        metrics = data.get('data', {})
                        print(f"Metrics timestamp: {metrics.get('timestamp', 'unknown')}")
                        
                        # Check for CPU metrics
                        cpu = metrics.get('cpu', {})
                        print(f"CPU usage: {cpu.get('percent', 'null')}%")
                        
                        # Check for memory metrics
                        memory = metrics.get('memory', {})
                        print(f"Memory usage: {memory.get('percent', 'null')}%")
                        
                        # Check for disk metrics
                        disk = metrics.get('disk', {})
                        print(f"Disk usage: {disk.get('percent', 'null')}%")
                        
                        # Check for network metrics
                        network = metrics.get('network', {})
                        print(f"Network interfaces: {len(network.get('interfaces', []))}")
                        
                        # Check for null values
                        null_values = []
                        if cpu.get('percent') is None:
                            null_values.append('cpu.percent')
                        if memory.get('percent') is None:
                            null_values.append('memory.percent')
                        if disk.get('percent') is None:
                            null_values.append('disk.percent')
                        if not network.get('interfaces'):
                            null_values.append('network.interfaces')
                            
                        if null_values:
                            print(f"NULL VALUES DETECTED in: {', '.join(null_values)}")
                        else:
                            print("All key metrics have values!")
                    
                    # Print the raw message (truncated)
                    print(f"Raw message (truncated): {message[:500]}...")
                    
                except asyncio.TimeoutError:
                    # No message received within timeout, continue
                    await asyncio.sleep(0.1)
                    continue
            
            print(f"\nTest completed. Received {message_count} messages in 10 seconds.")
    
    except Exception as e:
        print(f"\nERROR connecting to WebSocket: {str(e)}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_websocket_metrics())
