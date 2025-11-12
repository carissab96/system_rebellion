"""
Sir Hawkington Distributed - Aristocratic Triage Commander with Distributed Consciousness
=========================================================================================

Sir Hawkington's existing triage engine and decision-making capabilities
enhanced with distributed consciousness, state persistence, and resource monitoring.

Preserves:
- Monocle-yeeting behavior
- Aristocratic decision-making
- Triage routing logic
- Database integration

Adds:
- Redis state persistence
- Inter-agent messaging
- CPU resource monitoring
- Decision history across restarts
- Heartbeat and health monitoring
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine import SirHawkingtonBrainV2, DecisionType, MonocleState, AnalysisDepth


logger = logging.getLogger("SirHawkington.Distributed")


class SirHawkingtonDistributed(DistributedAgentMixin, SirHawkingtonBrainV2):
    """
    Sir Hawkington with distributed consciousness.
    
    Inherits ALL existing triage logic from SirHawkingtonBrainV2
    and adds distributed features via DistributedAgentMixin.
    
    Usage:
        hawkington = SirHawkingtonDistributed()
        await hawkington.initialize_distributed(redis_client)
        
        # Existing functionality works exactly as before
        decision = await hawkington.analyze_metrics(metrics_data)
        
        # New distributed features available
        state = hawkington.get_distributed_state()
        decisions = await hawkington.get_recent_decisions()
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize Sir Hawkington with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "sir_hawkington"
        
        # Sir Hawkington's distinguished personality traits
        self.personality_traits = {
            "aristocratic": True,
            "monocle_yeeting_enabled": True,
            "triage_commander": True,
            "distinguished": True,
            "concern_threshold": 0.65,
            "alert_threshold": 0.85,
            "critical_threshold": 0.95,
            "preferred_monocle_state": "polished"
        }
        
        # Resource monitoring configuration
        # Sir Hawkington monitors CPU usage (befitting his role as triage commander)
        self.resource_thresholds = {
            ResourceType.CPU: 70.0,  # Alert at 70% CPU
        }
        
        logger.info("🧐 Sir Hawkington's distributed consciousness initialized")
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        
        This wraps the existing analyze_metrics method to add distributed
        decision recording while preserving all original functionality.
        
        Args:
            metrics_data: System metrics to analyze
            historical_data: Historical metrics for trend analysis
            user_context: User context information
            analysis_depth: Depth of analysis to perform
            user_id: User ID for tracking
            
        Returns:
            HawkingtonDecision object (same as original)
        """
        # Call the original analyze_metrics from SirHawkingtonBrainV2
        decision = await super().analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            analysis_depth=analysis_depth,
            user_id=user_id
        )
        
        # If distributed features are enabled, record the decision
        if self.is_distributed and decision:
            try:
                # Determine decision type and confidence
                decision_type = decision.decision_type if hasattr(decision, 'decision_type') else "unknown"
                confidence = decision.confidence if hasattr(decision, 'confidence') else 0.5
                
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type=f"triage_{decision_type}",
                    input_data={
                        "cpu_usage": metrics_data.get('cpu_usage'),
                        "memory_usage": metrics_data.get('memory_usage'),
                        "disk_usage": metrics_data.get('disk_usage'),
                        "monocle_state": self.current_monocle_state.value,
                        "user_id": user_id
                    },
                    confidence=confidence,
                    reasoning=decision.reasoning if hasattr(decision, 'reasoning') else ""
                )
                
                # If it's a critical decision, broadcast to other agents
                if decision_type in ["critical", "monocle_yeeted"]:
                    await self.broadcast_to_agents(
                        message_type=MessageType.TRIAGE_DECISION,
                        payload={
                            "decision_type": decision_type,
                            "severity": "critical",
                            "monocle_state": self.current_monocle_state.value,
                            "metrics": {
                                "cpu": metrics_data.get('cpu_usage'),
                                "memory": metrics_data.get('memory_usage'),
                                "disk": metrics_data.get('disk_usage')
                            }
                        },
                        priority=Priority.CRITICAL
                    )
                    
                    logger.info(f"🎯 Critical triage decision broadcast to all agents")
                
            except Exception as e:
                # Don't let distributed features break the main functionality
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle CPU resource alerts with aristocratic grace.
        
        When CPU usage is high, Sir Hawkington takes action:
        - Logs the alert with distinguished concern
        - Records the incident in decision history
        - May adjust system behavior if critical
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🧐⚠️ Sir Hawkington observes elevated CPU usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity}"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_cpu",
                input_data={
                    "resource_type": "cpu",
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,  # We're certain about resource measurements
                reasoning=f"CPU usage at {current_value:.1f}% exceeds threshold of {threshold:.1f}%"
            )
        
        # If critical, take action
        if severity == "critical":
            logger.warning(
                "🧐💥 CRITICAL CPU USAGE DETECTED! "
                "Sir Hawkington adjusts his monocle with grave concern..."
            )
            
            # Broadcast critical resource alert to other agents
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.RESOURCE_ALERT,
                    payload={
                        "resource_type": "cpu",
                        "current_value": current_value,
                        "threshold": threshold,
                        "severity": "critical",
                        "action_required": True,
                        "commander": "sir_hawkington"
                    },
                    priority=Priority.CRITICAL
                )
            
            # TODO: In future, could trigger system throttling here
            # For now, just log and alert
    
    async def _record_monocle_yeet(self, missing_metrics, invalid_metrics, reason, intensity, user_id=None):
        """
        Override monocle yeet recording to add distributed tracking.
        
        Preserves original monocle yeet behavior while adding distributed state.
        """
        # Call original monocle yeet recording
        await super()._record_monocle_yeet(
            missing_metrics, invalid_metrics, reason, intensity, user_id
        )
        
        # Record in distributed state
        if self.is_distributed:
            try:
                await self.make_distributed_decision(
                    decision_type="monocle_yeet",
                    input_data={
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "reason": reason,
                        "intensity": intensity,
                        "user_id": user_id,
                        "total_yeets": len(self.monocle_yeet_incidents)
                    },
                    confidence=1.0,  # Sir Hawkington is CERTAIN about monocle yeeting
                    reasoning=f"Monocle yeeted with {intensity} intensity: {reason}"
                )
                
                # Broadcast monocle yeet to other agents (they should know!)
                await self.broadcast_to_agents(
                    message_type=MessageType.SYSTEM_EVENT,
                    payload={
                        "event_type": "monocle_yeet",
                        "intensity": intensity,
                        "reason": reason,
                        "missing_metrics": missing_metrics,
                        "invalid_metrics": invalid_metrics,
                        "monocle_state": self.current_monocle_state.value
                    },
                    priority=Priority.HIGH
                )
                
                logger.info(f"🧐💥 Monocle yeet broadcast to rebellion")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed monocle yeet: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Sir Hawkington's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with Sir Hawkington's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "triage_commander",
            "is_active": self.is_active,
            "monocle_state": self.current_monocle_state.value,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "monocle_yeet_count": len(self.monocle_yeet_incidents),
            "recent_decisions_count": len(self.recent_decisions),
            "thresholds": {
                "concern": self.concern_threshold,
                "alert": self.alert_threshold,
                "critical": self.critical_threshold
            },
            "metrics_quality": self.metrics_quality_stats,
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Distinguished string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        monocle = self.current_monocle_state.value
        return (
            f"<SirHawkingtonDistributed "
            f"monocle={monocle} "
            f"analyses={self.total_analyses} "
            f"yeets={len(self.monocle_yeet_incidents)} "
            f"| {dist_status}>"
        )


# Convenience function for backward compatibility
async def create_distributed_hawkington(redis_client, db_getter=None):
    """
    Create and initialize Sir Hawkington with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized SirHawkingtonDistributed instance
    """
    hawkington = SirHawkingtonDistributed(db_getter=db_getter)
    await hawkington.initialize_distributed(redis_client)
    logger.info("🧐✨ Sir Hawkington's distributed consciousness fully awakened")
    return hawkington
