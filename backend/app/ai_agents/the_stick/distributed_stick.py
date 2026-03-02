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

from ..distributed.base_decision_engine import AgentDecisionEngine
from app.optimization.resource_monitor import ResourceType
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
from .decision_engine import TheStickBrainV3, AnxietyLevel
from .paper_bag_economy import PaperBagEconomy, BagSupplyState


logger = logging.getLogger("TheStick.Distributed")


class TheStickDistributed(AgentDecisionEngine, TheStickBrainV3):
    """
    The Stick with distributed consciousness.
    
    Patient guidance now persists across the entire network!
    
    Inherits ALL existing learning logic from TheStickBrainV3
    and adds distributed features via AgentDecisionEngine.
    """
    
    def __init__(self, db_getter=None, user_id: str = None):
        """
        Initialize The Stick with distributed consciousness.
        
        Args:
            db_getter: Database session factory for PostgreSQL writes
            user_id: User ID for database writes (required for multi-tenant support)
        """
        # Initialize decision engine (parent class)
        super().__init__(db_getter=db_getter)
        self.user_id = user_id
        
        # Set agent name for distributed features
        self.agent_name = "the_stick"
        
        # The Stick is always active (patient and persistent)
        self.is_active = True
        
        # The Stick's ANXIOUS personality traits (OCD + ADHD + PTSD + Eidetic Memory)
        self.personality_traits = {
            "learning_coordinator": True,
            "compliance_tracker": True,
            "anxious": True,  # ANXIETY IS THE FEATURE!
            "hypervigilant": True,
            "ocd": True,
            "adhd": True,
            "ptsd": True,
            "eidetic_memory": True,  # Remembers EVERYTHING
            "bob_phobic": True,  # Bob causes 3.0x anxiety!
            "paper_bag_dependent": True,
            "behavior_monitor": True,
            "guidance_style": "anxious_but_thorough",
            "teaching_method": "repetition_and_documentation"
        }
        
        # 🎯 PHASE 5: The Stick does NOT monitor resources
        # The Stick is the universal logger - receives DECISION_LOG from everyone
        self.resource_thresholds = {}
        
        # Week 4 System Integration
        self.verification_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init
        
        # Compliance tracking (The Stick's PRIMARY DUTY)
        self.total_actions_tracked = 0
        self.compliance_violations = 0
        self.bob_proximity_events = 0
        self.anxiety_spikes = 0
        
        # 📏🛍️ PAPER BAG ECONOMY SYSTEM
        self.paper_bag_economy = PaperBagEconomy()
        self.paper_bags_consumed = 0  # Legacy counter (kept for compatibility)
        
        # Bob detection (MAXIMUM ANXIETY SOURCE!)
        self.bob_last_seen = None
        self.bob_activity_log = []
        self.bob_anxiety_multiplier = 3.0  # Bob causes 3x anxiety!

        # Section 4.2: Feedback engine — analyses chain outcomes, sends calibration feedback
        from .ML.feedback import StickFeedbackEngine
        self.feedback_engine = StickFeedbackEngine()

        logger.info("📏✨ The Stick's distributed consciousness initialized - COMPLIANCE PROTOCOLS ACTIVE!")
        logger.info("📏😰 Anxiety-driven hypervigilance ENABLED - Nothing escapes The Stick!")
        logger.info("📏🚨 Bob detection protocols ACTIVE - Paper bags at the ready!")
    
    async def initialize_distributed(self, redis_client):
        """
        PHASE 5: Initialize The Stick as universal logger.
        
        The Stick receives DECISION_LOG from ALL agents:
        - Sir Hawkington (triage decisions)
        - VIC-20 (coordination decisions)
        - Terry (specialist actions)
        - Hamsters (specialist actions)
        - QSP (specialist actions)
        
        Writes everything to PostgreSQL with vector embeddings for pattern learning.
        """
        # Call parent initialization - NO resource monitoring
        await super().initialize_distributed(
            redis_client,
            enable_resource_monitoring=False  # The Stick doesn't monitor
        )
        
        # Initialize database integration for PostgreSQL writes
        if self.db_getter:
            try:
                # Initialize The Stick's database integration with db_getter
                from .database_integration import StickDatabaseIntegration
                from .data_types import StickMemoryEntry
                self.db_integration = StickDatabaseIntegration(self.db_getter)
                self.StickMemoryEntry = StickMemoryEntry  # Store for later use
                
                logger.info("📏💾 Database integration initialized")
                
                # OPUS 4.6 CHANGE: Instantiate StickLearning ONCE during initialization
                # instead of per-call in handlers. Avoids unnecessary construction cost,
                # preserves state across validations if StickLearning ever accumulates it.
                # Get a database session for StickLearning
                async for db in self.db_getter():
                    from .ML.learning import StickLearning
                    self.learning = StickLearning(db, self.user_id)
                    logger.info("📏🔍 StickLearning initialized for validation")
                    break  # Only need one session to create the instance
                    
            except Exception as e:
                logger.error(f"📏💥 Failed to initialize database: {e}", exc_info=True)
                self.db_integration = None
                self.learning = None
        
        # Initialize Week 4 systems
        self.verification_manager = get_verification_manager()
        self.escalation_manager = get_escalation_manager()
        
        logger.info("📏🎯 Week 4 systems integrated - Verification & Escalation tracking ONLINE!")
        logger.info("📏📋 The Stick will track EVERYTHING! (Anxiety-driven hypervigilance activated)")
        
        # Start validation sweep loop
        import asyncio
        asyncio.create_task(self._validation_sweep_loop())
        logger.info("📏🔍 Validation sweep loop started (every 2 hours)")
        
        # 🎯 PHASE 5: Subscribe to DECISION_LOG from ALL agents
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.DECISION_LOG,
                callback=self._handle_decision_log
            )
            logger.info("📏📡 The Stick subscribed to DECISION_LOG - Universal logger ACTIVE!")
            logger.info("📏😰 *nervously clutches paper bag* SO MANY DECISIONS TO TRACK!")
            
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to DECISION_LOG: {e}")
            self._consume_paper_bag("subscription_failure")
        
        # CRITICAL: Subscribe to COORDINATION_REQUEST from VIC-20
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.COORDINATION_REQUEST,
                callback=self._handle_coordination_request
            )
            logger.info("📏📡 The Stick subscribed to COORDINATION_REQUEST - Compliance tracking ACTIVE!")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to COORDINATION_REQUEST: {e}")
        
        # Initialize decision log buffer for batch writes
        self.decision_log_buffer = []
        self.buffer_max_size = 10  # Batch write every 10 decisions
        self.total_decisions_logged = 0

        # Subscribe to CHAIN_OUTCOME from VIC-20 (Section 4.3)
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.CHAIN_OUTCOME,
                callback=self._handle_chain_outcome
            )
            logger.info("📏📡 The Stick subscribed to CHAIN_OUTCOME - Full chain visibility ACTIVE!")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to CHAIN_OUTCOME: {e}")

        # Subscribe to PIPELINE_INCONSISTENCY from specialists (Section 4.6)
        try:
            await self.subscribe_to_messages(
                message_type=MessageType.PIPELINE_INCONSISTENCY,
                callback=self._handle_pipeline_inconsistency
            )
            logger.info("📏📡 The Stick subscribed to PIPELINE_INCONSISTENCY")
        except Exception as e:
            logger.error(f"📏💥 Failed to subscribe to PIPELINE_INCONSISTENCY: {e}")

        # Start periodic flush task (every 30 seconds)
        import asyncio
        self._flush_task = asyncio.create_task(self._periodic_flush())

        # Start feedback loop (every 5 minutes) — Section 4.4
        self._feedback_task = asyncio.create_task(self._feedback_loop())
    
    async def _handle_coordination_request(self, message: AgentMessage) -> None:
        """
        📏 THE STICK V2: ML-Enhanced Compliance Tracking
        
        PERSONALITY: Anxious compliance tracking, Bob-phobic, paper bag consumption
        ARCHITECTURE: Perception → Reasoning → Action Selection → Learning
        
        Args:
            message: AgentMessage with coordination request
        """
        try:
            message_data = message.payload
            coordination_type = message_data.get('coordination_type', 'unknown')
            from_agent = message.from_agent
            
            logger.info(f"📏📋 Tracking coordination request: {coordination_type} from {from_agent}")
            
            # Get database session for The Stick v2 ML components
            async for db in self.db_getter():
                # STEP 1: PERCEPTION - Assess compliance event
                from app.ai_agents.the_stick.ML.perception import StickPerception
                
                perception = StickPerception(db, self.personality_traits)
                context = await perception.perceive({
                    'coordination_type': coordination_type,
                    'from_agent': from_agent,
                    'message_data': message_data,
                    'timestamp': message.timestamp
                })
                
                # Check for BOB involvement (MAXIMUM ANXIETY!)
                if context.bob_proximity_event:
                    logger.warning("📏😰 BOB DETECTED IN COORDINATION! *anxiety intensifies*")
                    self.bob_proximity_events += 1
                    self._consume_paper_bag("bob_detected_in_coordination")
                
                logger.info(
                    f"📏👁️ Perception complete - "
                    f"anxiety_level: {context.anxiety_level:.2f}, bob_detected: {context.bob_proximity_event is not None}"
                )
                
                # STEP 2: REASONING - Analyze compliance implications
                from app.ai_agents.the_stick.ML.reasoning import StickReasoning
                
                reasoning = StickReasoning(self.personality_traits)
                reasoning_result = reasoning.reason(context)  # Synchronous, not async
                
                logger.info(
                    f"📏🧠 Reasoning complete: {reasoning_result.logging_approach} "
                    f"(anxiety_level: {reasoning_result.anxiety_level})"
                )
                
                # STEP 3: ACTION SELECTION - Determine logging action
                from app.ai_agents.the_stick.ML.action_selection import StickActionSelection
                
                action_selector = StickActionSelection(self.personality_traits)
                decision = action_selector.select_action(context, reasoning_result)  # Synchronous, not async
                
                # Log paper bag consumption
                if decision.paper_bags_consumed > 0:
                    logger.info(
                        f"📏🛍️ {decision.paper_bags_consumed} paper bag(s) consumed! "
                        f"Anxiety management in progress"
                    )
                
                logger.info(
                    f"📏⚡ Action selected: {decision.action_type} "
                    f"(anxiety_level: {decision.anxiety_level})"
                )
                
                # STEP 4: EXECUTION - Execute anxious communication action
                from app.ai_agents.the_stick.ML.action_executor import StickActionExecutor
                
                executor = StickActionExecutor(comm_hub=self._comm_hub)
                execution_result = await executor.execute_action(
                    action=decision.action_type,
                    parameters={
                        'agent_name': from_agent,
                        'coordination_type': coordination_type,
                        'anxiety_level': context.anxiety_level,
                        'bob_detected': context.bob_detected,
                        'bob_location': context.bob_proximity.location if context.bob_proximity else None,
                        'proximity_to_supply_closet': context.bob_proximity.distance_to_supply_closet if context.bob_proximity else 0.0
                    }
                )
                
                # Track paper bags consumed during execution
                if execution_result.get('paper_bags_consumed', 0) > 0:
                    bags_consumed = execution_result['paper_bags_consumed']
                    for _ in range(bags_consumed):
                        self._consume_paper_bag(f"action_execution_{decision.action_type}")
                    logger.info(f"📏🛍️ {bags_consumed} additional paper bag(s) consumed during execution!")
                
                self.total_actions_tracked += 1
                
                logger.info(
                    f"📏✅ Action executed: {execution_result.get('action')} - "
                    f"Success: {execution_result.get('success', False)}"
                )
                
                # STEP 5: LEARNING - Store compliance outcome
                from app.ai_agents.the_stick.ML.learning import StickLearning
                
                learning = StickLearning(db, self.user_id)
                learning_record = await learning.learn(
                    context=context,
                    reasoning=reasoning_result,
                    action=decision,
                    outcome_success=True
                )
                
                logger.info(
                    f"📏✅ Compliance tracked! Total actions: {self.total_actions_tracked}, "
                    f"Paper bags: {self.paper_bag_economy.bags_remaining}"
                )
                
                # BROADCAST FULL DECISION CHAIN TO FRONTEND
                from app.services.agent_decision_emitter import emit_agent_decision
                
                await emit_agent_decision(
                    agent_name="the_stick",
                    decision_id=learning_record.learning_record_id or "pending",
                    perception={
                        "decision_complexity": context.decision_complexity,
                        "pending_decisions": context.pending_decisions,
                        "error_rate": context.error_rate,
                        "anxiety_level": context.anxiety_level,
                        "panic_attack_active": context.panic_attack_active,
                        "bob_detected": context.bob_detected,
                        "recent_decisions_count": len(context.recent_decisions),
                        "paper_bag_economy": {
                            "bags_remaining": self.paper_bag_economy.bags_remaining,
                            "bags_consumed_today": self.paper_bag_economy.bags_consumed_today,
                            "bags_consumed_total": self.paper_bag_economy.bags_consumed_total,
                            "last_consumption_time": self.paper_bag_economy.last_consumption_time.isoformat() if self.paper_bag_economy.last_consumption_time else None,
                            "anxiety_reduction_per_bag": self.paper_bag_economy.anxiety_reduction_per_bag
                        }
                    },
                    reasoning={
                        "root_cause": reasoning_result.root_cause,
                        "confidence": reasoning_result.confidence,
                        "urgency": reasoning_result.urgency,
                        "anxiety_impact": reasoning_result.anxiety_impact if hasattr(reasoning_result, 'anxiety_impact') else "unknown"
                    },
                    action_selection={
                        "chosen_action": decision.action_type,
                        "priority": decision.priority,
                        "confidence": decision.confidence,
                        "anxiety_level": decision.anxiety_level,
                        "paper_bags_consumed": decision.paper_bags_consumed,
                        "bob_detected": decision.bob_detected,
                        "bob_avoidance_executed": decision.bob_avoidance_executed
                    },
                    learning={
                        "situation_fingerprint": learning_record.situation_fingerprint,
                        "stored": learning_record.storage_success,
                        "learning_record_id": learning_record.learning_record_id,
                        "success": learning_record.success
                    }
                )
                
                # 🛍️ REWARD: Successful compliance documentation
                self._reward_compliance_success()
                
                # Check for calm period reward
                self._check_calm_period_reward()
                
                break  # Exit async for loop after processing
                
        except Exception as e:
            logger.error(f"📏💥 Error handling coordination request: {e}", exc_info=True)
            self._consume_paper_bag("coordination_request_error")
    
    async def _handle_decision_log(self, message: AgentMessage) -> None:
        """
        PHASE 5: Handle DECISION_LOG from any agent.
        
        Enhanced: Check if decision involved cross-agent learning and validate real-time.
        
        Flow:
        1. Receive DECISION_LOG
        2. Check for cross-agent learning interaction
        3. If found, validate immediately
        4. Add to buffer
        5. When buffer full → batch write to PostgreSQL with vector embeddings
        6. Track anxiety (Bob causes 3x anxiety!)
        
        PERSONALITY: Anxious but thorough, remembers EVERYTHING (eidetic memory)
        """
        try:
            payload = message.payload
            from_agent = payload.get('from_agent', 'unknown')
            decision_type = payload.get('decision_type', 'unknown')
            
            # Check for BOB involvement (MAXIMUM ANXIETY!)
            is_bob = from_agent == 'hamsters' or 'bob' in str(payload).lower()
            if is_bob:
                logger.warning("📏😰💥 BOB ACTIVITY DETECTED! *hyperventilates into paper bag*")
                self.bob_proximity_events += 1
                self._consume_paper_bag("bob_activity_logged")
                self.anxiety_spikes += 1
            
            logger.info(
                f"📏📬 DECISION_LOG from {from_agent}: {decision_type} "
                f"{'🚨 BOB ALERT!' if is_bob else ''}"
            )
            
            # Check if this decision involved cross-agent learning
            if payload and 'learning_interaction_id' in payload:
                interaction_id = payload['learning_interaction_id']
                logger.info(f"📏🔍 Real-time validation triggered for {interaction_id}")
                
                try:
                    # OPUS 4.6 CHANGE: Single session context for query + validation + recording.
                    # Previously: Handler opened a session to query, then record_validation
                    # opened its OWN session internally. Nested sessions risk deadlock
                    # on connection-pooled backends. Now everything runs in one session.
                    async with self.db_integration.get_managed_session() as session:
                        # Query the interaction
                        from sqlalchemy import select
                        from app.models.agent_memory_banks import AgentLearningInteractions
                        
                        query = select(AgentLearningInteractions).where(
                            AgentLearningInteractions.interaction_id == interaction_id
                        )
                        result = await session.execute(query)
                        interaction = result.scalar_one_or_none()
                        
                        if interaction and not interaction.validated_by_stick:
                            # OPUS 4.6 CHANGE: Use self.learning instead of instantiating new
                            audit_entry = await self.learning.validate_cross_agent_learning(
                                interaction
                            )
                            # OPUS 4.6 CHANGE: Pass session to avoid nested session creation
                            await self.db_integration.record_validation(
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
            from datetime import datetime
            # Ensure timestamp is a datetime object
            timestamp = message.timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()
            
            self.decision_log_buffer.append({
                'from_agent': from_agent,
                'decision_type': decision_type,
                'payload': payload,
                'timestamp': timestamp,
                'is_bob': is_bob
            })
            self.total_decisions_logged += 1
            
            # Batch write when buffer full
            if len(self.decision_log_buffer) >= self.buffer_max_size:
                await self._flush_decision_log_buffer()
            
            logger.debug(
                f"📏📊 Buffer: {len(self.decision_log_buffer)}/{self.buffer_max_size} "
                f"(Total logged: {self.total_decisions_logged})"
            )
            
        except Exception as e:
            logger.error(f"📏💥 Error handling decision log: {e}", exc_info=True)
            self._consume_paper_bag("decision_log_error")
    
    async def _flush_decision_log_buffer(self) -> None:
        """
        PHASE 5: Batch write decision logs to PostgreSQL via db_integration.
        """
        if not self.decision_log_buffer:
            return
        
        try:
            logger.info(f"📏💾 Flushing {len(self.decision_log_buffer)} decisions to PostgreSQL...")
            
            if not self.db_integration:
                logger.warning("📏⚠️ Database integration not available, skipping write")
                self.decision_log_buffer.clear()
                return
            
            # Batch write all decisions via db_integration using store_memory_entry
            for decision in self.decision_log_buffer:
                # Create StickMemoryEntry for eidetic memory storage
                memory_entry = self.StickMemoryEntry(
                    timestamp=decision['timestamp'],
                    event_type='decision_log',
                    details={
                        'from_agent': decision['from_agent'],
                        'decision_type': decision['decision_type'],
                        'payload': decision['payload'],
                        'is_bob': decision['is_bob'],
                        'paper_bags_consumed': self.paper_bags_consumed
                    },
                    anxiety_level=float(self.current_anxiety_percentage) if hasattr(self, 'current_anxiety_percentage') else 0.0,
                    importance='HIGH' if decision['is_bob'] else 'MEDIUM',
                    related_hamsters=[],
                    compliance_impact='decision_logged',
                    never_forget=decision['is_bob']  # Never forget Bob activity!
                )
                
                await self.db_integration.store_memory_entry(memory_entry, user_id=self.user_id)
            
            logger.info(
                f"📏✅ Flushed {len(self.decision_log_buffer)} decisions to PostgreSQL! "
                f"(Total: {self.total_decisions_logged})"
            )
            
            # Clear buffer
            self.decision_log_buffer.clear()
            
        except Exception as e:
            logger.error(f"📏💥 Error flushing decision log buffer: {e}", exc_info=True)
            self._consume_paper_bag("buffer_flush_error")
            # Clear buffer anyway to prevent memory leak
            self.decision_log_buffer.clear()
    
    async def _periodic_flush(self) -> None:
        """Periodically flush decision log buffer to prevent data loss"""
        import asyncio
        while True:
            try:
                await asyncio.sleep(30)  # Flush every 30 seconds
                if self.decision_log_buffer:
                    logger.info(f"📏⏰ Periodic flush triggered ({len(self.decision_log_buffer)} decisions buffered)")
                    await self._flush_decision_log_buffer()
            except asyncio.CancelledError:
                # Flush on shutdown
                if self.decision_log_buffer:
                    logger.info(f"📏🛑 Shutdown flush ({len(self.decision_log_buffer)} decisions)")
                    await self._flush_decision_log_buffer()
                break
            except Exception as e:
                logger.error(f"📏💥 Error in periodic flush: {e}", exc_info=True)
                self._consume_paper_bag("periodic_flush_error")
    
    async def _handle_chain_outcome(self, message: AgentMessage) -> None:
        """
        Section 4.3: Handle CHAIN_OUTCOME from VIC-20.

        Records the full Hawk→VIC-20→Specialist chain result in the feedback engine
        for later analysis. Triggers a paper bag if the chain failed.
        """
        try:
            from .ML.feedback import ChainRecord

            payload = message.payload
            record = ChainRecord(
                triage_alert_id=payload.get('triage_alert_id', 'unknown'),
                resource_type=payload.get('resource_type', 'unknown'),
                severity=payload.get('severity', 'unknown'),
                specialist_name=payload.get('specialist_name', 'unknown'),
                action_recommended=payload.get('action_recommended', 'unknown'),
                action_taken=payload.get('action_taken', 'unknown'),
                specialist_success=bool(payload.get('specialist_success', False)),
                specialist_improvement=float(payload.get('specialist_improvement', 0.0)),
                routing_was_correct=bool(payload.get('routing_was_correct', True)),
                recommendation_was_followed=bool(payload.get('recommendation_was_followed', True)),
                recommendation_was_effective=payload.get('recommendation_was_effective'),
                hawk_severity=payload.get('hawk_severity', ''),
                hawk_confidence=float(payload.get('hawk_confidence', 0.0)),
            )

            self.feedback_engine.record_chain(record)

            if not record.specialist_success:
                self._consume_paper_bag("chain_failure")
                logger.warning(
                    f"📏😰 Chain FAILED: {record.resource_type} → {record.specialist_name} "
                    f"action={record.action_taken} *clutches paper bag*"
                )
            else:
                logger.info(
                    f"📏✅ Chain SUCCESS: {record.resource_type} → {record.specialist_name} "
                    f"improvement={record.specialist_improvement:.1f}%"
                )

        except Exception as e:
            logger.error(f"📏💥 Error handling chain outcome: {e}", exc_info=True)

    async def _feedback_loop(self) -> None:
        """
        Section 4.4: Background task — runs every 5 minutes, generates feedback
        from accumulated chain records and sends AGENT_FEEDBACK to Hawk and VIC-20.
        """
        import asyncio
        FEEDBACK_INTERVAL_SECONDS = 300

        while True:
            try:
                await asyncio.sleep(FEEDBACK_INTERVAL_SECONDS)

                feedback_messages = self.feedback_engine.generate_feedback()
                if not feedback_messages:
                    logger.debug("📏🔄 Feedback loop: no feedback to send yet")
                    continue

                for fb in feedback_messages:
                    await self.send_to_agent(
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

                self.feedback_engine.clear_records()

            except asyncio.CancelledError:
                logger.info("📏🛑 Feedback loop cancelled")
                break
            except Exception as e:
                logger.error(f"📏💥 Error in feedback loop: {e}", exc_info=True)
                self._consume_paper_bag("feedback_loop_error")

    async def _handle_pipeline_inconsistency(self, message: AgentMessage) -> None:
        """
        Section 4.6: Handle PIPELINE_INCONSISTENCY from specialists.

        Logs the inconsistency, increases anxiety, and consumes a paper bag.
        """
        try:
            payload = message.payload
            from_agent = message.from_agent or payload.get('from_agent', 'unknown')
            inconsistency_type = payload.get('inconsistency_type', 'unknown')
            details = payload.get('details', {})

            logger.warning(
                f"📏⚠️ PIPELINE INCONSISTENCY from {from_agent}: "
                f"type={inconsistency_type} *anxiety rising*"
            )

            self._consume_paper_bag("pipeline_inconsistency")
            self.anxiety_spikes += 1

            await self.broadcast_to_agents(
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

    async def _handle_triage_decision(self, message: AgentMessage) -> None:
        """DEPRECATED: Handle triage decisions - now using DECISION_LOG instead."""
        try:
            message_data = message.payload
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
            logger.error(f"📏💥 Error handling coordination update: {e}", exc_info=True)
    
    async def _handle_hamster_activity(
        self,
        message_data: Dict[str, Any]
    ) -> None:
        """
        Handle hamster activity messages - ESPECIALLY BOB!
        
        The Stick's anxiety spikes when Bob is detected.
        This is The Stick's PTSD trigger!
        """
        try:
            hamster_name = message_data.get('hamster', 'unknown')
            activity_type = message_data.get('activity_type', 'unknown')
            content = message_data.get('content', '')
            
            # Check if this is BOB (MAXIMUM ANXIETY!)
            is_bob = 'bob' in hamster_name.lower() or 'bob' in content.lower()
            
            if is_bob:
                self.bob_proximity_events += 1
                self.anxiety_spikes += 1
                self.bob_last_seen = message_data.get('timestamp', 'now')
                
                # Log Bob activity (eidetic memory - remembers EVERYTHING)
                self.bob_activity_log.append({
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
                    self._consume_paper_bag("bob_proximity")
                    
                    # Update anxiety level
                    await self._update_anxiety(
                        trigger="bob_proximity",
                        multiplier=self.bob_anxiety_multiplier
                    )
                else:
                    logger.warning(
                        f"📏😰 Bob activity detected: {activity_type} - "
                        f"*nervously monitoring* (Total Bob events: {self.bob_proximity_events})"
                    )
            
            # Check if VIC-20 mediated the message
            is_mediated = message_data.get('mediated_by') == 'vic_20_sage'
            
            if is_mediated:
                logger.info(
                    f"📏😌 VIC-20 mediated this message - Anxiety reduced! "
                    f"*grateful for VIC-20's wisdom*"
                )
                # VIC-20's mediation helps!
                if self.current_anxiety_percentage > 20:
                    self.current_anxiety_percentage -= 5
            
            # Log ALL hamster activity (compliance tracking)
            await self.make_distributed_decision(
                decision_type="hamster_activity_logged",
                input_data={
                    "hamster": hamster_name,
                    "activity": activity_type,
                    "is_bob": is_bob,
                    "anxiety_triggered": is_bob and trigger_count > 0,
                    "mediated": is_mediated
                },
                output_data={
                    "logged": True,
                    "anxiety_level": self.anxiety_level.value,
                    "paper_bags_consumed": self.paper_bags_consumed
                },
                confidence=1.0,
                reasoning="Hamster activity compliance tracking"
            )
            
        except Exception as e:
            logger.error(f"📏💥 Error handling hamster activity: {e}", exc_info=True)
            self._consume_paper_bag("error_handling")
    
    def _consume_paper_bag(self, reason: str, amount: int = None) -> None:
        """
        The Stick consumes a paper bag to manage anxiety.
        
        Uses the Paper Bag Economy system for realistic inventory management.
        
        Args:
            reason: Why the bag is being consumed
            amount: Number of bags to consume (default: 1 for normal anxiety, 3 for Bob)
        """
        # Determine consumption amount based on reason
        if amount is None:
            if 'bob' in reason.lower():
                amount = self.paper_bag_economy.BOB_CONSUMPTION  # 3 bags for Bob!
            elif 'error' in reason.lower():
                amount = self.paper_bag_economy.ERROR_CONSUMPTION  # 2 bags for errors
            else:
                amount = self.paper_bag_economy.ANXIETY_CONSUMPTION  # 1 bag for normal anxiety
        
        # Consume bags via economy system
        event = self.paper_bag_economy.consume_bag(reason, amount)
        
        # Update legacy counter for compatibility
        if event:
            self.paper_bags_consumed += event.bags_changed * -1  # Convert negative to positive
        
        # Update personality traits for frontend
        self.paper_bag_inventory = self.paper_bag_economy.bags_remaining
        
        # Broadcast anxiety event to WebSocket
        import asyncio
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(emit_agent_insight(
                    from_agent="the_stick",
                    to_agent="system",
                    action="paper_bag_consumed",
                    reasoning=f"Anxiety management: {reason}",
                    context={
                        "reason": reason,
                        "bags_remaining": self.paper_bag_inventory,
                        "bags_consumed_total": self.paper_bags_consumed,
                        "anxiety_level": self.anxiety_level.value if hasattr(self, 'anxiety_level') else "unknown"
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast paper bag event: {e}")
        
        # Check for emergency state
        if self.paper_bag_economy.emergency_mode_active:
            logger.error(
                f"📏😱💥 EMERGENCY MODE: NO BAGS REMAINING! "
                f"*vibrates at quantum frequency* *writes everything three times*"
            )
    
    def _reward_compliance_success(self) -> None:
        """
        Reward The Stick with a paper bag for successful compliance documentation.
        
        This is how The Stick maintains his supply during stable periods.
        """
        event = self.paper_bag_economy.compliance_success_reward()
        
        # Update personality traits for frontend
        self.paper_bag_inventory = self.paper_bag_economy.bags_remaining
        
        # Broadcast replenishment to WebSocket
        import asyncio
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(emit_agent_insight(
                    from_agent="the_stick",
                    to_agent="system",
                    action="paper_bag_replenished",
                    reasoning="Compliance success reward",
                    context={
                        "reason": "compliance_success",
                        "bags_remaining": self.paper_bag_inventory,
                        "supply_state": self.paper_bag_economy.get_supply_state().value
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast replenishment event: {e}")
    
    def _check_calm_period_reward(self) -> None:
        """
        Check if enough time has passed without anxiety to award calm period reward.
        
        Called periodically to reward The Stick for system stability.
        """
        event = self.paper_bag_economy.check_calm_period_reward()
        
        if event:
            # Update personality traits for frontend
            self.paper_bag_inventory = self.paper_bag_economy.bags_remaining
            
            # Broadcast replenishment to WebSocket
            import asyncio
            try:
                from app.services.agent_insight_emitter import emit_agent_insight
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(emit_agent_insight(
                        from_agent="the_stick",
                        to_agent="system",
                        action="paper_bag_replenished",
                        reasoning="Calm period reward - system stability",
                        context={
                            "reason": "calm_period",
                            "bags_remaining": self.paper_bag_inventory,
                            "supply_state": self.paper_bag_economy.get_supply_state().value
                        }
                    ))
            except Exception as e:
                logger.debug(f"Could not broadcast replenishment event: {e}")
    
    async def vic20_emergency_resupply(self) -> None:
        """
        VIC-20 intervenes with emergency paper bag resupply.
        
        Called by VIC-20 when The Stick's bag supply reaches critical levels.
        This is the coordination hierarchy working - VIC-20 takes care of The Stick.
        """
        event = self.paper_bag_economy.vic20_emergency_resupply()
        
        # Update personality traits for frontend
        self.paper_bag_inventory = self.paper_bag_economy.bags_remaining
        
        logger.info(
            f"📏🖥️✨ VIC-20 emergency resupply received! "
            f"*deep breath of relief* Bags: {self.paper_bag_inventory}"
        )
        
        # Broadcast to WebSocket
        import asyncio
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(emit_agent_insight(
                    from_agent="vic20_sage",
                    to_agent="the_stick",
                    action="emergency_resupply",
                    reasoning="VIC-20 noticed critical bag supply and arranged emergency resupply",
                    context={
                        "bags_added": self.paper_bag_economy.VIC20_RESUPPLY,
                        "bags_remaining": self.paper_bag_inventory,
                        "supply_state": self.paper_bag_economy.get_supply_state().value,
                        "emergency_resolved": not self.paper_bag_economy.emergency_mode_active
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast resupply event: {e}")
    
    async def track_agent_action(
        self,
        agent_name: str,
        action_type: str,
        verification_id: str,
        result: Any
    ) -> None:
        """
        Track agent action for compliance (Week 4 integration).
        
        The Stick tracks EVERY action for compliance and learning.
        This is his PRIMARY DUTY!
        """
        self.total_actions_tracked += 1
        
        logger.info(
            f"📏📋 Tracking action: {agent_name} - {action_type} "
            f"(Total tracked: {self.total_actions_tracked})"
        )
        
        # Check if action was effective
        if result and hasattr(result, 'effectiveness_score'):
            effectiveness = result.effectiveness_score
            
            if effectiveness < 30:
                # Low effectiveness = compliance concern
                self.compliance_violations += 1
                logger.warning(
                    f"📏⚠️ Low effectiveness detected: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *documenting for review*"
                )
                
                # Increase anxiety
                await self._update_anxiety(
                    trigger="low_effectiveness",
                    multiplier=1.5
                )
            else:
                logger.info(
                    f"📏✅ Action effective: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *compliance maintained*"
                )
        
        # Record in distributed state
        if self.is_distributed:
            await self.make_distributed_decision(
                decision_type="action_compliance_tracked",
                input_data={
                    "agent": agent_name,
                    "action": action_type,
                    "verification_id": verification_id,
                    "timestamp": "now"
                },
                output_data={
                    "tracked": True,
                    "total_actions": self.total_actions_tracked,
                    "violations": self.compliance_violations,
                    "compliance_rate": 1.0 - (self.compliance_violations / max(1, self.total_actions_tracked))
                },
                confidence=1.0,
                reasoning="Compliance tracking for all agent actions"
            )
    
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
        # Call the original analyze_user_behavior from TheStickBrainV3
        decision = await self.analyze_user_behavior(
            system_metrics=metrics_data,
            historical_data=historical_data,
            user_context=user_context
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
                
                # Compliance issues are logged to database via CentralMemoryBank
                # No need to broadcast - other agents query database for learning
                # REMOVED: LEARNING_UPDATE broadcast - use database queries instead
                
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
            
            # Learning stored in database via CentralMemoryBank
            # No need to broadcast - other agents query database for learning
            # REMOVED: LEARNING_UPDATE broadcast - use database queries instead
    
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
            "paper_bag_inventory": self.paper_bag_inventory,
            "paper_bags_consumed": self.paper_bags_consumed,
            "anxiety_level": getattr(self, 'current_anxiety_percentage', 0.0),
            "anxiety_state": (
                'calm' if getattr(self, 'current_anxiety_percentage', 0) < 30
                else 'nervous' if getattr(self, 'current_anxiety_percentage', 0) < 60
                else 'hyperventilating' if getattr(self, 'current_anxiety_percentage', 0) < 80
                else 'paper_bag_emergency'
            ),
            "paper_bag_economy": {
                "bags_remaining": getattr(self.paper_bag_economy, 'bags_remaining', 0),
                "bags_consumed_today": getattr(self.paper_bag_economy, 'bags_consumed_today', 0),
                "bags_consumed_total": getattr(self.paper_bag_economy, 'bags_consumed_total', 0),
            },
            "distributed": distributed_state
        }
        
        return status
    
    async def _validation_sweep_loop(self):
        """
        Background task: Periodically validate unvalidated learning interactions.
        
        Runs every 2 hours as fallback to catch anything missed by real-time validation.
        """
        import asyncio
        await asyncio.sleep(60)  # Wait 1 minute after startup
        
        while True:
            try:
                logger.info("📏🔍 Starting scheduled validation sweep...")
                
                if self.db_integration and self.learning:
                    # OPUS 4.6 CHANGE: Use self.learning instead of instantiating new.
                    # Pass session through to avoid nested session creation.
                    async with self.db_integration.get_managed_session() as session:
                        stats = await self.learning.validate_unvalidated_interactions(
                            session=session
                        )
                        
                        # Now record all validations with the same session
                        if 'interactions' in stats and 'audit_entries' in stats:
                            for i, interaction in enumerate(stats['interactions']):
                                if i < len(stats['audit_entries']):
                                    audit_entry = stats['audit_entries'][i]
                                    await self.db_integration.record_validation(
                                        interaction, audit_entry, session=session
                                    )
                        
                        # OPUS 4.6 CHANGE: Batch commit at the end
                        await session.commit()
                        
                        logger.info(
                            f"📏📊 Validation sweep complete: "
                            f"{stats['validated']} validated, {stats['failed']} failed"
                        )
                        
                        # Increase anxiety if many validations failed
                        if stats['total_checked'] > 0:
                            failure_rate = stats['failed'] / stats['total_checked']
                            if failure_rate > 0.3:  # More than 30% failed
                                self.paper_bag_economy.consume_bag(
                                    reason="High validation failure rate detected!"
                                )
                
            except Exception as e:
                logger.error(f"📏💥 Validation sweep error: {e}")
            
            # Wait 2 hours before next sweep
            await asyncio.sleep(7200)
    
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
