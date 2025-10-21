# app/ai_agents/vic_20_sage/decision_engine.py
"""
VIC-20 Sage: Ancient Wisdom Coordination Master
The wise elder of System Rebellion who mediates conflicts and coordinates agents
NO FAKE DATA - REAL COORDINATION ONLY
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import statistics
from datetime import datetime, timedelta, timezone
import logging
import os
from .data_types import VIC20Decision, CoordinationState, VIC20DecisionType
from .database_integration import VIC20DatabaseIntegration  # wired directly to real DB API


UTC = timezone.utc

logger = logging.getLogger("VIC20Sage")


def utc_now() -> datetime:
    return datetime.now(UTC)


class AncientWisdom(Enum):
    HARMONY_OF_OPPOSITES = "What pulls apart also holds together"
    PATIENCE_OF_STONE = "The mountain moves not, yet shapes the wind"
    CHAOS_AS_TEACHER = "In disorder, find the pattern"
    STRENGTH_IN_DIFFERENCE = "The oak and reed both survive the storm"
    CAFFEINATED_MEDITATION = "Even the energized must sometimes rest"


class VIC20SageBrainV2:
    """
    VIC-20 Sage: streamlined for efficiency while preserving learning
    """

    def __init__(self):
        # The integration should lazily init its engine/connection internally
        self.db = VIC20DatabaseIntegration()

        self.coordination_state = CoordinationState.OBSERVING
        self.logger = logging.getLogger("VIC20Sage.Brain")

        # Learning caches (used as fallback if DB not available)
        self.coordination_patterns: Dict[str, Dict[str, Any]] = {}
        self.effectiveness_history: List[Dict[str, Any]] = []
        self.agent_performance_trends: Dict[str, Dict[str, float]] = {}

        # Thresholds
        self.coordination_thresholds = {
            "minimum_confidence": 0.8,
            "agent_response_time_max": 5.0,
            "system_improvement_target": 0.3,
        }

        # Stats
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.failed_coordinations = 0
        self.pattern_matches_found = 0

        # Local learning buffer (fallback)
        self._recent_coordinations: List[Dict[str, Any]] = []

        # Default user scope for early boot (e.g., prewarm)
        self._default_user_id = "system"

    @property
    def is_active(self) -> bool:
        return True

    def activate(self):
        pass

    def deactivate(self):
        pass

    async def _ensure_db(self):
        """Call integration's initializer if present; don't fail hard on errors."""
        try:
            if hasattr(self.db, "ensure_initialized") and callable(getattr(self.db, "ensure_initialized")):
                await self.db.ensure_initialized()
        except Exception as e:
            self.logger.warning(f"DB init failed, will use in-memory fallbacks: {e}")

    async def initialize_database(self, bootstrap_user_id: Optional[str] = None):
        """Initialize and pre-load learning patterns (non-fatal if DB isn't ready)."""
        if bootstrap_user_id:
            self._default_user_id = bootstrap_user_id
        await self._ensure_db()
        await self._load_learning_patterns()

    # ---------- utility for robust numeric coercions ----------

    @staticmethod
    def _num(val: Any, default: float = 0.0) -> float:
        """
        Convert val into a float safely.
        Accepts int/float, numeric strings, "85%" strings, and dicts like {"value": 0.82}.
        """
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
                    return VIC20SageBrainV2._num(val[k], default)
        return default

    # ---------- learning bootstrap ----------

    async def _load_learning_patterns(self):
        """Load historical patterns + per-agent harmony trends from DB; fallback to cache."""
        try:
            # 1) Successful patterns = recent coordinations with improvement/confidence
            recents = await self.db.get_recent_coordinations(limit=200)
            self.coordination_patterns = self._build_pattern_database_from_recents(recents)

            # 2) Agent trends via harmony status (use default/system user for warmup)
            harmony = await self.db.get_agent_harmony_status(self._default_user_id)
            trends: Dict[str, Dict[str, float]] = {}
            for agent, d in (harmony.get("agent_harmony") or {}).items():
                trends[agent] = {
                    "effectiveness_score": float(self._num(d.get("coordination_effectiveness"), 0.0)),
                    "response_time": float(self._num(d.get("response_time_average"), 0.0)),
                }
            self.agent_performance_trends = trends
        except Exception as e:
            self.logger.warning(f"Load-learning fallback (DB unavailable): {e}")

    # ---------- DB-wired helpers (previously missing) ----------

    async def get_successful_coordination_patterns(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Use DB's get_recent_coordinations and filter to 'successful' based on improvement/confidence.
        Robust to dict/str values.
        """
        await self._ensure_db()
        try:
            rows = await self.db.get_recent_coordinations(limit=400)

            # Optional time filter
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

                if eff >= 0.1:  # "successful enough"
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
            self.logger.warning(f"DB get_recent_coordinations failed, using in-memory cache: {e}")
            return [r for r in self._recent_coordinations if r.get("success")]

    async def get_agent_performance_trends(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """
        Adapt from DB.get_agent_harmony_status(user_id) → per-agent trend dict.
        Uses default/system user; days is informational here.
        """
        await self._ensure_db()
        try:
            h = await self.db.get_agent_harmony_status(self._default_user_id)
            out: Dict[str, Dict[str, float]] = {}
            for agent, d in (h.get("agent_harmony") or {}).items():
                out[agent] = {
                    "effectiveness_score": float(self._num(d.get("coordination_effectiveness"), 0.0)),
                    "response_time": float(self._num(d.get("response_time_average"), 0.0)),
                }
            return out
        except Exception as e:
            self.logger.warning(f"DB harmony status failed, using in-memory trends: {e}")
            return self.agent_performance_trends or {}

    # ---------- core coordination loop ----------

    async def coordinate_system_rebellion(
        self,
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
        user_id: str
    ) -> Optional[VIC20Decision]:
        self.coordination_state = CoordinationState.ANALYZING
        self.coordination_sessions += 1

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
            self.coordination_patterns = self._build_pattern_database_from_recents(recent_success)
            matches = await self._find_historical_patterns(analysis)

            # Step 3: decide if we should coordinate at all
            if not await self._assess_coordination_need(analysis, matches):
                return None

            # Step 4: produce a decision
            decision = await self._generate_coordination_decision(
                analysis, matches, system_snapshot, user_id
            )
            if decision:
                self.successful_coordinations += 1
                # Ensure fields the integration expects
                if not hasattr(decision, "system_context_snapshot"):
                    setattr(decision, "system_context_snapshot", system_snapshot)
                if not hasattr(decision, "similar_past_decisions"):
                    setattr(decision, "similar_past_decisions", matches)
                await self._store_coordination_for_learning(user_id, decision, system_snapshot)

            return decision

        except Exception as e:
            self.failed_coordinations += 1
            self.logger.error(f"Coordination failed - {e}")
            await self._store_coordination_for_learning(user_id, None, {
                "agent_data": all_agent_data,
                "system_context": system_context,
                "timestamp": utc_now().isoformat(),
                "error": str(e),
            })
            return None
        finally:
            self.coordination_state = CoordinationState.OBSERVING

    # ---------- analysis & decision helpers ----------

    async def _analyze_current_situation(
        self,
        all_agent_data: Dict[str, Any],
        system_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize current signals into a small set of features.
        """
        metrics = all_agent_data.get("system_metrics", {}) or system_context or {}
        issue_count = int(self._num(metrics.get("issue_count", 0), 0.0))
        p95_ms = float(self._num(metrics.get("p95_latency_ms", metrics.get("latency_p95_ms", 0)), 0.0))
        cpu = float(self._num(metrics.get("cpu_utilization", metrics.get("cpu", 0)), 0.0))
        disk_in_use = float(self._num(metrics.get("disk_in_use", 0), 0.0))  # 0..1

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

        confidence = 0.5 + 0.5 * (1.0 - health)  # worse health => higher confidence that action helps

        return {
            "system_health": round(max(0.0, min(1.0, health)), 3),
            "issue_count": issue_count,
            "suspected_pressure": suspected,
            "candidate_actions": candidate_actions,
            "confidence": round(min(max(confidence, 0.0), 1.0), 3),
            "raw": metrics,
        }

    async def _find_historical_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.coordination_patterns:
            return []
        target = (
            float(self._num(analysis.get("system_health", 0), 0.0)),
            float(self._num(analysis.get("issue_count", 0), 0.0)),
            {"latency": 1.0, "cpu": 0.5, "io": 0.75}.get(analysis.get("suspected_pressure"), 0.0),
        )
        matches: List[Tuple[str, float, Dict[str, Any]]] = []
        for pid, pat in self.coordination_patterns.items():
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
        self.pattern_matches_found += len(out)
        return out

    async def _assess_coordination_need(self, analysis: Dict[str, Any], matches: List[Dict[str, Any]]) -> bool:
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

        # Ensure attributes the DB writer expects exist
        setattr(decision, "system_context_snapshot", system_snapshot)
        setattr(decision, "similar_past_decisions", pattern_matches)

        # local learning fallback record
        self._recent_coordinations.append({
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
                        agent_name="vic20_sage",
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
                self.logger.error(f"Failed to log coordination event: {e}")
        
        # Log wisdom dispensed event
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event
                from app.core.database import get_async_db
                async for db in get_async_db():
                    await log_agent_event(
                        db=db,
                        agent_name="vic20_sage",
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
                self.logger.error(f"Failed to log wisdom event: {e}")

        return decision

    # ---------- persistence / logging (real DB methods) ----------

    async def _store_coordination_for_learning(
        self,
        user_id: str,
        decision: Optional[VIC20Decision],
        snapshot: Dict[str, Any]
    ):
        await self._ensure_db()
        try:
            if decision is not None:
                await self.db.store_coordination_decision(user_id=user_id, decision=decision)
            else:
                await self.db.store_user_behavior_observation(
                    user_id=user_id,
                    observation_data={"type": "coordination_error", **snapshot},
                )
        except Exception as e:
            self.logger.warning(f"Store-learning fallback (DB unavailable): {e}")
            # still capture locally
            self._recent_coordinations.append({
                "timestamp_ts": utc_now().timestamp(),
                "success": False,
                "agent_actions": [],
                "system_health": 0.0,
                "issue_count": 0,
                "suspected_pressure": None,
                "effectiveness_score": 0.0,
            })

    async def _log_mediation_event(self, mediation_result: Dict[str, Any], conflict_data: Dict[str, Any]):
        """Log mediation via the integration's real method."""
        try:
            user_id = conflict_data.get("user_id", self._default_user_id)
            await self._ensure_db()
            await self.db.store_mediation_result(
                user_id=user_id,
                conflict_data=conflict_data,
                mediation_result=mediation_result,
            )
            self.logger.info(
                f"Mediation logged: {mediation_result.get('mediation_approach')} for {conflict_data.get('type')}"
            )
        except Exception as e:
            self.logger.warning(f"Failed to log mediation: {e}")

    # ---------- mediation (kept compact) ----------

    async def _mediate_agent_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        agents_involved = conflict_data.get("agents", []) or conflict_data.get("agents_involved", [])
        conflict_type = conflict_data.get("type") or conflict_data.get("conflict_type") or "general_conflict"

        # default scaffold
        result = {
            "wisdom_applied": AncientWisdom.HARMONY_OF_OPPOSITES.value,
            "mediation_approach": "ORCHESTRATED_HARMONY",
            "expected_harmony": 0.6,
            "agent_specific_guidance": {},
        }

        # simple flavoring
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
            await self._log_mediation_event(result, {
                "agents": agents_involved,
                "type": conflict_type,
                "user_id": conflict_data.get("user_id", self._default_user_id),
            })
        except Exception:
            pass

        return result

    # ---------- convenience wrappers ----------

    async def process_metrics(
        self,
        metrics_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        user_id = user_context.get("user_id") if user_context else self._default_user_id
        await self.initialize_database(bootstrap_user_id=user_id)
        result = await self.coordinate_system_rebellion(
            {"system_metrics": metrics_data},
            metrics_data,
            user_id,
        )
        if result:
            return {
                "vic_20_sage": result.to_dict() if hasattr(result, "to_dict") else result,
                "vic20_stats": self.get_vic20_coordination_stats(),
            }
        return None

    async def coordinate_agent_emergency_response(
        self,
        emergency_type: str,
        affected_agents: List[str],
        system_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Provide the method your convenience function was calling.
        For v0 we simply log a plan; production could fan-out to orchestration.
        """
        plan = {
            "type": emergency_type,
            "agents": affected_agents,
            "started_at": utc_now().isoformat(),
            "status": "planned",
        }
        await self._store_coordination_for_learning(user_id, None, {
            "emergency": True,
            "plan": plan,
            "system_context": system_context,
        })
        plan["status"] = "completed"
        plan["ended_at"] = utc_now().isoformat()
        return plan

    def _build_pattern_database_from_recents(self, rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Normalize recent coordination rows into a searchable pattern DB (robust to weird types)."""
        patterns: Dict[str, Dict[str, Any]] = {}

        for r in rows:
            pid = r.get("memory_id") or f"pat_{int(utc_now().timestamp())}"

            actions = r.get("agent_actions", [])
            if isinstance(actions, dict):
                # normalize dict → list of {agent, action}
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
            eff = max(0.0, min(1.0, eff))  # clamp

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

    # ---------- public stats ----------

    def get_vic20_coordination_stats(self) -> Dict[str, Any]:
        total = max(1, self.coordination_sessions)
        return {
            "sessions": self.coordination_sessions,
            "successes": self.successful_coordinations,
            "failures": self.failed_coordinations,
            "pattern_matches_found": self.pattern_matches_found,
            "success_rate": round(self.successful_coordinations / total, 3),
        }

    def get_partnership_metrics_data(self, user_id: str) -> Dict[str, Any]:
        avg_eff = statistics.fmean(
            [v.get("effectiveness_score", 0.0) for v in self.agent_performance_trends.values()]
        ) if self.agent_performance_trends else 0.0
        return {
            "user_id": user_id,
            "agent_trends": self.agent_performance_trends,
            "avg_effectiveness": round(avg_eff, 3),
            "suggestions_available": avg_eff < 0.75,
        }


# === Global instance + simple wrappers ===

vic20_brain = VIC20SageBrainV2()


async def coordinate_agents(
    all_agent_data: Dict[str, Any],
    system_context: Dict[str, Any],
    user_id: str
) -> Optional[VIC20Decision]:
    await vic20_brain.initialize_database(bootstrap_user_id=user_id)
    return await vic20_brain.coordinate_system_rebellion(all_agent_data, system_context, user_id)


async def coordinate_emergency_response(
    emergency_type: str,
    affected_agents: List[str],
    system_context: Dict[str, Any],
    user_id: str,
) -> Dict[str, Any]:
    await vic20_brain.initialize_database(bootstrap_user_id=user_id)
    return await vic20_brain.coordinate_agent_emergency_response(
                emergency_type, affected_agents, system_context, user_id
    )


async def mediate_conflict(conflict_data: Dict[str, Any]) -> Dict[str, Any]:
    return await vic20_brain._mediate_agent_conflict(conflict_data)


def get_coordination_stats() -> Dict[str, Any]:
    return vic20_brain.get_vic20_coordination_stats()


def get_partnership_metrics(user_id: str) -> Dict[str, Any]:
    return vic20_brain.get_partnership_metrics_data(user_id)