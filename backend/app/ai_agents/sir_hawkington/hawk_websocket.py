"""
Sir Hawkington — WebSocket Emission Layer
==========================================

Owns ALL frontend-facing emission:
- get_agent_status() for heartbeat payloads
- emit_decision() for ML pipeline events
- emit_insight() for narrative feed events

Reads from personality state and ML pipeline results.
Does not make decisions. Does not send inter-agent messages.

Mirrors the structure of meth_snail/terry_websocket.py.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("SirHawkington.WebSocket")


class HawkWebSocket:
    """
    Sir Hawkington's frontend emission layer.

    Reads personality state and pipeline results.
    Formats and emits to frontend via WebSocket.
    """

    def __init__(self, personality):
        """
        Args:
            personality: HawkPersonalityState instance
        """
        self.personality = personality
        self.agent_name  = "sir_hawkington"

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get Sir Hawkington's complete status for heartbeat emission.

        Called by DistributedAgentManager.get_system_status()
        and the heartbeat WebSocket payload.
        """
        p = self.personality

        return {
            "agent_name":     self.agent_name,
            "agent_type":     "triage_commander",
            "is_active":      True,

            # Analysis tracking
            "total_analyses":      p.total_analyses,
            "successful_analyses": p.successful_analyses,

            # Monocle state
            "monocle_state":            p.current_monocle_state.value,
            "monocle_yeet_count":       len(p.monocle_yeet_incidents),
            "monocle_yeets_by_severity": p.monocle_yeets_by_severity,

            # Earl grey tea system
            "earl_grey": p.earl_grey.to_dict(),

            # Escalation stats
            "escalation_stats": {
                "total_alerts_sent":         p.total_alerts_sent,
                "escalated_alerts":          p.escalated_alerts,
                "emergency_alerts":          p.emergency_alerts,
                "cooldown_prevented_alerts": p.cooldown_prevented_alerts,
            },

            # Data quality
            "metrics_quality_stats": p.metrics_quality_stats,

            # Personality
            "personality_traits": p.personality_traits,
            "data_integrity_policy": "ARISTOCRATIC_STANDARDS_ABSOLUTE",
        }

    async def emit_decision(self, pipeline_result: Dict[str, Any]) -> None:
        """
        Emit full ML pipeline decision to frontend.

        Args:
            pipeline_result: Complete result dict from HawkOrchestrator.run_pipeline()
        """
        try:
            from app.services.agent_decision_emitter import emit_agent_decision

            context   = pipeline_result['context']
            reasoning = pipeline_result['reasoning']
            action    = pipeline_result['action']
            learning  = pipeline_result['learning_record']

            await emit_agent_decision(
                agent_name="sir_hawkington",
                decision_id=getattr(learning, 'learning_record_id', None) or "pending",
                perception={
                    "resource_type":           context.resource_type,
                    "current_value":           context.current_value,
                    "threshold":               context.threshold,
                    "severity":                context.severity,
                    "data_quality_score":      context.data_quality_score,
                    "monocle_yeets":           context.monocle_yeet_count,
                    "similar_triages_found":   len(context.similar_triages),
                    "recent_escalations_count": len(context.recent_escalations),
                },
                reasoning={
                    "should_escalate":  reasoning.should_escalate,
                    "risk_level":       reasoning.risk_level,
                    "confidence":       reasoning.confidence,
                    "primary_reason":   reasoning.primary_reason,
                },
                action_selection={
                    "chosen_action":        action.action_type,
                    "target_agent":         action.target_agent,
                    "confidence":           action.confidence,
                    "priority":             action.priority,
                    "monocle_state":        pipeline_result['monocle_state'],
                    "aristocratic_confidence": action.aristocratic_confidence,
                    "reasoning_summary":    action.reasoning_summary,
                },
                learning={
                    "situation_fingerprint": getattr(learning, 'situation_fingerprint', None),
                    "stored":                getattr(learning, 'storage_success', False),
                    "learning_record_id":    getattr(learning, 'learning_record_id', None),
                },
                # Earl grey and monocle personality data
                personality={
                    "earl_grey":     pipeline_result['earl_grey'],
                    "monocle_state": pipeline_result['monocle_state'],
                },
            )

        except Exception as e:
            logger.error(f"🧐💥 Failed to emit decision to frontend: {e}", exc_info=True)

    async def emit_insight(
        self,
        action: str,
        reasoning: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit narrative insight event to frontend.

        Args:
            action:    Action type string
            reasoning: Human-readable reasoning
            context:   Optional context dict
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight

            await emit_agent_insight(
                from_agent="sir_hawkington",
                to_agent=context.get('target_agent', 'the_stick') if context else 'the_stick',
                action=action,
                reasoning=reasoning,
                context=context or {},
            )

        except Exception as e:
            logger.error(f"🧐💥 Failed to emit insight: {e}", exc_info=True)
