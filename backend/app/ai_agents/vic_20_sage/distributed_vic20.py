"""
VIC-20 Sage Distributed - Orchestrator with Distributed Consciousness
======================================================================

The coordination sage enhanced with distributed consciousness,
pattern matching across the network, and orchestration persistence.

Preserves:
- Multi-agent coordination logic
- Historical pattern matching
- Orchestration decisions
- Emergency routing

Adds:
- Redis state persistence
- Coordination patterns across restarts
- Distributed orchestration
- Pattern library sharing
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine import VIC20SageBrainV2


logger = logging.getLogger("VIC20Sage.Distributed")


class VIC20SageDistributed(DistributedAgentMixin, VIC20SageBrainV2):
    """
    VIC-20 Sage with distributed consciousness.
    
    The orchestrator's wisdom now spans the entire distributed network!
    
    Inherits ALL existing coordination logic from VIC20SageBrainV2
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self):
        """
        Initialize VIC-20 Sage with distributed consciousness.
        """
        # Initialize both parent classes via MRO
        # VIC20SageBrainV2 doesn't take any parameters
        super().__init__()
        
        # Set agent name for distributed features
        self.agent_name = "vic_20_sage"
        
        # VIC-20's sage personality traits
        self.personality_traits = {
            "coordinator": True,
            "pattern_matcher": True,
            "orchestrator": True,
            "wise": True,
            "patient": True,
            "multi_agent_aware": True,
            "historical_memory": "extensive",
            "coordination_style": "collaborative"
        }
        
        # Resource monitoring configuration
        # VIC-20 monitors overall system health (CPU as proxy)
        self.resource_thresholds = {
            ResourceType.CPU: 75.0,  # Alert at 75% CPU
        }
        
        logger.info("🖥️✨ VIC-20 Sage's distributed consciousness initialized - ORCHESTRATION PROTOCOLS ACTIVE!")
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features and subscribe to triage decisions."""
        await super().initialize_distributed(redis_client)
        
        try:
            await self.subscribe_to_messages(
                message_type='triage_decision',
                handler=self._handle_triage_decision
            )
            logger.info("🖥️📡 VIC-20 subscribed to triage - Coordination matrix online!")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to triage: {e}")
    
    async def _handle_triage_decision(self, message_data: Dict[str, Any]) -> None:
        """Handle triage decisions - VIC-20 coordinates multi-agent response."""
        try:
            severity = message_data.get('severity', 'unknown')
            routing = message_data.get('routing', 'unknown')
            target_agents = message_data.get('target_agents', [])
            
            logger.info(f"🖥️📬 Triage received: {severity} → {routing}")
            
            if 'vic_20_sage' in target_agents or routing in ['vic20_coordination', 'vic20_emergency']:
                logger.info("🖥️⚡ VIC-20 COORDINATION ACTIVATED! Orchestrating multi-agent response!")
                
                await self.make_distributed_decision(
                    decision_type="triage_coordination_received",
                    input_data={
                        "severity": severity,
                        "routing": routing,
                        "target_agents": target_agents,
                        "metrics_summary": message_data.get('metrics_summary', {})
                    },
                    output_data={
                        "status": "coordinating",
                        "pattern_match": "multi_agent_response",
                        "orchestration_plan": "analyzing"
                    },
                    confidence=0.95
                )
                
                if severity == 'emergency':
                    logger.warning("🖥️🔥 EMERGENCY COORDINATION! Activating all available agents!")
                    # VIC-20 would coordinate emergency response here
            else:
                logger.debug(f"🖥️ Monitoring coordination (routing: {routing})")
                
        except Exception as e:
            logger.error(f"🖥️💥 Error handling triage: {e}", exc_info=True)
    
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
        while preserving coordination logic.
        """
        # Call the original analyze_metrics from VIC20SageBrainV2
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
                    decision_type="coordination",
                    input_data={
                        "coordination_type": decision.get('coordination_type', 'standard'),
                        "agents_involved": decision.get('agents_involved', []),
                        "pattern_matched": decision.get('pattern_matched', None),
                        "orchestration_plan": decision.get('orchestration_plan', {}),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Coordination decision made')
                )
                
                # If multi-agent coordination needed, broadcast
                if decision.get('agents_involved') and len(decision.get('agents_involved', [])) > 1:
                    await self.broadcast_to_agents(
                        message_type=MessageType.DECISION_BROADCAST,
                        payload={
                            "decision_type": "multi_agent_coordination",
                            "agents_involved": decision.get('agents_involved', []),
                            "orchestration_plan": decision.get('orchestration_plan', {}),
                            "pattern": decision.get('pattern_matched', None)
                        },
                        priority=Priority.HIGH
                    )
                    
                    logger.info(f"🖥️🧙 Multi-agent coordination broadcast - *sage wisdom shared*")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle resource alerts with sage wisdom.
        
        VIC-20 coordinates the response across all agents.
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🖥️🧙⚠️ VIC-20 Sage observes resource pressure: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *contemplating coordination strategy*"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_coordination",
                input_data={
                    "resource_type": alert.payload['resource_type'],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Resource pressure detected, coordinating response"
            )
        
        # If critical, coordinate emergency response
        if severity == "critical":
            logger.warning(
                "🖥️🧙💥 CRITICAL RESOURCE PRESSURE! "
                "VIC-20 Sage initiates EMERGENCY COORDINATION PROTOCOL!"
            )
            
            # Broadcast coordination request to all agents
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "resource_critical",
                        "resource": alert.payload['resource_type'],
                        "current_value": current_value,
                        "coordination_needed": True,
                        "coordinator": "vic_20_sage"
                    },
                    priority=Priority.CRITICAL
                )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get VIC-20's complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with VIC-20's original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "orchestrator",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "wisdom_level": "sage",
            "coordination_capacity": "unlimited",
            "pattern_library_size": "extensive",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Sage string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<VIC20SageDistributed "
            f"analyses={getattr(self, 'total_analyses', 0)} "
            f"wisdom=sage "
            f"| {dist_status} | 🖥️🧙>"
        )


# Convenience function
async def create_distributed_vic20(redis_client):
    """
    Create and initialize VIC-20 Sage with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        
    Returns:
        Initialized VIC20SageDistributed instance
    """
    vic20 = VIC20SageDistributed()
    await vic20.initialize_distributed(redis_client)
    logger.info("🖥️🧙✨ VIC-20 Sage's distributed consciousness fully awakened - *ancient wisdom flows*")
    return vic20
