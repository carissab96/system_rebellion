"""
VIC-20 Execution Planner.

Translates a CoordinationAction into a concrete coordination_request payload
that can be sent to a specialist via the message bus.
"""

import logging
from typing import Any, Dict, Optional

from .action_selection import CoordinationAction
from .reasoning import CoordinationReasoning
from .perception import VIC20PerceptionContext

logger = logging.getLogger('VIC20ExecutionPlanner')


class VIC20ExecutionPlanner:
    """
    Builds the coordination_request payload for a specialist.

    Responsibilities:
    - Translate VIC-20's internal action into a specialist-facing request
    - Attach triage_alert_id for chain tracking
    - Attach full_metrics so the specialist can make informed decisions
    """

    def build_coordination_request(
        self,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning,
        action: CoordinationAction,
        triage_data: Dict[str, Any],
        triage_alert_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the coordination_request payload to send to the specialist.

        Args:
            context: VIC-20 perception context
            reasoning: VIC-20 reasoning result
            action: VIC-20 action selection result
            triage_data: Raw triage alert from Hawk (contains full_metrics)
            triage_alert_id: Chain tracking ID from Hawk

        Returns:
            Dict ready to be sent as COORDINATION_REQUEST payload
        """
        request = {
            'resource_type': context.resource_type,
            'current_value': context.current_value,
            'threshold': context.threshold,
            'severity': context.severity,
            'full_metrics': triage_data.get('full_metrics', {}),
            'recommendation': {
                'action': action.recommended_action,
                'confidence': action.confidence,
                'parameters': action.action_parameters,
            },
            'from_coordinator': 'vic_20_sage',
            'triage_confidence': context.hawk_confidence,
            'vic20_message': action.message_to_specialist,
            'urgency': reasoning.urgency_level,
            'triage_alert_id': triage_alert_id,
        }

        logger.debug(
            f"🖥️📋 Built coordination_request for {action.target_specialist}: "
            f"action={action.recommended_action}, urgency={reasoning.urgency_level}"
        )

        return request

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate that a coordination_request has all required fields.
        Raises ValueError if invalid — no silent defaults.
        """
        required = ['resource_type', 'current_value', 'threshold', 'severity', 'recommendation']
        missing = [k for k in required if k not in request]
        if missing:
            raise ValueError(
                f"VIC20ExecutionPlanner: coordination_request missing required fields: {missing}"
            )
        return True
