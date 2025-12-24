#!/usr/bin/env python3
"""
VIC-20's Action Selection Layer - Coordination Routing Decisions

Selects:
- Target specialist for coordination
- Message content and urgency
- Fallback options if primary specialist unavailable
- Coordination strategy

VIC-20's personality is calm, analytical coordination.
No dramatic behaviors - just solid routing decisions.
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import VIC20PerceptionContext
from .reasoning import CoordinationReasoning

logger = logging.getLogger('VIC20ActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class CoordinationAction:
    """VIC-20's selected coordination action"""
    
    # Core action
    action_type: str  # 'route_to_specialist', 'escalate', 'monitor'
    target_specialist: str
    
    # Action details
    priority: str  # 'low', 'normal', 'high', 'critical'
    confidence: float
    
    # Communication
    message_to_specialist: str
    recommended_action: str
    action_parameters: Dict[str, Any]
    
    # Fallback plan
    fallback_specialists: list[str]
    
    # Coordination metadata
    coordination_strategy: str  # 'direct', 'broadcast', 'sequential'


class VIC20ActionSelection:
    """
    VIC-20's action selection layer for coordination routing.
    
    🖥️ "Selecting optimal coordination strategy..."
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
    def select_action(
        self,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning
    ) -> CoordinationAction:
        """
        Select the appropriate coordination action based on reasoning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            
        Returns:
            CoordinationAction with selected action and details
        """
        logger.info(f"🖥️⚡ Selecting coordination action for {context.resource_type}...")
        
        # Determine action type
        action_type = self._determine_action_type(reasoning)
        
        # Determine priority
        priority = self._determine_priority(reasoning.urgency_level)
        
        # Build message to specialist
        message = self._build_specialist_message(context, reasoning)
        
        # Determine coordination strategy
        strategy = self._determine_coordination_strategy(
            reasoning.urgency_level,
            reasoning.routing_confidence
        )
        
        action = CoordinationAction(
            action_type=action_type,
            target_specialist=reasoning.target_specialist,
            priority=priority,
            confidence=reasoning.routing_confidence,
            message_to_specialist=message,
            recommended_action=reasoning.recommended_action,
            action_parameters=reasoning.action_parameters,
            fallback_specialists=reasoning.alternative_specialists,
            coordination_strategy=strategy
        )
        
        logger.info(
            f"🖥️✅ Action selected: {action_type} to {reasoning.target_specialist}, "
            f"priority={priority}, strategy={strategy}"
        )
        
        return action
    
    def _determine_action_type(self, reasoning: CoordinationReasoning) -> str:
        """
        Determine the type of coordination action to take.
        """
        if reasoning.routing_confidence > 0.6:
            return 'route_to_specialist'
        elif reasoning.urgency_level == 'critical':
            return 'escalate'
        else:
            return 'monitor'
    
    def _determine_priority(self, urgency: str) -> str:
        """
        Determine action priority level.
        """
        priority_map = {
            'critical': 'critical',
            'high': 'high',
            'normal': 'normal'
        }
        return priority_map.get(urgency, 'normal')
    
    def _build_specialist_message(
        self,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning
    ) -> str:
        """
        Build coordination message to specialist.
        
        🖥️ VIC-20's messages are clear and data-driven.
        """
        message = (
            f"Coordination request from VIC-20: {context.resource_type.upper()} "
            f"at {context.current_value:.1f}% (threshold: {context.threshold:.1f}%). "
        )
        
        if reasoning.urgency_level == 'critical':
            message += "CRITICAL urgency - immediate action required. "
        elif reasoning.urgency_level == 'high':
            message += "High priority - prompt attention needed. "
        
        message += (
            f"Recommended action: {reasoning.recommended_action}. "
            f"Sir Hawkington's assessment: severity={context.severity}, "
            f"confidence={context.hawk_confidence:.2f}. "
        )
        
        if reasoning.specialist_success_rate > 0.8:
            message += (
                f"Your recent success rate for this resource type is {reasoning.specialist_success_rate:.1%}. "
            )
        
        if reasoning.alternative_specialists:
            message += f"Fallback options: {', '.join(reasoning.alternative_specialists)}. "
        
        return message
    
    def _determine_coordination_strategy(
        self,
        urgency: str,
        confidence: float
    ) -> str:
        """
        Determine coordination strategy.
        """
        if urgency == 'critical':
            return 'broadcast'  # Alert multiple specialists
        elif confidence > 0.8:
            return 'direct'  # Direct to best specialist
        else:
            return 'sequential'  # Try specialists in order
