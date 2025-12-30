#!/usr/bin/env python3
"""
The Stick's Action Selection Layer - Anxious Logging Execution

Selects:
- Logging action and storage strategy
- Paper bag consumption execution
- Bob avoidance maneuvers
- Hamster message archival
- Anxiety management protocols

Personality behaviors integrated:
- Anxiety level tracked and reported
- Paper bag consumption finalized
- Bob proximity alerts
- Hamster telepathy translations stored
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from .perception import StickPerceptionContext, PaperBagConsumption, HamsterTelepathyMessage
from .reasoning import LoggingReasoning

logger = logging.getLogger('StickActionSelection')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class LoggingAction:
    """The Stick's selected logging action"""
    
    # Core action
    action_type: str  # 'log_decision', 'emergency_log', 'panic_log', 'bob_evasion_log'
    logging_strategy: str
    
    # Action details
    priority: str  # 'low', 'normal', 'high', 'urgent', 'panic'
    confidence: float
    
    # Anxiety management (personality)
    anxiety_level: str
    paper_bags_consumed: int
    breathing_exercises_performed: bool
    panic_attack_managed: bool
    
    # Bob situation
    bob_detected: bool
    bob_avoidance_executed: bool
    safe_distance_maintained: bool
    
    # Hamster translation
    hamster_messages_archived: int
    translation_quality: str
    
    # Execution parameters
    immediate_logging: bool
    estimated_logging_time: int  # seconds


class StickActionSelection:
    """
    The Stick's action selection layer for decision logging.
    
    📊 "Selecting logging action... *breathes into paper bag* ...logging everything!"
    """
    
    def __init__(self, personality_traits: Dict[str, Any]):
        self.personality_traits = personality_traits
        
    def select_action(
        self,
        context: StickPerceptionContext,
        reasoning: LoggingReasoning
    ) -> LoggingAction:
        """
        Select logging action based on anxious reasoning.
        
        Args:
            context: Perception context
            reasoning: Reasoning analysis
            
        Returns:
            LoggingAction with anxiety management details
        """
        logger.info(f"📊⚡ Selecting logging action...")
        
        # Determine action type
        action_type = self._determine_action_type(
            reasoning.logging_priority,
            context.panic_attack_active,
            context.bob_proximity
        )
        
        # Determine priority
        priority = self._map_priority(reasoning.logging_priority)
        
        # Check if immediate logging required
        immediate = self._requires_immediate_logging(
            reasoning.logging_urgency,
            context.panic_attack_active
        )
        
        # Execute paper bag consumption if needed
        paper_bags_consumed = sum(e.bags_consumed for e in context.paper_bag_events)
        
        # Execute breathing exercises if needed
        breathing_performed = reasoning.breathing_exercises_required
        
        # Manage panic attack
        panic_managed = context.panic_attack_active and paper_bags_consumed > 0
        
        # Execute Bob avoidance if needed
        bob_detected = context.bob_proximity is not None and context.bob_proximity.bob_detected
        bob_avoidance_executed = bob_detected and reasoning.bob_threat_level in ['high', 'critical']
        safe_distance = not bob_detected or reasoning.bob_threat_level in ['none', 'low']
        
        # Archive hamster messages
        hamster_archived = len(context.hamster_messages)
        
        # Estimate logging time
        logging_time = self._estimate_logging_time(
            action_type,
            context.decision_complexity,
            paper_bags_consumed
        )
        
        action = LoggingAction(
            action_type=action_type,
            logging_strategy=reasoning.logging_approach,
            priority=priority,
            confidence=reasoning.confidence,
            anxiety_level=reasoning.anxiety_level,
            paper_bags_consumed=paper_bags_consumed,
            breathing_exercises_performed=breathing_performed,
            panic_attack_managed=panic_managed,
            bob_detected=bob_detected,
            bob_avoidance_executed=bob_avoidance_executed,
            safe_distance_maintained=safe_distance,
            hamster_messages_archived=hamster_archived,
            translation_quality=reasoning.translation_quality,
            immediate_logging=immediate,
            estimated_logging_time=logging_time
        )
        
        logger.info(
            f"📊✅ Action selected: {action_type}, "
            f"anxiety={reasoning.anxiety_level}, "
            f"paper_bags={paper_bags_consumed}, "
            f"bob_detected={bob_detected}"
        )
        
        if bob_detected:
            logger.warning(
                f"📊⚠️ Bob avoidance executed: {bob_avoidance_executed}, "
                f"safe_distance: {safe_distance}"
            )
        
        if hamster_archived > 0:
            logger.info(
                f"📊🐹 Archived {hamster_archived} hamster telepathic messages "
                f"(quality: {reasoning.translation_quality})"
            )
        
        return action
    
    def _determine_action_type(
        self,
        priority: str,
        panic_active: bool,
        bob_proximity: Optional[Any]
    ) -> str:
        """
        Determine logging/communication action type.
        
        The Stick now has soft enforcement tools:
        - anxious_reminder: Gentle nagging about violations
        - escalate_to_vic20: When reminders are ignored
        - bob_panic_protocol: EMERGENCY when Bob detected
        - pattern_alert: Proactive warnings about emerging patterns
        - log_decision: Standard logging
        """
        # BOB PANIC PROTOCOL (highest priority - survival!)
        if bob_proximity and bob_proximity.bob_detected:
            # Check if Bob is near supply closet (EMERGENCY)
            if hasattr(bob_proximity, 'distance_to_supply_closet'):
                if bob_proximity.distance_to_supply_closet < 10.0:  # Within 10 meters
                    return 'bob_panic_protocol'
            # Otherwise just anxious logging
            return 'bob_evasion_log'
        
        # PANIC MODE (full panic attack)
        elif panic_active:
            return 'panic_log'
        
        # URGENT (emergency logging)
        elif priority == 'urgent':
            return 'emergency_log'
        
        # HIGH PRIORITY (might need escalation or reminder)
        elif priority == 'high':
            # TODO: Add logic to check violation history
            # For now, default to anxious reminder if we detect repeated issues
            return 'anxious_reminder'
        
        # NORMAL (standard logging)
        else:
            return 'log_decision'
    
    def _map_priority(self, logging_priority: str) -> str:
        """
        Map logging priority to action priority.
        """
        priority_map = {
            'panic_mode': 'panic',
            'urgent': 'urgent',
            'high': 'high',
            'normal': 'normal',
            'low': 'low'
        }
        return priority_map.get(logging_priority, 'normal')
    
    def _requires_immediate_logging(
        self,
        urgency: str,
        panic_active: bool
    ) -> bool:
        """
        Determine if immediate logging is required.
        """
        if panic_active:
            return True
        
        if urgency in ['critical', 'high']:
            return True
        
        return False
    
    def _estimate_logging_time(
        self,
        action_type: str,
        complexity: float,
        paper_bags_consumed: int
    ) -> int:
        """
        Estimate logging time in seconds.
        """
        base_times = {
            'log_decision': 10,
            'emergency_log': 5,
            'panic_log': 30,  # Includes paper bag breathing time
            'bob_evasion_log': 20  # Includes evasion maneuvers
        }
        
        base = base_times.get(action_type, 10)
        
        # Complexity adds time
        base += int(complexity * 10)
        
        # Paper bag breathing adds time
        base += paper_bags_consumed * 15
        
        return base
