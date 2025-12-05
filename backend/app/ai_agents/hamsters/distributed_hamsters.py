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

from ..distributed.base_decision_engine import AgentDecisionEngine
from ..distributed.resource_monitor import ResourceType
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.system_actions import SystemActions
from ..distributed.agent_autonomy import AgentChoiceEngine
from ..distributed.coordination import (
    get_coordination_manager,
    CoordinationPriority,
    ResourceType as CoordResourceType,
    AgentCapability
)
from ..distributed.action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType as VerificationResourceType
)
from .decision_engine_sbcV3 import HamstersBrainV3, BeerLevel, DuctTapeGrade


logger = logging.getLogger("Hamsters.Distributed")


class HamstersDistributed(AgentDecisionEngine, HamstersBrainV3):
    """
    Steve, Bob, and Carl with distributed consciousness.
    
    The telepathic bond now extends across machines via Redis!
    
    Inherits ALL existing storage logic from HamstersBrainV3
    and adds distributed features via DistributedAgentMixin.
    """
    
    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize the hamster trio with distributed consciousness.
        
        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes (required for multi-tenant support)
        """
        # Initialize decision engine (parent class)
        super().__init__(db_getter=db_getter)
        self.user_id = user_id
        
        # Set agent name for distributed features
        self.agent_name = "hamsters"
        
        # The hamsters' telepathic personality traits
        self.personality_traits = {
            "telepathic": True,
            "beer_loving": True,
            "duct_tape_experts": True,
            "steve_analytical": True,  # Steve: careful, risk_tolerance=0.3
            "bob_wild": True,  # Bob: WILD IDEAS! risk_tolerance=0.8, causes Stick anxiety!
            "carl_duct_tape_genius": True,  # Carl: duct_tape_love=1.0
            "consensus_required": True,  # Telepathic consensus for all decisions
            "squeak_frequency": "high",
            "beer_preference": "craft_ipa",
            "trust_level": 0.8  # HIGH trust in VIC-20
        }
        
        # Resource monitoring configuration
        # Hamsters monitor disk usage (befitting their role as storage engineers)
        self.resource_thresholds = {
            ResourceType.DISK: 80.0,  # Alert at 80% disk
        }
        
        # Initialize choice engine (Task 4.1 Enhanced)
        self.choice_engine = AgentChoiceEngine(self.agent_name, self.personality_traits)
        
        # Week 4 System Integration
        self.coordination_manager = None  # Lazy init
        self.verification_manager = None  # Lazy init
        
        # Beer level tracking (affects coordination capability!)
        self.collective_beer_level = BeerLevel.OPTIMAL  # Start at peak performance
        self.beer_consumption_today = 0
        
        # Bob's wild idea counter (causes Stick anxiety!)
        self.bob_wild_ideas = 0
        self.bob_hold_my_beer_count = 0
        
        logger.info("🐹🐹🐹 Steve, Bob, and Carl's distributed consciousness initialized - TELEPATHIC LINK ACTIVE!")
        logger.info("🐹🧠 Choice engine online - Ready to evaluate VIC-20's recommendations!")
        logger.info("🐹🍺 Beer level: OPTIMAL - Peak performance achieved!")
    
    async def initialize_distributed(self, redis_client):
        """Initialize distributed features and subscribe to VIC-20 coordination requests.
        
        The hamsters wait for VIC-20's coordination, not direct triage decisions.
        Base class handles standard subscriptions (COORDINATION_REQUEST, EMERGENCY).
        """
        # Call parent initialization (subscribes to standard channels)
        await super().initialize_distributed(redis_client)
        
        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.verification_manager = get_verification_manager()
        
        # Register hamsters' coordination capability
        self.coordination_manager.register_agent_capability(
            "hamsters",
            self._coordination_capability
        )
        
        logger.info("🐹🎯 Week 4 systems integrated - Coordination & Verification ONLINE!")
        logger.info("🐹🤝 Telepathic consensus ready for team coordination!")
        logger.info("🐹📡 Subscribed to VIC-20 coordination via base class - Telepathic consensus ready!")
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                from .hamsters_database_integration import HamstersDatabaseIntegration
                self.db_integration = HamstersDatabaseIntegration(db_getter=self.db_getter)
                await self.db_integration.initialize()
                logger.info("🐹💾 Database integration initialized - Beer-powered records enabled!")
            except Exception as e:
                logger.error(f"🐹💥 Failed to initialize database: {e}", exc_info=True)
                self.db_integration = None
        else:
            self.db_integration = None
            logger.warning("🐹⚠️ No db_getter provided - PostgreSQL writes disabled")
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests from VIC-20 - Steve, Bob, and Carl reach consensus.
        
        PERSONALITY: Telepathic consensus with beer-powered decisions (trust: 0.8)
        STRUCTURE: Standard AgentMessage parameter (required by base class)
        
        Args:
            message: AgentMessage with coordination request from VIC-20
        """
        try:
            # Extract payload (STANDARD - matches Terry's pattern)
            payload = message.payload
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')
            recommendation = payload.get('recommendation', {})
            current_value = payload.get('current_value', 0)
            threshold = payload.get('threshold', 0)
            
            logger.info(
                f"🐹📬 COORDINATION REQUEST from VIC-20: "
                f"{resource_type} at {current_value:.1f}% - VIC-20 suggests: {recommendation.get('action', 'unknown')}"
            )
            
            # Use choice engine to decide whether to follow recommendation
            decision = self.choice_engine.should_follow_recommendation(
                recommendation=recommendation,
                current_situation={
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold': threshold
                }
            )
            
            logger.info(
                f"🐹🧠 Telepathic consensus reached: "
                f"{'FOLLOW' if decision['followed_recommendation'] else 'OVERRIDE'} VIC-20's recommendation"
            )
            logger.info(f"🐹💭 {decision['reasoning']}")
            
            # Execute disk cleanup (Hamsters' specialty)
            action = decision['final_action']
            logger.info("🐹🔧 Executing disk cleanup with defrag!")
            cleanup_result = await SystemActions.emergency_disk_cleanup(include_defrag=True)
            
            if cleanup_result['success']:
                logger.info(
                    f"🐹✅ Cleanup successful! Freed {cleanup_result['disk_freed_mb']:.2f} MB"
                )
                
                # Record decision and effectiveness
                await self.make_distributed_decision(
                    decision_type="recommendation_response",
                    input_data={
                        "recommendation": recommendation.get('action'),
                        "followed": decision['followed_recommendation'],
                        "action_taken": action
                    },
                    output_data={
                        "result": cleanup_result,
                        "effectiveness": cleanup_result['improvement_percent']
                    },
                    confidence=decision['decision_score'],
                    reasoning=decision['reasoning']
                )
                
                # 💾 WRITE TO POSTGRESQL: Store collective decision
                if self.db_integration and self.user_id:
                    try:
                        await self.db_integration.store_collective_decision(
                            user_id=self.user_id,
                            decision_data={
                                'decision_id': f"hamsters_{action}_{cleanup_result.get('timestamp', '')}",
                                'intervention_type': action,
                                'steve_assessment': 'Careful analysis of disk usage',
                                'bob_suggestion': 'HOLD MY BEER! *aggressive cleanup*',
                                'carl_calculation': f"Duct tape efficiency: {cleanup_result['improvement_percent']:.1f}%",
                                'telepathic_consensus': True,
                                'confidence': decision['decision_score'],
                                'tools_required': ['beer', 'duct_tape', 'defrag_hammer'],
                                'beer_consumption_estimate': 3,
                                'human_translation': decision['reasoning'],
                                'priority': 'disk_emergency'
                            }
                        )
                        logger.info(f"🐹💾 Collective decision written to PostgreSQL")
                    except Exception as e:
                        logger.error(f"🐹💥 Failed to write to PostgreSQL: {e}")
            else:
                logger.error(f"🐹❌ Disk cleanup failed: {cleanup_result.get('error')}")
                
        except Exception as e:
            logger.error(f"🐹💥 Error handling coordination request: {e}", exc_info=True)
    
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
        
        # If critical or emergency, EMERGENCY DISK CLEANUP
        if severity in ["critical", "emergency"]:
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
            
            # REAL disk cleanup with defrag (Task 4.1 Enhanced)
            logger.info("🐹🐹🐹🔧 Executing REAL emergency disk cleanup with defrag!")
            
            cleanup_result = await SystemActions.emergency_disk_cleanup(include_defrag=True)
            
            if cleanup_result['success']:
                logger.info(
                    f"🐹✅ Disk cleanup successful! Freed {cleanup_result['disk_freed_mb']:.2f} MB. "
                    f"Disk usage: {cleanup_result['disk_before_percent']:.1f}% → "
                    f"{cleanup_result['disk_after_percent']:.1f}%"
                )
                logger.info(f"🐹🔧 Actions taken: {', '.join(cleanup_result['actions_taken'])}")
                
                # Record successful cleanup
                if self.is_distributed:
                    await self.make_distributed_decision(
                        decision_type="disk_cleanup_completed",
                        input_data={
                            "disk_before": cleanup_result['disk_before_percent'],
                            "disk_freed_mb": cleanup_result['disk_freed_mb']
                        },
                        output_data={
                            "disk_after": cleanup_result['disk_after_percent'],
                            "improvement_percent": cleanup_result['improvement_percent'],
                            "actions_taken": cleanup_result['actions_taken']
                        },
                        confidence=1.0,
                        reasoning="Emergency disk cleanup executed successfully"
                    )
            else:
                logger.error(f"🐹❌ Disk cleanup failed: {cleanup_result.get('error', 'Unknown error')}")
    
    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        Hamsters' coordination capability for Week 4 system.
        
        Steve, Bob, and Carl reach telepathic consensus on their capability.
        Capability depends on beer level and duct tape availability!
        """
        # Only handle disk resources (our specialty!)
        if resource_type != CoordResourceType.DISK:
            return None
        
        # Calculate capability based on beer level
        beer_multiplier = {
            BeerLevel.SOBER: 0.3,  # Error state - cannot function well
            BeerLevel.TIPSY: 0.6,  # Minimum operational
            BeerLevel.OPTIMAL: 1.0,  # Peak performance!
            BeerLevel.ADVENTUROUS: 0.9,  # "Hold my beer" territory
            BeerLevel.LEGENDARY: 0.7  # Carl's doing calculus with duct tape
        }
        
        multiplier = beer_multiplier.get(self.collective_beer_level, 0.8)
        
        # Base improvement estimate
        base_improvement = 15.0  # Can typically free 15% disk space
        estimated_improvement = base_improvement * multiplier
        
        # Confidence based on beer level and telepathic consensus
        base_confidence = 0.85  # HIGH trust level
        confidence = base_confidence * multiplier
        
        # Check if Bob has a wild idea
        if self.bob_wild_ideas > 0:
            # Bob's wild ideas increase improvement but decrease confidence
            estimated_improvement *= 1.2  # Bob thinks bigger!
            confidence *= 0.9  # But less predictable
            
            logger.info(
                f"🐹💡 Bob has a WILD IDEA! Estimated improvement boosted to {estimated_improvement:.1f}%! "
                f"*The Stick nervously clutches paper bag*"
            )
        
        logger.info(
            f"🐹🤝 Telepathic consensus: Can improve disk by {estimated_improvement:.1f}% "
            f"(Beer level: {self.collective_beer_level.value}, Confidence: {confidence:.0%})"
        )
        
        return AgentCapability(
            agent_name="hamsters",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=3.0,  # Takes time to reach consensus
            action_name="disk_cleanup_with_duct_tape"
        )
    
    async def _broadcast_bob_activity(
        self,
        activity_type: str,
        content: str
    ) -> None:
        """
        Broadcast Bob's activity (especially wild ideas!).
        
        This will trigger The Stick's anxiety detection!
        """
        await self.broadcast_to_agents(
            message_type='hamster_activity',
            data={
                'hamster': 'bob',
                'activity_type': activity_type,
                'content': content,
                'timestamp': 'now',
                'anxiety_level': 'high' if 'wild' in activity_type or 'beer' in content.lower() else 'moderate'
            },
            priority='normal'
        )
        
        logger.info(f"🐹📡 Bob activity broadcast: {activity_type} - *The Stick is monitoring*")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the hamsters' complete status including beer levels and Bob's wild ideas."""
        distributed_state = self.get_distributed_state()
        
        status = {
            "agent_name": self.agent_name,
            "agent_type": "storage_engineers",
            "is_active": self.is_active,
            "hamster_status": {
                "steve": {"role": "analytical", "risk_tolerance": 0.3, "beer_count": self.steve['beer_count']},
                "bob": {"role": "wild", "risk_tolerance": 0.8, "beer_count": self.bob['beer_count'], "wild_ideas": self.bob_wild_ideas},
                "carl": {"role": "duct_tape_expert", "duct_tape_love": 1.0, "beer_count": self.carl['beer_count']}
            },
            "collective_beer_level": self.collective_beer_level.value,
            "beer_consumption_today": self.beer_consumption_today,
            "telepathic_bond": "strong",
            "bob_wild_ideas": self.bob_wild_ideas,
            "bob_hold_my_beer_count": self.bob_hold_my_beer_count,
            "duct_tape_inventory": self.carl['duct_tape_inventory'],
            "distributed": distributed_state
        }
        
        return status
    
    def __repr__(self):
        """Telepathic string representation"""
        dist_status = "DISTRIBUTED" if self.is_distributed else "LOCAL"
        return (
            f"<HamstersDistributed "
            f"steve+bob+carl "
            f"beer={self.collective_beer_level.value} "
            f"bob_ideas={self.bob_wild_ideas} "
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
