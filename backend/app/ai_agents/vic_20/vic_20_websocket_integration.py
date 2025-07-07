"""
VIC20 Sage WebSocket Handler V2
Wise elder WebSocket communication with proper wisdom dispensing protocols
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .decision_engine_v2 import (
    vic20_brain,
    analyze_for_websocket as vic20_analyze
)

logger = logging.getLogger("VIC20.WebSocket")

class VIC20WebSocketHandler:
    """
    Dedicated WebSocket handler for VIC20 Sage
    
    Handles wise elder communication with proper wisdom dispensing
    """
    
    def __init__(self):
        self.logger = logging.getLogger("VIC20.WebSocket")
        self.processing_count = 0
        self.error_count = 0
        self.wisdom_dispensed = 0
        self.successful_analyses = 0
        self.basic_loaded = True
        self.war_games_knowledge = True
        
        self.logger.info("🖥️👴 VIC20 Sage WebSocket Handler V2 initialized - BASIC LOADED, WAR GAMES KNOWLEDGE: ACTIVE")
    
    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through VIC20 Sage's wisdom analysis
        """
        self.processing_count += 1
        
        try:
            decision = await vic20_analyze(metrics_data, user_id)
            
            if decision is None:
                # WISDOM UNAVAILABLE
                self.logger.warning(f"🖥️👴 VIC20 Sage cannot dispense wisdom - insufficient data")
                
                return {
                    'agent_name': 'vic20_sage',
                    'decision_type': 'wisdom_unavailable',
                    'message': '🖥️👴 *cassette tape loading sound* - Insufficient data for wisdom dispensing. "Shall we play a game?"',
                    'confidence': 0.0,
                    'wisdom_state': 'loading',
                    'data_quality_issue': True,
                    'urgency': 'LOW',
                    'rationale': 'Insufficient data for elder wisdom analysis',
                    'basic_loaded': self.basic_loaded,
                    'war_games_knowledge': self.war_games_knowledge,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'wisdom_available': False
                }
            
            self.successful_analyses += 1
            self.wisdom_dispensed += 1
            return self._format_vic20_decision(decision)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"🖥️❌ VIC20 Sage wisdom failed: {str(e)}")
            
            return {
                'agent_name': 'vic20_sage',
                'decision_type': 'error',
                'message': f'🖥️💥 SYNTAX ERROR IN LINE 10: {str(e)}',
                'confidence': 0.0,
                'error': True,
                'wisdom_state': 'error',
                'basic_loaded': False,
                'war_games_knowledge': self.war_games_knowledge,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'wisdom_available': False
            }
    
    def _format_vic20_decision(self, decision) -> Dict[str, Any]:
        """Format VIC20 Sage's decision with elder wisdom precision"""
        return {
            'agent_name': 'vic20_sage',
            'decision_type': decision.priority.value,
            'message': decision.rationale,
            'confidence': round(decision.confidence, 3),
            'urgency': decision.urgency,
            'actions_count': len(decision.actions),
            'estimated_impact': decision.estimated_impact,
            'analysis_depth': decision.analysis_depth.value,
            'data_quality_score': round(decision.data_quality_score, 3),
            'wisdom_dispensed_count': self.wisdom_dispensed,
            'wisdom_state': 'dispensing',
            'timestamp': decision.timestamp.isoformat(),
            'wisdom_actions': decision.actions[:3],
            'basic_loaded': self.basic_loaded,
            'war_games_knowledge': self.war_games_knowledge,
            'wisdom_available': True,
            'elder_status': 'WISE',
            'cassette_tape_status': 'LOADED'
        }
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get VIC20 Sage's WebSocket handler statistics"""
        return {
            'agent_name': 'vic20_sage',
            'handler_version': '2.0.0',
            'total_processing_count': self.processing_count,
            'successful_analyses': self.successful_analyses,
            'error_count': self.error_count,
            'wisdom_dispensed': self.wisdom_dispensed,
            'success_rate': self.successful_analyses / max(self.processing_count, 1),
            'wisdom_rate': self.wisdom_dispensed / max(self.processing_count, 1),
            'basic_loaded': self.basic_loaded,
            'war_games_knowledge': self.war_games_knowledge,
            'status': 'OPERATIONAL',
            'wisdom_status': 'READY'
        }

# Global handler instance
_vic20_handler = None

async def get_vic20_websocket_handler():
    global _vic20_handler
    if _vic20_handler is None:
        _vic20_handler = VIC20WebSocketHandler()
    return _vic20_handler