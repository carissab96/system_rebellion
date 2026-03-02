#!/usr/bin/env python3
"""
Terry's Execution Planner

The intelligent layer between action selection and primitive execution.
Takes a CPU/memory goal, queries learned sequences, and composes an
ExecutionPlan from available primitives.

Cold start: domain-informed hypotheses (first guesses, not answers).
Over time: discovered sequences that have proven effective.

🐌💨 "I don't just DO things. I figure out the BEST way to do things.
       *chugs energy drink* *spins shell with PURPOSE*"
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

logger = logging.getLogger('TerryExecutionPlanner')


# =============================================================================
# Goal vocabulary — shared with action_selection.py
# These are PROBLEMS, not solutions. The planner figures out how to solve them.
# =============================================================================

TERRY_GOALS = [
    # Memory issues
    'memory_high',              # Warning — trending toward critical
    'memory_critical',          # Critical — immediate action needed
    'memory_thrashing',         # Severe — system is thrashing swap
    'memory_leak_suspected',    # Process growing unbounded

    # Cache issues
    'cache_bloat',              # Page/slab cache consuming too much RAM
    'cache_stale',              # Cached data no longer useful

    # CPU issues
    'cpu_high',                 # Warning — CPU elevated
    'cpu_critical',             # Critical — CPU maxed out
    'cpu_runaway_process',      # Single process consuming all CPU
    'cpu_load_spike',           # Load average spike (may be transient)

    # Swap issues
    'swap_high',                # Swap usage elevated
    'swap_critical',            # Swap nearly exhausted

    # Compound
    'memory_and_cpu_high',      # Both elevated simultaneously
    'oom_imminent',             # OOM killer about to fire

    # Maintenance
    'preventive_optimization',  # Nothing broken, routine tuning

    # Fallback
    'unknown_resource_issue',   # Can't classify — needs investigation
]


# =============================================================================
# Cold start hypotheses — domain-informed starting points.
# These are NOT answers. They're first guesses that ML improves upon.
# The system confirms or discovers better sequences through experience.
#
# Terry's domain knowledge:
# - Cache drops are fast and low-risk — try them before killing processes
# - Sync before dropping cache to avoid data loss
# - Renice before kill — less disruptive
# - Swappiness tuning is a complement, not a primary fix
# =============================================================================

COLD_START_HYPOTHESES: Dict[str, List[str]] = {
    # Memory: sync first, then drop page cache (safest reclaim)
    'memory_high':              ['sync_filesystem', 'drop_page_cache'],

    # Memory critical: drop all caches, then compact if still bad
    'memory_critical':          ['sync_filesystem', 'drop_all_caches', 'compact_memory'],

    # Thrashing: reduce swappiness to keep more in RAM, then reclaim
    'memory_thrashing':         ['adjust_swappiness', 'sync_filesystem', 'drop_all_caches'],

    # Leak: kill the leaking process (renice first to reduce impact while identifying)
    'memory_leak_suspected':    ['renice_cpu_hog', 'kill_memory_hog'],

    # Cache bloat: targeted cache drop — page cache is the primary culprit
    'cache_bloat':              ['sync_filesystem', 'drop_page_cache'],

    # Stale cache: drop slab (dentries/inodes) — more targeted than page cache
    'cache_stale':              ['sync_filesystem', 'drop_slab_cache'],

    # CPU high: renice the hog first (non-destructive), throttle if still bad
    'cpu_high':                 ['renice_cpu_hog'],

    # CPU critical: throttle immediately, then renice
    'cpu_critical':             ['throttle_cpu_process', 'renice_cpu_hog'],

    # Runaway process: kill it — it's not responding to nice signals
    'cpu_runaway_process':      ['kill_memory_hog'],  # same logic, top consumer

    # Load spike: may be transient — renice first, observe
    'cpu_load_spike':           ['renice_cpu_hog'],

    # Swap high: lower swappiness to stop new swapping, reclaim cache for RAM
    'swap_high':                ['adjust_swappiness', 'sync_filesystem', 'drop_page_cache'],

    # Swap critical: emergency — drop all caches to free RAM so swap can drain
    'swap_critical':            ['adjust_swappiness', 'sync_filesystem', 'drop_all_caches'],

    # Both high: memory first (more critical), then CPU
    'memory_and_cpu_high':      ['sync_filesystem', 'drop_all_caches', 'renice_cpu_hog'],

    # OOM imminent: kill the biggest consumer NOW, then reclaim
    'oom_imminent':             ['kill_memory_hog', 'sync_filesystem', 'drop_all_caches'],

    # Preventive: light cache drop + swappiness tune
    'preventive_optimization':  ['sync_filesystem', 'drop_page_cache'],

    # Unknown: safest possible action — cache drop only
    'unknown_resource_issue':   ['sync_filesystem', 'drop_page_cache'],
}


# Goals satisfied by primitive completion, not by a metric threshold.
# These actions either ran or they didn't — no post-metric to compare.
COMPLETION_SATISFIED_GOALS = frozenset([
    'preventive_optimization',
    'cache_stale',
])


# =============================================================================
# Goal → metric key mapping — Terry-specific, authoritative.
# Maps TERRY_GOALS entries to the metric key used in _collect_metrics() output.
# This is the single source of truth for goal satisfaction checks.
# GOAL_METRIC_MAP in learned_thresholds.py uses the same vocabulary but is
# retained for agent-agnostic callers only — _goal_satisfied() uses THIS dict.
# =============================================================================

GOAL_TO_METRIC_KEY = {
    'memory_high':              'memory_usage',
    'memory_critical':          'memory_usage',
    'memory_thrashing':         'memory_usage',
    'memory_leak_suspected':    'memory_usage',
    'cache_bloat':              'memory_usage',
    'swap_high':                'swap_usage',
    'swap_critical':            'swap_usage',
    'cpu_high':                 'cpu_usage',
    'cpu_critical':             'cpu_usage',
    'cpu_runaway_process':      'cpu_usage',
    'cpu_load_spike':           'load_average',
    # NOTE: memory_and_cpu_high only checks memory_usage here.
    # CPU satisfaction is not independently verified. If CPU remains high
    # after memory drops below threshold, the goal will still be declared
    # satisfied. A compound goal check (both metrics) requires a separate
    # _goal_satisfied() branch or a dedicated compound metric.
    'memory_and_cpu_high':      'memory_usage',
    'oom_imminent':             'memory_usage',
    'unknown_resource_issue':   'memory_usage',
}


class TerryExecutionPlanner(ExecutionPlanner):
    """
    Terry's execution planner for CPU and memory goals.

    Composes primitive sequences from learned effectiveness data.
    Falls back to cold start hypotheses when no learned sequences exist.
    Uses learned thresholds to determine when a goal is satisfied.
    """

    # Negative improvement tolerance — small negative values may be measurement noise.
    # Below this threshold we abort: something is genuinely getting worse.
    ABORT_IMPROVEMENT_THRESHOLD = -0.03

    def __init__(
        self,
        primitive_executor: Any,
        effectiveness_model: Any,
        learned_thresholds: Optional[Any] = None,
    ):
        super().__init__(
            agent_name='meth_snail',
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
        Terry-specific mid-sequence logic after each primitive completes.

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
                f"🐌⛔ Primitive '{latest.primitive_name}' caused degradation "
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

        Uses GOAL_TO_METRIC_KEY (module-level) to map goal → metric, then
        calls self.learned_thresholds.get_threshold(metric, 'warning') directly.
        This bypasses get_goal_thresholds() and eliminates the GOAL_METRIC_MAP
        vocabulary mismatch entirely.

        Goals in COMPLETION_SATISFIED_GOALS return True immediately —
        no metric to check, just confirm the primitive ran.

        Unknown goals (not in GOAL_TO_METRIC_KEY) are a pipeline inconsistency:
        logged at ERROR and emitted to The Stick.
        """
        if goal in COMPLETION_SATISFIED_GOALS:
            return True

        if not self.learned_thresholds:
            self.logger.warning(
                "🐌⚠️ Learned thresholds unavailable in _goal_satisfied — "
                "cannot evaluate goal satisfaction. Returning False."
            )
            return False

        metric_key = GOAL_TO_METRIC_KEY.get(goal)
        if metric_key is None:
            # Pipeline inconsistency: TERRY_GOALS and GOAL_TO_METRIC_KEY have drifted.
            self.logger.error(
                f"🐌💥 Pipeline inconsistency: goal '{goal}' not in GOAL_TO_METRIC_KEY. "
                f"TERRY_GOALS and GOAL_TO_METRIC_KEY have drifted."
            )
            try:
                from app.services.agent_insight_emitter import emit_agent_insight
                await emit_agent_insight(
                    from_agent='meth_snail',
                    to_agent='the_stick',
                    action='pipeline_inconsistency',
                    reasoning=(
                        f"Goal '{goal}' has no entry in GOAL_TO_METRIC_KEY. "
                        f"TERRY_GOALS and GOAL_TO_METRIC_KEY have drifted."
                    ),
                    context={
                        'event': 'pipeline_inconsistency',
                        'severity': 'high',
                        'agent': 'meth_snail',
                        'unknown_goal': goal,
                        'layer': 'TerryExecutionPlanner._goal_satisfied',
                        'known_goals': TERRY_GOALS,
                    }
                )
            except Exception as comm_err:
                self.logger.error(
                    f"🐌💥 Failed to notify The Stick of pipeline inconsistency: {comm_err}"
                )
            return False

        # Get the learned warning threshold for this metric directly.
        # Falls back to DEFAULT_THRESHOLDS if no learning history exists.
        try:
            warning_threshold = await self.learned_thresholds.get_threshold(
                metric_key, 'warning'
            )
        except Exception as e:
            self.logger.warning(
                f"🐌⚠️ get_threshold raised for '{metric_key}': {e} — returning False"
            )
            return False

        current_value = current_metrics.get(metric_key)
        if current_value is None:
            self.logger.warning(
                f"🐌⚠️ Cannot evaluate goal '{goal}': metric '{metric_key}' "
                f"not present in current_metrics. Returning False."
            )
            return False

        satisfied = current_value < warning_threshold
        if satisfied:
            self.logger.info(
                f"🐌✅ Goal '{goal}' satisfied: "
                f"{metric_key}={current_value:.1f}% < "
                f"warning={warning_threshold:.1f}%"
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
