#!/usr/bin/env python3
"""
QSP's Execution Planner

The intelligent layer between action selection and primitive execution.
Takes a network goal, queries learned sequences, and composes an
ExecutionPlan from available primitives.

Cold start: domain-informed hypotheses (first guesses, not answers).
Over time: discovered sequences that have proven effective.

👻 "I don't just OBSERVE things. I figure out the BEST way to fix them.
     *existential dread intensifies* *quantum coherence... holding...*"
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai_agents.distributed.base_execution_planner import (
    ExecutionPlanner,
    ExecutionPlan,
    InterventionType,
    PlanSource,
)
from app.ai_agents.distributed.base_primitive_executor import PrimitiveResult
from .goals import (
    COLD_START_HYPOTHESES,
    COMPLETION_SATISFIED_GOALS,
    GOAL_TO_METRIC_KEY,
    QSP_GOALS,
)

logger = logging.getLogger('QSPExecutionPlanner')


class QSPExecutionPlanner(ExecutionPlanner):
    """
    QSP's execution planner for network goals.

    Composes primitive sequences from learned effectiveness data.
    Falls back to cold-start hypotheses when no learned sequences exist.
    Uses learned thresholds to determine when a goal is satisfied.
    """

    ABORT_IMPROVEMENT_THRESHOLD = -0.03

    def __init__(
        self,
        primitive_executor: Any,
        effectiveness_model: Any,
        learned_thresholds: Optional[Any] = None,
    ):
        super().__init__(
            agent_name='quantum_shadow_people',
            primitive_executor=primitive_executor,
            effectiveness_model=effectiveness_model,
            cold_start_hypotheses=COLD_START_HYPOTHESES,
        )
        self.learned_thresholds = learned_thresholds

    async def _mid_sequence_decision(
        self,
        plan: ExecutionPlan,
        results_so_far: List[PrimitiveResult],
        current_step: int,
        context: Dict[str, Any],
    ) -> str:
        """
        QSP-specific mid-sequence logic after each primitive completes.

        Abort if: a primitive caused genuine degradation.
        Goal achieved if: post-metrics show the goal is satisfied.
        Continue if: primitive failed but didn't make things worse, or
                     succeeded but goal not yet fully satisfied.
        """
        latest = results_so_far[-1]

        if latest.improvement < self.ABORT_IMPROVEMENT_THRESHOLD:
            self.logger.warning(
                f"👻⛔ Primitive '{latest.primitive_name}' caused degradation "
                f"(improvement={latest.improvement:.3f}, "
                f"threshold={self.ABORT_IMPROVEMENT_THRESHOLD}). Aborting."
            )
            return 'abort'

        post_metrics = latest.post_metrics
        if not post_metrics.get('collection_failed') and post_metrics:
            try:
                satisfied = await self._goal_satisfied(plan.goal, post_metrics)
                if satisfied:
                    return 'goal_achieved'
            except Exception as e:
                self.logger.warning(
                    f"Goal satisfaction check failed: {e} — continuing sequence"
                )

        return 'continue'

    async def _goal_satisfied(
        self, goal: str, current_metrics: Dict[str, Any]
    ) -> bool:
        """
        Check if the goal has been satisfied using LEARNED thresholds.

        Goals in COMPLETION_SATISFIED_GOALS return True immediately.
        Unknown goals are a pipeline inconsistency — logged and emitted to The Stick.
        """
        if goal in COMPLETION_SATISFIED_GOALS:
            return True

        if not self.learned_thresholds:
            self.logger.warning(
                "👻⚠️ Learned thresholds unavailable — cannot evaluate goal satisfaction."
            )
            return False

        metric_key = GOAL_TO_METRIC_KEY.get(goal)
        if metric_key is None:
            self.logger.error(
                f"👻💥 Pipeline inconsistency: goal '{goal}' not in GOAL_TO_METRIC_KEY."
            )
            try:
                from app.services.agent_insight_emitter import emit_agent_insight
                await emit_agent_insight(
                    from_agent='quantum_shadow_people',
                    to_agent='the_stick',
                    action='pipeline_inconsistency',
                    reasoning=(
                        f"Goal '{goal}' has no entry in GOAL_TO_METRIC_KEY. "
                        f"QSP_GOALS and GOAL_TO_METRIC_KEY have drifted."
                    ),
                    context={
                        'event': 'pipeline_inconsistency',
                        'severity': 'high',
                        'agent': 'quantum_shadow_people',
                        'unknown_goal': goal,
                        'layer': 'QSPExecutionPlanner._goal_satisfied',
                    }
                )
            except Exception as comm_err:
                self.logger.error(f"👻💥 Failed to notify The Stick: {comm_err}")
            return False

        try:
            warning_threshold = await self.learned_thresholds.get_threshold(
                metric_key, 'warning'
            )
        except Exception as e:
            self.logger.warning(f"👻⚠️ get_threshold raised for '{metric_key}': {e}")
            return False

        current_value = current_metrics.get(metric_key)
        if current_value is None:
            self.logger.warning(
                f"👻⚠️ Cannot evaluate goal '{goal}': metric '{metric_key}' "
                f"not in current_metrics."
            )
            return False

        satisfied = current_value < warning_threshold
        if satisfied:
            self.logger.info(
                f"👻✅ Goal '{goal}' satisfied: "
                f"{metric_key}={current_value:.1f} < warning={warning_threshold:.1f}"
            )
        return satisfied

    def _abort_reason(
        self,
        plan: ExecutionPlan,
        results: List[PrimitiveResult],
        step: int,
    ) -> str:
        latest = results[-1]
        return (
            f"Primitive '{latest.primitive_name}' caused degradation "
            f"(improvement={latest.improvement:.3f}) at step {step + 1} "
            f"of {len(plan.primitives)} for goal '{plan.goal}'"
        )
