"""
Sir Hawkington — ML Pipeline Orchestrator
===========================================

The decomposed god function.

Receives alert payload from the communication layer.
Runs the ML pipeline: perception → reasoning → action selection → learning.
Updates personality state with results.
Returns structured results for communication and websocket layers.

Does not handle messaging. Does not emit to frontend.
Pure pipeline orchestration.

Mirrors the structure of meth_snail/terry_orchestrator.py.
"""

import logging
from typing import Dict, Any, Optional
from datetime import date

logger = logging.getLogger("SirHawkington.Orchestrator")


class HawkOrchestrator:
    """
    Orchestrates Sir Hawkington's ML pipeline.

    Runs perception → reasoning → action selection → learning.
    Reads and writes personality state.
    Returns results for communication and websocket layers.
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        """
        Args:
            personality: HawkPersonalityState instance
            db_getter:   Database session factory
            user_id:     User ID for database writes
        """
        self.personality = personality
        self.db_getter   = db_getter
        self.user_id     = user_id
        self._comm_hub_ref = None   # Set by HawkingtonAgent after communication init

    async def run_pipeline(self, alert_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run the complete ML pipeline for an incoming alert.

        Args:
            alert_payload: Resource alert data dict containing at minimum:
                - resource_type: str
                - current_value: float
                - threshold:     float
                - severity:      str
                - full_metrics:  Dict (may be empty)

        Returns:
            Complete pipeline result dict, or None on failure.
            Contains all data needed by communication and websocket layers.
        """
        # Daily earl grey reset on first pipeline run of the day
        self.personality._reset_earl_grey_if_needed()

        resource_type = alert_payload.get('resource_type', 'unknown')
        severity      = alert_payload.get('severity', 'unknown')
        current_value = alert_payload.get('current_value', 0.0)
        threshold     = alert_payload.get('threshold', 0.0)
        full_metrics  = alert_payload.get('full_metrics', {})
        triage_alert_id = alert_payload.get('triage_alert_id')

        result = None

        try:
            db_gen = self.db_getter()
            async for db in db_gen:

                # ── STEP 1: PERCEPTION ────────────────────────────────────────
                from app.ai_agents.sir_hawkington.ML.perception import HawkPerception

                perception = HawkPerception(db, self.personality.personality_traits)
                context = await perception.perceive({
                    'resource_type': resource_type,
                    'current_value': current_value,
                    'threshold':     threshold,
                    'severity':      severity,
                    'full_metrics':  full_metrics,
                })

                # Sync monocle yeets from perception to personality state
                yeet_count = len(perception.monocle_yeet_incidents)
                if yeet_count > 0:
                    for incident in perception.monocle_yeet_incidents:
                        self.personality.yeet_monocle(
                            reason=incident.reason,
                            resource_type=incident.affected_resource,
                            intensity="moderate",
                            user_id=self.user_id,
                        )
                    logger.warning(
                        f"🧐💥 {yeet_count} monocle yeet(s) during perception — "
                        f"data quality: {context.data_quality_score:.2f}"
                    )

                # ── STEP 2: REASONING ─────────────────────────────────────────
                from app.ai_agents.sir_hawkington.ML.reasoning import HawkReasoning

                reasoning_layer = HawkReasoning(self.personality.personality_traits)
                reasoning = reasoning_layer.reason(context)

                # ── STEP 3: ACTION SELECTION ──────────────────────────────────
                from app.ai_agents.sir_hawkington.ML.action_selection import HawkActionSelection

                action_layer = HawkActionSelection(
                    db=db,
                    personality_traits=self.personality.personality_traits,
                    system_id="default"
                )
                action = await action_layer.select_action(context, reasoning)

                # ── STEP 4: EXECUTION ─────────────────────────────────────────
                from app.ai_agents.sir_hawkington.ML.primitives import HawkPrimitiveExecutor
                from app.ai_agents.sir_hawkington.ML.execution_planner import HawkExecutionPlanner
                
                primitive_executor = HawkPrimitiveExecutor()
                execution_planner = HawkExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=action_layer.action_effectiveness
                )
                
                goal = f"triage_{reasoning.risk_level}"
                trend = full_metrics.get('trend', 'stable') if full_metrics else 'stable'
                severity_float = context.current_value / 100.0 if context.current_value else 0.5
                
                plan = await execution_planner.compose_plan(
                    goal=goal,
                    severity=severity_float,
                    trend=trend,
                    context={'metrics_snapshot': full_metrics}
                )
                
                execution_result_obj = await execution_planner.execute_plan(
                    plan=plan,
                    context={'metrics_snapshot': full_metrics}
                )

                # ── EARL GREY / MONOCLE YEET CALL SITES ──────────────────────
                #
                # DISMISS (normal, no escalation needed):
                #   sip earl grey, polish monocle
                #
                # ESCALATE (single-agent coordination or multi-agent emergency):
                #   interrupt earl grey, yeet monocle
                #
                if action.action_type == 'dismiss':
                    # 🧐☕ Everything is fine. Sip tea.
                    self.personality.sip_earl_grey()
                    self.personality.polish_monocle()
                    logger.info(
                        f"🧐⏸️ NOT escalating {resource_type} — "
                        f"action={action.action_type}, "
                        f"confidence={action.confidence:.2f}"
                    )
                else:
                    # 🧐☕💢 Something requires action. Tea interrupted.
                    self.personality.interrupt_earl_grey()
                    if action.action_type == 'escalate' and reasoning.risk_level == 'critical':
                        self.personality.yeet_monocle(
                            reason=reasoning.primary_reason,
                            resource_type=resource_type,
                            intensity="severe",
                            user_id=self.user_id,
                        )
                    else:
                        self.personality.adjust_monocle()
                    logger.info(
                        f"🧐📨 Escalating {resource_type} alert to VIC-20 — "
                        f"action={action.action_type}, "
                        f"target={action.target_agent}, "
                        f"priority={action.priority}"
                    )
                    self.personality.record_escalation(
                        emergency=(action.priority == 'critical')
                    )

                # ── STEP 5: LEARNING ──────────────────────────────────────────
                from app.ai_agents.sir_hawkington.ML.learning import HawkLearning

                learning_layer = HawkLearning(db, self.user_id)
                learning_record = await learning_layer.learn(
                    context=context,
                    reasoning=reasoning,
                    action=action,
                    outcome_success=execution_result_obj.overall_success
                )

                # Update analysis counters
                self.personality.record_analysis(success=True)

                # ── ASSEMBLE RESULT ───────────────────────────────────────────
                result = {
                    'triage_alert_id': triage_alert_id,
                    'resource_type':   resource_type,
                    'severity':        severity,
                    'current_value':   current_value,
                    'threshold':       threshold,

                    # ML pipeline outputs
                    'context':         context,
                    'reasoning':       reasoning,
                    'action':          action,
                    'execution_result': execution_result_obj,
                    'learning_record': learning_record,

                    # Personality state snapshot for emission
                    'monocle_state':      self.personality.current_monocle_state.value,
                    'earl_grey':          self.personality.earl_grey.to_dict(),
                    'data_quality_score': context.data_quality_score,

                    # Routing decision summary
                    'should_escalate':  action.action_type != 'dismiss',
                    'target_agent':     action.target_agent,
                    'priority':         action.priority,
                    'confidence':       action.confidence,
                    'reasoning_summary': action.reasoning_summary,

                    # Full metrics for downstream use
                    'full_metrics':    full_metrics,
                }

                logger.info(
                    f"🧐✅ Pipeline complete: {resource_type} → "
                    f"action={action.action_type}, "
                    f"monocle={self.personality.current_monocle_state.value}, "
                    f"earl_grey={self.personality.earl_grey.current_cup_sips}/"
                    f"{self.personality.earl_grey.sips_per_cup}"
                )

                break   # Only need one db session

        except Exception as e:
            logger.error(
                f"🧐💥 ARISTOCRATIC HORROR — Pipeline failed for {resource_type}: {e}",
                exc_info=True,
            )
            self.personality.record_analysis(success=False)
            return None

        return result
