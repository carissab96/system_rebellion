import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._connection_lock = asyncio.Lock()
        self._max_retries = 3
        self._retry_delay = 1.0
    
    async def connect(self, websocket: WebSocket):
        """Add a websocket connection with proper locking."""
        async with self._connection_lock:
            if websocket not in self.active_connections:
                self.active_connections.append(websocket)
                print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a websocket connection with proper locking."""
        async with self._connection_lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                print(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        async with self._connection_lock:
            # Make a copy of the connections to avoid modification during iteration
            connections = self.active_connections.copy()
        
        # Send messages outside the lock to avoid deadlocks
        disconnected_connections = []
        for connection in connections:
            try:
                # Use a timeout to prevent hanging on broken connections
                try:
                    await asyncio.wait_for(connection.send_json(message), timeout=2.0)
                except asyncio.TimeoutError:
                    print(f"Timeout sending message to WebSocket")
                    disconnected_connections.append(connection)
                    continue
            except WebSocketDisconnect:
                print(f"WebSocket disconnected during broadcast")
                disconnected_connections.append(connection)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                # Check specifically for EPIPE errors which indicate broken pipe
                if "EPIPE" in str(e) or "ConnectionClosed" in str(e) or "WebSocketDisconnect" in str(e):
                    print(f"Connection closed or broken pipe, removing connection")
                    disconnected_connections.append(connection)
        
        # Remove all disconnected connections
        if disconnected_connections:
            async with self._connection_lock:
                for connection in disconnected_connections:
                    if connection in self.active_connections:
                        self.active_connections.remove(connection)
                print(f"Removed {len(disconnected_connections)} closed connections. Remaining: {len(self.active_connections)}")

    async def handle_connection(self, websocket: WebSocket):
        """Handle connection with retry logic"""
        retry_count = 0
        while retry_count < self._max_retries:
            try:
                await self.connect(websocket)
                return True
            except Exception as e:
                print(f"Connection attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                await asyncio.sleep(self._retry_delay)
        
        print("Maximum connection attempts reached")
        return False

    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
        """Send a message to a specific client with error handling."""
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=2.0)
            return True
        except (WebSocketDisconnect, asyncio.TimeoutError) as e:
            print(f"Failed to send message: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending message: {e}")
            return False

# The Meth Snail's Global WebSocket Manager
websocket_manager = WebSocketManager()