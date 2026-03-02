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
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import HawkPerceptionContext
from .reasoning import TriageReasoning

logger = logging.getLogger('HawkActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


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


class HawkActionSelection:
    """
    Sir Hawkington's action selection layer.
    
    🧐 "One must select the proper course of action with aristocratic precision!"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        self.current_monocle_state = 'polished'
        
    def select_action(
        self,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning
    ) -> TriageAction:
        """
        Select the appropriate triage action based on reasoning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            
        Returns:
            TriageAction with selected action and details
        """
        logger.info(f"🧐⚡ Selecting action for {context.resource_type} triage...")
        
        # Determine action type
        action_type = self._determine_action_type(reasoning)
        
        # Select target agent
        target_agent = reasoning.target_specialist if action_type == 'escalate' else None
        
        # Determine priority
        priority = self._determine_priority(reasoning)
        
        # Update monocle state based on data quality and confidence
        self._update_monocle_state(context.data_quality_score, reasoning.confidence)
        
        # Calculate aristocratic confidence (personality-adjusted)
        aristocratic_confidence = self._calculate_aristocratic_confidence(
            reasoning.confidence,
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
            aristocratic_confidence=aristocratic_confidence
        )
        
        logger.info(
            f"🧐✅ Action selected: {action_type} to {target_agent or 'none'}, "
            f"priority={priority}, monocle={self.current_monocle_state}"
        )
        
        return action
    
    def _determine_action_type(self, reasoning: TriageReasoning) -> str:
        """
        Determine the type of action to take.
        """
        if reasoning.should_escalate:
            return 'escalate'
        elif reasoning.risk_level in ['medium', 'high']:
            return 'monitor'
        else:
            return 'dismiss'
    
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
        # Start with base confidence
        confidence = base_confidence
        
        # Reduce confidence for each monocle yeet
        confidence -= (monocle_yeets * 0.05)
        
        # Boost confidence if data quality is excellent
        if data_quality > 0.9:
            confidence += 0.1
        
        # Aristocratic personality: slightly more conservative
        confidence *= 0.95
        
        return max(0.0, min(1.0, confidence))
    
    def _build_escalation_message(
        self,
        context: HawkPerceptionContext,
        reasoning: TriageReasoning
    ) -> str:
        """
        Build aristocratic message to VIC-20.
        
        🧐 "One must communicate with proper decorum!"
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
