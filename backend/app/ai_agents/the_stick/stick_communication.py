"""
The Stick — Communication Layer
==================================

Owns ALL inter-agent messaging:
- Redis initialization and message bus setup
- Message handler registration (DECISION_LOG, COORDINATION_REQUEST, CHAIN_OUTCOME, PIPELINE_INCONSISTENCY)
- Background tasks: periodic flush, feedback loop, validation sweep, heartbeat
- Legacy handlers (triage, coordination update, hamster activity)
- Outbound: send_to_agent (AGENT_FEEDBACK), broadcast (DECISION_LOG)

Uses AgentCommunicationHub from shared infrastructure (composition, not inheritance).
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..distributed.communication import AgentCommunicationHub
from ..distributed.message_protocol import MessageType, Priority, AgentMessage
from ..distributed.action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType as VerificationResourceType
)
from ..distributed.alert_escalation import (
    get_escalation_manager,
    AlertLevel,
    ResourceType as EscalationResourceType
)
from ..distributed.event_logger import log_agent_startup

from .data_types import AnxietyLevel

logger = logging.getLogger("TheStick.Communication")


class StickCommunication:
    """
    The Stick communication layer.

    Wraps AgentCommunicationHub for Redis pub/sub messaging.
    Registers all 4 message handlers.
    Routes ML pipeline results to frontend and other agents.
    """

    def __init__(self, personality, websocket, orchestrator):
        """
        Args:
            personality: StickPersonalityState instance
            websocket: StickWebSocket instance
            orchestrator: StickOrchestrator instance
        """
        self.personality = personality
        self.websocket = websocket
        self.orchestrator = orchestrator

        self.agent_name = "the_stick"
        self._comm_hub: Optional[AgentCommunicationHub] = None
        self._agent_manager = None  # Set by DistributedAgentManager
        self._shutdown = False

    @property
    def comm_hub(self) -> Optional[AgentCommunicationHub]:
        return self._comm_hub

    @property
    def is_distributed(self) -> bool:
        return self._comm_hub is not None

    async def initialize(self, redis_client) -> None:
        """
        Initialize communication layer.

        From distributed_stick.py:120-230 (initialize_distributed).
        """
        p = self.personality

        # 1. Create communication hub — NO resource monitoring for The Stick
        self._comm_hub = AgentCommunicationHub(
            redis_client=redis_client,
            agent_name="the_stick",
            agent_role="learning_coordinator",
            personality_traits=p.personality_traits
        )
        await self._comm_hub.initialize()

        # Pass comm_hub reference to orchestrator
        self.orchestrator._comm_hub_ref = self._comm_hub

        # 2. Initialize database integration for PostgreSQL writes
        if p.db_getter:
            try:
                from .database_integration import StickDatabaseIntegration
                from .data_types import StickMemoryEntry
                p.db_integration = StickDatabaseIntegration(p.db_getter)
                p.StickMemoryEntry = StickMemoryEntry

                logger.info("📏💾 Database integration initialized")

                # Initialize StickLearning ONCE (OPUS 4.6 pattern)
                async for db in p.db_getter():
                    from .ML.learning import StickLearning
                    p.learning = StickLearning(db, self.personality.user_id if hasattr(self.personality, 'user_id') else None)
                    logger.info("📏🔍 StickLearning initialized for validation")
                    break

            except Exception as e:
                logger.error(f"📏💥 Failed to initialize database: {e}", exc_info=True)
                p.db_integration = None
                p.learning = None

        # 3. Initialize Week 4 systems
        p.verification_manager = get_verification_manager()
        p.escalation_manager = get_escalation_manager()

        logger.info("📏🎯 Week 4 systems integrated - Verification & Escalation tracking ONLINE!")

        # 4. Subscribe to DECISION_LOG from ALL agents
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.DECISION_LOG,
                self._handle_decision_log
            )
            logger.info("📏📡 The Stick subscribed to DECISION_LOG - Universal logger ACTIVE!")
            logger.info("📏😰 *nervously clutches paper bag* SO MANY DECISIONS TO TRACK!")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to DECISION_LOG: {e}")
            self.orchestrator._consume_paper_bag("subscription_failure")

        # 5. Subscribe to COORDINATION_REQUEST from VIC-20
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.COORDINATION_REQUEST,
                self._handle_coordination_request
            )
            logger.info("📏📡 The Stick subscribed to COORDINATION_REQUEST - Compliance tracking ACTIVE!")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to COORDINATION_REQUEST: {e}")

        # 6. Subscribe to CHAIN_OUTCOME from VIC-20 (Section 4.3)
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.CHAIN_OUTCOME,
                self._handle_chain_outcome
            )
            logger.info("📏📡 The Stick subscribed to CHAIN_OUTCOME - Full chain visibility ACTIVE!")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to CHAIN_OUTCOME: {e}")

        # 7. Subscribe to PIPELINE_INCONSISTENCY from specialists (Section 4.6)
        try:
            self._comm_hub.message_bus.register_handler(
                MessageType.PIPELINE_INCONSISTENCY,
                self._handle_pipeline_inconsistency
            )
            logger.info("📏📡 The Stick subscribed to PIPELINE_INCONSISTENCY")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to PIPELINE_INCONSISTENCY: {e}")

        # Set personality traits in state
        state = self._comm_hub.get_state()
        if state:
            state.personality_traits = p.personality_traits
            await self._comm_hub.state_manager.save_state(state)

        # Update health
        from ..distributed.agent_state import AgentHealth
        await self._comm_hub.state_manager.update_health(AgentHealth.HEALTHY)

        # 8. Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(30))
        self._flush_task = asyncio.create_task(self._periodic_flush())
        self._feedback_task = asyncio.create_task(self._feedback_loop())
        self._validation_task = asyncio.create_task(self._validation_sweep_loop())

        # Log startup
        await log_agent_startup(
            agent_name=self.agent_name,
            metadata={
                "personality_traits": p.personality_traits,
                "resource_thresholds": p.resource_thresholds,
            }
        )

        logger.info("📏📡 The Stick communication layer initialized")
        logger.info("📏😰 Anxiety-driven hypervigilance ENABLED - Nothing escapes The Stick!")
        logger.info("📏🚨 Bob detection protocols ACTIVE - Paper bags at the ready!")

    async def shutdown(self) -> None:
        """Shutdown communication cleanly."""
        self._shutdown = True

        # Cancel background tasks
        for task_name in ['_heartbeat_task', '_flush_task', '_feedback_task', '_validation_task']:
            task = getattr(self, task_name, None)
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if self._comm_hub:
            await self._comm_hub.shutdown()

        logger.info("📏🛑 The Stick communication layer shut down")

    # ==================================================================
    # BACKGROUND TASKS
    # ==================================================================

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
                logger.error(f"📏💥 Heartbeat error: {e}")

    async def _periodic_flush(self) -> None:
        """
        Periodically flush decision log buffer.

        From distributed_stick.py:560-577.
        """
        while not self._shutdown:
            try:
                await asyncio.sleep(30)  # Flush every 30 seconds
                p = self.personality
                if p.decision_log_buffer:
                    logger.info(f"📏⏰ Periodic flush triggered ({len(p.decision_log_buffer)} decisions buffered)")
                    await self.orchestrator.flush_decision_log_buffer()
            except asyncio.CancelledError:
                # Flush on shutdown
                p = self.personality
                if p.decision_log_buffer:
                    logger.info(f"📏🛑 Shutdown flush ({len(p.decision_log_buffer)} decisions)")
                    await self.orchestrator.flush_decision_log_buffer()
                break
            except Exception as e:
                logger.error(f"📏💥 Error in periodic flush: {e}", exc_info=True)
                self.orchestrator._consume_paper_bag("periodic_flush_error")

    async def _feedback_loop(self) -> None:
        """
        Background task — generates feedback from accumulated chain records.

        From distributed_stick.py:623-667 — runs every 5 minutes.
        """
        FEEDBACK_INTERVAL_SECONDS = 300

        while not self._shutdown:
            try:
                await asyncio.sleep(FEEDBACK_INTERVAL_SECONDS)

                p = self.personality
                feedback_messages = p.feedback_engine.generate_feedback()
                if not feedback_messages:
                    logger.debug("📏🔄 Feedback loop: no feedback to send yet")
                    continue

                for fb in feedback_messages:
                    await self._comm_hub.message_bus.send_to_agent(
                        to_agent=fb.target_agent,
                        message_type=MessageType.AGENT_FEEDBACK,
                        payload={
                            'feedback_type': fb.feedback_type,
                            'resource_type': fb.resource_type,
                            'data': fb.data,
                            'reasoning': fb.reasoning,
                            'confidence': fb.confidence,
                            'from_agent': 'the_stick',
                        },
                        priority=Priority.NORMAL,
                    )
                    logger.info(
                        f"📏📤 Feedback sent to {fb.target_agent}: "
                        f"type={fb.feedback_type}, resource={fb.resource_type}, "
                        f"confidence={fb.confidence:.2f}"
                    )

                p.feedback_engine.clear_records()

            except asyncio.CancelledError:
                logger.info("📏🛑 Feedback loop cancelled")
                break
            except Exception as e:
                logger.error(f"📏💥 Error in feedback loop: {e}", exc_info=True)
                self.orchestrator._consume_paper_bag("feedback_loop_error")

    async def _validation_sweep_loop(self) -> None:
        """
        Background task: Periodically validate unvalidated learning interactions.

        From distributed_stick.py:1282-1332. Runs every 2 hours.
        """
        await asyncio.sleep(60)  # Wait 1 minute after startup

        while not self._shutdown:
            try:
                await self.orchestrator.validation_sweep()
            except Exception as e:
                logger.error(f"📏💥 Validation sweep error: {e}")

            # Wait 2 hours before next sweep
            await asyncio.sleep(7200)

    # ==================================================================
    # MESSAGE HANDLERS
    # ==================================================================

    async def _handle_decision_log(self, message: AgentMessage) -> None:
        """
        Handle DECISION_LOG from any agent.

        From distributed_stick.py:405-507 — universal logger with buffer.
        EXACT payload keys preserved.
        """
        p = self.personality

        try:
            payload = message.payload
            from_agent = payload.get('from_agent', 'unknown')
            decision_type = payload.get('decision_type', 'unknown')

            # Check for BOB involvement (MAXIMUM ANXIETY!)
            is_bob = from_agent == 'hamsters' or 'bob' in str(payload).lower()
            if is_bob:
                logger.warning("📏😰💥 BOB ACTIVITY DETECTED! *hyperventilates into paper bag*")
                p.bob_proximity_events += 1
                self.orchestrator._consume_paper_bag("bob_activity_logged")
                p.anxiety_spikes += 1

            logger.info(
                f"📏📬 DECISION_LOG from {from_agent}: {decision_type} "
                f"{'🚨 BOB ALERT!' if is_bob else ''}"
            )

            # Check if this decision involved cross-agent learning
            if payload and 'learning_interaction_id' in payload:
                interaction_id = payload['learning_interaction_id']
                logger.info(f"📏🔍 Real-time validation triggered for {interaction_id}")

                try:
                    async with p.db_integration.get_managed_session() as session:
                        from sqlalchemy import select
                        from app.models.agent_memory_banks import AgentLearningInteractions

                        query = select(AgentLearningInteractions).where(
                            AgentLearningInteractions.interaction_id == interaction_id
                        )
                        result = await session.execute(query)
                        interaction = result.scalar_one_or_none()

                        if interaction and not interaction.validated_by_stick:
                            audit_entry = await p.learning.validate_cross_agent_learning(
                                interaction
                            )
                            await p.db_integration.record_validation(
                                interaction, audit_entry, session=session
                            )
                            await session.commit()

                            logger.info(
                                f"📏✅ Real-time validation complete: "
                                f"{audit_entry.validation_result}"
                            )
                except Exception as e:
                    logger.error(f"📏💥 Real-time validation failed: {e}")

            # Add to buffer
            timestamp = message.timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()

            p.decision_log_buffer.append({
                'from_agent': from_agent,
                'decision_type': decision_type,
                'payload': payload,
                'timestamp': timestamp,
                'is_bob': is_bob
            })
            p.total_decisions_logged += 1

            # Batch write when buffer full
            if len(p.decision_log_buffer) >= p.buffer_max_size:
                await self.orchestrator.flush_decision_log_buffer()

            logger.debug(
                f"📏📊 Buffer: {len(p.decision_log_buffer)}/{p.buffer_max_size} "
                f"(Total logged: {p.total_decisions_logged})"
            )

        except Exception as e:
            logger.error(f"📏💥 Error handling decision log: {e}", exc_info=True)
            self.orchestrator._consume_paper_bag("decision_log_error")

    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        Handle COORDINATION_REQUEST — routes to 5-step ML pipeline.

        From distributed_stick.py:232-403.
        """
        try:
            await self.orchestrator.run_coordination_pipeline(
                message_data=message.payload,
                from_agent=message.from_agent,
                timestamp=message.timestamp,
            )
        except Exception as e:
            logger.error(f"📏💥 Error handling coordination request: {e}", exc_info=True)
            self.orchestrator._consume_paper_bag("coordination_request_error")

    async def _handle_chain_outcome(self, message: AgentMessage) -> None:
        """
        Handle CHAIN_OUTCOME from VIC-20.

        From distributed_stick.py:579-621.
        """
        self.orchestrator.record_chain_outcome(message.payload)

    async def _handle_pipeline_inconsistency(self, message: AgentMessage) -> None:
        """
        Handle PIPELINE_INCONSISTENCY from specialists.

        From distributed_stick.py:669-702. EXACT payload keys.
        """
        p = self.personality

        try:
            payload = message.payload
            from_agent = message.from_agent or payload.get('from_agent', 'unknown')
            inconsistency_type = payload.get('inconsistency_type', 'unknown')
            details = payload.get('details', {})

            logger.warning(
                f"📏⚠️ PIPELINE INCONSISTENCY from {from_agent}: "
                f"type={inconsistency_type} *anxiety rising*"
            )

            self.orchestrator._consume_paper_bag("pipeline_inconsistency")
            p.anxiety_spikes += 1

            await self._comm_hub.broadcast_message(
                message_type=MessageType.DECISION_LOG,
                payload={
                    'decision_type': 'pipeline_inconsistency_logged',
                    'from_agent': 'the_stick',
                    'source_agent': from_agent,
                    'inconsistency_type': inconsistency_type,
                    'details': details,
                },
                priority=Priority.NORMAL,
            )

        except Exception as e:
            logger.error(f"📏💥 Error handling pipeline inconsistency: {e}", exc_info=True)

    # ==================================================================
    # LEGACY HANDLERS — preserved for backward compatibility
    # ==================================================================

    async def _handle_triage_decision(self, message: AgentMessage) -> None:
        """DEPRECATED: Handle triage decisions — now using DECISION_LOG instead."""
        try:
            message_data = message.payload
            severity = message_data.get('severity', 'unknown')
            routing = message_data.get('routing', 'unknown')
            target_agents = message_data.get('target_agents', [])

            logger.info(f"🥢📬 Triage received: {severity} → {routing}")

            await self._comm_hub.make_decision(
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
                triage_severity=severity,
                triage_routing=routing
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
        """Handle coordination updates from VIC-20."""
        try:
            coordination_id = message_data.get('coordination_id', 'unknown')
            severity = message_data.get('severity', 'unknown')
            agents_involved = message_data.get('agents_involved', [])
            status = message_data.get('status', 'unknown')

            logger.info(f"🥢📬 Coordination update received: {coordination_id} - {status}")

            await self._comm_hub.make_decision(
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
                triage_severity=severity,
                coordination_id=coordination_id
            )

            logger.debug(f"🥢📝 Coordination logged: {len(agents_involved)} agents involved")

        except Exception as e:
            logger.error(f"📏💥 Error handling coordination update: {e}", exc_info=True)

    async def _handle_hamster_activity(self, message_data: Dict[str, Any]) -> None:
        """
        Handle hamster activity messages — ESPECIALLY BOB!

        From distributed_stick.py:778-864.
        """
        p = self.personality

        try:
            hamster_name = message_data.get('hamster', 'unknown')
            activity_type = message_data.get('activity_type', 'unknown')
            content = message_data.get('content', '')

            # Check if this is BOB (MAXIMUM ANXIETY!)
            is_bob = 'bob' in hamster_name.lower() or 'bob' in content.lower()

            if is_bob:
                p.bob_proximity_events += 1
                p.anxiety_spikes += 1
                p.bob_last_seen = message_data.get('timestamp', 'now')

                # Log Bob activity (eidetic memory - remembers EVERYTHING)
                p.bob_activity_log.append({
                    'timestamp': message_data.get('timestamp'),
                    'activity': activity_type,
                    'content': content,
                    'anxiety_level': 'MAXIMUM'
                })

                # Check for anxiety triggers
                anxiety_triggers = ['hold my beer', 'wild idea', 'emergency', 'fire', 'chaos', 'duct tape']
                trigger_count = sum(1 for trigger in anxiety_triggers if trigger in content.lower())

                if trigger_count > 0:
                    logger.warning(
                        f"📏😰😰😰 BOB DETECTED! Anxiety level: CRITICAL! "
                        f"Triggers detected: {trigger_count} - *CONSUMING PAPER BAG*"
                    )
                    self.orchestrator._consume_paper_bag("bob_proximity")

                    # Update anxiety level
                    await p._update_anxiety(
                        trigger="bob_proximity",
                        multiplier=p.bob_anxiety_multiplier
                    )
                else:
                    logger.warning(
                        f"📏😰 Bob activity detected: {activity_type} - "
                        f"*nervously monitoring* (Total Bob events: {p.bob_proximity_events})"
                    )

            # Check if VIC-20 mediated the message
            is_mediated = message_data.get('mediated_by') == 'vic_20_sage'

            if is_mediated:
                logger.info(
                    f"📏😌 VIC-20 mediated this message - Anxiety reduced! "
                    f"*grateful for VIC-20's wisdom*"
                )
                # VIC-20's mediation helps!
                if p.current_anxiety_percentage > 20:
                    p.current_anxiety_percentage -= 5

            # Log ALL hamster activity (compliance tracking)
            await self._comm_hub.make_decision(
                decision_type="hamster_activity_logged",
                input_data={
                    "hamster": hamster_name,
                    "activity": activity_type,
                    "is_bob": is_bob,
                    "anxiety_triggered": is_bob and trigger_count > 0 if is_bob else False,
                    "mediated": is_mediated
                },
                output_data={
                    "logged": True,
                    "anxiety_level": p.anxiety_level.value,
                    "paper_bags_consumed": p.paper_bags_consumed
                },
                confidence=1.0,
                reasoning="Hamster activity compliance tracking"
            )

        except Exception as e:
            logger.error(f"📏💥 Error handling hamster activity: {e}", exc_info=True)
            self.orchestrator._consume_paper_bag("error_handling")

    # ==================================================================
    # DISTRIBUTED STATE / ANALYZE METRICS
    # ==================================================================

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

    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data=None,
        user_context=None,
        user_id=None,
    ):
        """Delegate to orchestrator's analyze_metrics."""
        return await self.orchestrator.analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            user_id=user_id,
        )
