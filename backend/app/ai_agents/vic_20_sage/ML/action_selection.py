#!/usr/bin/env python3
"""
VIC-20's Action Selection Layer - Coordination Routing Decisions

Selects:
- Target specialist for coordination
- Message content and urgency
- Fallback options if primary specialist unavailable
- Coordination strategy

VIC-20's personality is calm, analytical coordination.
"""
import logging
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from .action_effectiveness import ActionEffectivenessModel
from .perception import VIC20PerceptionContext
from .reasoning import CoordinationReasoning

logger = logging.getLogger('VIC20ActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


EXPLORATION_CONFIG = {
    'initial_epsilon': 0.35,
    'min_epsilon': 0.15,
    'decay_rate': 0.998,
}


@dataclass
class CoordinationAction:
    """VIC-20's selected coordination action"""
    
    # Core action
    action_type: str
    target_specialist: str
    
    # Action details
    priority: str
    confidence: float
    
    # Communication
    message_to_specialist: str
    recommended_action: str
    action_parameters: Dict[str, Any]
    
    # Fallback plan
    fallback_specialists: list[str]
    
    # Coordination metadata
    coordination_strategy: str
    exploration: bool = False
    epsilon: float = 0.0
    alternatives_considered: List[str] = field(default_factory=list)


class VIC20ActionSelection:
    """
    VIC-20's action selection layer for coordination routing.
    
    🖥️ "Selecting optimal coordination strategy..."
    """
    
    ACTION_MAP = {
        'critical': ['route_to_primary_specialist', 'escalate_to_human'],
        'high': ['route_to_primary_specialist'],
        'normal': ['route_to_primary_specialist', 'route_to_fallback', 'monitor_resolution'],
    }
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any], system_id: str = "default"):
        self.db = db
        self.personality_traits = personality_traits
        self.system_id = system_id
        
        self.action_effectiveness = ActionEffectivenessModel(
            db_session=db,
            agent_name="vic_20_sage"
        )
        self.epsilon = EXPLORATION_CONFIG['initial_epsilon']
        
    async def select_action(
        self,
        context: VIC20PerceptionContext,
        reasoning: CoordinationReasoning
    ) -> CoordinationAction:
        """
        Select the appropriate coordination action based on reasoning and learned effectiveness.
        """
        logger.info(f"🖥️⚡ Selecting coordination action for {context.resource_type}...")
        
        urgency = reasoning.urgency_level
        viable_actions = self.ACTION_MAP.get(urgency, ['monitor_resolution'])
        
        scored_actions = await self._score_viable_actions(viable_actions, urgency, context)
        
        exploration = False
        if random.random() < self.epsilon and len(viable_actions) > 1:
            exploration = True
            action_type = random.choice([a for a in viable_actions if a != scored_actions[0][0]])
            confidence = 0.3
            logger.info(f"🖥️🎲 Exploring alternative routing: {action_type} over {scored_actions[0][0]}")
        else:
            action_type = scored_actions[0][0]
            confidence = scored_actions[0][1]
            
        self.epsilon = max(
            EXPLORATION_CONFIG['min_epsilon'],
            self.epsilon * EXPLORATION_CONFIG['decay_rate']
        )
        
        priority = self._determine_priority(urgency)
        message = self._build_specialist_message(context, reasoning)
        strategy = self._determine_coordination_strategy(urgency, confidence)
        
        action = CoordinationAction(
            action_type=action_type,
            target_specialist=reasoning.target_specialist,
            priority=priority,
            confidence=confidence,
            message_to_specialist=message,
            recommended_action=reasoning.recommended_action,
            action_parameters=reasoning.action_parameters,
            fallback_specialists=reasoning.alternative_specialists,
            coordination_strategy=strategy,
            exploration=exploration,
            epsilon=self.epsilon,
            alternatives_considered=viable_actions
        )
        
        logger.info(
            f"🖥️✅ Action selected: {action_type} to {reasoning.target_specialist}, "
            f"priority={priority}, strategy={strategy}"
        )
        
        return action
        
    async def _score_viable_actions(self, viable_actions: List[str], urgency: str, context: VIC20PerceptionContext) -> List[tuple[str, float]]:
        """Score actions based on expected effectiveness"""
        scored = []
        try:
            effectiveness_scores = await self.action_effectiveness.score_all_actions(
                root_cause=urgency,
                severity=context.severity
            )
        except Exception as e:
            logger.warning(f"🖥️⚠️ Effectiveness model failed: {e}")
            effectiveness_scores = {}
            
        for action in viable_actions:
            score = effectiveness_scores.get(action, 0.5)
            
            # Contextual modifiers
            if action == 'escalate_to_human' and urgency == 'critical':
                score += 0.2
            elif action == 'route_to_fallback' and context.hawk_confidence < 0.5:
                # Fallback if Hawk isn't confident
                score += 0.1
                
            score = max(0.1, min(0.99, score))
            scored.append((action, score))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _determine_priority(self, urgency: str) -> str:
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
        if urgency == 'critical':
            return 'broadcast'
        elif confidence > 0.8:
            return 'direct'
        else:
            return 'sequential'
