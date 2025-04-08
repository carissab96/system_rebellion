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
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                # Remove the problematic connection
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