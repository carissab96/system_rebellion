#!/usr/bin/env python3
"""
Hamsters' Learned Thresholds System

Adaptive threshold learning for storage management:
- Disk usage thresholds (warning, critical)
- Fragmentation thresholds (when to defrag)
- Inode usage thresholds (when inodes matter)

Learns from false alarms and missed actions to adjust thresholds over time.
Collective thresholds across Steve, Bob, and Carl (not per-hamster).
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threshold_learning import ThresholdLearningRecord

logger = logging.getLogger('HamstersLearnedThresholds')

# Threshold learning configuration.
# Extracted from _calculate_threshold_level() so they can be tuned without
# touching the algorithm. Asymmetric by design: missing a critical event
# (too_late) is worse than a false alarm, so too_late_adjustment is more
# aggressive than false_alarm_adjustment.
THRESHOLD_LEARNING_CONFIG = {
    'false_alarm_trigger': 0.3,       # False alarm rate that triggers upward adjustment
    'too_late_trigger': 0.2,          # Too-late rate that triggers downward adjustment
    'false_alarm_adjustment': 0.03,   # 3% increase per evaluation (less aggressive)
    'too_late_adjustment': 0.07,      # 7% decrease per evaluation (more aggressive)
    'threshold_ceiling': 95.0,        # Never raise threshold above 95%
    'threshold_floor': 50.0,          # Never lower threshold below 50%
    'min_samples_for_learning': 5,    # Minimum records before learning kicks in
    'learning_window_days': 30,       # How far back to look
    'confidence_normalization': 20.0, # Sample size for full confidence
}

# Storage-specific defaults (industry standard starting points)
DEFAULT_THRESHOLDS = {
    'disk_usage': {
        'warning': 80.0,   # %
        'critical': 90.0   # %
    },
    'fragmentation': {
        'warning': 20.0,   # %
        'critical': 40.0   # %
    },
    'inode_usage': {
        'warning': 80.0,   # %
        'critical': 90.0   # %
    }
}


@dataclass
class ThresholdAssessment:
    """Assessment of learned thresholds for a metric"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    warning_confidence: float
    critical_confidence: float
    sample_size: int
    last_adjustment: Optional[datetime]


