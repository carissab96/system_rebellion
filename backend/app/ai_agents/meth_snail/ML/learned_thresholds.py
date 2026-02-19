#!/usr/bin/env python3
"""
Learned Thresholds System

System-specific thresholds that adapt based on outcomes.
No hardcoded "85% is critical" - instead learns what's critical for THIS system.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import statistics
from sqlalchemy import and_, or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learned_thresholds import ThresholdLearningRecord


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Module-level config — single source of truth for all threshold learning rates
THRESHOLD_LEARNING_CONFIG = {
    'false_alarm_adjustment': 3.0,    # Raise threshold by this when false alarm detected
    'too_late_adjustment': 5.0,       # Lower threshold by this when acted too late (asymmetric: late is worse)
    'success_blend_weight': 0.4,      # Weight of successful intervention value in blend
    'min_threshold': 10.0,
    'max_threshold': 99.0,
    'contextual_cap': 5.0,            # Max contextual adjustment ±
    'contextual_conservative': 0.3,   # Fraction of delta to apply as adjustment
    'monitor_offset': -10.0,          # Monitor threshold = warning + this offset
}

# Module-level default thresholds — extracted from instance to prevent drift
DEFAULT_THRESHOLDS = {
    'memory_usage': {
        'monitor': 70.0,
        'warning': 80.0,
        'critical': 90.0,
        'emergency': 95.0
    },
    'cpu_usage': {
        'monitor': 60.0,
        'warning': 75.0,
        'critical': 85.0,
        'emergency': 95.0
    },
    'swap_usage': {
        'monitor': 20.0,
        'warning': 40.0,
        'critical': 60.0,
        'emergency': 80.0
    },
    'disk_usage': {
        'monitor': 70.0,
        'warning': 80.0,
        'critical': 90.0,
        'emergency': 95.0
    }
}

# Goal → metric mapping for ExecutionPlanner integration.
# Must contain ALL entries from TERRY_GOALS in execution_planner.py.
# GOAL_TO_METRIC_KEY in execution_planner.py is the authoritative Terry-specific mapping.
# get_goal_thresholds() is now DEPRECATED — _goal_satisfied() calls get_threshold() directly
# using GOAL_TO_METRIC_KEY. This map is retained for agent-agnostic callers only.
GOAL_METRIC_MAP = {
    # Terry's full goal vocabulary (matches TERRY_GOALS + GOAL_TO_METRIC_KEY)
    'memory_high':              'memory_usage',
    'memory_critical':          'memory_usage',
    'memory_thrashing':         'memory_usage',
    'memory_leak_suspected':    'memory_usage',
    'cache_bloat':              'memory_usage',
    'cache_stale':              'memory_usage',
    'cpu_high':                 'cpu_usage',
    'cpu_critical':             'cpu_usage',
    'cpu_runaway_process':      'cpu_usage',
    'cpu_load_spike':           'load_average',
    'swap_high':                'swap_usage',
    'swap_critical':            'swap_usage',
    'memory_and_cpu_high':      'memory_usage',
    'oom_imminent':             'memory_usage',
    'preventive_optimization':  'memory_usage',
    'unknown_resource_issue':   'memory_usage',
}


@dataclass
class ThresholdAssessment:
    """Current threshold values with confidence"""
    monitor: float
    warning: float
    critical: float
    emergency: float
    
    # Confidence in each threshold (0.0-1.0)
    monitor_confidence: float
    warning_confidence: float
    critical_confidence: float
    emergency_confidence: float
    
    # Context
    metric_name: str
    system_id: str
    
    # Metadata
    sample_size: int
    last_updated: Optional[datetime]


class LearnedThresholds:
    """
    System-specific thresholds that learn from outcomes.
    
    Instead of "85% memory is critical," learns:
    "On THIS system, when memory hits 88% during business hours
    with growth_rate > 2%, it becomes critical within 15 minutes.
    But at night with growth_rate < 1%, it's usually fine."
    """
    
    def __init__(self, db_session: AsyncSession, system_id: str, agent_name: str = "meth_snail"):
        self.db = db_session
        self.system_id = system_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{agent_name}.learned_thresholds")
        
        # Reference module-level defaults (single source of truth)
        self.default_thresholds = DEFAULT_THRESHOLDS
        
        # Cache of learned thresholds (loaded from DB)
        self._threshold_cache: Dict[str, ThresholdAssessment] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=15)  # Refresh every 15 minutes
    
    async def get_threshold(
        self, 
        metric_name: str, 
        level: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Get threshold for this metric, adjusted for context.
        
        Args:
            metric_name: 'memory_usage', 'cpu_usage', etc.
            level: 'monitor', 'warning', 'critical', 'emergency'
            context: Optional context (time_of_day, day_of_week, etc.)
            
        Returns:
            Learned threshold value
        """
        
        # Get or refresh cached thresholds
        assessment = await self._get_threshold_assessment(metric_name)
        
        # Get base threshold
        base_threshold = getattr(assessment, level)
        
        if not context:
            return base_threshold
        
        # Apply contextual adjustment
        adjustment = await self._calculate_contextual_adjustment(
            metric_name, level, base_threshold, context
        )
        
        adjusted = base_threshold + adjustment
        
        if adjustment != 0:
            self.logger.debug(
                f"📚 {metric_name} {level} threshold: {base_threshold:.1f} → {adjusted:.1f} "
                f"(context adjustment: {adjustment:+.1f})"
            )
        
        return adjusted
    
    async def _get_threshold_assessment(self, metric_name: str) -> ThresholdAssessment:
        """Get threshold assessment from cache or DB"""
        
        # Check cache
        if metric_name in self._threshold_cache:
            if metric_name in self._cache_expiry:
                if utc_now().replace(tzinfo=None) < self._cache_expiry[metric_name]:
                    return self._threshold_cache[metric_name]
        
        # Load from database
        assessment = await self._load_thresholds_from_db(metric_name)
        
        # Cache it
        self._threshold_cache[metric_name] = assessment
        self._cache_expiry[metric_name] = utc_now().replace(tzinfo=None) + self._cache_ttl
        
        return assessment
    
    async def _load_thresholds_from_db(self, metric_name: str) -> ThresholdAssessment:
        """
        Load learned thresholds from database.
        
        Analyzes historical outcomes to determine optimal thresholds.
        """
        
        # Query recent learning records for this metric
        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        
        result = await self.db.execute(
            select(ThresholdLearningRecord).where(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date
                )
            )
        )
        records = result.scalars().all()
        
        if not records:
            # No learning history yet, use defaults
            defaults = self.default_thresholds.get(metric_name, self.default_thresholds['memory_usage'])
            
            self.logger.info(
                f"📚 No learning history for {metric_name}, using defaults "
                f"(warning: {defaults['warning']:.1f}, critical: {defaults['critical']:.1f})"
            )
            
            return ThresholdAssessment(
                monitor=defaults['monitor'],
                warning=defaults['warning'],
                critical=defaults['critical'],
                emergency=defaults['emergency'],
                monitor_confidence=0.3,
                warning_confidence=0.3,
                critical_confidence=0.3,
                emergency_confidence=0.3,
                metric_name=metric_name,
                system_id=self.system_id,
                sample_size=0,
                last_updated=None
            )
        
        # Analyze records to determine optimal thresholds
        thresholds = await self._analyze_threshold_records(metric_name, records)
        
        self.logger.info(
            f"📚 Loaded learned thresholds for {metric_name}: "
            f"warning={thresholds.warning:.1f} (conf: {thresholds.warning_confidence:.2f}), "
            f"critical={thresholds.critical:.1f} (conf: {thresholds.critical_confidence:.2f}) "
            f"[n={thresholds.sample_size}]"
        )
        
        return thresholds
    
    async def _analyze_threshold_records(
        self, 
        metric_name: str, 
        records: List[ThresholdLearningRecord]
    ) -> ThresholdAssessment:
        """
        Analyze learning records to determine optimal thresholds.
        
        Strategy:
        - False alarms suggest threshold too low → increase
        - Acted too late suggests threshold too high → decrease
        - Successful interventions confirm threshold appropriate
        """
        
        defaults = self.default_thresholds.get(metric_name, self.default_thresholds['memory_usage'])
        
        # Separate records by outcome type
        false_alarms = [r for r in records if r.was_false_alarm]
        acted_too_late = [r for r in records if r.should_have_acted_sooner]
        successful = [r for r in records if r.outcome_success and not r.was_false_alarm and not r.should_have_acted_sooner]
        
        # Calculate thresholds for each level
        warning_threshold = await self._calculate_threshold_level(
            'warning', defaults['warning'], false_alarms, acted_too_late, successful
        )
        
        critical_threshold = await self._calculate_threshold_level(
            'critical', defaults['critical'], false_alarms, acted_too_late, successful
        )
        
        emergency_threshold = await self._calculate_threshold_level(
            'emergency', defaults['emergency'], false_alarms, acted_too_late, successful
        )
        
        # Monitor threshold is typically lower than warning
        monitor_threshold = warning_threshold + THRESHOLD_LEARNING_CONFIG['monitor_offset']
        
        # Calculate confidence based on sample size and consistency
        total_samples = len(records)
        warning_confidence = min(1.0, total_samples / 50.0)  # Full confidence at 50+ samples
        critical_confidence = min(1.0, total_samples / 50.0)
        emergency_confidence = min(1.0, total_samples / 30.0)  # Emergency needs fewer samples
        monitor_confidence = warning_confidence * 0.8  # Slightly less confident in monitor
        
        return ThresholdAssessment(
            monitor=monitor_threshold,
            warning=warning_threshold,
            critical=critical_threshold,
            emergency=emergency_threshold,
            monitor_confidence=monitor_confidence,
            warning_confidence=warning_confidence,
            critical_confidence=critical_confidence,
            emergency_confidence=emergency_confidence,
            metric_name=metric_name,
            system_id=self.system_id,
            sample_size=total_samples,
            last_updated=utc_now().replace(tzinfo=None)
        )
    
    async def _calculate_threshold_level(
        self,
        level: str,
        default: float,
        false_alarms: List[ThresholdLearningRecord],
        acted_too_late: List[ThresholdLearningRecord],
        successful: List[ThresholdLearningRecord]
    ) -> float:
        """Calculate optimal threshold for a specific level.
        
        Both signals are independent and applied as a net adjustment.
        False alarms push the threshold up; too-late signals push it down.
        They are NOT mutually exclusive — both can fire in the same cycle.
        """
        cfg = THRESHOLD_LEARNING_CONFIG
        threshold = default
        net_adjustment = 0.0
        
        # Signal 1: false alarms — threshold was too low, raise it
        level_false_alarms = [r for r in false_alarms if r.threshold_level == level]
        if level_false_alarms:
            avg_false_alarm_value = statistics.mean([r.metric_value for r in level_false_alarms])
            overshoot = avg_false_alarm_value + cfg['false_alarm_adjustment'] - threshold
            if overshoot > 0:
                net_adjustment += overshoot
        
        # Signal 2: acted too late — threshold was too high, lower it
        level_too_late = [r for r in acted_too_late if r.threshold_level == level]
        if level_too_late:
            avg_too_late_value = statistics.mean([r.metric_value for r in level_too_late])
            undershoot = threshold - (avg_too_late_value - cfg['too_late_adjustment'])
            if undershoot > 0:
                net_adjustment -= undershoot
        
        threshold += net_adjustment
        
        # Signal 3: successful interventions confirm threshold — blend toward success value
        level_successful = [r for r in successful if r.threshold_level == level]
        if level_successful:
            avg_success_value = statistics.mean([r.metric_value for r in level_successful])
            blend_weight = cfg['success_blend_weight']
            threshold = (threshold * (1.0 - blend_weight)) + (avg_success_value * blend_weight)
        
        return max(cfg['min_threshold'], min(cfg['max_threshold'], threshold))
    
    async def _calculate_contextual_adjustment(
        self,
        metric_name: str,
        level: str,
        base_threshold: float,
        context: Dict[str, Any]
    ) -> float:
        """
        Adjust threshold based on context.
        
        Learn: "At night, memory can safely go higher"
        Learn: "During deployments, CPU spikes are normal"
        """
        
        cfg = THRESHOLD_LEARNING_CONFIG
        adjustment = 0.0
        
        # Query for similar contexts
        similar_records = await self._query_similar_contexts(metric_name, level, context)
        
        if not similar_records or len(similar_records) < 5:
            return 0.0  # Not enough data for contextual adjustment
        
        # Both signals are independent — apply net adjustment
        false_alarms_in_context = [r for r in similar_records if r.was_false_alarm]
        if false_alarms_in_context:
            avg_safe_value = statistics.mean([r.metric_value for r in false_alarms_in_context])
            if avg_safe_value > base_threshold:
                adjustment += (avg_safe_value - base_threshold) * cfg['contextual_conservative']
        
        too_late_in_context = [r for r in similar_records if r.should_have_acted_sooner]
        if too_late_in_context:
            avg_critical_value = statistics.mean([r.metric_value for r in too_late_in_context])
            if avg_critical_value < base_threshold:
                adjustment += (avg_critical_value - base_threshold) * cfg['contextual_conservative']
        
        cap = cfg['contextual_cap']
        adjustment = max(-cap, min(cap, adjustment))
        
        return adjustment
    
    async def _query_similar_contexts(
        self,
        metric_name: str,
        level: str,
        context: Dict[str, Any]
    ) -> List[ThresholdLearningRecord]:
        """
        Query database for records with similar context.
        
        Similar means:
        - Same time of day (±2 hours)
        - Same day of week
        - Similar system load
        """
        
        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        
        # Build context filters
        filters = [
            ThresholdLearningRecord.system_id == self.system_id,
            ThresholdLearningRecord.metric_name == metric_name,
            ThresholdLearningRecord.threshold_level == level,
            ThresholdLearningRecord.created_at >= cutoff_date
        ]
        
        # Time of day filter (if provided)
        if 'time_of_day' in context:
            hour = context['time_of_day']
            # Match records within ±2 hours, handling midnight wraparound correctly
            low = (hour - 2) % 24
            high = (hour + 2) % 24
            if low <= high:
                filters.append(
                    func.extract('hour', ThresholdLearningRecord.created_at).between(low, high)
                )
            else:
                # Wraps midnight: e.g. hour=1 → low=23, high=3
                filters.append(
                    or_(
                        func.extract('hour', ThresholdLearningRecord.created_at) >= low,
                        func.extract('hour', ThresholdLearningRecord.created_at) <= high
                    )
                )
        
        result = await self.db.execute(
            select(ThresholdLearningRecord).where(and_(*filters)).limit(100)
        )
        records = result.scalars().all()
        
        return records
    
    async def record_outcome(
        self,
        metric_name: str,
        metric_value: float,
        threshold_level: str,
        action_taken: Optional[str],
        outcome: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ):
        """
        Record outcome of a threshold crossing.
        
        This is how the system learns:
        - Was this a false alarm?
        - Did we act too late?
        - Was the threshold appropriate?
        """
        
        # Determine learning signals
        was_false_alarm = (
            action_taken is None and 
            outcome.get('resolved_naturally', False)
        )
        
        should_have_acted_sooner = (
            outcome.get('became_critical_before_action', False) or
            outcome.get('rapid_escalation', False)
        )
        
        outcome_success = outcome.get('success', False)
        
        # Get current threshold before recording
        old_assessment = await self._get_threshold_assessment(metric_name)
        old_threshold = getattr(old_assessment, threshold_level)
        
        # Create learning record
        record = ThresholdLearningRecord(
            system_id=self.system_id,
            agent_name=self.agent_name,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold_level=threshold_level,
            action_taken=action_taken,
            outcome_success=outcome_success,
            system_state=outcome.get('system_state', {}),
            context=context or {},
            time_to_critical=outcome.get('time_to_critical'),
            was_false_alarm=was_false_alarm,
            should_have_acted_sooner=should_have_acted_sooner
        )
        
        self.db.add(record)
        await self.db.flush()
        
        # Invalidate cache to force reload on next access
        if metric_name in self._threshold_cache:
            del self._threshold_cache[metric_name]
            del self._cache_expiry[metric_name]
        
        # Get new threshold after learning
        new_assessment = await self._get_threshold_assessment(metric_name)
        new_threshold = getattr(new_assessment, threshold_level)
        
        # Check if threshold changed significantly (>2%)
        threshold_changed = abs(new_threshold - old_threshold) > 2.0
        
        # Log learning
        if was_false_alarm:
            self.logger.info(
                f"📚 LEARNED: {metric_name} {threshold_level} threshold may be too low "
                f"(false alarm at {metric_value:.1f}%)"
            )
        elif should_have_acted_sooner:
            self.logger.warning(
                f"📚 LEARNED: {metric_name} {threshold_level} threshold may be too high "
                f"(should have acted sooner at {metric_value:.1f}%)"
            )
        elif outcome_success:
            self.logger.info(
                f"📚 LEARNED: {metric_name} {threshold_level} threshold appropriate "
                f"(successful intervention at {metric_value:.1f}%)"
            )
        
        # Emit learning event if threshold changed significantly
        if threshold_changed:
            try:
                from app.services.agent_decision_emitter import emit_learning_event
                
                # Count recent false alarms and too-late actions
                summary = await self.get_learning_summary(metric_name)
                
                reason_parts = []
                if summary['false_alarms'] > 0:
                    reason_parts.append(f"{summary['false_alarms']} false alarms")
                if summary['acted_too_late'] > 0:
                    reason_parts.append(f"{summary['acted_too_late']} too late")
                reason = ", ".join(reason_parts) if reason_parts else "learning from outcomes"
                
                await emit_learning_event(
                    agent_name=self.agent_name,
                    event_type="threshold_adjusted",
                    learning_data={
                        "metric": metric_name,
                        "threshold_level": threshold_level,
                        "old_value": round(old_threshold, 1),
                        "new_value": round(new_threshold, 1),
                        "reason": reason,
                        "confidence": round(getattr(new_assessment, f"{threshold_level}_confidence"), 2),
                        "total_records": summary['total_records']
                    },
                    user_id=user_id
                )
            except Exception as e:
                self.logger.error(f"🐌💥 Failed to emit learning event: {e}")
    
    async def get_threshold_confidence(self, metric_name: str, level: str) -> float:
        """Get confidence in a specific threshold"""
        assessment = await self._get_threshold_assessment(metric_name)
        return getattr(assessment, f"{level}_confidence")
    
    async def request_stick_validation(
        self,
        metric_name: str,
        threshold_level: str,
        db_getter
    ) -> bool:
        """
        Request The Stick to validate a learned threshold.
        
        Integration point: Terry learns → The Stick validates → audit trail created.
        
        Args:
            metric_name: Metric being thresholded (e.g., 'memory_usage')
            threshold_level: Level being validated (e.g., 'warning', 'critical')
            db_getter: Database session getter for The Stick
            
        Returns:
            True if validated, False if rejected
        """
        try:
            # Get threshold assessment
            assessment = await self._get_threshold_assessment(metric_name)
            learned_value = getattr(assessment, threshold_level)
            
            # Get default value
            defaults = self.default_thresholds.get(metric_name, self.default_thresholds['memory_usage'])
            default_value = defaults[threshold_level]
            
            # Get learning metadata
            cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
            result = await self.db.execute(
                select(ThresholdLearningRecord).where(
                    and_(
                        ThresholdLearningRecord.system_id == self.system_id,
                        ThresholdLearningRecord.metric_name == metric_name,
                        ThresholdLearningRecord.created_at >= cutoff_date
                    )
                )
            )
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
                    f"🐌📏 Threshold validation result: {audit_entry.validation_result} "
                    f"({metric_name}.{threshold_level})"
                )
                
                return audit_entry.validation_result
                
        except Exception as e:
            self.logger.error(f"Failed to request Stick validation: {e}")
            raise  # Surface the failure — silent False conflates unreachable with rejected
    
    async def is_below_threshold(
        self,
        metric_name: str,
        current_value: float,
        level: str = 'warning',
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a metric value is below the learned threshold for a given level.
        Used by ExecutionPlanner to evaluate goal satisfaction.
        
        Returns True if the value is safe (below threshold), False if threshold is crossed.
        """
        threshold = await self.get_threshold(metric_name, level, context)
        return current_value < threshold
    
    async def get_goal_thresholds(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, float]]:
        """
        Return learned thresholds for all levels of the metric associated with a goal.
        Used by ExecutionPlanner as the single source of truth for goal-to-metric mapping.
        
        Returns None if the goal is not in GOAL_METRIC_MAP (unknown goal — caller must handle).
        """
        metric_name = GOAL_METRIC_MAP.get(goal)
        if metric_name is None:
            return None
        
        return {
            level: await self.get_threshold(metric_name, level, context)
            for level in ('monitor', 'warning', 'critical', 'emergency')
        }
    
    async def get_learning_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary of learning for this metric"""
        
        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
        
        result = await self.db.execute(
            select(ThresholdLearningRecord).where(
                and_(
                    ThresholdLearningRecord.system_id == self.system_id,
                    ThresholdLearningRecord.metric_name == metric_name,
                    ThresholdLearningRecord.created_at >= cutoff_date
                )
            )
        )
        records = result.scalars().all()
        
        if not records:
            return {
                'metric_name': metric_name,
                'total_records': 0,
                'learning_status': 'no_data'
            }
        
        false_alarms = sum(1 for r in records if r.was_false_alarm)
        acted_too_late = sum(1 for r in records if r.should_have_acted_sooner)
        successful = sum(1 for r in records if r.outcome_success)
        
        assessment = await self._get_threshold_assessment(metric_name)
        
        return {
            'metric_name': metric_name,
            'total_records': len(records),
            'false_alarms': false_alarms,
            'acted_too_late': acted_too_late,
            'successful_interventions': successful,
            'current_thresholds': {
                'warning': assessment.warning,
                'critical': assessment.critical,
                'emergency': assessment.emergency
            },
            'confidence': {
                'warning': assessment.warning_confidence,
                'critical': assessment.critical_confidence,
                'emergency': assessment.emergency_confidence
            },
            'learning_status': 'active' if len(records) >= 10 else 'learning'
        }
