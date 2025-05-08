import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()  # Add a lock for thread safety
        self._max_retries = 3  # Maximum number of reconnection attempts
        self._retry_delay = 1  # Delay between retries in seconds

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            async with self._lock:
                if websocket not in self.active_connections:
                    self.active_connections.append(websocket)
            print("WebSocket connected successfully")
        except Exception as e:
            print(f"Error connecting WebSocket: {e}")
            raise

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print("WebSocket disconnected")

    async def broadcast(self, message: dict):
        async with self._lock:
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
        for connection in disconnected_connections:
            await self.disconnect(connection)

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

# The Meth Snail's Global WebSocket Manager
websocket_manager = WebSocketManager()