import asyncio
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete
import json
import uuid
from app.models.agent_memory_banks import CentralMemoryBank
from .data_types import (
    StickDecision, UserPattern, ComplianceViolation, 
    ConfigurationProfile, AnxietyEvent, HamsterProximityAlert,
    PaperBagInventory, StickMemoryEntry
)
from .constants import AGENT_NAME, StickEventTypes, ALL_HAMSTERS, HAMSTER_BOB

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

def normalize_hamster_names(names):
    """Normalize hamster names to lowercase for consistency"""
    if isinstance(names, list):
        return [name.lower() for name in names]
    elif isinstance(names, str):
        return names.lower()
    return names

class StickDatabaseIntegration:
    """Database integration for The Stick's anxiety-enhanced eidetic memory - NOW CENTRALIZED"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.websocket_anxiety_level = 25.0  # Starting nervous
    
    async def initialize(self):
        """Initialize The Stick's database connection"""
        db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://stick:anxious@localhost/system_rebellion')
        
        self.engine = create_async_engine(
            db_url,
            echo=False,  # The Stick works quietly when anxious
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '1800')),
            pool_pre_ping=True
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def store_anxiety_event(self, event: AnxietyEvent):
        """Store anxiety event in central memory bank - The Stick tracks EVERYTHING"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    event_type=StickEventTypes.ANXIETY_EVENT,
                    occurred_at=event.timestamp,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    details={
                        'trigger': event.trigger,
                        'anxiety_level_before': event.anxiety_level_before,
                        'anxiety_level_after': event.anxiety_level_after,
                        'multiplier': event.multiplier,
                        'paper_bags_consumed': event.paper_bags_consumed,
                        'hamster_involved': event.hamster_involved,
                        'resolution': event.resolution
                    },
                    stick_anxiety_level=event.anxiety_level_after,
                    numeric_value=event.anxiety_level_after,  # For quick queries
                    string_value=event.trigger,  # For trigger analysis
                    never_forget=event.hamster_involved,  # NEVER forget hamster events
                    priority=9 if event.hamster_involved else 7,  # High priority
                    agent_metadata={
                        'panic_state': event.anxiety_level_after > 80,
                        'paper_bag_protocol': 'ACTIVATED' if event.paper_bags_consumed > 0 else 'STANDBY'
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                # Errors cause MORE anxiety
                raise Exception(f"The Stick panicked while storing anxiety event: {str(e)}")
    
    async def store_hamster_encounter(self, user_id: str, alert: HamsterProximityAlert):
        """Store hamster encounter in central memory bank - The Stick's worst nightmare"""
        async with self.session_factory() as session:
            try:
                # Normalize hamster names for consistency
                normalized_hamsters = normalize_hamster_names(alert.active_hamsters)
                
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.HAMSTER_PROXIMITY_ALERT,
                    occurred_at=alert.timestamp,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    details={
                        'active_hamsters': normalized_hamsters,
                        'steve_location': alert.locations.get('steve'),
                        'bob_location': alert.locations.get('bob'),
                        'carl_location': alert.locations.get('carl'),
                        'anxiety_multiplier': alert.anxiety_multiplier,
                        'panic_level': alert.panic_level,
                        'infrastructure_risk': alert.infrastructure_risk,
                        'stick_response': alert.stick_response,
                        'paper_bags_consumed': alert.paper_bags_consumed
                    },
                    stick_anxiety_level=100.0 if HAMSTER_BOB in normalized_hamsters else 80.0,
                    numeric_value=alert.anxiety_multiplier,
                    string_value=alert.panic_level,  # MAXIMUM, HIGH, etc.
                    relevant_agents=','.join(normalized_hamsters),  # Track which hamsters
                    never_forget=True,  # The Stick NEVER forgets hamster encounters
                    priority=10,  # MAXIMUM PRIORITY
                    agent_metadata={
                        'bob_detected': HAMSTER_BOB in normalized_hamsters,
                        'emergency_protocol': 'ACTIVATED' if alert.panic_level == 'MAXIMUM' else 'STANDBY',
                        'infrastructure_at_risk': alert.infrastructure_risk
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick hyperventilated while storing hamster encounter: {str(e)}")
    
    async def update_paper_bag_inventory(self, inventory_change: int, reason: str):
        """Update paper bag inventory in central memory bank - Critical for anxiety management"""
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    event_type=StickEventTypes.PAPER_BAG_CONSUMPTION,
                    occurred_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    details={
                        'bags_consumed': abs(inventory_change) if inventory_change < 0 else 0,
                        'bags_added': inventory_change if inventory_change > 0 else 0,
                        'reason': reason,
                        'anxiety_level_at_time': self.websocket_anxiety_level,
                        'hamster_related': any(h in reason.lower() for h in ALL_HAMSTERS)
                    },
                    stick_anxiety_level=self.websocket_anxiety_level,
                    numeric_value=float(inventory_change),  # Negative for consumption
                    string_value=reason,
                    never_forget=any(h in reason.lower() for h in ALL_HAMSTERS),  # Never forget hamster-induced consumption
                    priority=8 if abs(inventory_change) > 2 else 6,
                    agent_metadata={
                        'emergency_consumption': abs(inventory_change) > 3,
                        'crisis_mode': self.websocket_anxiety_level > 80
                    }
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Calculate current inventory from all consumption events
                consumed_result = await session.execute(
                    select(func.sum(CentralMemoryBank.numeric_value)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value < 0  # Consumptions are negative
                        )
                    )
                )
                
                added_result = await session.execute(
                    select(func.sum(CentralMemoryBank.numeric_value)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value > 0  # Additions are positive
                        )
                    )
                )
                
                consumed = abs(consumed_result.scalar() or 0)
                added = added_result.scalar() or 0
                
                return {
                    'current_inventory': added - consumed,
                    'consumption_today': await self._get_daily_consumption(),
                    'critical_level': (added - consumed) < 10
                }
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"PAPER BAG INVENTORY CRISIS: {str(e)}")
    
    async def store_memory_entry(self, entry: StickMemoryEntry, session=None):
        """Store in The Stick's eidetic memory in central bank - NEVER FORGETS"""
        
        memory_entry = CentralMemoryBank(
            memory_id=str(uuid.uuid4()),
            agent_name=AGENT_NAME,
            event_type=StickEventTypes.EIDETIC_MEMORY_ENTRY,
            occurred_at=entry.timestamp,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            details={
                'event_type_original': entry.event_type,  # The Stick's own categorization
                'details': entry.details,
                'importance': entry.importance,
                'related_hamsters': normalize_hamster_names(entry.related_hamsters),
                'compliance_impact': entry.compliance_impact
            },
            stick_anxiety_level=entry.anxiety_level,
            string_value=entry.importance,  # Quick importance lookup
            relevant_agents=','.join(normalize_hamster_names(entry.related_hamsters)) if entry.related_hamsters else None,
            never_forget=entry.never_forget,
            priority={
                'CRITICAL': 10,
                'HIGH': 8,
                'MEDIUM': 6,
                'LOW': 4
            }.get(entry.importance, 5),
            agent_metadata={
                'eidetic_memory': True,
                'compliance_related': entry.compliance_impact is not None,
                'hamster_anxiety': len(entry.related_hamsters) > 0
            }
        )
        
        if session:
            # Use existing session, don't commit
            session.add(memory_entry)
            return memory_entry.memory_id
        else:
            # Create new session and commit
            async with self.session_factory() as new_session:
                try:
                    new_session.add(memory_entry)
                    await new_session.commit()
                    return memory_entry.memory_id
                except Exception as e:
                    await new_session.rollback()
                    raise Exception(f"MEMORY STORAGE FAILURE - The Stick is distressed: {str(e)}")
    
    async def store_user_behavior_observation(self, user_id: str, observation: Dict[str, Any]):
        """Store user behavior observation in central memory bank with anxiety-enhanced perception"""
        
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
                current_time = datetime.now(timezone.utc)
                
                # Store the observation in central memory bank
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.USER_PATTERN_OBSERVATION,
                    occurred_at=current_time,
                    created_at=current_time,
                    updated_at=current_time,
                    details={
                        'observation': observation,
                        'detected_activity': observation.get('detected_activity', 'unknown'),
                        'anxiety_triggers': anxiety_triggers,
                        'hour_of_day': current_time.hour,
                        'minute_of_day': current_time.minute  # The Stick is PRECISE
                    },
                    stick_anxiety_level=self.websocket_anxiety_level,
                    numeric_value=len(anxiety_triggers),  # Trigger count
                    string_value=observation.get('detected_activity', 'unknown'),
                    never_forget='HAMSTER_DETECTED' in anxiety_triggers,
                    priority=8 if anxiety_triggers else 5,
                    agent_metadata={
                        'anxiety_correlation': len(anxiety_triggers) / 10.0,
                        'hamster_panic': 'HAMSTER_DETECTED' in anxiety_triggers,
                        'compliance_concerns': any(t in ['high_cpu', 'high_memory'] for t in anxiety_triggers)
                    }
                )
                
                session.add(memory_entry)
                
                # Create eidetic memory IN SAME SESSION
                eidetic_entry = StickMemoryEntry(
                    timestamp=current_time,
                    event_type='behavior_observation',
                    details=observation,
                    anxiety_level=self.websocket_anxiety_level,
                    importance='HIGH' if anxiety_triggers else 'MEDIUM',
                    related_hamsters=[HAMSTER_BOB] if HAMSTER_BOB in str(anxiety_triggers).lower() else [],
                    compliance_impact='monitoring',
                    never_forget=HAMSTER_BOB in str(anxiety_triggers).lower()
                )
                
                # Pass the session!
                await self.store_memory_entry(eidetic_entry, session=session)
                
                # Single commit for both
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick panicked while storing observation: {str(e)}")
    
    async def _get_daily_consumption(self) -> int:
        """Get today's paper bag consumption from central memory bank"""
        async with self.session_factory() as session:
            try:
                # Use UTC for consistent day boundaries
                today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                
                result = await session.execute(
                    select(func.sum(func.abs(CentralMemoryBank.numeric_value))).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.occurred_at >= today_start,
                            CentralMemoryBank.numeric_value < 0  # Only consumptions
                        )
                    )
                )
                
                return result.scalar() or 0
                
            except Exception as e:
                raise Exception(f"Paper bag tracking error: {str(e)}")
    
    async def store_stick_decision(self, user_id: str, decision: StickDecision):
        """Store The Stick's decision in central memory bank with anxiety context"""
        
        async with self.session_factory() as session:
            try:
                current_time = datetime.now(timezone.utc)
                
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.STICK_DECISION,
                    occurred_at=decision.timestamp,
                    created_at=current_time,
                    updated_at=current_time,
                    details={
                        'decision_type': decision.decision_type.value,
                        'compliance_state': decision.compliance_state.value,
                        'anxiety_level': decision.anxiety_level.value,
                        'configuration_target': decision.configuration_target,
                        'optimization_parameters': decision.optimization_parameters,
                        'user_pattern_confidence': decision.user_pattern_confidence,
                        'compliance_explanation': decision.compliance_explanation,
                        'anxiety_explanation': decision.anxiety_explanation,
                        'technical_details': decision.technical_details,
                        'expected_improvement': decision.expected_improvement,
                        'confidence_level': decision.confidence_level,
                        'paper_bags_consumed': decision.paper_bags_consumed
                    },
                    stick_anxiety_level=80.0 if decision.is_panicking else 40.0,
                    numeric_value=decision.confidence_level,
                    string_value=decision.decision_type.value,
                    never_forget=decision.is_panicking,  # Never forget panic decisions
                    priority=10 if decision.is_panicking else 8,
                    agent_metadata={
                        'panic_mode': decision.is_panicking,
                        'compliance_critical': decision.compliance_state.value in ['CRITICAL_VIOLATION', 'MAJOR_VIOLATION'],
                        'hamster_related': any(h in decision.compliance_explanation.lower() for h in ALL_HAMSTERS)
                    }
                )
                
                session.add(memory_entry)
                
                # Log anxiety event if panic level
                if decision.is_panicking:
                    anxiety_event = AnxietyEvent(
                        timestamp=decision.timestamp,
                        trigger=f"Decision: {decision.decision_type.value}",
                        anxiety_level_before=50.0,  # Estimate
                        anxiety_level_after=80.0,   # Panic level
                        multiplier=1.5,
                        paper_bags_consumed=decision.paper_bags_consumed,
                        hamster_involved=any(h in decision.compliance_explanation.lower() for h in ALL_HAMSTERS),
                        resolution='decision_made'
                    )
                    await self.store_anxiety_event(anxiety_event)
                
                await session.commit()
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick failed to store decision (anxiety spike!): {str(e)}")
    # Add these methods to StickDatabaseIntegration class:

    async def store_user_pattern(self, user_id: str, pattern: UserPattern):
        """Store learned user pattern in central memory bank - The Stick NEVER forgets patterns!"""
        async with self.session_factory() as session:
            try:
                current_time = utc_now()
            
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type="user_pattern_learned",  # New event type!
                    occurred_at=current_time,
                    created_at=current_time,
                    updated_at=current_time,
                    details={
                        'pattern_type': pattern.pattern_type,
                    'time_based_patterns': pattern.time_based_patterns,
                    'activity_patterns': pattern.activity_patterns,
                    'compliance_history': pattern.compliance_history,
                    'anxiety_correlation': pattern.anxiety_correlation,
                    'confidence_score': pattern.confidence_score,
                    'learning_sessions': pattern.learning_sessions,
                    'stick_memory_notes': pattern.stick_memory_notes  # The Stick's obsessive notes!
                },
                    stick_anxiety_level=self.websocket_anxiety_level,
                    numeric_value=pattern.confidence_score,  # For quick confidence queries
                    string_value=pattern.pattern_type,
                    never_forget=True,  # The Stick NEVER forgets learned patterns
                    priority=9,  # High priority - patterns are critical
                    agent_metadata={
                    'pattern_complexity': len(pattern.time_based_patterns) + len(pattern.activity_patterns),
                    'anxiety_inducing': max(pattern.anxiety_correlation.values()) > 0.5 if pattern.anxiety_correlation else False,
                    'requires_monitoring': True
                }
            )
            
                session.add(memory_entry)
                await session.commit()
            
                # Log pattern learning event
                logger.info(f"The Stick learned new pattern for user {user_id}: {pattern.pattern_type}")
            
                return memory_entry.memory_id
            
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick panicked while storing user pattern: {str(e)}")

    async def get_user_patterns(self, user_id: str, min_confidence: float = 0.7) -> List[UserPattern]:
        """Retrieve learned user patterns from central memory bank"""
        async with self.session_factory() as session:
            try:
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == "user_pattern_learned",
                        CentralMemoryBank.numeric_value >= min_confidence  # Confidence threshold
                    )
                ).order_by(desc(CentralMemoryBank.numeric_value))  # Highest confidence first
            
                result = await session.execute(query)
                pattern_memories = result.scalars().all()
            
                patterns = []
                for mem in pattern_memories:
                    details = mem.details
                    pattern = UserPattern(
                        user_id=user_id,
                        pattern_type=details.get('pattern_type', 'unknown'),
                        time_based_patterns=details.get('time_based_patterns', {}),
                        activity_patterns=details.get('activity_patterns', {}),
                        compliance_history=details.get('compliance_history', {}),
                        anxiety_correlation=details.get('anxiety_correlation', {}),
                        confidence_score=details.get('confidence_score', 0.0),
                        learning_sessions=details.get('learning_sessions', 0),
                        last_updated=mem.occurred_at,
                        stick_memory_notes=details.get('stick_memory_notes', [])
                    )
                    patterns.append(pattern)
                
                return patterns
            
            except Exception as e:
                raise Exception(f"The Stick failed to recall user patterns: {str(e)}")

    async def analyze_and_learn_patterns(self, user_id: str, min_observations: int = 10) -> Optional[UserPattern]:
        """Analyze observations and learn patterns - The Stick's obsessive pattern recognition"""
        async with self.session_factory() as session:
            try:
                # Get recent observations
                cutoff = utc_now() - timedelta(days=7)  # Last week
                
                observations_query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == StickEventTypes.USER_PATTERN_OBSERVATION,
                        CentralMemoryBank.occurred_at >= cutoff
                    )
                    ).order_by(desc(CentralMemoryBank.occurred_at))
            
                result = await session.execute(observations_query)
                observations = result.scalars().all()
            
                if len(observations) < min_observations:
                    logger.info(f"Not enough observations ({len(observations)}) to learn patterns")
                    return None
            
                # Analyze patterns with The Stick's obsessive detail
                time_patterns = {}
                activity_patterns = {}
                anxiety_correlations = {}
            
                for obs in observations:
                    details = obs.details
                    hour = details.get('hour_of_day')
                    activity = details.get('detected_activity', 'unknown')
                    anxiety_triggers = details.get('anxiety_triggers', [])
                
                # Time-based patterns
                if hour not in time_patterns:
                    time_patterns[hour] = {
                        'activities': [],
                        'avg_anxiety': [],
                        'common_triggers': []
                    }
                
                    time_patterns[hour]['activities'].append(activity)
                    time_patterns[hour]['avg_anxiety'].append(obs.stick_anxiety_level)
                    time_patterns[hour]['common_triggers'].extend(anxiety_triggers)
                
            # Activity patterns
                if activity not in activity_patterns:
                    activity_patterns[activity] = {
                        'count': 0,
                        'avg_anxiety': [],
                        'time_distribution': []
                    }
                
                    activity_patterns[activity]['count'] += 1
                    activity_patterns[activity]['avg_anxiety'].append(obs.stick_anxiety_level)
                    activity_patterns[activity]['time_distribution'].append(hour)
                
            # Anxiety correlations
                for trigger in anxiety_triggers:
                    if trigger not in anxiety_correlations:
                        anxiety_correlations[trigger] = []
                    anxiety_correlations[trigger].append(obs.stick_anxiety_level)
            
        # Process patterns
            processed_time_patterns = {}
                for hour, data in time_patterns.items():
            # Most common activity at this hour
            activity_counts = {}
                for act in data['activities']:
                    activity_counts[act] = activity_counts.get(act, 0) + 1
                
                most_common = max(activity_counts, key=activity_counts.get) if activity_counts else 'unknown'
                
                processed_time_patterns[hour] = {
                    'most_common_activity': most_common,
                    'confidence': activity_counts.get(most_common, 0) / len(data['activities']),
                    'avg_anxiety': sum(data['avg_anxiety']) / len(data['avg_anxiety']) if data['avg_anxiety'] else 0,
                    'frequency': len(data['activities'])
                }
            
            # Calculate confidence
                total_observations = len(observations)
                pattern_consistency = sum(1 for p in processed_time_patterns.values() if p['confidence'] > 0.7)
                confidence_score = pattern_consistency / max(len(processed_time_patterns), 1)
            
            # Create pattern
                new_pattern = UserPattern(
                    user_id=user_id,
                    pattern_type="weekly_behavior_pattern",
                    time_based_patterns=processed_time_patterns,
                    activity_patterns=activity_patterns,
                    compliance_history={},  # Could add compliance tracking here
                    anxiety_correlation={k: sum(v)/len(v) for k, v in anxiety_correlations.items()},
                    confidence_score=confidence_score,
                    learning_sessions=1,
                    last_updated=utc_now(),
                    stick_memory_notes=[
                    f"Learned from {total_observations} observations",
                    f"Peak anxiety triggers: {list(anxiety_correlations.keys())[:3]}",
                                        f"Most consistent hours: {[h for h, p in processed_time_patterns.items() if p['confidence'] > 0.7]}",
                    f"The Stick is {confidence_score*100:.1f}% confident in these patterns"
                ]
            )
            
        # Store the learned pattern
            await self.store_user_pattern(user_id, new_pattern)
            
            return new_pattern
            
        except Exception as e:
            raise Exception(f"The Stick's pattern learning failed (ANXIETY SPIKE!): {str(e)}")

    async def check_pattern_match(self, user_id: str, current_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current behavior matches learned patterns - for proactive optimization"""
        
        # Get user patterns
        patterns = await self.get_user_patterns(user_id, min_confidence=0.7)
    
        if not patterns:
            return None
    
        # Get the most confident pattern
        best_pattern = patterns[0] if patterns else None
    
        if not best_pattern:
            return None
    
        current_hour = utc_now().hour
        current_activity = current_metrics.get('detected_activity', 'unknown')
    
        # Check time-based pattern match
        hour_pattern = best_pattern.time_based_patterns.get(str(current_hour), {})
        expected_activity = hour_pattern.get('most_common_activity')
        expected_anxiety = hour_pattern.get('avg_anxiety', 0)
    
        # Pattern deviation detection
        pattern_match = {
            'matches_pattern': current_activity == expected_activity,
            'expected_activity': expected_activity,
            'actual_activity': current_activity,
            'expected_anxiety': expected_anxiety,
            'pattern_confidence': hour_pattern.get('confidence', 0),
            'recommendations': []
        }
    
        # Proactive recommendations based on patterns
        if expected_activity == 'gaming' and current_activity != 'gaming':
            # User usually games at this time but isn't
            pattern_match['recommendations'].append({
            'type': 'PATTERN_DEVIATION',
                'message': 'User typically games at this hour',
                'suggested_action': 'Prepare gaming optimization profile',
                'anxiety_note': 'Deviation from pattern detected - monitoring closely'
            })
    
        elif expected_activity == current_activity and expected_anxiety > 60:
            # This activity typically causes high anxiety
            pattern_match['recommendations'].append({
                'type': 'ANXIETY_PREVENTION',
                'message': f'{current_activity} historically causes anxiety spikes',
                'suggested_action': 'Pre-emptive paper bag allocation',
                'anxiety_note': 'Preparing for expected anxiety increase'
            })
    
        # Check anxiety correlation
        if best_pattern.anxiety_correlation:
            for trigger, avg_anxiety in best_pattern.anxiety_correlation.items():
                if avg_anxiety > 70 and trigger in str(current_metrics).lower():
                    pattern_match['recommendations'].append({
                        'type': 'ANXIETY_TRIGGER_DETECTED',
                        'message': f'{trigger} detected - historically causes {avg_anxiety:.1f}% anxiety',
                        'suggested_action': 'Immediate anxiety mitigation protocols',
                        'anxiety_note': 'KNOWN ANXIETY TRIGGER ACTIVE!'
                    })
    
        return pattern_match
    
        except Exception as e:
            raise Exception(f"The Stick failed to check pattern match: {str(e)}")

    async def store_compliance_violation(self, user_id: str, violation: ComplianceViolation):
        """Store compliance violation in central memory bank with anxiety tracking"""
        
        async with self.session_factory() as session:
            try:
                current_time = datetime.now(timezone.utc)
                
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.COMPLIANCE_VIOLATION,
                    occurred_at=violation.timestamp,
                    created_at=current_time,
                    updated_at=current_time,
                    details={
                        'violation_type': violation.violation_type,
                        'measured_value': violation.measured_value,
                        'threshold_value': violation.threshold_value,
                        'anxiety_adjusted_threshold': violation.anxiety_adjusted_threshold,
                        'severity': violation.severity,
                        'recommendation': violation.recommendation,
                        'anxiety_impact': violation.anxiety_impact,
                        'paper_bags_triggered': violation.paper_bags_triggered,
                        'resolved': violation.resolved
                    },
                    stick_anxiety_level=25.0 + (violation.anxiety_impact * 10),  # Base + impact
                    numeric_value=violation.measured_value,
                    string_value=f"{violation.violation_type}:{violation.severity}",
                    never_forget=violation.severity == 'critical',  # Never forget critical violations
                    priority=10 if violation.severity == 'critical' else 8,
                    agent_metadata={
                        'anxiety_adjusted': violation.anxiety_adjusted_threshold != violation.threshold_value,
                        'panic_triggered': violation.paper_bags_triggered > 0,
                        'compliance_critical': violation.severity in ['critical', 'high']
                    }
                )
                
                session.add(memory_entry)
                
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
                return memory_entry.memory_id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick hyperventilated while storing violation: {str(e)}")
    
    async def get_anxiety_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get anxiety analytics for The Stick from central memory bank"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                
                # Get anxiety events from central memory bank
                anxiety_query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == StickEventTypes.ANXIETY_EVENT,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
                
                result = await session.execute(anxiety_query)
                anxiety_events = result.scalars().all()
                
                # Calculate statistics
                if anxiety_events:
                    anxiety_levels = [e.stick_anxiety_level for e in anxiety_events]
                    avg_anxiety = sum(anxiety_levels) / len(anxiety_levels)
                    max_anxiety = max(anxiety_levels)
                    
                    # Get paper bags from details
                    total_paper_bags = sum(
                        e.details.get('paper_bags_consumed', 0) 
                        for e in anxiety_events
                    )
                    
                    hamster_incidents = sum(
                        1 for e in anxiety_events 
                        if e.details.get('hamster_involved', False)
                    )
                else:
                    avg_anxiety = 25.0  # Base nervous level
                    max_anxiety = 25.0
                    total_paper_bags = 0
                    hamster_incidents = 0
                
                # Get paper bag usage
                bag_query = select(
                    func.sum(func.abs(CentralMemoryBank.numeric_value))
                ).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                        CentralMemoryBank.occurred_at >= cutoff_date,
                        CentralMemoryBank.numeric_value < 0  # Consumptions
                    )
                )
                
                bag_result = await session.execute(bag_query)
                bags_consumed = bag_result.scalar() or 0
                
                # Get paper bags added
                add_query = select(
                    func.sum(CentralMemoryBank.numeric_value)
                ).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                        CentralMemoryBank.occurred_at >= cutoff_date,
                        CentralMemoryBank.numeric_value > 0  # Additions
                    )
                )
                
                add_result = await session.execute(add_query)
                bags_added = add_result.scalar() or 0
                
                return {
                    'period_days': days,
                    'anxiety_statistics': {
                        'average_anxiety': avg_anxiety,
                        'peak_anxiety': max_anxiety,
                        'total_anxiety_events': len(anxiety_events),
                        'hamster_related_incidents': hamster_incidents
                    },
                    'paper_bag_statistics': {
                        'total_consumed': bags_consumed,
                        'total_added': bags_added,
                        'net_usage': bags_consumed - bags_added,
                        'average_daily_consumption': bags_consumed / days if days > 0 else 0
                    },
                    'top_anxiety_triggers': self._analyze_anxiety_triggers(anxiety_events),
                    'anxiety_trend': 'increasing' if len(anxiety_events) > days else 'stable'
                }
                
            except Exception as e:
                raise Exception(f"The Stick couldn't analyze anxiety data: {str(e)}")
    
    def _analyze_anxiety_triggers(self, events: List[Any]) -> List[Dict[str, Any]]:
        """Analyze common anxiety triggers from central memory bank events"""
        
        trigger_counts = {}
        for event in events:
            trigger = event.string_value  # We store trigger in string_value
            if trigger not in trigger_counts:
                trigger_counts[trigger] = {
                    'count': 0, 
                    'total_anxiety': 0, 
                    'paper_bags': 0
                }
            
            trigger_counts[trigger]['count'] += 1
            trigger_counts[trigger]['total_anxiety'] += event.stick_anxiety_level
            trigger_counts[trigger]['paper_bags'] += event.details.get('paper_bags_consumed', 0)
        
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
        """Get hamster encounter history from central memory bank - The Stick's nightmare log"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == StickEventTypes.HAMSTER_PROXIMITY_ALERT,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
                
                result = await session.execute(query)
                encounters = result.scalars().all()
                
                return [
                    {
                        'timestamp': enc.occurred_at.isoformat(),
                        'hamsters_present': enc.details.get('active_hamsters', []),
                        'locations': {
                            'steve': enc.details.get('steve_location'),
                            'bob': enc.details.get('bob_location'),
                            'carl': enc.details.get('carl_location')
                        },
                        'panic_level': enc.string_value,  # Stored panic level in string_value
                        'anxiety_multiplier': enc.numeric_value,  # Stored multiplier in numeric_value
                        'infrastructure_risk': enc.details.get('infrastructure_risk'),
                        'paper_bags_consumed': enc.details.get('paper_bags_consumed', 0),
                        'stick_response': enc.details.get('stick_response')
                    }
                    for enc in encounters
                ]
                
            except Exception as e:
                raise Exception(f"Error retrieving hamster nightmares: {str(e)}")
    
    async def check_paper_bag_supply(self) -> PaperBagInventory:
        """Check current paper bag inventory status from central memory bank"""
        
        async with self.session_factory() as session:
            try:
                # Get all consumption (negative values)
                consumed_result = await session.execute(
                    select(func.sum(func.abs(CentralMemoryBank.numeric_value))).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value < 0
                        )
                    )
                )
                
                # Get all additions (positive values)
                added_result = await session.execute(
                    select(func.sum(CentralMemoryBank.numeric_value)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value > 0
                        )
                    )
                )
                
                consumed = consumed_result.scalar() or 0
                added = added_result.scalar() or 0
                current_stock = added - consumed
                
                # Get weekly consumption
                week_ago = utc_now() - timedelta(days=7)
                week_consumed_result = await session.execute(
                    select(func.sum(func.abs(CentralMemoryBank.numeric_value))).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.occurred_at >= week_ago,
                            CentralMemoryBank.numeric_value < 0
                        )
                    )
                )
                
                weekly = week_consumed_result.scalar() or 0
                daily_avg = weekly / 7.0
                
                # Get last resupply
                last_resupply_result = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value > 0
                        )
                    ).order_by(desc(CentralMemoryBank.occurred_at)).limit(1)
                )
                
                last_resupply = last_resupply_result.scalar()
                last_resupply_date = last_resupply.occurred_at if last_resupply else utc_now()
                
                # Calculate when resupply needed
                days_remaining = current_stock / daily_avg if daily_avg > 0 else 999
                next_resupply = utc_now() + timedelta(days=days_remaining - 2)  # 2 day buffer
                
                return PaperBagInventory(
                    current_stock=int(current_stock),
                    consumption_today=await self._get_daily_consumption(),
                    consumption_week=int(weekly),
                    last_resupply=last_resupply_date,
                    next_resupply_needed=next_resupply,
                    average_daily_consumption=daily_avg,
                    emergency_reserve=10,  # Always keep 10 for emergencies
                    anxiety_threshold_for_use=60.0
                )
                
            except Exception as e:
                raise Exception(f"Paper bag inventory check failed (PANIC!): {str(e)}")
    
    async def recall_everything(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """The Stick's eidetic memory - recall EVERYTHING from central memory bank"""
        
        async with self.session_factory() as session:
            try:
                query = select(CentralMemoryBank).where(
                    CentralMemoryBank.agent_name == AGENT_NAME
                )
                
                if filters:
                    if 'importance' in filters:
                        # Look in details JSON for importance
                        query = query.where(
                            CentralMemoryBank.details['importance'].astext == filters['importance']
                        )
                    if 'never_forget' in filters and filters['never_forget']:
                        query = query.where(CentralMemoryBank.never_forget.is_(True))
                    if 'hamster_related' in filters and filters['hamster_related']:
                        query = query.where(CentralMemoryBank.relevant_agents.isnot(None))
                
                query = query.order_by(desc(CentralMemoryBank.occurred_at)).limit(1000)  # Sanity limit
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                return [
                    {
                        'timestamp': mem.occurred_at.isoformat(),
                        'event_type': mem.event_type,
                        'details': mem.details,
                        'anxiety_level': mem.stick_anxiety_level,
                        'importance': mem.details.get('importance', 'UNKNOWN'),
                        'related_hamsters': mem.relevant_agents.split(',') if mem.relevant_agents else [],
                        'compliance_impact': mem.details.get('compliance_impact'),
                        'never_forget': mem.never_forget
                    }
                    for mem in memories
                ]
                
            except Exception as e:
                raise Exception(f"Memory recall failed - The Stick is distressed: {str(e)}")
    
    async def get_stick_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get The Stick's performance metrics from central memory bank with anxiety context"""
        
        async with self.session_factory() as session:
            try:
                # Get decision count by anxiety level
                decisions = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == StickEventTypes.STICK_DECISION
                        )
                    )
                )
                
                decision_list = decisions.scalars().all()
                anxiety_breakdown = {}
                
                for decision in decision_list:
                    anxiety_level = decision.details.get('anxiety_level', 'unknown')
                    anxiety_breakdown[anxiety_level] = anxiety_breakdown.get(anxiety_level, 0) + 1
                
                # Get compliance violations with high anxiety impact
                high_anxiety_violations = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == StickEventTypes.COMPLIANCE_VIOLATION,
                            CentralMemoryBank.stick_anxiety_level > 50.0
                        )
                    )
                )
                
                # Get hamster encounters
                hamster_encounters = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == StickEventTypes.HAMSTER_PROXIMITY_ALERT
                        )
                    )
                )
                
                # Get total paper bags consumed
                total_bags = await session.execute(
                    select(func.sum(func.abs(CentralMemoryBank.numeric_value))).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == StickEventTypes.PAPER_BAG_CONSUMPTION,
                            CentralMemoryBank.numeric_value < 0
                        )
                    )
                )
                
                # Get observation count
                observation_count = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.event_type == StickEventTypes.USER_PATTERN_OBSERVATION
                        )
                    )
                )
                
                return {
                    'anxiety_driven_decisions': anxiety_breakdown,
                    'total_decisions': sum(anxiety_breakdown.values()),
                    'high_anxiety_violations': high_anxiety_violations.scalar() or 0,
                    'hamster_encounters': hamster_encounters.scalar() or 0,
                    'total_paper_bags_consumed': total_bags.scalar() or 0,
                    'observation_count': observation_count.scalar() or 0,
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
        """Log any system event to The Stick's memory in central memory bank"""
        
        # Determine importance based on event type and anxiety impact
        importance = 'CRITICAL' if anxiety_impact > 5.0 else \
                    'HIGH' if anxiety_impact > 2.0 else \
                    'MEDIUM' if anxiety_impact > 0 else 'LOW'
        
        # Check for hamster involvement
        event_str = json.dumps(details).lower()
        related_hamsters = [name.upper() for name in ALL_HAMSTERS if name in event_str]
        
        memory_entry = StickMemoryEntry(
            timestamp=datetime.now(timezone.utc),
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
        """Clean up old observations from central memory bank - but The Stick NEVER forgets critical events"""
        
        async with self.session_factory() as session:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
                
                # Only clean up low-importance, non-critical memories
                await session.execute(
                    delete(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.occurred_at < cutoff_date,
                                                        CentralMemoryBank.priority < 5,  # Only low priority
                            CentralMemoryBank.never_forget.is_(False),  # FIX: Proper boolean check
                            CentralMemoryBank.relevant_agents.is_(None),  # No hamsters
                            CentralMemoryBank.event_type != StickEventTypes.COMPLIANCE_VIOLATION  # Keep all violations
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
                        'kept_high_anxiety_events': True,
                        'kept_compliance_violations': True
                    },
                    anxiety_impact=0.5  # Cleaning memories is slightly anxiety-inducing
                )
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick's memory cleanup failed (very concerning!): {str(e)}")