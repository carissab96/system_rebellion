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
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threshold_learning import ThresholdLearningRecord

logger = logging.getLogger('HamstersLearnedThresholds')

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
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        records = await self.db.execute(
            self.db.query(ThresholdLearningRecord).filter(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.agent_name == self.agent_name,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date
                )
            )
        )
        records = records.scalars().all()
        
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
        
        Logic:
        - False alarms (triggered unnecessarily) → raise threshold (less sensitive)
        - Missed actions (should have acted sooner) → lower threshold (more sensitive)
        - Successful interventions → reinforce current threshold
        
        Returns:
            (threshold_value, confidence)
        """
        level_records = [r for r in records if r.threshold_level == level]
        
        if not level_records:
            # No data for this level - use default
            metric_name = records[0].metric_name if records else 'disk_usage'
            default = DEFAULT_THRESHOLDS.get(metric_name, {})
            return default.get(level, 80.0), 0.0
        
        # Count outcomes
        false_alarms = sum(1 for r in level_records if r.was_false_alarm)
        acted_too_late = sum(1 for r in level_records if r.should_have_acted_sooner)
        successful = sum(1 for r in level_records if r.was_successful)
        
        # Get baseline (most recent default or learned value)
        baseline = level_records[-1].threshold_value
        
        # Adjustment logic
        total_outcomes = len(level_records)
        false_alarm_rate = false_alarms / total_outcomes
        too_late_rate = acted_too_late / total_outcomes
        success_rate = successful / total_outcomes
        
        # If too many false alarms, raise threshold (less sensitive)
        if false_alarm_rate > 0.3:
            adjustment = baseline * 0.05  # 5% increase
            new_threshold = min(baseline + adjustment, 95.0)  # Cap at 95%
        # If acting too late, lower threshold (more sensitive)
        elif too_late_rate > 0.2:
            adjustment = baseline * 0.05  # 5% decrease
            new_threshold = max(baseline - adjustment, 50.0)  # Floor at 50%
        # Otherwise maintain current threshold
        else:
            new_threshold = baseline
        
        # Confidence based on sample size and success rate
        confidence = min(success_rate * (total_outcomes / 20.0), 1.0)
        
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
            threshold_level=threshold_level,
            threshold_value=current_threshold,
            metric_value_at_trigger=metric_value,
            was_successful=was_successful,
            was_false_alarm=was_false_alarm,
            should_have_acted_sooner=should_have_acted_sooner,
            outcome_notes=outcome_notes,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(record)
        await self.db.commit()
        
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
            self.logger.warning("🐹⚠️ No db_getter provided for validation")
            return True  # Skip validation if no db_getter
        
        try:
            # Get learning metadata
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            records = await self.db.execute(
                self.db.query(ThresholdLearningRecord).filter(
                    and_(
                        ThresholdLearningRecord.system_id == self.system_id,
                        ThresholdLearningRecord.agent_name == self.agent_name,
                        ThresholdLearningRecord.metric_name == metric_name,
                        ThresholdLearningRecord.created_at >= cutoff_date
                    )
                )
            )
            records = records.scalars().all()
            
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
                
                # Get user_id from first record or use system default
                user_id = records[0].user_id if records else "system"
                
                stick_learning = StickLearning(db, user_id)
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
            self.logger.error(f"🐹💥 Validation request failed: {e}")
            return True  # Don't block on validation failure
    
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
