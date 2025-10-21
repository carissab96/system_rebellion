"""
Agent Events WebSocket - Real-time Broadcast Only
Real-time agent events broadcast through WebSocket manager.

NO DATABASE POLLING - Only receives broadcasts from agents.
Identical pattern to agent_insights_websocket.py
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.api.websockets import get_websocket_manager
from app.api.websocket_auth import get_current_user_from_token
from app.core.resilience import get_circuit_breaker, get_backpressure_handler

import asyncio
import logging
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()

# Resilience components
events_circuit_breaker = get_circuit_breaker("agent_events_websocket")
events_backpressure = get_backpressure_handler("agent_events_messages")

def _now_iso() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

@router.websocket("/ws/agent-events")
async def agent_events_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent events.
    Modeled exactly after simplified_websocket_routes.py pattern.
    """
    client_id = f"client_{id(websocket)}"
    user = None
    ws_manager = get_websocket_manager()
    
    try:
        ws_start = time.time()
        
        # Accept the connection once (same as system-metrics)
        await websocket.accept()
        logger.info("WebSocket connection accepted for %s (%.2fms)", client_id, (time.time() - ws_start)*1000)

        # Authenticate strictly via query param (same as system-metrics)
        auth_start = time.time()
        token = (websocket.query_params.get("token") or "").replace("Bearer ", "").strip()
        if not token:
            await websocket.send_json({
                "type": "error",
                "message": "Missing authentication token in query string (?token=...)",
                "code": "missing_token",
            })
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            user = await get_current_user_from_token(token)
        except Exception as e:
            logger.error("Auth failed: %s", str(e))
            user = None

        if not user:
            await websocket.send_json({"type": "error", "message": "Invalid authentication token", "code": "invalid_token"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = str(getattr(user, "id", None))
        logger.info("⏱️ WebSocket authenticated for user %s (%s) - Auth took %.2fms", 
                   getattr(user, "email", None), client_id, (time.time() - auth_start)*1000)

        # Register the connection (same as system-metrics)
        # Don't call ws_manager.connect() as it tries to accept() again
        ws_manager.active_connections.add(websocket)
        logger.info("✅ WebSocket registered for %s", client_id)
        
        # Send connection confirmation (same as system-metrics)
        await websocket.send_json({
            "type": "connected",
            "message": "Agent events stream connected",
            "timestamp": _now_iso(),
            "client_id": client_id
        })
        logger.info("✅ Sent connection_established to %s", client_id)
        
        # Main loop - keep connection alive and handle client messages
        # Broadcasts come automatically through ws_manager
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
        if 'ws_manager' in locals() and websocket in ws_manager.active_connections:
            ws_manager.disconnect(websocket)
        logger.info(f"🎭 Agent events WebSocket disconnected")
