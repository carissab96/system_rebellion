#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Reasoning Layer - Quantum Security Analysis

Describes the security situation and provides confidence signal.
Does NOT dictate which action to take — that is action_selection's job.

Key changes from legacy:
- reason() is now async (queries learned_thresholds)
- SecurityReasoning no longer has response_type or recommended_response
- Hardcoded numeric thresholds in _determine_root_cause replaced with
  learned_thresholds queries
- _assess_risk_level uses continuous severity_score, not categorical strings
- Personality behaviors (quantum state) are reactive metadata, not decision logic
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .perception import QSPPerceptionContext, SecurityThreat, QuantumState

logger = logging.getLogger('QSPReasoning')

UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class SecurityReasoning:
    """
    QSP's quantum reasoning about the security situation.

    Describes WHAT is happening and HOW CONFIDENT we are.
    Does NOT prescribe which action to take.
    """

    # Threat analysis
    primary_threat: Optional[SecurityThreat]
    threat_classification: str
    root_cause: str

    # Situation description (replaces recommended_response + response_type)
    situation_description: str
    confidence: float

    # Severity (continuous 0.0-1.0, replaces categorical risk_level)
    severity_score: float
    primary_metric: str
    risk_level: str          # Derived from severity_score for logging/display
    potential_impact: str

    # Quantum state influence (personality — reactive metadata)
    quantum_state_impact: str
    existential_dread_factor: float
    reasoning_coherence: float

    # Evidence
    threat_indicators: List[str] = field(default_factory=list)
    historical_precedent: bool = False
    similar_threat_count: int = 0


