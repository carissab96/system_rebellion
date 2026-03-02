#!/usr/bin/env python3
"""
Hamsters' Execution Planner

The intelligent layer between action selection and primitive execution.
Takes a storage goal, queries learned sequences, and composes an
ExecutionPlan from available primitives.

Cold start: domain-informed hypotheses (first guesses, not answers).
Over time: discovered sequences that have proven effective.

🐹🐹🐹 "We don't just DO things. We figure out the BEST way to do things.
         *Steve measures twice* *Bob grabs beer* *Carl calculates duct tape*"
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai_agents.distributed.message_protocol import MessageType, Priority
from app.ai_agents.distributed.base_execution_planner import (
    ExecutionPlanner,
    ExecutionPlan,
    InterventionType,
    PlanSource,
)
from app.ai_agents.distributed.base_primitive_executor import PrimitiveResult

logger = logging.getLogger('HamstersExecutionPlanner')


# =============================================================================
# Goal vocabulary — shared with action_selection.py
# These are PROBLEMS, not solutions. The planner figures out how to solve them.
# =============================================================================

STORAGE_GOALS = [
    # Disk space
    'disk_full',                  # Critical — immediate action needed
    'disk_high',                  # Warning — trending toward critical

    # Fragmentation
    'fragmentation_critical',     # Severe — impacting performance
    'fragmentation_high',         # Notable — worth addressing

    # Inodes
    'inode_exhaustion',           # Critical — running out of inodes
    'inode_high',                 # Warning — inodes getting scarce

    # Logs
    'log_overflow',               # Logs consuming excessive space

    # Performance
    'slow_disk_io',               # I/O performance degraded
    'ssd_needs_trim',             # SSD optimization needed

    # Compound
    'disk_full_and_fragmented',   # Multiple simultaneous issues

    # Maintenance
    'preventive_maintenance',     # Nothing broken, routine optimization

    # Fallback
    'unknown_storage_issue',      # Can't classify — needs investigation
]


# =============================================================================
# Cold start hypotheses — domain-informed starting points.
# These are NOT answers. They're first guesses that ML improves upon.
# The system confirms or discovers better sequences through experience.
# =============================================================================

COLD_START_HYPOTHESES: Dict[str, List[str]] = {
    'disk_full':                ['rm_temp'],
    'disk_high':                ['rm_temp'],
    'fragmentation_critical':   ['e4defrag'],
    'fragmentation_high':       ['e4defrag'],
    'inode_exhaustion':         ['rm_temp'],
    'inode_high':               ['rm_temp'],
    'log_overflow':             ['logrotate'],
    'slow_disk_io':             ['fstrim'],
    'ssd_needs_trim':           ['fstrim'],
    # Domain knowledge: clear space BEFORE defragging — defrag needs room to work.
    # The system will confirm or improve this hypothesis through experience.
    'disk_full_and_fragmented': ['rm_temp', 'e4defrag'],
    'preventive_maintenance':   ['fstrim'],
    'unknown_storage_issue':    ['rm_temp'],
}


class HamsterExecutionPlanner(ExecutionPlanner):
    """
    Hamsters' execution planner for storage goals.

    Composes primitive sequences from learned effectiveness data.
    Falls back to cold start hypotheses when no learned sequences exist.
    Uses learned thresholds to determine when a goal is satisfied.
    """

    # Negative improvement tolerance — small negative values may be measurement noise.
    # Below this threshold we abort: something is genuinely getting worse.
    ABORT_IMPROVEMENT_THRESHOLD = -0.02

    def __init__(
        self,
        primitive_executor: Any,
        effectiveness_model: Any,
        learned_thresholds: Optional[Any] = None,
    ):
        super().__init__(
            agent_name='hamsters',
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
        Hamster-specific mid-sequence logic after each primitive completes.

        Abort if: a primitive caused genuine degradation (below noise threshold).
        Goal achieved if: post-metrics show the goal is satisfied.
        Continue if: primitive failed but didn't make things worse, or succeeded
                     but goal not yet fully satisfied.
        """
        latest = results_so_far[-1]

        # Things got meaningfully worse — abort.
        # Small negatives may be measurement noise; ABORT_IMPROVEMENT_THRESHOLD
        # filters those out.
        if latest.improvement < self.ABORT_IMPROVEMENT_THRESHOLD:
            self.logger.warning(
                f"🐹⛔ Primitive '{latest.primitive_name}' caused degradation "
                f"(improvement={latest.improvement:.3f}, "
                f"threshold={self.ABORT_IMPROVEMENT_THRESHOLD}). Aborting."
            )
            return 'abort'

        # Check if goal is already satisfied — skip remaining steps if so.
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

        # Primitive failed but didn't make things worse — continue.
        # The next primitive may still help.
        return 'continue'

    async def _goal_satisfied(
        self, goal: str, current_metrics: Dict[str, Any]
    ) -> bool:
        """
        Check if the goal has been satisfied using LEARNED thresholds.

        Single source of truth: delegates goal→metric mapping entirely to
        get_goal_thresholds() in LearnedThresholds. No duplicate mappings here.

        Goals that are satisfied by primitive completion (not by a metric
        threshold) are declared in COMPLETION_SATISFIED_GOALS below and
        return True immediately — there is no metric to check.

        If learned thresholds are unavailable, get_goal_thresholds() falls
        back to DEFAULT_THRESHOLDS. This method never falls through silently:
        an unknown goal emits a DECISION_LOG to The Stick and returns False.
        """
        # Goals satisfied by primitive completion, not by a metric threshold.
        # fstrim/logrotate either ran or they didn't — no post-metric to compare.
        COMPLETION_SATISFIED_GOALS = {
            'ssd_needs_trim',
            'slow_disk_io',
            'preventive_maintenance',
            'log_overflow',
        }
        if goal in COMPLETION_SATISFIED_GOALS:
            return True

        if not self.learned_thresholds:
            self.logger.warning(
                "🐹⚠️ Learned thresholds unavailable in _goal_satisfied — "
                "cannot evaluate goal satisfaction. Returning False."
            )
            return False

        try:
            threshold_info = await self.learned_thresholds.get_goal_thresholds(goal)
        except ValueError:
            # get_goal_thresholds() raises ValueError for goals not in GOAL_TO_METRIC.
            # This is a pipeline inconsistency: action_selection produced a goal
            # that the threshold system doesn't recognise. Notify The Stick.
            self.logger.error(
                f"🐹💥 Pipeline inconsistency: goal '{goal}' not in GOAL_TO_METRIC. "
                f"Action selection produced a goal the threshold system cannot evaluate. "
                f"STORAGE_GOALS and GOAL_TO_METRIC have drifted."
            )
            try:
                await self.send_to_agent(
                    to_agent='the_stick',
                    message_type=MessageType.DECISION_LOG,
                    payload={
                        'event': 'pipeline_inconsistency',
                        'severity': 'high',
                        'agent': 'hamsters',
                        'unknown_goal': goal,
                        'layer': 'HamsterExecutionPlanner._goal_satisfied',
                        'description': (
                            f"Goal '{goal}' has no entry in GOAL_TO_METRIC. "
                            f"action_selection.py produced a goal that the threshold "
                            f"system cannot evaluate. Check STORAGE_GOALS in "
                            f"execution_planner.py against GOAL_TO_METRIC in "
                            f"learned_thresholds.py."
                        ),
                        'known_goals': STORAGE_GOALS,
                    },
                    priority=Priority.HIGH,
                )
            except Exception as comm_err:
                self.logger.error(
                    f"🐹💥 Failed to notify The Stick of pipeline inconsistency: {comm_err}"
                )
            return False

        metric_name = threshold_info['metric_name']
        threshold = threshold_info['threshold']

        metric_key_map = {
            'disk_usage':    'disk_usage_percent',
            'inode_usage':   'inode_usage_percent',
            'fragmentation': 'fragmentation_level',
        }
        metric_key = metric_key_map.get(metric_name)
        current_value = current_metrics.get(metric_key) if metric_key else None

        if current_value is None:
            self.logger.warning(
                f"🐹⚠️ Cannot evaluate goal '{goal}': metric '{metric_name}' "
                f"(key '{metric_key}') not present in current_metrics. "
                f"Returning False."
            )
            return False

        satisfied = current_value < threshold
        if satisfied:
            self.logger.info(
                f"🐹✅ Goal '{goal}' satisfied: "
                f"{metric_name}={current_value:.1f}% < "
                f"{threshold_info['level']}={threshold:.1f}%"
            )
        return satisfied

    def _abort_reason(
        self,
        plan: ExecutionPlan,
        results: List[PrimitiveResult],
        step: int
    ) -> str:
        latest = results[-1]
        return (
            f"Primitive '{latest.primitive_name}' caused degradation "
            f"(improvement={latest.improvement:.3f}) at step {step + 1} "
            f"of {len(plan.primitives)} for goal '{plan.goal}'"
        )
