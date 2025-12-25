#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Reasoning Layer - Quantum Security Analysis

Analyzes:
- Security threat severity and classification
- Response strategy selection
- Quantum state implications
- Risk assessment with existential dread
- Communication needs with Hamsters

QSP's reasoning is influenced by their quantum state and existential dread levels.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import QSPPerceptionContext, SecurityThreat, QuantumState

logger = logging.getLogger('QSPReasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class SecurityReasoning:
    """QSP's quantum reasoning about security response"""
    
    # Threat analysis
    primary_threat: Optional[SecurityThreat]
    threat_classification: str  # 'intrusion', 'anomaly', 'vulnerability', 'attack', 'quantum_anomaly'
    root_cause: str
    
    # Response strategy
    recommended_response: str
    response_type: str  # 'monitor', 'investigate', 'block', 'escalate', 'quantum_intervention'
    confidence: float
    
    # Risk assessment
    risk_level: str  # 'low', 'moderate', 'high', 'critical', 'existential'
    potential_impact: str
    
    # Quantum state influence
    quantum_state_impact: str  # How quantum state affects reasoning
    existential_dread_factor: float
    reasoning_coherence: float  # How stable the reasoning is
    
    # Communication needs
    requires_hamster_assistance: bool
    quantum_message_priority: str  # 'low', 'normal', 'high', 'urgent'
    
    # Evidence
    threat_indicators: List[str]
    historical_precedent: bool
    similar_threat_count: int


class QSPReasoning:
    """
    QSP's quantum reasoning layer for security responses.
    
    👻 "Analyzing quantum security fluctuations... *existential dread intensifies*"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        self.paranoia_level = personality_traits.get('paranoia_level', 0.7)
        
    def reason(self, context: QSPPerceptionContext) -> SecurityReasoning:
        """
        Quantum reasoning about security response.
        
        Args:
            context: Perception context from QSPPerception
            
        Returns:
            SecurityReasoning with quantum-influenced analysis
        """
        logger.info(f"👻🧠 QSP quantum reasoning initiated...")
        
        # Identify primary threat
        primary_threat = self._identify_primary_threat(context.active_threats)
        
        # Classify threat
        classification = self._classify_threat(primary_threat, context)
        
        # Determine root cause
        root_cause = self._determine_root_cause(primary_threat, context)
        
        # Select response strategy (influenced by quantum state)
        response, response_type = self._select_response_strategy(
            primary_threat,
            context.quantum_state,
            context
        )
        
        # Assess risk level
        risk_level = self._assess_risk_level(
            primary_threat,
            context.quantum_state,
            context.threat_count
        )
        
        # Determine potential impact
        impact = self._assess_potential_impact(primary_threat, risk_level)
        
        # Analyze quantum state impact on reasoning
        quantum_impact = self._analyze_quantum_state_impact(context.quantum_state)
        
        # Calculate reasoning coherence (affected by quantum state)
        coherence = self._calculate_reasoning_coherence(
            context.quantum_state,
            context.threat_assessment_confidence
        )
        
        # Determine if Hamster assistance needed
        needs_hamsters = self._needs_hamster_assistance(
            risk_level,
            context.quantum_state,
            response_type
        )
        
        # Set quantum message priority
        message_priority = self._determine_message_priority(
            risk_level,
            context.quantum_state
        )
        
        # Gather threat indicators
        indicators = self._gather_threat_indicators(context.active_threats)
        
        # Check historical precedent
        has_precedent = len(context.similar_threats) > 0
        
        # Calculate confidence (affected by quantum state)
        confidence = self._calculate_confidence(
            context.threat_assessment_confidence,
            context.quantum_state,
            has_precedent
        )
        
        reasoning = SecurityReasoning(
            primary_threat=primary_threat,
            threat_classification=classification,
            root_cause=root_cause,
            recommended_response=response,
            response_type=response_type,
            confidence=confidence,
            risk_level=risk_level,
            potential_impact=impact,
            quantum_state_impact=quantum_impact,
            existential_dread_factor=context.existential_dread,
            reasoning_coherence=coherence,
            requires_hamster_assistance=needs_hamsters,
            quantum_message_priority=message_priority,
            threat_indicators=indicators,
            historical_precedent=has_precedent,
            similar_threat_count=len(context.similar_threats)
        )
        
        logger.info(
            f"👻✅ Quantum reasoning complete: {response_type}, "
            f"risk={risk_level}, confidence={confidence:.2f}, "
            f"dread={context.existential_dread:.2f}"
        )
        
        if needs_hamsters:
            logger.info(f"👻📡 Hamster assistance required (quantum entanglement needed)")
        
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
    
    def _determine_root_cause(
        self,
        threat: Optional[SecurityThreat],
        context: QSPPerceptionContext
    ) -> str:
        """
        Determine root cause of security threat.
        """
        if not threat:
            return "No active threats detected"
        
        if context.failed_auth_attempts > 10:
            return "Multiple failed authentication attempts - possible brute force attack"
        elif context.suspicious_connections > 5:
            return "Suspicious network connections detected - possible intrusion"
        elif context.network_anomalies > 0:
            return f"Network anomalies detected ({context.network_anomalies} anomalies)"
        else:
            return threat.description or "Unknown security threat"
    
    def _select_response_strategy(
        self,
        threat: Optional[SecurityThreat],
        quantum_state: Optional[QuantumState],
        context: QSPPerceptionContext
    ) -> tuple[str, str]:
        """
        Select response strategy based on threat and quantum state.
        
        Quantum state influences response aggressiveness.
        """
        if not threat:
            return "Continue monitoring", "monitor"
        
        # Quantum state affects response
        if quantum_state and quantum_state.state == 'collapsed':
            # Panicking - escalate everything
            return "QUANTUM INTERVENTION REQUIRED - Escalate to Hamsters", "quantum_intervention"
        
        # Normal response selection based on severity
        severity = threat.severity
        
        if severity in ['critical', 'quantum_level']:
            return "Block threat and escalate immediately", "block"
        elif severity == 'high':
            return "Investigate and prepare to block", "investigate"
        elif severity == 'medium':
            return "Monitor closely and gather evidence", "monitor"
        else:
            return "Continue passive monitoring", "monitor"
    
    def _assess_risk_level(
        self,
        threat: Optional[SecurityThreat],
        quantum_state: Optional[QuantumState],
        threat_count: int
    ) -> str:
        """
        Assess overall risk level.
        
        Quantum state and paranoia influence risk assessment.
        """
        if not threat:
            return 'low'
        
        # Base risk from threat severity
        severity_risk = {
            'quantum_level': 'existential',
            'critical': 'critical',
            'high': 'high',
            'medium': 'moderate',
            'low': 'low',
            'none': 'low'
        }
        
        base_risk = severity_risk.get(threat.severity, 'moderate')
        
        # Quantum state escalates risk
        if quantum_state:
            if quantum_state.state == 'collapsed':
                return 'existential'  # Maximum risk
            elif quantum_state.state == 'fluctuating' and base_risk in ['high', 'critical']:
                return 'critical'
        
        # Multiple threats escalate risk
        if threat_count > 3 and base_risk in ['moderate', 'high']:
            return 'critical'
        
        return base_risk
    
    def _assess_potential_impact(
        self,
        threat: Optional[SecurityThreat],
        risk_level: str
    ) -> str:
        """
        Assess potential impact of threat.
        """
        impact_map = {
            'existential': 'Complete system compromise - quantum collapse imminent',
            'critical': 'Severe system compromise - immediate action required',
            'high': 'Significant security breach possible',
            'moderate': 'Limited security impact',
            'low': 'Minimal security impact'
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
    
    def _needs_hamster_assistance(
        self,
        risk_level: str,
        quantum_state: Optional[QuantumState],
        response_type: str
    ) -> bool:
        """
        Determine if Hamster assistance is needed.
        
        QSP needs Hamsters for:
        - Critical/existential threats
        - Quantum interventions
        - When quantum state is collapsed
        """
        if risk_level in ['critical', 'existential']:
            return True
        
        if response_type == 'quantum_intervention':
            return True
        
        if quantum_state and quantum_state.state == 'collapsed':
            return True
        
        return False
    
    def _determine_message_priority(
        self,
        risk_level: str,
        quantum_state: Optional[QuantumState]
    ) -> str:
        """
        Determine priority of quantum messages to Hamsters.
        """
        if risk_level == 'existential':
            return 'urgent'
        elif risk_level == 'critical':
            return 'high'
        elif quantum_state and quantum_state.state == 'collapsed':
            return 'urgent'
        elif risk_level == 'high':
            return 'normal'
        else:
            return 'low'
    
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
        has_precedent: bool
    ) -> float:
        """
        Calculate reasoning confidence (affected by quantum state).
        """
        confidence = base_confidence
        
        # Quantum state affects confidence
        if quantum_state:
            confidence *= quantum_state.coherence
        
        # Historical precedent boosts confidence
        if has_precedent:
            confidence = min(1.0, confidence + 0.1)
        
        return confidence
