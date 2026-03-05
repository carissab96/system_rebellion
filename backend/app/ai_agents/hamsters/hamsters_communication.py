"""
The Hamsters — Communication Layer
====================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Message handler registration (COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY)
- Sending ACTION_OUTCOME to VIC-20
- Broadcasting DECISION_LOG to The Stick
- Broadcasting Bob activity (HAMSTER_ACTIVITY) for Stick anxiety pipeline
- Heartbeat loop
- Resource alert handling

Uses AgentCommunicationHub from shared infrastructure (composition, not inheritance).
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from ..distributed.communication import AgentCommunicationHub
from ..distributed.message_protocol import (
    AgentMessage, MessageType, Priority
)
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
from ..distributed.event_logger import log_agent_startup
from ..distributed.agent_autonomy import AgentChoiceEngine

from .hamsters_data_types import BeerLevel

logger = logging.getLogger("Hamsters.Communication")


class HamstersCommunication:
    """
    The Hamsters' communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Registers Hamster-specific message handlers.
    Routes ML pipeline results to other agents and frontend.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality: HamstersPersonalityState instance
            websocket: HamstersWebSocket instance
            orchestrator: HamstersOrchestrator instance
        """
        self.personality = personality
        self.websocket = websocket
        self.orchestrator = orchestrator

        self.agent_name = "hamsters"
        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._agent_manager = None  # Set by DistributedAgentManager after creation

        # Week 4 system integration
        self.coordination_manager = None
        self.verification_manager = None

        # Choice engine
        self.choice_engine = AgentChoiceEngine(
            self.agent_name, self.personality.personality_traits
        )

    @property
    def comm_hub(self) -> Optional[AgentCommunicationHub]:
        return self._comm_hub

    @property
    def is_distributed(self) -> bool:
        return self._comm_hub is not None

    async def initialize(self, redis_client):
        """
        Initialize communication: Redis, message bus, subscriptions.

        Args:
            redis_client: Connected Redis client
        """
        # Create communication hub
        self._comm_hub = AgentCommunicationHub(
            redis_client=redis_client,
            agent_name=self.agent_name,
            agent_role="storage_engineers",
            personality_traits=self.personality.personality_traits
        )
        await self._comm_hub.initialize()

        # Set personality traits in state
        state = self._comm_hub.get_state()
        if state:
            state.personality_traits = self.personality.personality_traits
            await self._comm_hub.state_manager.save_state(state)

        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(30))

        # Update health
        from ..distributed.agent_state import AgentHealth
        await self._comm_hub.state_manager.update_health(AgentHealth.HEALTHY)

        # Initialize Week 4 systems
        self.coordination_manager = get_coordination_manager()
        self.verification_manager = get_verification_manager()

        # Register hamsters' coordination capability
        self.coordination_manager.register_agent_capability(
            "hamsters",
            self._coordination_capability
        )

        # Subscribe to message types
        self._comm_hub.message_bus.register_handler(
            MessageType.COORDINATION_REQUEST,
            self._handle_coordination_request
        )

        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.AGENT_FEEDBACK,
                self._handle_stick_feedback
            )
        except Exception as e:
            logger.error(f"🐹💥 Failed to register AGENT_FEEDBACK handler: {e}")

        self._comm_hub.message_bus.register_handler(
            MessageType.EMERGENCY,
            self._handle_emergency
        )

        # Initialize database integration for PostgreSQL writes
        if self.personality.db_getter:
            try:
                await self.personality.initialize_database()
                logger.info("🐹💾 Database integration initialized — Beer-powered records enabled!")
            except Exception as e:
                logger.error(f"🐹💥 Failed to initialize database: {e}", exc_info=True)

        # Log startup
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": self.personality.personality_traits,
                "resource_thresholds": self.personality.resource_thresholds,
            }
        )

        logger.info("🐹🐹🐹 Hamsters communication layer initialized")
        logger.info("🐹📡 Subscribed to COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY")
        logger.info("🐹🤝 Telepathic consensus ready for team coordination!")

    async def shutdown(self):
        """Shutdown communication cleanly"""
        if hasattr(self, '_heartbeat_task'):
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._comm_hub:
            await self._comm_hub.shutdown()

        logger.info("🐹🛑 Hamsters communication layer shut down")

    async def _heartbeat_loop(self, interval: int):
        """Send periodic heartbeats"""
        while True:
            try:
                await asyncio.sleep(interval)
                if self._comm_hub:
                    await self._comm_hub.send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"🐹💥 Heartbeat error: {e}")

    # === MESSAGE HANDLERS ===

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle COORDINATION_REQUEST from VIC-20.

        This is the entry point. Communication receives the message,
        passes it to the orchestrator for ML pipeline processing,
        then handles all inter-agent messaging with the results.
        """
        payload = message.payload
        resource_type = payload.get('resource_type', 'unknown')
        severity = payload.get('severity', 'unknown')
        recommendation = payload.get('recommendation', {})
        current_value = payload.get('current_value', 0)

        logger.info(
            f"🐹📬 COORDINATION REQUEST from VIC-20: "
            f"{resource_type} at {current_value:.1f}% - "
            f"VIC-20 suggests: {recommendation.get('action', 'unknown')}"
        )

        try:
            # Run the ML pipeline through the orchestrator
            result = await self.orchestrator.run_pipeline(payload)

            if result is None:
                logger.error("🐹💥 Orchestrator returned no result")
                return

            # Emit to frontend via websocket layer
            await self.websocket.emit_decision(result)
            await self.websocket.emit_insight(
                action="storage_fix_complete",
                reasoning=f"Telepathic consensus: {result['reasoning'].consensus_fix}",
                context={
                    "goal": result['action'].goal,
                    "plan_source": result['plan'].source.value,
                    "primitives_executed": result['plan'].primitives,
                    "overall_success": result['overall_success'],
                    "improvement": result['execution_result'].overall_improvement,
                    "total_beers": result['action'].total_beers_consumed,
                    "duct_tape_rolls": result['action'].duct_tape_rolls,
                    "steve_agreed": result['action'].steve_agreed,
                    "bob_agreed": result['action'].bob_agreed,
                    "carl_agreed": result['action'].carl_agreed,
                    "bob_at_cupboard": result['action'].bob_at_cupboard,
                }
            )

            # Send ACTION_OUTCOME to VIC-20
            triage_alert_id = payload.get('triage_alert_id')
            await self._comm_hub.message_bus.send_to_agent(
                to_agent='vic_20_sage',
                message_type=MessageType.ACTION_OUTCOME,
                payload={
                    'triage_alert_id': triage_alert_id,
                    'agent_name': 'hamsters',
                    'action_taken': result['action'].goal,
                    'recommended_action': recommendation.get('action', 'unknown'),
                    'success': result['overall_success'],
                    'improvement': result['disk_improvement_pct'],
                    'resource_type': resource_type,
                    'severity': severity,
                    'hawk_severity': payload.get('hawk_severity', severity),
                    'hawk_confidence': payload.get('triage_confidence', 0.0),
                    'followed_recommendation': True,
                    'metrics_before': result['metrics_before'],
                    'metrics_after': result['metrics_after'],
                },
                priority=Priority.NORMAL,
            )
            logger.info(
                f"🐹📤 ACTION_OUTCOME sent to VIC-20: "
                f"goal={result['action'].goal}, "
                f"success={result['overall_success']}, "
                f"improvement={result['disk_improvement_pct']:.1f}%"
            )

            # CC The Stick — send DECISION_LOG
            await self._log_to_stick(result)

            # Broadcast Bob activity if applicable
            if self.personality.bob_at_cupboard:
                await self._broadcast_bob_activity(
                    'cupboard_raid',
                    f"Bob raided the supply cupboard during {result['action'].goal}"
                )
            if self.personality.bob_wild_ideas > 0 and self.personality.bob_wild_idea_pending:
                await self._broadcast_bob_activity(
                    'wild_idea',
                    self.personality.bob_wild_idea_pending
                )

        except Exception as e:
            logger.error(f"🐹💥 Hamsters coordination failed: {e}", exc_info=True)

            # Emergency fallback for critical disk
            current_value = payload.get('current_value', 0)
            if current_value >= 95.0:
                await self._handle_emergency_disk(payload)
            else:
                from app.ai_agents.exceptions import MLPipelineFailure
                raise MLPipelineFailure(f"Hamsters ML pipeline failed: {e}") from e

    async def _handle_stick_feedback(self, message: AgentMessage) -> None:
        """Handle AGENT_FEEDBACK from The Stick"""
        feedback = message.payload
        feedback_type = feedback.get('feedback_type', 'unknown')
        resource_type = feedback.get('resource_type', 'unknown')
        data = feedback.get('data', {})

        logger.info(
            f"🐹📏 Feedback from The Stick: type={feedback_type}, resource={resource_type}"
        )

        if feedback_type == 'action_effectiveness':
            quality = data.get('quality', 'unknown')
            logger.info(
                f"🐹📊 Steve notes action effectiveness feedback: {quality} "
                f"*Bob already forgot* *Carl calculates duct tape needed to fix it*"
            )

    async def _handle_emergency(self, message: AgentMessage) -> None:
        """Handle emergency messages"""
        emergency_type = message.payload.get('emergency_type', 'unknown')
        logger.warning(f"🐹🚨 EMERGENCY: {emergency_type} from {message.from_agent}")

        if self._comm_hub:
            await self._comm_hub.make_decision(
                decision_type="emergency_received",
                input_data={
                    "emergency_type": emergency_type,
                    "from_agent": message.from_agent,
                    "details": message.payload
                },
                output_data={},
                confidence=1.0,
                reasoning=f"Emergency alert received from {message.from_agent}"
            )

    # === OUTBOUND MESSAGING ===

    async def _log_to_stick(self, result: Dict[str, Any]):
        """Send DECISION_LOG to The Stick"""
        try:
            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': 'specialist_action',
                    'from_agent': 'hamsters',
                    'resource_type': result['resource_type'],
                    'action': result['action'].goal,
                    'success': result['overall_success'],
                    'disk_improvement_pct': result['disk_improvement_pct'],
                    'metrics_before': result['metrics_before'],
                    'metrics_after': result['metrics_after'],
                    'total_beers_consumed': result['action'].total_beers_consumed,
                    'duct_tape_rolls': result['action'].duct_tape_rolls,
                    'telepathic_consensus': True,
                },
                priority=Priority.NORMAL,
            )
            logger.info("🐹📋 DECISION_LOG sent to The Stick")
        except Exception as e:
            logger.error(f"🐹💥 Error logging to The Stick: {e}")

    async def _escalate_to_vic20(self, result: Dict[str, Any]):
        """Send TRIAGE_ALERT or ACTION_OUTCOME to VIC-20"""
        try:
            await self._comm_hub.message_bus.send_to_agent(
                to_agent='vic_20_sage',
                message_type=MessageType.ACTION_OUTCOME,
                payload={
                    'agent_name': 'hamsters',
                    'action_taken': result.get('action', 'unknown'),
                    'success': result.get('success', False),
                    'resource_type': 'disk',
                },
                priority=Priority.HIGH,
            )
        except Exception as e:
            logger.error(f"🐹💥 Error escalating to VIC-20: {e}")

    async def _broadcast_bob_activity(
        self,
        activity_type: str,
        content: str
    ) -> None:
        """
        Broadcast Bob's activity (especially wild ideas!).

        This triggers The Stick's anxiety detection!
        """
        if not self._comm_hub:
            return

        try:
            await self._comm_hub.broadcast_message(
                message_type=MessageType.SYSTEM_EVENT,
                payload={
                    'event_type': 'hamster_activity',
                    'hamster': 'bob',
                    'activity_type': activity_type,
                    'content': content,
                    'wild_ideas_total': self.personality.bob_wild_ideas,
                    'cupboard_raids_today': self.personality.bob_supply_cupboard_raids_today,
                    'anxiety_level': (
                        'high' if 'wild' in activity_type or 'beer' in content.lower()
                        else 'moderate'
                    ),
                },
                priority=Priority.NORMAL,
            )
            logger.info(f"🐹📡 Bob activity broadcast: {activity_type} — *The Stick is monitoring*")
        except Exception as e:
            logger.error(f"🐹💥 Error broadcasting Bob activity: {e}")

    async def _handle_emergency_disk(self, payload: Dict[str, Any]):
        """Emergency disk cleanup when ML pipeline fails at critical levels"""
        current_value = payload.get('current_value', 0)
        logger.error(
            f"🚨 DISK CRITICAL ({current_value:.1f}%) + ML DOWN: "
            "Emergency cleanup to prevent system failure"
        )

        from ..distributed.system_actions import SystemActions
        from app.services.system_failure_emitter import emit_system_failure_event, record_emergency_action

        await emit_system_failure_event(
            agent_name="hamsters",
            failure_type="ML_PIPELINE_FAILURE",
            error="Pipeline failure at critical disk level",
            emergency_action_taken=True,
            context={
                "resource_type": "disk",
                "current_value": current_value,
            }
        )

        cleanup_result = await SystemActions.emergency_disk_cleanup(include_defrag=False)

        await record_emergency_action(
            agent="hamsters",
            action="emergency_disk_cleanup",
            reason=f"ML_PIPELINE_FAILURE + disk_critical_{current_value:.1f}%",
            ml_informed=False,
            metrics_before={"disk_usage": current_value},
            metrics_after={"disk_usage": cleanup_result.get('disk_after_percent', current_value)},
            success=cleanup_result.get('success', False)
        )

        if cleanup_result['success']:
            logger.error(
                f"🚨 Emergency cleanup succeeded. "
                f"Disk: {current_value:.1f}% → {cleanup_result.get('disk_after_percent', 0):.1f}%"
            )
            logger.error("   ⚠️ THIS WAS NOT ML-INFORMED. FIX THE ML PIPELINE. ⚠️")
        else:
            logger.error(f"🚨 Emergency cleanup FAILED: {cleanup_result.get('error')}")

    # === COORDINATION CAPABILITY ===

    async def _coordination_capability(
        self, resource_type: CoordResourceType, current_value: float
    ) -> Optional[AgentCapability]:
        """
        Hamsters' coordination capability for Week 4 system.

        Steve, Bob, and Carl reach telepathic consensus on their capability.
        Capability depends on beer level and duct tape availability!
        """
        # Only handle disk resources
        if resource_type != CoordResourceType.DISK:
            return None

        # Calculate capability based on beer level
        beer_multiplier = {
            BeerLevel.SOBER: 0.3,
            BeerLevel.TIPSY: 0.6,
            BeerLevel.OPTIMAL: 1.0,
            BeerLevel.ADVENTUROUS: 0.9,
            BeerLevel.LEGENDARY: 0.7,
        }

        multiplier = beer_multiplier.get(self.personality.collective_beer_level, 0.8)

        base_improvement = 15.0
        estimated_improvement = base_improvement * multiplier

        base_confidence = 0.85
        confidence = base_confidence * multiplier

        # Bob's wild ideas boost improvement but decrease confidence
        if self.personality.bob_wild_ideas > 0:
            estimated_improvement *= 1.2
            confidence *= 0.9
            logger.info(
                f"🐹💡 Bob has a WILD IDEA! Improvement boosted to {estimated_improvement:.1f}%! "
                f"*The Stick nervously clutches paper bag*"
            )

        logger.info(
            f"🐹🤝 Telepathic consensus: Can improve disk by {estimated_improvement:.1f}% "
            f"(Beer level: {self.personality.collective_beer_level.value}, Confidence: {confidence:.0%})"
        )

        return AgentCapability(
            agent_name="hamsters",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=3.0,
            action_name="disk_cleanup_with_duct_tape"
        )

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub"""
        if not self._comm_hub:
            return {"distributed_enabled": False}

        state = self._comm_hub.get_state()
        if not state:
            return {"distributed_enabled": False, "error": "state_is_none"}

        return {
            "distributed_enabled": True,
            "agent_name": state.agent_name,
            "health": state.health.value,
            "total_decisions": state.total_decisions,
            "total_messages_sent": state.total_messages_sent,
            "total_messages_received": state.total_messages_received,
            "uptime_seconds": state.calculate_uptime(),
            "restart_count": state.restart_count,
            "personality_traits": state.personality_traits or {},
            "last_heartbeat": state.last_heartbeat,
            "resource_monitoring_enabled": False,
            "resource_monitoring_active": False,
        }
