#!/usr/bin/env python3
"""
Hamsters' Action Effectiveness Model

Two learning layers:
1. Primitive-level: tracks which individual primitives (fstrim, e4defrag, rm_temp, etc.)
   work for which metric pattern fingerprints. Used by score_all_actions().
2. Sequence-level: tracks which ordered primitive sequences work for which goals.
   Used by get_effective_sequences(), queried by the ExecutionPlanner.

Collective learning across Steve, Bob, and Carl.
"""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learned_thresholds import ActionOutcomeRecord, LearnedSequence

logger = logging.getLogger('HamstersActionEffectiveness')

# Primitive vocabulary — atomic operations tracked at the per-primitive level.
# Must stay in sync with HamsterPrimitiveExecutor._register_primitives().
# Composite action names (cleanup, cleanup_with_defrag, etc.) are gone —
# the ExecutionPlanner composes sequences from these primitives at runtime.
STORAGE_ACTIONS = [
    'fstrim',
    'e4defrag',
    'logrotate',
    'gzip_logs',
    'rm_temp',
    'apt_clean',
    'tar_archive',
]

# Set for O(1) membership checks at record_outcome() entry point.
# Old rows in action_outcome_records with composite names (cleanup,
# defrag_only, etc.) are inert — score_all_actions() never queries
# for them by name, so they cannot contaminate scores. No data migration
# needed; they are simply orphaned and will age out of the 60-day window.
_PRIMITIVE_VOCABULARY: frozenset = frozenset(STORAGE_ACTIONS)


@dataclass
class ActionScore:
    """Effectiveness score for an action in a specific pattern"""
    action: str
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    sample_size: int
    success_rate: float
    avg_improvement: float


