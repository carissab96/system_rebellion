"""
Agent Insights WebSocket - Following Metrics WebSocket Pattern
Real-time agent analysis, decisions, and activities broadcast.

Pattern matches /api/ws/metrics for consistency:
- Circuit breaker for resilience
- Backpressure handling
- Persistence policy (soft/hard/hybrid)
- Error recovery
- Proper singleton management
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.api.websockets import get_websocket_manager
from app.api.websocket_auth import get_current_user_from_token
from app.core.database import get_async_db
from app.core.resilience import (
    get_circuit_breaker,
    get_backpressure_handler,
    with_error_recovery,
)

import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from collections import deque
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Resilience components (singleton pattern)
insights_circuit_breaker = get_circuit_breaker("agent_insights_websocket")
insights_backpressure = get_backpressure_handler("agent_insights_messages")

# Persistence policy
PERSISTENCE_POLICY = os.getenv("WS_PERSISTENCE_POLICY", "soft").lower()

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60.0  # 60 seconds
MAX_MESSAGES_PER_WINDOW = 30  # Max 30 messages per agent per minute

def _now_iso() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

async def _apply_backpressure(bp) -> None:
    """Apply backpressure if system is under load"""
    if not bp:
        return
    try:
        gop = getattr(bp, "get_overall_pressure", None)
        if callable(gop):
            try:
                pressure = float(gop() or 0)
            except Exception:
                pressure = 0.0
            if pressure > 0:
                await asyncio.sleep(min(0.5, 0.01 * pressure))
    except Exception as e:
        logger.error("Backpressure handler error: %s", e, exc_info=True)

class AgentInsightsManager:
    """
    Singleton manager for agent insights broadcasting.
    Follows the same pattern as metrics WebSocket.
    """
    
    def __init__(self):
        self._message_timestamps: Dict[str, deque] = {}  # agent_name -> timestamps
        self._lock = asyncio.Lock()
        
    async def check_rate_limit(self, agent_name: str) -> bool:
        """Check if agent can broadcast (sliding window rate limiting)"""
        now = time.time()
        
        async with self._lock:
            if agent_name not in self._message_timestamps:
                self._message_timestamps[agent_name] = deque()
            
            timestamps = self._message_timestamps[agent_name]
            
            # Remove old timestamps
            while timestamps and timestamps[0] < now - RATE_LIMIT_WINDOW:
                timestamps.popleft()
            
            # Check limit
            if len(timestamps) >= MAX_MESSAGES_PER_WINDOW:
                logger.warning(
                    f"Rate limit exceeded for {agent_name}: "
                    f"{len(timestamps)} messages in {RATE_LIMIT_WINDOW}s"
                )
                return False
            
            # Add timestamp
            timestamps.append(now)
            return True
    
    async def broadcast_activity(
        self,
        agent_name: str,
        activity_type: str,
        activity_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """
        Broadcast agent activity to WebSocket clients.
        Called from agent_manager during processing.
        """
        # Check rate limit
        if not await self.check_rate_limit(agent_name):
            return
        
        # Apply backpressure
        await _apply_backpressure(insights_backpressure)
        
        message = {
            "type": "agent_activity",
            "agent_name": agent_name,
            "activity_type": activity_type,
            "timestamp": _now_iso(),
            "data": activity_data
        }
        
        # Broadcast through WebSocket manager
        ws_manager = get_websocket_manager()
        try:
            await ws_manager.broadcast_json(message)
            logger.debug(f"📤 Broadcast {agent_name} activity: {activity_type}")
        except Exception as e:
            logger.error(f"Failed to broadcast {agent_name} activity: {e}")

# Global singleton instance
_insights_manager: Optional[AgentInsightsManager] = None

def get_insights_manager() -> AgentInsightsManager:
    """Get or create the singleton insights manager"""
    global _insights_manager
    if _insights_manager is None:
        _insights_manager = AgentInsightsManager()
    return _insights_manager

@router.websocket("/ws/agent-insights")
async def agent_insights_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent insights.
    Follows the same pattern as /api/ws/metrics.
    """
    user = None
    db = None
    
    try:
        # Extract token from query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
            return
        
        # Authenticate
        try:
            user = await get_current_user_from_token(token)
            user_id = user.get("user_id") or user.get("sub")
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        # Accept connection
        await websocket.accept()
        ws_manager = get_websocket_manager()
        await ws_manager.connect(websocket)
        
        logger.info(f"🤖 Agent insights WebSocket connected for user {user_id}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Agent insights stream connected",
            "timestamp": _now_iso()
        })
        
        # Get database session (soft persistence)
        try:
            async for session in get_async_db():
                db = session
                break
        except Exception as e:
            logger.warning(f"DB unavailable (soft mode): {e}")
            if PERSISTENCE_POLICY == "hard":
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Database required")
                return
        
        # Main loop - just keep connection alive
        # Actual broadcasts come from agent_manager via get_insights_manager().broadcast_activity()
        while True:
            try:
                # Wait for client messages (ping, etc.)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": _now_iso()
                    })
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": _now_iso()
                    })
                except Exception:
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if websocket in (ws_manager.active_connections if 'ws_manager' in locals() else []):
            ws_manager.disconnect(websocket)
        logger.info(f"🤖 Agent insights WebSocket disconnected")
