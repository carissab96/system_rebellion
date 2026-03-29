#!/usr/bin/env python3
"""
Sir Hawkington's Execution Planner
Maps triage goals to primitive sequences.
"""

from typing import Dict, List, Any
from app.ai_agents.distributed.base_execution_planner import ExecutionPlanner, ExecutionPlan, PrimitiveResult

COLD_START_HYPOTHESES = {
    'triage_critical': ['escalate'],
    'triage_high': ['escalate'],
    'triage_medium': ['monitor'],
    'triage_low': ['dismiss'],
}

class HawkExecutionPlanner(ExecutionPlanner):
    def __init__(self, primitive_executor, effectiveness_model):
        super().__init__(
            agent_name="sir_hawkington",
            primitive_executor=primitive_executor,
            effectiveness_model=effectiveness_model,
            cold_start_hypotheses=COLD_START_HYPOTHESES
        )

    async def _mid_sequence_decision(
        self, plan: ExecutionPlan, results_so_far: List[PrimitiveResult], current_step: int, context: Dict[str, Any]
    ) -> str:
        """Triage sequences are usually 1 step, so just continue."""
        return 'continue'

    def _abort_reason(self, plan: ExecutionPlan, results: List[PrimitiveResult], step: int) -> str:
        return "Triage primitive failed."

    async def _goal_satisfied(self, goal: str, current_metrics: Dict[str, Any]) -> bool:
        """Triage goals are satisfied once the decision is executed."""
        return True
