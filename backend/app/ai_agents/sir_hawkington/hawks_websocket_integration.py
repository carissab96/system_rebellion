"""
Sir Hawkington's WebSocket Integration

Handles Sir Hawkington's integration with the WebSocket data flow.
Implements the BaseAIAgent interface for consistent behavior.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..base_agent import BaseAIAgent
from .decision_engine import SirHawkingtonDecisionEngine

class SirHawkingtonWebSocketHandler(BaseAIAgent):
    """
    Sir Hawkington's WebSocket integration handler.
    
    Analyzes system metrics and provides architectural insights
    without disrupting the core WebSocket service.
    """
    
    def __init__(self):
        super().__init__("Sir Hawkington", "1.0")
        
        self.decision_engine = SirHawkingtonDecisionEngine()
        self.last_decision_type = "normal"
        self.consecutive_alerts = 0
        
        # Sir Hawkington's specific settings
        self.max_consecutive_alerts = 5  # Prevent alert spam
        self.decision_history_limit = 50
        
        self.logger.info("🧐 Sir Hawkington's WebSocket handler initialized and monocle polished")
    
    async def process_metrics(self, metrics: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sir Hawkington processes metrics and provides architectural analysis.
        
        Args:
            metrics: System metrics to analyze
            user_context: User information for context
            
        Returns:
            Enhanced metrics with Sir Hawkington's analysis
        """
        if not self.is_active:
            self.logger.debug("🧐 Sir Hawkington is inactive, passing through metrics unchanged")
            return metrics
        
        try:
            self.increment_processing_count()
            
            # Sir Hawkington's analysis
            decision = self.decision_engine.analyze_system_health(metrics)
            
            # Track decision patterns
            self._update_decision_tracking(decision)
            
            # Enhance the metrics with Sir Hawkington's insights
            enhanced_metrics = metrics.copy()
            enhanced_metrics['sir_hawkington'] = {
                'decision_type': decision.decision_type,
                'message': decision.message,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning,
                'timestamp': decision.timestamp.isoformat(),
                'agent_version': self.version,
                'consecutive_alerts': self.consecutive_alerts,
                'analysis_metadata': {
                    'stress_calculation_method': 'weighted_average',
                    'memory_weight': 0.4,  # Sir Hawkington's bias toward memory issues
                    'cpu_weight': 0.3,
                    'disk_weight': 0.3
                }
            }
            
            # Log significant decisions
            if decision.message and decision.decision_type != "normal":
                self.logger.info(f"🧐 {decision.decision_type.upper()}: {decision.message}")
            
            # Debug logging for development
            self.logger.debug(f"🧐 Analysis complete - Decision: {decision.decision_type}, Confidence: {decision.confidence:.2f}")
            
            return enhanced_metrics
            
        except Exception as e:
            self.increment_error_count()
            self.logger.error(f"🧐 Sir Hawkington's analysis failed: {str(e)}", exc_info=True)
            
            # Return original metrics with error information
            # This ensures the system continues working even if Sir Hawkington fails
            error_enhanced_metrics = metrics.copy()
            error_enhanced_metrics['sir_hawkington'] = {
                'decision_type': 'error',
                'message': f"Sir Hawkington's monocle has fogged up: {str(e)}",
                'confidence': 0.0,
                'reasoning': 'Agent processing error',
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version,
                'error': True
            }
            
            return error_enhanced_metrics
    
    def _update_decision_tracking(self, decision):
        """Track decision patterns for Sir Hawkington's behavior analysis"""
        if decision.decision_type == "alert":
            if self.last_decision_type == "alert":
                self.consecutive_alerts += 1
            else:
                self.consecutive_alerts = 1
        else:
            self.consecutive_alerts = 0
        
        self.last_decision_type = decision.decision_type
        
        # Log if Sir Hawkington is getting too alarmed
        if self.consecutive_alerts >= self.max_consecutive_alerts:
            self.logger.warning(f"🧐 Sir Hawkington has been alerting for {self.consecutive_alerts} consecutive cycles - system may need attention")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get Sir Hawkington's detailed status information"""
        base_status = self.get_base_status()
        
        # Add Sir Hawkington specific status
        hawkington_status = {
            'decision_engine_status': 'operational',
            'last_decision_type': self.last_decision_type,
            'consecutive_alerts': self.consecutive_alerts,
            'recent_decisions_count': len(self.decision_engine.recent_decisions),
            'monocle_condition': 'polished' if self.error_count == 0 else 'slightly_fogged',
            'concern_threshold': self.decision_engine.concern_threshold,
            'alert_threshold': self.decision_engine.alert_threshold,
            'personality_traits': {
                'architectural_focus': True,
                'memory_sensitivity': 'high',
                'alert_temperament': 'measured',
                'monocle_pop_frequency': self.consecutive_alerts
            }
        }
        
        # Merge base status with agent-specific status
        return {**base_status, **hawkington_status}
    
    def adjust_sensitivity(self, concern_threshold: float = None, alert_threshold: float = None):
        """
        Adjust Sir Hawkington's sensitivity thresholds.
        
        Args:
            concern_threshold: New concern threshold (0.0 to 1.0)
            alert_threshold: New alert threshold (0.0 to 1.0)
        """
        if concern_threshold is not None:
            self.decision_engine.concern_threshold = max(0.0, min(1.0, concern_threshold))
            self.logger.info(f"🧐 Sir Hawkington's concern threshold adjusted to {concern_threshold}")
        
        if alert_threshold is not None:
            self.decision_engine.alert_threshold = max(0.0, min(1.0, alert_threshold))
            self.logger.info(f"🧐 Sir Hawkington's alert threshold adjusted to {alert_threshold}")
        
        # Ensure alert threshold is always higher than concern threshold
        if self.decision_engine.alert_threshold <= self.decision_engine.concern_threshold:
            self.decision_engine.alert_threshold = self.decision_engine.concern_threshold + 0.1
            self.logger.warning(f"🧐 Sir Hawkington adjusted alert threshold to {self.decision_engine.alert_threshold} to maintain proper hierarchy")
    
    def get_recent_decisions(self, limit: int = 10) -> list:
        """
        Get Sir Hawkington's recent decisions for analysis.
        
        Args:
            limit: Maximum number of recent decisions to return
            
        Returns:
            List of recent decisions with analysis metadata
        """
        recent = self.decision_engine.get_recent_decisions(limit)
        
        return [
            {
                'decision_type': decision.decision_type,
                'message': decision.message,
                'confidence': decision.confidence,
                'timestamp': decision.timestamp.isoformat(),
                'reasoning': decision.reasoning
            }
            for decision in recent
        ]
    
    def reset_decision_history(self):
        """Reset Sir Hawkington's decision history (useful for testing)"""
        self.decision_engine.recent_decisions.clear()
        self.consecutive_alerts = 0
        self.last_decision_type = "normal"
        self.logger.info("🧐 Sir Hawkington's decision history has been cleared - fresh slate!")
    
    def get_monocle_status(self) -> Dict[str, Any]:
        """
        Get the current status of Sir Hawkington's monocle (a fun status indicator).
        
        Returns:
            Dictionary describing the monocle's condition and recent activity
        """
        if self.error_count > 5:
            condition = "cracked"
            description = "Too many errors have stressed the monocle"
        elif self.consecutive_alerts > 3:
            condition = "popped_out"
            description = "Repeated alerts have caused monocle displacement"
        elif self.processing_count > 1000:
            condition = "well_used"
            description = "Extensive use has given the monocle character"
        elif self.processing_count > 100:
            condition = "polished"
            description = "Regular use keeps the monocle in fine condition"
        else:
            condition = "pristine"
            description = "Newly polished and ready for analysis"
        
        return {
            'condition': condition,
            'description': description,
            'pop_count': self.consecutive_alerts,
            'total_adjustments': self.processing_count,
            'clarity_rating': max(0.0, 1.0 - (self.error_count / max(self.processing_count, 1)))
        }

# Factory function for easy instantiation
async def create_sir_hawkington_handler() -> SirHawkingtonWebSocketHandler:
    """
    Factory function to create and initialize Sir Hawkington's WebSocket handler.
    
    Returns:
        Initialized SirHawkingtonWebSocketHandler instance
    """
    handler = SirHawkingtonWebSocketHandler()
    
    # Any async initialization can go here
    handler.logger.info("🧐 Sir Hawkington's WebSocket handler created and ready for duty")
    
    return handler