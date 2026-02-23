#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Action Selection - Quantum Security Response

ML-driven action selection. No ACTION_MAP. No epsilon-greedy. No throttle bias.

Flow:
  1. learned_thresholds.assess_severity() → continuous severity score
  2. action_effectiveness.score_all_actions() → ranked action scores
  3. Quantum personality overlay (does NOT change selected action)
  4. Emit decision to The Stick

Reference: Terry's action_selection.py
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .perception import QSPPerceptionContext
from .reasoning import SecurityReasoning
from .action_effectiveness import ALL_ACTIONS

logger = logging.getLogger('QSPActionSelection')

UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)


# =============================================================================
# Module-level config — no hardcoded logic in methods.
# =============================================================================

# Minimum effectiveness score to consider an action viable
ACTION_VIABILITY_CONFIG = {
    'min_score_to_select':    0.1,   # Below this, action is not viable
    'confidence_boost_threshold': 0.7,  # Reasoning confidence above this boosts top action
    'reasoning_boost_amount': 0.05,  # How much reasoning confidence boosts the score
}

# Severity thresholds for priority assignment (uses learned severity score 0.0-1.0)
PRIORITY_CONFIG = {
    'urgent_threshold':  0.85,
    'high_threshold':    0.60,
    'normal_threshold':  0.35,
}

# Actions that require escalation regardless of severity
ALWAYS_ESCALATE_ACTIONS = frozenset(['escalate_to_vic20'])

# Actions that are considered immediate (execute without delay)
IMMEDIATE_ACTIONS = frozenset(['block_ips', 'update_firewall', 'close_connections'])


@dataclass
class SecurityResponseAction:
    """QSP's selected security response action."""

    # Core action
    action_type: str
    response_strategy: str

    # Scoring metadata
    priority: str               # 'low', 'normal', 'high', 'urgent'
    confidence: float           # 0.0-1.0
    effectiveness_score: float  # Score from action_effectiveness model
    alternatives_considered: List[str] = field(default_factory=list)

    # Quantum state (personality — reactive, not decision logic)
    quantum_state: str = 'stable'
    existential_dread_level: float = 0.0
    quantum_coherence: float = 1.0

    # Hamster communication (personality)
    quantum_messages_sent: int = 0
    hamster_assistance_requested: bool = False

    # Execution parameters
    immediate_action: bool = False
    requires_escalation: bool = False

    # Learning metadata
    severity_score: float = 0.0         # Continuous severity 0.0-1.0
    primary_metric: str = 'threat_count'
    pre_metrics: Dict[str, float] = field(default_factory=dict)
    learning_record_id: Optional[str] = None