class ActionEffectivenessModel:
    """
    Hamsters' action effectiveness learning system.
    
    Learns which storage fix works best for which metric pattern.
    Collective learning (not per-hamster) unless hamster identity is already
    captured in execution data.
    """
    
    def __init__(self, db: AsyncSession, system_id: str = "default"):
        self.db = db
        self.system_id = system_id
        self.agent_name = "hamsters"
        self.logger = logger
    
    async def score_all_actions(
        self,
        metric_pattern: str
    ) -> List[ActionScore]:
        """
        Score all possible actions for a given metric pattern.
        
        Args:
            metric_pattern: Pattern fingerprint (e.g., 'disk_gradual_growth')
            
        Returns:
            List of ActionScore objects, sorted by score (best first)
        """
        scores = []
        
        for action in STORAGE_ACTIONS:
            score = await self._score_action(action, metric_pattern)
            scores.append(score)
        
        # Sort by score descending
        scores.sort(key=lambda s: s.score, reverse=True)
        
        return scores
    
    async def _score_action(
        self,
        action: str,
        metric_pattern: str
    ) -> ActionScore:
        """
        Calculate effectiveness score for an action in a pattern.
        
        Score combines:
        - Success rate (did it work?)
        - Average improvement (how much did it help?)
        - Recency (recent outcomes weighted more)
        """
        # Get outcome records from last 60 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)

        stmt = select(ActionOutcomeRecord).where(
            and_(
                ActionOutcomeRecord.agent_name == self.agent_name,
                ActionOutcomeRecord.action == action,
                ActionOutcomeRecord.metric_pattern_fingerprint == metric_pattern,
                ActionOutcomeRecord.created_at >= cutoff_date,
            )
        )
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        
        if not records:
            # No data - return neutral score
            return ActionScore(
                action=action,
                score=0.5,
                confidence=0.0,
                sample_size=0,
                success_rate=0.0,
                avg_improvement=0.0
            )
        
        # Calculate metrics
        sample_size = len(records)
        successful = sum(1 for r in records if r.success)
        success_rate = successful / sample_size
        
        # Calculate average improvement (positive = helped, negative = made things worse)
        improvements = [r.improvement for r in records if r.improvement is not None]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
        degradations = sum(1 for i in improvements if i < 0)
        if degradations > 0:
            self.logger.warning(
                f"🐹⚠️ Action '{action}' caused degradation in {degradations}/{len(improvements)} outcomes "
                f"for pattern '{metric_pattern}'"
            )
        
        # Calculate recency-weighted score
        now = datetime.now(timezone.utc)
        weighted_successes = 0.0
        total_weight = 0.0
        
        for record in records:
            # Weight decays with age (recent outcomes matter more)
            age_days = (now - record.created_at).days
            weight = max(0.1, 1.0 - (age_days / 60.0))  # Linear decay over 60 days
            
            total_weight += weight
            if record.success:
                weighted_successes += weight
        
        weighted_success_rate = weighted_successes / total_weight if total_weight > 0 else 0.0
        
        # Combine into final score
        # 60% weighted success rate + 40% improvement magnitude
        score = (0.6 * weighted_success_rate) + (0.4 * min(avg_improvement, 1.0))
        
        # Confidence based on sample size
        confidence = min(sample_size / 10.0, 1.0)  # Full confidence at 10+ samples
        
        return ActionScore(
            action=action,
            score=score,
            confidence=confidence,
            sample_size=sample_size,
            success_rate=success_rate,
            avg_improvement=avg_improvement
        )
    
    async def record_outcome(
        self,
        action: str,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
        severity: str,
        success: bool,
        metric_pattern: Optional[str] = None,
        outcome_notes: Optional[str] = None
    ):
        """
        Record outcome of an action for learning.

        Only accepts primitive vocabulary names. Rejects composite action names
        (cleanup, defrag_only, etc.) that predate the intelligent executor refactor.
        This is the single write chokepoint — contamination is prevented here,
        not filtered at read time.
        """
        if action not in _PRIMITIVE_VOCABULARY:
            self.logger.error(
                f"🐹💥 record_outcome() rejected unknown action '{action}'. "
                f"Must be one of: {sorted(_PRIMITIVE_VOCABULARY)}. "
                f"Old composite action names are not accepted. "
                f"Pass a primitive name from HamsterPrimitiveExecutor."
            )
            from app.ai_agents.exceptions import ActionSelectionFailure
            raise ActionSelectionFailure(
                f"record_outcome() called with non-primitive action '{action}'. "
                f"Valid primitives: {sorted(_PRIMITIVE_VOCABULARY)}"
            )

        # Generate pattern fingerprint if not provided
        if not metric_pattern:
            metric_pattern = self._generate_pattern_fingerprint(pre_metrics, severity)
        
        # Calculate improvement score
        improvement_score = self._calculate_improvement(pre_metrics, post_metrics)
        
        record = ActionOutcomeRecord(
            agent_name=self.agent_name,
            action=action,
            metric_pattern_fingerprint=metric_pattern,
            pre_metrics=pre_metrics,
            post_metrics=post_metrics,
            severity_score=float(1.0 if severity == 'critical' else 0.5),
            success=success,
            improvement=improvement_score,
            primary_metric='disk_usage_percent',
            other_actions_considered=[]
        )

        self.db.add(record)
        # Flush to assign ID without committing — caller owns the transaction boundary
        await self.db.flush()
        
        self.logger.info(
            f"🐹📊 Recorded action outcome: {action} for {metric_pattern} "
            f"(success={success}, improvement={improvement_score:.2f})"
        )
    
    def _generate_pattern_fingerprint(
        self,
        metrics: Dict[str, float],
        severity: str
    ) -> str:
        """
        Generate pattern fingerprint from metrics.

        Thresholds here are intentionally coarse bucket boundaries — they do NOT
        need to match learned_thresholds exactly. Their purpose is stable fingerprint
        grouping so that learning records for similar situations cluster together.
        Learned thresholds govern when to act; fingerprints govern what was learned.

        Examples:
        - 'disk_sudden_spike_critical'
        - 'disk_gradual_growth_warning'
        - 'fragmentation_high_warning'
        - 'inode_pressure_warning'
        """
        disk_usage = metrics.get('disk_usage_percent', 0.0)
        fragmentation = metrics.get('fragmentation_level', 0.0)
        inode_usage = metrics.get('inode_usage_percent', 0.0)

        # Inode exhaustion takes priority — it's a distinct failure mode
        if inode_usage > 90:
            pattern = 'inode_exhaustion'
        elif inode_usage > 75:
            pattern = 'inode_pressure'
        elif disk_usage > 95:
            pattern = 'disk_sudden_spike'
        elif disk_usage > 85:
            pattern = 'disk_gradual_growth'
        elif fragmentation > 30:
            pattern = 'fragmentation_high'
        elif fragmentation > 15:
            pattern = 'fragmentation_moderate'
        else:
            pattern = 'disk_normal'

        return f"{pattern}_{severity}"
    
    def _calculate_improvement(
        self,
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float]
    ) -> float:
        """
        Calculate improvement score.

        Positive = situation improved, negative = situation degraded.
        Range is roughly -1.0 to 1.0; clamped to [-1.0, 1.0].
        """
        # Primary metric: disk usage reduction
        pre_disk = pre_metrics.get('disk_usage_percent', 0.0)
        post_disk = post_metrics.get('disk_usage_percent', pre_disk)
        disk_delta = (pre_disk - post_disk) / 100.0  # positive = freed space

        # Secondary metric: fragmentation reduction
        pre_frag = pre_metrics.get('fragmentation_level', 0.0)
        post_frag = post_metrics.get('fragmentation_level', pre_frag)
        frag_delta = (pre_frag - post_frag) / 100.0  # positive = less fragmented

        # Tertiary metric: inode usage reduction
        pre_inode = pre_metrics.get('inode_usage_percent', 0.0)
        post_inode = post_metrics.get('inode_usage_percent', pre_inode)
        inode_delta = (pre_inode - post_inode) / 100.0  # positive = freed inodes

        # Weighted combination
        improvement = (0.6 * disk_delta) + (0.25 * frag_delta) + (0.15 * inode_delta)

        return max(-1.0, min(improvement, 1.0))
    
    async def request_stick_validation(
        self,
        action: str,
        metric_pattern: str,
        db_getter=None
    ) -> bool:
        """
        Request The Stick to validate action effectiveness learning.
        
        Args:
            action: Action being validated
            metric_pattern: Pattern fingerprint
            db_getter: Database session getter (for The Stick's session)
            
        Returns:
            True if validation passed, False otherwise
        """
        if not db_getter:
            self.logger.error(
                "🐹💥 No db_getter provided for Stick validation — "
                "cannot validate action effectiveness without audit trail"
            )
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(
                "db_getter is required for Stick validation. "
                "Pass a db_getter to request_stick_validation()."
            )
        
        try:
            # Get outcome records for this action/pattern
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
            stmt = select(ActionOutcomeRecord).where(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                    ActionOutcomeRecord.metric_pattern_fingerprint == metric_pattern,
                    ActionOutcomeRecord.created_at >= cutoff_date,
                )
            )
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            
            if not records:
                self.logger.warning(f"No records found for {action} with pattern {metric_pattern}")
                return False
            
            # Calculate statistics
            successful_attempts = sum(1 for r in records if r.success)
            raw_success_rate = successful_attempts / len(records) if records else 0.0
            
            # Get the learned effectiveness score from the action effectiveness model
            action_scores = await self.score_all_actions(metric_pattern)
            effectiveness_score = next((s.score for s in action_scores if s.action == action), raw_success_rate)
            
            # Get previous score for volatility check (if available)
            # TODO: Implement historical score tracking
            previous_score = None
            
            # Call The Stick's validation
            # CRITICAL: Use db_getter to get The Stick's session, don't nest sessions
            async for db in db_getter():
                from app.ai_agents.the_stick.ML.learning import StickLearning
                from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration

                if not hasattr(self, '_stick_learning') or self._stick_learning is None:
                    self._stick_learning = StickLearning(db, "system")
                stick_learning = self._stick_learning
                stick_db = StickDatabaseIntegration(db_getter)

                # Validate - returns standard ValidationAuditEntry
                audit_entry = stick_learning.validate_action_effectiveness(
                    agent_name=self.agent_name,
                    action=action,
                    metric_pattern=metric_pattern,
                    effectiveness_score=effectiveness_score,
                    raw_success_rate=raw_success_rate,
                    sample_size=len(records),
                    previous_score=previous_score
                )

                # Record audit trail using standard record_validation()
                # Note: This is a mock interaction for validation purposes
                # The interaction_id in audit_entry already contains the necessary info
                await stick_db.record_validation(None, audit_entry)

                self.logger.info(
                    f"🐹📊 Action validation result: {audit_entry.validation_result} "
                    f"({action} in pattern {metric_pattern[:16]}...)"
                )

                return audit_entry.validation_result
                
        except Exception as e:
            self.logger.error(f"🐹💥 THE STICK VALIDATION FAILED: {e}", exc_info=True)
            self.logger.error("   Learning cannot proceed without validation. This is a critical failure.")
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(f"The Stick validation system failed: {e}") from e
    
    async def get_effective_sequences(
        self,
        goal: str,
        min_confidence: float = 0.3,
        min_samples: int = 3,
    ) -> List[LearnedSequence]:
        """
        Query the LearnedSequence table for effective sequences for a given goal.

        Called by the ExecutionPlanner to find learned sequences before
        falling back to cold start hypotheses.

        Filters:
        - Matches goal
        - Not deprecated
        - Meets minimum confidence and sample size thresholds

        Returns sequences sorted by effectiveness_score descending.
        The planner applies its own ranking (severity proximity bonus) on top.
        """
        try:
            stmt = select(LearnedSequence).where(
                and_(
                    LearnedSequence.agent_name == self.agent_name,
                    LearnedSequence.goal == goal,
                    LearnedSequence.deprecated == False,
                    LearnedSequence.confidence >= min_confidence,
                    LearnedSequence.sample_size >= min_samples,
                )
            ).order_by(LearnedSequence.effectiveness_score.desc())

            result = await self.db.execute(stmt)
            sequences = result.scalars().all()

            self.logger.debug(
                f"🐹🔍 get_effective_sequences(goal='{goal}'): "
                f"found {len(sequences)} qualifying sequences "
                f"(min_confidence={min_confidence}, min_samples={min_samples})"
            )
            return list(sequences)

        except Exception as e:
            self.logger.error(
                f"🐹💥 get_effective_sequences failed for goal '{goal}': {e}",
                exc_info=True
            )
            raise

    async def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about action effectiveness learning"""
        stats = {}

        for action in STORAGE_ACTIONS:
            stmt = select(ActionOutcomeRecord).where(
                and_(
                    ActionOutcomeRecord.agent_name == self.agent_name,
                    ActionOutcomeRecord.action == action,
                )
            )
            result = await self.db.execute(stmt)
            records = result.scalars().all()

            if records:
                successful = sum(1 for r in records if r.success)
                success_rate = successful / len(records)
                improvements = [r.improvement for r in records if r.improvement is not None]
                avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
                degradations = sum(1 for i in improvements if i < 0)

                stats[action] = {
                    'attempts': len(records),
                    'success_rate': success_rate,
                    'avg_improvement': avg_improvement,
                    'degradation_count': degradations,
                    'status': 'active' if len(records) >= 10 else 'learning',
                }

        return stats
