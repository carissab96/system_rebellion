"""
Agent Logs WebSocket - Dedicated endpoint for streaming backend logs
Completely separate from system-metrics WebSocket
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.api.websocket_auth import get_current_user_from_token
import asyncio
import logging
from datetime import datetime, timezone
from typing import Set

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active WebSocket connections for agent logs
agent_log_connections: Set[WebSocket] = set()

def _now_iso() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

async def broadcast_agent_log(message: dict):
    """Broadcast a log message to all connected clients"""
    disconnected = set()
    
    for websocket in agent_log_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.debug(f"Failed to send to client: {e}")
            disconnected.add(websocket)
    
    # Clean up disconnected clients
    for ws in disconnected:
        agent_log_connections.discard(ws)

@router.websocket("/ws/agent-logs")
async def agent_logs_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent logs.
    Streams backend Python logging output to frontend.
    """
    client_id = f"client_{id(websocket)}"
    user = None
    
    try:
        # Authenticate FIRST via query param (before accepting connection)
        token = (websocket.query_params.get("token") or "").replace("Bearer ", "").strip()
        if not token:
            logger.warning("WebSocket connection rejected: missing token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            user = await get_current_user_from_token(token)
        except Exception as e:
            logger.error("Auth failed: %s", str(e))
            user = None

        if not user:
            logger.warning("WebSocket connection rejected: invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # THEN accept the connection after successful authentication
        await websocket.accept()
        logger.info(f"✅ Agent logs WebSocket connected: {client_id}")

        # Register the connection
        agent_log_connections.add(websocket)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Agent logs stream connected",
            "timestamp": _now_iso(),
            "client_id": client_id
        })
        
        # Main loop - keep connection alive and handle client messages
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
        agent_log_connections.discard(websocket)
        logger.info(f"❌ Agent logs WebSocket disconnected: {client_id}")
