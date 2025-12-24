#!/usr/bin/env python3
"""
Sir Hawkington's Reasoning Layer - Aristocratic Root Cause Analysis

Analyzes:
- Resource alert severity and trends
- System-wide impact assessment
- Escalation necessity based on patterns
- Confidence in triage decision

This is where Sir Hawkington's aristocratic judgment comes into play.
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import HawkPerceptionContext

logger = logging.getLogger('HawkReasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class TriageReasoning:
    """Sir Hawkington's triage reasoning and decision factors"""
    
    # Core assessment
    should_escalate: bool
    confidence: float
    severity_assessment: str
    
    # Reasoning details
    primary_reason: str
    contributing_factors: list[str]
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    
    # Routing decision
    target_specialist: str
    coordination_urgency: str  # 'normal', 'high', 'critical'
    
    # Evidence
    historical_support: float
    pattern_match_quality: float
    data_quality_factor: float


class HawkReasoning:
    """
    Sir Hawkington's reasoning layer for triage decisions.
    
    🧐 "One must apply aristocratic logic to determine the proper course of action!"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
        # Escalation thresholds (can be tuned based on learning)
        self.escalation_threshold = 0.6
        self.critical_threshold = 0.8
        
    def reason(self, context: HawkPerceptionContext) -> TriageReasoning:
        """
        Analyze the situation and determine triage decision.
        
        Args:
            context: Perception context from HawkPerception
            
        Returns:
            TriageReasoning with decision and supporting evidence
        """
        logger.info(f"🧐🧠 Reasoning about {context.resource_type} alert...")
        
        # Calculate severity assessment
        severity_assessment = self._assess_severity(
            context.current_value,
            context.threshold,
            context.severity
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(
            context.current_value,
            context.threshold,
            context.data_quality_score
        )
        
        # Calculate escalation confidence
        escalation_confidence = self._calculate_escalation_confidence(
            context.historical_confidence,
            context.pattern_match_confidence,
            context.data_quality_score,
            severity_assessment
        )
        
        # Decide whether to escalate
        should_escalate = self._should_escalate(
            escalation_confidence,
            risk_level,
            context.data_quality_score
        )
        
        # Determine target specialist
        target_specialist = self._route_to_specialist(context.resource_type)
        
        # Determine coordination urgency
        coordination_urgency = self._determine_urgency(risk_level, severity_assessment)
        
        # Build reasoning explanation
        primary_reason = self._build_primary_reason(
            context.resource_type,
            context.current_value,
            context.threshold,
            should_escalate
        )
        
        contributing_factors = self._identify_contributing_factors(
            context,
            severity_assessment,
            risk_level
        )
        
        reasoning = TriageReasoning(
            should_escalate=should_escalate,
            confidence=escalation_confidence,
            severity_assessment=severity_assessment,
            primary_reason=primary_reason,
            contributing_factors=contributing_factors,
            risk_level=risk_level,
            target_specialist=target_specialist,
            coordination_urgency=coordination_urgency,
            historical_support=context.historical_confidence,
            pattern_match_quality=context.pattern_match_confidence,
            data_quality_factor=context.data_quality_score
        )
        
        logger.info(
            f"🧐✅ Reasoning complete: escalate={should_escalate}, "
            f"confidence={escalation_confidence:.2f}, risk={risk_level}"
        )
        
        return reasoning
    
    def _assess_severity(
        self,
        current_value: float,
        threshold: float,
        reported_severity: str
    ) -> str:
        """
        Assess the true severity of the resource alert.
        """
        if threshold <= 0:
            return reported_severity
        
        overage = (current_value - threshold) / threshold
        
        if overage < 0.1:
            return 'low'
        elif overage < 0.25:
            return 'medium'
        elif overage < 0.5:
            return 'high'
        else:
            return 'critical'
    
    def _determine_risk_level(
        self,
        current_value: float,
        threshold: float,
        data_quality: float
    ) -> str:
        """
        Determine overall risk level considering data quality.
        """
        if threshold <= 0:
            return 'low'
        
        overage = (current_value - threshold) / threshold
        
        # Adjust risk based on data quality
        if data_quality < 0.5:
            # Poor data quality increases uncertainty
            if overage > 0.5:
                return 'high'  # Be cautious with poor data
            else:
                return 'medium'
        
        # Good data quality, assess normally
        if overage < 0.1:
            return 'low'
        elif overage < 0.3:
            return 'medium'
        elif overage < 0.6:
            return 'high'
        else:
            return 'critical'
    
    def _calculate_escalation_confidence(
        self,
        historical_confidence: float,
        pattern_match_confidence: float,
        data_quality: float,
        severity: str
    ) -> float:
        """
        Calculate overall confidence in escalation decision.
        """
        # Weight the factors
        confidence = (
            historical_confidence * 0.3 +
            pattern_match_confidence * 0.3 +
            data_quality * 0.2
        )
        
        # Boost confidence for critical severity
        if severity == 'critical':
            confidence = min(1.0, confidence + 0.2)
        elif severity == 'high':
            confidence = min(1.0, confidence + 0.1)
        
        return confidence
    
    def _should_escalate(
        self,
        confidence: float,
        risk_level: str,
        data_quality: float
    ) -> bool:
        """
        Decide whether to escalate to VIC-20.
        
        🧐 "One must know when to call for reinforcements!"
        """
        # Always escalate critical risks
        if risk_level == 'critical':
            return True
        
        # Escalate high risks with reasonable confidence
        if risk_level == 'high' and confidence >= self.escalation_threshold:
            return True
        
        # Escalate medium risks with high confidence
        if risk_level == 'medium' and confidence >= self.critical_threshold:
            return True
        
        # Don't escalate if data quality is too poor
        if data_quality < 0.3:
            logger.warning("🧐⚠️ Data quality too poor to escalate confidently")
            return False
        
        return False
    
    def _route_to_specialist(self, resource_type: str) -> str:
        """
        Determine which specialist should handle this resource type.
        """
        routing_map = {
            'cpu': 'meth_snail',
            'memory': 'meth_snail',
            'swap': 'meth_snail',
            'disk': 'hamsters',
            'network': 'quantum_shadow_people',
        }
        
        return routing_map.get(resource_type.lower(), 'vic20_sage')
    
    def _determine_urgency(self, risk_level: str, severity: str) -> str:
        """
        Determine coordination urgency level.
        """
        if risk_level == 'critical' or severity == 'critical':
            return 'critical'
        elif risk_level == 'high' or severity == 'high':
            return 'high'
        else:
            return 'normal'
    
    def _build_primary_reason(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        should_escalate: bool
    ) -> str:
        """
        Build primary reasoning explanation.
        """
        overage = ((current_value - threshold) / threshold * 100) if threshold > 0 else 0
        
        if should_escalate:
            return (
                f"{resource_type.upper()} at {current_value:.1f}% exceeds threshold "
                f"by {overage:.1f}% - escalation to VIC-20 warranted"
            )
        else:
            return (
                f"{resource_type.upper()} at {current_value:.1f}% within acceptable "
                f"range - monitoring continues"
            )
    
    def _identify_contributing_factors(
        self,
        context: HawkPerceptionContext,
        severity: str,
        risk_level: str
    ) -> list[str]:
        """
        Identify contributing factors to the decision.
        """
        factors = []
        
        if context.data_quality_score < 0.7:
            factors.append(f"Poor data quality ({context.data_quality_score:.2f})")
        
        if context.monocle_yeet_count > 0:
            factors.append(f"{context.monocle_yeet_count} monocle yeet(s) detected")
        
        if len(context.similar_triages) > 0:
            success_rate = sum(1 for t in context.similar_triages if t.get('success')) / len(context.similar_triages)
            factors.append(f"Historical success rate: {success_rate:.1%}")
        
        if severity == 'critical':
            factors.append("Critical severity level")
        
        if risk_level == 'high' or risk_level == 'critical':
            factors.append(f"Risk level: {risk_level}")
        
        return factors
