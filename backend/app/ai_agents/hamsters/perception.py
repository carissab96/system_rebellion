#!/usr/bin/env python3
"""
Hamsters' Perception Layer - Telepathic Storage Assessment

The telepathic trio (Steve, Bob, Carl) perceive storage issues collectively.

Collects:
- Disk usage metrics and fragmentation levels
- Storage complexity assessment (triggers beer consumption)
- Duct tape requirements (Carl's specialty)
- Bob's proximity to supply cupboard (triggers Stick's panic)
- QSP quantum messages (only Hamsters can parse them)
- Historical fix success rates

Personality behaviors (REACTIVE TO REAL DATA):
- Beer consumption = complexity/ingenuity level
- Duct tape calculations = every job measured in tape units
- Bob supply cupboard raids = 3am chaos
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.agent_learning import AgentLearningRecord

logger = logging.getLogger('HamstersPerception')

UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)


@dataclass
class BeerConsumptionEvent:
    """Beer consumption triggered by complexity level"""
    hamster: str  # 'steve', 'bob', or 'carl'
    beers_consumed: int
    reason: str
    complexity_level: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class DuctTapeCalculation:
    """Carl's duct tape assessment for the job"""
    regular_rolls: float
    premium_rolls: float
    quantum_rolls: float
    carls_special_rolls: float
    total_rolls: float
    job_complexity: str  # 'simple', 'moderate', 'complex', 'quantum'


@dataclass
class BobProximityAlert:
    """Bob's proximity to supply cupboard (triggers Stick's panic)"""
    bob_at_cupboard: bool
    time_of_raid: Optional[datetime]
    items_acquired: List[str]
    stick_panic_level: float  # 0.0-1.0


@dataclass
class HamstersPerceptionContext:
    """Everything the telepathic hamsters perceive about storage issues"""
    
    # Storage metrics
    disk_usage_percent: float
    fragmentation_level: float
    available_space_gb: float
    inode_usage_percent: float
    
    # Complexity assessment (triggers beer)
    complexity_level: float  # 0.0-1.0
    ingenuity_required: float  # 0.0-1.0
    
    # Beer consumption tracking
    beer_events: List[BeerConsumptionEvent] = field(default_factory=list)
    steve_beers_today: int = 0
    bob_beers_today: int = 0
    carl_beers_today: int = 0
    
    # Duct tape calculations
    duct_tape_assessment: Optional[DuctTapeCalculation] = None
    
    # Bob chaos tracking
    bob_proximity: Optional[BobProximityAlert] = None
    
    # QSP quantum messages (only Hamsters understand)
    qsp_messages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Historical context
    similar_fixes: List[Dict[str, Any]] = field(default_factory=list)
    recent_sudo_operations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Confidence factors
    telepathic_consensus_strength: float = 1.0
    fix_confidence: float = 0.5


