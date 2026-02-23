#!/usr/bin/env python3
"""
QSP's Learned Thresholds System

Adaptive threshold learning for security threat detection.
Learns from false positives and false negatives to adjust thresholds over time.
FALSE NEGATIVES (missed threats) are treated with higher urgency than false positives.

Cold-start values imported from heuristic_config.py.
Adjustment config imported from heuristic_config.py.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.threshold_learning import ThresholdLearningRecord
from .heuristic_config import DEFAULT_THRESHOLDS, THRESHOLD_ADJUSTMENT_CONFIG

logger = logging.getLogger('QSPLearnedThresholds')

UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)


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
    QSP's learned threshold system.

    Learns when to escalate security threats based on observed outcomes.
    Tracks false positives (escalated non-threats) and false negatives (missed threats)
    separately due to asymmetric costs in security domain.

    FALSE NEGATIVES weighted more heavily: missed threats are catastrophic.
    Adjustment rates from THRESHOLD_ADJUSTMENT_CONFIG (asymmetric by design).
    """

    def __init__(self, db: AsyncSession, system_id: str = "default"):
        self.db = db
        self.system_id = system_id
        self.agent_name = "quantum_shadow_people"
        self.logger = logger
        
    async def get_threshold(
        self,
        metric_name: str,
        level: str = 'warning',
    ) -> float:
        """
        Get learned threshold for a metric.

        Args:
            metric_name: e.g. 'failed_auth_attempts', 'network_anomalies'
            level: 'warning' or 'critical'

        Returns:
            Learned threshold value (or cold-start default if not enough data)
        """
        assessment = await self._get_threshold_assessment(metric_name)
        if level == 'warning':
            return assessment.warning_threshold
        elif level == 'critical':
            return assessment.critical_threshold
        defaults = DEFAULT_THRESHOLDS.get(metric_name, {})
        return float(defaults.get(level, 0.5))

    async def assess_severity(
        self,
        current_metrics: Dict[str, float],
        primary_metric: str,
    ) -> Dict[str, Any]:
        """
        Compute a continuous severity score 0.0-1.0 for the given metrics.

        Used by action_selection._get_severity_score() as the primary severity signal.

        Returns dict with:
            severity_score: float 0.0-1.0
            primary_metric: str
            threshold_levels: dict of metric → level hit ('ok'/'warning'/'critical')
        """
        threshold_levels: Dict[str, str] = {}
        scores = []

        for metric_name, value in current_metrics.items():
            metric_defaults = DEFAULT_THRESHOLDS.get(metric_name)

            if metric_defaults is not None:
                warning  = await self.get_threshold(metric_name, 'warning')
                critical = await self.get_threshold(metric_name, 'critical')

                if value >= critical:
                    threshold_levels[metric_name] = 'critical'
                    normalised = min(1.0, value / max(critical, 1.0))
                elif value >= warning:
                    threshold_levels[metric_name] = 'warning'
                    normalised = min(1.0, value / max(critical, 1.0))
                else:
                    threshold_levels[metric_name] = 'ok'
                    normalised = 0.0

                scores.append(normalised)
            else:
                # Unknown metric — include at half weight, log for awareness
                if value > 0:
                    threshold_levels[metric_name] = 'unknown'
                    normalised = min(1.0, value / 1000.0)  # Conservative normalization
                    scores.append(normalised * 0.5)  # Half weight for unknown metrics
                    self.logger.debug(
                        f"👻📏 Unknown metric '{metric_name}' with value {value:.1f} — "
                        f"included at half weight (no learned thresholds yet)"
                    )

        severity_score = sum(scores) / len(scores) if scores else 0.0

        return {
            'severity_score':    severity_score,
            'primary_metric':    primary_metric,
            'threshold_levels':  threshold_levels,
        }
    
    async def _get_threshold_assessment(
        self,
        metric_name: str,
    ) -> ThresholdAssessment:
        """
        Assess learned thresholds for a metric.

        Returns ThresholdAssessment with learned values or cold-start defaults.
        """
        cutoff_date = utc_now().replace(tzinfo=None) - timedelta(days=30)

        result = await self.db.execute(
            select(ThresholdLearningRecord).where(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.agent_name == self.agent_name,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date,
                )
            )
        )
        records = result.scalars().all()

        if len(records) < 5:
            default = DEFAULT_THRESHOLDS.get(metric_name, {})
            return ThresholdAssessment(
                metric_name=metric_name,
                warning_threshold=float(default.get('warning', 5)),
                critical_threshold=float(default.get('critical', 15)),
                warning_confidence=0.0,
                critical_confidence=0.0,
                sample_size=0,
                last_adjustment=None,
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
        level: str,
    ) -> Tuple[float, float]:
        """
        Calculate learned threshold from records.

        Asymmetric adjustment rates from THRESHOLD_ADJUSTMENT_CONFIG:
        - false_negative_adjustment > false_alarm_adjustment (missed threats are catastrophic)
        - false_alarm_adjustment raises threshold (less sensitive)
        - false_negative_adjustment lowers threshold (more sensitive)

        Returns:
            (threshold_value, confidence)
        """
        level_records = [r for r in records if r.threshold_level == level]

        if not level_records:
            metric_name = records[0].metric_name if records else 'failed_auth_attempts'
            default = DEFAULT_THRESHOLDS.get(metric_name, {})
            return float(default.get(level, 5)), 0.0

        false_positives = sum(1 for r in level_records if r.was_false_alarm)
        false_negatives = sum(1 for r in level_records if r.should_have_acted_sooner)
        successful      = sum(1 for r in level_records if r.was_successful)

        baseline = float(level_records[-1].threshold_value)
        total_outcomes = len(level_records)

        false_positive_rate = false_positives / total_outcomes
        false_negative_rate = false_negatives / total_outcomes
        success_rate        = successful / total_outcomes

        cfg = THRESHOLD_ADJUSTMENT_CONFIG
        fp_adj     = cfg['false_positive_adjustment']       # 0.05 — already a ratio
        fn_adj     = cfg['false_negative_adjustment']       # 0.10 — already a ratio
        fp_trigger = cfg['false_positive_trigger_rate']     # 0.3
        fn_trigger = cfg['false_negative_trigger_rate']     # 0.2

        if false_negative_rate > fn_trigger:
            # Missed threats: lower threshold aggressively (asymmetric)
            new_threshold = max(
                cfg['min_threshold_floor'],
                baseline - (baseline * fn_adj)
            )
        elif false_positive_rate > fp_trigger:
            # Too many false alarms: raise threshold
            new_threshold = baseline + (baseline * fp_adj)
        else:
            new_threshold = baseline

        # Confidence: false negatives penalise more than false positives
        confidence_penalty = (false_negative_rate * 0.5) + (false_positive_rate * 0.2)
        confidence = min((success_rate - confidence_penalty) * (total_outcomes / 20.0), 1.0)
        confidence = max(confidence, 0.0)

        return new_threshold, confidence
    
    async def record_outcome(
        self,
        metric_name: str,
        metric_value: float,
        threshold_level: str,
        was_successful: bool,
        was_false_positive: bool = False,
        was_false_negative: bool = False,
        outcome_notes: Optional[str] = None
    ):
        """
        Record outcome of a threshold-based security response.
        
        CRITICAL: was_false_positive and was_false_negative are tracked separately.
        False negatives (missed threats) are treated with higher urgency.
        
        Args:
            metric_name: 'failed_auth_attempts', 'network_anomalies', 'threat_severity'
            metric_value: Actual metric value at response time
            threshold_level: 'warning' or 'critical'
            was_successful: Did the response work?
            was_false_positive: Was this a non-threat that was escalated?
            was_false_negative: Was this a real threat that was missed?
            outcome_notes: Optional notes about the outcome
        """
        current_threshold = await self.get_threshold(metric_name, threshold_level)
        
        # Map to database schema fields
        # was_false_alarm = false_positive
        # should_have_acted_sooner = false_negative
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
            was_false_alarm=was_false_positive,
            should_have_acted_sooner=was_false_negative
        )
        
        self.db.add(record)
        await self.db.commit()
        
        if was_false_negative:
            self.logger.error(
                f"👻🚨 FALSE NEGATIVE recorded: {metric_name}.{threshold_level} "
                f"(value={metric_value:.1f}, threshold={current_threshold:.1f}) - MISSED THREAT"
            )
        elif was_false_positive:
            self.logger.info(
                f"👻� False positive recorded: {metric_name}.{threshold_level} "
                f"(value={metric_value:.1f}, threshold={current_threshold:.1f})"
            )
        else:
            self.logger.info(
                f"👻� Threshold learning recorded: {metric_name}.{threshold_level} "
                f"(value={metric_value:.1f}, threshold={current_threshold:.1f}, success={was_successful})"
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
                "👻💥 request_stick_validation() called with no db_getter — "
                "cannot validate. Learning STOPS."
            )
            from app.ai_agents.exceptions import ValidationSystemFailure
            raise ValidationSystemFailure("No db_getter provided for Stick validation.")

        cutoff_date = utc_now().replace(tzinfo=None) - timedelta(days=30)
        result = await self.db.execute(
            select(ThresholdLearningRecord).where(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.agent_name == self.agent_name,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date,
                )
            )
        )
        records = result.scalars().all()

        try:
            
            # Determine trigger reason from learning records
            # SEPARATE false positives and false negatives
            false_positive_count = sum(1 for r in records if r.was_false_alarm)
            false_negative_count = sum(1 for r in records if r.should_have_acted_sooner)
            
            # Determine primary trigger reason
            trigger_reason = None
            if false_positive_count > false_negative_count:
                trigger_reason = "false_positive"
            elif false_negative_count > 0:
                trigger_reason = "false_negative"  # Takes priority even with fewer occurrences
            
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
                
                # PRIORITY BOOST for security validations
                # QSP validations: priority 9 (pass) or 10 (fail)
                # False negatives: always priority 10
                if trigger_reason == "false_negative":
                    audit_entry.stick_anxiety_level = 100.0  # Maximum anxiety for missed threats
                
                # Record audit trail using standard record_validation()
                # Note: This is a mock interaction for validation purposes
                # The interaction_id in audit_entry already contains the necessary info
                await stick_db.record_validation(None, audit_entry)
                
                if trigger_reason == "false_negative":
                    self.logger.error(
                        f"👻🚨 FALSE NEGATIVE validation result: {audit_entry.validation_result} "
                        f"({metric_name}.{threshold_level}) - PRIORITY 10"
                    )
                else:
                    self.logger.info(
                        f"👻� Threshold validation result: {audit_entry.validation_result} "
                        f"({metric_name}.{threshold_level})"
                    )

                return audit_entry.validation_result

        except Exception as e:
            self.logger.error(f"👻💥 THE STICK VALIDATION FAILED: {e}", exc_info=True)
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
        """Get summary of threshold learning across all metrics."""
        summary = {}
        for metric_name in DEFAULT_THRESHOLDS:
            assessment = await self._get_threshold_assessment(metric_name)
            summary[metric_name] = {
                'warning':  {'threshold': assessment.warning_threshold,  'confidence': assessment.warning_confidence},
                'critical': {'threshold': assessment.critical_threshold, 'confidence': assessment.critical_confidence},
                'sample_size':     assessment.sample_size,
                'last_adjustment': assessment.last_adjustment.isoformat() if assessment.last_adjustment else None,
            }
        return summary