class QSPActionSelection:
    """
    QSP's ML-driven action selection.

    Primary signal: action_effectiveness.score_all_actions()
    Boost signal:   reasoning.confidence (does NOT override primary)
    Personality:    quantum state overlay (reactive metadata only)

    👻 "Selecting quantum response... *existential dread at {level}*"
    """

    def __init__(self, personality_traits: Dict[str, Any], db=None, system_id: str = "default"):
        self.personality_traits = personality_traits
        self.db = db
        self.system_id = system_id

        if not self.db:
            raise ValueError("QSPActionSelection requires a database session.")

        from .learned_thresholds import LearnedThresholds
        from .action_effectiveness import ActionEffectivenessModel

        self.learned_thresholds = LearnedThresholds(db, system_id)
        self.action_effectiveness = ActionEffectivenessModel(db, system_id)

        logger.info("👻🧠 QSP action selection initialized with ML pipeline.")

    async def select_action(
        self,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning,
    ) -> SecurityResponseAction:
        """
        ML-driven action selection.

        1. Get continuous severity score from learned_thresholds
        2. Extract current metrics from context
        3. Score all actions via action_effectiveness model
        4. Apply reasoning confidence boost (does NOT change ranking, only boosts top)
        5. Apply quantum personality overlay (metadata only)
        6. Return SecurityResponseAction
        """
        logger.info("👻⚡ Selecting quantum security response...")

        current_metrics = self._extract_metrics(context)
        primary_metric = self._identify_primary_metric(current_metrics)

        severity_score = await self._get_severity_score(current_metrics, primary_metric)

        try:
            action_scores = await self.action_effectiveness.score_all_actions(
                current_metrics=current_metrics,
                severity=severity_score,
                primary_metric=primary_metric,
            )
        except Exception as e:
            logger.error(f"👻💥 action_effectiveness.score_all_actions() FAILED: {e}", exc_info=True)
            from app.ai_agents.exceptions import ActionSelectionFailure
            raise ActionSelectionFailure(f"Action effectiveness model failed: {e}") from e

        if not action_scores:
            logger.error("👻💥 score_all_actions() returned empty list — no actions to select from.")
            from app.ai_agents.exceptions import ActionSelectionFailure
            raise ActionSelectionFailure("No action scores returned from effectiveness model.")

        # Apply reasoning confidence boost to top action only
        top_score = action_scores[0]
        cfg = ACTION_VIABILITY_CONFIG
        if reasoning.confidence >= cfg['confidence_boost_threshold']:
            boosted_score = top_score.base_score + cfg['reasoning_boost_amount']
            logger.debug(
                f"👻🔬 Reasoning confidence {reasoning.confidence:.2f} boosted "
                f"{top_score.action} score: {top_score.base_score:.3f} → {boosted_score:.3f}"
            )

        selected_action = top_score.action
        alternatives = [s.action for s in action_scores[1:4]]

        priority = self._assign_priority(severity_score)
        immediate = selected_action in IMMEDIATE_ACTIONS
        escalation = selected_action in ALWAYS_ESCALATE_ACTIONS or severity_score >= PRIORITY_CONFIG['urgent_threshold']

        # Quantum personality overlay — reactive metadata, does NOT affect decision
        quantum_state = context.quantum_state.state if context.quantum_state else 'stable'
        existential_dread = context.existential_dread
        coherence = context.quantum_state.coherence if context.quantum_state else 1.0

        action = SecurityResponseAction(
            action_type=selected_action,
            response_strategy=reasoning.situation_description,
            priority=priority,
            confidence=reasoning.confidence,
            effectiveness_score=top_score.base_score,
            alternatives_considered=alternatives,
            quantum_state=quantum_state,
            existential_dread_level=existential_dread,
            quantum_coherence=coherence,
            quantum_messages_sent=len(context.quantum_messages),
            hamster_assistance_requested=False,
            immediate_action=immediate,
            requires_escalation=escalation,
            severity_score=severity_score,
            primary_metric=primary_metric,
            pre_metrics=current_metrics,
        )

        logger.info(
            f"👻✅ Action selected: {selected_action} "
            f"(score={top_score.base_score:.3f}, severity={severity_score:.2f}, "
            f"priority={priority}, quantum_state={quantum_state})"
        )

        return action

    async def record_outcome(
        self,
        action: SecurityResponseAction,
        post_metrics: Dict[str, float],
        success: bool,
    ):
        """
        Record outcome for learning. Delegates to action_effectiveness.record_outcome().
        Matches Terry's pattern.
        """
        await self.action_effectiveness.record_outcome(
            action=action.action_type,
            current_metrics=action.pre_metrics,
            severity=action.severity_score,
            primary_metric=action.primary_metric,
            pre_metrics=action.pre_metrics,
            post_metrics=post_metrics,
            success=success,
            other_actions_considered=action.alternatives_considered,
        )

    async def _get_severity_score(
        self,
        current_metrics: Dict[str, float],
        primary_metric: str,
    ) -> float:
        """
        Get continuous severity score 0.0-1.0 from learned thresholds.

        Falls back to a simple ratio if learned_thresholds raises.
        """
        try:
            assessment = await self.learned_thresholds.assess_severity(
                current_metrics=current_metrics,
                primary_metric=primary_metric,
            )
            return assessment['severity_score']
        except Exception as e:
            logger.error(
                f"👻💥 learned_thresholds.assess_severity() FAILED: {e} — "
                f"cannot compute severity. Raising.",
                exc_info=True,
            )
            from app.ai_agents.exceptions import ActionSelectionFailure
            raise ActionSelectionFailure(f"Severity assessment failed: {e}") from e

    def _extract_metrics(self, context: QSPPerceptionContext) -> Dict[str, float]:
        """Extract numeric network metrics from perception context."""
        return {
            'total_connections':       float(context.total_connections),
            'established_connections': float(context.established_connections),
            'suspicious_connections':  float(context.suspicious_connections),
            'network_anomalies':       float(context.network_anomalies),
            'failed_auth_attempts':    float(context.failed_auth_attempts),
            'listening_ports':         float(context.listening_ports),
            'tcp_connections':         float(context.tcp_connections),
            'udp_connections':         float(context.udp_connections),
            'sent_rate_bps':           float(context.sent_rate_bps),
            'recv_rate_bps':           float(context.recv_rate_bps),
            'anomalous_states':        float(context.anomalous_states) if hasattr(context, 'anomalous_states') else 0.0,
            'existential_dread':       float(context.existential_dread),
        }

    def _identify_primary_metric(self, metrics: Dict[str, float]) -> str:
        """Return the metric with the highest absolute value (most pressing concern)."""
        if not metrics:
            return 'threat_count'
        return max(metrics, key=lambda k: abs(metrics[k]))

    def _assign_priority(self, severity_score: float) -> str:
        """Map continuous severity score to priority string using PRIORITY_CONFIG."""
        cfg = PRIORITY_CONFIG
        if severity_score >= cfg['urgent_threshold']:
            return 'urgent'
        elif severity_score >= cfg['high_threshold']:
            return 'high'
        elif severity_score >= cfg['normal_threshold']:
            return 'normal'
        return 'low'
