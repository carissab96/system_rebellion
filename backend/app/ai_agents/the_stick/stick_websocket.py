"""
The Stick — WebSocket Layer
==============================

Frontend emission for The Stick.

- get_agent_status() — EXACT 16-key dict + distributed
- emit_decision() — wraps emit_agent_decision(agent_name="the_stick", ...)
- emit_insight() — wraps emit_agent_insight(from_agent="the_stick", ...)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("TheStick.WebSocket")


class StickWebSocket:
    """
    WebSocket emission for The Stick.

    Wraps emit_agent_decision and emit_agent_insight.
    get_agent_status() returns the EXACT dict the frontend expects.
    """

    def __init__(self, personality):
        """
        Args:
            personality: StickPersonalityState instance
        """
        self.personality = personality

    def get_agent_status(self, distributed_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get The Stick's complete status including distributed state.

        Returns EXACT dict from distributed_stick.py:1254-1278.
        16 keys + 'distributed'.
        """
        status = self.personality.get_status()
        status["distributed"] = distributed_state or {}
        return status

    async def emit_decision(self, decision_data: Dict[str, Any]) -> None:
        """
        Emit decision to frontend.

        Wraps emit_agent_decision with agent_name="the_stick".
        """
        try:
            from app.services.agent_decision_emitter import emit_agent_decision
            await emit_agent_decision(
                agent_name="the_stick",
                **decision_data
            )
        except Exception as e:
            logger.error(f"📏💥 Error emitting decision: {e}")

    async def emit_insight(
        self,
        action: str,
        reasoning: str,
        context: Optional[Dict[str, Any]] = None,
        to_agent: str = "system"
    ) -> None:
        """
        Emit insight to frontend.

        Wraps emit_agent_insight with from_agent="the_stick".
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="the_stick",
                to_agent=to_agent,
                action=action,
                reasoning=reasoning,
                context=context or {}
            )
        except Exception as e:
            logger.error(f"📏💥 Error emitting insight: {e}")
