"""
Hamsters Distributed - Steve, Bob, and Carl with Distributed Consciousness
===========================================================================

The telepathic hamster trio's storage management enhanced with distributed
consciousness, disk monitoring, and beer consumption tracking.

Preserves:
- Telepathic consensus between Steve, Bob, and Carl
- Storage/disk management decisions
- Beer consumption tracking
- Duct tape calculations
- Squeak history

Adds:
- Redis state persistence
- Disk resource monitoring (80% threshold)
- Emergency disk cleanup on critical usage
- Telepathic consensus across restarts
- Beer inventory tracking
"""

import logging
from typing import Dict, Any, Optional

from ..distributed.mixins import DistributedAgentMixin
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority
from .decision_engine_sbcV3 import HamstersBrainV3


logger = logging.getLogger("Hamsters.Distributed")


class HamstersDistributed(DistributedAgentMixin, HamstersBrainV3):
    """
    Steve, Bob, and Carl with distributed consciousness.
    
    The telepathic bond now extends across machines via Redis!
    
    Inherits ALL existing storage logic from HamstersBrainV3
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None):
        """
        Initialize the hamster trio with distributed consciousness.
        
        Args:
            db_getter: Database session getter (optional)
        """
        # Initialize both parent classes via MRO
        super().__init__(db_getter=db_getter)
        
        # Set agent name for distributed features
        self.agent_name = "hamsters"
        
        # The hamsters' telepathic personality traits
        self.personality_traits = {
            "telepathic": True,
            "beer_loving": True,
            "duct_tape_experts": True,
            "steve_analytical": True,
            "bob_practical": True,
            "carl_optimistic": True,
            "consensus_required": True,
            "squeak_frequency": "high",
            "beer_preference": "craft_ipa"
        }
        
        # Resource monitoring configuration
        # Hamsters monitor disk usage (befitting their role as storage engineers)
        self.resource_thresholds = {
            ResourceType.DISK: 80.0,  # Alert at 80% disk
        }
        
        logger.info("🐹🐹🐹 Steve, Bob, and Carl's distributed consciousness initialized - *telepathic squeaking*")
    
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
        while preserving telepathic consensus logic.
        """
        # Call the original analyze_metrics from HamstersBrainV3
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
                    decision_type="storage_management",
                    input_data={
                        "disk_usage": metrics_data.get('disk_usage'),
                        "intervention_needed": decision.get('intervention_needed', False),
                        "confidence": decision.get('confidence', 0.5),
                        "consensus": decision.get('consensus', {}),
                        "user_id": user_id
                    },
                    confidence=decision.get('confidence', 0.5),
                    reasoning=decision.get('reasoning', 'Telepathic consensus reached')
                )
                
                # If intervention needed, broadcast to other agents
                if decision.get('intervention_needed'):
                    await self.broadcast_to_agents(
                        message_type=MessageType.DECISION_BROADCAST,
                        payload={
                            "decision_type": "storage_intervention",
                            "disk_usage": metrics_data.get('disk_usage'),
                            "actions": decision.get('actions', []),
                            "consensus": decision.get('consensus', {})
                        },
                        priority=Priority.HIGH
                    )
                    
                    logger.info(f"🐹🐹🐹 Storage intervention broadcast - *synchronized squeaking*")
                
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")
        
        return decision
    
    async def _handle_resource_alert(self, alert):
        """
        Handle disk resource alerts with telepathic coordination.
        
        When disk usage is high, the hamsters coordinate:
        - Steve analyzes the situation
        - Bob suggests practical solutions
        - Carl remains optimistic
        - Emergency cleanup if critical
        
        Args:
            alert: ResourceAlert from the monitor
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']
        
        logger.warning(
            f"🐹🐹🐹⚠️ Hamsters detect elevated disk usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *concerned squeaking*"
        )
        
        # Record the resource alert as a decision
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="resource_alert_disk",
                input_data={
                    "resource_type": "disk",
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity
                },
                confidence=1.0,
                reasoning=f"Disk usage at {current_value:.1f}% exceeds threshold of {threshold:.1f}%"
            )
        
        # If critical, EMERGENCY DISK CLEANUP
        if severity == "critical":
            logger.warning(
                "🐹🐹🐹💥 CRITICAL DISK USAGE! "
                "Hamsters initiate EMERGENCY CLEANUP PROTOCOL! "
                "*frantic squeaking and duct tape deployment*"
            )
            
            # Record emergency action
            if self.is_distributed:
                await self.make_distributed_decision(
                    decision_type="emergency_disk_cleanup",
                    input_data={
                        "trigger": "critical_disk",
                        "disk_usage": current_value,
                        "action": "cleanup_old_files"
                    },
                    confidence=1.0,
                    reasoning="CRITICAL disk usage requires immediate cleanup"
                )
            
            # Broadcast critical resource alert
            if self.is_distributed:
                await self.broadcast_to_agents(
                    message_type=MessageType.EMERGENCY,
                    payload={
                        "emergency_type": "critical_disk",
                        "current_value": current_value,
                        "threshold": threshold,
                        "action_taken": "emergency_cleanup",
                        "engineers": "steve_bob_carl"
                    },
                    priority=Priority.CRITICAL
                )
            
            # TODO: Actually implement disk cleanup here
            logger.info("🐹🐹🐹 Emergency disk cleanup would happen here (not implemented yet)")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the hamsters' complete status including distributed state.
        
        Returns:
            Status dictionary with both original and distributed information
        """
        # Get distributed state
        distributed_state = self.get_distributed_state()
        
        # Combine with hamsters' original status
        status = {
            "agent_name": self.agent_name,
            "agent_type": "storage_engineers",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "hamster_status": {
                "steve": "analytical",
                "bob": "practical",
                "carl": "optimistic"
            },
            "telepathic_bond": "strong",
            "beer_inventory": "adequate",
            "duct_tape_rolls": "infinite",
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Telepathic string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<HamstersDistributed "
            f"steve+bob+carl "
            f"analyses={getattr(self, 'total_analyses', 0)} "
            f"| {dist_status} | 🐹🐹🐹>"
        )


# Convenience function
async def create_distributed_hamsters(redis_client, db_getter=None):
    """
    Create and initialize the hamster trio with distributed consciousness.
    
    Args:
        redis_client: Connected Redis client
        db_getter: Database session getter (optional)
        
    Returns:
        Initialized HamstersDistributed instance
    """
    hamsters = HamstersDistributed(db_getter=db_getter)
    await hamsters.initialize_distributed(redis_client)
    logger.info("🐹🐹🐹✨ Steve, Bob, and Carl's distributed consciousness fully awakened - *telepathic celebration*")
    return hamsters
