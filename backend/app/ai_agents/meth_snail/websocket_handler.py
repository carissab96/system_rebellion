"""
Meth Snail WebSocket Handler
Handles real-time updates for jitter levels and shell spins
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.websockets import websocket_manager
from app.core.database import get_async_db
from app.models.agent_memory_banks import CentralMemoryBank
from app.schemas.agent_memory import MemoryPriority, MemoryType
from app.schemas.websocket import WebSocketMessage, MessageType

logger = logging.getLogger(__name__)

class MethSnailWebSocketHandler:
    """Handles WebSocket connections for Meth Snail's real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.broadcast_task = None
        self.broadcast_interval = 1.0  # seconds
        self.last_jitter_update = None
        self.last_metrics_update = None
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Meth Snail WebSocket connected: {client_id}")
        
        # Start broadcast task if not already running
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.broadcast_updates())
    
    def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Meth Snail WebSocket disconnected: {client_id}")
    
    async def broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        try:
            while self.active_connections:
                current_time = datetime.utcnow()
                
                # Get latest jitter data
                jitter_data = await self.get_latest_jitter_data()
                if jitter_data:
                    await self.broadcast({
                        "type": "jitter_update",
                        "data": jitter_data,
                        "timestamp": current_time.isoformat()
                    })
                
                # Get latest optimization metrics
                metrics_data = await self.get_latest_metrics()
                if metrics_data:
                    await self.broadcast({
                        "type": "metrics_update",
                        "data": metrics_data,
                        "timestamp": current_time.isoformat()
                    })
                
                await asyncio.sleep(self.broadcast_interval)
                
        except Exception as e:
            logger.error(f"Error in broadcast_updates: {str(e)}")
            # Re-raise to trigger task recreation
            raise
    
    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {str(e)}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def get_latest_jitter_data(self) -> Optional[Dict]:
        """Get the latest jitter level data from the database"""
        async with get_async_db() as db:
            try:
                # Get the most recent jitter level
                latest = await MethSnailJitterLevels.get_latest(db)
                if not latest:
                    return None
                    
                return {
                    "current_jitter_level": latest.current_jitter_level,
                    "peak_jitter_level": latest.peak_jitter_level,
                    "baseline_jitter_level": latest.baseline_jitter_level,
                    "caffeine_level_mg": latest.caffeine_level_mg,
                    "is_decaffeinated": latest.is_decaffeinated,
                    "shell_spin_probability": latest.shell_spin_probability,
                    "optimization_effectiveness": latest.optimization_effectiveness,
                    "focus_level": latest.focus_level,
                    "hypercaffeinated": latest.hypercaffeinated,
                    "requires_stick_intervention": latest.requires_stick_intervention,
                    "vic20_mediation_requested": latest.vic20_mediation_requested,
                    "energy_source": latest.energy_source,
                    "jitter_trend": latest.jitter_trend
                }
            except Exception as e:
                logger.error(f"Error getting latest jitter data: {str(e)}")
                return None
    
    async def get_latest_metrics(self) -> Optional[Dict]:
        """Get the latest optimization metrics from the database"""
        async with get_async_db() as db:
            try:
                # Get the most recent metrics
                latest = await MethSnailOptimizationStats.get_latest(db)
                if not latest:
                    return None
                    
                return {
                    "optimization_success": latest.optimization_success,
                    "shell_spins_executed": latest.shell_spins_executed,
                    "cpu_usage_before": latest.cpu_usage_before,
                    "cpu_usage_after": latest.cpu_usage_after,
                    "memory_usage_before": latest.memory_usage_before,
                    "memory_usage_after": latest.memory_usage_after,
                    "energy_drink_level": latest.energy_drink_level
                }
            except Exception as e:
                logger.error(f"Error getting latest metrics: {str(e)}")
                return None

# Create a singleton instance
meth_snail_ws_handler = MethSnailWebSocketHandler()

# WebSocket endpoint
async def meth_snail_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Meth Snail real-time updates"""
    client_id = f"meth-snail-{id(websocket)}"
    
    try:
        await meth_snail_ws_handler.connect(websocket, client_id)
        
        # Keep connection alive
        while True:
            # Client can send pings to check connection
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        logger.info(f"Meth Snail WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in Meth Snail WebSocket: {str(e)}")
    finally:
        meth_snail_ws_handler.disconnect(client_id)
