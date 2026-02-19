#!/usr/bin/env python3
"""
Base Execution Planner

The intelligent layer between action selection and primitive execution.
Takes a goal from action selection, queries learned sequences, and composes
an ExecutionPlan from available primitives.

On cold start: uses domain-informed hypotheses (first guesses, not answers).
As the system learns: uses discovered sequences that have proven effective.
Also handles mid-sequence decisions: abort, skip, continue.

Each agent domain subclasses this and provides:
- Cold start hypotheses (domain knowledge starting points)
- _mid_sequence_decision() (domain-specific abort/continue logic)
- _goal_satisfied() (domain-specific success check using learned thresholds)
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional, TYPE_CHECKING

from .base_primitive_executor import PrimitiveExecutor, PrimitiveResult

if TYPE_CHECKING:
    from app.models.learned_thresholds import LearnedSequence


class PlanSource(str, Enum):
    COLD_START = "cold_start_hypothesis"
    LEARNED = "learned_sequence"
    EMERGENCY = "emergency_override"


class InterventionType(str, Enum):
    REACTIVE = "reactive"        # Problem is already here
    PREEMPTIVE = "preemptive"    # Predicted problem, acting early
    MAINTENANCE = "maintenance"  # Routine, nothing wrong


@dataclass
class ExecutionPlan:
    """A plan composed by the ExecutionPlanner."""
    goal: str                           # From STORAGE_GOALS vocabulary
    primitives: List[str]               # Ordered primitive names
    source: PlanSource                  # Where this plan came from
    confidence: float                   # 0.0-1.0
    intervention_type: InterventionType
    trigger_severity: float             # 0.0-1.0, how bad when plan was composed
    trigger_trend: str                  # 'rising', 'stable', 'falling'
    sequence_id: Optional[int] = None   # FK to LearnedSequence if source is LEARNED
    reasoning: Optional[str] = None     # Why this plan was chosen

    def to_log_entry(self) -> str:
        if self.source == PlanSource.COLD_START:
            return (
                f"🐹🧪 Cold start hypothesis for '{self.goal}': "
                f"{self.primitives} — will learn from outcome"
            )
        elif self.source == PlanSource.LEARNED:
            return (
                f"🐹🧠 Learned sequence for '{self.goal}': "
                f"{self.primitives} "
                f"(confidence={self.confidence:.2f}, sequence_id={self.sequence_id})"
            )
        elif self.source == PlanSource.EMERGENCY:
            return (
                f"🐹🚨 EMERGENCY override for '{self.goal}': "
                f"{self.primitives} — learned pipeline unavailable, "
                f"ACTING AND SCREAMING"
            )
        return f"ExecutionPlan(goal={self.goal}, primitives={self.primitives})"


@dataclass
class ExecutionResult:
    """Full result from executing a plan — all primitives, in order."""
    plan: ExecutionPlan
    primitive_results: List[PrimitiveResult]
    overall_success: bool
    overall_improvement: float          # Aggregate improvement across sequence
    total_duration_seconds: float
    aborted_at_step: Optional[int] = None   # If sequence was halted mid-execution
    abort_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def was_aborted(self) -> bool:
        return self.aborted_at_step is not None

    @property
    def steps_completed(self) -> int:
        return len(self.primitive_results)

    @property
    def steps_planned(self) -> int:
        return len(self.plan.primitives)


class ExecutionPlanner(ABC):
    """
    Composes execution plans from primitives based on goals.

    This is where the intelligence lives. The planner takes a goal from
    action selection, queries the effectiveness model for learned sequences,
    and composes an ExecutionPlan. On cold start it uses domain-informed
    hypotheses. As the system learns it uses discovered sequences.

    The planner also handles mid-sequence decisions:
    - Should we abort if step 2 of 4 failed?
    - Should we skip step 3 if step 2 already fixed the problem?

    Subclasses provide domain-specific cold start hypotheses and
    abort/continuation logic.
    """

    MIN_LEARNED_CONFIDENCE = 0.3
    MIN_SAMPLE_SIZE = 3
    EMERGENCY_SEVERITY_THRESHOLD = 0.95

    def __init__(
        self,
        agent_name: str,
        primitive_executor: PrimitiveExecutor,
        effectiveness_model: Any,           # ActionEffectivenessModel
        cold_start_hypotheses: Dict[str, List[str]],
    ):
        self.agent_name = agent_name
        self.executor = primitive_executor
        self.effectiveness = effectiveness_model
        self.cold_start = cold_start_hypotheses
        self.logger = logging.getLogger(f"rebellion.{agent_name}.execution_planner")

    async def compose_plan(
        self,
        goal: str,
        severity: float,
        trend: str,
        context: Dict[str, Any],
    ) -> ExecutionPlan:
        """
        Compose an execution plan for a given goal.

        Queries learned sequences first. Falls back to cold start hypothesis
        if no learned sequence meets confidence threshold.

        Emergency override: if severity >= EMERGENCY_SEVERITY_THRESHOLD AND
        no learned sequence exists, use cold start BUT flag as EMERGENCY so
        The Stick knows this was survival, not intelligence.
        """
        # Try learned sequence first
        learned = await self._get_best_learned_sequence(goal, severity, trend)

        if learned is not None:
            self.logger.info(
                f"Using learned sequence for '{goal}': "
                f"{learned.primitives} "
                f"(confidence={learned.confidence:.2f}, samples={learned.sample_size})"
            )
            return ExecutionPlan(
                goal=goal,
                primitives=list(learned.primitives),
                source=PlanSource.LEARNED,
                confidence=learned.confidence,
                intervention_type=self._classify_intervention(severity, trend),
                trigger_severity=severity,
                trigger_trend=trend,
                sequence_id=learned.id,
                reasoning=(
                    f"Learned sequence with {learned.sample_size} samples, "
                    f"{learned.success_rate:.0%} success rate, "
                    f"{learned.avg_improvement:.3f} avg improvement"
                )
            )

        # Cold start hypothesis
        hypothesis = self.cold_start.get(goal)
        if hypothesis is None:
            self.logger.error(
                f"No cold start hypothesis for goal '{goal}' — "
                f"available goals: {list(self.cold_start.keys())}"
            )
            raise ValueError(
                f"No cold start hypothesis for unknown goal: '{goal}'. "
                f"Available goals: {list(self.cold_start.keys())}"
            )

        is_emergency = severity >= self.EMERGENCY_SEVERITY_THRESHOLD
        source = PlanSource.EMERGENCY if is_emergency else PlanSource.COLD_START

        if is_emergency:
            self.logger.warning(
                f"🚨 EMERGENCY: No learned sequence for '{goal}' at "
                f"severity {severity:.2f}. Using cold start hypothesis "
                f"AND flagging as emergency. This is survival, not intelligence."
            )

        return ExecutionPlan(
            goal=goal,
            primitives=list(hypothesis),
            source=source,
            confidence=0.1 if is_emergency else 0.0,
            intervention_type=self._classify_intervention(severity, trend),
            trigger_severity=severity,
            trigger_trend=trend,
            sequence_id=None,
            reasoning=(
                f"Emergency cold start — severity {severity:.2f}, no learned sequences"
                if is_emergency
                else f"Cold start hypothesis — no learned sequences for '{goal}'"
            )
        )

    async def execute_plan(
        self, plan: ExecutionPlan, context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute a plan step by step, collecting metrics between steps.

        Handles mid-sequence decisions after each step:
        - 'abort': stop, something went wrong
        - 'goal_achieved': problem solved, skip remaining steps
        - 'continue': proceed to next step
        """
        results: List[PrimitiveResult] = []
        start_time = time.monotonic()

        self.logger.info(plan.to_log_entry())

        for i, primitive_name in enumerate(plan.primitives):
            self.logger.info(
                f"  Step {i + 1}/{len(plan.primitives)}: {primitive_name}"
            )

            result = await self.executor.execute(primitive_name, context)
            results.append(result)

            if result.success:
                self.logger.info(
                    f"  ✓ {primitive_name}: "
                    f"improvement={result.improvement:.3f}, "
                    f"duration={result.duration_seconds:.1f}s"
                )
            else:
                self.logger.warning(
                    f"  ✗ {primitive_name} failed: {result.error}"
                )

            decision = await self._mid_sequence_decision(plan, results, i, context)

            if decision == 'abort':
                abort_reason = self._abort_reason(plan, results, i)
                self.logger.warning(
                    f"Aborting sequence at step {i + 1}/{len(plan.primitives)}: "
                    f"{abort_reason}"
                )
                total_duration = time.monotonic() - start_time
                return ExecutionResult(
                    plan=plan,
                    primitive_results=results,
                    overall_success=False,
                    overall_improvement=self._aggregate_improvement(results),
                    total_duration_seconds=total_duration,
                    aborted_at_step=i,
                    abort_reason=abort_reason
                )

            elif decision == 'goal_achieved':
                remaining = len(plan.primitives) - i - 1
                self.logger.info(
                    f"  Goal '{plan.goal}' achieved after step {i + 1} — "
                    f"skipping remaining {remaining} step(s)"
                )
                break

            # else: 'continue'

        total_duration = time.monotonic() - start_time
        overall_improvement = self._aggregate_improvement(results)
        all_succeeded = all(r.success for r in results)

        return ExecutionResult(
            plan=plan,
            primitive_results=results,
            overall_success=all_succeeded and overall_improvement > 0,
            overall_improvement=overall_improvement,
            total_duration_seconds=total_duration,
        )

    async def _get_best_learned_sequence(
        self, goal: str, severity: float, trend: str
    ) -> Optional[Any]:
        """
        Query effectiveness model for the best learned sequence.

        Filters by: goal match, not deprecated, minimum confidence and sample size.
        Ranks by effectiveness_score * confidence, with severity proximity bonus.
        """
        try:
            sequences = await self.effectiveness.get_effective_sequences(
                goal=goal,
                min_confidence=self.MIN_LEARNED_CONFIDENCE,
                min_samples=self.MIN_SAMPLE_SIZE,
            )
        except Exception as e:
            self.logger.error(
                f"Learned sequence query failed for goal '{goal}': {e} — "
                f"falling back to cold start hypothesis. SCREAMING.",
                exc_info=True
            )
            return None

        if not sequences:
            return None

        def rank(seq: Any) -> float:
            base = seq.effectiveness_score * seq.confidence
            if seq.trigger_severity is not None:
                severity_distance = abs(seq.trigger_severity - severity)
                proximity_bonus = max(0.0, 0.1 * (1.0 - severity_distance))
                base += proximity_bonus
            return base

        sequences.sort(key=rank, reverse=True)
        return sequences[0]

    @abstractmethod
    async def _mid_sequence_decision(
        self,
        plan: ExecutionPlan,
        results_so_far: List[PrimitiveResult],
        current_step: int,
        context: Dict[str, Any],
    ) -> str:
        """
        Decide what to do after each step in a sequence.

        Returns:
            'continue'       — proceed to next step
            'abort'          — stop execution, something went wrong
            'goal_achieved'  — problem is solved, skip remaining steps

        Domain-specific. Hamsters check if disk usage dropped below threshold.
        Terry checks if CPU/memory stabilized. QSP checks if threat is mitigated.
        """
        pass

    @abstractmethod
    def _abort_reason(
        self,
        plan: ExecutionPlan,
        results: List[PrimitiveResult],
        step: int
    ) -> str:
        """Generate human-readable abort reason for logging and audit."""
        pass

    @abstractmethod
    async def _goal_satisfied(
        self, goal: str, current_metrics: Dict[str, Any]
    ) -> bool:
        """
        Check if the goal has been satisfied using LEARNED thresholds.
        Not hardcoded. Queries the learned threshold system.
        """
        pass

    def _classify_intervention(
        self, severity: float, trend: str
    ) -> InterventionType:
        """Classify intervention type from severity and trend."""
        if severity < 0.3 and trend in ('stable', 'falling'):
            return InterventionType.MAINTENANCE
        elif severity < 0.5 and trend == 'rising':
            return InterventionType.PREEMPTIVE
        else:
            return InterventionType.REACTIVE

    def _aggregate_improvement(
        self, results: List[PrimitiveResult]
    ) -> float:
        """
        Aggregate improvement across multiple primitives.

        Takes total delta from first pre-metrics to last post-metrics.
        This is more accurate than summing per-step improvements because
        later steps operate on the already-improved state from earlier steps.

        Falls back to sum of per-step improvements if metric collection failed.
        """
        if not results:
            return 0.0

        first_pre = results[0].pre_metrics
        last_post = results[-1].post_metrics

        if first_pre.get('collection_failed') or last_post.get('collection_failed'):
            return sum(r.improvement for r in results)

        return self.executor._calculate_improvement(first_pre, last_post)
