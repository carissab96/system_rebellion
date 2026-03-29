"""
The Hamsters — WebSocket Emission Layer
========================================

Owns ALL frontend-facing emission:
- get_agent_status() for heartbeat payloads
- emit_decision() for ML pipeline events
- emit_insight() for narrative feed events

Reads from personality state. Reads from ML pipeline results.
Does not make decisions. Does not send inter-agent messages.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("Hamsters.WebSocket")


class HamstersWebSocket:
    """
    The Hamsters' frontend emission layer.

    Reads personality state and pipeline results.
    Formats and emits to frontend via WebSocket.
    """

    def __init__(self, personality):
        """
        Args:
            personality: HamstersPersonalityState instance
        """
        self.personality = personality
        self.agent_name = "hamsters"

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the Hamsters' complete status for heartbeat emission.

        Called by DistributedAgentManager.get_system_status()
        and the heartbeat WebSocket payload.
        """
        p = self.personality

        status = {
            "agent_name": self.agent_name,
            "agent_type": "storage_engineers",
            "is_active": p.is_active,
        }

        # Merge personality status
        status.update(p.get_status())

        # Additional top-level fields for backwards compat
        status["bob_wild_ideas"] = p.bob_wild_ideas
        status["bob_hold_my_beer_count"] = p.bob_hold_my_beer_count
        status["bob_at_cupboard"] = p.bob_at_cupboard
        status["duct_tape_inventory"] = p.carl_duct_tape_inventory
        status["telepathic_bond"] = (
            "strong" if p.telepathic_consensus_strength > 0.7
            else "moderate" if p.telepathic_consensus_strength > 0.4
            else "weak"
        )

        return status

    async def emit_decision(self, pipeline_result: Dict[str, Any]) -> None:
        """
        Emit full ML pipeline decision to frontend.

        Args:
            pipeline_result: Complete result from HamstersOrchestrator.run_pipeline()
        """
        try:
            from app.services.agent_decision_emitter import emit_agent_decision

            context = pipeline_result['context']
            reasoning = pipeline_result['reasoning']
            action = pipeline_result['action']
            learning_record = pipeline_result['learning_record']
            plan = pipeline_result['plan']
            execution_result = pipeline_result['execution_result']
            disk_improvement_pct = pipeline_result['disk_improvement_pct']

            await emit_agent_decision(
                agent_name="hamsters",
                decision_id=learning_record.learning_record_id,
                perception={
                    "disk_usage_percent": context.disk_usage_percent,
                    "fragmentation_level": context.fragmentation_level,
                    "duct_tape_assessment": {
                        "regular_rolls": context.duct_tape_assessment.regular_rolls,
                        "premium_rolls": context.duct_tape_assessment.premium_rolls,
                        "quantum_rolls": context.duct_tape_assessment.quantum_rolls,
                        "total_rolls": context.duct_tape_assessment.total_rolls,
                        "job_complexity": context.duct_tape_assessment.job_complexity,
                    },
                    "beer_consumption": {
                        "steve_beers_today": context.steve_beers_today,
                        "bob_beers_today": context.bob_beers_today,
                        "carl_beers_today": context.carl_beers_today,
                        "total_beers_today": (
                            context.steve_beers_today
                            + context.bob_beers_today
                            + context.carl_beers_today
                        ),
                    },
                    "supply_closet": {
                        "bob_at_cupboard": context.bob_proximity.bob_at_cupboard if context.bob_proximity else False,
                        "stick_panic_level": context.bob_proximity.stick_panic_level if context.bob_proximity else 0.0,
                        "items_acquired": context.bob_proximity.items_acquired if context.bob_proximity else [],
                        "time_of_raid": (
                            context.bob_proximity.time_of_raid.isoformat()
                            if (context.bob_proximity and context.bob_proximity.time_of_raid)
                            else None
                        ),
                    },
                    "complexity_level": context.complexity_level,
                    "ingenuity_required": context.ingenuity_required,
                },
                reasoning={
                    "steve_assessment": {
                        "recommended_fix": reasoning.steve_assessment.recommended_fix,
                        "confidence": reasoning.steve_assessment.confidence,
                        "reasoning": reasoning.steve_assessment.reasoning,
                    },
                    "bob_assessment": {
                        "recommended_fix": reasoning.bob_assessment.recommended_fix,
                        "confidence": reasoning.bob_assessment.confidence,
                        "reasoning": reasoning.bob_assessment.reasoning,
                    },
                    "carl_assessment": {
                        "recommended_fix": reasoning.carl_assessment.recommended_fix,
                        "confidence": reasoning.carl_assessment.confidence,
                        "reasoning": reasoning.carl_assessment.reasoning,
                    },
                    "consensus": reasoning.consensus_fix,
                    "consensus_confidence": reasoning.consensus_confidence,
                    "disagreement_level": reasoning.disagreement_level,
                },
                action_selection={
                    "goal": action.goal,
                    "plan_source": plan.source.value,
                    "plan_primitives": plan.primitives,
                    "plan_confidence": plan.confidence,
                    "alternatives_considered": [
                        reasoning.steve_assessment.recommended_fix,
                        reasoning.bob_assessment.recommended_fix,
                        reasoning.carl_assessment.recommended_fix,
                    ],
                    "exploration": hasattr(action, 'epsilon') and getattr(action, 'epsilon', 0) > 0,
                    "epsilon": getattr(action, 'epsilon', 0.0),
                    "total_beers_consumed": action.total_beers_consumed,
                    "duct_tape_rolls": action.duct_tape_rolls,
                    "requires_sudo": action.requires_sudo,
                    "steve_agreed": action.steve_agreed,
                    "bob_agreed": action.bob_agreed,
                    "carl_agreed": action.carl_agreed,
                },
                execution={
                    "metrics_before": pipeline_result['metrics_before'],
                    "metrics_after": pipeline_result['metrics_after'],
                    "success": execution_result.overall_success,
                    "improvement_percent": disk_improvement_pct,
                    "overall_improvement": execution_result.overall_improvement,
                    "steps_completed": execution_result.steps_completed,
                    "steps_planned": execution_result.steps_planned,
                    "aborted": execution_result.was_aborted,
                    "abort_reason": execution_result.abort_reason,
                    "duration_seconds": execution_result.total_duration_seconds,
                    "plan_source": plan.source.value,
                },
                learning={
                    "situation_fingerprint": learning_record.situation_fingerprint,
                    "stored": learning_record.storage_success,
                    "learning_record_id": learning_record.learning_record_id,
                    "success": execution_result.overall_success,
                },
            )
        except Exception as e:
            logger.error(f"🐹💥 Failed to emit decision: {e}", exc_info=True)

    async def emit_insight(
        self,
        action: str,
        reasoning: str,
        context: Dict[str, Any],
    ) -> None:
        """
        Emit agent insight to frontend narrative feed.

        Args:
            action: Action identifier
            reasoning: Human-readable reasoning
            context: Additional context for the frontend
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight

            await emit_agent_insight(
                from_agent="hamsters",
                to_agent="vic20_sage",
                action=action,
                reasoning=reasoning,
                context=context,
            )
        except Exception as e:
            logger.error(f"🐹💥 Failed to emit insight: {e}", exc_info=True)
