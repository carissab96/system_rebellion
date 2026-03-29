#!/usr/bin/env python3
"""
VIC-20 Sage's Execution Planner
Maps coordination goals to routing sequences.
"""

import logging
from typing import Dict, List, Any
from app.ai_agents.distributed.base_execution_planner import ExecutionPlanner, ExecutionPlan, PrimitiveResult

logger = logging.getLogger('VIC20ExecutionPlanner')

COLD_START_HYPOTHESES = {
    'route_critical': ['route_to_primary_specialist', 'escalate_to_human'],
    'route_high': ['route_to_primary_specialist'],
    'route_medium': ['route_to_fallback'],
    'route_low': ['monitor_resolution'],
}

class VIC20ExecutionPlanner(ExecutionPlanner):
    def __init__(self, primitive_executor, effectiveness_model):
        super().__init__(
            agent_name="vic_20_sage",
            primitive_executor=primitive_executor,
            effectiveness_model=effectiveness_model,
            cold_start_hypotheses=COLD_START_HYPOTHESES
        )

    async def _mid_sequence_decision(
        self, plan: ExecutionPlan, results_so_far: List[PrimitiveResult], current_step: int, context: Dict[str, Any]
    ) -> str:
        """Routing sequences usually fire completely, so just continue."""
        return 'continue'

    def _abort_reason(self, plan: ExecutionPlan, results: List[PrimitiveResult], step: int) -> str:
        return "Routing primitive failed."

    async def _goal_satisfied(self, goal: str, current_metrics: Dict[str, Any]) -> bool:
        """Coordination goals are satisfied once the routing decision is executed."""
        return True

    def build_coordination_request(
        self,
        context: Any,
        reasoning: Any,
        action: Any,
        triage_data: Dict[str, Any],
        triage_alert_id: str = None,
    ) -> Dict[str, Any]:
        """Retained from legacy planner for orchestrator compatibility."""
        request = {
            'resource_type': context.resource_type,
            'current_value': context.current_value,
            'threshold': context.threshold,
            'severity': context.severity,
            'full_metrics': triage_data.get('full_metrics', {}),
            'recommendation': {
                'action': getattr(action, 'recommended_action', 'unknown'),
                'confidence': action.confidence,
                'parameters': getattr(action, 'action_parameters', {}),
            },
            'from_coordinator': 'vic_20_sage',
            'triage_confidence': getattr(context, 'hawk_confidence', 0.5),
            'vic20_message': getattr(action, 'message_to_specialist', ''),
            'urgency': getattr(reasoning, 'urgency_level', 'normal'),
            'triage_alert_id': triage_alert_id,
        }
        return request
