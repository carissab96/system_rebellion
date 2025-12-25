#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Action Selection Layer - Quantum Security Response

Selects:
- Security response action based on quantum reasoning
- Monitoring/blocking/escalation strategy
- Quantum message transmission to Hamsters
- Existential dread management

Personality behaviors integrated:
- Quantum state tracked and reported
- Existential dread levels included
- Hamster communication protocol
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import QSPPerceptionContext, QuantumState, QuantumMessage
from .reasoning import SecurityReasoning

logger = logging.getLogger('QSPActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class SecurityResponseAction:
    """QSP's selected security response action"""
    
    # Core action
    action_type: str  # 'monitor', 'investigate', 'block', 'escalate', 'quantum_intervention'
    response_strategy: str
    
    # Action details
    priority: str  # 'low', 'normal', 'high', 'urgent'
    confidence: float
    
    # Quantum state (personality)
    quantum_state: str
    existential_dread_level: float
    quantum_coherence: float
    
    # Hamster communication
    quantum_messages_sent: int
    hamster_assistance_requested: bool
    message_priority: str
    
    # Execution parameters
    immediate_action: bool
    requires_escalation: bool
    estimated_resolution_time: int  # minutes


class QSPActionSelection:
    """
    QSP's action selection layer for security responses.
    
    👻 "Selecting quantum response... *existential dread at {level}*"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
    def select_action(
        self,
        context: QSPPerceptionContext,
        reasoning: SecurityReasoning
    ) -> SecurityResponseAction:
        """
        Select security response action based on quantum reasoning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            
        Returns:
            SecurityResponseAction with quantum state details
        """
        logger.info(f"👻⚡ Selecting quantum security response...")
        
        # Determine action type
        action_type = reasoning.response_type
        
        # Determine priority
        priority = self._determine_priority(reasoning.risk_level, context.response_urgency)
        
        # Check if immediate action required
        immediate = self._requires_immediate_action(reasoning.risk_level, action_type)
        
        # Check if escalation required
        escalation = self._requires_escalation(
            reasoning.risk_level,
            reasoning.requires_hamster_assistance
        )
        
        # Estimate resolution time
        resolution_time = self._estimate_resolution_time(action_type, reasoning.risk_level)
        
        # Get quantum state details
        quantum_state = context.quantum_state.state if context.quantum_state else 'unknown'
        existential_dread = context.existential_dread
        coherence = context.quantum_state.coherence if context.quantum_state else 1.0
        
        action = SecurityResponseAction(
            action_type=action_type,
            response_strategy=reasoning.recommended_response,
            priority=priority,
            confidence=reasoning.confidence,
            quantum_state=quantum_state,
            existential_dread_level=existential_dread,
            quantum_coherence=coherence,
            quantum_messages_sent=len(context.quantum_messages),
            hamster_assistance_requested=reasoning.requires_hamster_assistance,
            message_priority=reasoning.quantum_message_priority,
            immediate_action=immediate,
            requires_escalation=escalation,
            estimated_resolution_time=resolution_time
        )
        
        logger.info(
            f"👻✅ Action selected: {action_type}, "
            f"priority={priority}, quantum_state={quantum_state}, "
            f"dread={existential_dread:.2f}"
        )
        
        if reasoning.requires_hamster_assistance:
            logger.info(
                f"👻📡 Hamster assistance requested - "
                f"{len(context.quantum_messages)} quantum messages prepared"
            )
        
        return action
    
    def _determine_priority(self, risk_level: str, urgency: float) -> str:
        """
        Determine action priority level.
        """
        if risk_level == 'existential':
            return 'urgent'
        elif risk_level == 'critical':
            return 'urgent'
        elif risk_level == 'high' or urgency > 0.7:
            return 'high'
        elif risk_level == 'moderate':
            return 'normal'
        else:
            return 'low'
    
    def _requires_immediate_action(self, risk_level: str, action_type: str) -> bool:
        """
        Determine if immediate action is required.
        """
        if risk_level in ['critical', 'existential']:
            return True
        
        if action_type in ['block', 'quantum_intervention']:
            return True
        
        return False
    
    def _requires_escalation(
        self,
        risk_level: str,
        hamster_assistance: bool
    ) -> bool:
        """
        Determine if escalation is required.
        """
        if risk_level in ['critical', 'existential']:
            return True
        
        if hamster_assistance:
            return True
        
        return False
    
    def _estimate_resolution_time(self, action_type: str, risk_level: str) -> int:
        """
        Estimate resolution time in minutes.
        """
        base_times = {
            'monitor': 60,
            'investigate': 30,
            'block': 5,
            'escalate': 10,
            'quantum_intervention': 15
        }
        
        base = base_times.get(action_type, 30)
        
        # Critical situations take less time (more urgent)
        if risk_level in ['critical', 'existential']:
            base = int(base * 0.5)
        
        return base
