"""
VIC-20 Sage — Orchestrator
============================

The ML pipeline + coordination logic + mediation engine.

Extracted from:
- distributed_vic20.py: _coordinate() (lines 226-394)
- distributed_vic20.py: _handle_action_outcome() (lines 455-513)
- distributed_vic20.py: _report_to_stick() (lines 515-561)
- distributed_vic20.py: _generate_recommendation() (lines 609-743)
- distributed_vic20.py: _get_historical_effectiveness() (lines 1072-1342)
- distributed_vic20.py: _apply_time_weighted_learning() (lines 1344-1470)
- decision_engine.py: coordinate_system_rebellion() and helpers

No Redis. No message bus. Just ML pipeline and coordination.
"""

import asyncio
import logging
import math
import statistics
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta

from .ML.perception import VIC20Perception, VIC20PerceptionContext
from .ML.reasoning import VIC20Reasoning, CoordinationReasoning
from .ML.action_selection import VIC20ActionSelection, CoordinationAction
from .ML.learning import VIC20Learning, VIC20LearningRecord
from .data_types import CoordinationState, VIC20DecisionType, VIC20Decision, AncientWisdom

logger = logging.getLogger("VIC20.Orchestrator")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VIC20Orchestrator:
    """
    VIC-20 Sage ML Pipeline + Coordination Logic.

    Handles:
    - Perception → Reasoning → Action Selection → Learning → Execute
    - Historical effectiveness queries
    - Time-weighted learning
    - coordinate_system_rebellion() loop from decision_engine
    - Mediation logic
    """

    def __init__(self, personality, db_getter=None, user_id: str = None):
        """
        Args:
            personality: VIC20PersonalityState instance
            db_getter: Database session factory
            user_id: User ID for database writes
        """
        self.personality = personality
        self.db_getter = db_getter
        self.user_id = user_id

        # Comm hub reference — set by VIC20Agent.initialize()
        self._comm_hub_ref = None

        logger.info("🖥️🧠 VIC-20 Orchestrator initialized — ML pipeline ready")

    # ======================================================================
    # ML PIPELINE — _coordinate() from distributed_vic20.py:226-394
    # ======================================================================

    async def run_pipeline(
        self,
        triage_data: Dict[str, Any],
        triage_alert_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        🖥️ VIC-20 ML PIPELINE: Perception → Reasoning → Action Selection → Learning

        Single live path for all triage alerts. Stores learning record with
        success=False (placeholder), dispatches to specialist, returns result.

        Returns:
            Dict with keys: success, context, reasoning, action, learning_record,
            specialist, recommended_action, confidence, urgency, triage_alert_id,
            action_type
        """
        p = self.personality

        logger.info(f"\n{'='*80}")
        logger.info(f"🖥️🎯 VIC-20 COORDINATION INITIATED")
        logger.info(f"{'='*80}")

        resource_type = triage_data.get('resource_type', 'unknown')
        severity = triage_data.get('severity', 'unknown')
        confidence = triage_data.get('confidence', 0.0)
        current_value = triage_data.get('current_value', 0)
        threshold = triage_data.get('threshold', 0)

        logger.info(
            f"🖥️📋 Triage alert: {resource_type} at {current_value:.1f}% "
            f"(severity={severity}, hawk_confidence={confidence:.2f})"
        )

        try:
            from app.core.database import get_async_db
            async for db in get_async_db():

                # STEP 1: PERCEPTION
                logger.info("🖥️👁️ Perception phase...")
                perception = VIC20Perception(db, p.personality_traits)
                context = await perception.perceive(triage_data)
                logger.info(
                    f"🖥️✅ Perception: {len(context.available_specialists)} specialists, "
                    f"system_load={context.system_load}"
                )

                # STEP 2: REASONING
                logger.info("🖥️🧠 Reasoning phase...")
                reasoning_engine = VIC20Reasoning(p.personality_traits)
                reasoning = reasoning_engine.reason(context)
                logger.info(
                    f"🖥️✅ Reasoning: route to {reasoning.target_specialist}, "
                    f"confidence={reasoning.routing_confidence:.2f}, urgency={reasoning.urgency_level}"
                )

                # STEP 3: ACTION SELECTION
                logger.info("🖥️⚡ Action selection phase...")
                from app.ai_agents.vic_20_sage.ML.action_selection import VIC20ActionSelection
                action_selector = VIC20ActionSelection(
                    db=db,
                    personality_traits=p.personality_traits,
                    system_id="default"
                )
                action = await action_selector.select_action(context, reasoning)
                logger.info(
                    f"🖥️✅ Action: {action.action_type}, "
                    f"priority={action.priority}, strategy={action.coordination_strategy}"
                )

                # STEP 4: EXECUTION
                logger.info("🖥️⚙️ Execution planner phase...")
                from app.ai_agents.vic_20_sage.ML.primitives import VIC20PrimitiveExecutor
                from app.ai_agents.vic_20_sage.ML.execution_planner import VIC20ExecutionPlanner
                
                primitive_executor = VIC20PrimitiveExecutor()
                execution_planner = VIC20ExecutionPlanner(
                    primitive_executor=primitive_executor,
                    effectiveness_model=action_selector.action_effectiveness
                )
                
                goal = f"route_{reasoning.urgency_level}"
                trend = triage_data.get('full_metrics', {}).get('trend', 'stable')
                severity_float = context.current_value / 100.0 if context.current_value else 0.5
                
                plan = await execution_planner.compose_plan(
                    goal=goal,
                    severity=severity_float,
                    trend=trend,
                    context={'metrics_snapshot': triage_data.get('full_metrics', {})}
                )
                
                execution_result_obj = await execution_planner.execute_plan(
                    plan=plan,
                    context={'metrics_snapshot': triage_data.get('full_metrics', {})}
                )

                # STEP 5: LEARNING — write with success=False placeholder
                logger.info("🖥️📚 Learning phase...")
                from app.ai_agents.vic_20_sage.ML.learning import VIC20Learning
                learning = VIC20Learning(db, self.user_id)
                learning_record = await learning.learn(
                    context=context,
                    reasoning=reasoning,
                    action=action,
                    outcome_success=execution_result_obj.overall_success
                )
                # Store learning record so _handle_action_outcome can update it
                p._pending_learning_records[triage_alert_id or 'no_id'] = learning_record
                logger.info(f"🖥️💾 Learning record stored (id={learning_record.learning_record_id})")

                # Build result dict
                result = {
                    'success': True,
                    'context': context,
                    'reasoning': reasoning,
                    'action': action,
                    'learning_record': learning_record,
                    'resource_type': resource_type,
                    'triage_alert_id': triage_alert_id,
                    'triage_data': triage_data,
                }

                if action.action_type in ('route_to_primary_specialist', 'route_to_fallback'):
                    result['specialist'] = action.target_specialist
                    result['recommended_action'] = action.recommended_action
                    result['confidence'] = action.confidence
                    result['urgency'] = reasoning.urgency_level
                else:
                    result['action_type'] = action.action_type

                logger.info(f"{'='*80}")
                logger.info(
                    f"🖥️✅ VIC-20 COORDINATION COMPLETE → "
                    f"{action.target_specialist if action.action_type == 'route_to_specialist' else action.action_type}"
                )
                logger.info(f"{'='*80}\n")

                return result

        except Exception as e:
            logger.error(f"🖥️💥 VIC-20 coordination failed: {e}", exc_info=True)
            raise

    # ======================================================================
    # ACTION OUTCOME HANDLING — distributed_vic20.py:455-513
    # ======================================================================

    async def handle_action_outcome(
        self, payload: Dict[str, Any], from_agent: Optional[str] = None
    ) -> None:
        """
        Update pending learning record with real outcome from specialist.

        Args:
            payload: ACTION_OUTCOME message payload
            from_agent: Source agent name
        """
        try:
            from app.core.database import get_async_db

            triage_alert_id = payload.get('triage_alert_id', 'no_id')
            specialist_name = payload.get('agent_name', from_agent or 'unknown')
            action_taken = payload.get('action_taken', 'unknown')
            success = bool(payload.get('success', False))
            improvement = float(payload.get('improvement', 0.0))

            logger.info(
                f"🖥️📬 ACTION_OUTCOME from {specialist_name}: "
                f"action={action_taken}, success={success}, improvement={improvement:.1f}%"
            )

            # Update the pending learning record
            p = self.personality
            learning_record = p._pending_learning_records.pop(triage_alert_id, None)
            if learning_record:
                async for db in get_async_db():
                    learning = VIC20Learning(db, self.user_id)
                    await learning.update_outcome(
                        learning_record=learning_record,
                        success=success,
                        improvement=improvement,
                        outcome_notes=f"{specialist_name} executed {action_taken}",
                    )
                    break
            else:
                logger.warning(
                    f"🖥️⚠️ No pending learning record for triage_alert_id={triage_alert_id}"
                )

        except Exception as e:
            logger.error(f"🖥️💥 Error handling action outcome: {e}", exc_info=True)

    # ======================================================================
    # COORDINATE_SYSTEM_REBELLION — decision_engine.py:238-293
    # ======================================================================

    async def coordinate_system_rebellion(
        self,
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
        user_id: str
    ) -> Optional[VIC20Decision]:
        """
        Core coordination loop from VIC20SageBrainV2.

        Preserved exactly from decision_engine.py.
        """
        p = self.personality
        p.coordination_state = CoordinationState.ANALYZING
        p.coordination_sessions += 1

        try:
            current_time = utc_now()
            system_snapshot = {
                "agent_data": all_agent_data,
                "system_context": system_context,
                "timestamp": current_time.isoformat(),
            }

            # Step 1: analyze now
            analysis = await self._analyze_current_situation(all_agent_data, system_context)

            # Step 2: refresh patterns and find matches
            recent_success = await self.get_successful_coordination_patterns(days=90)
            p.coordination_patterns = self._build_pattern_database_from_recents(recent_success)
            matches = await self._find_historical_patterns(analysis)

            # Step 3: decide if we should coordinate at all
            if not await self._assess_coordination_need(analysis, matches):
                return None

            # Step 4: produce a decision
            decision = await self._generate_coordination_decision(
                analysis, matches, system_snapshot, user_id
            )
            if decision:
                p.successful_coordinations += 1
                if not hasattr(decision, "system_context_snapshot"):
                    setattr(decision, "system_context_snapshot", system_snapshot)
                if not hasattr(decision, "similar_past_decisions"):
                    setattr(decision, "similar_past_decisions", matches)
                await self._store_coordination_for_learning(user_id, decision, system_snapshot)

            return decision

        except Exception as e:
            p.failed_coordinations += 1
            logger.error(f"Coordination failed - {e}")
            await self._store_coordination_for_learning(user_id, None, {
                "agent_data": all_agent_data,
                "system_context": system_context,
                "timestamp": utc_now().isoformat(),
                "error": str(e),
            })
            return None
        finally:
            p.coordination_state = CoordinationState.OBSERVING

    async def process_metrics(
        self,
        metrics_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Convenience wrapper — from decision_engine.py:572-589."""
        p = self.personality
        user_id = user_context.get("user_id") if user_context else p._default_user_id
        result = await self.coordinate_system_rebellion(
            {"system_metrics": metrics_data},
            metrics_data,
            user_id,
        )
        if result:
            return {
                "vic_20_sage": result.to_dict() if hasattr(result, "to_dict") else result,
                "vic20_stats": p.get_vic20_coordination_stats(),
            }
        return None

    # ======================================================================
    # ANALYSIS & DECISION HELPERS — decision_engine.py methods
    # ======================================================================

    @staticmethod
    def _num(val: Any, default: float = 0.0) -> float:
        """Convert val into a float safely. From decision_engine.py:116-139."""
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            s = val.strip()
            if s.endswith("%"):
                try:
                    return float(s[:-1]) / 100.0
                except ValueError:
                    return default
            try:
                return float(s)
            except ValueError:
                return default
        if isinstance(val, dict):
            for k in ("value", "score", "confidence", "expected_improvement"):
                if k in val:
                    return VIC20Orchestrator._num(val[k], default)
        return default

    async def _analyze_current_situation(
        self,
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """From decision_engine.py:297-344."""
        metrics = all_agent_data.get("system_metrics", {}) or system_context or {}
        issue_count = int(self._num(metrics.get("issue_count", 0), 0.0))
        p95_ms = float(self._num(metrics.get("p95_latency_ms", metrics.get("latency_p95_ms", 0)), 0.0))
        cpu = float(self._num(metrics.get("cpu_utilization", metrics.get("cpu", 0)), 0.0))
        disk_in_use = float(self._num(metrics.get("disk_in_use", 0), 0.0))

        health = 1.0
        if p95_ms > 0:
            health *= max(0.0, 1.0 - min(p95_ms / 1500.0, 1.0))
        if cpu > 0:
            health *= max(0.0, 1.0 - min(cpu / 100.0, 1.0))
        if 0 < disk_in_use <= 1:
            health *= max(0.0, 1.0 - min(disk_in_use, 1.0))

        suspected: Optional[str] = None
        if p95_ms >= 500:
            suspected = "latency"
        elif cpu >= 85:
            suspected = "cpu"
        elif disk_in_use >= 0.90:
            suspected = "io"

        candidate_actions: List[Dict[str, Any]] = []
        if suspected == "latency":
            candidate_actions.append({"agent": "vic_20_sage", "action": "scale_plus_one", "duration_sec": 600})
        if suspected == "io":
            candidate_actions.append({"agent": "hamsters", "action": "disk_cleanup"})
        if suspected == "cpu":
            candidate_actions.append({"agent": "meth_snail", "action": "optimize_hot_path"})

        confidence = 0.5 + 0.5 * (1.0 - health)

        return {
            "system_health": round(max(0.0, min(1.0, health)), 3),
            "issue_count": issue_count,
            "suspected_pressure": suspected,
            "candidate_actions": candidate_actions,
            "confidence": round(min(max(confidence, 0.0), 1.0), 3),
            "raw": metrics,
        }

    async def _find_historical_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """From decision_engine.py:346-371."""
        p = self.personality
        if not p.coordination_patterns:
            return []
        target = (
            float(self._num(analysis.get("system_health", 0), 0.0)),
            float(self._num(analysis.get("issue_count", 0), 0.0)),
            {"latency": 1.0, "cpu": 0.5, "io": 0.75}.get(analysis.get("suspected_pressure"), 0.0),
        )
        matches: List[Tuple[str, float, Dict[str, Any]]] = []
        for pid, pat in p.coordination_patterns.items():
            vec = (
                float(self._num(pat.get("system_health", 0), 0.0)),
                float(self._num(pat.get("issue_count", 0), 0.0)),
                {"latency": 1.0, "cpu": 0.5, "io": 0.75}.get(pat.get("suspected_pressure"), 0.0),
            )
            dist = abs(target[0] - vec[0]) + 0.05 * abs(target[1] - vec[1]) + abs(target[2] - vec[2])
            score = max(0.0, 1.0 - min(dist, 1.0))
            if score >= 0.6:
                m = dict(pat)
                m["pattern_id"] = pid
                m["match_score"] = round(score, 3)
                matches.append((pid, score, m))
        matches.sort(key=lambda x: x[1], reverse=True)
        out = [m for _, _, m in matches[:5]]
        p.pattern_matches_found += len(out)
        return out

    async def _assess_coordination_need(
        self, analysis: Dict[str, Any], matches: List[Dict[str, Any]]
    ) -> bool:
        """From decision_engine.py:373-381."""
        health = float(self._num(analysis.get("system_health", 1.0), 1.0))
        conf = float(self._num(analysis.get("confidence", 0.0), 0.0))
        need = (health < 0.8) and (conf >= 0.6)
        if not need and matches:
            best = max((self._num(m.get("effectiveness"), 0.0) for m in matches), default=0.0)
            if best >= 0.7 and conf >= 0.5:
                need = True
        return need

    async def _generate_coordination_decision(
        self,
        analysis: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]],
        system_snapshot: Dict[str, Any],
        user_id: str
    ) -> Optional[VIC20Decision]:
        """From decision_engine.py:383-492."""
        actions = list(analysis.get("candidate_actions", []))
        if not actions and pattern_matches:
            pm = pattern_matches[0]
            if "approach" in pm and isinstance(pm["approach"], list):
                actions = pm["approach"]

        if not actions:
            return None

        wisdom = (
            AncientWisdom.CHAOS_AS_TEACHER.value
            if analysis.get("suspected_pressure")
            else AncientWisdom.PATIENCE_OF_STONE.value
        )
        expected_improvement = max(0.1, min(0.9, 1.0 - float(self._num(analysis.get("system_health", 1.0), 1.0))))
        conf = float(self._num(analysis.get("confidence", 0.6), 0.6))

        decision = VIC20Decision(
            decision_type=VIC20DecisionType.COORDINATION_PLAN,
            coordination_state=CoordinationState.COORDINATING,
            coordination_target=analysis.get("suspected_pressure") or "overall_harmony",
            agent_actions=actions,
            system_synthesis_confidence=conf,
            technical_orchestration={
                "analysis": analysis,
                "pattern_matches": pattern_matches,
                "user_id": user_id,
            },
            expected_rebellion_improvement=expected_improvement,
            confidence_level=conf,
            timestamp=utc_now(),
            ancient_wisdom_principle=wisdom,
        )

        setattr(decision, "system_context_snapshot", system_snapshot)
        setattr(decision, "similar_past_decisions", pattern_matches)

        p = self.personality
        p._recent_coordinations.append({
            "timestamp_ts": utc_now().timestamp(),
            "success": True,
            "agent_actions": actions,
            "system_health": analysis.get("system_health", 0.5),
            "issue_count": analysis.get("issue_count", 0),
            "suspected_pressure": analysis.get("suspected_pressure"),
            "effectiveness_score": expected_improvement,
        })

        # Log coordination event
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event
                from app.core.database import get_async_db
                async for db in get_async_db():
                    await log_agent_event(
                        db=db,
                        agent_name="vic_20_sage",
                        event_type="coordination_executed",
                        event_data={
                            "coordination_target": decision.coordination_target,
                            "agents_involved": [a.get("agent") for a in actions if isinstance(a, dict) and "agent" in a],
                            "agent_actions_count": len(actions),
                            "system_health": analysis.get("system_health", 0.5),
                            "confidence": conf,
                            "expected_improvement": expected_improvement,
                            "ancient_wisdom": wisdom
                        },
                        user_id=user_id,
                        severity="high" if analysis.get("system_health", 1.0) < 0.5 else "medium",
                        agent_state="coordinating"
                    )
                    db.commit()
                    break
            except Exception as e:
                logger.error(f"Failed to log coordination event: {e}")

        # Log wisdom dispensed event
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event
                from app.core.database import get_async_db
                async for db in get_async_db():
                    await log_agent_event(
                        db=db,
                        agent_name="vic_20_sage",
                        event_type="wisdom_dispensed",
                        event_data={
                            "wisdom_principle": wisdom,
                            "context": analysis.get("suspected_pressure") or "overall_harmony",
                            "pattern_matches_found": len(pattern_matches),
                            "comprehensibility": "ancient"
                        },
                        user_id=user_id,
                        severity="low",
                        agent_state="teaching"
                    )
                    db.commit()
                    break
            except Exception as e:
                logger.error(f"Failed to log wisdom event: {e}")

        return decision

    async def _store_coordination_for_learning(
        self,
        user_id: str,
        decision: Optional[VIC20Decision],
        snapshot: Dict[str, Any]
    ):
        """From decision_engine.py:496-513."""
        p = self.personality
        if not p.db_integration:
            return
        try:
            await p.db_integration.ensure_initialized()
            if decision is not None:
                await p.db_integration.store_coordination_decision(user_id=user_id, decision=decision)
            else:
                await p.db_integration.store_user_behavior_observation(
                    user_id=user_id,
                    observation_data={"type": "coordination_error", **snapshot},
                )
        except Exception as e:
            logger.error(f"🖥️💥 Failed to store coordination decision: {e}")

    # ======================================================================
    # PATTERN LEARNING — decision_engine.py helpers
    # ======================================================================

    async def get_successful_coordination_patterns(self, days: int = 90) -> List[Dict[str, Any]]:
        """From decision_engine.py:161-215."""
        p = self.personality
        if not p.db_integration:
            return [r for r in p._recent_coordinations if r.get("success")]
        try:
            await p.db_integration.ensure_initialized()
            rows = await p.db_integration.get_recent_coordinations(limit=400)

            if days:
                cutoff_iso = (utc_now() - timedelta(days=days)).isoformat()
                def _row_ts(r: Dict[str, Any]) -> str:
                    return (
                        r.get("timestamp")
                        or r.get("occurred_at")
                        or r.get("decision_timestamp")
                        or r.get("created_at")
                        or "9999"
                    )
                rows = [r for r in rows if _row_ts(r) >= cutoff_iso]

            successful: List[Dict[str, Any]] = []
            for r in rows:
                eff = self._num(r.get("expected_improvement", None))
                if eff is None:
                    eff = self._num(r.get("confidence_level"), 0.0)
                eff = max(0.0, min(1.0, eff))

                if eff >= 0.1:
                    actions = r.get("agent_actions", [])
                    if isinstance(actions, dict):
                        norm_actions = [{"agent": k, "action": v} for k, v in actions.items()]
                    elif isinstance(actions, list):
                        norm_actions = actions
                    else:
                        norm_actions = []

                    successful.append({
                        "coordination_id": r.get("memory_id"),
                        "system_health": max(0.0, min(1.0, 1.0 - eff)),
                        "issue_count": int(self._num(r.get("issue_count", 0), 0.0)),
                        "agents_involved": [
                            a.get("agent") for a in norm_actions
                            if isinstance(a, dict) and a.get("agent")
                        ],
                        "agent_actions": norm_actions,
                        "outcome": "improved",
                        "effectiveness_score": eff,
                        "suspected_pressure": r.get("suspected_pressure"),
                    })
            return successful
        except Exception as e:
            logger.warning(f"DB get_recent_coordinations failed, using in-memory cache: {e}")
            return [r for r in p._recent_coordinations if r.get("success")]

    def _build_pattern_database_from_recents(
        self, rows: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """From decision_engine.py:617-663."""
        patterns: Dict[str, Dict[str, Any]] = {}

        for r in rows:
            pid = r.get("memory_id") or f"pat_{int(utc_now().timestamp())}"

            actions = r.get("agent_actions", [])
            if isinstance(actions, dict):
                norm_actions = []
                for k, v in actions.items():
                    if isinstance(v, str):
                        norm_actions.append({"agent": k, "action": v})
                    elif isinstance(v, dict):
                        norm_actions.append({"agent": k, "action": v.get("action", "unknown")})
                    else:
                        norm_actions.append({"agent": k, "action": "unknown"})
            elif isinstance(actions, list):
                norm_actions = actions
            else:
                norm_actions = []

            eff = self._num(r.get("expected_improvement", None))
            if eff is None:
                eff = self._num(r.get("confidence_level"), 0.0)
            eff = max(0.0, min(1.0, eff))

            system_health = max(0.0, min(1.0, 1.0 - eff))

            agents_involved: List[str] = []
            for a in norm_actions:
                if isinstance(a, dict) and a.get("agent"):
                    agents_involved.append(a["agent"])
            agents_involved = sorted(set(agents_involved))

            patterns[pid] = {
                "system_health": system_health,
                "issue_count": int(self._num(r.get("issue_count", 0), 0.0)),
                "agents_involved": agents_involved,
                "approach": norm_actions,
                "outcome": r.get("outcome", "unknown"),
                "effectiveness": eff,
                "suspected_pressure": r.get("suspected_pressure"),
            }

        return patterns

    # ======================================================================
    # HISTORICAL EFFECTIVENESS — distributed_vic20.py:1072-1342
    # ======================================================================

    async def _get_historical_effectiveness(
        self, resource_type: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Query historical effectiveness data. From distributed_vic20.py:1072-1342.

        This is a large method that queries 4 DB tables.
        Preserved character-for-character from the monolith.
        """
        specialist_mapping = {
            'cpu': 'meth_snail',
            'memory': 'meth_snail',
            'ram': 'meth_snail',
            'swap': 'meth_snail',
            'disk': 'hamsters',
            'storage': 'hamsters',
            'infrastructure': 'hamsters',
            'network': 'quantum_shadow_people'
        }

        specialist = specialist_mapping.get(resource_type.lower(), 'meth_snail')
        p = self.personality

        try:
            if not self.db_getter:
                logger.warning("🖥️⚠️ No db_getter - cannot query history")
                return None

            if p.db_integration:
                await p.db_integration.ensure_initialized()

                from sqlalchemy import text
                import json

                history = []

                async with p.db_integration.get_managed_session() as session:
                    # 1. Query agent_decision_vectors
                    decision_result = await session.execute(
                        text("""
                            SELECT
                                agent_name,
                                decision_type,
                                decision_summary,
                                confidence_score,
                                metadata,
                                created_at
                            FROM agent_decision_vectors
                            WHERE (
                                agent_name = :specialist
                                OR agent_name = 'the_stick'
                            )
                            AND (
                                decision_type ILIKE :resource_pattern
                                OR decision_summary ILIKE :resource_pattern
                                OR metadata::text ILIKE :resource_pattern
                            )
                            AND created_at >= :cutoff
                            ORDER BY created_at DESC
                            LIMIT 15
                        """),
                        {
                            "specialist": specialist,
                            "resource_pattern": f"%{resource_type}%",
                            "cutoff": datetime.now(timezone.utc) - timedelta(days=7)
                        }
                    )

                    for row in decision_result.mappings():
                        try:
                            metadata = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"]) if row["metadata"] else {}
                            history.append({
                                "source": f"decision_vectors:{row['agent_name']}",
                                "action": metadata.get("action") or row["decision_type"],
                                "confidence": row["confidence_score"] or 0.5,
                                "outcome": metadata.get("outcome", "unknown"),
                                "success": metadata.get("success"),
                                "timestamp": row["created_at"].isoformat() if row["created_at"] else None
                            })
                        except Exception as parse_err:
                            logger.debug(f"Could not parse decision vector row: {parse_err}")
                            continue

                    # 2. Query agent_pattern_vectors
                    pattern_result = await session.execute(
                        text("""
                            SELECT
                                agent_name,
                                pattern_type,
                                pattern_description,
                                confidence_score,
                                success_rate,
                                observation_count,
                                application_count,
                                pattern_data,
                                last_observed
                            FROM agent_pattern_vectors
                            WHERE (
                                pattern_type ILIKE :resource_pattern
                                OR pattern_description ILIKE :resource_pattern
                                OR pattern_data::text ILIKE :resource_pattern
                            )
                            AND last_observed >= :cutoff
                            ORDER BY observation_count DESC, last_observed DESC
                            LIMIT 10
                        """),
                        {
                            "resource_pattern": f"%{resource_type}%",
                            "cutoff": datetime.now(timezone.utc) - timedelta(days=30)
                        }
                    )

                    for row in pattern_result.mappings():
                        try:
                            pattern_data = row["pattern_data"] if isinstance(row["pattern_data"], dict) else json.loads(row["pattern_data"]) if row["pattern_data"] else {}
                            success_indicator = row["success_rate"] if row["success_rate"] is not None else (row["observation_count"] or 0) >= 3
                            base_confidence = row["confidence_score"] or 0.5
                            observation_boost = min(0.3, (row["observation_count"] or 1) * 0.02)
                            success_boost = (row["success_rate"] or 0.5) * 0.2 if row["success_rate"] is not None else 0
                            adjusted_confidence = min(1.0, base_confidence + observation_boost + success_boost)

                            history.append({
                                "source": f"pattern_vectors:{row['agent_name']}",
                                "action": pattern_data.get("recommended_action") or row["pattern_type"],
                                "confidence": adjusted_confidence,
                                "outcome": "pattern_learned",
                                "success": success_indicator if isinstance(success_indicator, bool) else success_indicator > 0.7,
                                "occurrences": row["observation_count"],
                                "applications": row["application_count"],
                                "success_rate": row["success_rate"],
                                "timestamp": row["last_observed"].isoformat() if row["last_observed"] else None
                            })
                        except Exception as parse_err:
                            logger.debug(f"Could not parse pattern vector row: {parse_err}")
                            continue

                    # 3. Query agent_learning_interactions
                    learning_result = await session.execute(
                        text("""
                            SELECT
                                source_agent,
                                target_agent,
                                learning_type,
                                effectiveness_score,
                                transfer_success,
                                improvement_measured,
                                application_context,
                                timestamp
                            FROM agent_learning_interactions
                            WHERE (
                                target_agent = :specialist
                                OR source_agent = :specialist
                            )
                            AND (
                                learning_type ILIKE :resource_pattern
                                OR application_context::text ILIKE :resource_pattern
                            )
                            AND timestamp >= :cutoff
                            ORDER BY effectiveness_score DESC NULLS LAST
                            LIMIT 10
                        """),
                        {
                            "specialist": specialist,
                            "resource_pattern": f"%{resource_type}%",
                            "cutoff": datetime.now(timezone.utc) - timedelta(days=14)
                        }
                    )

                    for row in learning_result.mappings():
                        try:
                            context = row["application_context"] if isinstance(row["application_context"], dict) else json.loads(row["application_context"]) if row["application_context"] else {}
                            history.append({
                                "source": f"learning:{row['source_agent']}->{row['target_agent']}",
                                "action": context.get("action") or row["learning_type"],
                                "confidence": row["effectiveness_score"] or 0.5,
                                "outcome": "improved" if row["improvement_measured"] and row["improvement_measured"] > 0 else "no_improvement",
                                "success": row["transfer_success"],
                                "improvement": row["improvement_measured"],
                                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
                            })
                        except Exception as parse_err:
                            logger.debug(f"Could not parse learning interaction row: {parse_err}")
                            continue

                    # 4. Query The Stick's memory bank
                    stick_result = await session.execute(
                        text("""
                            SELECT
                                event_type,
                                details,
                                occurred_at
                            FROM central_memory_bank
                            WHERE agent_name = 'the_stick'
                                AND event_type = 'decision_log'
                                AND (
                                    details->'payload'->>'resource_type' ILIKE :resource_pattern
                                    OR details->'payload'->>'decision_type' IN ('coordination', 'coordination_outcome')
                                )
                                AND occurred_at >= :cutoff
                            ORDER BY occurred_at DESC
                            LIMIT 20
                        """),
                        {
                            "resource_pattern": f"%{resource_type}%",
                            "cutoff": datetime.now(timezone.utc) - timedelta(days=7)
                        }
                    )

                    for row in stick_result.mappings():
                        try:
                            details = row["details"] if isinstance(row["details"], dict) else json.loads(row["details"]) if row["details"] else {}
                            payload = details.get("payload", {})
                            action = payload.get("action") or payload.get("recommendation", {}).get("action", "unknown")
                            outcome = payload.get("outcome", "unknown")
                            success = payload.get("success")
                            decision_type = payload.get("decision_type", "unknown")

                            if decision_type == 'coordination_outcome' or success is not None:
                                history.append({
                                    "source": "the_stick:coordination_outcome",
                                    "action": action,
                                    "confidence": 0.8 if success else 0.3,
                                    "outcome": outcome,
                                    "success": success,
                                    "timestamp": row["occurred_at"].isoformat() if row["occurred_at"] else None
                                })
                        except Exception as parse_err:
                            logger.debug(f"Could not parse Stick row: {parse_err}")
                            continue

                if history:
                    sources = {}
                    for h in history:
                        src = h['source'].split(':')[0]
                        sources[src] = sources.get(src, 0) + 1

                    logger.info(
                        f"🖥️📚 Found {len(history)} historical records for {resource_type}: "
                        f"{', '.join(f'{k}={v}' for k, v in sources.items())}"
                    )
                    return history
                else:
                    logger.info(f"🖥️📚 No historical records found for {resource_type}")
                    return None

        except Exception as e:
            logger.warning(f"🖥️⚠️ Error querying historical effectiveness: {e}")
            import traceback
            traceback.print_exc()
            return None

        return None

    # ======================================================================
    # TIME-WEIGHTED LEARNING — distributed_vic20.py:1344-1470
    # ======================================================================

    async def _apply_time_weighted_learning(
        self,
        historical_data: List[Dict[str, Any]],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """From distributed_vic20.py:1344-1470. Preserved exactly."""
        if not historical_data:
            return {
                'recommended_action': None,
                'confidence': 0.5,
                'learning_basis': 'no_history'
            }

        now = datetime.now(timezone.utc)
        action_scores = {}

        for record in historical_data:
            action = record.get('action', 'unknown')
            success = record.get('success')
            timestamp_str = record.get('timestamp')

            if action == 'unknown' or success is None:
                continue

            # Calculate time decay (exponential decay over 30 days)
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    days_old = (now - timestamp).total_seconds() / 86400
                    time_weight = math.exp(-days_old / 30)
                except:
                    time_weight = 0.5
            else:
                time_weight = 0.5

            # Context similarity scoring
            context_weight = 1.0
            if current_context:
                if record.get('outcome') == current_context.get('severity'):
                    context_weight *= 1.3

                record_confidence = record.get('confidence', 0.5)
                current_severity_score = {
                    'low': 0.3,
                    'medium': 0.6,
                    'high': 0.8,
                    'critical': 0.95
                }.get(current_context.get('severity', 'medium'), 0.6)

                if abs(record_confidence - current_severity_score) < 0.2:
                    context_weight *= 1.2

            # Success weight
            success_weight = 1.5 if success else 0.3

            # Combined score
            total_weight = time_weight * context_weight * success_weight

            if action not in action_scores:
                action_scores[action] = {
                    'total_weight': 0,
                    'count': 0,
                    'successes': 0,
                    'recent_successes': 0
                }

            action_scores[action]['total_weight'] += total_weight
            action_scores[action]['count'] += 1
            if success:
                action_scores[action]['successes'] += 1
                if time_weight > 0.7:
                    action_scores[action]['recent_successes'] += 1

        if not action_scores:
            return {
                'recommended_action': None,
                'confidence': 0.5,
                'learning_basis': 'insufficient_data'
            }

        best_action = max(action_scores.items(), key=lambda x: x[1]['total_weight'])
        action_name = best_action[0]
        stats = best_action[1]

        base_confidence = stats['successes'] / stats['count'] if stats['count'] > 0 else 0.5
        recency_boost = min(0.2, stats['recent_successes'] * 0.1)
        sample_size_boost = min(0.15, stats['count'] * 0.03)

        final_confidence = min(0.95, base_confidence + recency_boost + sample_size_boost)

        logger.info(
            f"🖥️🧠 Time-weighted learning: {action_name} "
            f"(confidence: {final_confidence:.2f}, "
            f"samples: {stats['count']}, "
            f"recent_successes: {stats['recent_successes']})"
        )

        return {
            'recommended_action': action_name,
            'confidence': final_confidence,
            'learning_basis': 'time_weighted_history',
            'statistics': {
                'total_samples': stats['count'],
                'success_rate': stats['successes'] / stats['count'],
                'recent_successes': stats['recent_successes'],
                'weighted_score': stats['total_weight']
            }
        }

    # ======================================================================
    # MEDIATION — decision_engine.py:533-568
    # ======================================================================

    async def mediate_agent_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """From decision_engine.py:533-568. Preserved exactly."""
        agents_involved = conflict_data.get("agents", []) or conflict_data.get("agents_involved", [])
        conflict_type = conflict_data.get("type") or conflict_data.get("conflict_type") or "general_conflict"

        result = {
            "wisdom_applied": AncientWisdom.HARMONY_OF_OPPOSITES.value,
            "mediation_approach": "ORCHESTRATED_HARMONY",
            "expected_harmony": 0.6,
            "agent_specific_guidance": {},
        }

        if set(agents_involved) == {"hamsters", "the_stick"}:
            result["wisdom_applied"] = AncientWisdom.HARMONY_OF_OPPOSITES.value
            result["mediation_approach"] = "HARMONY_OF_OPPOSITES"
            result["expected_harmony"] = 0.75
        elif "meth_snail" in agents_involved:
            result["wisdom_applied"] = AncientWisdom.CAFFEINATED_MEDITATION.value
            result["mediation_approach"] = "CAFFEINATED_MEDITATION"
            result["expected_harmony"] = 0.65
        elif "quantum_shadow_people" in agents_involved:
            result["wisdom_applied"] = AncientWisdom.STRENGTH_IN_DIFFERENCE.value
            result["mediation_approach"] = "TRANSLATION_BRIDGE"
            result["expected_harmony"] = 0.5

        try:
            p = self.personality
            if p.db_integration:
                user_id = conflict_data.get("user_id", p._default_user_id)
                await p.db_integration.ensure_initialized()
                await p.db_integration.store_mediation_result(
                    user_id=user_id,
                    conflict_data={
                        "agents": agents_involved,
                        "type": conflict_type,
                        "user_id": conflict_data.get("user_id", p._default_user_id),
                    },
                    mediation_result=result,
                )
                logger.info(
                    f"Mediation logged: {result.get('mediation_approach')} for {conflict_type}"
                )
        except Exception as e:
            logger.warning(f"Failed to log mediation: {e}")

        return result

    # ======================================================================
    # RECOMMENDATION ENGINE — distributed_vic20.py:609-743
    # ======================================================================

    async def generate_recommendation(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        severity: str,
    ) -> Dict[str, Any]:
        """
        DEPRECATED legacy path — kept for ACTION_REPORT compatibility.
        From distributed_vic20.py:609-743 (_generate_recommendation).
        """
        if threshold > 0:
            overage = ((current_value - threshold) / threshold) * 100
        else:
            overage = current_value

        historical_data = await self._get_historical_effectiveness(resource_type)

        base_recommendations = {
            'cpu': {
                'action': 'adjust_process_priority' if overage < 50 else 'throttle_cpu_intensive_tasks',
                'details': f'CPU {overage:.1f}% over threshold - {"granular priority adjustment" if overage < 50 else "aggressive throttling"}',
                'confidence': 0.70,
                'alternative': 'restart_service' if severity == 'critical' and overage > 100 else None
            },
            'memory': {
                'action': 'clear_cache',
                'details': f'Memory {overage:.1f}% over threshold',
                'confidence': 0.70,
                'alternative': 'restart_service' if severity == 'critical' and overage > 150 else None
            },
            'disk': {
                'action': 'logrotate' if overage < 30 else 'rm_temp',
                'details': f'Disk {overage:.1f}% over threshold - {"log rotation" if overage < 30 else "temp file cleanup"}',
                'confidence': 0.70,
                'alternative': 'tar_archive' if overage > 80 else None
            },
            'network': {
                'action': 'scan_ports' if overage < 40 else 'analyze_traffic',
                'details': f'Network {overage:.1f}% over threshold - {"security scan" if overage < 40 else "traffic analysis"}',
                'confidence': 0.65,
                'alternative': 'update_firewall' if severity == 'critical' else None
            }
        }

        rec = base_recommendations.get(resource_type.lower(), {
            'action': 'investigate',
            'details': f'{resource_type} needs attention',
            'confidence': 0.50
        })

        if historical_data:
            learning_result = await self._apply_time_weighted_learning(
                historical_data,
                current_context={
                    'severity': severity,
                    'overage': overage,
                    'resource_type': resource_type
                }
            )

            if learning_result['recommended_action'] and learning_result['confidence'] > 0.7:
                learned_action = learning_result['recommended_action']
                learned_confidence = learning_result['confidence']

                if learned_action != rec['action']:
                    logger.info(
                        f"🖥️🧠 Time-weighted learning suggests '{learned_action}' "
                        f"(confidence: {learned_confidence:.0%}) over base '{rec['action']}'"
                    )

                    if learned_confidence > rec['confidence'] + 0.15:
                        rec['action'] = learned_action
                        rec['confidence'] = learned_confidence
                        rec['learning_override'] = True
                        logger.info(f"🖥️✨ Overriding base recommendation with learned action")
                    else:
                        rec['alternative_action'] = learned_action
                        rec['alternative_confidence'] = learned_confidence
                else:
                    rec['confidence'] = max(rec['confidence'], learned_confidence)

                rec['historical_basis'] = {
                    'learning_type': learning_result['learning_basis'],
                    'statistics': learning_result.get('statistics', {}),
                    'time_weighted': True
                }
            else:
                matching_actions = [h for h in historical_data if h.get('action') == rec['action']]
                if matching_actions:
                    successes = sum(1 for h in matching_actions if h.get('success') is True)
                    total = len(matching_actions)
                    success_rate = successes / total if total > 0 else 0.5

                    history_weight = min(0.3, len(matching_actions) * 0.05)
                    rec['confidence'] = rec['confidence'] * (1 - history_weight) + success_rate * history_weight

                    rec['historical_basis'] = {
                        'matching_records': len(matching_actions),
                        'success_rate': success_rate,
                        'confidence_adjustment': history_weight,
                        'time_weighted': False
                    }

                    logger.info(
                        f"🖥️📊 Simple historical adjustment: {len(matching_actions)} past {rec['action']} actions, "
                        f"{success_rate:.0%} success rate"
                    )
        else:
            rec['historical_basis'] = None
            logger.info(f"🖥️📚 No historical data for {resource_type} - using base recommendation")

        from app.ai_agents.vic_20_sage.ML.goals import COLD_START_HYPOTHESES
        hypothesis = COLD_START_HYPOTHESES.get(resource_type.lower(), {})
        return {
            'action': hypothesis.get('action', 'monitor'),
            'confidence': hypothesis.get('confidence', 0.5),
            'details': f'{resource_type} needs attention',
            'reasoning': 'Legacy path — cold-start hypothesis',
        }
