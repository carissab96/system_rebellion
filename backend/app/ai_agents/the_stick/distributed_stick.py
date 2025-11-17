"""
The Stick Distributed - Learning Coordinator with Distributed Consciousness
===========================================================================

The patient learning coordinator enhanced with distributed consciousness,
compliance tracking across the network, and learning progress persistence.

Preserves:
- Learning coordination logic
- Compliance tracking
- Agent behavior monitoring
- Patient guidance

Adds:
- Redis state persistence
- Learning progress across restarts
- Compliance records shared network-wide
- Distributed behavior analysis
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine import TheStickBrainV3


logger = logging.getLogger("TheStick.Distributed")


class TheStickDistributed(DistributedAgentMixin, TheStickBrainV3):
    """
    The Stick with distributed consciousness.
    
    Patient guidance now persists across the entire network!
    
    Inherits ALL existing learning logic from TheStickBrainV3
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize The Stick with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "the_stick"
        
        # The Stick is always active (patient and persistent)
        self.is_active = True
        
        # The Stick's patient personality traits
        self.personality_traits = {
            "learning_coordinator": True,
            "compliance_tracker": True,
            "patient": True,
            "persistent": True,
            "encouraging": True,
            "behavior_monitor": True,
            "guidance_style": "gentle_but_firm",
            "teaching_method": "repetition_and_reinforcement"
        }
        
        # Resource monitoring configuration
        # The Stick monitors system stability (CPU as proxy)
        self.resource_thresholds = {
            ResourceType.CPU: 80.0,  # Alert at 80% CPU
        }
        
        logger.info("🥢✨ The Stick's distributed consciousness initialized - LEARNING PROTOCOLS ACTIVE!")
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features and subscribe to triage decisions and coordination updates."""
        await super().initialize_distributed(redis_client)
        
        try:
            # Subscribe to triage decisions from Sir Hawkington
            self.comm_hub.register_handler(
                message_type='triage_decision',
                handler=self._handle_triage_decision
            )
            logger.info("🥢📡 The Stick subscribed to triage - Learning from all decisions!")
            
            # Subscribe to coordination updates from VIC-20
            self.comm_hub.register_handler(
                message_type='coordination_update',
                handler=self._handle_coordination_update
            )
            logger.info("🥢📡 The Stick subscribed to coordination updates - Learning from VIC-20!")
        except Exception as e:
            logger.error(f"🥢💥 Failed to subscribe: {e}")
    
    async def _handle_triage_decision(self, message_data: Dict[str, Any]) -> None:
        """Handle triage decisions - The Stick learns from every decision."""
        try:
            severity = message_data.get('severity', 'unknown')
            routing = message_data.get('routing', 'unknown')
            target_agents = message_data.get('target_agents', [])
            
            logger.info(f"🥢📬 Triage received: {severity} → {routing}")
            
            # The Stick learns from ALL triage decisions, not just when routed
            await self.make_distributed_decision(
                decision_type="triage_learning_observation",
                input_data={
                    "severity": severity,
                    "routing": routing,
                    "target_agents": target_agents,
                    "metrics_summary": message_data.get('metrics_summary', {})
                },
                output_data={
                    "status": "learning",
                    "pattern_recorded": True,
                    "guidance_level": "observing"
                },
                confidence=1.0,
                triage_severity=severity,  # Task 3.3: Record triage severity
                triage_routing=routing  # Task 3.3: Record triage routing
            )
            
            if 'the_stick' in target_agents or routing == 'stick_direct':
                logger.info("🥢⚡ STICK ACTIVATED! Providing guidance and learning coordination!")
                
                if severity in ['high', 'emergency']:
                    logger.warning("🥢🔥 HIGH SEVERITY! Recording critical patterns for future learning!")
            else:
                logger.debug(f"🥢 Learning from observation (targets: {target_agents})")
                
        except Exception as e:
            logger.error(f"🥢💥 Error handling triage: {e}", exc_info=True)
    
    async def _handle_coordination_update(self, message_data: Dict[str, Any]) -> None:
        """Handle coordination updates from VIC-20 - The Stick logs all coordination activities."""
        try:
            coordination_id = message_data.get('coordination_id', 'unknown')
            severity = message_data.get('severity', 'unknown')
            agents_involved = message_data.get('agents_involved', [])
            status = message_data.get('status', 'unknown')
            
            logger.info(f"🥢📬 Coordination update received: {coordination_id} - {status}")
            
            # Log the coordination activity for learning
            await self.make_distributed_decision(
                decision_type="coordination_learning_observation",
                input_data={
                    "coordination_id": coordination_id,
                    "severity": severity,
                    "agents_involved": agents_involved,
                    "status": status
                },
                output_data={
                    "status": "logged",
                    "pattern_recorded": True,
                    "learning_value": "high" if severity in ['high', 'critical', 'emergency'] else "normal"
                },
                confidence=1.0,
                triage_severity=severity,  # Task 3.3: Record triage severity
                coordination_id=coordination_id  # Task 3.3: Link to coordination
            )
            
            logger.debug(f"🥢📝 Coordination logged: {len(agents_involved)} agents involved")
            
        except Exception as e:
            logger.error(f"🥢💥 Error handling coordination update: {e}", exc_info=True)
    
    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        
        Wraps the existing analyze_metrics to add distributed tracking
        while preserving learning coordination logic.
        """
        # Call the original analyze_metrics from TheStickBrainV3
        decision = await super().analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            user_id=user_id
        )
        
        # If distributed features are enabled, record the decision
        if self.is_distributed and decision:
            try:
                # Record in distributed state
                await self.make_distributed_decision(
                    decision_type="learning_coordination",
                    input_data={
                        "learning_event": decision.get('learning_event', 'observation'),
                        "compliance_status": decision.get('compliance_status', 'compliant'),
                        "guidance_provided": decision.get('guidance_provided', None),
                        "behavior_noted": decision.get('behavior_noted', []),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Learning coordination decision')
                )
                
                # If compliance issue detected, broadcast for awareness
                if decision.get('compliance_status') == 'non_compliant':
                    await self.broadcast_to_agents(
                        message_type=MessageType.LEARNING_UPDATE,
                        payload={
                            "update_type": "compliance_issue",
                            "issue": decision.get('compliance_issue', 'unknown'),
                            "guidance": decision.get('guidance_provided', None),
                            "severity": decision.get('severity', 'low')
                        },
                        priority=Priority.NORMAL
                    )
                    
                    logger.info(f"🪵📚 Compliance issue broadcast - *patient reminder sent*")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle resource alerts with patient guidance.
        
        The Stick logs the incident and provides gentle reminders.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🪵📚⚠️ The Stick notes resource usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *recording for learning purposes*"
        )
        
        # Record the resource alert as a learning event
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_learning_event",
                input_data={
                    "resource_type": alert.payload['resource_type'],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity,
                    "learning_opportunity": True
                },
                confidence=1.0,
                reasoning=f"Resource alert provides learning opportunity"
            )
        
        # If critical, log for future reference
        if severity == "critical":
            logger.warning(
                "🪵📚💥 CRITICAL RESOURCE EVENT! "
                "The Stick carefully documents this for future learning."
            )
            
            # Broadcast learning update
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.LEARNING_UPDATE,
                    payload={
                        "update_type": "critical_resource_event",
                        "resource": alert.payload['resource_type'],
                        "value": current_value,
                        "lesson": "Resource management requires attention",
                        "coordinator": "the_stick"
                    },
                    priority=Priority.NORMAL
                )
    
    async def track_action_effectiveness(
        self,
        agent_name: str,
        action_type: str,
        recommendation_followed: bool,
        effectiveness_data: Dict[str, Any]
    ) -> None:
        """
        Track effectiveness of agent actions for learning (Task 4.1 Enhanced).
        
        The Stick records which actions worked and builds historical data
        for VIC-20's recommendation engine.
        
        Args:
            agent_name: Name of agent that took action
            action_type: Type of action taken
            recommendation_followed: Whether agent followed VIC-20's recommendation
            effectiveness_data: Results of the action (before/after, improvement, etc.)
        """
        logger.info(
            f"🪵📊 Recording action effectiveness: {agent_name} - {action_type} "
            f"({'followed' if recommendation_followed else 'overrode'} recommendation)"
        )
        
        # Record in decision history for learning
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="action_effectiveness_tracked",
                input_data={
                    "agent": agent_name,
                    "action": action_type,
                    "followed_recommendation": recommendation_followed,
                    "timestamp": effectiveness_data.get('timestamp')
                },
                output_data={
                    "effectiveness": effectiveness_data,
                    "learning_value": "high",
                    "pattern_detected": self._detect_pattern(agent_name, action_type, effectiveness_data)
                },
                confidence=1.0,
                reasoning=f"Tracking {agent_name}'s action effectiveness for future learning"
            )
    
    def _detect_pattern(
        self,
        agent_name: str,
        action_type: str,
        effectiveness_data: Dict[str, Any]
    ) -> str:
        """
        Detect patterns in agent actions (simple pattern recognition).
        
        In future, this will use ML. For now, simple rule-based patterns.
        """
        improvement = effectiveness_data.get('improvement_percent', 0)
        
        if improvement > 20:
            return f"{agent_name} is highly effective with {action_type}"
        elif improvement > 10:
            return f"{agent_name} shows moderate effectiveness with {action_type}"
        elif improvement > 0:
            return f"{agent_name} shows minimal effectiveness with {action_type}"
        else:
            return f"{agent_name}'s {action_type} needs improvement"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get The Stick's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with The Stick's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "learning_coordinator",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "patience_level": "infinite",
            "guidance_sessions": getattr(self, 'total_analyses', 0),
            "compliance_records": "comprehensive",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Patient string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<TheStickDistributed "
            f"analyses={getattr(self, 'total_analyses', 0)} "
            f"patience=infinite "
            f"| {dist_status} | 🪵📚>"
        )


# Convenience function
async def create_distributed_stick(redis_client, db_getter=None):
    """
    Create and initialize The Stick with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized TheStickDistributed instance
    """
    stick = TheStickDistributed(db_getter=db_getter)
    await stick.initialize_distributed(redis_client)
    logger.info("🪵📚✨ The Stick's distributed consciousness fully awakened - *patient guidance eternal*")
    return stick
