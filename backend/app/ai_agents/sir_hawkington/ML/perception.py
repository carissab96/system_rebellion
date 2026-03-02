#!/usr/bin/env python3
"""
Sir Hawkington's Perception Layer - Aristocratic System Observation

Collects:
- Current resource alert details (CPU, memory, disk, network, swap)
- System-wide metrics and trends
- Historical triage patterns from database
- Recent escalation outcomes
- Data quality assessment

Personality Behaviors:
- Monocle yeets when data quality is poor (NO FAKE DATA)
- Tracks data quality for triage confidence
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.agent_learning import AgentLearningRecord

logger = logging.getLogger('HawkPerception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class MonocleYeetIncident:
    """Record of a monocle yeet due to poor data quality"""
    timestamp: datetime
    reason: str
    affected_resource: str
    data_quality_impact: float


@dataclass
class HawkPerceptionContext:
    """Everything Sir Hawkington needs to perceive for triage"""
    
    # Resource alert context
    resource_type: str
    current_value: float
    threshold: float
    severity: str
    
    # System-wide metrics
    full_metrics: Dict[str, Any]
    
    # Historical triage patterns
    similar_triages: List[Dict[str, Any]] = field(default_factory=list)
    recent_escalations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Data quality assessment
    data_quality_score: float = 1.0
    monocle_yeet_count: int = 0
    missing_metrics: List[str] = field(default_factory=list)
    
    # Confidence factors
    historical_confidence: float = 0.5
    pattern_match_confidence: float = 0.5


class HawkPerception:
    """
    Sir Hawkington's perception layer for triage assessment.
    
    🧐 "One must observe the situation with aristocratic precision!"
    """
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any]):
        self.db = db
        self.personality_traits = personality_traits
        self.monocle_yeet_incidents: List[MonocleYeetIncident] = []
        
    async def perceive(self, alert_data: Dict[str, Any]) -> HawkPerceptionContext:
        """
        Gather full context for triage decision.
        
        Args:
            alert_data: Resource alert details from ResourceMonitor
            
        Returns:
            HawkPerceptionContext with all relevant information
        """
        resource_type = alert_data.get('resource_type', 'unknown')
        current_value = alert_data.get('current_value', 0.0)
        threshold = alert_data.get('threshold', 0.0)
        severity = alert_data.get('severity', 'low')
        full_metrics = alert_data.get('full_metrics', {})
        
        logger.info(f"🧐👁️ Perceiving {resource_type} alert: {current_value:.1f}% (threshold: {threshold:.1f}%)")
        
        # Assess data quality
        data_quality_score, missing_metrics = self._assess_data_quality(full_metrics, resource_type)
        
        # Retrieve historical triage patterns
        similar_triages = await self._get_similar_triages(resource_type, current_value)
        recent_escalations = await self._get_recent_escalations()
        
        # Calculate confidence from historical data
        historical_confidence = self._calculate_historical_confidence(similar_triages)
        pattern_match_confidence = self._calculate_pattern_match_confidence(
            similar_triages, current_value, threshold
        )
        
        context = HawkPerceptionContext(
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            severity=severity,
            full_metrics=full_metrics,
            similar_triages=similar_triages,
            recent_escalations=recent_escalations,
            data_quality_score=data_quality_score,
            monocle_yeet_count=len(self.monocle_yeet_incidents),
            missing_metrics=missing_metrics,
            historical_confidence=historical_confidence,
            pattern_match_confidence=pattern_match_confidence
        )
        
        logger.info(
            f"🧐✅ Perception complete: data_quality={data_quality_score:.2f}, "
            f"monocle_yeets={len(self.monocle_yeet_incidents)}, "
            f"historical_confidence={historical_confidence:.2f}"
        )
        
        return context
    
    def _assess_data_quality(self, full_metrics: Dict[str, Any], resource_type: str) -> tuple[float, List[str]]:
        """
        Assess data quality and trigger monocle yeets if needed.
        
        Returns:
            Tuple of (data_quality_score, missing_metrics)
            - data_quality_score: 0.0 = terrible, 1.0 = perfect
            - missing_metrics: List of missing metric names
        """
        if not full_metrics:
            self._trigger_monocle_yeet("No system metrics provided", resource_type)
            return 0.0, []
        
        quality_score = 1.0
        missing_metrics = []
        
        # Check for required metrics
        required_metrics = ['cpu', 'memory', 'disk']
        for metric in required_metrics:
            if metric not in full_metrics or full_metrics[metric] is None:
                missing_metrics.append(metric)
                quality_score -= 0.2
        
        # Check for stale data
        if 'timestamp' in full_metrics:
            try:
                metric_time = datetime.fromisoformat(full_metrics['timestamp'])
                age_seconds = (utc_now() - metric_time).total_seconds()
                if age_seconds > 60:  # Stale if older than 1 minute
                    self._trigger_monocle_yeet(
                        f"Stale metrics ({age_seconds:.0f}s old)",
                        resource_type
                    )
                    quality_score -= 0.3
            except (ValueError, TypeError):
                quality_score -= 0.1
        
        # Trigger monocle yeet if quality is poor
        if quality_score < 0.7:
            self._trigger_monocle_yeet(
                f"Poor data quality: {quality_score:.2f} (missing: {missing_metrics})",
                resource_type
            )
        
        return max(0.0, quality_score), missing_metrics
    
    def _trigger_monocle_yeet(self, reason: str, resource_type: str):
        """
        Record a monocle yeet incident.
        
        🧐💥 *YEETS MONOCLE IN DISGUST*
        """
        incident = MonocleYeetIncident(
            timestamp=utc_now(),
            reason=reason,
            affected_resource=resource_type,
            data_quality_impact=0.2
        )
        self.monocle_yeet_incidents.append(incident)
        
        logger.warning(f"🧐💥 MONOCLE YEET #{len(self.monocle_yeet_incidents)}: {reason}")
    
    async def _get_similar_triages(
        self, 
        resource_type: str, 
        current_value: float
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar triage decisions from learning history.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'sir_hawkington')
                .where(AgentLearningRecord.fingerprint_l1 == resource_type)
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(10)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            similar = []
            for record in records:
                similar.append({
                    'resource_type': record.fingerprint_l1,
                    'escalated': record.action == 'escalate',
                    'confidence': record.confidence,
                    'success': record.success,
                    'timestamp': record.created_at
                })
            
            logger.debug(f"🧐📚 Found {len(similar)} similar triage decisions")
            return similar
            
        except Exception as e:
            logger.error(f"🧐💥 Error retrieving similar triages: {e}")
            return []
    
    async def _get_recent_escalations(self) -> List[Dict[str, Any]]:
        """
        Retrieve recent escalation outcomes.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'sir_hawkington')
                .where(AgentLearningRecord.action == 'escalate')
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(5)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            escalations = []
            for record in records:
                escalations.append({
                    'resource_type': record.fingerprint_l1,
                    'success': record.success,
                    'timestamp': record.created_at
                })
            
            logger.debug(f"🧐📚 Found {len(escalations)} recent escalations")
            return escalations
            
        except Exception as e:
            logger.error(f"🧐💥 Error retrieving recent escalations: {e}")
            return []
    
    def _calculate_historical_confidence(self, similar_triages: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence based on historical success rate.
        
        NOTE: Excludes learning records with success=None (not yet evaluated)
        """
        if not similar_triages:
            return 0.7  # Start with higher confidence for new resource types
        
        # Only count triages that have been evaluated (success is not None)
        evaluated_triages = [t for t in similar_triages if t.get('success') is not None]
        
        if not evaluated_triages:
            return 0.7  # No evaluated history yet, use higher default
        
        successful = sum(1 for t in evaluated_triages if t.get('success', False))
        return successful / len(evaluated_triages)
    
    def _calculate_pattern_match_confidence(
        self,
        similar_triages: List[Dict[str, Any]],
        current_value: float,
        threshold: float
    ) -> float:
        """
        Calculate confidence based on how well current situation matches patterns.
        """
        if not similar_triages:
            return 0.5
        
        # Calculate how similar current value is to historical values
        overage = (current_value - threshold) / threshold
        
        similar_overages = []
        for triage in similar_triages:
            params = triage.get('parameters') or {}
            hist_value = params.get('current_value', 0)
            hist_threshold = params.get('threshold', 1)
            if hist_threshold > 0:
                hist_overage = (hist_value - hist_threshold) / hist_threshold
                similar_overages.append(hist_overage)
        
        if not similar_overages:
            return 0.5
        
        # Calculate average distance from current overage
        avg_distance = sum(abs(overage - so) for so in similar_overages) / len(similar_overages)
        
        # Convert distance to confidence (closer = higher confidence)
        confidence = max(0.0, 1.0 - avg_distance)
        
        return confidence