class HamstersPerception:
    """
    Hamsters' telepathic perception layer for storage issues.
    
    🐹🐹🐹 "Telepathically assessing storage situation... *cracks beer*"
    """
    
    def __init__(self, db: AsyncSession, personality_traits: Dict[str, Any]):
        self.db = db
        self.personality_traits = personality_traits
        
        # Individual hamster traits
        self.steve_risk_tolerance = personality_traits.get('steve_risk_tolerance', 0.3)
        self.bob_risk_tolerance = personality_traits.get('bob_risk_tolerance', 0.8)
        self.carl_risk_tolerance = personality_traits.get('carl_risk_tolerance', 0.5)
        
        # Beer tracking
        self.beer_events: List[BeerConsumptionEvent] = []
        
    async def perceive(self, storage_alert: Dict[str, Any]) -> HamstersPerceptionContext:
        """
        Telepathically perceive storage situation and assess complexity.
        
        Args:
            storage_alert: Storage alert from VIC-20
            
        Returns:
            HamstersPerceptionContext with full telepathic assessment
        """
        disk_usage = storage_alert.get('current_value', 0.0)
        threshold = storage_alert.get('threshold', 0.0)
        severity = storage_alert.get('severity', 'low')
        
        logger.info(
            f"🐹👁️ Hamsters telepathically perceiving storage situation: "
            f"{disk_usage:.1f}% (severity: {severity})"
        )
        
        # Assess complexity and ingenuity required
        complexity = self._assess_complexity(disk_usage, threshold, severity)
        ingenuity = self._assess_ingenuity_required(complexity, storage_alert)
        
        logger.info(
            f"🐹🧠 Telepathic assessment: complexity={complexity:.2f}, "
            f"ingenuity_required={ingenuity:.2f}"
        )
        
        # PERSONALITY BEHAVIOR: Beer consumption based on complexity
        beer_events = self._assess_beer_requirements(complexity, ingenuity)
        
        if beer_events:
            total_beers = sum(e.beers_consumed for e in beer_events)
            logger.info(
                f"🐹🍺 Beer consumption triggered: {total_beers} beers total "
                f"(complexity: {complexity:.2f})"
            )
            for event in beer_events:
                logger.info(
                    f"🐹🍺 {event.hamster.upper()}: {event.beers_consumed} beers - {event.reason}"
                )
        
        # PERSONALITY BEHAVIOR: Carl's duct tape calculations
        duct_tape = self._calculate_duct_tape_requirements(
            complexity,
            ingenuity,
            disk_usage
        )
        
        logger.info(
            f"🐹📏 Carl's duct tape assessment: {duct_tape.total_rolls:.1f} total rolls "
            f"({duct_tape.job_complexity} job)"
        )
        
        # PERSONALITY BEHAVIOR: Check Bob's supply cupboard proximity
        bob_proximity = self._check_bob_proximity()
        
        if bob_proximity and bob_proximity.bob_at_cupboard:
            logger.warning(
                f"🐹⚠️ BOB IS AT THE SUPPLY CUPBOARD! "
                f"Stick panic level: {bob_proximity.stick_panic_level:.2f}"
            )
        
        # Retrieve similar fixes from history
        similar_fixes = await self._get_similar_fixes(disk_usage, complexity)
        
        # Get recent sudo operations
        recent_sudo = await self._get_recent_sudo_operations()
        
        # Calculate telepathic consensus strength
        consensus_strength = self._calculate_consensus_strength(
            complexity,
            ingenuity,
            beer_events
        )
        
        # Calculate fix confidence from historical data
        fix_confidence = self._calculate_fix_confidence(similar_fixes)
        
        # Count beers consumed today
        steve_beers = sum(e.beers_consumed for e in beer_events if e.hamster == 'steve')
        bob_beers = sum(e.beers_consumed for e in beer_events if e.hamster == 'bob')
        carl_beers = sum(e.beers_consumed for e in beer_events if e.hamster == 'carl')
        
        context = HamstersPerceptionContext(
            disk_usage_percent=disk_usage,
            fragmentation_level=storage_alert.get('fragmentation', 0.0),
            available_space_gb=storage_alert.get('available_space_gb', 0.0),
            inode_usage_percent=storage_alert.get('inode_usage', 0.0),
            complexity_level=complexity,
            ingenuity_required=ingenuity,
            beer_events=beer_events,
            steve_beers_today=steve_beers,
            bob_beers_today=bob_beers,
            carl_beers_today=carl_beers,
            duct_tape_assessment=duct_tape,
            bob_proximity=bob_proximity,
            similar_fixes=similar_fixes,
            recent_sudo_operations=recent_sudo,
            telepathic_consensus_strength=consensus_strength,
            fix_confidence=fix_confidence
        )
        
        logger.info(
            f"🐹✅ Telepathic perception complete: consensus={consensus_strength:.2f}, "
            f"confidence={fix_confidence:.2f}, beers={steve_beers + bob_beers + carl_beers}"
        )
        
        return context
    
    def _assess_complexity(
        self,
        disk_usage: float,
        threshold: float,
        severity: str
    ) -> float:
        """
        Assess storage problem complexity (0.0-1.0).
        Higher complexity = more beer required.
        """
        # Base complexity from disk usage
        overage = (disk_usage - threshold) / threshold if threshold > 0 else 0
        complexity = min(1.0, overage)
        
        # Severity multiplier
        severity_multipliers = {
            'critical': 1.5,
            'high': 1.2,
            'medium': 1.0,
            'low': 0.8
        }
        complexity *= severity_multipliers.get(severity, 1.0)
        
        return min(1.0, complexity)
    
    def _assess_ingenuity_required(
        self,
        complexity: float,
        storage_alert: Dict[str, Any]
    ) -> float:
        """
        Assess ingenuity level required (0.0-1.0).
        Higher ingenuity = more creative solutions = more beer.
        """
        # Base ingenuity from complexity
        ingenuity = complexity
        
        # Boost if fragmentation is high
        fragmentation = storage_alert.get('fragmentation', 0.0)
        if fragmentation > 0.7:
            ingenuity += 0.2
        
        # Boost if inodes are constrained
        inode_usage = storage_alert.get('inode_usage', 0.0)
        if inode_usage > 0.8:
            ingenuity += 0.15
        
        return min(1.0, ingenuity)
    
    def _assess_beer_requirements(
        self,
        complexity: float,
        ingenuity: float
    ) -> List[BeerConsumptionEvent]:
        """
        PERSONALITY BEHAVIOR: Determine beer consumption based on complexity.
        
        Beer consumption = f(complexity, ingenuity)
        - Steve: Careful, 2 beers baseline
        - Bob: Wild, 4 beers baseline
        - Carl: Moderate, 3 beers baseline
        
        More complexity = more beers for everyone
        """
        events = []
        
        # Calculate beer multiplier from complexity and ingenuity
        beer_multiplier = (complexity + ingenuity) / 2.0
        
        # Steve (careful, paces himself)
        steve_baseline = 2
        steve_beers = int(steve_baseline * (1.0 + beer_multiplier * 0.5))
        if steve_beers > steve_baseline:
            events.append(BeerConsumptionEvent(
                hamster='steve',
                beers_consumed=steve_beers - steve_baseline,
                reason=f"Complexity requires careful analysis (complexity: {complexity:.2f})",
                complexity_level=complexity
            ))
        
        # Bob (wild, always ready)
        bob_baseline = 4
        bob_beers = int(bob_baseline * (1.0 + beer_multiplier))
        if bob_beers > bob_baseline:
            events.append(BeerConsumptionEvent(
                hamster='bob',
                beers_consumed=bob_beers - bob_baseline,
                reason=f"Wild ideas require fuel! (ingenuity: {ingenuity:.2f})",
                complexity_level=complexity
            ))
        
        # Carl (duct tape genius, moderate)
        carl_baseline = 3
        carl_beers = int(carl_baseline * (1.0 + beer_multiplier * 0.75))
        if carl_beers > carl_baseline:
            events.append(BeerConsumptionEvent(
                hamster='carl',
                beers_consumed=carl_beers - carl_baseline,
                reason=f"Quantum duct tape calculations require focus (complexity: {complexity:.2f})",
                complexity_level=complexity
            ))
        
        return events
    
    def _calculate_duct_tape_requirements(
        self,
        complexity: float,
        ingenuity: float,
        disk_usage: float
    ) -> DuctTapeCalculation:
        """
        PERSONALITY BEHAVIOR: Carl measures every job in duct tape units.
        
        Duct tape requirements = f(complexity, ingenuity, disk_usage)
        """
        # Base duct tape from complexity
        base_rolls = complexity * 10.0
        
        # Regular duct tape (always needed)
        regular = base_rolls * 0.4
        
        # Premium duct tape (for tougher jobs)
        premium = base_rolls * 0.3 if complexity > 0.5 else 0.0
        
        # Quantum duct tape (for really complex jobs)
        quantum = base_rolls * 0.2 if complexity > 0.7 else 0.0
        
        # Carl's Special (for impossible jobs)
        carls_special = base_rolls * 0.1 if ingenuity > 0.8 else 0.0
        
        total = regular + premium + quantum + carls_special
        
        # Determine job complexity category
        if complexity < 0.3:
            job_complexity = 'simple'
        elif complexity < 0.6:
            job_complexity = 'moderate'
        elif complexity < 0.8:
            job_complexity = 'complex'
        else:
            job_complexity = 'quantum'
        
        return DuctTapeCalculation(
            regular_rolls=regular,
            premium_rolls=premium,
            quantum_rolls=quantum,
            carls_special_rolls=carls_special,
            total_rolls=total,
            job_complexity=job_complexity
        )
    
    def _check_bob_proximity(self) -> Optional[BobProximityAlert]:
        """
        PERSONALITY BEHAVIOR: Check if Bob is at the supply cupboard.
        
        Bob raids the supply cupboard at 3am for redneck engineering parts.
        This triggers The Stick's panic attacks.
        """
        # Check current time
        now = utc_now()
        hour = now.hour
        
        # Bob raids at 3am (or randomly during complex jobs)
        bob_at_cupboard = (hour == 3) or (hour >= 2 and hour <= 4)
        
        if bob_at_cupboard:
            # Stick's panic level based on Bob's chaos
            stick_panic = 0.8 if hour == 3 else 0.6
            
            # Items Bob typically acquires
            items = [
                'quantum duct tape',
                'redneck engineering parts',
                'mystery components',
                'Carl\'s special tape'
            ]
            
            return BobProximityAlert(
                bob_at_cupboard=True,
                time_of_raid=now,
                items_acquired=items,
                stick_panic_level=stick_panic
            )
        
        return None
    
    async def _get_similar_fixes(
        self,
        disk_usage: float,
        complexity: float
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar storage fixes from learning history.
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'hamsters')
                .where(AgentLearningRecord.decision_type.like('storage_fix%'))
                .order_by(desc(AgentLearningRecord.timestamp))
                .limit(10)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            similar = []
            for record in records:
                similar.append({
                    'disk_usage': record.input_data.get('disk_usage_percent'),
                    'fix_type': record.output_data.get('fix_type'),
                    'success': record.success,
                    'beers_consumed': record.output_data.get('total_beers_consumed', 0),
                    'duct_tape_used': record.output_data.get('duct_tape_rolls', 0),
                    'timestamp': record.timestamp
                })
            
            logger.debug(f"🐹📚 Found {len(similar)} similar storage fixes")
            return similar
            
        except Exception as e:
            logger.error(f"🐹💥 Error retrieving similar fixes: {e}")
            return []
    
    async def _get_recent_sudo_operations(self) -> List[Dict[str, Any]]:
        """
        Get recent sudo operations (fstrim, defrag, etc).
        """
        try:
            query = (
                select(AgentLearningRecord)
                .where(AgentLearningRecord.agent_name == 'hamsters')
                .where(AgentLearningRecord.decision_type.like('sudo_%'))
                .order_by(desc(AgentLearningRecord.timestamp))
                .limit(5)
            )
            
            result = await self.db.execute(query)
            records = result.scalars().all()
            
            operations = []
            for record in records:
                operations.append({
                    'operation': record.decision_type,
                    'success': record.success,
                    'timestamp': record.timestamp
                })
            
            return operations
            
        except Exception as e:
            logger.error(f"🐹💥 Error retrieving sudo operations: {e}")
            return []
    
    def _calculate_consensus_strength(
        self,
        complexity: float,
        ingenuity: float,
        beer_events: List[BeerConsumptionEvent]
    ) -> float:
        """
        Calculate telepathic consensus strength.
        
        Stronger consensus = higher confidence in collective decision.
        """
        # Base consensus from complexity (easier problems = stronger consensus)
        consensus = 1.0 - (complexity * 0.3)
        
        # Beer helps consensus (up to a point)
        total_beers = sum(e.beers_consumed for e in beer_events)
        beer_boost = min(0.2, total_beers * 0.02)
        consensus += beer_boost
        
        return min(1.0, max(0.3, consensus))
    
    def _calculate_fix_confidence(
        self,
        similar_fixes: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence in fix based on historical success.
        """
        if not similar_fixes:
            return 0.5  # Neutral confidence
        
        successful = sum(1 for f in similar_fixes if f.get('success', False))
        return successful / len(similar_fixes)
