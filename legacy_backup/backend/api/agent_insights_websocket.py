"""
Agent Insights WebSocket Endpoint
Real-time broadcasting of agent analysis, decisions, and activities as they happen during processing.

This is separate from:
- /api/ws/metrics (system metrics only)
- /api/ws/agent-events (historical personality events from database)

Features:
- Redis caching for rate limiting
- Proper throttling (max messages per time window)
- Singleton manager pattern
- Connection pooling
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, Set
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from collections import deque

from app.api.websocket_auth import get_current_user_from_token
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

class AgentInsightsWebSocketManager:
    """
    Manages WebSocket connections for real-time agent insights broadcasting.
    
    Called by agent_manager.py during agent processing to broadcast:
    - Triage decisions
    - Analysis results
    - Recommendations
    - Agent activities
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self._broadcast_lock = asyncio.Lock()
        
        # Rate limiting with sliding window
        self._rate_limit_window = 60.0  # 60 second window
        self._max_messages_per_window = 30  # Max 30 messages per agent per minute
        self._message_timestamps: Dict[str, deque] = {}  # agent_name -> deque of timestamps
        
        # Redis for distributed rate limiting
        self._redis = None
        self._redis_prefix = "agent_insights:throttle:"
        
        # Connection health tracking
        self._connection_health: Dict[str, int] = {}  # user_id -> failed_send_count
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        async with self._broadcast_lock:
            self.active_connections[user_id] = websocket
        logger.info(f"🤖 Agent insights WebSocket connected for user {user_id}")
        
    def disconnect(self, user_id: str):
        """Disconnect WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self._connection_health:
            del self._connection_health[user_id]
        logger.info(f"🤖 Agent insights WebSocket disconnected for user {user_id}")
    
    async def _get_redis(self):
        """Get Redis client (lazy initialization)"""
        if self._redis is None:
            try:
                self._redis = await get_redis_client()
            except Exception as e:
                logger.warning(f"Redis not available for rate limiting: {e}")
                self._redis = None
        return self._redis
    
    async def _check_rate_limit(self, agent_name: str) -> bool:
        """
        Check if agent can send message (sliding window rate limiting)
        
        Returns:
            True if message allowed, False if rate limited
        """
        now = time.time()
        
        # Initialize deque for this agent if needed
        if agent_name not in self._message_timestamps:
            self._message_timestamps[agent_name] = deque()
        
        timestamps = self._message_timestamps[agent_name]
        
        # Remove timestamps outside the window
        while timestamps and timestamps[0] < now - self._rate_limit_window:
            timestamps.popleft()
        
        # Check if we're at the limit
        if len(timestamps) >= self._max_messages_per_window:
            logger.warning(
                f"Rate limit exceeded for {agent_name}: "
                f"{len(timestamps)} messages in last {self._rate_limit_window}s"
            )
            return False
        
        # Add current timestamp
        timestamps.append(now)
        
        # Also check Redis for distributed rate limiting
        redis = await self._get_redis()
        if redis:
            try:
                key = f"{self._redis_prefix}{agent_name}"
                count = await redis.incr(key)
                if count == 1:
                    await redis.expire(key, int(self._rate_limit_window))
                
                if count > self._max_messages_per_window:
                    logger.warning(f"Redis rate limit exceeded for {agent_name}: {count} messages")
                    return False
            except Exception as e:
                logger.error(f"Redis rate limit check failed: {e}")
                # Continue without Redis rate limiting
        
        return True
        
    async def broadcast_agent_activity(
        self, 
        agent_name: str, 
        activity_type: str, 
        activity_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ):
        """
        Broadcast agent activity to connected clients.
        
        Called from agent_manager.py after agent processing.
        
        Args:
            agent_name: Name of agent (sir_hawkington, the_stick, etc.)
            activity_type: Type of activity (triage_decision, optimization_applied, etc.)
            activity_data: Activity-specific data matching field mappings
            user_id: Optional - broadcast to specific user only, or all if None
        """
        # Throttle broadcasts (max 1 per agent per second)
        now = datetime.now(timezone.utc).timestamp()
        last_time = self._last_broadcast_time.get(agent_name, 0)
        
        if now - last_time < self._throttle_interval:
            logger.debug(f"Throttling {agent_name} broadcast (too frequent)")
            return
            
        self._last_broadcast_time[agent_name] = now
        
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
                        logger.debug(f"📤 Sent {agent_name} activity to user {user_id}")
                    except Exception as e:
                        logger.error(f"Error sending to {user_id}: {e}")
                        # Don't disconnect here - let the main loop handle it
            else:
                # Broadcast to all connected users
                disconnected = []
                for uid, websocket in list(self.active_connections.items()):
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to {uid}: {e}")
                        disconnected.append(uid)
                        
                # Clean up disconnected clients
                for uid in disconnected:
                    if uid in self.active_connections:
                        del self.active_connections[uid]
                        
                if disconnected:
                    logger.info(f"Cleaned up {len(disconnected)} disconnected clients")
                else:
                    logger.debug(f"📤 Broadcast {agent_name} activity to {len(self.active_connections)} clients")
    
    async def broadcast_triage_decision(
        self,
        decision_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Broadcast Sir Hawkington triage decision"""
        await self.broadcast_agent_activity(
            "sir_hawkington",
            "triage_decision",
            decision_data,
            user_id
        )
    
    async def broadcast_optimization(
        self,
        agent_name: str,
        optimization_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Broadcast agent optimization/recommendation"""
        await self.broadcast_agent_activity(
            agent_name,
            "optimization_applied",
            optimization_data,
            user_id
        )
    
    async def broadcast_analysis(
        self,
        agent_name: str,
        analysis_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Broadcast agent analysis result"""
        await self.broadcast_agent_activity(
            agent_name,
            "analysis_complete",
            analysis_data,
            user_id
        )
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global manager instance
_agent_insights_manager: Optional[AgentInsightsWebSocketManager] = None

def get_agent_insights_manager() -> AgentInsightsWebSocketManager:
    """Get or create the agent insights WebSocket manager"""
    global _agent_insights_manager
    if _agent_insights_manager is None:
        _agent_insights_manager = AgentInsightsWebSocketManager()
    return _agent_insights_manager


@router.websocket("/ws/agent-insights")
async def agent_insights_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time agent insights and activities.
    
    Broadcasts live agent analysis, decisions, and recommendations as they happen.
    
    Query params:
    - token: JWT authentication token
    
    Messages sent:
    - agent_activity: Real-time agent activities
    - pong: Response to ping
    """
    manager = get_agent_insights_manager()
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
            
        # Connect
        await manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Agent insights stream connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (ping, etc.)
                data = await websocket.receive_json()
                
                # Handle ping/pong
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
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
