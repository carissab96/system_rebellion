"""
Terry the Meth Snail — ML Pipeline Orchestrator
==================================================

The decomposed god function.

Receives coordination context from the communication layer.
Runs the ML pipeline: perception → reasoning → action selection → execution → learning.
Updates personality state with results.
Returns structured results for communication and websocket layers.

Does not handle messaging. Does not emit to frontend.
Pure pipeline orchestration.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("MethSnail.Orchestrator")


class TerryOrchestrator:
    """
    Orchestrates Terry's ML pipeline.

    Runs perception → reasoning → action selection → execution → learning.
    Reads and writes personality state.
    Returns results for communication and websocket layers.
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        """
        Args:
            personality: TerryPersonalityState instance
            db_getter: Database session factory
            user_id: User ID for database writes
        """
        self.personality = personality
        self.db_getter = db_getter
        self.user_id = user_id
        self._comm_hub_ref = None  # Set by TerryAgent after communication init

    async def run_pipeline(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run the complete ML pipeline for a coordination request.

        Args:
            payload: COORDINATION_REQUEST payload from VIC-20

        Returns:
            Complete pipeline result dict, or None on failure.
            Contains all data needed by communication and websocket layers.
        """
        resource_type = payload.get('resource_type', 'unknown')
        severity = payload.get('severity', 'unknown')
        recommendation = payload.get('recommendation', {})
        current_value = payload.get('current_value', 0)
        threshold = payload.get('threshold', 0)
        full_metrics = payload.get('full_metrics', {})

        result = None

        try:
            # Get database session
            db_gen = self.db_getter()
            async for db in db_gen:

                # STEP 1: PERCEPTION
                from app.ai_agents.meth_snail.ML.perception import TerryPerception

                perception = TerryPerception(
                    db,
                    self.personality.personality_traits,
                    db_integration=self.personality.db_integration
                )
                context = await perception.perceive({
                    'resource_type': resource_type,
                    'severity': severity,
                    'current_value': current_value,
                    'threshold': threshold,
                    'recommendation': recommendation,
                    'full_metrics': full_metrics
                })

                # Sync shell spins to personality state
                shell_spin_count = len(perception.shell_spin_incidents)
                if shell_spin_count > 0:
                    self.personality.shell_spin_incidents.extend(
                        perception.shell_spin_incidents
                    )
                    self.personality.metrics_quality_stats['shell_spins_total'] += shell_spin_count
                    logger.info(
                        f"🐌📊 Synced {shell_spin_count} shell spin(s). "
                        f"Total: {len(self.personality.shell_spin_incidents)}"
                    )

                logger.info("🐌👁️ Perception complete")

                # STEP 2: REASONING
                from app.ai_agents.meth_snail.ML.reasoning import TerryReasoning

                reasoning = TerryReasoning(db)
                reasoning_result = await reasoning.reason(context)

                logger.info(
                    f"🐌🧠 Reasoning: {reasoning_result.root_cause} → "
                    f"{reasoning_result.recommended_action} "
                    f"(confidence: {reasoning_result.action_confidence:.2f})"
                )

                # STEP 3: ACTION SELECTION
                from app.ai_agents.meth_snail.ML.action_selection import TerryActionSelection

                action_selector = TerryActionSelection(
                    comm_hub=self._comm_hub_ref,
                    db=db,
                    system_id=payload.get('system_id', 'default')
                )
                decision = await action_selector.select_action(reasoning_result, context)

                # Log personality behaviors
                if decision.energy_drink_consumed:
                    logger.info(
                        f"🐌☕ Energy drink "
                        f"#{action_selector.energy_drink_system.energy_drinks_today}! "
                        f"*chugs and spins faster*"
                    )
                if decision.hawk_veto:
                    logger.warning(
                        f"🐌❌ HAWK VETO! "
                        f"Total vetoes: {action_selector.energy_drink_system.hawk_vetoes}"
                    )

                self.personality._last_energy_drink_system = (
                    action_selector.energy_drink_system
                )

                logger.info(
                    f"🐌⚡ Action: {decision.action} "
                    f"({'FOLLOWING VIC-20' if decision.followed_vic20 else 'OVERRIDING VIC-20'})"
                )

                # Track overrides in personality
                if not decision.followed_vic20:
                    self.personality.total_overrides += 1

                # STEP 4: EXECUTION
                logger.info(f"🐌💨💨 Executing {decision.action}!")

                from app.ai_agents.meth_snail.ML.primitive_executor import (
                    TerryPrimitiveExecutor
                )
                from app.ai_agents.meth_snail.ML.execution_planner import (
                    TerryExecutionPlanner,
                    COLD_START_HYPOTHESES
                )

                primitive_executor = TerryPrimitiveExecutor()
                execution_planner = TerryExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=action_selector.action_effectiveness,
                    learned_thresholds=action_selector.learned_thresholds,
                )

                goal = self._action_to_goal(
                    decision.action, reasoning_result, context
                )
                severity_float = action_selector._severity_to_float(reasoning_result)
                trend = (
                    context.full_metrics.get('trend', 'rising')
                    if hasattr(context, 'full_metrics')
                    else 'rising'
                )

                plan = await execution_planner.compose_plan(
                    goal=goal,
                    severity=severity_float,
                    trend=trend,
                    context={
                        **decision.parameters,
                        'system_id': payload.get('system_id', 'default'),
                    }
                )

                execution_result_obj = await execution_planner.execute_plan(
                    plan=plan,
                    context={
                        **decision.parameters,
                        'system_id': payload.get('system_id', 'default'),
                    }
                )

                # Extract metrics from execution result
                if execution_result_obj.primitive_results:
                    first = execution_result_obj.primitive_results[0]
                    last = execution_result_obj.primitive_results[-1]
                    metrics_before = (
                        first.pre_metrics
                        if not first.pre_metrics.get('collection_failed')
                        else {
                            'cpu_usage': full_metrics.get('cpu_usage', 0),
                            'memory_usage': full_metrics.get('memory_usage', 0),
                            'disk_usage': full_metrics.get('disk_usage', 0),
                        }
                    )
                    metrics_after = (
                        last.post_metrics
                        if not last.post_metrics.get('collection_failed')
                        else metrics_before
                    )
                else:
                    metrics_before = {
                        'cpu_usage': full_metrics.get('cpu_usage', 0),
                        'memory_usage': full_metrics.get('memory_usage', 0),
                        'disk_usage': full_metrics.get('disk_usage', 0),
                    }
                    metrics_after = metrics_before

                # Normalize keys
                metrics_before = {
                    'cpu_usage': metrics_before.get('cpu_usage', 0),
                    'memory_usage': metrics_before.get('memory_usage', 0),
                    'disk_usage': metrics_before.get(
                        'disk_usage',
                        metrics_before.get('disk_usage_percent', 0)
                    ),
                }
                metrics_after = {
                    'cpu_usage': metrics_after.get('cpu_usage', 0),
                    'memory_usage': metrics_after.get('memory_usage', 0),
                    'disk_usage': metrics_after.get(
                        'disk_usage',
                        metrics_after.get('disk_usage_percent', 0)
                    ),
                }

                # Build action result
                action_result = {
                    'success': execution_result_obj.overall_success,
                    'improvement': execution_result_obj.overall_improvement,
                    'duration_seconds': execution_result_obj.total_duration_seconds,
                    'plan_source': execution_result_obj.plan.source.value,
                    'steps_completed': execution_result_obj.steps_completed,
                    'steps_planned': execution_result_obj.steps_planned,
                    'aborted': execution_result_obj.was_aborted,
                    'abort_reason': execution_result_obj.abort_reason,
                    'error': (
                        execution_result_obj.abort_reason
                        if execution_result_obj.was_aborted
                        else None
                    ),
                }

                logger.info(
                    f"🐌📊 Execution: {execution_result_obj.steps_completed}/"
                    f"{execution_result_obj.steps_planned} steps, "
                    f"improvement={execution_result_obj.overall_improvement:.3f}"
                )

                # STEP 5: LEARNING
                from app.ai_agents.meth_snail.ML.learning import TerryLearning

                learning = TerryLearning(db, self.personality.personality_traits)
                learning_record = await learning.learn(
                    context=context,
                    reasoning_result=reasoning_result,
                    decision=decision,
                    execution_result={
                        'success': action_result.get('success', False),
                        'metrics_before': metrics_before,
                        'metrics_after': metrics_after
                    },
                    action_selector=action_selector,
                    user_id=self.user_id
                )

                logger.info(
                    f"🐌📚 Learning: {decision.action} "
                    f"{'SUCCEEDED' if learning_record.success else 'FAILED'}"
                )

                # Calculate overall improvement
                cpu_imp = metrics_before['cpu_usage'] - metrics_after['cpu_usage']
                mem_imp = metrics_before['memory_usage'] - metrics_after['memory_usage']
                disk_imp = metrics_before['disk_usage'] - metrics_after['disk_usage']
                overall_improvement = max(cpu_imp, mem_imp, disk_imp)

                # Build insight context for websocket emission
                insight_context = {
                    "resource_type": resource_type,
                    "action": decision.action,
                    "followed_vic20": decision.followed_vic20,
                    "severity": severity,
                    "current_value": current_value,
                    "threshold": threshold,
                    "confidence": decision.confidence,
                    "root_cause": reasoning_result.root_cause,
                    "shell_spins": shell_spin_count,
                    "data_quality_score": context.data_quality_score,
                    "energy_drink_consumed": decision.energy_drink_consumed,
                    "hawk_veto": decision.hawk_veto,
                    "energy_drinks_today": (
                        action_selector.energy_drink_system.energy_drinks_today
                    ),
                    "exploration_rate": action_selector.epsilon,
                    "cache_clear_bias": action_selector.cache_clear_bias
                }

                # Return everything communication and websocket layers need
                result = {
                    'context': context,
                    'reasoning_result': reasoning_result,
                    'decision': decision,
                    'action_selector': action_selector,
                    'action_result': action_result,
                    'execution_result': execution_result_obj,
                    'learning_record': learning_record,
                    'metrics_before': metrics_before,
                    'metrics_after': metrics_after,
                    'full_metrics': full_metrics,
                    'overall_improvement': overall_improvement,
                    'insight_context': insight_context,
                    'shell_spin_count': shell_spin_count,
                }

                # Break after first db session iteration
                break

            return result

        except Exception as e:
            logger.error(f"🐌💥 Pipeline failed: {e}", exc_info=True)
            raise

    def _action_to_goal(self, action: str, reasoning_result, context) -> str:
        """
        Map action name from action_selection to execution planner goal.

        action_selection picks WHAT to do (e.g. 'emergency_cache_clear').
        The execution planner needs WHY (e.g. 'memory_critical').
        This mapping bridges the two vocabularies.
        """
        root_cause = getattr(reasoning_result, 'root_cause', 'unknown')
        severity = getattr(reasoning_result, 'severity', 'moderate')

        ACTION_TO_GOAL = {
            'emergency_cache_clear':        'memory_critical',
            'clear_cache':                  'cache_bloat',
            'kill_memory_hog':              'memory_leak_suspected',
            'optimize_memory_allocation':   'memory_high',
            'restart_service':              'memory_critical',
            'throttle_cpu_intensive_tasks': 'cpu_high',
            'adjust_process_priority':      'cpu_high',
            'monitor':                      'unknown_resource_issue',
            'escalate':                     'unknown_resource_issue',
        }

        ROOT_CAUSE_TO_GOAL = {
            'memory_thrashing':     'memory_thrashing',
            'memory_leak':          'memory_leak_suspected',
            'cache_bloat':          'cache_bloat',
            'high_memory_usage':    'memory_high',
            'critical_memory':      'memory_critical',
            'high_cpu_usage':       'cpu_high',
            'cpu_runaway':          'cpu_runaway_process',
            'cpu_spike':            'cpu_load_spike',
            'swap_pressure':        'swap_high',
            'oom_risk':             'oom_imminent',
            'preventive':           'preventive_optimization',
        }

        # Try direct action mapping first
        goal = ACTION_TO_GOAL.get(action)
        if goal:
            return goal

        # Try root cause mapping
        goal = ROOT_CAUSE_TO_GOAL.get(root_cause)
        if goal:
            return goal

        # Severity-based fallback
        if isinstance(severity, str):
            severity_lower = severity.lower()
            if severity_lower in ('critical', 'emergency'):
                return 'memory_critical'
            elif severity_lower == 'high':
                return 'memory_high'

        return 'unknown_resource_issue'
