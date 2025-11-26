"""
Meth Snail WebSocket Handler
Handles real-time updates for jitter levels and shell spins
Now queries from central_memory_bank with pattern insights!
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.agent_memory_banks import (
    CentralMemoryBank,
    UserLearningPatterns,
)
from app.models.agent_memory import AgentGlobalPattern
from app.ai_agents.meth_snail.constants import AGENT_NAME, JITTER_THRESHOLDS
from app.core.database import get_async_session

logger = logging.getLogger(__name__)

class MethSnailWebSocketHandler:
    """Handles WebSocket connections for Meth Snail's real-time updates with pattern insights"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.broadcast_task = None
        self.broadcast_interval = 1.0  # seconds
        self.pattern_cache: Dict[str, Any] = {}  # Cache patterns for performance
        self.pattern_cache_ttl = 300  # 5 minutes
        self.last_pattern_update = None
        self.agent_name = AGENT_NAME
    
    async def connect(self, websocket: WebSocket, client_id: str, user_id: Optional[str] = None):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "user_id": user_id
        }
        logger.info(f"Meth Snail WebSocket connected: {client_id} (user: {user_id})")
        
        # Send initial data including patterns
        if user_id:
            await self.send_initial_data(client_id, user_id)
        
        # Start broadcast task if not already running
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.broadcast_updates())
    
    def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Meth Snail WebSocket disconnected: {client_id}")
    
    async def send_initial_data(self, client_id: str, user_id: str):
        """Send initial data packet including patterns to new connection"""
        try:
            async for session in get_async_session():
                # Get latest jitter data
                jitter_data = await self.get_latest_jitter_data(session, user_id)
                
                # Get latest metrics
                metrics_data = await self.get_latest_metrics(session, user_id)
                
                # Get learned patterns
                patterns = await self.get_user_patterns(session, user_id)
                
                # Get shell spin stats
                shell_spin_stats = await self.get_shell_spin_stats(session, user_id)
                
                initial_packet = {
                    "type": "initial_data",
                    "data": {
                        "jitter": jitter_data,
                        "metrics": metrics_data,
                        "patterns": patterns,
                        "shell_spin_stats": shell_spin_stats
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                connection = self.active_connections[client_id]
                await connection["websocket"].send_text(json.dumps(initial_packet))
                
        except Exception as e:
            logger.error(f"Error sending initial data to {client_id}: {str(e)}")
    
    async def broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        try:
            while self.active_connections:
                current_time = datetime.utcnow()
                
                async for session in get_async_session():
                    # Broadcast to each user with their specific data
                    for client_id, connection in list(self.active_connections.items()):
                        user_id = connection.get("user_id")
                        if not user_id:
                            continue
                        
                        try:
                            # Get latest jitter data
                            jitter_data = await self.get_latest_jitter_data(session, user_id)
                            if jitter_data:
                                await self.send_to_client(client_id, {
                                    "type": "jitter_update",
                                    "data": jitter_data,
                                    "timestamp": current_time.isoformat()
                                })
                            
                            # Get latest optimization metrics
                            metrics_data = await self.get_latest_metrics(session, user_id)
                            if metrics_data:
                                await self.send_to_client(client_id, {
                                    "type": "metrics_update",
                                    "data": metrics_data,
                                    "timestamp": current_time.isoformat()
                                })
                            
                            # Check for new patterns periodically
                            if not self.last_pattern_update or \
                               (current_time - self.last_pattern_update).seconds > 60:
                                patterns = await self.get_user_patterns(session, user_id)
                                if patterns:
                                    await self.send_to_client(client_id, {
                                        "type": "pattern_update",
                                        "data": patterns,
                                        "timestamp": current_time.isoformat()
                                    })
                                    self.last_pattern_update = current_time
                            
                            # Send alerts for critical events
                            alerts = await self.check_for_alerts(session, user_id)
                            if alerts:
                                await self.send_to_client(client_id, {
                                    "type": "alert",
                                    "data": alerts,
                                    "timestamp": current_time.isoformat()
                                })
                                
                        except Exception as e:
                            logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                
                await asyncio.sleep(self.broadcast_interval)
                
        except Exception as e:
            logger.error(f"Error in broadcast_updates: {str(e)}")
            # Re-raise to trigger task recreation
            raise
    
    async def send_to_client(self, client_id: str, message: Dict):
        """Send a message to a specific client"""
        if client_id not in self.active_connections:
            return
            
        try:
            connection = self.active_connections[client_id]
            await connection["websocket"].send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to {client_id}: {str(e)}")
            self.disconnect(client_id)
    
    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection["websocket"].send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {str(e)}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def get_latest_jitter_data(self, session: AsyncSession, user_id: str) -> Optional[Dict]:
        """Get the latest jitter level data from central memory bank"""
        try:
            # Query the most recent jitter level update
            result = await session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.STATE_CHANGED.value)
                .where(CentralMemoryBank.subject_kind == "jitter_level")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(1)
            )
            
            latest = result.scalar_one_or_none()
            if not latest:
                return None
            
            # Extract jitter data from the details JSON
            details = latest.details or {}
            
            # Get jitter level name
            jitter_level = details.get('current_jitter_level', 0.0)
            jitter_name = self._get_jitter_level_name(jitter_level)
            
            return {
                "current_jitter_level": jitter_level,
                "jitter_level_name": jitter_name,
                "peak_jitter_level": details.get('peak_jitter_level', 0.0),
                "baseline_jitter_level": details.get('baseline_jitter_level', 0.1),
                "caffeine_level_mg": details.get('caffeine_level_mg', 0.0),
                "is_decaffeinated": details.get('is_decaffeinated', False),
                "shell_spin_probability": details.get('shell_spin_probability', 0.05),
                "optimization_effectiveness": details.get('optimization_effectiveness', 0.9),
                "focus_level": details.get('focus_level', 0.5),
                "hypercaffeinated": details.get('hypercaffeinated', False),
                "requires_stick_intervention": details.get('requires_stick_intervention', False),
                "vic20_mediation_requested": details.get('vic20_mediation_requested', False),
                "energy_source": details.get('energy_source', 'none'),
                "jitter_trend": details.get('jitter_trend', 'stable'),
                "foil_hat_status": latest.agent_metadata.get('foil_hat_status', 'secure')
            }
        except Exception as e:
            logger.error(f"Error getting latest jitter data: {str(e)}")
            return None
    
    async def get_latest_metrics(self, session: AsyncSession, user_id: str) -> Optional[Dict]:
        """Get the latest optimization metrics from central memory bank"""
        try:
            # Query the most recent optimization metrics
            result = await session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.METRICS_ANALYZED.value)
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(1)
            )
            
            latest = result.scalar_one_or_none()
            if not latest:
                return None
            
            # Extract metrics from the details JSON
            details = latest.details or {}
            
            # Calculate improvements
            cpu_improvement = None
            memory_improvement = None
            
            if details.get('cpu_usage_before') is not None and details.get('cpu_usage_after') is not None:
                cpu_improvement = details['cpu_usage_before'] - details['cpu_usage_after']
            
            if details.get('memory_usage_before') is not None and details.get('memory_usage_after') is not None:
                memory_improvement = details['memory_usage_before'] - details['memory_usage_after']
            
            return {
                "optimization_success": details.get('optimization_success', False),
                "shell_spins_executed": details.get('shell_spin_count', 0),
                "cpu_usage_before": details.get('cpu_usage_before'),
                "cpu_usage_after": details.get('cpu_usage_after'),
                "cpu_improvement": cpu_improvement,
                "memory_usage_before": details.get('memory_usage_before'),
                "memory_usage_after": details.get('memory_usage_after'),
                "memory_improvement": memory_improvement,
                "energy_drink_level": details.get('energy_drink_level', 0),
                "caffeinated": latest.metadata_.get('caffeinated', False),
                "timestamp": latest.occurred_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting latest metrics: {str(e)}")
            return None
    
    async def get_user_patterns(self, session: AsyncSession, user_id: str) -> Optional[Dict]:
        """Get user's learned patterns"""
        try:
            # Check cache first
            cache_key = f"{user_id}_patterns"
            if cache_key in self.pattern_cache:
                cached_data = self.pattern_cache[cache_key]
                if (datetime.utcnow() - cached_data['timestamp']).seconds < self.pattern_cache_ttl:
                    return cached_data['data']
            
            # Get user patterns
            user_result = await session.execute(
                select(UserLearningPattern)
                .where(UserLearningPattern.user_id == user_id)
                .where(UserLearningPattern.most_effective_agent == self.agent_name)
                                .order_by(desc(UserLearningPattern.timestamp))
                .limit(10)
            )
            
            user_patterns = user_result.scalars().all()
            
            # Get global patterns
            global_result = await session.execute(
                select(AgentGlobalPattern)
                .where(AgentGlobalPattern.pattern_key.like(f"{self.agent_name}%"))
                .order_by(desc(AgentGlobalPattern.updated_at))
                .limit(5)
            )
            
            global_patterns = global_result.scalars().all()
            
            patterns_data = {
                "user_patterns": [
                    {
                        "pattern_id": pattern.pattern_id,
                        "pattern_type": pattern.interaction_pattern.get("pattern_type", "unknown"),
                        "confidence": pattern.interaction_pattern.get("confidence", 0),
                        "effectiveness": pattern.agent_effectiveness_ranking.get(self.agent_name, 0),
                        "timestamp": pattern.timestamp.isoformat()
                    } for pattern in user_patterns
                ],
                "global_patterns": [
                    {
                        "pattern_key": pattern.pattern_key,
                        "confidence": pattern.value.get("confidence", 0),
                        "pattern_type": pattern.value.get("pattern_data", {}).get("pattern_type", "unknown"),
                        "updated_at": pattern.updated_at.isoformat()
                    } for pattern in global_patterns
                ],
                "pattern_summary": {
                    "total_patterns": len(user_patterns),
                    "high_confidence_patterns": sum(1 for p in user_patterns 
                                                   if p.interaction_pattern.get("confidence", 0) > 0.8),
                    "optimization_patterns": sum(1 for p in user_patterns 
                                                if p.interaction_pattern.get("pattern_type") == "optimization"),
                    "shell_spin_patterns": sum(1 for p in user_patterns 
                                              if p.interaction_pattern.get("pattern_type") == "shell_spinning")
                }
            }
            
            # Cache the result
            self.pattern_cache[cache_key] = {
                'data': patterns_data,
                'timestamp': datetime.utcnow()
            }
            
            return patterns_data
            
        except Exception as e:
            logger.error(f"Error getting user patterns: {str(e)}")
            return None
    
    async def get_shell_spin_stats(self, session: AsyncSession, user_id: str) -> Optional[Dict]:
        """Get shell spin statistics"""
        try:
            # Get shell spin count for last 24 hours
            cutoff = datetime.utcnow() - timedelta(hours=24)
            
            result = await session.execute(
                select(func.count(CentralMemoryBank.id))
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ANOMALY_DETECTED.value)
                .where(CentralMemoryBank.string_value == "shell_spin")
                .where(CentralMemoryBank.occurred_at >= cutoff)
            )
            
            recent_spins = result.scalar() or 0
            
            # Get all-time shell spin count
            all_time_result = await session.execute(
                select(func.count(CentralMemoryBank.id))
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ANOMALY_DETECTED.value)
                .where(CentralMemoryBank.string_value == "shell_spin")
            )
            
            all_time_spins = all_time_result.scalar() or 0
            
            # Get last shell spin
            last_spin_result = await session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ANOMALY_DETECTED.value)
                .where(CentralMemoryBank.string_value == "shell_spin")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(1)
            )
            
            last_spin = last_spin_result.scalar_one_or_none()
            
            return {
                "shell_spins_24h": recent_spins,
                "shell_spins_all_time": all_time_spins,
                "last_spin_timestamp": last_spin.occurred_at.isoformat() if last_spin else None,
                "last_spin_cause": last_spin.details.get("cause", "unknown") if last_spin else None,
                "spin_rate": "HIGH" if recent_spins > 10 else "MODERATE" if recent_spins > 5 else "LOW"
            }
            
        except Exception as e:
            logger.error(f"Error getting shell spin stats: {str(e)}")
            return None
    
    async def check_for_alerts(self, session: AsyncSession, user_id: str) -> Optional[List[Dict]]:
        """Check for alert conditions"""
        alerts = []
        
        try:
            # Check for recent high jitter
            jitter_data = await self.get_latest_jitter_data(session, user_id)
            if jitter_data and jitter_data.get("current_jitter_level", 0) > 0.8:
                alerts.append({
                    "alert_type": "high_jitter",
                    "severity": "warning" if jitter_data["current_jitter_level"] < 0.9 else "critical",
                    "message": f"Jitter level critical: {jitter_data['jitter_level_name']}",
                    "recommendation": "Consider immediate decaffeination protocol"
                })
            
            # Check for excessive shell spinning
            shell_stats = await self.get_shell_spin_stats(session, user_id)
            if shell_stats and shell_stats.get("shell_spins_24h", 0) > 20:
                alerts.append({
                    "alert_type": "excessive_shell_spinning",
                    "severity": "warning",
                    "message": f"Excessive shell spinning: {shell_stats['shell_spins_24h']} in 24h",
                    "recommendation": "Data quality issues detected - investigation required"
                })
            
            # Check for optimization failures
            recent_metrics = await self.get_latest_metrics(session, user_id)
            if recent_metrics and not recent_metrics.get("optimization_success", True):
                alerts.append({
                    "alert_type": "optimization_failure",
                    "severity": "info",
                    "message": "Recent optimization attempt failed",
                    "recommendation": "Review system metrics for anomalies"
                })
            
            return alerts if alerts else None
            
        except Exception as e:
            logger.error(f"Error checking for alerts: {str(e)}")
            return None
    
    def _get_jitter_level_name(self, jitter_level: float) -> str:
        """Convert jitter level to human-readable name"""
        if jitter_level < JITTER_THRESHOLDS["calm"]:
            return "CALM"
        elif jitter_level < JITTER_THRESHOLDS["normal"]:
            return "NORMAL"
        elif jitter_level < JITTER_THRESHOLDS["energized"]:
            return "ENERGIZED"
        elif jitter_level < JITTER_THRESHOLDS["jittery"]:
            return "JITTERY"
        else:
            return "HYPERCAFFEINATED"
    
    async def handle_client_message(self, client_id: str, message: str):
        """Handle messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                await self.send_to_client(client_id, {"type": "pong"})
            
            elif message_type == "request_patterns":
                # Client requesting pattern update
                connection = self.active_connections.get(client_id)
                if connection and connection.get("user_id"):
                    async for session in get_async_session():
                        patterns = await self.get_user_patterns(session, connection["user_id"])
                        await self.send_to_client(client_id, {
                            "type": "pattern_update",
                            "data": patterns,
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            elif message_type == "request_stats":
                # Client requesting full stats update
                connection = self.active_connections.get(client_id)
                if connection and connection.get("user_id"):
                    async for session in get_async_session():
                        jitter_data = await self.get_latest_jitter_data(session, connection["user_id"])
                        metrics_data = await self.get_latest_metrics(session, connection["user_id"])
                        shell_stats = await self.get_shell_spin_stats(session, connection["user_id"])
                        
                        await self.send_to_client(client_id, {
                            "type": "stats_update",
                            "data": {
                                "jitter": jitter_data,
                                "metrics": metrics_data,
                                "shell_spins": shell_stats
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {str(e)}")

# Create a singleton instance
meth_snail_ws_handler = MethSnailWebSocketHandler()

async def get_meth_snail_ws_handler() -> MethSnailWebSocketHandler:
    """Get the singleton instance of MethSnailWebSocketHandler"""
    return meth_snail_ws_handler

# WebSocket endpoint
async def meth_snail_websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """WebSocket endpoint for Meth Snail real-time updates"""
    client_id = f"meth-snail-{id(websocket)}"
    
    try:
        await meth_snail_ws_handler.connect(websocket, client_id, user_id)
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            await meth_snail_ws_handler.handle_client_message(client_id, data)
                
    except WebSocketDisconnect:
        logger.info(f"Meth Snail WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in Meth Snail WebSocket: {str(e)}")
    finally:
        meth_snail_ws_handler.disconnect(client_id)