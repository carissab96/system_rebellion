"""
Quantum Shadow People — Communication Layer
==============================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Message handler registration (COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY)
- Sending ACTION_OUTCOME to VIC-20
- Broadcasting DECISION_LOG to The Stick
- Heartbeat loop
- Week 4 coordination capability

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

from .qsp_data_types import ParanoiaLevel

logger = logging.getLogger("QSP.Communication")


class QSPCommunication:
    """
    Quantum Shadow People communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Registers QSP-specific message handlers.
    Routes ML pipeline results to other agents and frontend.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality: QSPPersonalityState instance
            websocket: QSPWebSocket instance
            orchestrator: QSPOrchestrator instance
        """
        self.personality = personality
        self.websocket = websocket
        self.orchestrator = orchestrator

        self.agent_name = "quantum_shadow_people"
        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._agent_manager = None  # Set by DistributedAgentManager

        # Week 4 system integration
        self.coordination_manager = None
        self.verification_manager = None

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
            agent_role="network_specialists",
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

        # Register QSP's coordination capability
        self.coordination_manager.register_agent_capability(
            "quantum_shadow_people",
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
            logger.error(f"👻💥 Failed to register AGENT_FEEDBACK handler: {e}")

        self._comm_hub.message_bus.register_handler(
            MessageType.EMERGENCY,
            self._handle_emergency
        )

        # Initialize database integration
        if self.personality.db_getter:
            try:
                await self.personality.initialize_database()
                logger.info(
                    "👻💾 Database integration initialized — "
                    "Paranoid records enabled!"
                )
            except Exception as e:
                logger.error(
                    f"👻💥 Failed to initialize database: {e}", exc_info=True
                )

        # Log startup
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": self.personality.personality_traits,
                "resource_thresholds": self.personality.resource_thresholds,
            }
        )

        logger.info("👻🔮 QSP communication layer initialized")
        logger.info(
            "👻📡 Subscribed to COORDINATION_REQUEST, AGENT_FEEDBACK, EMERGENCY"
        )
        logger.info("👻🔒 Paranoid coordination protocols active — Trust no one!")

    async def shutdown(self):
        """Shutdown communication cleanly."""
        if hasattr(self, '_heartbeat_task'):
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._comm_hub:
            await self._comm_hub.shutdown()

        logger.info("👻🛑 QSP communication layer shut down")

    async def _heartbeat_loop(self, interval: int):
        """Send periodic heartbeats."""
        while True:
            try:
                await asyncio.sleep(interval)
                if self._comm_hub:
                    await self._comm_hub.send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"👻💥 Heartbeat error: {e}")

    # === MESSAGE HANDLERS ===

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle COORDINATION_REQUEST from VIC-20.

        Communication receives the message, passes it to the orchestrator
        for ML pipeline processing, then handles all inter-agent messaging.
        """
        payload = message.payload
        resource_type = payload.get('resource_type', 'unknown')
        severity = payload.get('severity', 'unknown')
        recommendation = payload.get('recommendation', {})
        current_value = payload.get('current_value', 0)

        logger.info(
            f"👻📬 COORDINATION REQUEST from VIC-20: "
            f"{resource_type} at {current_value:.1f}% — "
            f"VIC-20 suggests: {recommendation.get('action', 'unknown')}"
        )

        try:
            # Run the ML pipeline through the orchestrator
            result = await self.orchestrator.run_pipeline(payload)

            if result is None or not result.get("success"):
                logger.error("👻💥 Orchestrator returned failure or no result")
                return

            # Emit to frontend via websocket layer
            await self.websocket.emit_decision(result)

            network_result = result["network_result"]
            decision = result["decision"]

            if network_result["success"]:
                await self.websocket.emit_insight(
                    action="security_scan_success",
                    reasoning=(
                        f"Quantum security protocol executed: "
                        f"{result['reasoning'].threat_classification}"
                    ),
                    context={
                        "success": True,
                        "quantum_state": decision.quantum_state,
                        "threat_level": result["context"].threat_level,
                    }
                )

            # Send ACTION_OUTCOME to VIC-20
            triage_alert_id = payload.get('triage_alert_id')
            improvement_pct = float(network_result.get('improvement', 0.0)) * 100.0
            await self._comm_hub.message_bus.send_to_agent(
                to_agent='vic_20_sage',
                message_type=MessageType.ACTION_OUTCOME,
                payload={
                    'triage_alert_id': triage_alert_id,
                    'agent_name': 'quantum_shadow_people',
                    'action_taken': decision.action_type,
                    'recommended_action': recommendation.get('action', 'unknown'),
                    'success': network_result['success'],
                    'improvement': improvement_pct,
                    'resource_type': resource_type,
                    'severity': severity,
                    'hawk_severity': payload.get('hawk_severity', severity),
                    'hawk_confidence': payload.get('triage_confidence', 0.0),
                    'followed_recommendation': True,
                    'metrics_before': result.get('metrics_before', {}),
                    'metrics_after': result.get('metrics_after', {}),
                },
                priority=Priority.NORMAL,
            )
            logger.info(
                f"👻📤 ACTION_OUTCOME sent to VIC-20: "
                f"action={decision.action_type}, "
                f"success={network_result['success']}, "
                f"improvement={improvement_pct:.1f}%"
            )

            # CC The Stick — send DECISION_LOG
            await self._log_to_stick(result)

        except Exception as e:
            logger.error(
                f"👻💥 QSP coordination failed: {e}", exc_info=True
            )
            from app.ai_agents.exceptions import MLPipelineFailure
            raise MLPipelineFailure(
                f"QSP ML pipeline failed: {e}"
            ) from e

    async def _handle_stick_feedback(self, message: AgentMessage) -> None:
        """
        Handle AGENT_FEEDBACK from The Stick.

        QSP is paranoid — even feedback from The Stick is treated with suspicion.
        """
        feedback = message.payload
        feedback_type = feedback.get('feedback_type', 'unknown')
        resource_type = feedback.get('resource_type', 'unknown')
        data = feedback.get('data', {})

        logger.info(
            f"👻📏 Feedback from The Stick: type={feedback_type}, "
            f"resource={resource_type} *quantum suspicion activated*"
        )

        if feedback_type == 'routing_quality':
            quality = data.get('quality', 'unknown')
            logger.info(
                f"👻📊 Routing quality feedback: {quality} "
                f"*adjusting quantum paranoia levels accordingly*"
            )
            if quality == 'poor':
                self.personality.paranoia_level = ParanoiaLevel.ELEVATED
                logger.warning(
                    "👻⚠️ Paranoia elevated due to poor routing quality"
                )

    async def _handle_emergency(self, message: AgentMessage) -> None:
        """Handle emergency messages."""
        emergency_type = message.payload.get('emergency_type', 'unknown')
        logger.warning(
            f"👻🚨 EMERGENCY: {emergency_type} from {message.from_agent}"
        )

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

    async def _log_to_stick(self, result: Dict[str, Any]) -> None:
        """Send DECISION_LOG to The Stick."""
        try:
            decision = result["decision"]
            network_result = result["network_result"]
            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': 'specialist_action',
                    'from_agent': 'quantum_shadow_people',
                    'resource_type': result.get('resource_type', 'network'),
                    'action': decision.action_type,
                    'success': network_result['success'],
                    'improvement': network_result['improvement'],
                    'metrics_before': result.get('metrics_before', {}),
                    'metrics_after': result.get('metrics_after', {}),
                    'paranoia_level': self.personality.paranoia_level.value,
                    'quantum_state': decision.quantum_state,
                },
                priority=Priority.NORMAL,
            )
            logger.info("👻📋 DECISION_LOG sent to The Stick")
        except Exception as e:
            logger.error(f"👻💥 Error logging to The Stick: {e}")

    # === COORDINATION CAPABILITY ===

    async def _coordination_capability(
        self, resource_type: CoordResourceType, current_value: float
    ) -> Optional[AgentCapability]:
        """
        QSP's paranoid coordination capability for Week 4 system.

        Network security is NOT negotiable. QSP is ALWAYS suspicious.
        Capability depends on quantum phase state and paranoia level!
        """
        if resource_type != CoordResourceType.NETWORK:
            return None

        p = self.personality

        # Base improvement estimate
        base_improvement = 12.0

        # Adjust based on paranoia level
        paranoia_multiplier = {
            ParanoiaLevel.HEALTHY: 1.0,
            ParanoiaLevel.ELEVATED: 1.2,
            ParanoiaLevel.MAXIMUM: 1.5,
            ParanoiaLevel.JUSTIFIED: 2.0,
        }
        multiplier = paranoia_multiplier.get(p.paranoia_level, 1.0)
        estimated_improvement = base_improvement * multiplier

        # Confidence — always suspicious
        base_confidence = 0.5

        if p.tequila_shots_today > 5:
            base_confidence *= 0.8
            logger.warning(
                f"👻🍸 {p.tequila_shots_today} tequila shots — "
                "MAXIMUM PARANOIA ACHIEVED!"
            )
        elif p.tequila_shots_today > 3:
            base_confidence *= 0.9

        if p.threats_detected > 0:
            threat_boost = min(0.3, p.threats_detected * 0.1)
            base_confidence += threat_boost

        confidence = min(base_confidence, 0.9)

        logger.info(
            f"👻🔒 Paranoid capability: {estimated_improvement:.1f}% improvement "
            f"(Paranoia: {p.paranoia_level.value}, "
            f"Confidence: {confidence:.0%}, "
            f"Threats: {p.threats_detected})"
        )

        return AgentCapability(
            agent_name="quantum_shadow_people",
            resource_type=resource_type,
            estimated_improvement=estimated_improvement,
            confidence=confidence,
            estimated_duration=4.0,
            action_name="paranoid_network_lockdown"
        )

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub."""
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
