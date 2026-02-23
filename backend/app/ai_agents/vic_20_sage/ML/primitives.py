"""
VIC-20 Primitive Executor.

Primitives are the atomic operations VIC-20 can perform directly
(not delegated to specialists). These are coordination-layer actions only.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger('VIC20PrimitiveExecutor')


class VIC20PrimitiveExecutor:
    """
    Executes VIC-20's own coordination primitives.

    VIC-20 does NOT fix resources directly — that is the specialists' job.
    These primitives are coordination actions: routing, logging, monitoring.
    """

    PRIMITIVES = frozenset([
        'route_to_specialist',
        'log_to_stick',
        'monitor_situation',
        'request_status_update',
        'escalate_to_emergency',
    ])

    async def execute(self, primitive: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a VIC-20 coordination primitive.

        Args:
            primitive: Name of the primitive to execute
            parameters: Parameters for the primitive

        Returns:
            Result dict with success, primitive, and any output

        Raises:
            ValueError: If primitive is unknown — no fallback
        """
        if primitive not in self.PRIMITIVES:
            raise ValueError(
                f"VIC20PrimitiveExecutor: unknown primitive '{primitive}'. "
                f"Valid primitives: {sorted(self.PRIMITIVES)}"
            )

        handler = getattr(self, f'_execute_{primitive}', None)
        if handler is None:
            raise NotImplementedError(
                f"VIC20PrimitiveExecutor: primitive '{primitive}' is declared but not implemented."
            )

        logger.debug(f"🖥️⚙️ Executing primitive: {primitive}")
        return await handler(parameters)

    async def _execute_route_to_specialist(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'primitive': 'route_to_specialist',
            'specialist': params.get('specialist'),
            'action': params.get('action'),
        }

    async def _execute_log_to_stick(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'primitive': 'log_to_stick',
            'logged': True,
        }

    async def _execute_monitor_situation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'primitive': 'monitor_situation',
            'monitoring': True,
            'resource_type': params.get('resource_type'),
        }

    async def _execute_request_status_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'primitive': 'request_status_update',
            'target': params.get('target'),
        }

    async def _execute_escalate_to_emergency(self, params: Dict[str, Any]) -> Dict[str, Any]:
        logger.warning(
            f"🖥️🚨 EMERGENCY ESCALATION: {params.get('resource_type')} "
            f"at {params.get('current_value')}%"
        )
        return {
            'success': True,
            'primitive': 'escalate_to_emergency',
            'resource_type': params.get('resource_type'),
            'current_value': params.get('current_value'),
        }