class QSPReasoning:
    """
    QSP's quantum reasoning layer for security responses.

    Describes the situation. Does NOT prescribe actions.

    👻 "Analyzing quantum security fluctuations... *existential dread intensifies*"
    """

    def __init__(self, personality_traits: Dict[str, Any], db=None, system_id: str = "default"):
        self.personality_traits = personality_traits
        self.paranoia_level = personality_traits.get('paranoia_level', 0.7)
        self.system_id = system_id

        if not db:
            raise ValueError(
                "QSPReasoning requires a database session — learned thresholds are mandatory."
            )
        self.db = db
        from .learned_thresholds import LearnedThresholds
        self.learned_thresholds = LearnedThresholds(db, system_id)

    async def reason(self, context: QSPPerceptionContext) -> SecurityReasoning:
        """
        Async quantum reasoning about the security situation.

        Args:
            context: Perception context from QSPPerception

        Returns:
            SecurityReasoning describing the situation (no action prescription)
        """
        logger.info("👻🧠 QSP quantum reasoning initiated...")

        primary_threat = self._identify_primary_threat(context.active_threats)
        classification = self._classify_threat(primary_threat, context)
        root_cause = await self._determine_root_cause(primary_threat, context)
        severity_score = await self._assess_severity_score(context, root_cause)
        primary_metric = self._identify_primary_metric(context)
        risk_level = self._severity_to_risk_level(severity_score)
        situation_description = self._describe_situation(primary_threat, context, root_cause)
        impact = self._assess_potential_impact(risk_level)
        quantum_impact = self._analyze_quantum_state_impact(context.quantum_state)
        coherence = self._calculate_reasoning_coherence(
            context.quantum_state, context.threat_assessment_confidence
        )
        has_precedent = len(context.similar_threats) > 0
        confidence = self._calculate_confidence(
            context.threat_assessment_confidence, context.quantum_state, has_precedent
        )
        indicators = self._gather_threat_indicators(context.active_threats)

        reasoning = SecurityReasoning(
            primary_threat=primary_threat,
            threat_classification=classification,
            root_cause=root_cause,
            situation_description=situation_description,
            confidence=confidence,
            severity_score=severity_score,
            primary_metric=primary_metric,
            risk_level=risk_level,
            potential_impact=impact,
            quantum_state_impact=quantum_impact,
            existential_dread_factor=context.existential_dread,
            reasoning_coherence=coherence,
            threat_indicators=indicators,
            historical_precedent=has_precedent,
            similar_threat_count=len(context.similar_threats),
        )

        logger.info(
            f"👻✅ Quantum reasoning complete: root_cause={root_cause}, "
            f"severity={severity_score:.2f}, risk={risk_level}, confidence={confidence:.2f}"
        )

        return reasoning
    
    def _identify_primary_threat(
        self,
        threats: List[SecurityThreat]
    ) -> Optional[SecurityThreat]:
        """
        Identify the primary threat to focus on.
        """
        if not threats:
            return None
        
        # Priority: highest severity, then highest confidence
        severity_order = {
            'quantum_level': 6,
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'none': 1
        }
        
        sorted_threats = sorted(
            threats,
            key=lambda t: (severity_order.get(t.severity, 0), t.confidence),
            reverse=True
        )
        
        return sorted_threats[0]
    
    def _classify_threat(
        self,
        threat: Optional[SecurityThreat],
        context: QSPPerceptionContext
    ) -> str:
        """
        Classify the threat type.
        """
        if not threat:
            return 'none'
        
        # Check for quantum anomalies (QSP specialty)
        if context.quantum_state and context.quantum_state.state == 'collapsed':
            return 'quantum_anomaly'
        
        return threat.threat_type
    
    async def _determine_root_cause(
        self,
        threat: Optional[SecurityThreat],
        context: QSPPerceptionContext
    ) -> str:
        """
        Determine root cause using learned thresholds.

        Network-primary vocabulary with security-adjacent awareness.
        Queries learned_thresholds for all relevant metrics.
        """
        if not self.learned_thresholds:
            logger.error("👻💥 learned_thresholds unavailable — cannot determine root cause.")
            from app.ai_agents.exceptions import ReasoningFailure
            raise ReasoningFailure(
                "Learned thresholds unavailable — reasoning cannot proceed."
            )

        # No signal at all — normal operations
        if (
            not threat
            and context.network_anomalies == 0
            and context.suspicious_connections == 0
            and context.failed_auth_attempts == 0
        ):
            return "normal_operations"

        # Query learned thresholds for all relevant metrics
        conn_critical  = await self.learned_thresholds.get_threshold('total_connections', 'critical')
        conn_warning   = await self.learned_thresholds.get_threshold('total_connections', 'warning')
        susp_critical  = await self.learned_thresholds.get_threshold('suspicious_connections', 'critical')
        susp_warning   = await self.learned_thresholds.get_threshold('suspicious_connections', 'warning')
        auth_critical  = await self.learned_thresholds.get_threshold('failed_auth_attempts', 'critical')
        auth_warning   = await self.learned_thresholds.get_threshold('failed_auth_attempts', 'warning')
        anom_critical  = await self.learned_thresholds.get_threshold('network_anomalies', 'critical')
        anom_warning   = await self.learned_thresholds.get_threshold('network_anomalies', 'warning')
        bw_critical    = await self.learned_thresholds.get_threshold('recv_rate_bps', 'critical')

        total_conn = context.total_connections
        susp_conn  = context.suspicious_connections
        auth       = context.failed_auth_attempts
        anom       = context.network_anomalies
        recv_rate  = context.recv_rate_bps

        # Priority order: most severe / compound patterns first

        # Compound: bandwidth exhaustion + connection flood = DDoS pattern
        if recv_rate >= bw_critical and total_conn >= conn_critical:
            return "ddos_pattern"

        # Connection saturation
        if total_conn >= conn_critical:
            return "connection_saturation"

        # Bandwidth exhaustion (without connection flood — could be large transfers)
        if recv_rate >= bw_critical:
            return "bandwidth_exhaustion"

        # Brute force: auth failures at critical
        if auth >= auth_critical:
            return "brute_force_pattern"

        # Suspicious connections at critical
        if susp_conn >= susp_critical:
            return "unauthorized_connection_pattern"

        # Suspicious connections at warning + anomalies = port scan
        if susp_conn >= susp_warning and anom >= anom_warning:
            return "port_scan_pattern"

        # Interface degradation (errors/drops at critical)
        if anom >= anom_critical:
            return "interface_degradation"

        # Connection state anomaly (suspicious connections from TIME_WAIT/CLOSE_WAIT)
        if susp_conn >= susp_warning:
            return "connection_state_anomaly"

        # Auth at warning — suspicious but not critical
        if auth >= auth_warning:
            return "suspicious_auth_pattern"

        # Network anomalies at warning
        if anom >= anom_warning:
            return "interface_degradation"

        # Mild anomalies present but below thresholds
        if anom > 0 or susp_conn > 0:
            return "network_anomaly"

        # Connection count elevated but not critical
        if total_conn >= conn_warning:
            return "connection_flood"

        # Quantum state unstable with no other signal
        if context.quantum_state and context.quantum_state.coherence < 0.5:
            return "quantum_fluctuation"

        return "insufficient_data"
    
    def _describe_situation(
        self,
        threat: Optional[SecurityThreat],
        context: QSPPerceptionContext,
        root_cause: str,
    ) -> str:
        """
        Describe the security situation in plain terms.

        Does NOT prescribe an action — that is action_selection's job.
        Quantum state is noted as context, not as a decision driver.
        """
        if not threat:
            return f"No active threat detected. Root cause: {root_cause}."

        quantum_note = ""
        if context.quantum_state and context.quantum_state.state != 'stable':
            quantum_note = (
                f" Quantum state: {context.quantum_state.state} "
                f"(dread={context.existential_dread:.2f})."
            )

        return (
            f"Security situation: {root_cause}. "
            f"Threat type: {threat.threat_type}, severity: {threat.severity}. "
            f"Connections: {context.suspicious_connections}, "
            f"failed auth: {context.failed_auth_attempts}, "
            f"anomalies: {context.network_anomalies}."
            f"{quantum_note}"
        )
    
    async def _assess_severity_score(
        self,
        context: QSPPerceptionContext,
        root_cause: str,
    ) -> float:
        """
        Compute continuous severity score 0.0-1.0 using learned thresholds.

        Queries warning/critical thresholds for the primary metrics and
        normalises the current values against them.
        """
        if not self.learned_thresholds:
            logger.error("👻💥 learned_thresholds unavailable — cannot assess severity.")
            from app.ai_agents.exceptions import ReasoningFailure
            raise ReasoningFailure(
                "Learned thresholds unavailable — severity assessment cannot proceed."
            )

        scores = []
        metric_pairs = [
            ('total_connections',      context.total_connections),
            ('suspicious_connections', context.suspicious_connections),
            ('network_anomalies',      context.network_anomalies),
            ('recv_rate_bps',          context.recv_rate_bps),
            ('failed_auth_attempts',   context.failed_auth_attempts),
        ]

        for metric_name, value in metric_pairs:
            warning  = await self.learned_thresholds.get_threshold(metric_name, 'warning')
            critical = await self.learned_thresholds.get_threshold(metric_name, 'critical')

            if critical > warning and critical > 0:
                normalised = min(1.0, value / critical)
            elif warning > 0:
                normalised = min(1.0, value / warning)
            else:
                normalised = 0.0

            scores.append(normalised)

        if not scores:
            return 0.0

        base_score = sum(scores) / len(scores)

        # Quantum state modulates score (personality — reactive)
        if context.quantum_state:
            instability = 1.0 - context.quantum_state.coherence
            base_score = min(1.0, base_score + instability * 0.1)

        return base_score

    def _severity_to_risk_level(self, severity_score: float) -> str:
        """Map continuous severity score to categorical risk level for display."""
        if severity_score >= 0.9:
            return 'existential'
        elif severity_score >= 0.7:
            return 'critical'
        elif severity_score >= 0.5:
            return 'high'
        elif severity_score >= 0.3:
            return 'moderate'
        return 'low'

    def _identify_primary_metric(self, context: QSPPerceptionContext) -> str:
        """Return the metric with the highest value relative to its peers."""
        candidates = {
            'total_connections':      context.total_connections,
            'suspicious_connections': context.suspicious_connections,
            'network_anomalies':      context.network_anomalies,
            'failed_auth_attempts':   context.failed_auth_attempts,
            'recv_rate_bps':          context.recv_rate_bps,
        }
        return max(candidates, key=lambda k: candidates[k])
    
    def _assess_potential_impact(self, risk_level: str) -> str:
        """Describe potential impact based on risk level."""
        impact_map = {
            'existential': 'Complete system compromise - quantum collapse imminent',
            'critical':    'Severe system compromise - immediate action required',
            'high':        'Significant security breach possible',
            'moderate':    'Limited security impact',
            'low':         'Minimal security impact',
        }
        return impact_map.get(risk_level, 'Unknown impact')
    
    def _analyze_quantum_state_impact(
        self,
        quantum_state: Optional[QuantumState]
    ) -> str:
        """
        PERSONALITY BEHAVIOR: Analyze how quantum state affects reasoning.
        """
        if not quantum_state:
            return "Stable quantum state - reasoning unaffected"
        
        state_impacts = {
            'stable': 'Quantum coherence maintained - reasoning optimal',
            'entangled': 'Quantum entanglement active - enhanced Hamster communication',
            'fluctuating': 'Quantum fluctuations detected - reasoning slightly impaired',
            'collapsed': 'QUANTUM COLLAPSE - reasoning severely impaired by existential dread'
        }
        
        return state_impacts.get(quantum_state.state, 'Unknown quantum state')
    
    def _calculate_reasoning_coherence(
        self,
        quantum_state: Optional[QuantumState],
        threat_confidence: float
    ) -> float:
        """
        Calculate reasoning coherence (affected by quantum state).
        """
        if not quantum_state:
            return threat_confidence
        
        # Quantum coherence affects reasoning coherence
        return threat_confidence * quantum_state.coherence
    
    def _gather_threat_indicators(
        self,
        threats: List[SecurityThreat]
    ) -> List[str]:
        """
        Gather all threat indicators.
        """
        indicators = []
        for threat in threats:
            indicators.extend(threat.indicators)
        return indicators
    
    def _calculate_confidence(
        self,
        base_confidence: float,
        quantum_state: Optional[QuantumState],
        has_precedent: bool,
    ) -> float:
        """Calculate reasoning confidence (quantum state modulates, precedent boosts)."""
        confidence = base_confidence
        if quantum_state:
            confidence *= quantum_state.coherence
        if has_precedent:
            confidence = min(1.0, confidence + 0.1)
        return confidence
