#!/usr/bin/env python3
"""
The Stick's Reasoning Layer - Anxious Decision Analysis

Analyzes:
- Logging strategy and priority
- Anxiety management approach
- Paper bag requirements
- Hamster message interpretation
- Bob avoidance tactics

The Stick's reasoning is heavily influenced by anxiety levels and Bob proximity.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import StickPerceptionContext, BobProximityEvent, HamsterTelepathyMessage

logger = logging.getLogger('StickReasoning')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class LoggingReasoning:
    """The Stick's anxious reasoning about logging"""
    
    # Logging strategy
    logging_priority: str  # 'low', 'normal', 'high', 'urgent', 'panic_mode'
    logging_approach: str
    confidence: float
    
    # Anxiety management
    anxiety_level: str  # 'calm', 'nervous', 'anxious', 'panicking', 'bob_detected'
    paper_bags_needed: int
    breathing_exercises_required: bool
    
    # Bob situation
    bob_threat_level: str  # 'none', 'low', 'moderate', 'high', 'critical'
    bob_avoidance_strategy: str
    
    # Hamster translation
    hamster_messages_understood: int
    translation_quality: str  # 'clear', 'partial', 'unclear'
    
    # Decision analysis
    decision_complexity_assessment: str
    logging_urgency: str  # 'normal', 'elevated', 'high', 'critical'
    
    # Evidence
    recent_decision_count: int
    similar_event_precedent: bool


