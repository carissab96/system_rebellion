import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete
import json
from models.stick_model import (
    StickUserPatterns, StickDecisionLog, StickComplianceHistory, 
    StickConfigurationProfiles, StickAnxietyLog, StickHamsterEncounters,
    StickPaperBagUsage, StickMemoryBank, StickSqueakTranslations,
    StickEmergencyProtocols
)
from .data_types import (
    StickDecision, UserPattern, ComplianceViolation, 
    ConfigurationProfile, AnxietyEvent, HamsterProximityAlert,
    PaperBagInventory, StickMemoryEntry
)

class StickDatabaseIntegration:
    """Database integration for The Stick's anxiety-enhanced eidetic memory"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.websocket_anxiety_level = 25.0  # Starting nervous
    
    async def initialize(self):
        """Initialize The Stick's database connection"""
        self.engine = create_async_engine(
            'postgresql+asyncpg://stick:anxious@localhost/system_rebellion',
            echo=False  # The Stick works quietly when anxious
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def store_anxiety_event(self, event: AnxietyEvent):
        """Store anxiety event - The Stick tracks EVERYTHING"""
        async with self.session_factory() as session:
            try:
                anxiety_log = StickAnxietyLog(
                    timestamp=event.timestamp,
                    trigger=event.trigger,
                    anxiety_level_before=event.anxiety_level_before,
                    anxiety_level_after=event.anxiety_level_after,
                    multiplier=event.multiplier,
                    paper_bags_consumed=event.paper_bags_consumed,
                    hamster_involved=event.hamster_involved,
                    resolution=event.resolution
                )
                
                session.add(anxiety_log)
                await session.commit()
                return anxiety_log.id
                
            except Exception as e:
                await session.rollback()
                # Errors cause MORE anxiety
                raise Exception(f"The Stick panicked while storing anxiety event: {str(e)}")
    
    async def store_hamster_encounter(self, user_id: str, alert: HamsterProximityAlert):
        """Store hamster encounter - The Stick's worst nightmare"""
        async with self.session_factory() as session:
            try:
                encounter = StickHamsterEncounters(
                    user_id=user_id,
                    timestamp=alert.timestamp,
                    hamsters_present=','.join(alert.active_hamsters),
                    steve_location=alert.locations.get('steve'),
                    bob_location=alert.locations.get('bob'),
                    carl_location=alert.locations.get('carl'),
                    anxiety_multiplier=alert.anxiety_multiplier,
                    panic_level=alert.panic_level,
                    infrastructure_risk=alert.infrastructure_risk,
                    stick_response=alert.stick_response,
                    paper_bags_consumed=alert.paper_bags_consumed
                )
                
                session.add(encounter)
                await session.commit()
                return encounter.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick hyperventilated while storing hamster encounter: {str(e)}")
    
    async def update_paper_bag_inventory(self, inventory_change: int, reason: str):
        """Update paper bag inventory - Critical for anxiety management"""
        async with self.session_factory() as session:
            try:
                usage = StickPaperBagUsage(
                    timestamp=datetime.now(),
                    bags_consumed=abs(inventory_change) if inventory_change < 0 else 0,
                    bags_added=inventory_change if inventory_change > 0 else 0,
                    reason=reason,
                    anxiety_level_at_time=self.websocket_anxiety_level,
                    hamster_related='hamster' in reason.lower()
                )
                
                session.add(usage)
                await session.commit()
                
                # Calculate current inventory
                total_consumed = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_consumed))
                )
                total_added = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_added))
                )
                
                consumed = total_consumed.scalar() or 0
                added = total_added.scalar() or 0
                
                return {
                    'current_inventory': added - consumed,
                    'consumption_today': await self._get_daily_consumption(),
                    'critical_level': (added - consumed) < 10
                }
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"PAPER BAG INVENTORY CRISIS: {str(e)}")
    
    async def store_memory_entry(self, entry: StickMemoryEntry):
        """Store in The Stick's eidetic memory - NEVER FORGETS"""
        async with self.session_factory() as session:
            try:
                memory = StickMemoryBank(
                    timestamp=entry.timestamp,
                    event_type=entry.event_type,
                    details=entry.details,
                    anxiety_level=entry.anxiety_level,
                    importance=entry.importance,
                    related_hamsters=','.join(entry.related_hamsters) if entry.related_hamsters else None,
                    compliance_impact=entry.compliance_impact,
                    never_forget=entry.never_forget
                )
                
                session.add(memory)
                await session.commit()
                
                # The Stick remembers this FOREVER
                return memory.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"MEMORY STORAGE FAILURE - The Stick is distressed: {str(e)}")
    
    async def store_user_behavior_observation(self, user_id: str, observation: Dict[str, Any]):
        """Store user behavior with anxiety-enhanced perception"""
        
        # Check for anxiety triggers in observation
        anxiety_triggers = []
        if observation.get('cpu_usage', 0) > 80:
            anxiety_triggers.append('high_cpu')
        if observation.get('memory_usage', 0) > 75:
            anxiety_triggers.append('high_memory')
        if observation.get('hamster_activity', False):
            anxiety_triggers.append('HAMSTER_DETECTED')
        
        async with self.session_factory() as session:
            try:
                # Get or create user pattern
                existing_pattern = await session.execute(
                    select(StickUserPatterns).where(
                        StickUserPatterns.user_id == user_id
                    )
                )
                
                pattern = existing_pattern.scalar_one_or_none()
                
                if pattern:
                    pattern.observation_count += 1
                    pattern.last_observation = datetime.now()
                    
                    # Update patterns with anxiety context
                    current_patterns = pattern.learned_patterns or {}
                    hour = datetime.now().hour
                    
                    if 'time_based' not in current_patterns:
                        current_patterns['time_based'] = {}
                    
                    if str(hour) not in current_patterns['time_based']:
                        current_patterns['time_based'][str(hour)] = {
                            'activities': [],
                            'metrics': [],
                            'anxiety_triggers': [],
                            'count': 0
                        }
                    
                    current_patterns['time_based'][str(hour)]['activities'].append(
                        observation.get('detected_activity', 'unknown')
                    )
                    current_patterns['time_based'][str(hour)]['metrics'].append(
                        observation.get('system_metrics', {})
                    )
                    current_patterns['time_based'][str(hour)]['anxiety_triggers'].extend(anxiety_triggers)
                    current_patterns['time_based'][str(hour)]['count'] += 1
                    
                    pattern.learned_patterns = current_patterns
                    pattern.confidence_score = self._calculate_pattern_confidence(current_patterns)
                    pattern.anxiety_correlation = len(anxiety_triggers) / 10.0  # Normalize to 0-1
                    
                else:
                    # Create new pattern with anxiety awareness
                    pattern = StickUserPatterns(
                        user_id=user_id,
                        observation_count=1,
                        learned_patterns={
                            'time_based': {
                                str(datetime.now().hour): {
                                    'activities': [observation.get('detected_activity', 'unknown')],
                                    'metrics': [observation.get('system_metrics', {})],
                                    'anxiety_triggers': anxiety_triggers,
                                    'count': 1
                                }
                            }
                        },
                        confidence_score=0.1,
                        anxiety_correlation=len(anxiety_triggers) / 10.0,
                        last_observation=datetime.now()
                    )
                    session.add(pattern)
                
                # Store memory entry
                memory_entry = StickMemoryEntry(
                    timestamp=datetime.now(),
                    event_type='behavior_observation',
                    details=observation,
                    anxiety_level=self.websocket_anxiety_level if hasattr(self, 'websocket_anxiety_level') else 25.0,
                    importance='HIGH' if anxiety_triggers else 'MEDIUM',
                    related_hamsters=['Bob'] if 'bob' in str(anxiety_triggers).lower() else [],
                    compliance_impact='monitoring',
                    never_forget='Bob' in str(anxiety_triggers)
                )
                
                await self.store_memory_entry(memory_entry)
                
                await session.commit()
                return pattern.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick panicked while storing observation: {str(e)}")
    
    async def _get_daily_consumption(self) -> int:
        """Get today's paper bag consumption"""
        async with self.session_factory() as session:
            try:
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                result = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_consumed)).where(
                        StickPaperBagUsage.timestamp >= today_start
                    )
                )
                
                return result.scalar() or 0
                
            except Exception as e:
                raise Exception(f"Paper bag tracking error: {str(e)}")
    
    async def store_stick_decision(self, user_id: str, decision: StickDecision):
        """Store The Stick's decision with anxiety context"""
        
        async with self.session_factory() as session:
            try:
                decision_log = StickDecisionLog(
                    user_id=user_id,
                    decision_type=decision.decision_type.value,
                    compliance_state=decision.compliance_state.value,
                    anxiety_level=decision.anxiety_level.value,
                    configuration_target=decision.configuration_target,
                    optimization_parameters=decision.optimization_parameters,
                    user_pattern_confidence=decision.user_pattern_confidence,
                    compliance_explanation=decision.compliance_explanation,
                    anxiety_explanation=decision.anxiety_explanation,
                    technical_details=decision.technical_details,
                    expected_improvement=decision.expected_improvement,
                    confidence_level=decision.confidence_level,
                    paper_bags_consumed=decision.paper_bags_consumed,
                    timestamp=decision.timestamp
                )
                
                session.add(decision_log)
                
                # Log anxiety event if panic level
                if decision.is_panicking:
                    anxiety_event = AnxietyEvent(
                        timestamp=decision.timestamp,
                        trigger=f"Decision: {decision.decision_type.value}",
                        anxiety_level_before=50.0,  # Estimate
                        anxiety_level_after=80.0,   # Panic level
                        multiplier=1.5,
                        paper_bags_consumed=decision.paper_bags_consumed,
                        hamster_involved='hamster' in decision.compliance_explanation.lower(),
                        resolution='decision_made'
                    )
                    await self.store_anxiety_event(anxiety_event)
                
                await session.commit()
                return decision_log.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store decision (anxiety spike!): {str(e)}")
    
    async def store_compliance_violation(self, user_id: str, violation: ComplianceViolation):
        """Store compliance violation with anxiety tracking"""
        
        async with self.session_factory() as session:
            try:
                compliance_record = StickComplianceHistory(
                    user_id=user_id,
                    violation_type=violation.violation_type,
                    measured_value=violation.measured_value,
                    threshold_value=violation.threshold_value,
                    anxiety_adjusted_threshold=violation.anxiety_adjusted_threshold,
                    severity=violation.severity,
                    recommendation=violation.recommendation,
                    anxiety_impact=violation.anxiety_impact,
                    paper_bags_triggered=violation.paper_bags_triggered,
                    resolved=violation.resolved,
                    timestamp=violation.timestamp
                )
                
                session.add(compliance_record)
                
                # Log the anxiety impact
                if violation.anxiety_impact > 0:
                    anxiety_event = AnxietyEvent(
                        timestamp=violation.timestamp,
                        trigger=f"Compliance violation: {violation.violation_type}",
                        anxiety_level_before=25.0,  # Base anxiety
                        anxiety_level_after=25.0 + (violation.anxiety_impact * 10),
                        multiplier=violation.anxiety_impact,
                        paper_bags_consumed=violation.paper_bags_triggered,
                        hamster_involved=False,
                        resolution='violation_documented'
                    )
                    await self.store_anxiety_event(anxiety_event)
                
                await session.commit()
                return compliance_record.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick hyperventilated while storing violation: {str(e)}")
    
    async def get_anxiety_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get anxiety analytics for The Stick"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get anxiety events
                anxiety_query = select(StickAnxietyLog).where(
                    StickAnxietyLog.timestamp >= cutoff_date
                ).order_by(desc(StickAnxietyLog.timestamp))
                
                result = await session.execute(anxiety_query)
                anxiety_events = result.scalars().all()
                
                # Calculate statistics
                if anxiety_events:
                    avg_anxiety = sum(e.anxiety_level_after for e in anxiety_events) / len(anxiety_events)
                    max_anxiety = max(e.anxiety_level_after for e in anxiety_events)
                    total_paper_bags = sum(e.paper_bags_consumed for e in anxiety_events)
                    hamster_incidents = sum(1 for e in anxiety_events if e.hamster_involved)
                else:
                    avg_anxiety = 25.0  # Base nervous level
                    max_anxiety = 25.0
                    total_paper_bags = 0
                    hamster_incidents = 0
                
                # Get paper bag usage
                bag_query = select(
                    func.sum(StickPaperBagUsage.bags_consumed),
                    func.sum(StickPaperBagUsage.bags_added)
                ).where(StickPaperBagUsage.timestamp >= cutoff_date)
                
                bag_result = await session.execute(bag_query)
                bags_consumed, bags_added = bag_result.one()
                
                return {
                    'period_days': days,
                    'anxiety_statistics': {
                        'average_anxiety': avg_anxiety,
                        'peak_anxiety': max_anxiety,
                        'total_anxiety_events': len(anxiety_events),
                        'hamster_related_incidents': hamster_incidents
                    },
                    'paper_bag_statistics': {
                        'total_consumed': bags_consumed or 0,
                        'total_added': bags_added or 0,
                        'net_usage': (bags_consumed or 0) - (bags_added or 0),
                        'average_daily_consumption': (bags_consumed or 0) / days if days > 0 else 0
                    },
                    'top_anxiety_triggers': self._analyze_anxiety_triggers(anxiety_events),
                    'anxiety_trend': 'increasing' if len(anxiety_events) > days else 'stable'
                }
                
            except Exception as e:
                raise Exception(f"The Stick couldn't analyze anxiety data: {str(e)}")
    
    def _analyze_anxiety_triggers(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Analyze common anxiety triggers"""
        
        trigger_counts = {}
        for event in events:
            trigger = event.trigger
            if trigger not in trigger_counts:
                trigger_counts[trigger] = {'count': 0, 'total_anxiety': 0, 'paper_bags': 0}
            
            trigger_counts[trigger]['count'] += 1
            trigger_counts[trigger]['total_anxiety'] += event.anxiety_level_after
            trigger_counts[trigger]['paper_bags'] += event.paper_bags_consumed
        
        # Sort by frequency
        sorted_triggers = sorted(
            trigger_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]  # Top 5
        
        return [
            {
                'trigger': trigger,
                'occurrences': data['count'],
                'average_anxiety': data['total_anxiety'] / data['count'],
                'total_paper_bags': data['paper_bags']
            }
            for trigger, data in sorted_triggers
        ]
    
    async def get_hamster_encounter_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get hamster encounter history - The Stick's nightmare log"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = select(StickHamsterEncounters).where(
                    and_(
                        StickHamsterEncounters.user_id == user_id,
                        StickHamsterEncounters.timestamp >= cutoff_date
                    )
                ).order_by(desc(StickHamsterEncounters.timestamp))
                
                result = await session.execute(query)
                encounters = result.scalars().all()
                
                return [
                    {
                        'timestamp': enc.timestamp.isoformat(),
                        'hamsters_present': enc.hamsters_present.split(','),
                        'locations': {
                            'steve': enc.steve_location,
                            'bob': enc.bob_location,
                            'carl': enc.carl_location
                        },
                        'panic_level': enc.panic_level,
                        'anxiety_multiplier': enc.anxiety_multiplier,
                        'infrastructure_risk': enc.infrastructure_risk,
                        'paper_bags_consumed': enc.paper_bags_consumed,
                        'stick_response': enc.stick_response
                    }
                    for enc in encounters
                ]
                
            except Exception as e:
                raise Exception(f"Error retrieving hamster nightmares: {str(e)}")
    
    async def check_paper_bag_supply(self) -> PaperBagInventory:
        """Check current paper bag inventory status"""
        
        async with self.session_factory() as session:
            try:
                # Get all usage
                total_consumed = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_consumed))
                )
                total_added = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_added))
                )
                
                consumed = total_consumed.scalar() or 0
                added = total_added.scalar() or 0
                current_stock = added - consumed
                
                # Get weekly consumption
                week_ago = datetime.now() - timedelta(days=7)
                week_consumed = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_consumed)).where(
                        StickPaperBagUsage.timestamp >= week_ago
                    )
                )
                
                weekly = week_consumed.scalar() or 0
                daily_avg = weekly / 7.0
                
                # Calculate when resupply needed
                days_remaining = current_stock / daily_avg if daily_avg > 0 else 999
                next_resupply = datetime.now() + timedelta(days=days_remaining - 2)  # 2 day buffer
                
                return PaperBagInventory(
                    current_stock=current_stock,
                    consumption_today=await self._get_daily_consumption(),
                    consumption_week=weekly,
                    last_resupply=datetime.now(),  # Would need to track this properly
                    next_resupply_needed=next_resupply,
                    average_daily_consumption=daily_avg,
                    emergency_reserve=10,  # Always keep 10 for emergencies
                    anxiety_threshold_for_use=60.0
                )
                
            except Exception as e:
                raise Exception(f"Paper bag inventory check failed (PANIC!): {str(e)}")
    
    async def recall_everything(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """The Stick's eidetic memory - recall EVERYTHING"""
        
        async with self.session_factory() as session:
            try:
                query = select(StickMemoryBank)
                
                if filters:
                    if 'importance' in filters:
                        query = query.where(StickMemoryBank.importance == filters['importance'])
                    if 'never_forget' in filters and filters['never_forget']:
                        query = query.where(StickMemoryBank.never_forget == True)
                    if 'hamster_related' in filters and filters['hamster_related']:
                        query = query.where(StickMemoryBank.related_hamsters.isnot(None))
                
                query = query.order_by(desc(StickMemoryBank.timestamp)).limit(1000)  # Sanity limit
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                return [
                    {
                        'timestamp': mem.timestamp.isoformat(),
                        'event_type': mem.event_type,
                        'details': mem.details,
                        'anxiety_level': mem.anxiety_level,
                        'importance': mem.importance,
                        'related_hamsters': mem.related_hamsters.split(',') if mem.related_hamsters else [],
                        'compliance_impact': mem.compliance_impact,
                        'never_forget': mem.never_forget
                    }
                    for mem in memories
                ]
                
            except Exception as e:
                raise Exception(f"Memory recall failed - The Stick is distressed: {str(e)}")
    
    async def get_stick_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get The Stick's performance metrics with anxiety context"""
        
        async with self.session_factory() as session:
            try:
                # Get decision count by anxiety level
                anxiety_decisions = await session.execute(
                    select(
                        StickDecisionLog.anxiety_level,
                        func.count(StickDecisionLog.id)
                    ).where(
                        StickDecisionLog.user_id == user_id
                    ).group_by(StickDecisionLog.anxiety_level)
                )
                
                anxiety_breakdown = {row[0]: row[1] for row in anxiety_decisions}
                
                # Get compliance violations with anxiety impact
                high_anxiety_violations = await session.execute(
                    select(func.count(StickComplianceHistory.id)).where(
                        and_(
                            StickComplianceHistory.user_id == user_id,
                            StickComplianceHistory.anxiety_impact > 2.0
                        )
                    )
                )
                
                # Get hamster encounters
                hamster_encounters = await session.execute(
                    select(func.count(StickHamsterEncounters.id)).where(
                        StickHamsterEncounters.user_id == user_id
                    )
                )
                
                # Get paper bag consumption
                total_bags = await session.execute(
                    select(func.sum(StickPaperBagUsage.bags_consumed))
                )
                
                # Get pattern confidence
                pattern_data = await session.execute(
                    select(StickUserPatterns).where(
                        StickUserPatterns.user_id == user_id
                    )
                )
                
                pattern = pattern_data.scalar_one_or_none()
                
                return {
                    'anxiety_driven_decisions': anxiety_breakdown,
                    'total_decisions': sum(anxiety_breakdown.values()),
                    'high_anxiety_violations': high_anxiety_violations.scalar() or 0,
                    'hamster_encounters': hamster_encounters.scalar() or 0,
                    'total_paper_bags_consumed': total_bags.scalar() or 0,
                    'pattern_confidence': pattern.confidence_score if pattern else 0.0,
                    'observation_count': pattern.observation_count if pattern else 0,
                    'anxiety_correlation': pattern.anxiety_correlation if pattern else 0.0,
                    'hypervigilance_effectiveness': self._calculate_effectiveness(anxiety_breakdown),
                    'stick_status': 'ANXIOUSLY_EFFECTIVE'
                }
                
            except Exception as e:
                raise Exception(f"The Stick failed to calculate metrics (concerning!): {str(e)}")
    
    def _calculate_effectiveness(self, anxiety_breakdown: Dict[str, int]) -> float:
        """Calculate effectiveness based on anxiety levels"""
        
        if not anxiety_breakdown:
            return 0.0
        
        # Higher anxiety = better detection (to a point)
        effectiveness_weights = {
            'calm': 0.5,
            'nervous': 0.7,
            'anxious': 0.9,
            'panicking': 0.8,  # Slightly less effective when panicking
            'full_panic': 0.6,  # Reduced effectiveness at max panic
            'paper_bag_breathing': 0.4  # Limited effectiveness while breathing into bag
        }
        
        total_weighted = sum(
            anxiety_breakdown.get(level, 0) * weight
            for level, weight in effectiveness_weights.items()
        )
        total_decisions = sum(anxiety_breakdown.values())
        
        return total_weighted / total_decisions if total_decisions > 0 else 0.5
    
    async def log_system_event(self, event_type: str, details: Dict[str, Any], anxiety_impact: float = 0.0):
        """Log any system event to The Stick's memory"""
        
        # Determine importance based on event type and anxiety impact
        importance = 'CRITICAL' if anxiety_impact > 5.0 else \
                    'HIGH' if anxiety_impact > 2.0 else \
                    'MEDIUM' if anxiety_impact > 0 else 'LOW'
        
        # Check for hamster involvement
        event_str = json.dumps(details).lower()
        hamster_names = ['steve', 'bob', 'carl']
        related_hamsters = [name.capitalize() for name in hamster_names if name in event_str]
        
        memory_entry = StickMemoryEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            details=details,
            anxiety_level=anxiety_impact * 10,  # Convert to percentage
            importance=importance,
            related_hamsters=related_hamsters,
            compliance_impact='monitoring',
            never_forget=bool(related_hamsters) or anxiety_impact > 3.0
        )
        
        await self.store_memory_entry(memory_entry)
    
    async def cleanup_old_observations(self, days_to_keep: int = 90):
        """Clean up old observations - but The Stick NEVER forgets critical events"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Only clean up low-importance, non-critical memories
                await session.execute(
                    delete(StickMemoryBank).where(
                        and_(
                            StickMemoryBank.timestamp < cutoff_date,
                            StickMemoryBank.importance == 'LOW',
                            StickMemoryBank.never_forget == False,
                            StickMemoryBank.related_hamsters.is_(None)
                        )
                    )
                )
                
                # Clean up old decision logs (but keep high-anxiety ones)
                old_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
                
                await session.execute(
                    delete(StickDecisionLog).where(
                        and_(
                            StickDecisionLog.timestamp < old_cutoff,
                            StickDecisionLog.anxiety_level.in_(['calm', 'nervous'])
                        )
                    )
                )
                
                await session.commit()
                
                # Log the cleanup
                await self.log_system_event(
                    'memory_cleanup',
                    {
                        'cleaned_before': cutoff_date.isoformat(),
                        'kept_critical_memories': True,
                        'kept_hamster_memories': True,
                        'kept_high_anxiety_events': True
                    },
                    anxiety_impact=0.5  # Cleaning memories is slightly anxiety-inducing
                )
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick's memory cleanup failed (very concerning!): {str(e)}")