"""
The Hamsters — ML Pipeline Orchestrator
========================================

Pure ML pipeline. No messaging. No frontend emission.

Receives coordination context from the communication layer.
Runs perception → reasoning → action selection → learning → execution.
Returns structured result for communication and websocket layers.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("Hamsters.Orchestrator")


class HamstersOrchestrator:
    """
    Orchestrates the Hamsters' ML pipeline.

    Runs perception → reasoning → action selection → execution → learning.
    Reads and writes personality state.
    Returns results for communication and websocket layers.
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        """
        Args:
            personality: HamstersPersonalityState instance
            db_getter: Database session factory
            user_id: User ID for database writes
        """
        self.personality = personality
        self.db_getter = db_getter
        self.user_id = user_id

        # Set by agent entry point after communication init
        self._comm_hub_ref = None

    async def run_pipeline(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run the complete ML pipeline for a coordination request.

        Args:
            payload: COORDINATION_REQUEST payload from VIC-20

        Returns:
            Complete pipeline result dict, or None on failure.
            Contains all data needed by communication and websocket layers.
        """
        # Daily reset at top of every pipeline run
        self.personality._reset_daily_counters_if_needed()

        resource_type = payload.get('resource_type', 'unknown')
        severity = payload.get('severity', 'unknown')
        recommendation = payload.get('recommendation', {})
        current_value = payload.get('current_value', 0)
        threshold = payload.get('threshold', 0)

        logger.info(f"\n{'='*80}")
        logger.info(f"🐹🎯 HAMSTERS ML PIPELINE INITIATED")
        logger.info(f"{'='*80}")
        logger.info(
            f"🐹📬 Resource: {resource_type} at {current_value:.1f}% "
            f"(severity: {severity}, VIC-20 suggests: {recommendation.get('action', 'unknown')})"
        )

        try:
            # Lazy imports — ML layers stay untouched
            from .ML.perception import HamstersPerception
            from .ML.reasoning import HamstersReasoning
            from .ML.action_selection import HamstersActionSelection
            from .ML.learning import HamstersLearning
            from .ML.primitive_executor import HamsterPrimitiveExecutor
            from .ML.execution_planner import HamsterExecutionPlanner

            db_gen = self.db_getter()
            async for db in db_gen:
                # === STEP 1: PERCEPTION ===
                logger.info("🐹👁️ Perception phase (telepathic assessment)...")
                perception = HamstersPerception(db, self.personality.personality_traits)

                storage_alert = {
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold': threshold,
                    'severity': severity,
                    'fragmentation': payload.get('fragmentation', 0.0),
                    'available_space_gb': payload.get('available_space_gb', 0.0),
                    'inode_usage': payload.get('inode_usage', 0.0),
                }

                context = await perception.perceive(storage_alert)

                # Sync beer consumption from perception to personality state
                total_beers = context.steve_beers_today + context.bob_beers_today + context.carl_beers_today
                if total_beers > 0:
                    logger.info(
                        f"🐹🍺 Beer consumption: Steve={context.steve_beers_today}, "
                        f"Bob={context.bob_beers_today}, Carl={context.carl_beers_today} "
                        f"(total: {total_beers})"
                    )
                    # Sync to personality state
                    self.personality.consume_beer('steve', context.steve_beers_today, 'pipeline perception', 0.5)
                    self.personality.consume_beer('bob', context.bob_beers_today, 'pipeline perception', 0.5)
                    self.personality.consume_beer('carl', context.carl_beers_today, 'pipeline perception', 0.5)

                if context.bob_proximity:
                    self.personality.bob_at_cupboard = context.bob_proximity.bob_at_cupboard

                # Duct tape assessment from perception
                if context.duct_tape_assessment:
                    logger.info(
                        f"🐹📏 Carl's duct tape assessment: {context.duct_tape_assessment.total_rolls:.1f} rolls "
                        f"({context.duct_tape_assessment.job_complexity} job)"
                    )

                # Bob's cupboard check
                if context.bob_proximity and context.bob_proximity.bob_at_cupboard:
                    logger.warning(
                        f"🐹⚠️ BOB AT SUPPLY CUPBOARD! Alerting The Stick! "
                        f"Panic level: {context.bob_proximity.stick_panic_level:.2f}"
                    )
                    self.personality.bob_raids_cupboard(
                        context.bob_proximity.items_acquired if context.bob_proximity.items_acquired else []
                    )

                logger.info(
                    f"🐹✅ Perception complete: complexity={context.complexity_level:.2f}, "
                    f"ingenuity={context.ingenuity_required:.2f}"
                )

                # === STEP 2: REASONING ===
                logger.info("🐹🧠 Reasoning phase (telepathic consensus)...")
                reasoning_engine = HamstersReasoning(self.personality.personality_traits)
                reasoning = reasoning_engine.reason(context)

                logger.info(f"🐹💭 Steve: {reasoning.steve_assessment.recommended_fix}")
                logger.info(f"🐹💭 Bob: {reasoning.bob_assessment.recommended_fix}")
                logger.info(f"🐹💭 Carl: {reasoning.carl_assessment.recommended_fix}")
                logger.info(
                    f"🐹✅ Consensus reached: {reasoning.consensus_fix}, "
                    f"confidence={reasoning.consensus_confidence:.2f}, "
                    f"disagreement={reasoning.disagreement_level:.2f}"
                )

                # Update telepathic consensus in personality
                self.personality.record_telepathic_consensus(reasoning.consensus_confidence)

                # === STEP 3: ACTION SELECTION ===
                logger.info("🐹⚡ Action selection phase...")
                action_selector = HamstersActionSelection(
                    self.personality.personality_traits, db, self.user_id
                )
                action = await action_selector.select_action(context, reasoning)

                logger.info(
                    f"🐹✅ Goal selected: {action.goal}, "
                    f"beers={action.total_beers_consumed}, "
                    f"duct_tape={action.duct_tape_rolls:.1f} rolls"
                )

                if action.sudo_command:
                    logger.info(f"🐹🔧 Sudo hint: {action.sudo_command}")

                # Carl calculates duct tape for this job
                complexity_map = {
                    'low': 'simple', 'medium': 'moderate',
                    'high': 'complex', 'critical': 'quantum'
                }
                tape_complexity = complexity_map.get(str(severity).lower(), 'moderate')
                duct_tape_job = self.personality.carl_calculates_duct_tape(tape_complexity, action.goal)

                # === STEP 4: LEARNING ===
                logger.info("🐹📚 Learning phase (pre-execution)...")
                learning = HamstersLearning(db, self.user_id)
                learning_record = await learning.learn(context, reasoning, action)

                logger.info("🐹💾 Learning record stored in PostgreSQL")

                # === STEP 5: EXECUTION ===
                logger.info(f"🐹🔧 Execution phase: goal='{action.goal}'...")

                primitive_executor = HamsterPrimitiveExecutor(agent_name='hamsters')
                planner = HamsterExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=learning.action_effectiveness,
                    learned_thresholds=learning.learned_thresholds,
                )

                severity_float = {
                    'low': 0.2, 'medium': 0.4, 'warning': 0.5,
                    'high': 0.7, 'critical': 0.9, 'emergency': 1.0
                }.get(str(severity).lower(), 0.5)

                plan = await planner.compose_plan(
                    goal=action.goal,
                    severity=severity_float,
                    trend='rising',
                    context={},
                )

                execution_result = await planner.execute_plan(plan, context={})

                # Record sequence outcome
                await learning.record_sequence_outcome(
                    execution_result,
                    system_id=getattr(self, 'system_id', 'hamsters')
                )

                # Build metrics_before / metrics_after
                first_result = execution_result.primitive_results[0] if execution_result.primitive_results else None
                last_result = execution_result.primitive_results[-1] if execution_result.primitive_results else None

                metrics_before = (
                    first_result.pre_metrics if first_result and not first_result.pre_metrics.get('collection_failed')
                    else {'disk_usage': context.disk_usage_percent, 'cpu_usage': 0, 'memory_usage': 0}
                )
                metrics_after = (
                    last_result.post_metrics if last_result and not last_result.post_metrics.get('collection_failed')
                    else {'disk_usage': context.disk_usage_percent, 'cpu_usage': 0, 'memory_usage': 0}
                )

                disk_before = metrics_before.get('disk_usage_percent', metrics_before.get('disk_usage', 0))
                disk_after = metrics_after.get('disk_usage_percent', metrics_after.get('disk_usage', 0))
                disk_improvement_pct = (
                    ((disk_before - disk_after) / disk_before * 100.0)
                    if disk_before > 0 else 0.0
                )

                # Update learning record outcome
                pre_metrics_dict = {
                    'disk_usage_percent': disk_before,
                    'fragmentation_level': context.fragmentation_level,
                    'inode_usage_percent': context.inode_usage_percent,
                }
                post_metrics_dict = {
                    'disk_usage_percent': disk_after,
                    'fragmentation_level': context.fragmentation_level,
                    'inode_usage_percent': context.inode_usage_percent,
                }

                await learning.update_outcome(
                    learning_record,
                    success=execution_result.overall_success,
                    outcome_notes=(
                        execution_result.abort_reason
                        if execution_result.was_aborted
                        else f"improvement={execution_result.overall_improvement:.3f}"
                    ),
                    pre_metrics=pre_metrics_dict,
                    post_metrics=post_metrics_dict,
                )

                # Record success in personality
                self.personality.record_analysis(execution_result.overall_success)

                if execution_result.overall_success:
                    logger.info(
                        f"🐹✅ Execution successful: goal='{action.goal}', "
                        f"steps={execution_result.steps_completed}/{execution_result.steps_planned}, "
                        f"improvement={execution_result.overall_improvement:.3f}, "
                        f"duration={execution_result.total_duration_seconds:.1f}s"
                    )
                else:
                    logger.warning(
                        f"🐹⚠️ Execution incomplete: goal='{action.goal}', "
                        f"aborted={execution_result.was_aborted}, "
                        f"reason={execution_result.abort_reason}"
                    )

                # Request The Stick validation for learned thresholds
                try:
                    from app.core.database import get_async_db
                    await learning.learned_thresholds.request_stick_validation(
                        metric_name='disk_usage',
                        threshold_level='warning' if disk_before < 90 else 'critical',
                        learned_value=await learning.learned_thresholds.get_threshold('disk_usage', 'warning'),
                        default_value=80.0,
                        db_getter=get_async_db,
                    )
                    logger.info("🐹📏 Threshold validation request sent to The Stick")
                    
                    metric_pattern = f"disk_{trend}" if trend else "disk_gradual_growth_warning"
                    await learning.action_effectiveness.request_stick_validation(
                        action=action.goal,
                        metric_pattern=metric_pattern,
                        db_getter=get_async_db
                    )
                    logger.info("🐹🎯 Action effectiveness validation request sent to The Stick")
                except Exception as e:
                    logger.error(f"🐹⚠️ Validation request failed: {e}")

                logger.info(f"{'='*80}")
                logger.info(f"🐹✅ HAMSTERS ML PIPELINE COMPLETE")
                logger.info(f"{'='*80}\n")

                # === BUILD RESULT DICT ===
                return {
                    'context': context,
                    'reasoning': reasoning,
                    'action': action,
                    'action_selector': action_selector,
                    'learning_record': learning_record,
                    'learning': learning,
                    'plan': plan,
                    'execution_result': execution_result,
                    'duct_tape_job': duct_tape_job,
                    'metrics_before': {'disk_usage': disk_before},
                    'metrics_after': {'disk_usage': disk_after},
                    'disk_improvement_pct': disk_improvement_pct,
                    'overall_success': execution_result.overall_success,
                    'resource_type': resource_type,
                    'severity': severity,
                    'recommendation': recommendation,
                    'payload': payload,
                }

        except Exception as e:
            logger.error(f"🐹💥 HAMSTERS ML PIPELINE FAILED: {e}", exc_info=True)

            self.personality.record_analysis(success=False)

            # Re-raise with context for communication layer to handle emergency
            raise
