#!/usr/bin/env python3
"""
The Stick's Primitive Executor
Registers atomic logging and compliance actions.
"""

from typing import Dict, Any
from app.ai_agents.distributed.base_primitive_executor import PrimitiveExecutor, PrimitiveDefinition, PrimitiveResult

class StickPrimitiveExecutor(PrimitiveExecutor):
    def __init__(self):
        super().__init__("the_stick")
        
    def _register_primitives(self):
        self.register(PrimitiveDefinition(
            name="log_standard_decision",
            command=None,
            requires_sudo=False,
            domain="compliance",
            description="Log a standard system decision."
        ))
        self.register(PrimitiveDefinition(
            name="log_emergency_event",
            command=None,
            requires_sudo=False,
            domain="compliance",
            description="Log an urgent emergency event."
        ))
        self.register(PrimitiveDefinition(
            name="execute_panic_protocol",
            command=None,
            requires_sudo=False,
            domain="compliance",
            description="Execute full panic protocol (requires paper bags).",
            risk_level=2
        ))
        self.register(PrimitiveDefinition(
            name="execute_bob_evasion",
            command=None,
            requires_sudo=False,
            domain="compliance",
            description="Execute Bob evasion and archive evidence.",
            risk_level=3
        ))
        self.register(PrimitiveDefinition(
            name="log_anxious_reminder",
            command=None,
            requires_sudo=False,
            domain="compliance",
            description="Log an anxious reminder for recurring minor issues."
        ))
        
    async def _execute_python_primitive(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        """Execute a Python primitive for compliance logging."""
        self.logger.info(f"📊 Executing formalized compliance action: {name}")
        return PrimitiveResult(
            primitive_name=name,
            success=True,
            pre_metrics=context.get('metrics_snapshot', {}),
            post_metrics=context.get('metrics_snapshot', {}),
            improvement=0.1,  # Base improvement for a successful logging operation
            duration_seconds=0.1
        )
        
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics (mocked/passthrough for compliance agent)."""
        return {"compliance_state": "logged"}
        
    def _calculate_improvement(self, pre: Dict[str, Any], post: Dict[str, Any]) -> float:
        """Improvement calculation for compliance."""
        return 0.1
