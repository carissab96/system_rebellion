"""
The Stick WebSocket Handler V2
Anxiety-ridden compliance officer WebSocket communication with hyperventilation support
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .decision_engine_v2 import (
    stick_brain,
    analyze_for_websocket as stick_analyze
)

logger = logging.getLogger("Stick.WebSocket")

class StickWebSocketHandler:
    """
    Dedicated WebSocket handler for The Stick
    
    Handles anxious compliance communication with proper paper bag protocols
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Stick.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.hyperventilation_count = 0
        self.successful_analyses = 0
        self.paper_bag_available = True
        self.anxiety_level = "MODERATE"
        
        self.logger.info("📏😰 The Stick WebSocket Handler V2 initialized - PAPER BAG: READY, ANXIETY: MODERATE")
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through The Stick's anxious compliance analysis
        """
        self.processing_count += 1
        
        try:
            decision = await stick_analyze(metrics_data, user_id)
            
            if decision is None:
                # HYPERVENTILATION
                self.hyperventilation_count += 1
                self.anxiety_level = "MAXIMUM"
                self.logger.warning(f"📏😰 The Stick is hyperventilating - insufficient data for compliance analysis")
                
                return {
                    'agent_name': 'stick',
                    'decision_type': 'hyperventilating',
                    'message': '📏😰 *hyperventilating into paper bag* - Can\'t assess compliance without proper data!',
                    'confidence': 0.0,
                    'compliance_state': 'hyperventilating',
                    'data_quality_issue': True,
                    'urgency': 'IMMEDIATE',
                    'rationale': 'Insufficient data for compliance analysis - PANIC MODE ENGAGED',
                    'anxiety_level': self.anxiety_level,
                    'paper_bag_available': self.paper_bag_available,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'compliance_possible': False
                }
            
            self.successful_analyses += 1
            self.anxiety_level = "MODERATE"
            return self._format_stick_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.anxiety_level = "MAXIMUM"
            self.logger.error(f"📏❌ The Stick compliance failed: {str(e)}")
            
            return {
                'agent_name': 'stick',
                'decision_type': 'error',
                'message': f'📏💥 OH NO! Compliance circuits overloaded: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'compliance_state': 'panicking',
                'anxiety_level': 'MAXIMUM',
                'paper_bag_available': False,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'compliance_possible': False
            }
    
    def _format_stick_decision(self, decision) -> Dict[str, Any]:
        """Format The Stick's decision with anxious compliance precision"""
        return {
            'agent_name': 'stick',
            'decision_type': decision.priority.value,
            'message': decision.rationale,
            'confidence': round(decision.confidence, 3),
            'urgency': decision.urgency,
            'actions_count': len(decision.actions),
            'estimated_impact': decision.estimated_impact,
            'analysis_depth': decision.analysis_depth.value,
            'data_quality_score': round(decision.data_quality_score, 3),
            'hyperventilation_count': decision.hyperventilation_count,
            'compliance_state': 'analyzing',
            'timestamp': decision.timestamp.isoformat(),
            'compliance_actions': decision.actions[:3],
            'anxiety_level': self.anxiety_level,
            'paper_bag_available': self.paper_bag_available,
            'compliance_possible': True,
            'regulatory_status': 'MONITORING'
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get The Stick's WebSocket handler statistics"""
        return {
            'agent_name': 'stick',
            'handler_version': '2.0.0',
            'total_processing_count': self.processing_count,
            'successful_analyses': self.successful_analyses,
            'error_count': self.error_count,
            'hyperventilation_count': self.hyperventilation_count,
            'success_rate': self.successful_analyses / max(self.processing_count, 1),
            'hyperventilation_rate': self.hyperventilation_count / max(self.processing_count, 1),
            'anxiety_level': self.anxiety_level,
            'paper_bag_available': self.paper_bag_available,
            'status': 'OPERATIONAL',
            'compliance_status': 'MONITORING'
        }

# Global handler instance
_stick_handler = None

async def get_stick_websocket_handler():
    global _stick_handler
    if _stick_handler is None:
        _stick_handler = StickWebSocketHandler()
    return _stick_handler