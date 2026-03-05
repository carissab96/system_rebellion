"""
Quantum Shadow People — WebSocket Emission
=============================================

Frontend emission layer. Builds status payloads and emits
ML decision chains to the WebSocket narrative feed.

Extracted from distributed_qsp.py emit_agent_decision/emit_agent_insight
calls and get_agent_status.

No Redis. No message bus. Just frontend emission.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("QSP.WebSocket")


class QSPWebSocket:
    """
    Quantum Shadow People frontend emission.

    Reads from personality state to build status payloads.
    Emits full ML decision chains and insight events.
    """

    def __init__(self, personality):
        self.personality = personality
        logger.info("👻📡 QSP WebSocket emission layer initialized")

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Build full agent status for frontend display.

        Called by:
        - QSPAgent.get_agent_status()
        - DistributedAgentManager.get_system_status()
        - Heartbeat payload
        """
        return self.personality.get_status()

    async def emit_decision(self, pipeline_result: Dict[str, Any]) -> None:
        """
        Emit full ML decision chain to frontend.

        Args:
            pipeline_result: Dict from QSPOrchestrator.run_pipeline()
        """
        if not pipeline_result.get("success"):
            return

        context = pipeline_result["context"]
        reasoning_result = pipeline_result["reasoning"]
        decision = pipeline_result["decision"]
        network_result = pipeline_result["network_result"]
        learning_record = pipeline_result["learning_record"]
        metrics_before = pipeline_result.get("metrics_before", {})
        metrics_after = pipeline_result.get("metrics_after", {})
        p = self.personality

        try:
            from app.services.agent_decision_emitter import emit_agent_decision

            await emit_agent_decision(
                agent_name="quantum_shadow_people",
                decision_id=learning_record.learning_record_id,
                perception={
                    "threat_level": context.threat_level,
                    "quantum_state": context.quantum_state.state
                    if context.quantum_state
                    else "stable",
                    "existential_dread": context.existential_dread,
                    "total_connections": context.total_connections,
                    "suspicious_connections": context.suspicious_connections,
                    "network_anomalies": context.network_anomalies,
                    "failed_auth_attempts": context.failed_auth_attempts,
                    "recv_rate_bps": context.recv_rate_bps,
                    "tequila_system": {
                        "shots_today": p.tequila_shots_today,
                        "paranoia_level": p.paranoia_level.value,
                        "threats_detected": p.threats_detected,
                        "false_alarms": p.false_alarms,
                    },
                },
                reasoning={
                    "threat_classification": reasoning_result.threat_classification,
                    "root_cause": reasoning_result.root_cause,
                    "confidence": reasoning_result.confidence,
                    "severity_score": reasoning_result.severity_score,
                    "risk_level": reasoning_result.risk_level,
                    "situation_description": reasoning_result.situation_description,
                },
                action_selection={
                    "chosen_action": decision.action_type,
                    "alternatives_considered": decision.alternatives_considered,
                    "confidence": decision.confidence,
                    "priority": decision.priority,
                    "quantum_state": decision.quantum_state,
                    "severity_score": decision.severity_score,
                    "plan_source": network_result["plan_source"],
                    "steps_completed": network_result["steps_completed"],
                },
                execution={
                    "metrics_before": metrics_before,
                    "metrics_after": metrics_after,
                    "success": network_result["success"],
                    "improvement": network_result["improvement"],
                    "aborted": network_result["aborted"],
                    "abort_reason": network_result["abort_reason"],
                },
                learning={
                    "situation_fingerprint": learning_record.situation_fingerprint,
                    "stored": learning_record.storage_success,
                    "learning_record_id": learning_record.learning_record_id,
                    "success": learning_record.success,
                },
            )
            logger.info("👻📡 Full decision chain emitted to frontend")
        except Exception as e:
            logger.error(f"👻⚠️ Failed to emit decision: {e}")

    async def emit_insight(
        self, action: str, reasoning: str, context: Dict[str, Any]
    ) -> None:
        """
        Emit a narrative insight to the frontend WebSocket feed.

        Args:
            action: Action name (e.g. "security_scan_success")
            reasoning: Human-readable reasoning string
            context: Additional context dict
        """
        try:
            from app.services.agent_insight_emitter import emit_agent_insight

            await emit_agent_insight(
                from_agent="quantum_shadow_people",
                to_agent="vic20_sage",
                action=action,
                reasoning=reasoning,
                context=context,
            )
        except Exception as e:
            logger.error(f"👻⚠️ Failed to emit insight: {e}")
