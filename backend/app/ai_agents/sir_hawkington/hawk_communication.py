"""
Sir Hawkington — Communication Layer
======================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Resource monitor wiring (Hawk is the ONLY system monitor)
- Message handler registration
- Sending TRIAGE_ALERT to VIC-20
- Sending DECISION_LOG to The Stick
- Human notification on catastrophic data failure

Uses AgentCommunicationHub from shared infrastructure (composition, not inheritance).

Mirrors the structure of meth_snail/terry_communication.py.
"""

import asyncio
import logging
import socket
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..distributed.communication import AgentCommunicationHub
from ..distributed.message_protocol import AgentMessage, MessageType, Priority
from ..distributed.coordination import get_coordination_manager
from ..distributed.alert_escalation import get_escalation_manager
from ..distributed.event_logger import log_agent_startup
from .energy_drink_authorization import HawkEnergyDrinkAuthorizer

logger = logging.getLogger("SirHawkington.Communication")


class HawkCommunication:
    """
    Sir Hawkington's communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Wires the ResourceMonitor so Hawk receives system alerts.
    Routes ML pipeline results to VIC-20 and The Stick.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality:  HawkPersonalityState instance
            websocket:    HawkWebSocket instance
            orchestrator: HawkOrchestrator instance
        """
        self.personality  = personality
        self.websocket    = websocket
        self.orchestrator = orchestrator

        self.agent_name     = "sir_hawkington"
        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._resource_monitor = None
        self._heartbeat_task   = None
        self._agent_manager    = None   # Set by DistributedAgentManager after creation

        self.coordination_manager = None
        self.escalation_manager   = None

        self.energy_drink_authorizer = HawkEnergyDrinkAuthorizer()

    @property
    def comm_hub(self) -> Optional[AgentCommunicationHub]:
        return self._comm_hub

    @property
    def is_distributed(self) -> bool:
        return self._comm_hub is not None

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    async def initialize(self, redis_client):
        """
        Initialize communication: Redis, ResourceMonitor, message bus, subscriptions.

        Called by HawkingtonAgent.initialize().
        """
        # Create and initialize communication hub
        self._comm_hub = AgentCommunicationHub(
            redis_client=redis_client,
            agent_name=self.agent_name,
            agent_role="triage_commander",
            personality_traits=self.personality.personality_traits,
        )
        await self._comm_hub.initialize()

        # Wire comm_hub into orchestrator for downstream use
        self.orchestrator._comm_hub_ref = self._comm_hub

        # Set personality traits in Redis state
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
        self.escalation_manager   = get_escalation_manager()

        # Register coordination capability
        self.coordination_manager.register_agent_capability(
            "sir_hawkington",
            self._coordination_capability,
        )

        # Subscribe to message types
        self._comm_hub.message_bus.register_handler(
            MessageType.COORDINATION_REQUEST,
            self._handle_coordination_request,
        )
        self._comm_hub.message_bus.register_handler(
            MessageType.EMERGENCY,
            self._handle_emergency,
        )
        self._comm_hub.message_bus.register_handler(
            MessageType.AGENT_QUERY,
            self._handle_agent_query,
        )
        self._comm_hub.message_bus.register_handler(
            MessageType.AGENT_FEEDBACK,
            self._handle_stick_feedback,
        )

        # Wire ResourceMonitor — Hawk is the ONLY system monitor
        await self._initialize_resource_monitor()

        # Log startup
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": self.personality.personality_traits,
                "resource_thresholds": {
                    str(k): v
                    for k, v in self.personality.resource_thresholds.items()
                },
            },
        )

        logger.info("🧐📡 Sir Hawkington communication layer initialized")
        logger.info("🧐🎯 Triage commander ONLINE — Aristocratic standards MAINTAINED")

    async def _initialize_resource_monitor(self):
        """
        Initialize the ResourceMonitor and register the alert callback.

        Hawk is the sole system monitor. He watches everything.
        """
        try:
            from app.optimization.resource_monitor import ResourceMonitor, ResourceType

            self._resource_monitor = ResourceMonitor()
            await self._resource_monitor.initialize()

            # Register alert thresholds from personality state
            for resource_type, threshold in self.personality.resource_thresholds.items():
                self._resource_monitor.set_threshold(resource_type, threshold)

            # Register the callback that feeds alerts into the ML pipeline
            self._resource_monitor.register_alert_callback(self._handle_resource_alert)

            # Start the monitoring loop so thresholds are actually checked
            self._monitoring_task = asyncio.create_task(self._resource_monitor.start_monitoring())

            logger.info("🧐📊 ResourceMonitor initialized — Hawk watches ALL resources")

        except Exception as e:
            logger.error(f"🧐💥 ResourceMonitor initialization failed: {e}", exc_info=True)

    # =========================================================================
    # SHUTDOWN
    # =========================================================================

    async def shutdown(self):
        """Shutdown communication cleanly."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._resource_monitor:
            await self._resource_monitor.stop_monitoring()

        if self._comm_hub:
            await self._comm_hub.shutdown()

        logger.info("🧐🛑 Sir Hawkington communication layer shut down")

    # =========================================================================
    # HEARTBEAT
    # =========================================================================

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
                logger.error(f"🧐💥 Heartbeat error: {e}")

    # =========================================================================
    # RESOURCE ALERT ENTRY POINT
    # =========================================================================

    async def _handle_resource_alert(self, alert) -> None:
        """
        Entry point for ResourceMonitor alerts.

        This is the top of the entire hierarchy.
        Hawk receives raw resource alerts, runs the ML pipeline,
        then routes results to VIC-20 or The Stick accordingly.

        Args:
            alert: ResourceAlert from ResourceMonitor
        """
        # Build payload from alert
        resource_type = getattr(alert, 'resource_type', None) or alert.payload.get('resource_type', 'unknown')
        current_value = getattr(alert, 'current_value', None) or alert.payload.get('current_value', 0.0)
        threshold     = getattr(alert, 'threshold', None)     or alert.payload.get('threshold', 0.0)
        severity      = getattr(alert, 'severity', None)      or alert.payload.get('severity', 'unknown')

        # Check cooldown — suppress frontend spam
        should_emit, alert_state = self.personality.should_emit_alert(resource_type, severity)

        import uuid
        triage_alert_id = str(uuid.uuid4())

        alert_payload = {
            'resource_type':   resource_type,
            'current_value':   current_value,
            'threshold':       threshold,
            'severity':        severity,
            'triage_alert_id': triage_alert_id,
            'alert_state':     alert_state,
            'full_metrics':    self._resource_monitor.last_metrics if self._resource_monitor else {},
        }

        # Run the ML pipeline
        result = await self.orchestrator.run_pipeline(alert_payload)

        if result is None:
            logger.error(f"🧐💥 Pipeline returned no result for {resource_type}")
            return

        # Emit to frontend (always, subject to cooldown)
        if should_emit:
            await self.websocket.emit_decision(result)
            await self.websocket.emit_insight(
                action=f"{result['action'].action_type}_{resource_type}",
                reasoning=result['reasoning_summary'],
                context={
                    'resource_type': resource_type,
                    'target_agent':  result.get('target_agent'),
                    'severity':      severity,
                    'alert_state':   alert_state,
                },
            )

        # Route result to VIC-20 or The Stick
        if result['should_escalate']:
            await self._escalate_to_vic20(result)
        else:
            await self._log_to_stick(result)

    # =========================================================================
    # ROUTING
    # =========================================================================

    async def _escalate_to_vic20(self, result: Dict[str, Any]) -> None:
        """
        Send TRIAGE_ALERT to VIC-20 for coordination.

        Single-agent coordination → VIC20_COORDINATION
        Multi-agent emergency     → VIC20_EMERGENCY (monocle yeet)
        """
        if not self._comm_hub:
            return

        priority_map = {
            'critical': Priority.CRITICAL,
            'high':     Priority.HIGH,
            'normal':   Priority.NORMAL,
            'low':      Priority.LOW,
        }
        priority = priority_map.get(result.get('priority', 'normal'), Priority.NORMAL)

        is_emergency = result.get('priority') == 'critical'

        payload = {
            'triage_alert_id': result['triage_alert_id'],
            'resource_type':   result['resource_type'],
            'current_value':   result['current_value'],
            'threshold':       result['threshold'],
            'severity':        result['severity'],
            'target_agent':    result['target_agent'],
            'confidence':      result['confidence'],
            'reasoning':       result['reasoning_summary'],
            'monocle_state':   result['monocle_state'],
            'earl_grey':       result['earl_grey'],
            'full_metrics':    result['full_metrics'],
            'emergency':       is_emergency,
        }

        await self._comm_hub.message_bus.send_to_agent(
            to_agent='vic_20_sage',
            message_type=MessageType.TRIAGE_ALERT,
            payload=payload,
            priority=priority,
        )

        # CC The Stick on everything
        await self._log_to_stick(result)

        logger.info(
            f"🧐📨 TRIAGE_ALERT sent to VIC-20: "
            f"resource={result['resource_type']}, "
            f"target={result['target_agent']}, "
            f"emergency={is_emergency}"
        )

    async def _log_to_stick(self, result: Dict[str, Any]) -> None:
        """
        Send DECISION_LOG to The Stick.
        Every triage decision — escalation or dismiss — gets logged.
        """
        if not self._comm_hub:
            return

        try:
            await self._comm_hub.message_bus.send_to_agent(
                to_agent='the_stick',
                message_type=MessageType.DECISION_LOG,
                payload={
                    'agent':          'sir_hawkington',
                    'decision_type':  'triage',
                    'resource_type':  result['resource_type'],
                    'severity':       result['severity'],
                    'action_taken':   result['action'].action_type,
                    'should_escalate': result['should_escalate'],
                    'confidence':     result['confidence'],
                    'monocle_state':  result['monocle_state'],
                    'earl_grey':      result['earl_grey'],
                    'reasoning':      result['reasoning_summary'],
                },
                priority=Priority.LOW,
            )
        except Exception as e:
            logger.error(f"🧐💥 Failed to log to Stick: {e}")

    async def _notify_human(self, reason: str, resource_type: str) -> None:
        """
        Send human-in-the-loop notification for catastrophic data failures.

        Called when incoming data is missing/empty — the system itself may be broken.
        """
        logger.critical(
            f"🧐🚨 HUMAN NOTIFICATION REQUIRED — {reason} "
            f"[resource={resource_type}] "
            f"Data pipeline may be broken. Manual inspection required."
        )
        # TODO: wire to actual notification service (email, PagerDuty, etc.)
        # For now, critical log is the notification mechanism

    # =========================================================================
    # MESSAGE HANDLERS
    # =========================================================================

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle COORDINATION_REQUEST from VIC-20 with aristocratic grace.

        Typically VIC-20 routing CPU throttling recommendations back to Hawk.
        """
        message_data     = message.payload
        coordination_type = message_data.get('coordination_type', 'unknown')

        if coordination_type == 'resource_recommendation':
            from ..distributed.system_actions import SystemActions

            recommendation = message_data.get('recommendation', {})
            logger.info(
                f"🧐 *adjusts monocle* VIC-20's recommendation has merit... "
                f"Suggested action: {recommendation.get('suggested_action', 'unknown')}"
            )

            throttle_result = await SystemActions.throttle_cpu_intensive_tasks()

            if throttle_result['success']:
                logger.info(
                    f"🧐✅ System throttled with DISTINCTION! "
                    f"CPU: {throttle_result['cpu_before']:.1f}% → "
                    f"{throttle_result['cpu_after']:.1f}%"
                )
            else:
                logger.warning("🧐⚠️ Throttling attempt yielded unsatisfactory results")

    async def _handle_emergency(self, message: AgentMessage) -> None:
        """Handle emergency messages from other agents."""
        emergency_type = message.payload.get('emergency_type', 'unknown')
        logger.critical(
            f"🧐🚨 EMERGENCY received from {message.from_agent}: {emergency_type}"
        )

    async def _handle_agent_query(self, message: AgentMessage) -> None:
        """Handle queries from other agents — currently energy drink auth from Terry."""
        request_type = message.payload.get('request_type', 'unknown')
        if request_type == 'energy_drink_authorization':
            await self._handle_energy_drink_request(message)
        else:
            logger.warning(f"🧐⚠️ Unknown agent query type: {request_type}")

    async def _handle_energy_drink_request(self, message: AgentMessage) -> None:
        """
        Handle energy drink authorization request from Terry.

        Real cross-agent interaction: Terry requests, Hawk approves or vetoes.
        """
        message_data  = message.payload
        request_id    = message_data.get('request_id')
        reply_channel = message_data.get('reply_channel')
        agent         = message_data.get('agent', 'unknown')

        logger.info(
            f"🧐☕ Received energy drink request from {agent}:\n"
            f"   Action: {message_data.get('action')}\n"
            f"   Reason: {message_data.get('reason')}\n"
            f"   Current consumption: {message_data.get('energy_drinks_consumed_today', 0)}\n"
            f"   *adjusts monocle thoughtfully*"
        )

        from app.ai_agents.meth_snail.data_types import EnergyDrinkRequest, EnergyDrinkType
        from datetime import datetime, timezone

        request = EnergyDrinkRequest(
            user_id=message_data.get('user_id', 'system'),
            energy_drink_type=EnergyDrinkType.ENERGY_DRINK,
            caffeine_mg=160.0,
            consumption_reason=message_data.get('reason', 'unknown'),
            current_jitter_level=message_data.get('current_jitter_level', 0.5),
            energy_drinks_consumed_today=message_data.get('energy_drinks_consumed_today', 0),
            time_since_last_drink_minutes=message_data.get('time_since_last_drink_minutes'),
            optimization_urgency=message_data.get('optimization_urgency', 'immediate'),
            timestamp=datetime.now(timezone.utc)
        )

        authorization = await self.energy_drink_authorizer.authorize_energy_drink(request)

        if reply_channel and self._comm_hub:
            try:
                monocle_state = self.personality.current_monocle_state.value
                response_msg = AgentMessage(
                    message_type=MessageType.AGENT_RESPONSE,
                    from_agent=self.agent_name,
                    to_agent=agent,
                    priority=Priority.HIGH,
                    payload={
                        'request_id':             request_id,
                        'approved':               authorization.authorized,
                        'authorized_by':          authorization.authorized_by,
                        'commentary':             authorization.authorization_notes,
                        'recommended_caffeine_mg': authorization.recommended_caffeine_mg,
                        'recommended_type':       authorization.recommended_type.value if authorization.recommended_type else 'water',
                        'safety_warnings':        authorization.safety_warnings,
                        'monocle_state':          monocle_state,
                        'timestamp':              authorization.timestamp.isoformat()
                    }
                )
                await self._comm_hub.message_bus.publish(
                    response_msg,
                    channel=reply_channel,
                )
                logger.info(
                    f"🧐✅ Response sent to {agent} via {reply_channel}:\n"
                    f"   Decision: {'APPROVED' if authorization.authorized else 'DENIED'}\n"
                    f"   Commentary: {authorization.authorization_notes}"
                )
            except Exception as e:
                logger.error(f"🧐💥 Failed to send energy drink response: {e}", exc_info=True)
        else:
            logger.warning(f"🧐⚠️ No reply channel or comm_hub — cannot respond to Terry")

    async def _handle_stick_feedback(self, message: AgentMessage) -> None:
        """The Stick says adjust thresholds. We listen."""
        from app.optimization.resource_monitor import ResourceType

        feedback      = message.payload
        feedback_type = feedback.get('feedback_type')

        if feedback_type == 'threshold_adjustment':
            resource_type = feedback.get('resource_type')
            data      = feedback.get('data', {})
            direction = data.get('direction')
            step      = data.get('step', 5.0)
            floor     = data.get('floor', 50.0)
            ceiling   = data.get('ceiling', 95.0)

            if resource_type and direction:
                try:
                    rt  = ResourceType(resource_type)
                    old = self.personality.resource_thresholds.get(rt)
                    if old is not None:
                        if direction == 'raise':
                            new = min(ceiling, old + step)
                        elif direction == 'lower':
                            new = max(floor, old - step)
                        else:
                            logger.warning(f"🧐❓ Unknown threshold direction: {direction}")
                            return

                        self.personality.resource_thresholds[rt] = new

                        # Also update the live ResourceMonitor if it's running
                        if self._resource_monitor:
                            self._resource_monitor.set_threshold(rt, new)

                        logger.info(
                            f"🧐📏 Threshold adjusted by The Stick: "
                            f"{resource_type} {old} → {new} "
                            f"(direction={direction}, step={step})"
                        )
                except ValueError:
                    logger.warning(f"🧐⚠️ Unknown resource type in feedback: {resource_type}")

    # =========================================================================
    # CAPABILITY REGISTRATION
    # =========================================================================

    def _coordination_capability(self, resource_type, current_value, threshold):
        """Register Sir Hawkington's coordination capability with the manager."""
        from ..distributed.coordination import AgentCapability, ResourceType as CoordResourceType
        return AgentCapability(
            agent_name="sir_hawkington",
            resource_type=resource_type,
            estimated_improvement=0.3,
            confidence=0.8,
            estimated_duration=2.0,
            action_name="aristocratic_throttle",
        )

    # =========================================================================
    # STATE
    # =========================================================================

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub."""
        if not self._comm_hub:
            return {"distributed_enabled": False}

        state = self._comm_hub.get_state()
        if not state:
            raise RuntimeError("💥 FATAL: sir_hawkington state is None")

        return {
            "distributed_enabled":          True,
            "agent_name":                   state.agent_name,
            "health":                       state.health.value,
            "total_decisions":              state.total_decisions,
            "total_messages_sent":          state.total_messages_sent,
            "total_messages_received":      state.total_messages_received,
            "uptime_seconds":               state.calculate_uptime(),
            "restart_count":                state.restart_count,
            "personality_traits":           state.personality_traits or {},
            "last_heartbeat":               state.last_heartbeat,
            "resource_monitoring_enabled":  True,
            "resource_monitoring_active":   self._resource_monitor is not None,
        }
