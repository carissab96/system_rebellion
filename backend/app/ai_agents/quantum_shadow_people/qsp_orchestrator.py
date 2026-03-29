"""
Quantum Shadow People — Orchestrator (ML Pipeline)
=====================================================

Pure ML pipeline execution. Receives an alert payload, runs:
Perception → Reasoning → Action Selection → Execution → Learning

Extracted from distributed_qsp._handle_coordination_request (lines 166–538).

Calls personality methods for state mutation (tequila shots, paranoia).
Returns structured result dict — does NOT touch Redis or WebSocket.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("QSP.Orchestrator")


class QSPOrchestrator:
    """
    Quantum Shadow People ML Pipeline.

    Runs the full Perception → Reasoning → Action Selection →
    Execution (planner + primitives) → Learning chain.

    Does NOT send messages, emit WebSocket events, or write to Redis.
    All of that is the communication layer's job.
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        self.personality = personality
        self.db_getter = db_getter or personality.db_getter
        self.user_id = user_id

        # Set by communication layer after init
        self._comm_hub_ref = None

        logger.info("👻🧠 QSP Orchestrator initialized — ML pipeline ready")

    async def run_pipeline(self, alert_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full ML pipeline for a coordination request.

        Args:
            alert_payload: Dict with resource_type, severity, current_value,
                           threshold, recommendation, full_metrics

        Returns:
            Dict with keys: success, perception, reasoning, action, execution,
            learning, network_result
        """
        resource_type = alert_payload.get("resource_type", "unknown")
        severity = alert_payload.get("severity", "unknown")
        recommendation = alert_payload.get("recommendation", {})
        current_value = alert_payload.get("current_value", 0)
        threshold = alert_payload.get("threshold", 0)
        full_metrics = alert_payload.get("full_metrics", {})

        logger.info(
            f"👻📬 COORDINATION REQUEST: "
            f"{resource_type} at {current_value:.1f}% — "
            f"VIC-20 suggests: {recommendation.get('action', 'unknown')}"
        )

        try:
            db_gen = self.db_getter()
            async for db in db_gen:
                # STEP 1: PERCEPTION
                from app.ai_agents.quantum_shadow_people.ML.perception import (
                    QSPPerception,
                )

                perception = QSPPerception(db, self.personality.personality_traits)
                context = await perception.perceive(
                    {
                        "resource_type": resource_type,
                        "severity": severity,
                        "current_value": current_value,
                        "threshold": threshold,
                        "recommendation": recommendation,
                        "full_metrics": full_metrics,
                    }
                )

                logger.info(
                    f"👻👁️ Perception complete — "
                    f"threat_level: {context.threat_level}, "
                    f"quantum_state: {context.quantum_state.state}"
                )

                # STEP 2: REASONING
                from app.ai_agents.quantum_shadow_people.ML.reasoning import (
                    QSPReasoning,
                )

                reasoning = QSPReasoning(
                    self.personality.personality_traits,
                    db,
                    getattr(self.personality, "system_id", None),
                )
                reasoning_result = await reasoning.reason(context)

                logger.info(
                    f"👻🧠 Reasoning complete: "
                    f"{reasoning_result.threat_classification} → "
                    f"{reasoning_result.recommended_response} "
                    f"(confidence: {reasoning_result.confidence:.2f})"
                )

                # STEP 3: ACTION SELECTION
                from app.ai_agents.quantum_shadow_people.ML.action_selection import (
                    QSPActionSelection,
                )

                action_selector = QSPActionSelection(
                    self.personality.personality_traits,
                    db,
                    getattr(self.personality, "system_id", None),
                )
                decision = await action_selector.select_action(context, reasoning_result)

                logger.info(
                    f"👻⚡ Action selected: {decision.action_type} "
                    f"(quantum_state: {decision.quantum_state})"
                )

                # STEP 4: EXECUTION
                logger.info(f"👻🔒 EXECUTING QUANTUM ACTION: {decision.action_type}")

                from app.ai_agents.quantum_shadow_people.ML.primitives import (
                    QSPPrimitiveExecutor,
                )
                from app.ai_agents.quantum_shadow_people.ML.execution_planner import (
                    QSPExecutionPlanner,
                )

                primitive_executor = QSPPrimitiveExecutor()
                planner = QSPExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=action_selector.action_effectiveness,
                    learned_thresholds=action_selector.learned_thresholds,
                )

                goal = reasoning_result.root_cause
                plan = await planner.compose_plan(
                    goal=goal,
                    severity=decision.severity_score,
                    trend="rising" if decision.severity_score >= 0.5 else "stable",
                    context={},
                )
                execution_result = await planner.execute_plan(plan, context={})

                metrics_before = (
                    execution_result.primitive_results[0].pre_metrics
                    if execution_result.primitive_results
                    else {}
                )
                metrics_after = (
                    execution_result.primitive_results[-1].post_metrics
                    if execution_result.primitive_results
                    else {}
                )
                network_result = {
                    "success": execution_result.overall_success,
                    "improvement": execution_result.overall_improvement,
                    "plan_source": plan.source.value,
                    "steps_completed": execution_result.steps_completed,
                    "aborted": execution_result.was_aborted,
                    "abort_reason": execution_result.abort_reason,
                }

                # STEP 5: LEARNING
                from app.ai_agents.quantum_shadow_people.ML.learning import (
                    QSPLearning,
                )

                learning = QSPLearning(db, self.user_id)
                learning_record = await learning.learn(
                    context=context,
                    reasoning=reasoning_result,
                    action=decision,
                    outcome_success=network_result.get("success", False),
                )

                # Build pre/post metric dicts
                pre_metrics_dict = {
                    "total_connections": float(context.total_connections),
                    "suspicious_connections": float(context.suspicious_connections),
                    "network_anomalies": float(context.network_anomalies),
                    "failed_auth_attempts": float(context.failed_auth_attempts),
                    "recv_rate_bps": float(context.recv_rate_bps),
                }
                post_metrics_dict = (
                    dict(metrics_after)
                    if metrics_after and not metrics_after.get("collection_failed")
                    else pre_metrics_dict
                )

                # Update learning outcome
                await learning.update_outcome(
                    learning_record,
                    success=network_result["success"],
                    threat_resolved=network_result["success"],
                    false_positive=False,
                    false_negative=False,
                    outcome_notes=(
                        f"Plan '{plan.source.value}' completed "
                        f"{network_result['steps_completed']} steps"
                    ),
                    pre_metrics=pre_metrics_dict,
                    post_metrics=post_metrics_dict,
                )

                # Request Stick validation on success
                if network_result["success"]:
                    try:
                        from app.core.database import get_async_db

                        # VALIDATE LEARNED THRESHOLDS FIRST
                        for metric in ["suspicious_connections", "network_anomalies", "total_connections", "failed_auth_attempts"]:
                            value = pre_metrics_dict.get(metric)
                            if value is None:
                                continue
                                
                            warning_thresh = await learning.learned_thresholds.get_threshold(metric, 'warning')
                            critical_thresh = await learning.learned_thresholds.get_threshold(metric, 'critical')
                            threshold_level = 'critical' if value >= critical_thresh else 'warning'
                            
                            await learning.learned_thresholds.request_stick_validation(
                                metric_name=metric,
                                threshold_level=threshold_level,
                                learned_value=warning_thresh if threshold_level == 'warning' else critical_thresh,
                                default_value=10.0,
                                db_getter=get_async_db,
                            )
                        logger.info("👻📏 Threshold validation request sent to The Stick")

                        # VALIDATE ACTION EFFECTIVENESS
                        pattern = learning.action_effectiveness._create_metric_pattern(
                            pre_metrics_dict, decision.severity_score
                        )
                        await learning.action_effectiveness.request_stick_validation(
                            action=decision.action_type,
                            metric_pattern=pattern,
                            db_getter=get_async_db,
                        )
                        logger.info("👻🎯 Action effectiveness validation request sent to The Stick")
                    except Exception as e:
                        logger.error(f"👻⚠️ Validation request failed: {e}")

                logger.info(
                    f"👻{'✅' if network_result['success'] else '❌'} "
                    f"Pipeline complete: {decision.action_type}, "
                    f"success={network_result['success']}, "
                    f"improvement={network_result['improvement']:.3f}"
                )

                return {
                    "success": True,
                    "context": context,
                    "reasoning": reasoning_result,
                    "decision": decision,
                    "network_result": network_result,
                    "learning_record": learning_record,
                    "metrics_before": metrics_before,
                    "metrics_after": metrics_after,
                    "pre_metrics_dict": pre_metrics_dict,
                    "post_metrics_dict": post_metrics_dict,
                    "plan_source": plan.source.value,
                    "resource_type": resource_type,
                    "severity": severity,
                    "alert_payload": alert_payload,
                }

        except Exception as e:
            logger.error(f"👻💥 QSP ML PIPELINE FAILED: {e}", exc_info=True)
            return await self._handle_pipeline_failure(
                e, resource_type, severity, current_value, threshold, full_metrics
            )

    async def _handle_pipeline_failure(
        self,
        error: Exception,
        resource_type: str,
        severity: str,
        current_value: float,
        threshold: float,
        full_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Emergency fallback when ML pipeline fails.

        Only takes action if there's an active critical threat.
        """
        from app.services.system_failure_emitter import (
            emit_system_failure_event,
            record_emergency_action,
        )

        await emit_system_failure_event(
            agent_name="quantum_shadow_people",
            failure_type="ML_PIPELINE_FAILURE",
            error=str(error),
            emergency_action_taken=False,
            context={
                "resource_type": resource_type,
                "current_value": current_value,
                "threshold": threshold,
                "severity": severity,
            },
        )

        threat_indicators = {
            "suspicious_connections": full_metrics.get("suspicious_connections", 0),
            "failed_auth_attempts": full_metrics.get("failed_auth_attempts", 0),
            "network_anomalies": full_metrics.get("network_anomalies", 0),
        }

        is_critical_threat = (
            severity in ["critical", "emergency"]
            or threat_indicators["suspicious_connections"] > 50
            or threat_indicators["failed_auth_attempts"] > 20
            or threat_indicators["network_anomalies"] > 10
        )

        if is_critical_threat:
            logger.error(
                "🚨 ACTIVE CRITICAL THREAT + ML DOWN: "
                "Emergency block to prevent security breach"
            )

            from app.ai_agents.distributed.system_actions import SystemActions

            block_result = await SystemActions.throttle_network_operations()

            await record_emergency_action(
                agent="quantum_shadow_people",
                action="emergency_network_throttle",
                reason=f"ML_PIPELINE_FAILURE + active_critical_threat (severity={severity})",
                ml_informed=False,
                metrics_before={"threat_indicators": threat_indicators},
                metrics_after={
                    "connections_throttled": block_result.get("connections_reduced", 0)
                },
                success=block_result.get("success", False),
            )

            return {
                "success": False,
                "error": str(error),
                "emergency_action": True,
                "block_result": block_result,
            }
        else:
            logger.error(
                "   No active critical threat. No emergency action. FIX THE ML PIPELINE."
            )
            from app.ai_agents.exceptions import MLPipelineFailure

            raise MLPipelineFailure(f"QSP ML pipeline failed: {error}") from error
