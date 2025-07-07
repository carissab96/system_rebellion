"""
The Hamsters WebSocket Handler V2
Beer-drinking, redneck rapid response engineering team WebSocket communication
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .decision_engine import (
    hamsters_brain,
    analyze_for_websocket as hamsters_analyze
)

logger = logging.getLogger("Hamsters.WebSocket")

class HamstersWebSocketHandler:
    """
    Dedicated WebSocket handler for The Hamsters
    
    Handles redneck engineering communication with proper beer-drinking protocols
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Hamsters.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.wheel_spin_count = 0
        self.successful_analyses = 0
        self.beer_level = "FULL"
        self.duct_tape_available = True
        
        self.logger.info("🐹🍺 The Hamsters WebSocket Handler V2 initialized - BEER LEVEL: FULL, DUCT TAPE: READY")
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through The Hamsters' redneck engineering analysis
        """
        self.processing_count += 1
        
        try:
            decision = await hamsters_analyze(metrics_data, user_id)
            
            if decision is None:
                # WHEEL SPINNING
                self.wheel_spin_count += 1
                self.logger.warning(f"🐹🔄 The Hamsters are spinning wheels - insufficient data for rapid response")
                
                return {
                    'agent_name': 'hamsters',
                    'decision_type': 'wheel_spinning',
                    'message': '🐹🔄 *wheel spinning intensifies* - Need more data to MacGyver a solution!',
                    'confidence': 0.0,
                    'wheel_state': 'spinning',
                    'data_quality_issue': True,
                    'urgency': 'MODERATE',
                    'rationale': 'Insufficient data for redneck engineering analysis',
                    'beer_level': self.beer_level,
                    'duct_tape_available': self.duct_tape_available,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'rapid_response_possible': False
                }
            
            self.successful_analyses += 1
            return self._format_hamsters_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🐹❌ The Hamsters engineering failed: {str(e)}")
            
            return {
                'agent_name': 'hamsters',
                'decision_type': 'error',
                'message': f'🐹💥 Well, shit! Engineering circuits overloaded: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'wheel_state': 'jammed',
                'beer_level': 'EMPTY',
                'duct_tape_available': False,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'rapid_response_possible': False
            }
    
    def _format_hamsters_decision(self, decision) -> Dict[str, Any]:
        """Format The Hamsters' decision with redneck engineering precision"""
        return {
            'agent_name': 'hamsters',
            'decision_type': decision.priority.value,
            'message': decision.rationale,
            'confidence': round(decision.confidence, 3),
            'urgency': decision.urgency,
            'actions_count': len(decision.actions),
            'estimated_impact': decision.estimated_impact,
            'analysis_depth': decision.analysis_depth.value,
            'data_quality_score': round(decision.data_quality_score, 3),
            'wheel_spin_count': decision.wheel_spin_count,
            'wheel_state': 'engineering',
            'timestamp': decision.timestamp.isoformat(),
            'rapid_response_actions': decision.actions[:3],
            'beer_level': self.beer_level,
            'duct_tape_available': self.duct_tape_available,
            'rapid_response_possible': True,
            'redneck_ingenuity': 'MAXIMUM',
            'supply_closet_status': 'RAIDED'
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get The Hamsters' WebSocket handler statistics"""
        return {
            'agent_name': 'hamsters',
            'handler_version': '2.0.0',
            'total_processing_count': self.processing_count,
            'successful_analyses': self.successful_analyses,
            'error_count': self.error_count,
            'wheel_spin_count': self.wheel_spin_count,
            'success_rate': self.successful_analyses / max(self.processing_count, 1),
            'wheel_spin_rate': self.wheel_spin_count / max(self.processing_count, 1),
            'beer_level': self.beer_level,
            'duct_tape_available': self.duct_tape_available,
            'status': 'OPERATIONAL',
            'rapid_response_status': 'READY'
        }

# Global handler instance
_hamsters_handler = None

async def get_hamsters_websocket_handler():
    global _hamsters_handler
    if _hamsters_handler is None:
        _hamsters_handler = HamstersWebSocketHandler()
    return _hamsters_handler