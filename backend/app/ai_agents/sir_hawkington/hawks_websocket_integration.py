"""
Sir Hawkington WebSocket Handler V2
Aristocratic WebSocket communication with proper monocle-yeeting support
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .decision_engine import (
    sir_hawkington_brain,
    analyze_for_websocket as hawkington_analyze
)

logger = logging.getLogger("SirHawkington.WebSocket")

class SirHawkingtonWebSocketHandler:
    """
    Dedicated WebSocket handler for Sir Hawkington
    
    Handles aristocratic communication with proper monocle etiquette
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SirHawkington.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.monocle_yeet_count = 0
        self.successful_analyses = 0
        
        self.logger.info("🧐 Sir Hawkington WebSocket Handler V2 initialized with aristocratic precision")
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through Sir Hawkington's aristocratic analysis
        
        Args:
            metrics_data: Raw system metrics
            user_id: User ID for tracking
            
        Returns:
            Sir Hawkington's analysis formatted for WebSocket
        """
        self.processing_count += 1
        
        try:
            decision = await hawkington_analyze(metrics_data, user_id)
            
            if decision is None:
                # MONOCLE YEETED
                self.monocle_yeet_count += 1
                self.logger.warning(f"🧐💥 Sir Hawkington has yeeted his monocle - insufficient data quality")
                
                return {
                    'agent_name': 'sir_hawkington',
                    'decision_type': 'monocle_yeeted',
                    'message': '🧐💥 I say! The data quality is most unsatisfactory. *yeets monocle*',
                    'confidence': 0.0,
                    'monocle_state': 'yeeted',
                    'data_quality_issue': True,
                    'stress_score': 0.0,
                    'urgency': 'IMMEDIATE',
                    'reasoning': 'Insufficient data quality for aristocratic analysis',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'aristocratic_seal': False
                }
            
            self.successful_analyses += 1
            return self._format_hawkington_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🧐❌ Sir Hawkington processing failed: {str(e)}")
            
            return {
                'agent_name': 'sir_hawkington',
                'decision_type': 'error',
                'message': f'🧐💥 Most regrettable! An error has occurred: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'monocle_state': 'cracked',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'aristocratic_seal': False
            }
    
    def _format_hawkington_decision(self, decision) -> Dict[str, Any]:
        """Format Sir Hawkington's decision with aristocratic precision"""
        return {
            'agent_name': 'sir_hawkington',
            'decision_type': decision.decision_type.value,
            'message': decision.message,
            'confidence': round(decision.confidence, 3),
            'stress_score': round(decision.stress_score, 3),
            'monocle_state': decision.monocle_state.value,
            'urgency': decision.urgency,
            'reasoning': decision.reasoning,
            'estimated_impact': decision.estimated_impact,
            'analysis_depth': decision.analysis_depth.value,
            'data_quality_score': round(decision.data_quality_score, 3),
            'monocle_yeet_count': decision.monocle_yeet_count,
            'timestamp': decision.timestamp.isoformat(),
            'aristocratic_seal': True,
            'recommendations': getattr(decision, 'recommendations', [])
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get Sir Hawkington's WebSocket handler statistics"""
        return {
            'agent_name': 'sir_hawkington',
            'handler_version': '2.0.0',
            'total_processing_count': self.processing_count,
            'successful_analyses': self.successful_analyses,
            'error_count': self.error_count,
            'monocle_yeet_count': self.monocle_yeet_count,
            'success_rate': self.successful_analyses / max(self.processing_count, 1),
            'monocle_yeet_rate': self.monocle_yeet_count / max(self.processing_count, 1),
            'current_monocle_state': sir_hawkington_brain.current_monocle_state.value,
            'status': 'OPERATIONAL',
            'aristocratic_status': 'DISTINGUISHED'
        }

# Global handler instance
_hawkington_handler = None

async def get_hawkington_websocket_handler():
    global _hawkington_handler
    if _hawkington_handler is None:
        _hawkington_handler = SirHawkingtonWebSocketHandler()
    return _hawkington_handler