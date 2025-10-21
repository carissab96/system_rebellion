"""
Agent Events & Insights WebSocket Endpoint
UNIFIED endpoint for:
1. Real-time agent activity broadcasts (live from agent processing)
2. Historical personality events (from AgentEventLog database)

This combines the original agent-insights plan with the event logging system.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets import get_websocket_manager
from app.api.websocket_auth import get_current_user_from_token
from app.core.database import get_async_db
from app.models.agent_events import AgentEventLog

logger = logging.getLogger(__name__)
router = APIRouter()

class AgentEventsWebSocketManager:
    """
    Manages WebSocket connections for agent event streaming
    
    Supports TWO modes:
    1. Live broadcasts - Real-time agent activity as it happens
    2. Historical polling - Events from AgentEventLog database
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.polling_tasks: Dict[str, asyncio.Task] = {}  # user_id -> task
        self.last_event_id: Dict[str, int] = {}  # user_id -> last_event_id
        self._broadcast_lock = asyncio.Lock()  # Thread-safe broadcasting
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and start event polling"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"🎭 Agent events WebSocket connected for user {user_id}")
        
        # Start polling task for this user
        task = asyncio.create_task(self._poll_events(user_id))
        self.polling_tasks[user_id] = task
        
    def disconnect(self, user_id: str):
        """Disconnect WebSocket and stop polling"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
        if user_id in self.polling_tasks:
            self.polling_tasks[user_id].cancel()
            del self.polling_tasks[user_id]
            
        if user_id in self.last_event_id:
            del self.last_event_id[user_id]
            
        logger.info(f"🎭 Agent events WebSocket disconnected for user {user_id}")
        
    async def _poll_events(self, user_id: str):
        """Poll for new events and send to client"""
        poll_interval = 2.0  # seconds
        
        while user_id in self.active_connections:
            try:
                # Get new events since last poll
                events = await self._fetch_new_events(user_id)
                
                if events:
                    websocket = self.active_connections.get(user_id)
                    if websocket:
                        for event in events:
                            try:
                                await websocket.send_json({
                                    "type": "agent_event",
                                    "event": {
                                        "id": event.id,
                                        "timestamp": event.timestamp.isoformat(),
                                        "agent_name": event.agent_name,
                                        "event_type": event.event_type,
                                        "event_data": event.event_data,
                                        "severity": event.severity,
                                        "agent_state": event.agent_state
                                    }
                                })
                                # Update last event ID
                                self.last_event_id[user_id] = event.id
                            except Exception as e:
                                logger.error(f"Error sending event to {user_id}: {e}")
                                break
                
                await asyncio.sleep(poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error polling events for {user_id}: {e}")
                await asyncio.sleep(poll_interval)
                
    async def _fetch_new_events(self, user_id: str) -> list:
        """Fetch new events from database"""
        try:
            async for db in get_async_db():
                # Get events newer than last seen
                last_id = self.last_event_id.get(user_id, 0)
                
                query = select(AgentEventLog).where(
                    and_(
                        AgentEventLog.user_id == user_id,
                        AgentEventLog.id > last_id
                    )
                ).order_by(AgentEventLog.id.asc()).limit(50)
                
                result = await db.execute(query)
                events = result.scalars().all()
                
                return events
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []
            
    async def send_event(self, user_id: str, event: Dict[str, Any]):
        """Send a single event to a specific user"""
        websocket = self.active_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json({
                    "type": "agent_event",
                    "event": event
                })
            except Exception as e:
                logger.error(f"Error sending event to {user_id}: {e}")
                self.disconnect(user_id)
                
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients"""
        async with self._broadcast_lock:
            disconnected = []
            for user_id, websocket in list(self.active_connections.items()):
                try:
                    await websocket.send_json({
                        "type": "agent_event",
                        "event": event
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")
                    disconnected.append(user_id)
                    
            for user_id in disconnected:
                self.disconnect(user_id)
    
    async def broadcast_agent_activity(
        self, 
        agent_name: str, 
        activity_type: str, 
        activity_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ):
        """
        Broadcast live agent activity (called from agent_manager during processing)
        
        Args:
            agent_name: Name of the agent (sir_hawkington, the_stick, etc.)
            activity_type: Type of activity (triage_decision, monocle_yeet, etc.)
            activity_data: Activity-specific data
            user_id: Optional - broadcast to specific user only
        """
        message = {
            "type": "agent_activity",
            "agent_name": agent_name,
            "activity_type": activity_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": activity_data
        }
        
        async with self._broadcast_lock:
            if user_id:
                # Send to specific user
                websocket = self.active_connections.get(user_id)
                if websocket:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending activity to {user_id}: {e}")
                        self.disconnect(user_id)
            else:
                # Broadcast to all
                disconnected = []
                for uid, websocket in list(self.active_connections.items()):
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting activity to {uid}: {e}")
                        disconnected.append(uid)
                        
                for uid in disconnected:
                    self.disconnect(uid)

# Global manager instance
_agent_events_manager: Optional[AgentEventsWebSocketManager] = None

def get_agent_events_manager() -> AgentEventsWebSocketManager:
    """Get or create the agent events WebSocket manager"""
    global _agent_events_manager
    if _agent_events_manager is None:
        _agent_events_manager = AgentEventsWebSocketManager()
    return _agent_events_manager


@router.websocket("/ws/agent-events")
async def agent_events_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time agent personality events
    
    Events include:
    - Monocle yeets (Sir Hawkington)
    - Paper bag consumption (The Stick)
    - Shell spins (Meth Snail)
    - Supply closet raids (Hamsters)
    - Dimensional shifts (QSP)
    - Coordinations (VIC-20)
    
    Query params:
    - token: JWT authentication token
    """
    manager = get_agent_events_manager()
    user_id = None
    
    try:
        # Authenticate user
        if token:
            try:
                user = await get_current_user_from_token(token)
                user_id = user.get("user_id") or user.get("sub")
            except Exception as e:
                logger.warning(f"WebSocket auth failed: {e}")
                await websocket.close(code=1008, reason="Authentication failed")
                return
        
        if not user_id:
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        # Connect and start streaming
        await manager.connect(websocket, user_id)
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Agent events stream connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (ping/pong, filters, etc.)
                data = await websocket.receive_json()
                
                # Handle client commands
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                elif data.get("type") == "get_recent":
                    # Send recent events on demand
                    limit = data.get("limit", 20)
                    events = await _get_recent_events(user_id, limit)
                    await websocket.send_json({
                        "type": "recent_events",
                        "events": events
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            manager.disconnect(user_id)


async def _get_recent_events(user_id: str, limit: int = 20) -> list:
    """Get recent events for a user"""
    try:
        async for db in get_async_db():
            query = select(AgentEventLog).where(
                AgentEventLog.user_id == user_id
            ).order_by(AgentEventLog.timestamp.desc()).limit(limit)
            
            result = await db.execute(query)
            events = result.scalars().all()
            
            return [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "agent_name": event.agent_name,
                    "event_type": event.event_type,
                    "event_data": event.event_data,
                    "severity": event.severity,
                    "agent_state": event.agent_state
                }
                for event in reversed(events)  # Oldest first
            ]
    except Exception as e:
        logger.error(f"Error fetching recent events: {e}")
        return []
