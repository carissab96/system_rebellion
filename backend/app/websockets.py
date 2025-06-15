import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import logging
import time
from typing import List, Dict, Any, Optional
from enum import Enum

class ConnectionState(Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    DEAD = "dead"

class WebSocketManager:
    def __init__(self, 
                 heartbeat_interval: float = 15.0,
                 message_timeout: float = 2.0,
                 heartbeat_timeout: float = 1.0,
                 max_error_count: int = 5,
                 connection_timeout: float = 30.0,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        
        self.active_connections: List[WebSocket] = []
        self.connection_health: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Configuration
        self._heartbeat_interval = heartbeat_interval
        self._message_timeout = message_timeout
        self._heartbeat_timeout = heartbeat_timeout
        self._max_error_count = max_error_count
        self._connection_timeout = connection_timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        
        # Synchronization
        self._connection_lock = asyncio.Lock()
        self._heartbeat_started = asyncio.Event()
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._shutdown = False
        
        print("🦅 Sir Hawkington's Distinguished WebSocket Manager initialized")
    
    async def connect(self, websocket: WebSocket) -> bool:
        """Add a websocket connection with proper atomic operations."""
        try:
            async with self._connection_lock:
                # Atomic check and add to prevent duplicates
                if websocket in self.active_connections:
                    print(f"⚠️ WebSocket already connected: {id(websocket) % 10000}")
                    return True
                
                # Add to both structures atomically
                self.active_connections.append(websocket)
                self.connection_health[websocket] = {
                    "connected_at": time.time(),
                    "last_successful_msg": time.time(),
                    "last_heartbeat": time.time(),
                    "error_count": 0,
                    "state": ConnectionState.ACTIVE,
                    "client_id": f"client_{id(websocket) % 10000}"
                }
                
                client_id = self.connection_health[websocket]["client_id"]
                print(f"🔌 WebSocket connected ({client_id}). Total connections: {len(self.active_connections)}")
                
            # Start heartbeat task if this is the first connection
            await self._ensure_heartbeat_running()
            return True
            
        except Exception as e:
            print(f"❌ Error connecting WebSocket: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a websocket connection with proper cleanup."""
        async with self._connection_lock:
            client_id = "unknown"
            
            # Get client ID before cleanup
            if websocket in self.connection_health:
                client_id = self.connection_health[websocket].get("client_id", "unknown")
                del self.connection_health[websocket]
            
            # Remove from active connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                print(f"👋 WebSocket disconnected ({client_id}). Remaining: {len(self.active_connections)}")
            
            # Stop heartbeat if no connections remain
            if not self.active_connections and self._heartbeat_task:
                await self._stop_heartbeat()
    
    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast a message to all active connections. Returns number of successful sends."""
        # Get snapshot of connections
        async with self._connection_lock:
            connections_snapshot = [(ws, health.copy()) for ws, health in self.connection_health.items() 
                                  if health["state"] == ConnectionState.ACTIVE]
        
        if not connections_snapshot:
            return 0
        
        successful_sends = 0
        failed_connections = []
        
        # Send messages without holding the lock
        for websocket, health in connections_snapshot:
            success = await self._send_to_client_safe(websocket, message)
            if success:
                successful_sends += 1
                # Update health info
                async with self._connection_lock:
                    if websocket in self.connection_health:
                        self.connection_health[websocket]["last_successful_msg"] = time.time()
                        self.connection_health[websocket]["error_count"] = 0
                        if self.connection_health[websocket]["state"] == ConnectionState.DEGRADED:
                            self.connection_health[websocket]["state"] = ConnectionState.ACTIVE
            else:
                failed_connections.append(websocket)
        
        # Handle failed connections
        if failed_connections:
            await self._handle_failed_connections(failed_connections)
        
        return successful_sends
    
    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
        """Send a message to a specific client."""
        # Check if connection is still valid
        async with self._connection_lock:
            if websocket not in self.connection_health:
                return False
            
            health = self.connection_health[websocket]
            if health["state"] == ConnectionState.DEAD:
                return False
        
        success = await self._send_to_client_safe(websocket, message)
        
        # Update health based on result
        async with self._connection_lock:
            if websocket in self.connection_health:
                if success:
                    self.connection_health[websocket]["last_successful_msg"] = time.time()
                    self.connection_health[websocket]["error_count"] = 0
                    if self.connection_health[websocket]["state"] == ConnectionState.DEGRADED:
                        self.connection_health[websocket]["state"] = ConnectionState.ACTIVE
                else:
                    self.connection_health[websocket]["error_count"] += 1
                    if self.connection_health[websocket]["error_count"] >= self._max_error_count:
                        self.connection_health[websocket]["state"] = ConnectionState.DEAD
                    else:
                        self.connection_health[websocket]["state"] = ConnectionState.DEGRADED
        
        return success
    
    async def _send_to_client_safe(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
        """Safely send a message to a client with proper error handling."""
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=self._message_timeout)
            return True
            
        except (WebSocketDisconnect, ConnectionResetError, ConnectionAbortedError):
            # Connection cleanly closed or reset
            return False
            
        except asyncio.TimeoutError:
            # Connection is slow or unresponsive
            return False
            
        except Exception as e:
            # Check for specific connection errors
            error_str = str(e).lower()
            if any(err in error_str for err in ['epipe', 'connectionclosed', 'websocketdisconnect', 'broken pipe']):
                return False
            
            # Log unexpected errors
            client_id = "unknown"
            if websocket in self.connection_health:
                client_id = self.connection_health[websocket].get("client_id", "unknown")
            print(f"❌ Unexpected error sending to {client_id}: {e}")
            return False
    
    async def _ensure_heartbeat_running(self):
        """Ensure the heartbeat task is running."""
        if self._heartbeat_started.is_set():
            return
        
        self._heartbeat_started.set()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        print("💓 Heartbeat task started")
    
    async def _stop_heartbeat(self):
        """Stop the heartbeat task."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            print("💓 Heartbeat task stopped")
        
        self._heartbeat_started.clear()
        self._heartbeat_task = None
    
    async def _heartbeat_loop(self):
        """Main heartbeat loop."""
        try:
            while not self._shutdown:
                await self._send_heartbeats()
                await self._cleanup_dead_connections()
                await asyncio.sleep(self._heartbeat_interval)
                
        except asyncio.CancelledError:
            print("💓 Heartbeat task cancelled")
            raise
        except Exception as e:
            print(f"❌ Critical error in heartbeat task: {e}")
            # Try to restart the heartbeat task
            self._heartbeat_started.clear()
            if not self._shutdown:
                await asyncio.sleep(5)  # Wait before restart
                await self._ensure_heartbeat_running()
    
    async def _send_heartbeats(self):
        """Send heartbeat messages to all active connections."""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": time.time()
        }
        
        # Get snapshot of active connections
        async with self._connection_lock:
            active_connections = [ws for ws, health in self.connection_health.items() 
                                if health["state"] in [ConnectionState.ACTIVE, ConnectionState.DEGRADED]]
        
        if not active_connections:
            return
        
        # Send heartbeats without holding the lock
        for websocket in active_connections:
            try:
                await asyncio.wait_for(websocket.send_json(heartbeat_message), 
                                     timeout=self._heartbeat_timeout)
                
                # Update heartbeat timestamp
                async with self._connection_lock:
                    if websocket in self.connection_health:
                        self.connection_health[websocket]["last_heartbeat"] = time.time()
                        
            except Exception:
                # Increment error count for failed heartbeats
                async with self._connection_lock:
                    if websocket in self.connection_health:
                        self.connection_health[websocket]["error_count"] += 1
    
    async def _cleanup_dead_connections(self):
        """Remove connections that are dead or unresponsive."""
        now = time.time()
        to_remove = []
        
        async with self._connection_lock:
            for websocket, health in self.connection_health.items():
                client_id = health.get("client_id", "unknown")
                
                # Check if connection is dead based on various criteria
                is_dead = (
                    health["state"] == ConnectionState.DEAD or
                    health["error_count"] >= self._max_error_count or
                    (now - health.get("last_successful_msg", 0)) > self._connection_timeout
                )
                
                if is_dead:
                    print(f"⚰️ Removing dead connection ({client_id})")
                    to_remove.append(websocket)
            
            # Remove dead connections
            for websocket in to_remove:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
                if websocket in self.connection_health:
                    del self.connection_health[websocket]
            
            if to_remove:
                print(f"🧹 Cleaned up {len(to_remove)} dead connections. Active: {len(self.active_connections)}")
    
    async def _handle_failed_connections(self, failed_connections: List[WebSocket]):
        """Handle connections that failed to receive messages."""
        async with self._connection_lock:
            for websocket in failed_connections:
                if websocket in self.connection_health:
                    health = self.connection_health[websocket]
                    health["error_count"] += 1
                    
                    if health["error_count"] >= self._max_error_count:
                        health["state"] = ConnectionState.DEAD
                    else:
                        health["state"] = ConnectionState.DEGRADED
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        async with self._connection_lock:
            stats = {
                "total_connections": len(self.active_connections),
                "active": 0,
                "degraded": 0,
                "dead": 0,
                "connections": []
            }
            
            for websocket, health in self.connection_health.items():
                state = health["state"]
                stats[state.value] += 1
                
                stats["connections"].append({
                    "client_id": health["client_id"],
                    "state": state.value,
                    "connected_at": health["connected_at"],
                    "error_count": health["error_count"],
                    "last_successful_msg": health.get("last_successful_msg", 0)
                })
            
            return stats
    
    async def shutdown(self):
        """Gracefully shutdown the manager."""
        print("🛑 Shutting down WebSocket Manager")
        self._shutdown = True
        
        # Stop heartbeat task
        await self._stop_heartbeat()
        
        # Close all connections
        async with self._connection_lock:
            for websocket in self.active_connections.copy():
                try:
                    await websocket.close()
                except Exception:
                    pass  # Ignore errors during shutdown
            
            self.active_connections.clear()
            self.connection_health.clear()
        
        print("✅ WebSocket Manager shutdown complete")


# Sir Hawkington's Distinguished WebSocket Manager
websocket_manager = WebSocketManager()







# import asyncio
# from fastapi import WebSocket, WebSocketDisconnect
# import asyncio
# import logging
# import time
# from typing import List, Dict, Any, Set, Optional

# class WebSocketManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []
#         self.connection_health: Dict[WebSocket, Dict[str, Any]] = {}
#         # Lock to protect access to active_connections
#         self._connection_lock = asyncio.Lock()
#         # Set up a heartbeat task
#         self._heartbeat_task = None
#         # Track known bad connections
#         self._known_bad: Set[WebSocket] = set()
#         print(" Sir Hawkington's Distinguished WebSocket Manager initialized")
        
#         # Start the heartbeat
#         self._start_heartbeat()
#         self._max_retries = 3
#         self._retry_delay = 1.0
    
#     async def connect(self, websocket: WebSocket):
#         """Add a websocket connection with proper locking."""
#         async with self._connection_lock:
#             if websocket not in self.active_connections:
#                 self.active_connections.append(websocket)
#                 # Initialize connection health tracking
#                 self.connection_health[websocket] = {
#                     "connected_at": time.time(),
#                     "last_successful_msg": time.time(),
#                     "error_count": 0,
#                     "client_id": f"client_{id(websocket) % 10000}"
#                 }
#                 print(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
    
#     async def disconnect(self, websocket: WebSocket):
#         """Remove a websocket connection with proper locking."""
#         async with self._connection_lock:
#             if websocket in self.active_connections:
#                 self.active_connections.remove(websocket)
#                 # Clean up health tracking
#                 if websocket in self.connection_health:
#                     client_id = self.connection_health[websocket].get("client_id", "unknown")
#                     del self.connection_health[websocket]
                    
#                 # Remove from known bad if present
#                 self._known_bad.discard(websocket)
                
#                 print(f"👋 WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
    
#     async def broadcast(self, message: Dict[str, Any]):
#         """Broadcast a message to all active connections."""
#         async with self._connection_lock:
#             # Make a copy of the connections to avoid modification during iteration
#             connections = [c for c in self.active_connections if c not in self._known_bad]
        
#         # Send messages outside the lock to avoid deadlocks
#         disconnected_connections = []
#         for connection in connections:
#             # Skip known bad connections
#             if connection in self._known_bad:
#                 continue
                
#             success = await self.send_to_client(connection, message)
#             if not success:
#                 disconnected_connections.append(connection)
#                 # Mark as known bad to avoid future attempts
#                 self._known_bad.add(connection)
#             else:
#                 # Update last successful message time
#                 if connection in self.connection_health:
#                     self.connection_health[connection]["last_successful_msg"] = time.time()
#                     self.connection_health[connection]["error_count"] = 0
        
#         # Remove all disconnected connections
#         if disconnected_connections:
#             async with self._connection_lock:
#                 for connection in disconnected_connections:
#                     if connection in self.active_connections:
#                         self.active_connections.remove(connection)
#                         # Clean up health tracking
#                         if connection in self.connection_health:
#                             client_id = self.connection_health[connection].get("client_id", "unknown")
#                             del self.connection_health[connection]
                            
#                 print(f"🧹 Removed {len(disconnected_connections)} closed connections. Remaining: {len(self.active_connections)}")

#     async def handle_connection(self, websocket: WebSocket):
#         """Handle connection with retry logic"""
#         # Start the heartbeat task if it's not already running
#         await self.start_heartbeat_if_needed()
        
#         retries = 0
#         while retries < self._max_retries:
#             try:
#                 await self.connect(websocket)
#                 return
#             except Exception as e:
#                 retries += 1
#                 print(f"Error connecting WebSocket (attempt {retries}/{self._max_retries}): {e}")
#                 await asyncio.sleep(self._retry_delay * retries)
        
#         print("Maximum connection attempts reached")
#         return False

#     async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
#         """Send a message to a specific client with error handling."""
#         # Get client ID for better logging
#         client_id = "unknown"
#         if websocket in self.connection_health:
#             client_id = self.connection_health[websocket].get("client_id", "unknown")
            
#         try:
#             # Use a timeout to prevent hanging on broken connections
#             await asyncio.wait_for(websocket.send_json(message), timeout=2.0)
#             # Update health tracking on success
#             if websocket in self.connection_health:
#                 self.connection_health[websocket]["last_successful_msg"] = time.time()
#             return True
#         except (WebSocketDisconnect, asyncio.TimeoutError) as e:
#             print(f"⚠️ Client {client_id}: Failed to send message: {e}")
#             # Update error count
#             if websocket in self.connection_health:
#                 self.connection_health[websocket]["error_count"] += 1
#             return False
#         except Exception as e:
#             print(f"❌ Client {client_id}: Unexpected error sending message: {e}")
#             # Check specifically for EPIPE errors which indicate broken pipe
#             if "EPIPE" in str(e) or "ConnectionClosed" in str(e) or "WebSocketDisconnect" in str(e):
#                 print(f"🚧 Client {client_id}: Connection closed or broken pipe, marking as bad")
#                 self._known_bad.add(websocket)
            
#             # Update error count
#             if websocket in self.connection_health:
#                 self.connection_health[websocket]["error_count"] += 1
#             return False

#     def _start_heartbeat(self):
#         """Start a background task to send heartbeats and clean up dead connections."""
#         # Store the coroutine for later execution when an event loop is available
#         # We'll start it in the handle_connection method which runs in an event loop
#         self._heartbeat_running = False
        
#         print("💓 Heartbeat task prepared but not started yet")
    
#     async def start_heartbeat_if_needed(self):
#         """Start the heartbeat task if it's not already running"""
#         if self._heartbeat_running:
#             return
            
#         async def heartbeat_task():
#             self._heartbeat_running = True
#             print("💓 Heartbeat task started")
#             while True:
#                 try:
#                     await self._send_heartbeats()
#                     await self._cleanup_dead_connections()
#                     await asyncio.sleep(15)  # Send heartbeat every 15 seconds
#                 except Exception as e:
#                     print(f"❌ Error in heartbeat task: {e}")
#                     await asyncio.sleep(5)  # Shorter sleep on error
        
#         # Now we're in an event loop, so we can create the task
#         self._heartbeat_task = asyncio.create_task(heartbeat_task())
    
#     async def _send_heartbeats(self):
#         """Send heartbeat messages to all connections to keep them alive."""
#         heartbeat_message = {
#             "type": "heartbeat",
#             "timestamp": time.time()
#         }
        
#         async with self._connection_lock:
#             # Make a copy of the connections to avoid modification during iteration
#             connections = [c for c in self.active_connections if c not in self._known_bad]
        
#         for connection in connections:
#             # Skip known bad connections
#             if connection in self._known_bad:
#                 continue
                
#             try:
#                 # Use a shorter timeout for heartbeats
#                 await asyncio.wait_for(connection.send_json(heartbeat_message), timeout=1.0)
#                 # Update last successful message time
#                 if connection in self.connection_health:
#                     self.connection_health[connection]["last_heartbeat"] = time.time()
#             except Exception:
#                 # Don't log heartbeat errors to avoid spam
#                 # Just increment error count
#                 if connection in self.connection_health:
#                     self.connection_health[connection]["error_count"] += 1
    
#     async def _cleanup_dead_connections(self):
#         """Remove connections that haven't responded to heartbeats."""
#         now = time.time()
#         to_remove = []
        
#         async with self._connection_lock:
#             for connection in self.active_connections:
#                 if connection in self.connection_health:
#                     health = self.connection_health[connection]
#                     # Check if connection is dead (no successful message in 30 seconds)
#                     if now - health.get("last_successful_msg", 0) > 30:
#                         client_id = health.get("client_id", "unknown")
#                         print(f"⚰️ Client {client_id}: Connection dead, removing")
#                         to_remove.append(connection)
#                     # Or if it has too many errors
#                     elif health.get("error_count", 0) > 5:
#                         client_id = health.get("client_id", "unknown")
#                         print(f"💀 Client {client_id}: Too many errors, removing")
#                         to_remove.append(connection)
            
#             # Remove dead connections
#             for connection in to_remove:
#                 if connection in self.active_connections:
#                     self.active_connections.remove(connection)
#                 # Clean up health tracking
#                 if connection in self.connection_health:
#                     del self.connection_health[connection]
#                 # Remove from known bad
#                 self._known_bad.discard(connection)
            
#             if to_remove:
#                 print(f"🧹 Removed {len(to_remove)} dead connections. Remaining: {len(self.active_connections)}")


# # Sir Hawkington's Distinguished WebSocket Manager
# websocket_manager = WebSocketManager()