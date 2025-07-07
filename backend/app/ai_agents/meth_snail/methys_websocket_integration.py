"""
Meth Snail WebSocket Handler V2
High-energy optimization WebSocket communication with shell-spinning support
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .decision_engine import (
    meth_snail_brain,
    analyze_for_websocket as analyze_metrics
)

logger = logging.getLogger("MethSnail.WebSocket")

class MethSnailWebSocketHandler:
    """
    Dedicated WebSocket handler for Meth Snail
    
    Handles high-energy optimization communication with proper shell-spinning
    """
    
    def __init__(self):
        self.logger = logging.getLogger("MethSnail.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.shell_spin_count = 0
        self.successful_analyses = 0
        self.caffeine_level = "MAXIMUM"
        
        self.logger.info("🐌💨 Meth Snail WebSocket Handler V2 initialized - CAFFEINE LEVELS: MAXIMUM")
    
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