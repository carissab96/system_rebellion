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

from ..distributed.base_decision_engine import AgentDecisionEngine
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.system_actions import SystemActions
from ..distributed.coordination import (
    get_coordination_manager,
    CoordinationPriority,
    ResourceType as CoordResourceType,
    AgentCapability
)
from ..distributed.alert_escalation import (
    get_escalation_manager,
    AlertLevel,
    ResourceType as EscalationResourceType
)
from .decision_engine import SirHawkingtonBrainV2, DecisionType, MonocleState, AnalysisDepth


logger = logging.getLogger("SirHawkington.Distributed")


class SirHawkingtonDistributed(AgentDecisionEngine, SirHawkingtonBrainV2):
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
            "preferred_monocle_state": "polished",
            "trust_level": 0.6  # MEDIUM - Aristocratic wisdom
        }
        
        # Resource monitoring configuration
        # Sir Hawkington monitors CPU usage (befitting his role as triage commander)
        self.resource_thresholds = {
            ResourceType.CPU: 70.0,  # Alert at 70% CPU
        }
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init
        
        # Escalation tracking (aristocratic alert management)
        self.total_alerts_sent = 0
        self.escalated_alerts = 0
        self.emergency_alerts = 0
        self.cooldown_prevented_alerts = 0
        
        # Monocle-yeeting escalation levels
        self.monocle_yeets_by_severity = {
            "mild": 0,
            "moderate": 0,
            "severe": 0,
            "catastrophic": 0
        }
        
        logger.info("🧐 Sir Hawkington's distributed consciousness initialized")
        logger.info("🧐📢 Alert escalation protocols active - Distinguished triage!")
    
    async def initialize_distributed(self, redis_client):
        """
        Initialize distributed features and inject comm_hub into triage engine.
        
        This extends the base initialization to also enable triage broadcasting.
        """
        # Call parent initialization (subscribes to standard channels)
        await super().initialize_distributed(redis_client)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.escalation_manager = get_escalation_manager()
        
        # Register Sir Hawkington's coordination capability
        self.coordination_manager.register_agent_capability(
            "sir_hawkington",
            self._coordination_capability
        )
        
        logger.info("🧐🎯 Week 4 systems integrated - Coordination & Escalation ONLINE!")
        logger.info("🧐📢 Alert escalation with cooldowns - Preventing alert fatigue!")
        
        # Inject comm_hub into the global triage engine
        try:
            from .triage_engine import get_triage_engine
            triage_engine = await get_triage_engine()
            if hasattr(self, '_comm_hub') and self._comm_hub is not None:
                triage_engine.set_comm_hub(self._comm_hub)
                logger.info("🧐📡 Triage engine connected to distributed consciousness")
        except Exception as e:
            logger.error(f"🧐💥 Failed to inject comm_hub into triage engine: {e}")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests from VIC-20 with aristocratic grace.
        
        PERSONALITY: Aristocratic CPU throttling with monocle adjustment
        STRUCTURE: Standard AgentMessage parameter (required by base class)
        
        Args:
            message: AgentMessage with coordination request from VIC-20
        """
        message_data = message.payload
        coordination_type = message_data.get('coordination_type', 'unknown')
        
        if coordination_type == 'resource_recommendation':
            recommendation = message_data.get('recommendation', {})
            
            logger.info(
                f"🧐 *adjusts monocle* VIC-20's recommendation has merit... "
                f"Suggested action: {recommendation.get('suggested_action', 'unknown')}"
            )
            
            # Execute aristocratic CPU throttling
            logger.info("🧐⚙️ Initiating aristocratic system throttling with distinguished grace...")
            throttle_result = await SystemActions.throttle_cpu_intensive_tasks()
            
            if throttle_result['success']:
                logger.info(
                    f"🧐✅ System throttled with DISTINCTION! CPU: {throttle_result['cpu_before']:.1f}% → "
                    f"{throttle_result['cpu_after']:.1f}%. Improvement: {throttle_result['improvement']:.1f}%"
                )
                
                # Record with aristocratic flair (PERSONALITY!)
                await self.make_decision_and_broadcast(
                    decision_type="cpu_throttle_completed",
                    input_data={
                        "trigger": "coordination_request",
                        "recommendation": recommendation.get('suggested_action'),
                        "cpu_before": throttle_result['cpu_before']
                    },
                    output_data={
                        "cpu_after": throttle_result['cpu_after'],
                        "improvement": throttle_result['improvement'],
                        "improvement_percent": throttle_result['improvement_percent'],
                        "monocle_state": self.current_monocle_state.value,  # PERSONALITY!
                        "aristocratic_approval": "granted"  # PERSONALITY!
                    },
                    confidence=1.0,
                    reasoning="Coordination request addressed with aristocratic efficiency",
                    broadcast=True,
                    priority=Priority.HIGH
                )
            else:
                logger.error(f"🧐❌ CPU throttling failed: {throttle_result.get('error', 'Unknown error')}")
    
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
        
        # If critical or emergency, take action
        if severity in ["critical", "emergency"]:
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
            
            # REAL CPU throttling (Task 4.1 Enhanced)
            logger.info("🧐⚙️ Initiating aristocratic system throttling with distinguished grace...")
            
            throttle_result = await SystemActions.throttle_cpu_intensive_tasks()
            
            if throttle_result['success']:
                logger.info(
                    f"🧐✅ System throttled with DISTINCTION! CPU: {throttle_result['cpu_before']:.1f}% → "
                    f"{throttle_result['cpu_after']:.1f}%. Improvement: {throttle_result['improvement']:.1f}%"
                )
                logger.info(f"🧐⚙️ Actions taken: {', '.join(throttle_result['actions_taken'])}")
                
                # Record successful throttling
                if self.is_distributed:
                    await self.make_distributed_decision(
                        decision_type="cpu_throttle_completed",
                        input_data={
                            "cpu_before": throttle_result['cpu_before'],
                            "trigger": "critical_cpu"
                        },
                        output_data={
                            "cpu_after": throttle_result['cpu_after'],
                            "improvement": throttle_result['improvement'],
                            "improvement_percent": throttle_result['improvement_percent'],
                            "monocle_state": "polished",
                            "aristocratic_approval": "granted"
                        },
                        confidence=1.0,
                        reasoning="Critical CPU usage addressed with aristocratic efficiency"
                    )
            else:
                logger.error(f"🧐❌ CPU throttling failed: {throttle_result.get('error', 'Unknown error')}")
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        Sir Hawkington's coordination capability for Week 4 system.
        
        As the triage commander, Sir Hawkington can handle CPU resources
        with aristocratic precision.
        """
        # Only handle CPU resources (Sir Hawkington's specialty!)
        if resource_type != CoordResourceType.CPU:
            return None
        
        # Base improvement estimate (aristocratic precision)
        base_improvement = 10.0  # Conservative but reliable
        
        # Adjust based on monocle state
        monocle_multiplier = {
            MonocleState.POLISHED: 1.0,  # Peak performance
            MonocleState.ADJUSTED: 0.9,  # Slightly distracted
            MonocleState.FOGGED: 0.7,  # Vision impaired
            MonocleState.YEETED: 0.5,  # Compromised
            MonocleState.CLEANING: 0.8  # Temporarily unavailable
        }
        
        multiplier = monocle_multiplier.get(self.current_monocle_state, 0.8)
        estimated_improvement = base_improvement * multiplier
        
        # Confidence based on monocle state and recent performance
        base_confidence = 0.75  # Aristocratic confidence
        confidence = base_confidence * multiplier
        
        if self.current_monocle_state == MonocleState.YEETED:
            logger.warning(
                f"🧐💥 Monocle YEETED! Capability compromised! "
                f"(Confidence: {confidence:.0%})"
            )
        else:
            logger.info(
                f"🧐🎯 Aristocratic capability: {estimated_improvement:.1f}% improvement "
                f"(Monocle: {self.current_monocle_state.value}, Confidence: {confidence:.0%})"
            )
        
        return AgentCapability(
            agent_name="sir_hawkington",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=2.0,  # Aristocratic thoroughness
            action_name="aristocratic_cpu_throttle"
        )
    
    async def _check_alert_escalation(
        self,
        resource_type: str,
        current_value: float,
        severity: str
    ) -> bool:
        """
        Check if alert should be sent using Week 4 escalation system.
        
        Returns True if alert should be sent, False if in cooldown.
        """
        # Map severity to AlertLevel
        severity_map = {
            "low": AlertLevel.INFO,
            "normal": AlertLevel.WARNING,
            "high": AlertLevel.CRITICAL,
            "critical": AlertLevel.CRITICAL,
            "emergency": AlertLevel.EMERGENCY
        }
        
        alert_level = severity_map.get(severity, AlertLevel.WARNING)
        
        # Map resource type to EscalationResourceType
        resource_map = {
            "cpu": EscalationResourceType.CPU,
            "memory": EscalationResourceType.MEMORY,
            "disk": EscalationResourceType.DISK,
            "network": EscalationResourceType.NETWORK
        }
        
        escalation_resource = resource_map.get(resource_type, EscalationResourceType.CPU)
        
        # Check if we should alert
        should_alert = self.escalation_manager.should_alert(
            resource_type=escalation_resource,
            current_value=current_value,
            threshold=self.resource_thresholds.get(ResourceType.CPU, 70.0),
            new_level=alert_level
        )
        
        if should_alert:
            self.total_alerts_sent += 1
            
            if alert_level == AlertLevel.EMERGENCY:
                self.emergency_alerts += 1
                logger.warning(
                    f"🧐🚨 EMERGENCY ALERT! Bypassing cooldown! "
                    f"(Total emergency: {self.emergency_alerts})"
                )
            elif alert_level == AlertLevel.CRITICAL:
                self.escalated_alerts += 1
                logger.info(
                    f"🧐📢 Alert escalated to CRITICAL "
                    f"(Total escalated: {self.escalated_alerts})"
                )
            
            logger.info(
                f"🧐✅ Alert approved by escalation manager "
                f"(Total alerts: {self.total_alerts_sent})"
            )
        else:
            self.cooldown_prevented_alerts += 1
            logger.info(
                f"🧐⏳ Alert in cooldown - Preventing spam "
                f"(Prevented: {self.cooldown_prevented_alerts})"
            )
        
        return should_alert
    
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
            f"alerts={self.total_alerts_sent}(prevented={self.cooldown_prevented_alerts}) "
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
