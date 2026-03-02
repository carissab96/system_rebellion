"""
Terry the Meth Snail — WebSocket Emission Layer
=================================================

Owns ALL frontend-facing emission:
- get_agent_status() for heartbeat payloads
- emit_agent_decision() for ML pipeline events
- emit_agent_insight() for narrative feed events

Reads from personality state. Reads from ML pipeline results.
Does not make decisions. Does not send inter-agent messages.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("MethSnail.WebSocket")


class TerryWebSocket:
    """
    Terry's frontend emission layer.

    Reads personality state and pipeline results.
    Formats and emits to frontend via WebSocket.
    """

    def __init__(self, personality):
        """
        Args:
            personality: TerryPersonalityState instance
        """
        self.personality = personality
        self.agent_name = "meth_snail"

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Terry's complete status for heartbeat emission.

        Called by DistributedAgentManager.get_system_status()
        and the heartbeat WebSocket payload.
        """
        p = self.personality

        return {
            "agent_name": self.agent_name,
            "agent_type": "memory_optimizer",
            "is_active": True,
            "total_analyses": p.total_analyses,
            "successful_analyses": p.successful_analyses,
            "shell_spin_count": len(p.shell_spin_incidents),
            "energy_drinks_consumed": getattr(
                p._last_energy_drink_system,
                'energy_drinks_today', 0
            ),
            "current_jitter_level": p._get_jitter_level_name(p._current_jitter),
            "optimization_stats": {
                "total_optimizations": p.total_analyses,
                "successful_optimizations": p.successful_analyses
            },
            "personality_traits": p.personality_traits,
            "override_stats": {
                "total_overrides": p.total_overrides,
                "successful_overrides": p.successful_overrides,
                "override_success_rate": p.override_success_rate
            }
        }

    async def emit_decision(self, pipeline_result: Dict[str, Any]) -> None:
        """
        Emit full ML pipeline decision to frontend.

        Args:
            pipeline_result: Complete result from TerryOrchestrator.run_pipeline()
        """
        try:
            from app.services.agent_decision_emitter import emit_agent_decision

            context = pipeline_result['context']
            reasoning_result = pipeline_result['reasoning_result']
            decision = pipeline_result['decision']
            learning_record = pipeline_result['learning_record']
            action_selector = pipeline_result['action_selector']
            full_metrics = pipeline_result['full_metrics']
            metrics_before = pipeline_result['metrics_before']
            metrics_after = pipeline_result['metrics_after']

            # Calculate improvement
            memory_improvement = 0.0
            if metrics_before['memory_usage'] > 0:
                memory_improvement = (
                    (metrics_before['memory_usage'] - metrics_after['memory_usage'])
                    / metrics_before['memory_usage'] * 100.0
                )

            await emit_agent_decision(
                agent_name="meth_snail",
                decision_id=learning_record.learning_record_id,
                perception={
                    "data_quality_score": context.data_quality_score,
                    "shell_spin_count": context.shell_spin_count,
                    "shell_spin_incidents": [
                        {
                            "reason": incident.reason,
                            "timestamp": incident.timestamp,
                            "severity": incident.severity
                        }
                        for incident in context.shell_spin_incidents
                    ],
                    "metrics": {
                        "cpu": full_metrics.get('cpu_usage', 0),
                        "memory": full_metrics.get('memory_usage', 0),
                        "disk": full_metrics.get('disk_usage', 0)
                    },
                    "similar_situations_found": len(context.similar_situations),
                    "recent_actions_count": len(context.recent_actions),
                    "energy_drink_system": action_selector.energy_drink_system.get_stats()
                },
                reasoning={
                    "root_cause": reasoning_result.root_cause,
                    "confidence": reasoning_result.action_confidence,
                    "evidence": reasoning_result.evidence,
                    "reasoning": reasoning_result.reasoning
                },
                action_selection={
                    "chosen_action": decision.action,
                    "alternatives_considered": decision.alternatives_considered or [],
                    "exploration": decision.exploration,
                    "epsilon": decision.epsilon,
                    "confidence": decision.confidence,
                    "followed_vic20": decision.followed_vic20,
                    "energy_drink_consumed": decision.energy_drink_consumed,
                    "hawk_veto": decision.hawk_veto,
                    "reasoning": decision.reasoning
                },
                execution={
                    "metrics_before": metrics_before,
                    "metrics_after": metrics_after,
                    "success": learning_record.success,
                    "improvement_percent": memory_improvement,
                    "duration_seconds": pipeline_result['action_result'].get('duration_seconds', 0)
                },
                learning={
                    "fingerprint_l1": learning_record.fingerprint_l1,
                    "fingerprint_l2": learning_record.fingerprint_l2,
                    "fingerprint_l3": learning_record.fingerprint_l3,
                    "stored": learning_record.storage_success,
                    "learning_record_id": learning_record.learning_record_id,
                    "success": learning_record.success
                }
            )
        except Exception as e:
            logger.error(f"🐌💥 Failed to emit decision: {e}", exc_info=True)

    async def emit_insight(
        self,
        action: str,
        reasoning: str,
        context: Dict[str, Any]
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
                from_agent="meth_snail",
                to_agent="vic20_sage",
                action=action,
                reasoning=reasoning,
                context=context
            )
        except Exception as e:
            logger.error(f"🐌💥 Failed to emit insight: {e}", exc_info=True)
