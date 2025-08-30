# app/ai_agents/hamsters/database_integration.py
"""
The Hamsters Database Integration - Central Memory Bank Edition
Steve, Bob, and Carl's infrastructure memories stored collectively
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import json

from sqlalchemy import text, select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.models.central_memory_bank import CentralMemoryBank
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction, PinnedMemory,
    upsert_global_pattern, upsert_user_pattern, record_learning_interaction,
    pin_memory, get_user_patterns, LearningTypes, MemoryTypes
)
from .constants import HamstersEventTypes, AGENT_NAME, ALL_HAMSTERS, PRIORITY_MAP
from .datatypes import InfrastructureIntervention, HamsterCommunication, DuctTapeUsage

logger = logging.getLogger("Hamsters.Database")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

class HamstersDatabaseIntegration:
    """
    Database integration for The Hamsters using central memory bank
    Tracks collective and individual hamster activities
    """
    
    def __init__(self, db_getter=None):
        self.logger = logging.getLogger("Hamsters.Database")
        self.engine = None
        self._db_session_maker = None
        self.db_getter = db_getter
        self._initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
            
        try:
            db_config = self._get_database_config()
            
            if db_config['url'].startswith('postgresql'):
                self.engine = create_async_engine(
                    db_config['url'],
                    echo=db_config.get('echo', False),
                    pool_size=db_config.get('pool_size', 10),
                    max_overflow=db_config.get('max_overflow', 20),
                    pool_recycle=db_config.get('pool_recycle', 1800),
                    pool_pre_ping=db_config.get('pool_pre_ping', True),
                    poolclass=QueuePool
                )
            else:
                # SQLite
                self.engine = create_async_engine(
                    db_config['url'],
                    echo=db_config.get('echo', False),
                    connect_args=db_config.get('connect_args', {}),
                    poolclass=NullPool
                )
            
            self._db_session_maker = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            self._initialized = True
            self.logger.info("🐹 Database integration initialized with beer-powered efficiency")
            
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to initialize database: {str(e)}")
            raise
    
    def _get_database_config(self) -> dict:
        """Get database configuration based on environment"""
        env = os.getenv('ENV', 'development').lower()
        
        if env == 'production':
            return {
                'url': os.getenv('DATABASE_URL'),
                'echo': False,
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),
                'pool_pre_ping': True
            }
        elif env == 'test':
            return {
                'url': 'sqlite+aiosqlite:///:memory:',
                'echo': False,
                'connect_args': {"check_same_thread": False}
            }
        else:  # development
            return {
                'url': 'sqlite+aiosqlite:///./system_rebellion.db',
                'echo': True,
                'connect_args': {"check_same_thread": False}
            }
    
    async def get_session(self) -> AsyncSession:
        """Get a database session"""
        if not self._initialized:
            await self.initialize()
        return self._db_session_maker()
    
    async def store_infrastructure_intervention(
        self,
        user_id: str,
        intervention: InfrastructureIntervention
    ) -> str:
        """Store a complete infrastructure intervention in central memory bank"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                # Determine priority based on intervention type
                priority = PRIORITY_MAP.get(intervention.status.value, 2)
                
                # Create the memory entry
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=intervention.started_at,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=intervention.type.value,
                    subject_kind="infrastructure_intervention",
                    subject_id=intervention.intervention_id,
                    priority=priority,
                    title=f"Infrastructure {intervention.type.value} by The Hamsters",
                    description=intervention.human_readable_summary,
                    details={
                        'intervention_type': intervention.type.value,
                        'status': intervention.status.value,
                        'steve_action': intervention.steve_action,
                        'bob_action': intervention.bob_action,
                        'carl_action': intervention.carl_action,
                        'beer_consumed': intervention.beer_consumed,
                        'duct_tape_used': [tape.__dict__ for tape in intervention.duct_tape_used],
                        'tools_used': intervention.tools_used,
                        'space_freed_gb': intervention.space_freed_gb,
                        'fragmentation_reduced_percent': intervention.fragmentation_reduced_percent,
                        'temperature_reduced_celsius': intervention.temperature_reduced_celsius,
                        'mystery_solved': intervention.mystery_solved,
                        'required_vic20_intervention': intervention.required_vic20_intervention,
                        'caused_stick_anxiety_spike': intervention.caused_stick_anxiety_spike
                    },
                    metadata={
                        'squeaks_emitted': intervention.squeaks_emitted,
                        'completed_at': intervention.completed_at.isoformat() if intervention.completed_at else None,
                                                'duration': str(intervention.completed_at - intervention.started_at) if intervention.completed_at else None,
                        'is_3am_intervention': 2 <= intervention.started_at.hour <= 5
                    },
                    numeric_value=float(intervention.space_freed_gb),
                    string_value=intervention.type.value,
                    tags=['infrastructure', intervention.type.value, f'priority_{intervention.status.value}'],
                    relevant_agents='vic_20_sage,the_stick' if intervention.required_vic20_intervention else None,
                    stick_anxiety_level=20.0 if intervention.caused_stick_anxiety_spike else None
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Pin important interventions
                if priority >= 4:  # HIGH or CRITICAL
                    await self._pin_intervention_memory(user_id, memory_id, intervention)
                
                # Track learning if this was a successful intervention
                if intervention.status.value == 'completed' and intervention.space_freed_gb > 10:
                    await self._record_infrastructure_learning(user_id, memory_id, intervention)
                
                self.logger.info(f"🐹 Stored intervention {memory_id}: {intervention.type.value}")
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to store intervention: {str(e)}")
            raise
    
    async def store_hamster_communication(
        self,
        user_id: Optional[str],
        communication: HamsterCommunication
    ) -> str:
        """Store hamster communication attempts"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=communication.timestamp,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.HAMSTER_SQUEAK,
                    subject_kind="communication",
                    subject_id=f"{communication.source_hamster}_{communication.timestamp.timestamp()}",
                    priority=2,  # MEDIUM
                    title=f"{communication.source_hamster.title()} squeaks",
                    description=communication.human_translation,
                    details={
                        'source_hamster': communication.source_hamster,
                        'telepathic_message': communication.telepathic_message,
                        'audible_squeaks': communication.audible_squeaks,
                        'target_agent': communication.target_agent,
                        'understood': communication.understood
                    },
                    metadata={
                        'communication_type': 'squeak',
                        'hamster_mood': self._determine_hamster_mood(communication.source_hamster)
                    },
                    string_value=communication.audible_squeaks,
                    tags=['communication', communication.source_hamster, 'squeak'],
                    relevant_agents=communication.target_agent
                )
                
                session.add(memory_entry)
                await session.commit()
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to store communication: {str(e)}")
            raise
    
    async def track_duct_tape_usage(
        self,
        user_id: Optional[str],
        usage: DuctTapeUsage
    ) -> str:
        """Track Carl's duct tape consumption"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=usage.timestamp,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.DUCT_TAPE_USAGE,
                    subject_kind="resource_consumption",
                    subject_id=f"duct_tape_{usage.timestamp.timestamp()}",
                    priority=1,  # LOW
                    title=f"{usage.grade} duct tape used by {usage.applied_by}",
                    description=f"{usage.amount_strips} strips of {usage.grade} tape for {usage.purpose}",
                    details={
                        'grade': usage.grade,
                        'amount_strips': usage.amount_strips,
                        'purpose': usage.purpose,
                        'applied_by': usage.applied_by,
                        'effectiveness': usage.effectiveness
                    },
                    metadata={
                        'is_carls_special': usage.grade == 'carls_special',
                        'resource_type': 'duct_tape'
                    },
                    numeric_value=float(usage.amount_strips),
                    string_value=usage.grade,
                    tags=['resource', 'duct_tape', usage.applied_by, usage.grade]
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Update Carl's duct tape expertise patterns
                if usage.effectiveness > 0.8:
                    await self._update_carl_duct_tape_patterns(user_id, usage)
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to track duct tape usage: {str(e)}")
            raise
    
    async def log_beer_consumption(
        self,
        user_id: Optional[str],
        hamster_name: str,
        beers: int,
        occasion: str
    ) -> str:
        """Track beer consumption for operational metrics"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.BEER_CONSUMPTION,
                    subject_kind="resource_consumption",
                    subject_id=f"beer_{hamster_name}_{utc_now().timestamp()}",
                    priority=1,  # LOW
                    title=f"{hamster_name.title()} consumed {beers} beers",
                    description=f"Beer consumption for {occasion}",
                    details={
                        'hamster_name': hamster_name,
                        'beers_consumed': beers,
                        'occasion': occasion,
                        'operational_impact': self._calculate_beer_impact(hamster_name, beers)
                    },
                    metadata={
                        'resource_type': 'beer',
                        'is_emergency_consumption': 'emergency' in occasion.lower()
                    },
                    numeric_value=float(beers),
                    string_value=hamster_name,
                    tags=['resource', 'beer', hamster_name, occasion]
                )
                
                session.add(memory_entry)
                await session.commit()
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to log beer consumption: {str(e)}")
            raise
    
    async def log_supply_closet_raid(
        self,
        user_id: Optional[str],
        items_taken: List[str],
        purpose: str,
        raided_by: str = "bob"
    ) -> str:
        """Log supply closet raids (usually Bob)"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.SUPPLY_CLOSET_RAID,
                    subject_kind="resource_acquisition",
                    subject_id=f"raid_{utc_now().timestamp()}",
                    priority=2,  # MEDIUM
                    title=f"Supply closet raided by {raided_by.title()}",
                    description=f"Acquired {len(items_taken)} items for {purpose}",
                    details={
                        'raided_by': raided_by,
                        'items_taken': items_taken,
                        'purpose': purpose,
                        'item_count': len(items_taken)
                    },
                    metadata={
                        'is_emergency_raid': 'emergency' in purpose.lower(),
                        'typical_bob_behavior': raided_by == 'bob'
                    },
                    numeric_value=float(len(items_taken)),
                    string_value=raided_by,
                    tags=['resource', 'supply_closet', raided_by, 'raid']
                )
                
                session.add(memory_entry)
                await session.commit()
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to log supply closet raid: {str(e)}")
            raise
    
    async def store_collective_decision(
        self,
        user_id: str,
        decision_data: Dict[str, Any]
    ) -> str:
        """Store collective hamster decisions with consensus tracking"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                priority = PRIORITY_MAP.get(decision_data.get('priority', 'routine_maintenance'), 2)
                
                                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.COLLECTIVE_DECISION,
                    subject_kind="collective_decision",
                    subject_id=decision_data.get('decision_id', str(uuid4())),
                    priority=priority,
                    title=f"Collective decision: {decision_data.get('intervention_type', 'unknown')}",
                    description=decision_data.get('human_translation', 'Hamsters made a decision'),
                    details={
                        'intervention_type': decision_data.get('intervention_type'),
                        'steve_assessment': decision_data.get('steve_assessment'),
                        'bob_suggestion': decision_data.get('bob_suggestion'),
                        'carl_calculation': decision_data.get('carl_calculation'),
                        'telepathic_consensus': decision_data.get('telepathic_consensus', False),
                        'confidence': decision_data.get('confidence', 0.0),
                        'tools_required': decision_data.get('tools_required', []),
                        'beer_consumption_estimate': decision_data.get('beer_consumption_estimate', 0),
                        'duct_tape_grade': decision_data.get('duct_tape_grade')
                    },
                    metadata={
                        'actual_squeaks': decision_data.get('actual_squeaks'),
                        'estimated_duration': decision_data.get('estimated_duration'),
                        'urgency': decision_data.get('urgency'),
                        'is_unanimous': decision_data.get('telepathic_consensus', False)
                    },
                    numeric_value=decision_data.get('confidence', 0.0),
                    string_value=decision_data.get('intervention_type', 'unknown'),
                    tags=['decision', 'collective', f'priority_{priority}'],
                    cross_agent_validated=decision_data.get('telepathic_consensus', False),
                    validation_count=3 if decision_data.get('telepathic_consensus', False) else 0
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Record individual hamster contributions
                await self._record_individual_contributions(user_id, memory_id, decision_data)
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to store collective decision: {str(e)}")
            raise
    
    async def get_recent_interventions(
        self,
        hours: int = 24,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent intervention history from central memory bank"""
        try:
            async with await self.get_session() as session:
                since = utc_now() - timedelta(hours=hours)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type.in_([
                            HamstersEventTypes.DISK_CLEANUP,
                            HamstersEventTypes.DEFRAGMENTATION,
                            HamstersEventTypes.LOG_ROTATION,
                            HamstersEventTypes.EMERGENCY_SPACE,
                            HamstersEventTypes.PARTITION_MANAGEMENT,
                            HamstersEventTypes.THERMAL_EVENT,
                            HamstersEventTypes.MYSTERY_NOISE,
                            HamstersEventTypes.CABLE_MANAGEMENT
                        ]),
                        CentralMemoryBank.occurred_at >= since
                    )
                )
                
                if user_id:
                    query = query.where(CentralMemoryBank.user_id == user_id)
                
                query = query.order_by(CentralMemoryBank.occurred_at.desc())
                
                result = await session.execute(query)
                interventions = result.scalars().all()
                
                return [self._format_intervention_memory(i) for i in interventions]
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to get recent interventions: {str(e)}")
            return []
    
    async def get_hamster_performance_metrics(
        self,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get hamster performance metrics from central memory bank"""
        try:
            async with await self.get_session() as session:
                since = utc_now() - timedelta(days=days)
                
                # Get intervention stats
                intervention_query = select(
                    func.count(CentralMemoryBank.id).label('total_interventions'),
                    func.sum(CentralMemoryBank.numeric_value).label('total_space_freed'),
                    func.avg(
                        func.cast(CentralMemoryBank.details['confidence'], func.Float)
                    ).label('avg_confidence')
                ).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type.in_([
                            HamstersEventTypes.DISK_CLEANUP,
                            HamstersEventTypes.DEFRAGMENTATION,
                            HamstersEventTypes.EMERGENCY_SPACE
                        ]),
                        CentralMemoryBank.occurred_at >= since
                    )
                )
                
                if user_id:
                    intervention_query = intervention_query.where(CentralMemoryBank.user_id == user_id)
                
                intervention_result = await session.execute(intervention_query)
                intervention_stats = intervention_result.one()
                
                # Get beer consumption
                beer_query = select(
                    func.sum(CentralMemoryBank.numeric_value).label('total_beer')
                ).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == HamstersEventTypes.BEER_CONSUMPTION,
                        CentralMemoryBank.occurred_at >= since
                    )
                )
                
                if user_id:
                    beer_query = beer_query.where(CentralMemoryBank.user_id == user_id)
                
                beer_result = await session.execute(beer_query)
                beer_stats = beer_result.scalar() or 0
                
                # Get 3AM intervention count
                three_am_query = text("""
                    SELECT COUNT(*) as count
                    FROM central_memory_bank
                    WHERE agent_name = :agent_name
                        AND event_type = :event_type
                        AND occurred_at >= :since
                        AND EXTRACT(HOUR FROM occurred_at) BETWEEN 2 AND 5
                        AND (:user_id IS NULL OR user_id = :user_id)
                """)
                
                three_am_result = await session.execute(
                    three_am_query,
                    {
                        'agent_name': AGENT_NAME,
                        'event_type': HamstersEventTypes.THREE_AM_INTERVENTION,
                        'since': since,
                        'user_id': user_id
                    }
                )
                three_am_count = three_am_result.scalar() or 0
                
                total_interventions = int(intervention_stats.total_interventions or 0)
                
                return {
                    'total_interventions': total_interventions,
                    'total_space_freed_gb': float(intervention_stats.total_space_freed or 0),
                    'average_confidence': float(intervention_stats.avg_confidence or 0),
                    'total_beer_consumed': int(beer_stats),
                    'three_am_interventions': int(three_am_count),
                    'avg_beer_per_intervention': (
                        int(beer_stats) / total_interventions if total_interventions > 0 else 0
                    ),
                    'observation_count': total_interventions,
                    'period_days': days
                }
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to get performance metrics: {str(e)}")
            return {
                'total_interventions': 0,
                'total_space_freed_gb': 0.0,
                'average_confidence': 0.0,
                'total_beer_consumed': 0,
                'three_am_interventions': 0,
                'avg_beer_per_intervention': 0.0,
                'observation_count': 0,
                'period_days': days
            }
    
    async def check_pattern_match(
        self,
        user_id: str,
        metrics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if current metrics match any learned patterns"""
        try:
            # Get user patterns
            patterns = await get_user_patterns(self.engine, user_id)
            
            matches = []
            for pattern in patterns:
                if pattern.get('interaction_pattern'):
                    # Check disk space patterns
                    if 'disk_cleanup_trigger' in pattern['interaction_pattern']:
                        trigger = pattern['interaction_pattern']['disk_cleanup_trigger']
                        disk_usage = metrics_data.get('disk', {}).get('usage_percent', 0)
                        
                        if disk_usage >= trigger:
                                                        matches.append({
                                'pattern_type': 'disk_cleanup',
                                'confidence': pattern.get('success_patterns', {}).get('average_confidence', 0.7),
                                'recommended_action': 'aggressive_cleanup',
                                'historical_success_rate': pattern.get('success_patterns', {}).get('success_rate', 0.8),
                                'typical_space_freed': pattern.get('success_patterns', {}).get('avg_space_freed', 30)
                            })
                    
                    # Check fragmentation patterns
                    if 'defrag_threshold' in pattern['interaction_pattern']:
                        threshold = pattern['interaction_pattern']['defrag_threshold']
                        fragmentation = metrics_data.get('disk', {}).get('fragmentation_percent', 0)
                        
                        if fragmentation >= threshold:
                            matches.append({
                                'pattern_type': 'defragmentation',
                                'confidence': pattern.get('success_patterns', {}).get('average_confidence', 0.75),
                                'recommended_action': 'defrag_special',
                                'expected_improvement': pattern.get('success_patterns', {}).get('avg_improvement', 25)
                            })
            
            return {
                'pattern_matches': matches,
                'has_matches': len(matches) > 0,
                'recommendations': [m['recommended_action'] for m in matches],
                'best_match': max(matches, key=lambda x: x['confidence']) if matches else None
            }
            
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to check pattern match: {str(e)}")
            return {'pattern_matches': [], 'has_matches': False}
    
    async def store_user_behavior_observation(
        self,
        user_id: str,
        metrics_data: Dict[str, Any]
    ) -> str:
        """Store user behavior observation for pattern learning"""
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.USER_BEHAVIOR_OBSERVATION,
                    subject_kind="behavior_observation",
                    subject_id=f"obs_{utc_now().timestamp()}",
                    priority=1,  # LOW
                    title="Infrastructure metrics observation",
                    description="Hamsters observed system metrics for pattern learning",
                    details={
                        'disk_usage': metrics_data.get('disk', {}).get('usage_percent'),
                        'fragmentation': metrics_data.get('disk', {}).get('fragmentation_percent'),
                        'memory_usage': metrics_data.get('memory', {}).get('usage_percent'),
                        'log_size_gb': metrics_data.get('disk', {}).get('log_size_gb'),
                        'timestamp': utc_now().isoformat()
                    },
                    metadata={
                        'observation_type': 'routine',
                        'hamster_on_duty': self._get_hamster_on_duty()
                    },
                    tags=['observation', 'pattern_learning', 'metrics']
                )
                
                session.add(memory_entry)
                await session.commit()
                
                return memory_id
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to store behavior observation: {str(e)}")
            raise
    
    async def analyze_and_learn_patterns(
        self,
        user_id: str,
        min_observations: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Analyze observations and learn infrastructure patterns"""
        try:
            async with await self.get_session() as session:
                # Get recent observations
                observations_query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HamstersEventTypes.USER_BEHAVIOR_OBSERVATION,
                        CentralMemoryBank.occurred_at >= utc_now() - timedelta(days=30)
                    )
                ).order_by(CentralMemoryBank.occurred_at.desc()).limit(min_observations)
                
                result = await session.execute(observations_query)
                observations = result.scalars().all()
                
                if len(observations) < min_observations:
                    return None
                
                # Analyze patterns
                disk_usage_points = []
                intervention_triggers = []
                
                for obs in observations:
                    details = obs.details or {}
                    disk_usage = details.get('disk_usage')
                    if disk_usage:
                        disk_usage_points.append(disk_usage)
                        
                        # Check if an intervention followed
                        intervention = await self._check_intervention_after_observation(
                            session, user_id, obs.occurred_at
                        )
                        if intervention:
                            intervention_triggers.append({
                                'disk_usage': disk_usage,
                                'intervention_type': intervention.event_type,
                                'success': intervention.details.get('success', True)
                            })
                
                # Calculate patterns
                if intervention_triggers:
                    avg_trigger_point = sum(t['disk_usage'] for t in intervention_triggers) / len(intervention_triggers)
                    success_rate = sum(1 for t in intervention_triggers if t['success']) / len(intervention_triggers)
                    
                    # Create pattern
                    pattern = UserLearningPattern(
                        user_id=user_id,
                        pattern_id=f"hamsters_disk_pattern_{user_id}_{utc_now().timestamp()}",
                        interaction_pattern={
                            'disk_cleanup_trigger': avg_trigger_point,
                            'intervention_count': len(intervention_triggers),
                            'observation_count': len(observations)
                        },
                        success_patterns={
                            'success_rate': success_rate,
                            'average_confidence': 0.75,
                            'pattern_strength': min(len(intervention_triggers) / 10, 1.0)
                        },
                        most_effective_agent=AGENT_NAME,
                        complexity_tolerance=0.7  # Hamsters handle complex infrastructure
                    )
                    
                    await upsert_user_pattern(self.engine, pattern)
                    
                    # Store pattern learned event
                    await self._store_pattern_learned_event(user_id, pattern)
                    
                    return {
                        'pattern_type': 'disk_cleanup_threshold',
                        'trigger_point': avg_trigger_point,
                        'success_rate': success_rate,
                        'confidence_score': min(len(intervention_triggers) / 10, 1.0),
                        'stick_memory_notes': f"User typically needs cleanup at {avg_trigger_point:.0f}% disk usage"
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to analyze patterns: {str(e)}")
            return None
    
    async def get_database_health(self) -> Dict[str, Any]:
        """Get database connection health status"""
        try:
            async with await self.get_session() as session:
                # Simple health check query
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                return {
                    'status': 'healthy',
                    'connection': 'active',
                    'response_time_ms': 1,  # Would need actual timing
                    'hamster_approved': True
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connection': 'failed',
                'error': str(e),
                'hamster_approved': False
            }
    
    # Private helper methods
    
    def _determine_hamster_mood(self, hamster_name: str) -> str:
        """Determine individual hamster mood"""
        moods = {
            'steve': ['cautious', 'thoughtful', 'concerned', 'optimistic'],
            'bob': ['excited', 'wild', 'enthusiastic', 'ready for chaos'],
            'carl': ['focused', 'calculating', 'tape-ready', 'precise']
        }
        import random
        return random.choice(moods.get(hamster_name, ['busy']))
    
    def _calculate_beer_impact(self, hamster_name: str, beers: int) -> str:
        """Calculate operational impact of beer consumption"""
        if hamster_name == 'steve':
            if beers < 2:
                return "Needs more courage"
            elif beers <= 3:
                return "Optimal decision making"
            else:
                return "Unusually adventurous"
        elif hamster_name == 'bob':
            if beers < 3:
                return "Not wild enough"
            elif beers <= 5:
                return "Peak wildness"
            else:
                return "Maximum chaos mode"
        else:  # carl
            if beers <= 3:
                return "Precise duct tape application"
            elif beers <= 4:
                return "Creative tape solutions"
            else:
                return "Experimental tape physics"
    
    def _get_hamster_on_duty(self) -> str:
        """Determine which hamster is currently on duty"""
        hour = utc_now().hour
        if 2 <= hour <= 5:
            return "bob"  # Bob handles 3AM emergencies
        elif 6 <= hour <= 14:
            return "steve"  # Steve takes morning shift
        else:
            return "carl"  # Carl handles afternoon/evening
    
    def _format_intervention_memory(self, memory: CentralMemoryBank) -> Dict[str, Any]:
        """Format intervention memory for return"""
        details = memory.details or {}
        metadata = memory.metadata or {}
        
        return {
            'id': memory.memory_id,
            'intervention_id': memory.subject_id,
            'type': memory.event_type,
            'status': details.get('status', 'unknown'),
            'priority': memory.priority,
            'started_at': memory.occurred_at,
            'completed_at': metadata.get('completed_at'),
            'steve_action': details.get('steve_action'),
            'bob_action': details.get('bob_action'),
            'carl_action': details.get('carl_action'),
            'space_freed_gb': details.get('space_freed_gb', 0),
            'beer_consumed': details.get('beer_consumed', 0),
            'tools_used': details.get('tools_used', []),
            'duration': metadata.get('duration')
        }
    
    async def _pin_intervention_memory(
        self,
        user_id: str,
        memory_id: str,
        intervention: InfrastructureIntervention
    ):
        """Pin important intervention memories"""
        try:
            pinned = PinnedMemory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_type=MemoryTypes.SUCCESSFUL_INTERVENTION,
                                content={
                    'intervention_type': intervention.type.value,
                    'space_freed_gb': intervention.space_freed_gb,
                    'steve_action': intervention.steve_action,
                    'bob_action': intervention.bob_action,
                    'carl_action': intervention.carl_action,
                    'summary': intervention.human_readable_summary
                },
                importance=5 if intervention.space_freed_gb > 50 else 3,
                source_memory_id=memory_id
            )
            
            await pin_memory(self.engine, pinned)
            
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to pin intervention memory: {str(e)}")
    
    async def _record_infrastructure_learning(
        self,
        user_id: str,
        memory_id: str,
        intervention: InfrastructureIntervention
    ):
        """Record successful infrastructure learning"""
        try:
            # Check if The Stick observed this intervention
            stick_observed = intervention.caused_stick_anxiety_spike
            
            learning = LearningInteraction(
                interaction_id=str(uuid4()),
                timestamp=utc_now(),
                source_agent=AGENT_NAME,
                target_agent='the_stick' if stick_observed else 'vic_20_sage',
                source_memory_id=memory_id,
                learning_type=LearningTypes.OPTIMIZATION_TECHNIQUE,
                adaptation_method={
                    'technique': intervention.type.value,
                    'space_freed': intervention.space_freed_gb,
                    'beer_required': intervention.beer_consumed,
                    'duct_tape_used': len(intervention.duct_tape_used)
                },
                application_context={
                    'infrastructure_state': 'critical' if intervention.space_freed_gb > 50 else 'normal',
                    'time_of_day': intervention.started_at.hour,
                    'hamster_consensus': True
                },
                transfer_success=True,
                effectiveness_score=min(intervention.space_freed_gb / 50, 1.0),
                improvement_measured=intervention.space_freed_gb,
                validated_by_stick=stick_observed,
                cross_validation_count=1
            )
            
            await record_learning_interaction(self.engine, learning)
            
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to record infrastructure learning: {str(e)}")
    
    async def _record_individual_contributions(
        self,
        user_id: str,
        parent_memory_id: str,
        decision_data: Dict[str, Any]
    ):
        """Record individual hamster contributions to collective decisions"""
        try:
            async with await self.get_session() as session:
                # Steve's analysis
                steve_memory = CentralMemoryBank(
                    memory_id=str(uuid4()),
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.STEVE_ANALYSIS,
                    subject_kind="individual_contribution",
                    subject_id=f"steve_{parent_memory_id}",
                    priority=1,
                    title="Steve's careful analysis",
                    description=decision_data.get('steve_assessment', ''),
                    parent_memory_id=parent_memory_id,
                    tags=['steve', 'analysis', 'careful']
                )
                
                # Bob's wild idea
                bob_memory = CentralMemoryBank(
                    memory_id=str(uuid4()),
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.BOB_WILD_IDEA,
                    subject_kind="individual_contribution",
                    subject_id=f"bob_{parent_memory_id}",
                    priority=1,
                    title="Bob's wild suggestion",
                    description=decision_data.get('bob_suggestion', ''),
                    parent_memory_id=parent_memory_id,
                    tags=['bob', 'wild_idea', 'creative']
                )
                
                # Carl's calculation
                carl_memory = CentralMemoryBank(
                    memory_id=str(uuid4()),
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.CARL_DUCT_TAPE_CALC,
                    subject_kind="individual_contribution",
                    subject_id=f"carl_{parent_memory_id}",
                    priority=1,
                    title="Carl's duct tape calculation",
                    description=decision_data.get('carl_calculation', ''),
                    parent_memory_id=parent_memory_id,
                    tags=['carl', 'duct_tape', 'calculation']
                )
                
                session.add_all([steve_memory, bob_memory, carl_memory])
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to record individual contributions: {str(e)}")
    
    async def _update_carl_duct_tape_patterns(
        self,
        user_id: str,
        usage: DuctTapeUsage
    ):
        """Update Carl's duct tape expertise patterns"""
        try:
            # Check if we should create a global pattern for this tape technique
            if usage.effectiveness > 0.9 and usage.grade in ['quantum', 'carls_special']:
                pattern = GlobalPattern(
                    pattern_key=f"carl_tape_technique_{usage.purpose}_{usage.grade}",
                    value={
                        'technique': usage.purpose,
                        'tape_grade': usage.grade,
                        'strips_required': usage.amount_strips,
                        'effectiveness': usage.effectiveness,
                        'discovered_by': 'carl',
                        'discovery_date': utc_now().isoformat()
                    }
                )
                
                await upsert_global_pattern(self.engine, pattern)
                
                self.logger.info(f"🐹 Carl discovered new duct tape technique: {usage.purpose}")
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to update Carl's patterns: {str(e)}")
    
    async def _check_intervention_after_observation(
        self,
        session: AsyncSession,
        user_id: str,
        observation_time: datetime
    ) -> Optional[CentralMemoryBank]:
        """Check if an intervention followed an observation"""
        try:
            # Look for interventions within 1 hour of observation
            query = select(CentralMemoryBank).where(
                and_(
                    CentralMemoryBank.agent_name == AGENT_NAME,
                    CentralMemoryBank.user_id == user_id,
                    CentralMemoryBank.event_type.in_([
                        HamstersEventTypes.DISK_CLEANUP,
                        HamstersEventTypes.DEFRAGMENTATION,
                        HamstersEventTypes.EMERGENCY_SPACE
                    ]),
                    CentralMemoryBank.occurred_at >= observation_time,
                    CentralMemoryBank.occurred_at <= observation_time + timedelta(hours=1)
                )
            ).limit(1)
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to check intervention: {str(e)}")
            return None
    
    async def _store_pattern_learned_event(
        self,
        user_id: str,
        pattern: UserLearningPattern
    ):
        """Store pattern learned event in central memory bank"""
        try:
            async with await self.get_session() as session:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid4()),
                    occurred_at=utc_now(),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.PATTERN_LEARNED,
                    subject_kind="pattern_discovery",
                    subject_id=pattern.pattern_id,
                    priority=3,  # MEDIUM-HIGH
                    title="Infrastructure pattern discovered",
                    description=f"Hamsters learned user's disk cleanup pattern",
                    details={
                        'pattern_type': 'disk_cleanup_threshold',
                        'trigger_point': pattern.interaction_pattern.get('disk_cleanup_trigger'),
                        'confidence': pattern.success_patterns.get('pattern_strength'),
                        'observations_used': pattern.interaction_pattern.get('observation_count')
                    },
                    metadata={
                        'learning_complete': True,
                        'can_be_promoted': pattern.success_patterns.get('pattern_strength', 0) > 0.8
                    },
                    tags=['pattern', 'learning', 'infrastructure', 'discovery']
                )
                
                session.add(memory_entry)
                await session.commit()
                
                # Notify other agents about the pattern
                await self._notify_agents_about_pattern(user_id, pattern)
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to store pattern learned event: {str(e)}")
    
        async def _notify_agents_about_pattern(
        self,
        user_id: str,
        pattern: UserLearningPattern
    ):
            """Notify other agents about discovered patterns"""
        try:
            # Create a learning interaction for The Stick (anxiety about disk space)
            if 'disk_cleanup_trigger' in pattern.interaction_pattern:
                trigger_point = pattern.interaction_pattern['disk_cleanup_trigger']
                
                stick_learning = LearningInteraction(
                    interaction_id=str(uuid4()),
                    timestamp=utc_now(),
                    source_agent=AGENT_NAME,
                    target_agent='the_stick',
                    source_memory_id=pattern.pattern_id,
                    learning_type=LearningTypes.PATTERN_GENERALIZATION,
                    adaptation_method={
                        'pattern_type': 'disk_threshold',
                        'trigger_value': trigger_point,
                        'source': 'hamster_observations'
                    },
                    application_context={
                        'user_id': user_id,
                        'anxiety_trigger': f"Disk usage above {trigger_point}%"
                    },
                    transfer_success=True,
                    effectiveness_score=0.8,
                    validated_by_stick=False  # Will be validated when Stick uses it
                )
                
                await record_learning_interaction(self.engine, stick_learning)
                
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to notify agents: {str(e)}")