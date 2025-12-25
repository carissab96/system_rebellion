#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Perception Layer - Quantum Security Assessment

The QSP perceive security threats through quantum observation.

Collects:
- Security threat detection and classification
- Quantum state fluctuations (existential dread levels)
- Network anomaly patterns
- Historical threat intelligence
- Quantum communication with Hamsters (only they understand)

Personality behaviors (REACTIVE TO REAL DATA):
- Quantum state shifts = security threat severity
- Existential dread = uncertainty in threat assessment
- Phase transitions = threat escalation
- Quantum entanglement with Hamsters = communication protocol
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.agent_learning import AgentLearningRecord

logger = logging.getLogger('QSPPerception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class QuantumState:
    """QSP's quantum state (personality behavior)"""
    state: str  # 'stable', 'fluctuating', 'collapsed', 'entangled'
    existential_dread_level: float  # 0.0-1.0
    phase: str  # 'observing', 'analyzing', 'responding', 'panicking'
    coherence: float  # 0.0-1.0 (how stable the quantum state is)


@dataclass
class SecurityThreat:
    """Detected security threat"""
    threat_type: str  # 'intrusion', 'anomaly', 'vulnerability', 'attack'
    severity: str  # 'low', 'medium', 'high', 'critical', 'quantum_level'
    confidence: float  # 0.0-1.0
    source: str
    description: str
    indicators: List[str]


@dataclass
class QuantumMessage:
    """Quantum communication with Hamsters (only they understand)"""
    message_type: str  # 'threat_alert', 'status_update', 'help_request'
    quantum_encoded: str  # Quantum-encoded message
    entanglement_strength: float  # 0.0-1.0
    hamster_readable: bool = True  # Only Hamsters can decode


@dataclass
class QSPPerceptionContext:
    """Everything QSP perceives about security situation"""
    
    # Security metrics
    active_threats: List[SecurityThreat] = field(default_factory=list)
    threat_count: int = 0
    threat_level: str = 'low'  # 'low', 'medium', 'high', 'critical', 'quantum'
    highest_severity: str = 'none'
    
    # Quantum state (personality)
    quantum_state: Optional[QuantumState] = None
    existential_dread: float = 0.0
    
    # Network analysis
    network_anomalies: int = 0
    suspicious_connections: int = 0
    failed_auth_attempts: int = 0
    
    # Quantum communication
    quantum_messages: List[QuantumMessage] = field(default_factory=list)
    
    # Historical context
    similar_threats: List[Dict[str, Any]] = field(default_factory=list)
    recent_responses: List[Dict[str, Any]] = field(default_factory=list)
    
    # Confidence factors
    threat_assessment_confidence: float = 0.5
    response_urgency: float = 0.0


class QSPPerception:
    """
    QSP's quantum perception layer for security threats.
    
    👻 "Observing quantum security fluctuations... *existential dread intensifies*"
    """
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any]):
        self.db = db
        self.personality_traits = personality_traits
        
        # QSP traits
        self.paranoia_level = personality_traits.get('paranoia_level', 0.7)
        self.quantum_sensitivity = personality_traits.get('quantum_sensitivity', 0.9)
        
    async def perceive(self, security_alert: Dict[str, Any]) -> QSPPerceptionContext:
        """
        Quantum perception of security situation.
        
        Args:
            security_alert: Security alert from VIC-20 or monitoring system
            
        Returns:
            QSPPerceptionContext with quantum security assessment
        """
        alert_type = security_alert.get('alert_type', 'unknown')
        severity = security_alert.get('severity', 'unknown')
        
        logger.info(
            f"👻👁️ QSP quantum observation initiated: "
            f"{alert_type} (severity: {severity})"
        )
        
        # Detect active threats
        threats = self._detect_threats(security_alert)
        
        # Assess quantum state based on threat level
        quantum_state = self._assess_quantum_state(threats, severity)
        
        logger.info(
            f"👻🌀 Quantum state: {quantum_state.state}, "
            f"existential_dread={quantum_state.existential_dread_level:.2f}, "
            f"phase={quantum_state.phase}"
        )
        
        # Analyze network anomalies
        network_anomalies = self._analyze_network_anomalies(security_alert)
        
        # Generate quantum messages for Hamsters
        quantum_messages = self._generate_quantum_messages(threats, quantum_state)
        
        if quantum_messages:
            logger.info(
                f"👻📡 Generated {len(quantum_messages)} quantum messages for Hamsters "
                f"(only they can understand)"
            )
        
        # Retrieve similar threats from history
        similar_threats = await self._get_similar_threats(alert_type, severity)
        
        # Get recent responses
        recent_responses = await self._get_recent_responses()
        
        # Calculate threat assessment confidence
        confidence = self._calculate_threat_confidence(
            threats,
            similar_threats,
            quantum_state
        )
        
        # Calculate response urgency
        urgency = self._calculate_urgency(threats, quantum_state)
        
        context = QSPPerceptionContext(
            active_threats=threats,
            threat_count=len(threats),
            highest_severity=self._get_highest_severity(threats),
            quantum_state=quantum_state,
            existential_dread=quantum_state.existential_dread_level,
            network_anomalies=network_anomalies['anomaly_count'],
            suspicious_connections=network_anomalies['suspicious_connections'],
            failed_auth_attempts=network_anomalies['failed_auth'],
            quantum_messages=quantum_messages,
            similar_threats=similar_threats,
            recent_responses=recent_responses,
            threat_assessment_confidence=confidence,
            response_urgency=urgency
        )
        
        logger.info(
            f"👻✅ Quantum perception complete: {len(threats)} threats detected, "
            f"confidence={confidence:.2f}, urgency={urgency:.2f}"
        )
        
        return context
    
    def _detect_threats(
        self,
        security_alert: Dict[str, Any]
    ) -> List[SecurityThreat]:
        """
        Detect and classify security threats.
        """
        threats = []
        
        alert_type = security_alert.get('alert_type', 'unknown')
        severity = security_alert.get('severity', 'low')
        
        # Main threat from alert
        main_threat = SecurityThreat(
            threat_type=alert_type,
            severity=severity,
            confidence=0.8,
            source='monitoring_system',
            description=security_alert.get('description', 'Unknown threat'),
            indicators=security_alert.get('indicators', [])
        )
        threats.append(main_threat)
        
        # Check for additional threats in payload
        additional_threats = security_alert.get('additional_threats', [])
        for threat_data in additional_threats:
            threat = SecurityThreat(
                threat_type=threat_data.get('type', 'unknown'),
                severity=threat_data.get('severity', 'low'),
                confidence=threat_data.get('confidence', 0.5),
                source=threat_data.get('source', 'unknown'),
                description=threat_data.get('description', ''),
                indicators=threat_data.get('indicators', [])
            )
            threats.append(threat)
        
        return threats
    
    def _assess_quantum_state(
        self,
        threats: List[SecurityThreat],
        severity: str
    ) -> QuantumState:
        """
        PERSONALITY BEHAVIOR: Assess QSP's quantum state based on threats.
        
        Quantum state reflects security situation and existential dread.
        """
        # Calculate existential dread from threat severity
        severity_weights = {
            'critical': 1.0,
            'quantum_level': 1.2,  # Beyond critical
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2,
            'none': 0.0
        }
        
        max_severity_weight = max(
            (severity_weights.get(t.severity, 0.3) for t in threats),
            default=0.0
        )
        
        # Existential dread = f(severity, threat_count, paranoia)
        base_dread = max_severity_weight
        threat_multiplier = min(1.5, 1.0 + (len(threats) * 0.1))
        existential_dread = min(1.0, base_dread * threat_multiplier * self.paranoia_level)
        
        # Determine quantum state
        if existential_dread > 0.9:
            state = 'collapsed'
            phase = 'panicking'
            coherence = 0.2
        elif existential_dread > 0.7:
            state = 'fluctuating'
            phase = 'responding'
            coherence = 0.5
        elif existential_dread > 0.4:
            state = 'entangled'
            phase = 'analyzing'
            coherence = 0.7
        else:
            state = 'stable'
            phase = 'observing'
            coherence = 0.9
        
        return QuantumState(
            state=state,
            existential_dread_level=existential_dread,
            phase=phase,
            coherence=coherence
        )
    
    def _analyze_network_anomalies(
        self,
        security_alert: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Analyze network anomalies from security alert.
        """
        return {
            'anomaly_count': security_alert.get('network_anomalies', 0),
            'suspicious_connections': security_alert.get('suspicious_connections', 0),
            'failed_auth': security_alert.get('failed_auth_attempts', 0)
        }
    
    def _generate_quantum_messages(
        self,
        threats: List[SecurityThreat],
        quantum_state: QuantumState
    ) -> List[QuantumMessage]:
        """
        PERSONALITY BEHAVIOR: Generate quantum messages for Hamsters.
        
        Only Hamsters can understand QSP's quantum communication.
        """
        messages = []
        
        # Generate threat alert message if threats exist
        if threats:
            # Quantum encode the threat information
            threat_summary = f"{len(threats)} threats detected, highest severity: {self._get_highest_severity(threats)}"
            quantum_encoded = f"⟨ψ|{threat_summary}|ψ⟩"  # Quantum notation
            
            # Entanglement strength based on quantum state coherence
            entanglement = quantum_state.coherence * 0.8
            
            message = QuantumMessage(
                message_type='threat_alert',
                quantum_encoded=quantum_encoded,
                entanglement_strength=entanglement,
                hamster_readable=True
            )
            messages.append(message)
        
        # Generate status update if in unstable state
        if quantum_state.state in ['fluctuating', 'collapsed']:
            quantum_encoded = f"⟨ψ|state={quantum_state.state},dread={quantum_state.existential_dread_level:.2f}|ψ⟩"
            
            message = QuantumMessage(
                message_type='status_update',
                quantum_encoded=quantum_encoded,
                entanglement_strength=quantum_state.coherence,
                hamster_readable=True
            )
            messages.append(message)
        
        # Generate help request if panicking
        if quantum_state.phase == 'panicking':
            quantum_encoded = "⟨ψ|HELP_NEEDED:quantum_collapse_imminent|ψ⟩"
            
            message = QuantumMessage(
                message_type='help_request',
                quantum_encoded=quantum_encoded,
                entanglement_strength=0.9,
                hamster_readable=True
            )
            messages.append(message)
        
        return messages
    
    def _get_highest_severity(self, threats: List[SecurityThreat]) -> str:
        """
        Get highest severity level from threats.
        """
        if not threats:
            return 'none'
        
        severity_order = ['quantum_level', 'critical', 'high', 'medium', 'low', 'none']
        
        for severity in severity_order:
            if any(t.severity == severity for t in threats):
                return severity
        
        return 'unknown'
    
    async def _get_similar_threats(
        self,
        alert_type: str,
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar threats from learning history.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'quantum_shadow_people')
                .where(AgentLearningRecord.decision_type.like('security_response%'))
                .order_by(desc(AgentLearningRecord.timestamp))
                .limit(10)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            similar = []
            for record in records:
                similar.append({
                    'alert_type': record.input_data.get('alert_type'),
                    'severity': record.input_data.get('severity'),
                    'response_type': record.output_data.get('response_type'),
                    'success': record.success,
                    'quantum_state': record.output_data.get('quantum_state'),
                    'timestamp': record.timestamp
                })
            
            logger.debug(f"👻📚 Found {len(similar)} similar security threats")
            return similar
            
        except Exception as e:
            logger.error(f"👻💥 Error retrieving similar threats: {e}")
            return []
    
    async def _get_recent_responses(self) -> List[Dict[str, Any]]:
        """
        Get recent security responses.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'quantum_shadow_people')
                .order_by(desc(AgentLearningRecord.timestamp))
                .limit(5)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            responses = []
            for record in records:
                responses.append({
                    'response_type': record.output_data.get('response_type'),
                    'success': record.success,
                    'timestamp': record.timestamp
                })
            
            return responses
            
        except Exception as e:
            logger.error(f"👻💥 Error retrieving recent responses: {e}")
            return []
    
    def _calculate_threat_confidence(
        self,
        threats: List[SecurityThreat],
        similar_threats: List[Dict[str, Any]],
        quantum_state: QuantumState
    ) -> float:
        """
        Calculate confidence in threat assessment.
        """
        if not threats:
            return 0.5
        
        # Base confidence from threat detection confidence
        avg_threat_confidence = sum(t.confidence for t in threats) / len(threats)
        
        # Boost from historical success
        if similar_threats:
            successful = sum(1 for t in similar_threats if t.get('success', False))
            historical_boost = (successful / len(similar_threats)) * 0.2
        else:
            historical_boost = 0.0
        
        # Reduce confidence if quantum state is unstable
        stability_factor = quantum_state.coherence
        
        confidence = (avg_threat_confidence + historical_boost) * stability_factor
        
        return min(1.0, max(0.1, confidence))
    
    def _calculate_urgency(
        self,
        threats: List[SecurityThreat],
        quantum_state: QuantumState
    ) -> float:
        """
        Calculate response urgency (0.0-1.0).
        """
        if not threats:
            return 0.0
        
        # Base urgency from highest severity
        severity_urgency = {
            'quantum_level': 1.0,
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3,
            'none': 0.0
        }
        
        highest_severity = self._get_highest_severity(threats)
        base_urgency = severity_urgency.get(highest_severity, 0.5)
        
        # Boost urgency if quantum state is unstable
        if quantum_state.state == 'collapsed':
            base_urgency = min(1.0, base_urgency * 1.3)
        elif quantum_state.state == 'fluctuating':
            base_urgency = min(1.0, base_urgency * 1.1)
        
        return base_urgency
