"""
The Stick — Orchestrator
==========================

Core logic extracted from distributed_stick.py:

- 5-step COORDINATION_REQUEST ML pipeline (Perception → Reasoning → Action Selection → Execution → Learning)
- Paper bag economy helpers (_consume_paper_bag, _reward_compliance_success, _check_calm_period_reward, vic20_emergency_resupply)
- Decision log buffer + flush
- Chain outcome handling (feedback engine)
- Pipeline inconsistency handling
- Validation sweep loop
- Feedback loop (Section 4.4)
- analyze_metrics / process_metrics entry points
- Legacy handlers (triage, coordination update, hamster activity)
- Agent action tracking (compliance)
- Pattern detection

Every method name, dict key, payload structure preserved character-for-character.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .data_types import AnxietyLevel, StickMemoryEntry
from .data_types import utc_now

logger = logging.getLogger("TheStick.Orchestrator")


class StickOrchestrator:
    """
    The Stick's core orchestration logic.

    Handles:
    - 5-step ML pipeline for COORDINATION_REQUEST
    - Paper bag economy management
    - Decision log buffer + batch flush
    - Chain outcome recording
    - Pipeline inconsistency logging
    - Validation sweep (background)
    - Feedback loop (background)
    - analyze_metrics / process_metrics
    - Agent action tracking + effectiveness
    - Hamster activity handling
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        """
        Args:
            personality: StickPersonalityState instance
            db_getter: Database session factory
            user_id: User ID
        """
        self.personality = personality
        self.db_getter = db_getter or personality.db_getter
        self.user_id = user_id

        # Ref to comm hub — set by communication layer
        self._comm_hub_ref = None

        logger.info("📏🧠 Orchestrator initialized")

    # ==================================================================
    # 5-STEP ML PIPELINE — distributed_stick.py:232-403
    # ==================================================================

    async def run_coordination_pipeline(
        self,
        message_data: Dict[str, Any],
        from_agent: str,
        timestamp: Any,
    ) -> None:
        """
        5-step ML pipeline for COORDINATION_REQUEST.

        From distributed_stick.py:232-403.
        EXACT method structure, variable names, and payload keys.
        """
        p = self.personality
        coordination_type = message_data.get('coordination_type', 'unknown')

        logger.info(f"📏📋 Tracking coordination request: {coordination_type} from {from_agent}")

        # Get database session for The Stick v2 ML components
        async for db in self.db_getter():
            # STEP 1: PERCEPTION
            from app.ai_agents.the_stick.ML.perception import StickPerception

            perception = StickPerception(db, p.personality_traits)
            context = await perception.perceive({
                'coordination_type': coordination_type,
                'from_agent': from_agent,
                'message_data': message_data,
                'timestamp': timestamp
            })

            # Check for BOB involvement (MAXIMUM ANXIETY!)
            if context.bob_proximity_event:
                logger.warning("📏😰 BOB DETECTED IN COORDINATION! *anxiety intensifies*")
                p.bob_proximity_events += 1
                self._consume_paper_bag("bob_detected_in_coordination")

            logger.info(
                f"📏👁️ Perception complete - "
                f"anxiety_level: {context.anxiety_level:.2f}, bob_detected: {context.bob_proximity_event is not None}"
            )

            # STEP 2: REASONING
            from app.ai_agents.the_stick.ML.reasoning import StickReasoning

            reasoning = StickReasoning(p.personality_traits)
            reasoning_result = reasoning.reason(context)  # Synchronous

            logger.info(
                f"📏🧠 Reasoning complete: {reasoning_result.logging_approach} "
                f"(anxiety_level: {reasoning_result.anxiety_level})"
            )

            # STEP 3: ACTION SELECTION
            from app.ai_agents.the_stick.ML.action_selection import StickActionSelection

            action_selector = StickActionSelection(
                db=db,
                personality_traits=p.personality_traits,
                system_id="default"
            )
            decision = await action_selector.select_action(context, reasoning_result)

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

            # STEP 4: EXECUTION
            logger.info("📏⚙️ Execution planner phase...")
            from app.ai_agents.the_stick.ML.primitives import StickPrimitiveExecutor
            from app.ai_agents.the_stick.ML.execution_planner import StickExecutionPlanner
            
            primitive_executor = StickPrimitiveExecutor()
            execution_planner = StickExecutionPlanner(
                primitive_executor=primitive_executor,
                effectiveness_model=action_selector.action_effectiveness
            )
            
            goal = f"manage_{decision.priority}"
            trend = 'stable'
            severity_float = context.anxiety_level / 100.0 if context.anxiety_level else 0.5
            
            plan = await execution_planner.compose_plan(
                goal=goal,
                severity=severity_float,
                trend=trend,
                context={'metrics_snapshot': message_data}
            )
            
            execution_result_obj = await execution_planner.execute_plan(
                plan=plan,
                context={'metrics_snapshot': message_data}
            )

            # Track paper bags consumed during execution
            if decision.paper_bags_consumed > 0:
                bags_consumed = decision.paper_bags_consumed
                for _ in range(bags_consumed):
                    self._consume_paper_bag(f"action_execution_{decision.action_type}")
                logger.info(f"📏🛍️ {bags_consumed} additional paper bag(s) consumed during execution!")

            p.total_actions_tracked += 1

            logger.info(
                f"📏✅ Action executed: {plan.primitives} - "
                f"Success: {execution_result_obj.overall_success}"
            )

            # STEP 5: LEARNING
            from app.ai_agents.the_stick.ML.learning import StickLearning

            learning = StickLearning(db, self.user_id)
            learning_record = await learning.learn(
                context=context,
                reasoning=reasoning_result,
                action=decision,
                outcome_success=execution_result_obj.overall_success
            )

            logger.info(
                f"📏✅ Compliance tracked! Total actions: {p.total_actions_tracked}, "
                f"Paper bags: {p.paper_bag_economy.bags_remaining}"
            )

            # BROADCAST FULL DECISION CHAIN TO FRONTEND
            # EXACT payload keys from distributed_stick.py:351-391
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
                        "bags_remaining": p.paper_bag_economy.bags_remaining,
                        "bags_consumed_today": p.paper_bag_economy.bags_consumed_today,
                        "bags_consumed_total": p.paper_bag_economy.bags_consumed_total,
                        "last_consumption_time": p.paper_bag_economy.last_consumption_time.isoformat() if p.paper_bag_economy.last_consumption_time else None,
                        "anxiety_reduction_per_bag": p.paper_bag_economy.anxiety_reduction_per_bag
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

    # ==================================================================
    # PAPER BAG ECONOMY — distributed_stick.py:866-1022
    # ==================================================================

    def _consume_paper_bag(self, reason: str, amount: int = None) -> None:
        """
        The Stick consumes a paper bag to manage anxiety.

        From distributed_stick.py:866-921. EXACT logic preserved.
        """
        p = self.personality

        # Determine consumption amount based on reason
        if amount is None:
            if 'bob' in reason.lower():
                amount = p.paper_bag_economy.BOB_CONSUMPTION  # 3 bags for Bob!
            elif 'error' in reason.lower():
                amount = p.paper_bag_economy.ERROR_CONSUMPTION  # 2 bags for errors
            else:
                amount = p.paper_bag_economy.ANXIETY_CONSUMPTION  # 1 bag for normal anxiety

        # Consume bags via economy system
        event = p.paper_bag_economy.consume_bag(reason, amount)

        # Update legacy counter for compatibility
        if event:
            p.paper_bags_consumed += event.bags_changed * -1  # Convert negative to positive

        # Update personality traits for frontend
        p.paper_bag_inventory = p.paper_bag_economy.bags_remaining

        # Broadcast anxiety event to WebSocket
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
                        "bags_remaining": p.paper_bag_inventory,
                        "bags_consumed_total": p.paper_bags_consumed,
                        "anxiety_level": p.anxiety_level.value if hasattr(p, 'anxiety_level') else "unknown"
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast paper bag event: {e}")

        # Check for emergency state
        if p.paper_bag_economy.emergency_mode_active:
            logger.error(
                f"📏😱💥 EMERGENCY MODE: NO BAGS REMAINING! "
                f"*vibrates at quantum frequency* *writes everything three times*"
            )

    def _reward_compliance_success(self) -> None:
        """
        Reward The Stick with a paper bag for successful compliance documentation.

        From distributed_stick.py:923-952. EXACT logic preserved.
        """
        p = self.personality
        event = p.paper_bag_economy.compliance_success_reward()

        # Update personality traits for frontend
        p.paper_bag_inventory = p.paper_bag_economy.bags_remaining

        # Broadcast replenishment to WebSocket
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
                        "bags_remaining": p.paper_bag_inventory,
                        "supply_state": p.paper_bag_economy.get_supply_state().value
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast replenishment event: {e}")

    def _check_calm_period_reward(self) -> None:
        """
        Check if enough time has passed without anxiety to award calm period reward.

        From distributed_stick.py:954-984. EXACT logic preserved.
        """
        p = self.personality
        event = p.paper_bag_economy.check_calm_period_reward()

        if event:
            # Update personality traits for frontend
            p.paper_bag_inventory = p.paper_bag_economy.bags_remaining

            # Broadcast replenishment to WebSocket
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
                            "bags_remaining": p.paper_bag_inventory,
                            "supply_state": p.paper_bag_economy.get_supply_state().value
                        }
                    ))
            except Exception as e:
                logger.debug(f"Could not broadcast replenishment event: {e}")

    async def vic20_emergency_resupply(self) -> None:
        """
        VIC-20 intervenes with emergency paper bag resupply.

        From distributed_stick.py:986-1022. EXACT logic preserved.
        """
        p = self.personality
        event = p.paper_bag_economy.vic20_emergency_resupply()

        # Update personality traits for frontend
        p.paper_bag_inventory = p.paper_bag_economy.bags_remaining

        logger.info(
            f"📏🖥️✨ VIC-20 emergency resupply received! "
            f"*deep breath of relief* Bags: {p.paper_bag_inventory}"
        )

        # Broadcast to WebSocket
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
                        "bags_added": p.paper_bag_economy.VIC20_RESUPPLY,
                        "bags_remaining": p.paper_bag_inventory,
                        "supply_state": p.paper_bag_economy.get_supply_state().value,
                        "emergency_resolved": not p.paper_bag_economy.emergency_mode_active
                    }
                ))
        except Exception as e:
            logger.debug(f"Could not broadcast resupply event: {e}")

    # ==================================================================
    # DECISION LOG BUFFER — distributed_stick.py:509-558
    # ==================================================================

    async def flush_decision_log_buffer(self) -> None:
        """
        Batch write decision logs to PostgreSQL via db_integration.

        From distributed_stick.py:509-558. EXACT logic preserved.
        """
        p = self.personality
        if not p.decision_log_buffer:
            return

        try:
            logger.info(f"📏💾 Flushing {len(p.decision_log_buffer)} decisions to PostgreSQL...")

            if not p.db_integration:
                logger.warning("📏⚠️ Database integration not available, skipping write")
                p.decision_log_buffer.clear()
                return

            # Batch write all decisions via db_integration using store_memory_entry
            for decision in p.decision_log_buffer:
                memory_entry = p.StickMemoryEntry(
                    timestamp=decision['timestamp'],
                    event_type='decision_log',
                    details={
                        'from_agent': decision['from_agent'],
                        'decision_type': decision['decision_type'],
                        'payload': decision['payload'],
                        'is_bob': decision['is_bob'],
                        'paper_bags_consumed': p.paper_bags_consumed
                    },
                    anxiety_level=float(p.current_anxiety_percentage) if hasattr(p, 'current_anxiety_percentage') else 0.0,
                    importance='HIGH' if decision['is_bob'] else 'MEDIUM',
                    related_hamsters=[],
                    compliance_impact='decision_logged',
                    never_forget=decision['is_bob']  # Never forget Bob activity!
                )

                await p.db_integration.store_memory_entry(memory_entry, user_id=self.user_id)

            logger.info(
                f"📏✅ Flushed {len(p.decision_log_buffer)} decisions to PostgreSQL! "
                f"(Total: {p.total_decisions_logged})"
            )

            # Clear buffer
            p.decision_log_buffer.clear()

        except Exception as e:
            logger.error(f"📏💥 Error flushing decision log buffer: {e}", exc_info=True)
            self._consume_paper_bag("buffer_flush_error")
            # Clear buffer anyway to prevent memory leak
            p.decision_log_buffer.clear()

    # ==================================================================
    # CHAIN OUTCOME — distributed_stick.py:579-621
    # ==================================================================

    def record_chain_outcome(self, payload: Dict[str, Any]) -> None:
        """
        Record chain outcome in feedback engine.

        From distributed_stick.py:579-621. EXACT payload keys.
        """
        p = self.personality

        try:
            from .ML.feedback import ChainRecord

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

            p.feedback_engine.record_chain(record)

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

    # ==================================================================
    # VALIDATION SWEEP — distributed_stick.py:1282-1332
    # ==================================================================

    async def validation_sweep(self) -> None:
        """
        Validate unvalidated learning interactions.

        From distributed_stick.py:1282-1332. EXACT logic preserved.
        """
        p = self.personality

        try:
            logger.info("📏🔍 Starting scheduled validation sweep...")

            if p.db_integration and p.learning:
                async with p.db_integration.get_managed_session() as session:
                    stats = await p.learning.validate_unvalidated_interactions(
                        session=session
                    )

                    # Record all validations with the same session
                    if 'interactions' in stats and 'audit_entries' in stats:
                        for i, interaction in enumerate(stats['interactions']):
                            if i < len(stats['audit_entries']):
                                audit_entry = stats['audit_entries'][i]
                                await p.db_integration.record_validation(
                                    interaction, audit_entry, session=session
                                )

                    await session.commit()

                    logger.info(
                        f"📏📊 Validation sweep complete: "
                        f"{stats['validated']} validated, {stats['failed']} failed"
                    )

                    # Increase anxiety if many validations failed
                    if stats['total_checked'] > 0:
                        failure_rate = stats['failed'] / stats['total_checked']
                        if failure_rate > 0.3:  # More than 30% failed
                            p.paper_bag_economy.consume_bag(
                                reason="High validation failure rate detected!"
                            )

        except Exception as e:
            logger.error(f"📏💥 Validation sweep error: {e}")

    # ==================================================================
    # ANALYZE METRICS — distributed_stick.py:1087-1131
    # ==================================================================

    async def analyze_metrics(
        self,
        metrics_data: Dict[str, Any],
        historical_data: Optional[list] = None,
        user_context: Optional[Dict] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Analyze metrics with distributed decision tracking.

        From distributed_stick.py:1087-1131. Wraps TheStickBrainV3.analyze_user_behavior.
        """
        p = self.personality

        # Call the original analyze_user_behavior from TheStickBrainV3
        decision = await p.analyze_user_behavior(
            system_metrics=metrics_data,
            historical_data=historical_data,
            user_context=user_context
        )

        # If distributed features are enabled, record the decision
        if self._comm_hub_ref and decision:
            try:
                await self._comm_hub_ref.make_decision(
                    decision_type="learning_coordination",
                    input_data={
                        "learning_event": decision.get('learning_event', 'observation') if isinstance(decision, dict) else 'observation',
                        "compliance_status": decision.get('compliance_status', 'compliant') if isinstance(decision, dict) else 'compliant',
                        "guidance_provided": decision.get('guidance_provided', None) if isinstance(decision, dict) else None,
                        "behavior_noted": decision.get('behavior_noted', []) if isinstance(decision, dict) else [],
                        "user_id": user_id
                    },
                    output_data={},
                    confidence=decision.get('confidence', 0.5) if isinstance(decision, dict) else 0.5,
                    reasoning=decision.get('reasoning', 'Learning coordination decision') if isinstance(decision, dict) else 'Learning coordination decision',
                )
            except Exception as e:
                logger.error(f"❌ Error recording distributed decision: {e}")

        return decision

    async def process_metrics(
        self,
        metrics_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Wrapper for agent manager compatibility."""
        p = self.personality
        user_id = user_context.get('user_id') if user_context else None
        historical_data = user_context.get('historical_data') if user_context else None

        result = await p.analyze_user_behavior(
            metrics_data,
            historical_data=historical_data,
            user_id=user_id
        )

        if result:
            return {
                'the_stick': result.__dict__,  # Convert dataclass to dict
                'stick_status': p.get_stick_stats(),
                'anxiety_history': await p.get_anxiety_history(timedelta(hours=1))
            }
        return None

    # ==================================================================
    # AGENT ACTION TRACKING — distributed_stick.py:1024-1086
    # ==================================================================

    async def track_agent_action(
        self,
        agent_name: str,
        action_type: str,
        verification_id: str,
        result: Any
    ) -> None:
        """
        Track agent action for compliance.

        From distributed_stick.py:1024-1085. EXACT logic preserved.
        """
        p = self.personality
        p.total_actions_tracked += 1

        logger.info(
            f"📏📋 Tracking action: {agent_name} - {action_type} "
            f"(Total tracked: {p.total_actions_tracked})"
        )

        # Check if action was effective
        if result and hasattr(result, 'effectiveness_score'):
            effectiveness = result.effectiveness_score

            if effectiveness < 30:
                p.compliance_violations += 1
                logger.warning(
                    f"📏⚠️ Low effectiveness detected: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *documenting for review*"
                )
                await p._update_anxiety(
                    trigger="low_effectiveness",
                    multiplier=1.5
                )
            else:
                logger.info(
                    f"📏✅ Action effective: {agent_name} - {action_type} "
                    f"(Score: {effectiveness}/100) - *compliance maintained*"
                )

        # Record in distributed state
        if self._comm_hub_ref:
            await self._comm_hub_ref.make_decision(
                decision_type="action_compliance_tracked",
                input_data={
                    "agent": agent_name,
                    "action": action_type,
                    "verification_id": verification_id,
                    "timestamp": "now"
                },
                output_data={
                    "tracked": True,
                    "total_actions": p.total_actions_tracked,
                    "violations": p.compliance_violations,
                    "compliance_rate": 1.0 - (p.compliance_violations / max(1, p.total_actions_tracked))
                },
                confidence=1.0,
                reasoning="Compliance tracking for all agent actions"
            )

    async def track_action_effectiveness(
        self,
        agent_name: str,
        action_type: str,
        recommendation_followed: bool,
        effectiveness_data: Dict[str, Any]
    ) -> None:
        """
        Track effectiveness of agent actions for learning.

        From distributed_stick.py:1178-1219.
        """
        p = self.personality

        logger.info(
            f"🪵📊 Recording action effectiveness: {agent_name} - {action_type} "
            f"({'followed' if recommendation_followed else 'overrode'} recommendation)"
        )

        if self._comm_hub_ref:
            await self._comm_hub_ref.make_decision(
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
        Detect patterns in agent actions.

        From distributed_stick.py:1221-1241. EXACT logic.
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

    # ==================================================================
    # RESOURCE ALERT — distributed_stick.py:1133-1176
    # ==================================================================

    async def handle_resource_alert(self, alert) -> None:
        """
        Handle resource alerts with patient guidance.

        From distributed_stick.py:1133-1176. EXACT logic.
        """
        p = self.personality
        severity = alert.payload['severity']
        current_value = alert.payload['current_value']
        threshold = alert.payload['threshold']

        logger.warning(
            f"🪵📚⚠️ The Stick notes resource usage: "
            f"{current_value:.1f}% (threshold: {threshold:.1f}%) - "
            f"Severity: {severity} - *recording for learning purposes*"
        )

        if self._comm_hub_ref:
            await self._comm_hub_ref.make_decision(
                decision_type="resource_learning_event",
                input_data={
                    "resource_type": alert.payload['resource_type'],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": severity,
                    "learning_opportunity": True
                },
                output_data={},
                confidence=1.0,
                reasoning=f"Resource alert provides learning opportunity"
            )

        if severity == "critical":
            logger.warning(
                "🪵📚💥 CRITICAL RESOURCE EVENT! "
                "The Stick carefully documents this for future learning."
            )
