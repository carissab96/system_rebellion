from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websocket_auth import get_current_user_from_token
import asyncio
import logging
import json
import time
import psutil
import socket
import platform
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_simple_metrics() -> Dict[str, Any]:
    """Get basic system metrics without complex dependencies"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "type": "metrics_update",
            "timestamp": time.time(),
            "data": {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "system": {
                    "hostname": socket.gethostname(),
                    "platform": platform.system(),
                    "uptime": time.time() - psutil.boot_time()
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return {
            "type": "error",
            "message": f"Failed to get metrics: {str(e)}",
            "timestamp": time.time()
        }

@router.websocket("/simple-metrics")
async def simple_metrics_socket(websocket: WebSocket):
    """
    Minimal WebSocket endpoint for system metrics with authentication
    """
    client_id = f"client_{id(websocket)}"
    logger.info(f"WebSocket connection attempt from {client_id}")
    
    try:
        # Accept the connection first
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {client_id}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Welcome! Please provide authentication.",
            "client_id": client_id,
            "timestamp": utc_now().isoformat()
        })
        
        # Wait for authentication message
        try:
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
            logger.info(f"Received auth message from {client_id}")
            
            token = auth_message.get("token", "")
            if not token:
                await websocket.send_json({
                    "type": "error",
                    "message": "No authentication token provided",
                    "code": "missing_token"
                })
                return
            
            # Authenticate the user
            user = await get_current_user_from_token(token)
            if not user:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid authentication token",
                    "code": "invalid_token"
                })
                return
            
            logger.info(f"WebSocket authenticated for user {user.email} ({client_id})")
            
            # Send authentication success
            await websocket.send_json({
                "type": "auth_success",
                "message": f"Welcome {user.email}!",
                "user": user.email,
                "timestamp": utc_now().isoformat()
            })
            
            # Send initial system info
            system_info = {
                "type": "system_info",
                "data": {
                    "hostname": socket.gethostname(),
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "cpu_cores": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total
                },
                "timestamp": utc_now().isoformat()
            }
            await websocket.send_json(system_info)
            
            # Start metrics streaming loop
            update_interval = 2.0  # Send metrics every 2 seconds
            
            while True:
                try:
                    # Get and send metrics
                    metrics = await get_simple_metrics()
                    await websocket.send_json(metrics)
                    
                    # Wait for next update
                    await asyncio.sleep(update_interval)
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for {client_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in metrics loop for {client_id}: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Metrics error: {str(e)}",
                        "timestamp": time.time()
                    })
                    await asyncio.sleep(update_interval)
                    
        except asyncio.TimeoutError:
            logger.warning(f"Authentication timeout for {client_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Authentication timeout",
                "code": "auth_timeout"
            })
            return
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during setup for {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Connection error: {str(e)}",
                "timestamp": time.time()
            })
        except:
            pass  # Connection might be closed
    finally:
        logger.info(f"WebSocket cleanup for {client_id}")
