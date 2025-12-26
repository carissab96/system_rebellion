#!/usr/bin/env python3
"""
The Stick's Perception Layer - Anxious Logging Assessment

The Stick perceives all agent decisions and system events for logging.

Collects:
- Agent decision logs and coordination messages
- Bob proximity detection (triggers panic attacks)
- Hamster telepathic messages (only The Stick can translate)
- System error rates and anomalies
- Paper bag inventory status

Personality behaviors (REACTIVE TO REAL DATA):
- Anxiety level = f(error_rate, Bob_proximity, decision_complexity)
- Paper bag consumption = triggered by panic attacks
- Bob detection = proximity to supply cupboard
- Hamster translation = only The Stick understands their telepathy
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.agent_learning import AgentLearningRecord

logger = logging.getLogger('StickPerception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class BobProximityEvent:
    """Bob proximity detection (triggers panic)"""
    bob_detected: bool
    proximity_level: float  # 0.0-1.0 (how close Bob is)
    location: str  # 'supply_cupboard', 'workspace', 'unknown'
    panic_triggered: bool
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class PaperBagConsumption:
    """Paper bag consumption during panic attack"""
    bags_consumed: int
    panic_severity: float  # 0.0-1.0
    trigger: str  # 'bob_detection', 'error_spike', 'decision_overload'
    breathing_duration_seconds: int
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class HamsterTelepathyMessage:
    """Hamster telepathic message (only The Stick can translate)"""
    raw_telepathy: str  # Raw hamster telepathic signal
    translated_message: str  # The Stick's translation
    hamster_source: str  # 'steve', 'bob', 'carl', 'consensus'
    translation_confidence: float  # 0.0-1.0


@dataclass
class StickPerceptionContext:
    """Everything The Stick perceives about logging situation"""
    
    # Decision logging
    pending_decisions: int
    recent_decisions: List[Dict[str, Any]] = field(default_factory=list)
    decision_complexity: float = 0.0  # 0.0-1.0
    
    # Anxiety triggers (personality)
    anxiety_level: float = 0.0  # 0.0-1.0
    bob_proximity: Optional[BobProximityEvent] = None
    bob_proximity_event: Optional[BobProximityEvent] = None  # Alias for compatibility
    panic_attack_active: bool = False
    
    # Paper bag tracking
    paper_bag_events: List[PaperBagConsumption] = field(default_factory=list)
    paper_bags_consumed_today: int = 0
    paper_bag_inventory: int = 50  # Starting inventory
    
    # Hamster telepathy translation
    hamster_messages: List[HamsterTelepathyMessage] = field(default_factory=list)
    
    # System health
    error_rate: float = 0.0
    anomaly_count: int = 0
    
    # Historical context
    similar_logging_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Confidence factors
    logging_confidence: float = 0.5


class StickPerception:
    """
    The Stick's anxious perception layer for decision logging.
    
    📊 "Logging all decisions... *breathes into paper bag* ...Bob detected! PANIC!"
    """
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any]):
        self.db = db
        self.personality_traits = personality_traits
        
        # Stick traits
        self.anxiety_baseline = personality_traits.get('anxiety_baseline', 0.4)
        self.bob_sensitivity = personality_traits.get('bob_sensitivity', 0.9)
        
        # Paper bag tracking
        self.paper_bag_events: List[PaperBagConsumption] = []
        
    async def perceive(self, logging_request: Dict[str, Any]) -> StickPerceptionContext:
        """
        Anxiously perceive logging situation.
        
        Args:
            logging_request: Decision log or coordination message
            
        Returns:
            StickPerceptionContext with anxiety assessment
        """
        request_type = logging_request.get('request_type', 'unknown')
        agent_source = logging_request.get('agent', 'unknown')
        
        logger.info(
            f"📊👁️ The Stick perceiving logging request: "
            f"{request_type} from {agent_source}"
        )
        
        # Assess decision complexity
        complexity = self._assess_decision_complexity(logging_request)
        
        # PERSONALITY BEHAVIOR: Detect Bob proximity
        bob_proximity = self._detect_bob_proximity(logging_request)
        
        if bob_proximity and bob_proximity.bob_detected:
            logger.warning(
                f"📊⚠️ BOB DETECTED! Proximity: {bob_proximity.proximity_level:.2f}, "
                f"Location: {bob_proximity.location}"
            )
        
        # PERSONALITY BEHAVIOR: Calculate anxiety level
        anxiety = self._calculate_anxiety_level(
            complexity,
            bob_proximity,
            logging_request
        )
        
        # PERSONALITY BEHAVIOR: Check for panic attack
        panic_active = self._check_panic_attack(anxiety, bob_proximity)
        
        # PERSONALITY BEHAVIOR: Paper bag consumption if panicking
        paper_bag_events = []
        if panic_active:
            paper_bag_event = self._consume_paper_bag(anxiety, bob_proximity)
            paper_bag_events.append(paper_bag_event)
            logger.warning(
                f"📊💨 PANIC ATTACK! Consumed {paper_bag_event.bags_consumed} paper bags, "
                f"breathing for {paper_bag_event.breathing_duration_seconds}s"
            )
        
        # PERSONALITY BEHAVIOR: Translate Hamster telepathy
        hamster_messages = self._translate_hamster_telepathy(logging_request)
        
        if hamster_messages:
            logger.info(
                f"📊🐹 Translated {len(hamster_messages)} hamster telepathic messages "
                f"(only The Stick can understand)"
            )
            for msg in hamster_messages:
                logger.info(
                    f"📊🐹 {msg.hamster_source}: {msg.translated_message} "
                    f"(confidence: {msg.translation_confidence:.2f})"
                )
        
        # Get recent decisions
        recent_decisions = await self._get_recent_decisions()
        
        # Get similar logging events
        similar_events = await self._get_similar_logging_events(request_type)
        
        # Assess system health
        error_rate = logging_request.get('error_rate', 0.0)
        anomaly_count = logging_request.get('anomaly_count', 0)
        
        # Calculate logging confidence
        confidence = self._calculate_logging_confidence(
            anxiety,
            complexity,
            len(similar_events)
        )
        
        # Count paper bags consumed today
        bags_today = sum(e.bags_consumed for e in paper_bag_events)
        
        context = StickPerceptionContext(
            pending_decisions=logging_request.get('pending_decisions', 0),
            recent_decisions=recent_decisions,
            decision_complexity=complexity,
            anxiety_level=anxiety,
            bob_proximity=bob_proximity,
            panic_attack_active=panic_active,
            paper_bag_events=paper_bag_events,
            paper_bags_consumed_today=bags_today,
            paper_bag_inventory=50 - bags_today,  # Deduct from inventory
            hamster_messages=hamster_messages,
            error_rate=error_rate,
            anomaly_count=anomaly_count,
            similar_logging_events=similar_events,
            logging_confidence=confidence
        )
        
        logger.info(
            f"📊✅ Perception complete: anxiety={anxiety:.2f}, "
            f"panic={panic_active}, bags_consumed={bags_today}, "
            f"hamster_messages={len(hamster_messages)}"
        )
        
        return context
    
    def _assess_decision_complexity(self, logging_request: Dict[str, Any]) -> float:
        """
        Assess complexity of decision being logged (triggers anxiety).
        """
        # Base complexity from decision type
        decision_type = logging_request.get('decision_type', 'unknown')
        
        complexity_weights = {
            'triage': 0.7,
            'coordination': 0.8,
            'storage_fix': 0.6,
            'security_response': 0.9,
            'cache_clear': 0.4,
            'unknown': 0.5
        }
        
        base_complexity = complexity_weights.get(decision_type, 0.5)
        
        # Boost complexity if multiple agents involved
        agents_involved = logging_request.get('agents_involved', 1)
        if agents_involved > 2:
            base_complexity *= 1.2
        
        return min(1.0, base_complexity)
    
    def _detect_bob_proximity(
        self,
        logging_request: Dict[str, Any]
    ) -> Optional[BobProximityEvent]:
        """
        PERSONALITY BEHAVIOR: Detect Bob's proximity (triggers panic).
        
        Bob near supply cupboard = maximum panic for The Stick.
        """
        # Check if Bob is mentioned in the request
        agent_source = logging_request.get('agent', '')
        decision_data = logging_request.get('decision_data', {})
        
        # Check for Bob in hamster consensus
        bob_mentioned = (
            'bob' in agent_source.lower() or
            'bob' in str(decision_data).lower()
        )
        
        if not bob_mentioned:
            return None
        
        # Check Bob's location
        bob_location = decision_data.get('bob_location', 'unknown')
        
        # Proximity level based on location
        if bob_location == 'supply_cupboard' or 'cupboard' in bob_location.lower():
            proximity = 1.0  # Maximum proximity = maximum panic
            location = 'supply_cupboard'
            panic_triggered = True
        elif bob_location == 'workspace':
            proximity = 0.6
            location = 'workspace'
            panic_triggered = proximity > 0.7
        else:
            proximity = 0.3
            location = 'unknown'
            panic_triggered = False
        
        # Bob sensitivity affects panic threshold
        if proximity * self.bob_sensitivity > 0.5:
            panic_triggered = True
        
        return BobProximityEvent(
            bob_detected=True,
            proximity_level=proximity,
            location=location,
            panic_triggered=panic_triggered
        )
    
    def _calculate_anxiety_level(
        self,
        complexity: float,
        bob_proximity: Optional[BobProximityEvent],
        logging_request: Dict[str, Any]
    ) -> float:
        """
        PERSONALITY BEHAVIOR: Calculate The Stick's anxiety level.
        
        Anxiety = f(baseline, complexity, Bob_proximity, error_rate)
        """
        # Start with baseline anxiety
        anxiety = self.anxiety_baseline
        
        # Complexity increases anxiety
        anxiety += complexity * 0.3
        
        # Bob proximity MASSIVELY increases anxiety
        if bob_proximity and bob_proximity.bob_detected:
            anxiety += bob_proximity.proximity_level * self.bob_sensitivity * 0.5
        
        # Error rate increases anxiety
        error_rate = logging_request.get('error_rate', 0.0)
        if error_rate > 0.1:
            anxiety += error_rate * 0.2
        
        return min(1.0, anxiety)
    
    def _check_panic_attack(
        self,
        anxiety: float,
        bob_proximity: Optional[BobProximityEvent]
    ) -> bool:
        """
        PERSONALITY BEHAVIOR: Check if panic attack is triggered.
        
        Panic attack = anxiety > 0.7 OR Bob detected near cupboard
        """
        if anxiety > 0.7:
            return True
        
        if bob_proximity and bob_proximity.panic_triggered:
            return True
        
        return False
    
    def _consume_paper_bag(
        self,
        anxiety: float,
        bob_proximity: Optional[BobProximityEvent]
    ) -> PaperBagConsumption:
        """
        PERSONALITY BEHAVIOR: Consume paper bags during panic attack.
        
        Paper bag consumption = f(anxiety, Bob_proximity)
        """
        # Determine trigger
        if bob_proximity and bob_proximity.bob_detected:
            trigger = 'bob_detection'
        elif anxiety > 0.8:
            trigger = 'decision_overload'
        else:
            trigger = 'error_spike'
        
        # Calculate bags needed
        if anxiety > 0.9 or (bob_proximity and bob_proximity.proximity_level > 0.8):
            bags = 3  # Severe panic
            breathing_duration = 60
        elif anxiety > 0.7:
            bags = 2  # Moderate panic
            breathing_duration = 30
        else:
            bags = 1  # Mild panic
            breathing_duration = 15
        
        return PaperBagConsumption(
            bags_consumed=bags,
            panic_severity=anxiety,
            trigger=trigger,
            breathing_duration_seconds=breathing_duration
        )
    
    def _translate_hamster_telepathy(
        self,
        logging_request: Dict[str, Any]
    ) -> List[HamsterTelepathyMessage]:
        """
        PERSONALITY BEHAVIOR: Translate Hamster telepathic messages.
        
        Only The Stick can understand Hamster telepathy.
        """
        messages = []
        
        # Check if request contains hamster telepathy
        decision_data = logging_request.get('decision_data', {})
        
        # Look for hamster consensus data
        if 'steve_assessment' in decision_data:
            # Steve's careful thoughts
            steve_msg = HamsterTelepathyMessage(
                raw_telepathy="*careful telepathic analysis*",
                translated_message=decision_data.get('steve_assessment', 'Unknown'),
                hamster_source='steve',
                translation_confidence=0.9
            )
            messages.append(steve_msg)
        
        if 'bob_suggestion' in decision_data:
            # Bob's wild ideas
            bob_msg = HamsterTelepathyMessage(
                raw_telepathy="*chaotic telepathic energy*",
                translated_message=decision_data.get('bob_suggestion', 'Unknown'),
                hamster_source='bob',
                translation_confidence=0.7  # Bob is harder to understand
            )
            messages.append(bob_msg)
        
        if 'carl_calculation' in decision_data:
            # Carl's duct tape wisdom
            carl_msg = HamsterTelepathyMessage(
                raw_telepathy="*duct tape telepathic calculations*",
                translated_message=decision_data.get('carl_calculation', 'Unknown'),
                hamster_source='carl',
                translation_confidence=0.85
            )
            messages.append(carl_msg)
        
        if 'telepathic_consensus' in decision_data:
            # Consensus message
            consensus_msg = HamsterTelepathyMessage(
                raw_telepathy="*unified telepathic agreement*",
                translated_message="Hamsters reached telepathic consensus",
                hamster_source='consensus',
                translation_confidence=0.95
            )
            messages.append(consensus_msg)
        
        return messages
    
    async def _get_recent_decisions(self) -> List[Dict[str, Any]]:
        """
        Get recent decisions from all agents.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(10)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            decisions = []
            for record in records:
                decisions.append({
                    'agent': record.agent_name,
                    'decision_type': f"{record.resource_type}_{record.action}",
                    'confidence': record.confidence,
                    'success': record.success,
                    'timestamp': record.created_at
                })
            
            logger.debug(f"📊📚 Found {len(decisions)} recent decisions")
            return decisions
            
        except Exception as e:
            logger.error(f"📊💥 Error retrieving recent decisions: {e}")
            return []
    
    async def _get_similar_logging_events(
        self,
        request_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get similar logging events from history.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'the_stick')
                .order_by(desc(AgentLearningRecord.created_at))
                .limit(5)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            events = []
            for record in records:
                events.append({
                    'request_type': record.action,
                    'anxiety_level': record.parameters.get('anxiety_level', 0.0) if record.parameters else 0.0,
                    'panic_attack': record.parameters.get('panic_attack_active', False) if record.parameters else False,
                    'timestamp': record.created_at
                })
            
            return events
            
        except Exception as e:
            logger.error(f"📊💥 Error retrieving similar events: {e}")
            return []
    
    def _calculate_logging_confidence(
        self,
        anxiety: float,
        complexity: float,
        similar_event_count: int
    ) -> float:
        """
        Calculate logging confidence (reduced by anxiety).
        """
        # Base confidence
        confidence = 0.8
        
        # Anxiety reduces confidence
        confidence -= anxiety * 0.3
        
        # Complexity reduces confidence
        confidence -= complexity * 0.1
        
        # Historical events boost confidence
        if similar_event_count > 0:
            confidence += 0.1
        
        return min(1.0, max(0.3, confidence))
