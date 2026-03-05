#!/usr/bin/env python3
"""
Sir Hawkington's Action Selection Layer - Aristocratic Decision Making

Selects:
- Whether to escalate to VIC-20 or handle locally
- Target specialist for coordination
- Urgency and priority levels
- Communication strategy

Personality Behaviors:
- Monocle polishing when confident
- Aristocratic tone in communications
"""
import logging
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learned_thresholds import ActionEffectivenessModel
from .perception import HawkPerceptionContext
from .reasoning import TriageReasoning

logger = logging.getLogger('HawkActionSelection')

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
class TriageAction:
    """Sir Hawkington's selected triage action"""
    
    # Core action
    action_type: str  # 'escalate', 'monitor', 'dismiss'
    target_agent: Optional[str]
    
    # Action details
    priority: str  # 'low', 'normal', 'high', 'critical'
    confidence: float
    
    # Communication
    message_to_vic20: Optional[str]
    reasoning_summary: str
    
    # Personality state
    monocle_state: str  # 'polished', 'adjusting', 'yeeted'
    aristocratic_confidence: float
    
    # ML Tracking
    exploration: bool = False
    epsilon: float = 0.0
    alternatives_considered: List[str] = field(default_factory=list)


class HawkActionSelection:
    """
    Sir Hawkington's action selection layer.
    
    🧐 "One must select the proper course of action with aristocratic precision!"
    """
    
    ACTION_MAP = {
        'critical': ['escalate'],
        'high': ['escalate', 'monitor'],
        'medium': ['monitor', 'escalate', 'dismiss'],
        'low': ['dismiss', 'monitor'],
    }
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any], system_id: str = "default"):
        self.db = db
        self.personality_traits = personality_traits
        self.system_id = system_id
        self.current_monocle_state = 'polished'
        
        self.action_effectiveness = ActionEffectivenessModel(
            db=db,
            system_id=self.system_id,
            agent_name="sir_hawkington"
        )
        self.epsilon = EXPLORATION_CONFIG['initial_epsilon']
        
    async def select_action(
        self,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning
    ) -> TriageAction:
        """
        Select the appropriate triage action based on reasoning and learned effectiveness.
        """
        logger.info(f"🧐⚡ Selecting action for {context.resource_type} triage...")
        
        # 1) Determine viable actions purely from Action Map
        risk_level = reasoning.risk_level
        viable_actions = self.ACTION_MAP.get(risk_level, ['monitor'])
        
        # 2) Score them via EventEffectivenessModel
        scored_actions = await self._score_viable_actions(viable_actions, risk_level, context)
        
        # 3) Select action (Epsilon-greedy)
        exploration = False
        if random.random() < self.epsilon and len(viable_actions) > 1:
            exploration = True
            action_type = random.choice([a for a in viable_actions if a != scored_actions[0][0]])
            confidence = 0.3  # Low confidence for random exploration
            logger.info(f"🧐🎲 Aristocratic curiosity — exploring {action_type} over {scored_actions[0][0]}")
        else:
            action_type = scored_actions[0][0]
            confidence = scored_actions[0][1]
            
        # Update exploration decay for next time (in-memory for now)
        self.epsilon = max(
            EXPLORATION_CONFIG['min_epsilon'],
            self.epsilon * EXPLORATION_CONFIG['decay_rate']
        )
        
        # Select target agent
        target_agent = reasoning.target_specialist if action_type == 'escalate' else None
        
        # Determine priority based on action and reasoning urgency
        priority = self._determine_priority(reasoning)
        
        # Update monocle state based on data quality and confidence
        self._update_monocle_state(context.data_quality_score, confidence)
        
        # Calculate aristocratic confidence (personality-adjusted)
        aristocratic_confidence = self._calculate_aristocratic_confidence(
            confidence,
            context.data_quality_score,
            context.monocle_yeet_count
        )
        
        # Build message to VIC-20
        message_to_vic20 = self._build_escalation_message(
            context,
            reasoning
        ) if action_type == 'escalate' else None
        
        # Build reasoning summary
        reasoning_summary = self._build_reasoning_summary(reasoning)
        
        action = TriageAction(
            action_type=action_type,
            target_agent=target_agent,
            priority=priority,
            confidence=aristocratic_confidence,
            message_to_vic20=message_to_vic20,
            reasoning_summary=reasoning_summary,
            monocle_state=self.current_monocle_state,
            aristocratic_confidence=aristocratic_confidence,
            exploration=exploration,
            epsilon=self.epsilon,
            alternatives_considered=viable_actions
        )
        
        logger.info(
            f"🧐✅ Action selected: {action_type} to {target_agent or 'none'}, "
            f"priority={priority}, monocle={self.current_monocle_state}"
        )
        
        return action
        
    async def _score_viable_actions(self, viable_actions: List[str], risk_level: str, context: HawkPerceptionContext) -> List[tuple[str, float]]:
        """Score actions based on expected effectiveness"""
        scored = []
        
        try:
            effectiveness_scores = await self.action_effectiveness.score_all_actions(
                root_cause=risk_level,
                severity=context.severity
            )
        except Exception as e:
            logger.warning(f"🧐⚠️ Effectiveness model failed, falling back to basic scoring: {e}")
            effectiveness_scores = {}
            
        for action in viable_actions:
            score = effectiveness_scores.get(action, 0.5)
            
            # Contextual modifiers
            if action == 'escalate' and risk_level == 'critical':
                score += 0.3
            elif action == 'dismiss' and context.data_quality_score < 0.5:
                # Never confidently dismiss if data is trash
                score -= 0.4
                
            score = max(0.1, min(0.99, score))
            scored.append((action, score))
            
        # Sort descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _determine_priority(self, reasoning: TriageReasoning) -> str:
        """
        Determine action priority level.
        """
        if reasoning.coordination_urgency == 'critical':
            return 'critical'
        elif reasoning.coordination_urgency == 'high':
            return 'high'
        elif reasoning.risk_level == 'medium':
            return 'normal'
        else:
            return 'low'
    
    def _update_monocle_state(self, data_quality: float, confidence: float):
        """
        Update Sir Hawkington's monocle state based on situation.
        
        🧐 *adjusts monocle with aristocratic precision*
        """
        if data_quality < 0.5:
            self.current_monocle_state = 'yeeted'
            logger.warning("🧐💥 Monocle yeeted due to poor data quality!")
        elif confidence < 0.6:
            self.current_monocle_state = 'adjusted'
            logger.info("🧐🔧 Adjusting monocle - confidence needs improvement")
        else:
            self.current_monocle_state = 'polished'
            logger.debug("🧐✨ Monocle polished and ready")
    
    def _calculate_aristocratic_confidence(
        self,
        base_confidence: float,
        data_quality: float,
        monocle_yeets: int
    ) -> float:
        """
        Adjust confidence based on Sir Hawkington's aristocratic standards.
        
        🧐 "One's confidence must be tempered by the quality of one's data!"
        """
        confidence = base_confidence
        confidence -= (monocle_yeets * 0.05)
        if data_quality > 0.9:
            confidence += 0.1
        confidence *= 0.95
        return max(0.0, min(1.0, confidence))
    
    def _build_escalation_message(
        self,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning
    ) -> str:
        """
        Build aristocratic message to VIC-20.
        """
        message = (
            f"My dear VIC-20, I must bring to your attention a matter of some urgency. "
            f"The {context.resource_type.upper()} has reached {context.current_value:.1f}%, "
            f"which exceeds our threshold of {context.threshold:.1f}%. "
        )
        
        if reasoning.risk_level == 'critical':
            message += "This is a CRITICAL situation requiring immediate specialist attention. "
        elif reasoning.risk_level == 'high':
            message += "This warrants prompt specialist attention. "
        
        message += (
            f"I recommend routing to {reasoning.target_specialist} "
            f"with {reasoning.coordination_urgency} priority. "
        )
        
        if context.monocle_yeet_count > 0:
            message += f"(Note: {context.monocle_yeet_count} monocle yeet(s) during assessment - data quality concerns) "
        
        message += "Yours in vigilance, Sir Hawkington."
        
        return message
    
    def _build_reasoning_summary(self, reasoning: TriageReasoning) -> str:
        """
        Build concise reasoning summary.
        """
        summary = f"{reasoning.primary_reason}. "
        
        if reasoning.contributing_factors:
            summary += "Contributing factors: " + ", ".join(reasoning.contributing_factors) + ". "
        
        summary += f"Confidence: {reasoning.confidence:.2f}, Risk: {reasoning.risk_level}."
        
        return summary
