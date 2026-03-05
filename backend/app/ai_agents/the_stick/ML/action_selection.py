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
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from .action_effectiveness import ActionEffectivenessModel
from .perception import StickPerceptionContext, PaperBagConsumption, HamsterTelepathyMessage
from .reasoning import LoggingReasoning

logger = logging.getLogger('StickActionSelection')

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
class LoggingAction:
    """The Stick's selected logging action"""
    
    # Core action
    action_type: str
    logging_strategy: str
    
    # Action details
    priority: str
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
    
    # ML Tracking
    exploration: bool = False
    epsilon: float = 0.0
    alternatives_considered: List[str] = field(default_factory=list)


class StickActionSelection:
    """
    The Stick's action selection layer for decision logging.
    
    📊 "Selecting logging action... *breathes into paper bag* ...logging everything!"
    """
    
    ACTION_MAP = {
        'bob_spotted': ['execute_bob_evasion', 'execute_panic_protocol'],
        'panic_attack': ['execute_panic_protocol', 'log_emergency_event'],
        'urgent': ['log_emergency_event', 'execute_panic_protocol'],
        'high': ['log_anxious_reminder', 'log_standard_decision'],
        'normal': ['log_standard_decision', 'log_anxious_reminder'],
        'low': ['log_standard_decision'],
        'panic_mode': ['execute_panic_protocol']
    }
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any], system_id: str = "default"):
        self.db = db
        self.personality_traits = personality_traits
        self.system_id = system_id
        
        self.action_effectiveness = ActionEffectivenessModel(
            db=db,
            system_id=self.system_id,
            agent_name="the_stick"
        )
        self.epsilon = EXPLORATION_CONFIG['initial_epsilon']
        
    async def select_action(
        self,
        context: StickPerceptionContext,
        reasoning: LoggingReasoning
    ) -> LoggingAction:
        """
        Select logging action based on anxious reasoning and learned effectiveness.
        """
        logger.info(f"📊⚡ Selecting logging action...")
        
        # Determine root cause
        bob_detected = context.bob_proximity and context.bob_proximity.bob_detected
        if bob_detected:
            root_cause = 'bob_spotted'
        elif context.panic_attack_active:
            root_cause = 'panic_attack'
        else:
            root_cause = reasoning.logging_priority
        
        viable_actions = self.ACTION_MAP.get(root_cause, ['log_standard_decision'])
        
        scored_actions = await self._score_viable_actions(viable_actions, root_cause, context)
        
        exploration = False
        if random.random() < self.epsilon and len(viable_actions) > 1:
            exploration = True
            action_type = random.choice([a for a in viable_actions if a != scored_actions[0][0]])
            confidence = 0.3
            logger.info(f"📊🎲 Trying alternative protocol: {action_type}")
        else:
            action_type = scored_actions[0][0]
            confidence = scored_actions[0][1]
            
        self.epsilon = max(
            EXPLORATION_CONFIG['min_epsilon'],
            self.epsilon * EXPLORATION_CONFIG['decay_rate']
        )
        
        priority = self._map_priority(reasoning.logging_priority)
        immediate = self._requires_immediate_logging(reasoning.logging_urgency, context.panic_attack_active)
        paper_bags_consumed = sum(e.bags_consumed for e in context.paper_bag_events)
        breathing_performed = reasoning.breathing_exercises_required
        panic_managed = context.panic_attack_active and paper_bags_consumed > 0
        
        bob_avoidance_executed = bob_detected and action_type == 'execute_bob_evasion'
        safe_distance = not bob_detected or reasoning.bob_threat_level in ['none', 'low']
        
        hamster_archived = len(context.hamster_messages)
        logging_time = self._estimate_logging_time(action_type, context.decision_complexity, paper_bags_consumed)
        
        action = LoggingAction(
            action_type=action_type,
            logging_strategy=reasoning.logging_approach,
            priority=priority,
            confidence=confidence,
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
            estimated_logging_time=logging_time,
            exploration=exploration,
            epsilon=self.epsilon,
            alternatives_considered=viable_actions
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
        
    async def _score_viable_actions(self, viable_actions: List[str], root_cause: str, context: StickPerceptionContext) -> List[tuple[str, float]]:
        """Score actions based on expected effectiveness"""
        scored = []
        try:
            effectiveness_scores = await self.action_effectiveness.score_all_actions(
                root_cause=root_cause,
                severity=context.decision_complexity
            )
        except Exception as e:
            logger.warning(f"📊⚠️ Effectiveness model failed (panic!): {e}")
            effectiveness_scores = {}
            
        for action in viable_actions:
            score = effectiveness_scores.get(action, 0.5)
            
            # Contextual modifiers
            if action == 'execute_bob_evasion' and root_cause == 'bob_spotted':
                score += 0.3
            elif action == 'execute_panic_protocol' and context.panic_attack_active:
                score += 0.2
                
            score = max(0.1, min(0.99, score))
            scored.append((action, score))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _map_priority(self, logging_priority: str) -> str:
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
        base_times = {
            'log_standard_decision': 10,
            'log_anxious_reminder': 12,
            'log_emergency_event': 5,
            'execute_panic_protocol': 30,
            'execute_bob_evasion': 20
        }
        
        base = base_times.get(action_type, 10)
        base += int(complexity * 10)
        base += paper_bags_consumed * 15
        
        return base
