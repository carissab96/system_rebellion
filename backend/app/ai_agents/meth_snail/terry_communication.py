"""
Terry the Meth Snail — Communication Layer
============================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Message handler registration (COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY)
- Sending ACTION_OUTCOME to VIC-20
- Broadcasting ACTION_REPORT and DECISION_LOG
- CC'ing The Stick on decisions
- Reporting overrides to The Stick

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

logger = logging.getLogger("MethSnail.Communication")


class TerryCommunication:
    """
    Terry's communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Registers Terry-specific message handlers.
    Routes ML pipeline results to other agents and frontend.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality: TerryPersonalityState instance
            websocket: TerryWebSocket instance
            orchestrator: TerryOrchestrator instance
        """
        self.personality = personality
        self.websocket = websocket
        self.orchestrator = orchestrator

        self.agent_name = "meth_snail"
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
            agent_role="memory_optimizer",
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

        # Register coordination capability
        self.coordination_manager.register_agent_capability(
            "meth_snail",
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
            logger.error(f"🐌💥 Failed to register AGENT_FEEDBACK handler: {e}")

        self._comm_hub.message_bus.register_handler(
            MessageType.EMERGENCY,
            self._handle_emergency
        )

        # Log startup
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": self.personality.personality_traits,
                "resource_thresholds": {},
            }
        )

        logger.info("🐌💨 Terry communication layer initialized")
        logger.info("🐌📡 Subscribed to COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY")

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

        logger.info("🐌🛑 Terry communication layer shut down")

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
                logger.error(f"🐌💥 Heartbeat error: {e}")

    # === MESSAGE HANDLERS ===

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle COORDINATION_REQUEST from VIC-20.

        This is the entry point. Communication receives the message,
        passes it to the orchestrator for ML pipeline processing,
        then handles all inter-agent messaging with the results.
        """
        try:
            payload = message.payload
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')
            recommendation = payload.get('recommendation', {})
            current_value = payload.get('current_value', 0)

            logger.info(
                f"🐌📬 COORDINATION REQUEST from VIC-20: "
                f"{resource_type} at {current_value:.1f}% - "
                f"VIC-20 suggests: {recommendation.get('action', 'unknown')}"
            )

            # Run the ML pipeline through the orchestrator
            result = await self.orchestrator.run_pipeline(payload)

            if result is None:
                logger.error("🐌💥 Orchestrator returned no result")
                return

            # Emit to frontend via websocket layer
            await self.websocket.emit_decision(result)
            await self.websocket.emit_insight(
                action=f"{result['decision'].action}_executed",
                reasoning=result['decision'].reasoning,
                context=result.get('insight_context', {})
            )

            # Send ACTION_OUTCOME to VIC-20
            triage_alert_id = payload.get('triage_alert_id')
            await self._comm_hub.message_bus.send_to_agent(
                to_agent='vic_20_sage',
                message_type=MessageType.ACTION_OUTCOME,
                payload={
                    'triage_alert_id': triage_alert_id,
                    'agent_name': 'meth_snail',
                    'action_taken': result['decision'].action,
                    'recommended_action': recommendation.get('action', 'unknown'),
                    'success': result['learning_record'].success,
                    'improvement': result['overall_improvement'],
                    'resource_type': resource_type,
                    'severity': severity,
                    'hawk_severity': payload.get('hawk_severity', severity),
                    'hawk_confidence': payload.get('triage_confidence', 0.0),
                    'followed_recommendation': result['decision'].followed_vic20,
                    'metrics_before': result['metrics_before'],
                    'metrics_after': result['metrics_after'],
                },
                priority=Priority.NORMAL,
            )
            logger.info(
                f"🐌📤 ACTION_OUTCOME sent to VIC-20: "
                f"action={result['decision'].action}, "
                f"success={result['learning_record'].success}, "
                f"improvement={result['overall_improvement']:.1f}%"
            )

            # Report success/failure
            action_result = result['action_result']
            if action_result['success']:
                logger.info(f"🐌✅ {result['decision'].action} succeeded!")

                await self._report_to_vic20(
                    resource_type=resource_type,
                    action=result['decision'].action,
                    result=action_result,
                    followed_recommendation=result['decision'].followed_vic20
                )

                await self._cc_the_stick(
                    decision_type='specialist_action',
                    resource_type=resource_type,
                    action=result['decision'].action,
                    result=action_result,
                    followed_vic20=result['decision'].followed_vic20
                )

                # Track override effectiveness
                if not result['decision'].followed_vic20:
                    self.personality.record_override_result(result['learning_record'].success)
                    if result['learning_record'].success:
                        logger.info(
                            f"🐌✅ TERRY WAS RIGHT! "
                            f"(Rate: {self.personality.successful_overrides}/{self.personality.total_overrides})"
                        )
                    else:
                        logger.warning(
                            f"🐌⚠️ Maybe VIC-20 was right... "
                            f"(Rate: {self.personality.successful_overrides}/{self.personality.total_overrides})"
                        )

                # Write result to database
                await self._write_action_result(
                    resource_type=resource_type,
                    action=result['decision'].action,
                    result=action_result,
                    followed_vic20=result['decision'].followed_vic20,
                    severity=severity
                )

                # Emit success to frontend
                await self.websocket.emit_insight(
                    action=f"{result['decision'].action}_success",
                    reasoning=f"Action completed - improvement: {result['overall_improvement']:.1f}%",
                    context={
                        "success": True,
                        "metrics_before": result['metrics_before'],
                        "metrics_after": result['metrics_after'],
                        "followed_vic20": result['decision'].followed_vic20,
                        "confidence": result['decision'].confidence
                    }
                )
            else:
                logger.error(f"🐌❌ {result['decision'].action} failed: {action_result.get('error')}")
                await self._cc_the_stick(
                    decision_type='specialist_action_failed',
                    resource_type=resource_type,
                    action=result['decision'].action,
                    result=action_result,
                    followed_vic20=result['decision'].followed_vic20
                )

        except Exception as e:
            logger.error(f"🐌💥 Terry coordination failed: {e}", exc_info=True)
            raise

    async def _handle_stick_feedback(self, message: AgentMessage) -> None:
        """Handle AGENT_FEEDBACK from The Stick"""
        feedback = message.payload
        feedback_type = feedback.get('feedback_type', 'unknown')
        resource_type = feedback.get('resource_type', 'unknown')
        data = feedback.get('data', {})

        logger.info(f"🐌📏 Feedback from The Stick: type={feedback_type}, resource={resource_type}")

        if feedback_type == 'action_effectiveness':
            quality = data.get('quality', 'unknown')
            logger.info(f"🐌📊 Action effectiveness feedback: {quality}")

    async def _handle_emergency(self, message: AgentMessage) -> None:
        """Handle emergency messages"""
        emergency_type = message.payload.get('emergency_type', 'unknown')
        logger.warning(f"🐌🚨 EMERGENCY: {emergency_type} from {message.from_agent}")

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

    async def broadcast_shell_spin(
        self,
        reason: str,
        missing_metrics: list,
        invalid_metrics: list,
        spin_count: int
    ):
        """Broadcast shell spin incident to other agents"""
        if not self._comm_hub:
            return

        try:
            await self._comm_hub.make_decision(
                decision_type="shell_spin_incident",
                input_data={
                    "missing_metrics": missing_metrics,
                    "invalid_metrics": invalid_metrics,
                    "reason": reason,
                    "total_spins": spin_count
                },
                output_data={},
                confidence=1.0,
                reasoning=f"Shell spinning due to: {reason}"
            )

            await self._comm_hub.broadcast_message(
                message_type=MessageType.SYSTEM_EVENT,
                payload={
                    "event_type": "shell_spin",
                    "reason": reason,
                    "missing_metrics": missing_metrics,
                    "invalid_metrics": invalid_metrics,
                    "spin_count": spin_count
                },
                priority=Priority.NORMAL
            )
            logger.info("🐌💫 Shell spin broadcast to rebellion")
        except Exception as e:
            logger.error(f"❌ Error broadcasting shell spin: {e}")

    async def _report_to_vic20(
        self, resource_type: str, action: str,
        result: Dict[str, Any], followed_recommendation: bool
    ):
        """Report action result back to VIC-20"""
        try:
            await self._comm_hub.broadcast_message(
                message_type=MessageType.ACTION_REPORT,
                payload={
                    'from_agent': 'meth_snail',
                    'resource_type': resource_type,
                    'action': action,
                    'result': result,
                    'followed_recommendation': followed_recommendation,
                    'terry_says': (
                        'I WAS FASTER!' if not followed_recommendation
                        else 'Okay, VIC-20 was right this time'
                    ),
                    'override_count': self.personality.total_overrides,
                    'success_rate': self.personality.override_success_rate
                },
                priority=Priority.NORMAL
            )
        except Exception as e:
            logger.error(f"🐌💥 Error reporting to VIC-20: {e}")

    async def _cc_the_stick(
        self, decision_type: str, resource_type: str,
        action: str, result: Dict[str, Any], followed_vic20: bool
    ):
        """CC The Stick on specialist action"""
        try:
            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': decision_type,
                    'from_agent': 'meth_snail',
                    'resource_type': resource_type,
                    'action': action,
                    'result': result,
                    'followed_vic20': followed_vic20,
                    'override_count': self.personality.total_overrides,
                    'success_rate': self.personality.override_success_rate,
                    'timestamp': asyncio.get_event_loop().time()
                },
                priority=Priority.NORMAL
            )
        except Exception as e:
            logger.error(f"🐌💥 Error CC'ing The Stick: {e}")

    async def _write_action_result(
        self, resource_type: str, action: str,
        result: Dict[str, Any], followed_vic20: bool, severity: str
    ):
        """Write action result to database"""
        try:
            if not self.personality.db_integration:
                logger.warning("🐌⚠️ Database integration not available")
                return

            await self.personality.db_integration.store_decision_dict(
                user_id=self.orchestrator.user_id,
                decision_data={
                    'decision_type': 'specialist_action',
                    'resource_type': resource_type,
                    'action': action,
                    'followed_vic20': followed_vic20,
                    'result': result,
                    'severity': severity,
                    'override_count': self.personality.total_overrides,
                    'success_rate': self.personality.override_success_rate
                }
            )
            logger.info("🐌💾 Action result written to PostgreSQL")
        except Exception as e:
            logger.error(f"🐌💥 Error writing action result: {e}", exc_info=True)

    async def _coordination_capability(
        self, resource_type: CoordResourceType, current_value: float
    ) -> Optional[AgentCapability]:
        """Terry's coordination capability for Week 4 system"""
        if resource_type != CoordResourceType.MEMORY:
            return None

        base_improvement = 20.0

        if self.personality.override_success_rate > 0.7:
            confidence = 0.7
            estimated_improvement = base_improvement * 1.2
        elif self.personality.override_success_rate > 0.5:
            confidence = 0.5
            estimated_improvement = base_improvement
        else:
            confidence = 0.3
            estimated_improvement = base_improvement * 0.8

        if self.personality.energy_drinks_today > 3:
            confidence *= 1.2

        return AgentCapability(
            agent_name="meth_snail",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=min(confidence, 1.0),
            estimated_duration=1.0,
            action_name="aggressive_cache_clear"
        )

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub"""
        if not self._comm_hub:
            return {"distributed_enabled": False}

        state = self._comm_hub.get_state()
        if not state:
            raise RuntimeError("💥 FATAL: meth_snail state is None")

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
            "resource_monitoring_active": False
        }
