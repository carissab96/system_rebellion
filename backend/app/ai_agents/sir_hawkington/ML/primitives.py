#!/usr/bin/env python3
"""
Sir Hawkington's Primitive Executor
Registers atomic triage actions. Since Hawk is a coordination agent, 
his primitives don't run shell commands; instead, they formalize the 
selected triage action.
"""

from typing import Dict, Any
from app.ai_agents.distributed.base_primitive_executor import PrimitiveExecutor, PrimitiveDefinition, PrimitiveResult

class HawkPrimitiveExecutor(PrimitiveExecutor):
    def __init__(self):
        super().__init__("sir_hawkington")
        
    def _register_primitives(self):
        self.register(PrimitiveDefinition(
            name="dismiss",
            command=None,
            requires_sudo=False,
            domain="triage",
            description="Dismiss alert as false positive or low severity."
        ))
        self.register(PrimitiveDefinition(
            name="monitor",
            command=None,
            requires_sudo=False,
            domain="triage",
            description="Monitor alert for further developments."
        ))
        self.register(PrimitiveDefinition(
            name="escalate",
            command=None,
            requires_sudo=False,
            domain="triage",
            description="Escalate alert to VIC-20 for routing to a specialist."
        ))
        
    async def _execute_python_primitive(self, name: str, context: Dict[str, Any]) -> PrimitiveResult:
        """Execute a Python primitive for triage."""
        self.logger.info(f"🧐 Executing formalized triage action: {name}")
        return PrimitiveResult(
            primitive_name=name,
            success=True,
            pre_metrics=context.get('metrics_snapshot', {}),
            post_metrics=context.get('metrics_snapshot', {}),
            improvement=0.1,  # Base improvement for a successful triage decision
            duration_seconds=0.1
        )
        
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics (mocked/passthrough for triage agent)."""
        return {"triage_state": "assessed"}
        
    def _calculate_improvement(self, pre: Dict[str, Any], post: Dict[str, Any]) -> float:
        """Improvement calculation for triage."""
        return 0.1