class StickReasoning:
    """
    The Stick's anxious reasoning layer for decision logging.
    
    📊 "Analyzing logging requirements... *anxiety intensifies* ...must log everything!"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        self.anxiety_threshold = personality_traits.get('anxiety_threshold', 0.6)
        
    def reason(self, context: StickPerceptionContext) -> LoggingReasoning:
        """
        Anxiously reason about logging approach.
        
        Args:
            context: Perception context from StickPerception
            
        Returns:
            LoggingReasoning with anxiety-influenced analysis
        """
        logger.info(f"📊🧠 The Stick reasoning about logging approach...")
        
        # Determine logging priority (influenced by anxiety)
        priority = self._determine_logging_priority(
            context.anxiety_level,
            context.decision_complexity,
            context.panic_attack_active
        )
        
        # Select logging approach
        approach = self._select_logging_approach(
            priority,
            context.anxiety_level,
            context.bob_proximity
        )
        
        # Assess anxiety level category
        anxiety_category = self._categorize_anxiety(context.anxiety_level)
        
        # Calculate paper bag needs
        paper_bags_needed = self._calculate_paper_bag_needs(
            context.anxiety_level,
            context.panic_attack_active,
            context.paper_bags_consumed_today
        )
        
        # Determine if breathing exercises needed
        breathing_needed = context.anxiety_level > 0.6 or context.panic_attack_active
        
        # Assess Bob threat level
        bob_threat = self._assess_bob_threat(context.bob_proximity)
        
        # Determine Bob avoidance strategy
        bob_avoidance = self._plan_bob_avoidance(context.bob_proximity)
        
        # Analyze hamster message translation
        hamster_count = len(context.hamster_messages)
        translation_quality = self._assess_translation_quality(context.hamster_messages)
        
        # Assess decision complexity
        complexity_assessment = self._assess_complexity(context.decision_complexity)
        
        # Determine logging urgency
        urgency = self._determine_urgency(
            context.anxiety_level,
            context.pending_decisions,
            context.error_rate
        )
        
        # Check for similar event precedent
        has_precedent = len(context.similar_logging_events) > 0
        
        # Calculate confidence (reduced by anxiety)
        confidence = self._calculate_confidence(
            context.logging_confidence,
            context.anxiety_level,
            has_precedent
        )
        
        reasoning = LoggingReasoning(
            logging_priority=priority,
            logging_approach=approach,
            confidence=confidence,
            anxiety_level=anxiety_category,
            paper_bags_needed=paper_bags_needed,
            breathing_exercises_required=breathing_needed,
            bob_threat_level=bob_threat,
            bob_avoidance_strategy=bob_avoidance,
            hamster_messages_understood=hamster_count,
            translation_quality=translation_quality,
            decision_complexity_assessment=complexity_assessment,
            logging_urgency=urgency,
            recent_decision_count=len(context.recent_decisions),
            similar_event_precedent=has_precedent
        )
        
        logger.info(
            f"📊✅ Reasoning complete: priority={priority}, "
            f"anxiety={anxiety_category}, bob_threat={bob_threat}, "
            f"paper_bags_needed={paper_bags_needed}"
        )
        
        if context.bob_proximity and context.bob_proximity.bob_detected:
            logger.warning(f"📊⚠️ BOB DETECTED! Avoidance strategy: {bob_avoidance}")
        
        return reasoning
    
    def _determine_logging_priority(
        self,
        anxiety: float,
        complexity: float,
        panic_active: bool
    ) -> str:
        """
        Determine logging priority (influenced by anxiety).
        """
        if panic_active:
            return 'panic_mode'
        elif anxiety > 0.8:
            return 'urgent'
        elif anxiety > 0.6 or complexity > 0.7:
            return 'high'
        elif complexity > 0.4:
            return 'normal'
        else:
            return 'low'
    
    def _select_logging_approach(
        self,
        priority: str,
        anxiety: float,
        bob_proximity: Optional[BobProximityEvent]
    ) -> str:
        """
        Select logging approach based on anxiety and Bob situation.
        """
        if bob_proximity and bob_proximity.bob_detected:
            return "Log everything while avoiding Bob - maintain safe distance from supply cupboard"
        elif priority == 'panic_mode':
            return "Emergency logging protocol - log while breathing into paper bag"
        elif priority == 'urgent':
            return "Rapid logging with anxiety management - prioritize critical decisions"
        elif anxiety > 0.6:
            return "Careful logging with frequent breathing breaks"
        else:
            return "Standard logging protocol - maintain calm and thorough records"
    
    def _categorize_anxiety(self, anxiety: float) -> str:
        """
        Categorize anxiety level.
        """
        if anxiety > 0.9:
            return 'bob_detected'  # Maximum anxiety
        elif anxiety > 0.7:
            return 'panicking'
        elif anxiety > 0.5:
            return 'anxious'
        elif anxiety > 0.3:
            return 'nervous'
        else:
            return 'calm'
    
    def _calculate_paper_bag_needs(
        self,
        anxiety: float,
        panic_active: bool,
        bags_consumed_today: int
    ) -> int:
        """
        Calculate additional paper bags needed.
        """
        if panic_active:
            return 3  # Immediate need
        elif anxiety > 0.7:
            return 2  # Preventive measure
        elif anxiety > 0.5:
            return 1  # Just in case
        else:
            return 0  # No immediate need
    
    def _assess_bob_threat(
        self,
        bob_proximity: Optional[BobProximityEvent]
    ) -> str:
        """
        Assess Bob threat level.
        """
        if not bob_proximity or not bob_proximity.bob_detected:
            return 'none'
        
        proximity = bob_proximity.proximity_level
        
        if proximity > 0.8:
            return 'critical'  # Bob at supply cupboard
        elif proximity > 0.6:
            return 'high'
        elif proximity > 0.4:
            return 'moderate'
        else:
            return 'low'
    
    def _plan_bob_avoidance(
        self,
        bob_proximity: Optional[BobProximityEvent]
    ) -> str:
        """
        Plan Bob avoidance strategy.
        """
        if not bob_proximity or not bob_proximity.bob_detected:
            return "No avoidance needed - Bob not detected"
        
        if bob_proximity.location == 'supply_cupboard':
            return "EVACUATE AREA - Bob at supply cupboard! Maintain 50ft minimum distance!"
        elif bob_proximity.proximity_level > 0.6:
            return "Increase distance - Bob too close for comfort"
        else:
            return "Monitor Bob's location - maintain awareness"
    
    def _assess_translation_quality(
        self,
        hamster_messages: List[HamsterTelepathyMessage]
    ) -> str:
        """
        Assess quality of Hamster telepathy translation.
        """
        if not hamster_messages:
            return 'none'
        
        avg_confidence = sum(m.translation_confidence for m in hamster_messages) / len(hamster_messages)
        
        if avg_confidence > 0.8:
            return 'clear'
        elif avg_confidence > 0.6:
            return 'partial'
        else:
            return 'unclear'
    
    def _assess_complexity(self, complexity: float) -> str:
        """
        Assess decision complexity.
        """
        if complexity > 0.8:
            return 'highly_complex'
        elif complexity > 0.6:
            return 'complex'
        elif complexity > 0.4:
            return 'moderate'
        else:
            return 'simple'
    
    def _determine_urgency(
        self,
        anxiety: float,
        pending_decisions: int,
        error_rate: float
    ) -> str:
        """
        Determine logging urgency.
        """
        if anxiety > 0.8 or error_rate > 0.2:
            return 'critical'
        elif pending_decisions > 10 or anxiety > 0.6:
            return 'high'
        elif pending_decisions > 5:
            return 'elevated'
        else:
            return 'normal'
    
    def _calculate_confidence(
        self,
        base_confidence: float,
        anxiety: float,
        has_precedent: bool
    ) -> float:
        """
        Calculate reasoning confidence (reduced by anxiety).
        """
        confidence = base_confidence
        
        # Anxiety reduces confidence
        confidence -= anxiety * 0.3
        
        # Historical precedent boosts confidence
        if has_precedent:
            confidence += 0.1
        
        return min(1.0, max(0.2, confidence))
