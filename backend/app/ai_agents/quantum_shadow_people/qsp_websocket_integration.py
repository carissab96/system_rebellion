# app/ai_agents/qsp/websocket_handler.py
"""
WebSocket handler for Quantum Shadow People
Integrates with complete database architecture
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from .decision_engine import QuantumShadowPeopleBrainV2, QSPDecision
from .database_integration import QSPDatabaseIntegration
from .constants import AGENT_NAME

def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings in nested structures"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle dataclass objects
        return serialize_for_json(obj.__dict__)
    else:
        return obj

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class QSPWebSocketHandler:
    """
    Quantum Shadow People WebSocket Handler with full database integration
    """
    
    def __init__(self, db_getter=None):
        self.db = QSPDatabaseIntegration(db_getter)
        self.qsp_brain = QuantumShadowPeopleBrainV2(db_getter)
        self.active_connections = {}
        self.quantum_fixes_in_progress = {}
        
    async def initialize(self):
        """Initialize database connections"""
        await self.db.initialize()
        await self.qsp_brain.initialize_database()
        
    async def process_metrics(self, metrics_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process metrics with full database integration"""
        
        # Store observation for pattern learning
        if user_id:
            await self.db.store_user_behavior_observation(user_id, metrics_data)
        
        # Check for pattern matches
        pattern_match = None
        if user_id:
            pattern_match = await self.db.check_pattern_match(user_id, metrics_data)
        
        # Get historical data for analysis
        historical_data = None
        if user_id:
            historical_data = await self.db.get_historical_network_data(user_id, days=7)
        
        # Analyze with QSP brain
        decision = await self.qsp_brain.analyze_network_metrics(
            network_data=metrics_data,
            historical_data=historical_data,
            user_id=user_id
        )
        
        # Store decision if made
        if decision and user_id:
            memory_id = await self.db.store_decision(user_id, decision)
            
            # Share insight with other agents if significant
            if decision.expected_improvement > 0.7:
                # app/ai_agents/qsp/websocket_handler.py (continued)

                await self.db.share_quantum_insight(
                    target_agent='vic_20',
                    insight={
                        'type': 'network_optimization',
                        'metric': decision.decision_type.value,
                        'improvement': decision.expected_improvement,
                        'quantum_state': decision.quantum_state.value,
                        'confidence': decision.confidence_level
                    },
                    source_memory_id=memory_id
                )
        
        # Check for pattern learning opportunity
        if user_id:
            # Every 50 observations, try to learn patterns
            observation_count = await self._get_observation_count(user_id)
            if observation_count % 50 == 0:
                learned_pattern = await self.db.analyze_and_learn_patterns(user_id)
                if learned_pattern:
                    # Pattern learned - already stored in database
                    pass
        
        # Format response
        return self._format_response(decision, pattern_match, metrics_data)
    
    async def _get_observation_count(self, user_id: str) -> int:
        """Get count of observations for pattern learning trigger"""
        # In production, this would query CMB
        # For now, return a reasonable number
        return 50
    
    def _format_response(self, decision: Optional[QSPDecision], pattern_match: Optional[Dict], 
                        metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response with quantum insights"""
        response = {
            'agent': AGENT_NAME,
            'timestamp': utc_now().isoformat(),
            'quantum_state': self.qsp_brain.quantum_state.value,
            'network_status': self._determine_network_status(metrics_data)
        }
        
        if decision:
            response['decision'] = {
                'type': decision.decision_type.value,
                'target': decision.network_target,
                'expected_improvement': decision.expected_improvement,
                'mysterious_explanation': decision.mysterious_explanation,
                'tequila_shots_required': decision.tequila_jello_shots_required,
                'comprehensibility': decision.comprehensibility_score
            }
            response['status'] = 'quantum_intervention_applied'
        else:
            response['status'] = 'monitoring_from_shadows'
            response['message'] = 'Network operating within quantum parameters'
        
        if pattern_match and pattern_match['matched']:
            response['pattern_detected'] = {
                'type': pattern_match['pattern_type'],
                'confidence': pattern_match['confidence'],
                'recommendation': pattern_match['recommended_action']
            }
        
        return response
    
    def _determine_network_status(self, metrics: Dict[str, Any]) -> str:
        """Determine overall network status"""
        latency = metrics.get('latency', 0)
        packet_loss = metrics.get('packet_loss', 0)
        bandwidth = metrics.get('bandwidth_utilization', 0)
        
        if latency > 200 or packet_loss > 0.1 or bandwidth > 0.95:
            return 'critical'
        elif latency > 100 or packet_loss > 0.05 or bandwidth > 0.85:
            return 'degraded'
        elif latency > 50 or packet_loss > 0.01 or bandwidth > 0.7:
            return 'moderate'
        else:
            return 'optimal'