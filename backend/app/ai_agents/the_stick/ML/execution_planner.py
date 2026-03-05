#!/usr/bin/env python3
"""
The Stick's Execution Planner
Maps compliance goals to logging sequences.
"""

import logging
from typing import Dict, List, Any
from app.ai_agents.distributed.base_execution_planner import ExecutionPlanner, ExecutionPlan, PrimitiveResult

logger = logging.getLogger('StickExecutionPlanner')

COLD_START_HYPOTHESES = {
    'manage_bob': ['execute_bob_evasion'],
    'manage_panic': ['execute_panic_protocol'],
    'manage_emergency': ['log_emergency_event'],
    'manage_warning': ['log_anxious_reminder'],
    'manage_routine': ['log_standard_decision'],
}

class StickExecutionPlanner(ExecutionPlanner):
    def __init__(self, primitive_executor, effectiveness_model):
        super().__init__(
            agent_name="the_stick",
            primitive_executor=primitive_executor,
            effectiveness_model=effectiveness_model,
            cold_start_hypotheses=COLD_START_HYPOTHESES
        )

    async def _mid_sequence_decision(
        self, plan: ExecutionPlan, results_so_far: List[PrimitiveResult], current_step: int, context: Dict[str, Any]
    ) -> str:
        """Compliance sequences usually fire completely, so just continue."""
        return 'continue'

    def _abort_reason(self, plan: ExecutionPlan, results: List[PrimitiveResult], step: int) -> str:
        return "Compliance primitive failed."

    async def _goal_satisfied(self, goal: str, current_metrics: Dict[str, Any]) -> bool:
        """Compliance goals are satisfied once the logging decision is executed."""
        return True
