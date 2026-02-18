#!/usr/bin/env python3
"""
QSP (Quantum Shadow People) Action Selection Layer - Quantum Security Response

Selects:
- Security response action based on quantum reasoning
- Exploration vs Exploitation (epsilon-greedy)
- Adaptive throttle bias (learns when throttling is actually needed)
- Monitoring/blocking/escalation strategy
- Quantum message transmission to Hamsters
- Existential dread management

Personality behaviors integrated:
- Quantum state tracked and reported
- Existential dread levels included
- Hamster communication protocol
"""
import logging
import random
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
    
    # Map security threats to viable actions
    # QSP handles: Network security and monitoring
    ACTION_MAP = {
        # === TRAFFIC ISSUES ===
        'high_traffic': [
            'monitor',              # Just watch first
            'analyze_traffic',      # Analyze patterns
            'rate_limit',           # Apply rate limiting
            'throttle_network',     # Throttle if needed
        ],
        'ddos_attack': [
            'rate_limit',           # Rate limit immediately
            'block',                # Block attacking IPs
            'update_firewall_rules', # Update firewall
            'escalate',             # Get help
        ],
        'bandwidth_saturation': [
            'throttle_network',     # Throttle bandwidth
            'rate_limit',           # Limit connections
            'close_suspicious_connections', # Close heavy users
            'analyze_traffic',      # Find the hog
        ],
        
        # === SECURITY THREATS ===
        'suspicious_activity': [
            'investigate',          # Analyze first
            'scan_ports',           # Check for vulnerabilities
            'monitor',              # Watch closely
            'block',                # Block if confirmed
        ],
        'intrusion_attempt': [
            'block',                # Block immediately
            'update_firewall_rules', # Update firewall
            'scan_ports',           # Check vulnerabilities
            'escalate',             # Alert coordination
        ],
        'brute_force_attack': [
            'block',                # Block attacker
            'rate_limit',           # Limit auth attempts
            'update_firewall_rules', # Add firewall rules
            'escalate',             # Alert coordination
        ],
        'port_scan_detected': [
            'block',                # Block scanner
            'update_firewall_rules', # Close unnecessary ports
            'investigate',          # Analyze intent
            'monitor',              # Watch for more
        ],
        'unauthorized_access': [
            'block',                # Block immediately
            'close_suspicious_connections', # Kill sessions
            'update_firewall_rules', # Lock down
            'escalate',             # Critical alert
        ],
        
        # === ANOMALIES ===
        'network_anomaly': [
            'investigate',          # Analyze anomaly
            'analyze_traffic',      # Check patterns
            'quantum_scan',         # Quantum-level scan
            'monitor',              # Observe
        ],
        'quantum_fluctuation': [
            'quantum_scan',         # QSP's specialty
            'investigate',          # Deep analysis
            'monitor',              # Watch quantum state
            'escalate',             # May need help
        ],
        
        # === NORMAL OPERATIONS ===
        'normal_operations': [
            'monitor',              # Just observe
            'scan_ports',           # Periodic security check
        ],
        'preventive_scan': [
            'scan_ports',           # Check vulnerabilities
            'quantum_scan',         # Quantum check
            'analyze_traffic',      # Baseline traffic
            'monitor',              # Passive monitoring
        ],
        
        # === UNKNOWN/UNCERTAIN ===
        'unknown': [
            'monitor',              # Observe first
            'investigate',          # Analyze
            'quantum_scan',         # Quantum analysis
            'escalate',             # Ask for help
        ],
        'insufficient_data': [
            'monitor',              # Gather more data
            'analyze_traffic',      # Collect baseline
            'escalate',             # Ask VIC-20 for guidance
        ],
    }
    
    def __init__(self, personality_traits: Dict[str, Any], db=None, system_id: str = "default"):
        self.personality_traits = personality_traits
        self.db = db
        self.system_id = system_id
        
        # Learned thresholds and action effectiveness (initialized lazily)
        self.learned_thresholds = None
        self.action_effectiveness = None
        
        # Initialize learning systems if db available
        if self.db:
            from .learned_thresholds import LearnedThresholds
            from .action_effectiveness import ActionEffectivenessModel
            
            self.learned_thresholds = LearnedThresholds(db, system_id)
            self.action_effectiveness = ActionEffectivenessModel(db, system_id)
            logger.info("👻🧠 Learned thresholds and action effectiveness enabled!")
        
        # Exploration vs Exploitation
        self.epsilon = 0.15  # 15% chance to explore (try non-preferred actions)
        self.min_epsilon = 0.05  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Decay exploration over time
        
        # Adaptive throttle bias (starts high, decreases if throttle not effective)
        self.throttle_bias = 1.2  # 20% bias toward throttle (QSP's paranoia!)
        self.throttle_successes = 0
        self.throttle_attempts = 0
        
        logger.info("👻⚡ QSP's action selection initialized!")
        logger.info(f"👻🔬 Exploration rate: {self.epsilon:.1%}, Throttle bias: {self.throttle_bias:.2f}")
        
    async def select_action(
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
        
        # If action effectiveness model available, use learned scores
        if self.action_effectiveness:
            metric_pattern = self.action_effectiveness._generate_pattern_fingerprint(
                {
                    'threat_count': context.threat_count,
                    'failed_auth_attempts': context.failed_auth_attempts,
                    'network_anomalies': context.network_anomalies
                },
                context.severity
            )
            action_scores = await self.action_effectiveness.score_all_actions(metric_pattern)
            
            # Use learned best action if confidence is high enough
            if action_scores and action_scores[0].confidence > 0.5:
                action_type = action_scores[0].action
                logger.info(
                    f"👻🧠 Using learned best action: {action_type} "
                    f"(score={action_scores[0].score:.2f}, confidence={action_scores[0].confidence:.2f})"
                )
        
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
    
    def update_throttle_bias(self, action: str, success: bool):
        """
        Update QSP's throttle bias based on outcomes.
        
        If throttle keeps failing or isn't needed, reduce the bias.
        If other actions work better, reduce the bias.
        
        Args:
            action: Action that was executed
            success: Whether it succeeded
        """
        if 'throttle' in action:
            self.throttle_attempts += 1
            if success:
                self.throttle_successes += 1
            
            # Calculate success rate
            success_rate = self.throttle_successes / self.throttle_attempts
            
            # Adjust bias based on success rate
            if success_rate < 0.6:
                self.throttle_bias = max(1.0, self.throttle_bias * 0.95)
                logger.info(
                    f"👻📉 Throttle success rate low ({success_rate:.1%}) - "
                    f"reducing bias to {self.throttle_bias:.2f}"
                )
            elif success_rate > 0.8 and self.throttle_bias < 1.2:
                self.throttle_bias = min(1.2, self.throttle_bias * 1.02)
                logger.debug(f"👻📈 Throttle working well - bias: {self.throttle_bias:.2f}")
        
        elif success:
            # Other action succeeded - slightly reduce throttle bias
            # (QSP learns there are other good options)
            self.throttle_bias = max(1.0, self.throttle_bias * 0.98)
            logger.debug(
                f"👻💡 {action} worked! Learning alternatives exist. "
                f"Throttle bias: {self.throttle_bias:.2f}"
            )
    
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
            # Monitoring actions
            'monitor': 60,
            'investigate': 30,
            'scan_ports': 20,
            'analyze_traffic': 25,
            'quantum_scan': 15,
            
            # Defensive actions
            'throttle_network': 10,
            'rate_limit': 8,
            'close_suspicious_connections': 5,
            
            # Aggressive actions
            'block': 5,
            'update_firewall_rules': 12,
            
            # Learning actions
            'escalate': 10,
            'quantum_intervention': 15
        }
        
        base = base_times.get(action_type, 30)
        
        # Critical situations take less time (more urgent)
        if risk_level in ['critical', 'existential']:
            base = int(base * 0.5)
        
        return base
