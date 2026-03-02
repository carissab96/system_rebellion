#!/usr/bin/env python3
"""
QSP's Action Effectiveness Model

Learns which security response works best in which situation.
Scores every available action against the current situation based on
historical outcomes. Provides heuristic bootstrap scoring for cold start.

This is the ENGINE of QSP's decision-making.

Reference: Terry's action_effectiveness.py
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_outcome import ActionOutcomeRecord
from .heuristic_config import ACTION_HEURISTIC_CONFIG, QSP_DOMAIN_METRICS

logger = logging.getLogger('QSPActionEffectiveness')

UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)


# =============================================================================
# Single source of truth for QSP's action vocabulary.
# Import this list in every other file that needs to reference available actions.
# Do NOT duplicate it.
# =============================================================================

ALL_ACTIONS = [
    # Monitoring / investigative actions
    'monitor_passive',
    'investigate_connections',
    'scan_ports',
    'analyze_traffic',
    'quantum_scan',

    # Defensive actions
    'throttle_network',
    'apply_rate_limit',
    'close_connections',

    # Aggressive actions
    'block_ips',
    'update_firewall',

    # Escalation
    'escalate_to_vic20',
]

_CACHE_TTL_SECONDS = 600  # 10 minutes


@dataclass
class ActionScore:
    """Effectiveness score for an action in a specific situation."""
    action: str
    base_score: float
    confidence: float
    expected_improvement: float
    sample_size: int
    reasoning: str
    historical_success_rate: float


class ActionEffectivenessModel:
    """
    QSP's action effectiveness learning system.

    Heuristic bootstrap provides meaningful cold-start scores.
    ML replaces heuristics as ActionOutcomeRecord data accumulates.
    """

    _LOWER_IS_BETTER = frozenset([
        'total_connections', 'suspicious_connections', 'network_anomalies',
        'failed_auth_attempts', 'anomalous_states',
        'sent_rate_bps', 'recv_rate_bps',
    ])

    def __init__(self, db: AsyncSession, system_id: str = "default"):
        self.db = db
        self.system_id = system_id
        self.agent_name = "quantum_shadow_people"
        self.logger = logger
        self._effectiveness_cache: Dict[str, List[ActionScore]] = {}
        self._cache_expiry: Dict[str, datetime] = {}

    async def score_all_actions(
        self,
        current_metrics: Dict[str, float],
        severity: float,
        primary_metric: str,
    ) -> List[ActionScore]:
        """
        Score all available actions for the current situation.

        Args:
            current_metrics: Current security metric values
            severity:        Continuous severity score 0.0-1.0
            primary_metric:  Which metric is driving the situation

        Returns:
            List of ActionScore objects, sorted by base_score descending.
        """
        pattern = self._create_metric_pattern(current_metrics, severity)

        if self._is_cache_valid(pattern):
            return self._effectiveness_cache[pattern]

        scores = []
        for action in ALL_ACTIONS:
            score = await self._score_action(
                action, pattern, current_metrics, severity, primary_metric
            )
            scores.append(score)

        scores.sort(key=lambda s: s.base_score, reverse=True)

        self._effectiveness_cache[pattern] = scores
        self._cache_expiry[pattern] = utc_now().replace(tzinfo=None) + timedelta(
            seconds=_CACHE_TTL_SECONDS
        )
        return scores

    async def _score_action(
        self,
        action: str,
        pattern: str,
        current_metrics: Dict[str, float],
        severity: float,
        primary_metric: str,
    ) -> ActionScore:
        """
        Score a single action. Queries historical outcomes first.
        Falls back to heuristic bootstrap when no data exists.
        Blends recent (70%) with overall (30%) when recent data is available.
        """
        similar_outcomes = await self._query_similar_situations(action, pattern, severity)

        if not similar_outcomes:
            heuristic = self._get_heuristic_score(action, severity, primary_metric)
            return ActionScore(
                action=action,
                base_score=heuristic,
                confidence=0.0,
                expected_improvement=0.0,
                sample_size=0,
                reasoning="Cold start heuristic (no historical data for this pattern)",
                historical_success_rate=0.0,
            )

        sample_size = len(similar_outcomes)
        successful = sum(1 for r in similar_outcomes if r.success)
        success_rate = successful / sample_size

        improvements = [r.improvement for r in similar_outcomes if r.improvement is not None]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

        base_score = (success_rate * 0.6) + (min(1.0, avg_improvement) * 0.4)

        cutoff_recent = utc_now().replace(tzinfo=None) - timedelta(days=7)
        recent_outcomes = [r for r in similar_outcomes if r.created_at >= cutoff_recent]

        if recent_outcomes:
            recent_success_rate = sum(1 for r in recent_outcomes if r.success) / len(recent_outcomes)
            base_score = (recent_success_rate * 0.7) + (base_score * 0.3)
        else:
            recent_success_rate = None

        confidence = min(sample_size / 10.0, 1.0)
        reasoning = (
            f"Success rate: {success_rate:.0%} in {sample_size} similar situations, "
            f"avg improvement: {avg_improvement:.1%}"
        )
        if recent_success_rate is not None and len(recent_outcomes) >= 3:
            reasoning += f" (recent: {recent_success_rate:.0%})"

        return ActionScore(
            action=action,
            base_score=base_score,
            confidence=confidence,
            expected_improvement=avg_improvement,
            sample_size=sample_size,
            reasoning=reasoning,
            historical_success_rate=success_rate,
        )
    
    async def record_outcome(
        self,
        action: str,
        current_metrics: Dict[str, float],
        severity: float,
        primary_metric: str,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
        success: bool,
        other_actions_considered: Optional[List[str]] = None,
    ):
        """
        Record outcome of a security response for learning.

        Vocabulary guard runs BEFORE any DB work.
        Invalidates cache for this pattern when a new outcome is recorded.
        """
        if action not in set(ALL_ACTIONS):
            self.logger.error(
                f"👻💥 record_outcome() rejected unknown action '{action}' — "
                f"not in ALL_ACTIONS vocabulary. "
                f"Vocabulary gap between action_selection.py and action_effectiveness.py."
            )
            return

        pattern = self._create_metric_pattern(pre_metrics, severity)
        primary_metric_used = primary_metric or self._identify_primary_metric(pre_metrics, post_metrics)
        improvement = self._calculate_improvement(pre_metrics, post_metrics, primary_metric_used)

        record = ActionOutcomeRecord(
            agent_name=self.agent_name,
            action=action,
            metric_pattern_fingerprint=pattern,
            pre_metrics=pre_metrics,
            post_metrics=post_metrics,
            severity_score=severity,
            success=success,
            improvement=improvement,
            primary_metric=primary_metric_used,
            other_actions_considered=other_actions_considered or [],
        )

        self.db.add(record)
        await self.db.flush()

        self._invalidate_cache(pattern)

        self.logger.info(
            f"👻📊 Recorded action outcome: {action} for pattern {pattern[:40]}... "
            f"(success={success}, improvement={improvement:.3f})"
        )
    
    def _create_metric_pattern(
        self,
        metrics: Dict[str, float],
        severity: float,
    ) -> str:
        """
        Create a data fingerprint from binned metric values.

        Bins actual values into ranges — NOT if/else classification.
        The pattern is a data fingerprint, not a threat label.
        """
        sev_bin  = int(severity * 10) * 10
        conn_bin = int(metrics.get('total_connections', 0) / 100) * 100
        susp_bin = int(metrics.get('suspicious_connections', 0) / 10) * 10
        anom_bin = int(metrics.get('network_anomalies', 0) / 5) * 5
        auth_bin = int(metrics.get('failed_auth_attempts', 0) / 10) * 10
        recv_bin = int(metrics.get('recv_rate_bps', 0) / 10_000_000) * 10  # 10MB bins

        return (
            f"sev:{sev_bin:02d}"
            f"|conn:{conn_bin:04d}"
            f"|susp:{susp_bin:02d}"
            f"|anom:{anom_bin:02d}"
            f"|auth:{auth_bin:02d}"
            f"|recv:{recv_bin:03d}"
        )

    def _generalize_pattern(self, pattern: str) -> str:
        """Keep only severity and first metric part for fuzzy matching."""
        parts = pattern.split('|')
        return '|'.join(parts[:2]) if len(parts) >= 2 else pattern

    async def _query_similar_situations(
        self,
        action: str,
        pattern: str,
        severity: float,
        lookback_days: int = 60,
        max_results: int = 50,
    ) -> List[Any]:
        """
        Two-tier query: exact pattern first, generalized if < 5 records.

        Exact: severity tolerance ±0.2
        Generalized: severity tolerance ±0.3
        """
        cutoff = utc_now().replace(tzinfo=None) - timedelta(days=lookback_days)

        result = await self.db.execute(
            select(ActionOutcomeRecord).where(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                    ActionOutcomeRecord.metric_pattern_fingerprint == pattern,
                    ActionOutcomeRecord.severity_score >= severity - 0.2,
                    ActionOutcomeRecord.severity_score <= severity + 0.2,
                    ActionOutcomeRecord.created_at >= cutoff,
                )
            ).limit(max_results)
        )
        records = result.scalars().all()

        if len(records) >= 5:
            return records

        generalized = self._generalize_pattern(pattern)
        result = await self.db.execute(
            select(ActionOutcomeRecord).where(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                    ActionOutcomeRecord.metric_pattern_fingerprint.like(f"{generalized}%"),
                    ActionOutcomeRecord.severity_score >= severity - 0.3,
                    ActionOutcomeRecord.severity_score <= severity + 0.3,
                    ActionOutcomeRecord.created_at >= cutoff,
                )
            ).limit(max_results)
        )
        return result.scalars().all()

    def _get_heuristic_score(
        self,
        action: str,
        severity: float,
        primary_metric: str,
    ) -> float:
        """Cold-start heuristic score. Looks up action category, returns severity-correlated score."""
        cfg = ACTION_HEURISTIC_CONFIG

        if action in cfg['escalation_actions']:
            if primary_metric not in QSP_DOMAIN_METRICS:
                return cfg['escalate_out_of_domain']
            return cfg['escalate_in_domain']

        tier = 'high_severity' if severity >= 0.7 else ('mid_severity' if severity >= 0.4 else 'low_severity')

        for category_key, actions in [
            ('aggressive_actions',    cfg['aggressive_actions']),
            ('defensive_actions',     cfg['defensive_actions']),
            ('investigative_actions', cfg['investigative_actions']),
            ('passive_actions',       cfg['passive_actions']),
        ]:
            if action in actions:
                prefix = category_key.replace('_actions', '')
                return cfg.get(f"{prefix}_{tier}", cfg['default_score'])

        return cfg['default_score']

    def _identify_primary_metric(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
    ) -> str:
        """Find the metric with the largest absolute delta between pre and post."""
        best_metric = 'threat_count'
        best_delta = 0.0
        for key in pre_metrics:
            if key in post_metrics:
                delta = abs(pre_metrics[key] - post_metrics[key])
                if delta > best_delta:
                    best_delta = delta
                    best_metric = key
        return best_metric

    def _calculate_improvement(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
        metric_name: str,
    ) -> float:
        """
        Direction-aware improvement calculation.

        For _LOWER_IS_BETTER metrics: reduction = positive improvement.
        Returns value in [-1.0, 1.0].
        """
        pre_val = pre_metrics.get(metric_name, 0.0)
        post_val = post_metrics.get(metric_name, pre_val)

        if pre_val == 0.0 and post_val == 0.0:
            return 0.0

        delta = pre_val - post_val if metric_name in self._LOWER_IS_BETTER else post_val - pre_val
        scale = max(abs(pre_val), abs(post_val), 1.0)
        return max(-1.0, min(1.0, delta / scale))

    def _is_cache_valid(self, pattern: str) -> bool:
        if pattern not in self._effectiveness_cache:
            return False
        expiry = self._cache_expiry.get(pattern)
        if expiry is None:
            return False
        return utc_now().replace(tzinfo=None) < expiry

    def _invalidate_cache(self, pattern: str):
        self._effectiveness_cache.pop(pattern, None)
        self._cache_expiry.pop(pattern, None)

    async def request_stick_validation(
        self,
        action: str,
        metric_pattern: str,
        db_getter=None,
    ):
        """
        Request The Stick to validate action effectiveness learning.

        Raises ValidationSystemFailure if The Stick is unreachable or rejects.
        Does NOT return False — unreachable and rejected are different failures,
        both of which must stop learning.
        """
        if not db_getter:
            self.logger.error(
                "👻💥 request_stick_validation() called with no db_getter — "
                "cannot validate. Learning STOPS."
            )
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure("No db_getter provided for Stick validation.")

        cutoff_date = utc_now().replace(tzinfo=None) - timedelta(days=60)
        result = await self.db.execute(
            select(ActionOutcomeRecord).where(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                    ActionOutcomeRecord.metric_pattern_fingerprint == metric_pattern,
                    ActionOutcomeRecord.created_at >= cutoff_date,
                )
            )
        )
        records = result.scalars().all()

        if not records:
            self.logger.error(
                f"👻💥 request_stick_validation(): no records found for action='{action}' "
                f"pattern='{metric_pattern[:32]}...' — cannot validate."
            )
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(
                f"No outcome records found for {action} / {metric_pattern} — validation impossible."
            )

        successful_attempts = sum(1 for r in records if r.success)
        raw_success_rate = successful_attempts / len(records)

        try:
            async for db in db_getter():
                from app.ai_agents.the_stick.ML.learning import StickLearning
                from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration

                stick_learning = StickLearning(db, "system")
                stick_db = StickDatabaseIntegration(db_getter)

                audit_entry = stick_learning.validate_action_effectiveness(
                    agent_name=self.agent_name,
                    action=action,
                    metric_pattern=metric_pattern,
                    effectiveness_score=raw_success_rate,
                    raw_success_rate=raw_success_rate,
                    sample_size=len(records),
                    previous_score=None,
                )

                if not audit_entry.validation_result:
                    audit_entry.stick_anxiety_level = 50.0

                await stick_db.record_validation(None, audit_entry)

                self.logger.info(
                    f"👻📊 Stick validation result: {audit_entry.validation_result} "
                    f"({action} / {metric_pattern[:32]}...)"
                )
                return audit_entry.validation_result

        except Exception as e:
            self.logger.error(f"👻💥 THE STICK VALIDATION FAILED: {e}", exc_info=True)
            self.logger.error("   Learning cannot proceed without validation. This is a critical failure.")
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(f"The Stick validation system failed: {e}") from e

    async def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about action effectiveness learning."""
        stats = {}

        for action in ALL_ACTIONS:
            result = await self.db.execute(
                select(ActionOutcomeRecord).where(
                    and_(
                        ActionOutcomeRecord.agent_name == self.agent_name,
                        ActionOutcomeRecord.action == action,
                    )
                )
            )
            records = result.scalars().all()

            if records:
                successful = sum(1 for r in records if r.success)
                success_rate = successful / len(records)
                improvements = [r.improvement for r in records if r.improvement is not None]
                avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

                stats[action] = {
                    'attempts': len(records),
                    'success_rate': success_rate,
                    'avg_improvement': avg_improvement,
                    'status': 'active' if len(records) >= 10 else 'learning',
                }

        return stats
