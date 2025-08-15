"""
Meth Snail WebSocket Handler V2
High-energy optimization WebSocket communication with shell-spinning support
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from app.core.database import get_async_db
from app.models.meth_snail_model import MethSnailJitterLevels, MethSnailOptimizationStats
from .decision_engine import (
    meth_snail_brainV2,
    analyze_for_websocket as analyze_metrics
)

logger = logging.getLogger("MethSnail.WebSocket")

class MethSnailWebSocketHandler:
    """
    Dedicated WebSocket handler for Meth Snail
    
    Handles high-energy optimization communication with proper shell-spinning
    and real-time jitter level tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MethSnail.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.shell_spin_count = 0
        self.successful_analyses = 0
        self.caffeine_level = "MAXIMUM"
        self.active_connections: Dict[str, Any] = {}
        self.broadcast_task = None
        self.broadcast_interval = 1.0  # seconds
        
        self.logger.info("🐌💨 Meth Snail WebSocket Handler V2 initialized - CAFFEINE LEVELS: MAXIMUM")
        
        # Start the broadcast task
        self._start_broadcast_task()
    
    def _start_broadcast_task(self):
        """Start the background task for broadcasting updates"""
        if self.broadcast_task is None or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self._broadcast_updates())
    
    async def connect(self, client_id: str, websocket: Any):
        """Register a new WebSocket connection"""
        self.active_connections[client_id] = websocket
        self.logger.info(f"New WebSocket connection: {client_id}")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.logger.info(f"WebSocket disconnected: {client_id}")
    
    async def _broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        try:
            while self.active_connections:
                current_time = datetime.utcnow()
                
                # Get latest jitter data
                jitter_data = await self._get_latest_jitter_data()
                if jitter_data:
                    await self._broadcast({
                        "type": "jitter_update",
                        "data": jitter_data,
                        "timestamp": current_time.isoformat()
                    })
                
                # Get latest optimization metrics
                metrics_data = await self._get_latest_metrics()
                if metrics_data:
                    await self._broadcast({
                        "type": "metrics_update",
                        "data": metrics_data,
                        "timestamp": current_time.isoformat()
                    })
                
                await asyncio.sleep(self.broadcast_interval)
                
        except Exception as e:
            self.logger.error(f"Error in broadcast_updates: {str(e)}")
            # Re-raise to trigger task recreation
            raise
    
    async def _broadcast(self, message: Dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message_str)
            except Exception as e:
                self.logger.error(f"Error sending to {client_id}: {str(e)}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def _get_latest_jitter_data(self) -> Optional[Dict]:
        """Get the latest jitter level data from the database"""
        async with get_async_db() as db:
            try:
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
                self.logger.error(f"Error getting latest jitter data: {str(e)}")
                return None
    
    async def _get_latest_metrics(self) -> Optional[Dict]:
        """Get the latest optimization metrics from the database"""
        async with get_async_db() as db:
            try:
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
                self.logger.error(f"Error getting latest metrics: {str(e)}")
                return None
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through Meth Snail's optimization analysis
        """
        self.processing_count += 1
        
        try:
            decision = await analyze_metrics(metrics_data, user_id)
            
            if decision is None:
                # SHELL SPINNING
                self.shell_spin_count += 1
                self.logger.warning(f"🐌🔄 Meth Snail is spinning shell - insufficient data for optimization")
                
                return {
                    'agent_name': 'meth_snail',
                    'decision_type': 'shell_spinning',
                    'message': '🐌🔄 *shell spinning intensifies* - Need more data for optimization!',
                    'confidence': 0.0,
                    'shell_state': 'spinning',
                    'data_quality_issue': True,
                    'urgency': 'MODERATE',
                    'rationale': 'Insufficient data quality for optimization analysis',
                    'caffeine_level': self.caffeine_level,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'optimization_possible': False
                }
            
            self.successful_analyses += 1
            return self._format_meth_snail_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🐌❌ Meth Snail processing failed: {str(e)}")
            
            return {
                'agent_name': 'meth_snail',
                'decision_type': 'error',
                'message': f'🐌💥 Optimization circuits overloaded! Error: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'shell_state': 'cracked',
                'caffeine_level': 'DEPLETED',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'optimization_possible': False
            }
    
    def _format_meth_snail_decision(self, decision) -> Dict[str, Any]:
        """Format Meth Snail's decision with high-energy precision"""
        return {
            'agent_name': 'meth_snail',
            'decision_type': decision.priority.value,
            'message': decision.rationale,
            'confidence': round(decision.confidence, 3),
            'urgency': decision.urgency,
            'actions_count': len(decision.actions),
            'estimated_impact': decision.estimated_impact,
            'analysis_depth': decision.analysis_depth.value,
            'data_quality_score': round(decision.data_quality_score, 3),
            'shell_spin_count': decision.shell_spin_count,
            'shell_state': 'optimized',
            'timestamp': decision.timestamp.isoformat(),
            'optimization_actions': decision.actions[:5],
            'caffeine_level': self.caffeine_level,
            'optimization_possible': True,
            'energy_level': 'MAXIMUM'
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get Meth Snail's WebSocket handler statistics"""
        return {
            'agent_name': 'meth_snail',
            'handler_version': '2.0.0',
            'total_processing_count': self.processing_count,
            'successful_analyses': self.successful_analyses,
            'error_count': self.error_count,
            'shell_spin_count': self.shell_spin_count,
            'success_rate': self.successful_analyses / max(self.processing_count, 1),
            'shell_spin_rate': self.shell_spin_count / max(self.processing_count, 1),
            'caffeine_level': self.caffeine_level,
            'status': 'OPERATIONAL',
            'optimization_status': 'READY'
        }

# Global handler instance
_meth_snail_handler = None

async def get_meth_snail_websocket_handler():
    global _meth_snail_handler
    if _meth_snail_handler is None:
        _meth_snail_handler = MethSnailWebSocketHandler()
    return _meth_snail_handler