class LearnedThresholds:
    """
    Hamsters' learned threshold system.
    
    Learns when to trigger storage interventions based on observed outcomes.
    Collective thresholds (not per-hamster) - Steve, Bob, and Carl share the same
    learned boundaries for when disk usage/fragmentation becomes a problem.
    """
    
    def __init__(self, db: AsyncSession, system_id: str = "default"):
        self.db = db
        self.system_id = system_id
        self.agent_name = "hamsters"
        self.logger = logger
        
    async def get_threshold(
        self,
        metric_name: str,
        level: str = 'warning'
    ) -> float:
        """
        Get learned threshold for a metric.
        
        Args:
            metric_name: 'disk_usage', 'fragmentation', 'inode_usage'
            level: 'warning' or 'critical'
            
        Returns:
            Learned threshold value (or default if not enough data)
        """
        assessment = await self._get_threshold_assessment(metric_name)
        
        if level == 'warning':
            return assessment.warning_threshold
        elif level == 'critical':
            return assessment.critical_threshold
        else:
            raise ValueError(f"Unknown threshold level: {level}")
    
    async def _get_threshold_assessment(
        self,
        metric_name: str
    ) -> ThresholdAssessment:
        """
        Assess learned thresholds for a metric.
        
        Returns ThresholdAssessment with learned values or defaults.
        """
        # Get learning records from last 30 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)

        stmt = select(ThresholdLearningRecord).where(
            and_(
                ThresholdLearningRecord.system_id == self.system_id,
                ThresholdLearningRecord.agent_name == self.agent_name,
                ThresholdLearningRecord.metric_name == metric_name,
                ThresholdLearningRecord.created_at >= cutoff_date
            )
        )
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        
        if not records or len(records) < 5:
            # Not enough data - use defaults
            default = DEFAULT_THRESHOLDS.get(metric_name, {})
            return ThresholdAssessment(
                metric_name=metric_name,
                warning_threshold=default.get('warning', 80.0),
                critical_threshold=default.get('critical', 90.0),
                warning_confidence=0.0,
                critical_confidence=0.0,
                sample_size=0,
                last_adjustment=None
            )
        
        # Analyze records to determine learned thresholds
        warning_threshold, warning_confidence = self._calculate_threshold_level(
            records, 'warning'
        )
        critical_threshold, critical_confidence = self._calculate_threshold_level(
            records, 'critical'
        )
        
        last_adjustment = max(r.created_at for r in records)
        
        return ThresholdAssessment(
            metric_name=metric_name,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            warning_confidence=warning_confidence,
            critical_confidence=critical_confidence,
            sample_size=len(records),
            last_adjustment=last_adjustment
        )
    
    def _calculate_threshold_level(
        self,
        records: list,
        level: str
    ) -> Tuple[float, float]:
        """
        Calculate learned threshold from records.

        Both false-alarm and too-late signals fire independently and contribute
        a net adjustment. They are NOT mutually exclusive — a system can have
        both signals simultaneously (oscillating around the threshold). The
        asymmetric weighting means too-late wins in a tie: missing a critical
        event is worse than a false alarm.

        Baseline is always the industry-standard default, not a field from the
        record (ThresholdLearningRecord has no threshold_value column).

        Returns:
            (threshold_value, confidence)
        """
        config = THRESHOLD_LEARNING_CONFIG
        level_records = [r for r in records if r.threshold_level == level]

        if not level_records:
            metric_name = records[0].metric_name if records else 'disk_usage'
            default = DEFAULT_THRESHOLDS.get(metric_name, {})
            return default.get(level, 80.0), 0.0

        # Count outcomes
        false_alarms = sum(1 for r in level_records if r.was_false_alarm)
        acted_too_late = sum(1 for r in level_records if r.should_have_acted_sooner)
        successful = sum(1 for r in level_records if r.outcome_success)
        total = len(level_records)

        false_alarm_rate = false_alarms / total
        too_late_rate = acted_too_late / total
        success_rate = successful / total

        # Baseline from industry-standard defaults.
        # ThresholdLearningRecord stores metric_value (the reading at intervention
        # time), not threshold_value. The default IS the baseline — learning
        # adjusts from it, and the adjustment accumulates across evaluations
        # through the records themselves.
        metric_name = level_records[0].metric_name
        default = DEFAULT_THRESHOLDS.get(metric_name, {})
        baseline = default.get(level, 80.0)

        # Net adjustment — both signals contribute independently.
        adjustment = 0.0

        if false_alarm_rate > config['false_alarm_trigger']:
            # Too sensitive — raise threshold (less aggressive)
            adjustment += baseline * config['false_alarm_adjustment']

        if too_late_rate > config['too_late_trigger']:
            # Not sensitive enough — lower threshold (more aggressive)
            adjustment -= baseline * config['too_late_adjustment']

        # Apply net adjustment and enforce boundaries
        new_threshold = baseline + adjustment
        new_threshold = max(
            config['threshold_floor'],
            min(new_threshold, config['threshold_ceiling'])
        )

        # Confidence based on sample size and success rate
        confidence = min(
            success_rate * (total / config['confidence_normalization']),
            1.0
        )

        return new_threshold, confidence
    
    async def record_outcome(
        self,
        metric_name: str,
        metric_value: float,
        threshold_level: str,
        was_successful: bool,
        was_false_alarm: bool = False,
        should_have_acted_sooner: bool = False,
        outcome_notes: Optional[str] = None
    ):
        """
        Record outcome of a threshold-based intervention.
        
        Args:
            metric_name: 'disk_usage', 'fragmentation', 'inode_usage'
            metric_value: Actual metric value at intervention time
            threshold_level: 'warning' or 'critical'
            was_successful: Did the intervention work?
            was_false_alarm: Was the intervention unnecessary?
            should_have_acted_sooner: Should we have acted at a lower threshold?
            outcome_notes: Optional notes about the outcome
        """
        current_threshold = await self.get_threshold(metric_name, threshold_level)
        
        record = ThresholdLearningRecord(
            system_id=self.system_id,
            agent_name=self.agent_name,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_level=threshold_level,
            action_taken=None,  # Not tracking specific action here
            outcome_success=was_successful,
            system_state={},  # Could add other metrics here
            context={},  # Could add time of day, etc.
            was_false_alarm=was_false_alarm,
            should_have_acted_sooner=should_have_acted_sooner
        )
        
        self.db.add(record)
        # Flush to assign ID without committing — caller owns the transaction boundary
        await self.db.flush()

        self.logger.info(
            f"🐹📏 Recorded threshold learning: {metric_name}.{threshold_level} "
            f"(value={metric_value:.1f}, threshold={current_threshold:.1f}, "
            f"success={was_successful}, false_alarm={was_false_alarm})"
        )
    
    async def request_stick_validation(
        self,
        metric_name: str,
        threshold_level: str,
        learned_value: float,
        default_value: float,
        db_getter=None
    ) -> bool:
        """
        Request The Stick to validate a learned threshold.
        
        Args:
            metric_name: Metric being thresholded
            threshold_level: 'warning' or 'critical'
            learned_value: The learned threshold value
            default_value: The default threshold value
            db_getter: Database session getter (for The Stick's session)
            
        Returns:
            True if validation passed, False otherwise
        """
        if not db_getter:
            self.logger.error(
                "🐹💥 No db_getter provided for Stick validation — "
                "validation system cannot function without database access"
            )
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(
                "Stick validation requires db_getter — cannot silently skip validation"
            )
        
        try:
            # Get learning metadata
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            stmt = select(ThresholdLearningRecord).where(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.agent_name == self.agent_name,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date
                )
            )
            result = await self.db.execute(stmt)
            records = result.scalars().all()
            
            # Determine trigger reason from learning records
            false_alarm_count = sum(1 for r in records if r.was_false_alarm)
            acted_too_late_count = sum(1 for r in records if r.should_have_acted_sooner)
            
            # Determine primary trigger reason
            trigger_reason = None
            if false_alarm_count > acted_too_late_count:
                trigger_reason = "false_alarms"
            elif acted_too_late_count > 0:
                trigger_reason = "too_late"
            
            # Call The Stick's validation
            # CRITICAL: Use db_getter to get The Stick's session, don't nest sessions
            async for db in db_getter():
                from app.ai_agents.the_stick.ML.learning import StickLearning
                from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration
                
                stick_learning = StickLearning(db, "system")
                stick_db = StickDatabaseIntegration(db_getter)
                
                # Validate - returns standard ValidationAuditEntry
                audit_entry = stick_learning.validate_learned_threshold(
                    agent_name=self.agent_name,
                    metric_name=metric_name,
                    threshold_level=threshold_level,
                    learned_value=learned_value,
                    default_value=default_value,
                    sample_size=len(records),
                    trigger_reason=trigger_reason
                )
                
                # Record audit trail using standard record_validation()
                # Note: This is a mock interaction for validation purposes
                # The interaction_id in audit_entry already contains the necessary info
                await stick_db.record_validation(None, audit_entry)
                
                self.logger.info(
                    f"🐹📏 Threshold validation result: {audit_entry.validation_result} "
                    f"({metric_name}.{threshold_level})"
                )
                
                return audit_entry.validation_result
                
        except Exception as e:
            self.logger.error(f"🐹💥 THE STICK VALIDATION FAILED: {e}", exc_info=True)
            self.logger.error("   Learning cannot proceed without validation. This is a critical failure.")
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure(f"The Stick validation system failed: {e}") from e
    
    async def get_threshold_confidence(
        self,
        metric_name: str,
        level: str = 'warning'
    ) -> float:
        """Get confidence score for a learned threshold (0.0-1.0)"""
        assessment = await self._get_threshold_assessment(metric_name)
        return getattr(assessment, f"{level}_confidence")
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of threshold learning across all metrics"""
        summary = {}
        
        for metric_name in ['disk_usage', 'fragmentation', 'inode_usage']:
            assessment = await self._get_threshold_assessment(metric_name)
            summary[metric_name] = {
                'warning': {
                    'threshold': assessment.warning_threshold,
                    'confidence': assessment.warning_confidence
                },
                'critical': {
                    'threshold': assessment.critical_threshold,
                    'confidence': assessment.critical_confidence
                },
                'sample_size': assessment.sample_size,
                'last_adjustment': assessment.last_adjustment.isoformat() if assessment.last_adjustment else None
            }
        
        return summary

    async def is_below_threshold(
        self,
        metric_name: str,
        current_value: float,
        level: str = 'warning'
    ) -> bool:
        """
        Check if a metric value is below the learned threshold.

        Used by ExecutionPlanner for mid-sequence goal satisfaction checks.
        "Is disk usage now below the warning threshold?" → goal achieved.
        """
        threshold = await self.get_threshold(metric_name, level)
        return current_value < threshold

    async def get_goal_thresholds(
        self,
        goal: str
    ) -> Dict[str, Any]:
        """
        Get relevant thresholds for a goal.

        Maps goal vocabulary to metric thresholds so the planner
        doesn't need to know the internal metric-to-goal mapping.
        One translation point between goal space and metric space.

        Returns:
            {'metric_name': str, 'level': str, 'threshold': float}

        Raises:
            ValueError: If goal is not in the known goal vocabulary.
        """
        GOAL_TO_METRIC: Dict[str, Tuple[str, str]] = {
            'disk_full':              ('disk_usage',    'critical'),
            'disk_high':              ('disk_usage',    'warning'),
            'fragmentation_critical': ('fragmentation', 'critical'),
            'fragmentation_high':     ('fragmentation', 'warning'),
            'inode_exhaustion':       ('inode_usage',   'critical'),
            'inode_high':             ('inode_usage',   'warning'),
            'log_overflow':           ('disk_usage',    'warning'),
            'slow_disk_io':           ('fragmentation', 'warning'),
            'ssd_needs_trim':         ('fragmentation', 'warning'),
            'disk_full_and_fragmented': ('disk_usage',  'critical'),
            'preventive_maintenance': ('disk_usage',    'warning'),
            'unknown_storage_issue':  ('disk_usage',    'warning'),
        }

        mapping = GOAL_TO_METRIC.get(goal)
        if mapping is None:
            raise ValueError(
                f"Unknown goal '{goal}' — not in GOAL_TO_METRIC. "
                f"Valid goals: {sorted(GOAL_TO_METRIC.keys())}"
            )

        metric_name, level = mapping
        threshold = await self.get_threshold(metric_name, level)

        return {
            'metric_name': metric_name,
            'level': level,
            'threshold': threshold,
        }
