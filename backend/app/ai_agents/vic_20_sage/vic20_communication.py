"""
VIC-20 Sage — Communication Layer
====================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Message handler registration (TRIAGE_ALERT, ACTION_REPORT, ACTION_OUTCOME, AGENT_FEEDBACK)
- Outbound messaging (send_to_agent, broadcast_to_agents)
- Bob mediation logic
- _cc_the_stick and _report_to_stick
- Heartbeat loop
- AgentCapability coordination registration

Extracted from distributed_vic20.py:
- initialize_distributed() (lines 123-199)
- _handle_triage_alert_from_hawk() (lines 217-224)
- _handle_coordination_request() (lines 201-215)
- _handle_action_report() (lines 396-453)
- _handle_action_outcome() (lines 455-513)
- _handle_stick_feedback() (lines 563-579)
- _report_to_stick() (lines 515-561)
- _cc_the_stick() (lines 745-774)
- _mediate_hamster_message() (lines 798-859)
- _translate_bob_message() (lines 861-884)
- _coordination_capability() (lines 776-796)
- _handle_resource_alert() (lines 943-999)
- _generate_and_broadcast_recommendations() (lines 1001-1070)
- analyze_metrics() (lines 886-941)

All payload keys preserved character-for-character.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from ..distributed.communication import AgentCommunicationHub
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
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
from ..distributed.resource_prediction import (
    get_resource_predictor,
    ResourceType as PredictionResourceType
)
from ..distributed.event_logger import log_agent_startup

logger = logging.getLogger("VIC20.Communication")


class VIC20Communication:
    """
    VIC-20 Sage communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Registers VIC-20-specific message handlers.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality: VIC20PersonalityState instance
            websocket: VIC20WebSocket instance
            orchestrator: VIC20Orchestrator instance
        """
        self.personality = personality
        self.websocket = websocket
        self.orchestrator = orchestrator

        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._shutdown = False

        logger.info("🖥️📡 VIC-20 Communication initialized")

    @property
    def comm_hub(self) -> Optional[AgentCommunicationHub]:
        return self._comm_hub

    @property
    def is_distributed(self) -> bool:
        return self._comm_hub is not None and self._comm_hub.is_connected

    async def initialize(self, redis_client) -> None:
        """
        Initialize communication: Redis, message bus, subscriptions.

        Reproduces distributed_vic20.py:123-199 (initialize_distributed).

        Args:
            redis_client: Connected Redis client
        """
        p = self.personality

        # 1. Create communication hub — NO resource monitoring for VIC-20
        self._comm_hub = AgentCommunicationHub(
            redis_client=redis_client,
            agent_name="vic_20_sage",
            agent_role="orchestrator",
            personality_traits=p.personality_traits
        )
        await self._comm_hub.initialize()

        # Pass comm_hub reference to orchestrator
        self.orchestrator._comm_hub_ref = self._comm_hub

        # 2. Initialize database integration
        await p.initialize_database()

        # 3. Initialize Week 4 systems
        p.coordination_manager = get_coordination_manager()
        p.escalation_manager = get_escalation_manager()
        p.resource_predictor = get_resource_predictor()

        # Register VIC-20's coordination capability
        p.coordination_manager.register_agent_capability(
            "vic_20_sage",
            self._coordination_capability
        )

        logger.info("🖥️🎯 Week 4 systems integrated - Coordination, Escalation, Prediction ONLINE!")

        # 4. Subscribe to TRIAGE_ALERT from Sir Hawkington
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.TRIAGE_ALERT,
                self._handle_triage_alert_from_hawk
            )
            logger.info("🖥️📡 VIC-20 subscribed to TRIAGE_ALERT from Sir Hawkington - Coordination ready!")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to triage alerts: {e}")

        # 5. Subscribe to ACTION_REPORT from specialists
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.ACTION_REPORT,
                self._handle_action_report
            )
            logger.info("🖥️📡 VIC-20 subscribed to ACTION_REPORT from specialists - Learning loop ready!")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to action reports: {e}")

        # 6. Subscribe to ACTION_OUTCOME
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.ACTION_OUTCOME,
                self._handle_action_outcome
            )
            logger.info("🖥️📡 VIC-20 subscribed to ACTION_OUTCOME")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to action outcomes: {e}")

        # 7. Subscribe to AGENT_FEEDBACK from The Stick
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.AGENT_FEEDBACK,
                self._handle_stick_feedback
            )
            logger.info("🖥️📡 VIC-20 subscribed to AGENT_FEEDBACK from The Stick")
        except Exception as e:
            logger.error(f"🖥️💥 Failed to subscribe to agent feedback: {e}")

        # Set personality traits in state
        state = self._comm_hub.get_state()
        if state:
            state.personality_traits = p.personality_traits
            await self._comm_hub.state_manager.save_state(state)

        # Update health
        from ..distributed.agent_state import AgentHealth
        await self._comm_hub.state_manager.update_health(AgentHealth.HEALTHY)

        # 8. Start heartbeat loop
        self._heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(interval=30)
        )

        # 9. Log startup
        await log_agent_startup("vic_20_sage", {
            "subscriptions": ["TRIAGE_ALERT", "ACTION_REPORT", "ACTION_OUTCOME", "AGENT_FEEDBACK"],
            "coordinator": True,
            "mediator": True,
        })

        logger.info(
            "🖥️✨ VIC-20 Sage's distributed consciousness initialized - "
            "ORCHESTRATION PROTOCOLS ACTIVE!"
        )
        logger.info("🖥️💡 Recommendation engine online - READY TO GUIDE AGENTS!")
        logger.info("🖥️🛡️ Bob mediation protocols active - STICK PROTECTION ENABLED!")
        logger.info("🖥️📊 Coordination stats tracking enabled - MEASURING PEACE AND DRAMA!")

    async def shutdown(self) -> None:
        """Shutdown communication cleanly."""
        self._shutdown = True
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        if self._comm_hub:
            await self._comm_hub.shutdown()
        logger.info("🖥️👋 VIC-20 Communication shutdown complete")

    async def _heartbeat_loop(self, interval: int) -> None:
        """Send periodic heartbeats."""
        while not self._shutdown:
            try:
                await asyncio.sleep(interval)
                if self._comm_hub:
                    await self._comm_hub.send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Heartbeat error: {e}")

    # ==================================================================
    # MESSAGE HANDLERS
    # ==================================================================

    async def _handle_triage_alert_from_hawk(self, message: AgentMessage) -> None:
        """
        PHASE 3: Handle TRIAGE_ALERT from Sir Hawkington.

        Routes through the unified ML pipeline.
        From distributed_vic20.py:217-224.
        """
        triage_alert_id = message.payload.get('triage_alert_id')
        triage_data = message.payload

        # Run the ML pipeline
        result = await self.orchestrator.run_pipeline(triage_data, triage_alert_id=triage_alert_id)

        if not result or not result.get('success'):
            return

        context = result['context']
        reasoning = result['reasoning']
        action = result['action']
        learning_record = result['learning_record']
        resource_type = triage_data.get('resource_type', 'unknown')
        severity = triage_data.get('severity', 'unknown')
        current_value = triage_data.get('current_value', 0)

        # BROADCAST TO FRONTEND
        await self.websocket.emit_decision(
            context=context,
            reasoning=reasoning,
            action=action,
            learning_record=learning_record,
        )

        # EXECUTE — send to specialist
        if action.action_type == 'route_to_specialist':
            from app.ai_agents.vic_20_sage.ML.execution_planner import VIC20ExecutionPlanner
            planner = VIC20ExecutionPlanner()
            coordination_request = planner.build_coordination_request(
                context=context,
                reasoning=reasoning,
                action=action,
                triage_data=triage_data,
                triage_alert_id=triage_alert_id,
            )

            await self._comm_hub.message_bus.send_to_agent(
                to_agent=action.target_specialist,
                message_type=MessageType.COORDINATION_REQUEST,
                payload=coordination_request,
                priority=Priority.HIGH if action.priority in ['high', 'critical'] else Priority.NORMAL
            )

            # Emit insight — EXACT keys from distributed_vic20.py:351-366
            await self.websocket.emit_insight(
                to_agent=action.target_specialist,
                action_name="coordinate_specialist",
                reasoning_text=reasoning.primary_reason,
                context_data={
                    "resource_type": resource_type,
                    "current_value": current_value,
                    "severity": severity,
                    "specialist": action.target_specialist,
                    "recommended_action": action.recommended_action,
                    "confidence": action.confidence,
                    "urgency": reasoning.urgency_level,
                    "triage_alert_id": triage_alert_id,
                }
            )

            # CC The Stick — EXACT keys from distributed_vic20.py:368-374
            await self._cc_the_stick(
                decision_type='coordination_v2',
                resource_type=resource_type,
                specialist=action.target_specialist,
                recommendation={'action': action.recommended_action, 'confidence': action.confidence},
                severity=severity
            )

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle coordination requests. VIC-20 rarely receives these.
        From distributed_vic20.py:201-215.
        """
        message_data = message.payload
        logger.info(f"🖥️📬 VIC-20 received coordination request: {message_data.get('coordination_type', 'unknown')}")
        logger.info("🖥️💭 As the coordinator, I typically SEND these, not receive them!")

    async def _handle_action_report(self, message: AgentMessage) -> None:
        """
        PHASE 4: Handle ACTION_REPORT from specialists.
        From distributed_vic20.py:396-453. Payload keys preserved exactly.
        """
        try:
            payload = message.payload
            from_agent = payload.get('from_agent', 'unknown')
            resource_type = payload.get('resource_type', 'unknown')
            action = payload.get('action', 'unknown')
            result = payload.get('result', {})
            followed_recommendation = payload.get('followed_recommendation', False)

            success = result.get('success', False) if isinstance(result, dict) else False
            outcome = result.get('outcome', 'unknown') if isinstance(result, dict) else str(result)

            logger.info(
                f"🖥️📨 ACTION_REPORT from {from_agent}: "
                f"action={action}, success={success}, followed_rec={followed_recommendation}"
            )

            # Update The Stick with outcome — EXACT payload keys
            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': 'coordination_outcome',
                    'from_agent': 'vic_20_sage',
                    'specialist': from_agent,
                    'resource_type': resource_type,
                    'action': action,
                    'outcome': outcome,
                    'success': success,
                    'followed_recommendation': followed_recommendation,
                    'result_details': result,
                    'timestamp': asyncio.get_event_loop().time()
                },
                priority=Priority.NORMAL
            )

            logger.info(
                f"🖥️📋 Outcome logged to The Stick: "
                f"{from_agent} {action} → {'✅ SUCCESS' if success else '❌ FAILED'}"
            )

        except Exception as e:
            logger.error(f"🖥️💥 Error handling action report: {e}", exc_info=True)

    async def _handle_action_outcome(self, message: AgentMessage) -> None:
        """
        Section 3.7: Handle ACTION_OUTCOME from a specialist.
        From distributed_vic20.py:455-513. Delegates to orchestrator and reports to Stick.
        """
        try:
            payload = message.payload
            triage_alert_id = payload.get('triage_alert_id', 'no_id')
            specialist_name = payload.get('agent_name', message.from_agent or 'unknown')
            action_taken = payload.get('action_taken', 'unknown')
            success = bool(payload.get('success', False))
            improvement = float(payload.get('improvement', 0.0))
            resource_type = payload.get('resource_type', 'unknown')
            severity = payload.get('severity', 'unknown')

            # Delegate learning update to orchestrator
            await self.orchestrator.handle_action_outcome(payload, message.from_agent)

            # Report full chain to The Stick — EXACT keys from distributed_vic20.py:515-561
            await self._report_to_stick(
                triage_alert_id=triage_alert_id,
                specialist_name=specialist_name,
                action_recommended=payload.get('recommended_action', 'unknown'),
                action_taken=action_taken,
                resource_type=resource_type,
                severity=severity,
                specialist_success=success,
                specialist_improvement=improvement,
                hawk_severity=payload.get('hawk_severity', severity),
                hawk_confidence=float(payload.get('hawk_confidence', 0.0)),
            )

        except Exception as e:
            logger.error(f"🖥️💥 Error handling action outcome: {e}", exc_info=True)

    async def _handle_stick_feedback(self, message: AgentMessage) -> None:
        """
        Section 4.5: Handle AGENT_FEEDBACK from The Stick.
        From distributed_vic20.py:563-579.
        """
        feedback = message.payload
        feedback_type = feedback.get('feedback_type', 'unknown')
        logger.info(f"🖥️📏 Feedback from The Stick: type={feedback_type}")

        if feedback_type == 'routing_quality':
            specialist = feedback.get('specialist')
            quality = feedback.get('quality', 'unknown')
            logger.info(
                f"🖥️📊 Routing quality feedback: {specialist} → {quality}"
            )

    # ==================================================================
    # OUTBOUND MESSAGING
    # ==================================================================

    async def _report_to_stick(
        self,
        triage_alert_id: str,
        specialist_name: str,
        action_recommended: str,
        action_taken: str,
        resource_type: str,
        severity: str,
        specialist_success: bool,
        specialist_improvement: float,
        hawk_severity: str = '',
        hawk_confidence: float = 0.0,
    ) -> None:
        """
        Section 3.7: Send CHAIN_OUTCOME to The Stick.
        From distributed_vic20.py:515-561. Payload keys EXACT.
        """
        routing_was_correct = action_recommended == action_taken
        recommendation_was_effective = specialist_success and specialist_improvement > 0

        await self._comm_hub.message_bus.send_to_agent(
            to_agent='the_stick',
            message_type=MessageType.CHAIN_OUTCOME,
            payload={
                'triage_alert_id': triage_alert_id,
                'specialist_name': specialist_name,
                'action_recommended': action_recommended,
                'action_taken': action_taken,
                'resource_type': resource_type,
                'severity': severity,
                'specialist_success': specialist_success,
                'specialist_improvement': specialist_improvement,
                'routing_was_correct': routing_was_correct,
                'recommendation_was_followed': action_recommended == action_taken,
                'recommendation_was_effective': recommendation_was_effective,
                'hawk_severity': hawk_severity,
                'hawk_confidence': hawk_confidence,
                'from_coordinator': 'vic_20_sage',
            },
            priority=Priority.NORMAL,
        )

        logger.info(
            f"🖥️📋 Chain outcome reported to The Stick: "
            f"{specialist_name} {action_taken} → "
            f"{'✅' if specialist_success else '❌'} "
            f"(improvement={specialist_improvement:.1f}%, routing_correct={routing_was_correct})"
        )

    async def _cc_the_stick(
        self,
        decision_type: str,
        resource_type: str,
        specialist: str,
        recommendation: Dict[str, Any],
        severity: str
    ) -> None:
        """
        PHASE 3: CC The Stick on coordination decision.
        From distributed_vic20.py:745-774. Payload keys EXACT.
        """
        try:
            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': decision_type,
                    'from_agent': 'vic_20_sage',
                    'resource_type': resource_type,
                    'specialist': specialist,
                    'recommendation': recommendation,
                    'severity': severity,
                    'timestamp': asyncio.get_event_loop().time()
                },
                priority=Priority.NORMAL
            )
            logger.debug("🖥️📋 Decision logged to The Stick")
        except Exception as e:
            logger.error(f"🖥️💥 Error CC'ing The Stick: {e}", exc_info=True)

    # ==================================================================
    # BOB MEDIATION — distributed_vic20.py:798-884
    # ==================================================================

    async def _mediate_hamster_message(self, message: AgentMessage) -> None:
        """
        Mediate hamster messages, especially Bob's.
        From distributed_vic20.py:798-859.
        """
        p = self.personality
        try:
            message_data = message.payload
            from_agent = message.from_agent
            message_content = message_data.get('content', '')

            is_bob_message = 'bob' in from_agent.lower() or 'bob' in message_content.lower()

            if is_bob_message:
                p.bob_mediation_count += 1

                anxiety_triggers = ['hold my beer', 'wild idea', 'emergency', 'fire', 'chaos']
                is_anxiety_inducing = any(trigger in message_content.lower() for trigger in anxiety_triggers)

                if is_anxiety_inducing:
                    mediated_message = self._translate_bob_message(message_content)

                    logger.info(
                        f"🖥️🛡️ VIC-20 mediating Bob's message for The Stick: "
                        f"'{message_content[:50]}...' → '{mediated_message[:50]}...'"
                    )

                    await self._comm_hub.broadcast_message(
                        message_type=MessageType.SYSTEM_EVENT,
                        payload={
                            'source': 'hamsters',
                            'mediated_by': 'vic_20_sage',
                            'content': mediated_message,
                            'original_anxiety_level': 'high',
                            'mediated_anxiety_level': 'moderate'
                        },
                        priority=Priority.NORMAL
                    )

                    p.stick_anxiety_prevented += 1
                    p.bob_messages_filtered.append({
                        'timestamp': asyncio.get_event_loop().time(),
                        'original': message_content,
                        'mediated': mediated_message
                    })

                    logger.info(
                        f"🖥️🛡️ The Stick protected from Bob's chaos! "
                        f"(Total prevented: {p.stick_anxiety_prevented})"
                    )
                    return

            # Not Bob or not anxiety-inducing — pass through
            await self._update_stick_coordination(
                severity='normal',
                routing='hamster_activity',
                target_agents=['hamsters']
            )

        except Exception as e:
            logger.error(f"🖥️💥 Error mediating hamster message: {e}", exc_info=True)

    def _translate_bob_message(self, original_message: str) -> str:
        """
        Translate Bob's chaotic messages into calmer language.
        From distributed_vic20.py:861-884. Translations EXACT.
        """
        translations = {
            'hold my beer': 'proceeding with caution',
            'wild idea': 'alternative approach',
            'emergency': 'situation requiring attention',
            'fire': 'thermal event',
            'chaos': 'dynamic conditions',
            'BEER': 'operational fuel',
            'duct tape': 'infrastructure reinforcement',
            'full redneck': 'comprehensive response protocol'
        }

        mediated = original_message
        for trigger, replacement in translations.items():
            mediated = mediated.replace(trigger, replacement)
            mediated = mediated.replace(trigger.upper(), replacement.upper())

        return mediated

    async def _update_stick_coordination(
        self,
        severity: str,
        routing: str,
        target_agents: list,
    ) -> None:
        """Helper to update The Stick for non-critical events."""
        try:
            if self._comm_hub:
                await self._comm_hub.broadcast_message(
                    message_type=MessageType.DECISION_LOG,
                    payload={
                        'decision_type': 'observation',
                        'from_agent': 'vic_20_sage',
                        'severity': severity,
                        'routing': routing,
                        'target_agents': target_agents,
                        'timestamp': asyncio.get_event_loop().time()
                    },
                    priority=Priority.LOW
                )
        except Exception as e:
            logger.debug(f"Could not update stick coordination: {e}")

    # ==================================================================
    # RESOURCE ALERT HANDLING — distributed_vic20.py:943-1070
    # ==================================================================

    async def _handle_resource_alert(self, alert) -> None:
        """
        Handle resource alerts with sage wisdom.
        From distributed_vic20.py:943-999.
        """
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']

        logger.warning(
            f"🖥️🧙⚠️ VIC-20 Sage observes resource pressure: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *contemplating coordination strategy*"
        )

        if self.is_distributed:
            await self._comm_hub.make_decision(
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

        if self.is_distributed and severity in ["critical", "high"]:
            await self._generate_and_broadcast_recommendations(alert)


        if severity in ["critical", "emergency"]:
            logger.warning(
                "🖥️🧙💥 CRITICAL RESOURCE PRESSURE! "
                "VIC-20 Sage initiates EMERGENCY COORDINATION PROTOCOL!"
            )

            if self.is_distributed:
                await self._comm_hub.broadcast_message(
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

    async def _generate_and_broadcast_recommendations(self, alert) -> None:
        """
        Generate and broadcast recommendations.
        From distributed_vic20.py:1001-1070.
        """
        p = self.personality
        resource_type = alert.payload['resource_type']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']

        agent_map = {
            'cpu': 'sir_hawkington',
            'memory': 'meth_snail',
            'disk': 'hamsters',
            'network': 'quantum_shadow_people'
        }

        target_agent = agent_map.get(resource_type)
        if not target_agent:
            logger.warning(f"🖥️💡 No agent mapped for resource type: {resource_type}")
            return

        historical_data = await self.orchestrator._get_historical_effectiveness(resource_type)

        recommendation = p.recommendation_engine.generate_recommendation(
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            agent_name=target_agent,
            historical_data=historical_data
        )

        logger.info(
            f"🖥️💡 Generated recommendation for {target_agent}: "
            f"{recommendation['suggested_action']} (confidence: {recommendation['confidence']:.0%})"
        )

        await self._comm_hub.broadcast_message(
            message_type=MessageType.COORDINATION_REQUEST,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": recommendation,
                "from_coordinator": "vic_20_sage"
            },
            priority=Priority.HIGH
        )

        await self._comm_hub.make_decision(
            decision_type="recommendation_generated",
            input_data={
                "resource_type": resource_type,
                "target_agent": target_agent,
                "current_value": current_value,
                "threshold": threshold
            },
            output_data={
                "recommendation": recommendation['suggested_action'],
                "confidence": recommendation['confidence'],
                "urgency": recommendation['urgency']
            },
            confidence=recommendation['confidence'],
            reasoning=recommendation['reasoning']
        )

    # ==================================================================
    # ANALYZE METRICS — distributed_vic20.py:886-941
    # ==================================================================

    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.
        From distributed_vic20.py:886-941.
        """
        decision = await self.orchestrator.process_metrics(
            metrics_data=metrics_data,
            user_context=user_context
        )

        if self.is_distributed and decision:
            try:
                await self._comm_hub.make_decision(
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

                if decision.get('agents_involved') and len(decision.get('agents_involved', [])) > 1:
                    await self._comm_hub.message_bus.send_to_agent(
                        to_agent="the_stick",
                        message_type=MessageType.DECISION_LOG,
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

    # ==================================================================
    # COORDINATION CAPABILITY — distributed_vic20.py:776-796
    # ==================================================================

    async def _coordination_capability(
        self,
        resource_type: CoordResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """
        VIC-20's coordination capability for Week 4 system.
        From distributed_vic20.py:776-796.
        """
        return AgentCapability(
            agent_name="vic_20_sage",
            resource_type=resource_type,
            estimated_improvement=0.0,  # VIC-20 coordinates, doesn't act directly
            confidence=0.95,  # Very confident in coordination
            estimated_duration=1.0,
            action_name="coordinate_specialists"
        )

    def get_distributed_state(self) -> Dict[str, Any]:
        """Get distributed state from communication hub."""
        if self._comm_hub:
            try:
                return self._comm_hub.get_state()
            except Exception:
                pass
        return {
            "is_connected": False,
            "agent_name": "vic_20_sage",
            "status": "not_initialized"
        }
