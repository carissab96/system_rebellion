"""
VIC-20 Sage — WebSocket Emission
==================================

Frontend emission layer. Builds status payloads and emits
ML decision chains to the WebSocket narrative feed.

Extracted from distributed_vic20.py:292-366 (emit_agent_decision
and emit_agent_insight calls) and 1472-1505 (get_agent_status).

All payload keys preserved EXACTLY from the monolith.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("VIC20.WebSocket")


class VIC20WebSocket:
    """
    VIC-20 Sage WebSocket emission layer.

    Responsible for:
    - get_agent_status() — EXACT keys for frontend
    - emit_decision() — broadcast ML pipeline to narrative feed
    - emit_insight() — broadcast coordination insight
    """

    def __init__(self, personality):
        """
        Args:
            personality: VIC20PersonalityState instance
        """
        self.personality = personality
        logger.info("🖥️📡 VIC-20 WebSocket emission initialized")

    def get_agent_status(self, distributed_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get VIC-20's complete status including distributed state.

        EXACT keys from distributed_vic20.py:1483-1494.
        Frontend reads these — DO NOT rename any key.

        Returns:
            Status dictionary matching the original monolith format
        """
        status = self.personality.get_status()
        status["distributed"] = distributed_state or {}
        return status

    async def emit_decision(
        self,
        context,
        reasoning,
        action,
        learning_record,
    ) -> None:
        """
        Broadcast ML decision chain to WebSocket narrative feed.

        EXACT payload keys from distributed_vic20.py:293-329.

        Args:
            context: VIC20PerceptionContext
            reasoning: CoordinationReasoning
            action: CoordinationAction
            learning_record: VIC20LearningRecord
        """
        try:
            from app.services.agent_decision_emitter import emit_agent_decision

            await emit_agent_decision(
                agent_name="vic_20_sage",
                decision_id=learning_record.learning_record_id or "pending",
                perception={
                    "resource_type": context.resource_type,
                    "current_value": context.current_value,
                    "threshold": context.threshold,
                    "severity": context.severity,
                    "hawk_confidence": context.hawk_confidence,
                    "available_specialists": [s.agent_name for s in context.available_specialists],
                    "system_load": context.system_load,
                    "routing_confidence": context.routing_confidence,
                },
                reasoning={
                    "target_specialist": reasoning.target_specialist,
                    "routing_confidence": reasoning.routing_confidence,
                    "urgency_level": reasoning.urgency_level,
                    "specialist_success_rate": reasoning.specialist_success_rate,
                    "specialist_load": reasoning.specialist_load,
                    "primary_reason": reasoning.primary_reason,
                },
                action_selection={
                    "chosen_action": action.action_type,
                    "target_specialist": action.target_specialist,
                    "recommended_action": action.recommended_action,
                    "confidence": action.confidence,
                    "priority": action.priority,
                    "coordination_strategy": action.coordination_strategy,
                    "fallback_specialists": action.fallback_specialists,
                },
                learning={
                    "situation_fingerprint": learning_record.situation_fingerprint,
                    "stored": learning_record.storage_success,
                    "learning_record_id": learning_record.learning_record_id,
                    "success": learning_record.success,
                }
            )

            logger.debug("🖥️📡 VIC-20 decision emitted to WebSocket")

        except Exception as e:
            logger.error(f"🖥️💥 WebSocket emit failed: {e}", exc_info=True)

    async def emit_insight(
        self,
        to_agent: str,
        action_name: str,
        reasoning_text: str,
        context_data: Dict[str, Any],
    ) -> None:
        """
        Broadcast coordination insight to narrative feed.

        EXACT payload keys from distributed_vic20.py:351-366.

        Args:
            to_agent: Target agent name
            action_name: Action being taken
            reasoning_text: Primary reasoning text
            context_data: Context dict with exact keys
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight

            await emit_agent_insight(
                from_agent="vic_20_sage",
                to_agent=to_agent,
                action=action_name,
                reasoning=reasoning_text,
                context=context_data
            )

            logger.debug(f"🖥️📡 VIC-20 insight emitted → {to_agent}")

        except Exception as e:
            logger.error(f"🖥️💥 Insight emit failed: {e}", exc_info=True)
