# app/ai_agents/hamsters/database_integration.py
"""
The Hamsters Database Integration
DUAL-WRITE ARCHITECTURE: Agent-Specific Table + Central Memory Bank
NO FAKE DATA POLICY: Real data or graceful failure
"""

import os
import logging
import math
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import json
import asyncio

from sqlalchemy import text, select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from app.ai_agents.hamsters.data_types import (
    InfrastructureIntervention, HamsterCommunication, DuctTapeUsage
)
from app.models.agent_memory_banks import CentralMemoryBank, HamstersMemoryBank
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction, PinnedMemory,
    upsert_global_pattern, upsert_user_pattern, record_learning_interaction,
    pin_memory, get_user_patterns, LearningTypes, MemoryTypes
)
from app.utils.json_safety import to_json_safe
from .constants import HamstersEventTypes, AGENT_NAME, ALL_HAMSTERS, PRIORITY_MAP
from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage

logger = logging.getLogger("Hamsters.Database")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)
def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings in nested structures"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle dataclass objects
        return serialize_for_json(obj.__dict__)
    else:
        return obj
        
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
        self.db_getter = db_getter
        self._initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
        
        if not self.db_getter:
            raise ValueError("db_getter is required - The Hamsters need beer AND a shared pool!")
            
        try:
            # Verify db_getter works
            async for session in self.db_getter():
                break
            
            self._initialized = True
            self.logger.info("🐹🍺 Database integration initialized using shared connection pool (beer-powered efficiency!)")
            
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
    
    async def get_session(self):
        """Get a database session using db_getter pattern"""
        if not self._initialized:
            await self.initialize()
        async for session in self.db_getter():
            return session
    
    # === DUAL-WRITE METHOD 1: STORE INFRASTRUCTURE INTERVENTION ===
    
    async def store_infrastructure_intervention(
        self,
        user_id: str,
        intervention: InfrastructureIntervention
    ) -> str:
        """
        Store infrastructure intervention with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to HamstersMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            intervention: InfrastructureIntervention instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required intervention data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not intervention.intervention_id:
            raise ValueError("🐹💥 Missing intervention_id - cannot store without real ID")
        if not intervention.type:
            raise ValueError("🐹💥 Missing type - cannot store without real intervention type")
        if not intervention.started_at:
            raise ValueError("🐹💥 Missing started_at - cannot store without real timestamp")
        
        agent_memory_id = str(uuid4())
        memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Determine which hamster contributed
                contributing_hamster = "collective"
                if hasattr(intervention, 'primary_hamster'):
                    contributing_hamster = intervention.primary_hamster
                
                # Build infrastructure pattern
                infrastructure_pattern = to_json_safe({
                    'intervention_type': intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                    'status': intervention.status.value if hasattr(intervention.status, 'value') else str(intervention.status),
                    'tools_used': intervention.tools_used if intervention.tools_used else []
                })
                
                # Build duct tape solution
                duct_tape_solution = to_json_safe({
                    'duct_tape_used': [
                        {
                            'grade': tape.grade,
                            'amount_strips': tape.amount_strips,
                            'purpose': tape.purpose,
                            'applied_by': tape.applied_by,
                            'effectiveness': tape.effectiveness
                        }
                        for tape in intervention.duct_tape_used
                    ] if intervention.duct_tape_used else []
                })
                
                # Build beer consumption correlation
                beer_consumption_correlation = to_json_safe({
                    'beer_consumed': intervention.beer_consumed,
                    'intervention_success': intervention.status.value == 'completed' if hasattr(intervention.status, 'value') else False
                })
                
                # Build individual hamster contributions
                steve_contribution = to_json_safe({'action': intervention.steve_action}) if intervention.steve_action else None
                bob_contribution = to_json_safe({'action': intervention.bob_action}) if intervention.bob_action else None
                carl_contribution = to_json_safe({'action': intervention.carl_action}) if intervention.carl_action else None
                
                # Build stick anxiety trigger
                stick_anxiety_trigger = to_json_safe({
                    'caused_anxiety': hasattr(intervention, 'caused_stick_anxiety_spike') and intervention.caused_stick_anxiety_spike,
                    'required_vic20': intervention.required_vic20_intervention if hasattr(intervention, 'required_vic20_intervention') else False
                })
                
                # Calculate solution effectiveness (REAL or None)
                solution_effectiveness = None
                if intervention.space_freed_gb > 0:
                    solution_effectiveness = min(1.0, intervention.space_freed_gb / 100.0)
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = HamstersMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=intervention.started_at,
                    
                    # Hamsters-specific structured fields
                    contributing_hamster=contributing_hamster,
                    infrastructure_pattern=infrastructure_pattern,
                    duct_tape_solution=duct_tape_solution,
                    problem_type=intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                    beer_consumption_correlation=beer_consumption_correlation,
                    steve_contribution=steve_contribution,
                    bob_contribution=bob_contribution,
                    carl_contribution=carl_contribution,
                    stick_anxiety_trigger=stick_anxiety_trigger,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    solution_effectiveness=solution_effectiveness,
                    
                    # Link to central memory
                    shared_with_central=True,
                    central_memory_id=memory_id
                )
                
                session.add(agent_memory)
                await session.flush()  # Ensure agent memory is written first
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                priority = PRIORITY_MAP.get(intervention.status.value, 2) if hasattr(intervention.status, 'value') else 2
                
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                    occurred_at=intervention.started_at,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="infrastructure_intervention",
                    subject_id=intervention.intervention_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'intervention_type': intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                        'status': intervention.status.value if hasattr(intervention.status, 'value') else str(intervention.status),
                        'summary': intervention.human_readable_summary if hasattr(intervention, 'human_readable_summary') else None,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'beer_powered': intervention.beer_consumed > 0,
                        'duct_tape_used': len(intervention.duct_tape_used) > 0 if intervention.duct_tape_used else False,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=float(intervention.space_freed_gb) if intervention.space_freed_gb else 0.0,
                    string_value=intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                    priority=priority,
                    never_forget=(priority >= 4),
                    relevant_agents='vic_20_sage,the_stick' if (hasattr(intervention, 'required_vic20_intervention') and intervention.required_vic20_intervention) else None,
                    stick_anxiety_level=20.0 if (hasattr(intervention, 'caused_stick_anxiety_spike') and intervention.caused_stick_anxiety_spike) else None,
                    
                    agent_metadata=to_json_safe({
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(memory_entry)
                await session.commit()
                await session.refresh(agent_memory)
                await session.refresh(memory_entry)
                
                # === WRITE 3: VECTOR EMBEDDING (FIRE-AND-FORGET) ===
                try:
                    decision_text = create_decision_text(
                        agent_name=AGENT_NAME,
                        decision_type="infrastructure_intervention",
                        description=intervention.human_readable_summary if hasattr(intervention, 'human_readable_summary') and intervention.human_readable_summary else f"Infrastructure {intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type)}",
                        reasoning=f"Hamster collective intervention - Beer: {intervention.beer_consumed}, Duct tape: {len(intervention.duct_tape_used) if intervention.duct_tape_used else 0} applications",
                        context={
                            'priority': priority,
                            'event_type': intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                            'affected_agents': ['the_stick'] if (hasattr(intervention, 'caused_stick_anxiety_spike') and intervention.caused_stick_anxiety_spike) else []
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="infrastructure_intervention",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=intervention.started_at,
                        user_id=user_id,
                        event_type=intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                        priority=priority,
                        metadata=to_json_safe({
                            'intervention_type': intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type),
                            'beer_consumed': intervention.beer_consumed,
                            'duct_tape_used': len(intervention.duct_tape_used) if intervention.duct_tape_used else 0,
                            'space_freed_gb': intervention.space_freed_gb
                        }),
                        sql_memory_id=memory_id,
                        confidence_score=solution_effectiveness,
                        decision_summary=f"Hamster intervention: {intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type)}"
                    )
                    logger.debug(f"🔮 Queued vector embedding for intervention {memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                await session.close()
                
                logger.info(
                    f"🐹✨ DUAL-WRITE SUCCESS: Infrastructure intervention stored in agent table "
                    f"({agent_memory_id}) and CMB ({memory_id})"
                )
                
                # Pin important interventions
                if priority >= 4:
                    await self._pin_intervention(user_id, intervention, memory_id)
                
                return memory_id
                
        except ValueError as ve:
            # Data validation error - graceful failure with clear message
            logger.error(f"🐹💥 DATA VALIDATION FAILED: {str(ve)}")
            raise
            
        except Exception as e:
            logger.error(f"🐹💥 DUAL-WRITE FAILED: {str(e)}")
            raise Exception(f"🐹💥 Failed to store infrastructure intervention: {str(e)}")
    
    async def _pin_intervention(self, user_id: str, intervention: InfrastructureIntervention, memory_id: str):
        """Pin important infrastructure interventions"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"Infrastructure intervention: {intervention.type.value if hasattr(intervention.type, 'value') else str(intervention.type)}",
                importance=8
            )
            logger.info(f"📌 Pinned infrastructure intervention")
        except Exception as e:
            logger.warning(f"Failed to pin intervention: {str(e)}")
    
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
                    event_type=HamstersEventTypes.HAMSTER_SQUEAK.value,
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
                
                await session.close()
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
                    event_type=HamstersEventTypes.DUCT_TAPE_USAGE.value,
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
                
                await session.close()
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
                    event_type=HamstersEventTypes.BEER_CONSUMPTION.value,
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
                
                await session.close()
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
                    event_type=HamstersEventTypes.SUPPLY_CLOSET_RAID.value,
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
                
                await session.close()
                return memory_id
        except Exception as e:
            self.logger.error(f"🐹💥 Failed to log supply closet raid: {str(e)}")
            raise
    
    async def store_collective_decision(
        self,
        user_id: str,
        decision_data: Dict[str, Any]
    ) -> str:
        """
        Store collective hamster decisions with DUAL-WRITE pattern.
        
        WRITE 1: CentralMemoryBank (summary for cross-agent visibility)
        WRITE 2: HamstersMemoryBank (structured agent-specific data)
        WRITE 3: Vector embedding (fire-and-forget, non-blocking)
        
        Steve, Bob, and Carl's telepathic consensus is preserved for posterity!
        """
        now = utc_now()
        memory_id = str(uuid4())
        agent_memory_id = str(uuid4())
        
        try:
            async with await self.get_session() as session:
                priority = PRIORITY_MAP.get(decision_data.get('priority', 'routine_maintenance'), 2)
                confidence = decision_data.get('confidence', 0.0)
                intervention_type = decision_data.get('intervention_type', 'unknown')
                
                # === WRITE 1: CENTRAL MEMORY BANK (summary) ===
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    occurred_at=now,
                    created_at=now,
                    updated_at=now,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HamstersEventTypes.COLLECTIVE_DECISION.value,
                    subject_kind="collective_decision",
                    subject_id=agent_memory_id,
                    priority=priority,
                    title=f"Collective decision: {intervention_type}",
                    description=decision_data.get('human_translation', 'Hamsters made a decision'),
                    details=to_json_safe({
                        'intervention_type': intervention_type,
                        'telepathic_consensus': decision_data.get('telepathic_consensus', False),
                        'confidence': confidence,
                        'tools_required': decision_data.get('tools_required', []),
                        'beer_consumption_estimate': decision_data.get('beer_consumption_estimate', 0),
                        'agent_memory_ref': agent_memory_id
                    }),
                    metadata_=to_json_safe({
                        'actual_squeaks': decision_data.get('actual_squeaks'),
                        'estimated_duration': decision_data.get('estimated_duration'),
                        'urgency': decision_data.get('urgency'),
                        'is_unanimous': decision_data.get('telepathic_consensus', False),
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    numeric_value=confidence,
                    string_value=intervention_type,
                    tags=json.dumps(['decision', 'collective', f'priority_{priority}']),
                    cross_agent_validated=decision_data.get('telepathic_consensus', False),
                    validation_count=3 if decision_data.get('telepathic_consensus', False) else 0,
                    agent_metadata=to_json_safe({
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(memory_entry)
                await session.flush()  # Flush CMB first
                
                # === WRITE 2: HAMSTERS MEMORY BANK (structured data) ===
                agent_memory = HamstersMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=now,
                    
                    # Hamster-specific structured fields
                    contributing_hamster='collective',
                    infrastructure_pattern=to_json_safe({
                        'intervention_type': intervention_type,
                        'tools_required': decision_data.get('tools_required', [])
                    }),
                    duct_tape_solution=to_json_safe({
                        'grade': decision_data.get('duct_tape_grade'),
                        'carl_calculation': decision_data.get('carl_calculation')
                    }),
                    problem_type=intervention_type,
                    solution_effectiveness=confidence,
                    beer_consumption_correlation=to_json_safe({
                        'beers_consumed': decision_data.get('beer_consumption_estimate', 0),
                        'decision_quality': confidence
                    }),
                    
                    # Individual contributions
                    steve_contribution=to_json_safe({'assessment': decision_data.get('steve_assessment')}),
                    bob_contribution=to_json_safe({'suggestion': decision_data.get('bob_suggestion')}),
                    carl_contribution=to_json_safe({'calculation': decision_data.get('carl_calculation')}),
                    
                    # Event counters
                    beer_consumed_count=decision_data.get('beer_consumption_estimate', 0),
                    interventions_count=1,
                    last_intervention_timestamp=now,
                    
                    # Cross-agent coordination
                    shared_with_central=True,
                    central_memory_id=memory_id
                )
                
                session.add(agent_memory)
                await session.commit()
                
                self.logger.info(f"🐹💾 Dual-write complete: CMB={memory_id}, HamstersMemory={agent_memory_id}")
                
                # === WRITE 3: VECTOR EMBEDDING (fire-and-forget) ===
                try:
                    decision_text = create_decision_text(
                        agent_name=AGENT_NAME,
                        decision_type=intervention_type,
                        description=decision_data.get('human_translation', 'Collective hamster decision'),
                        reasoning=f"Steve: {decision_data.get('steve_assessment', 'N/A')}, Bob: {decision_data.get('bob_suggestion', 'N/A')}, Carl: {decision_data.get('carl_calculation', 'N/A')}",
                        context={
                            'priority': priority,
                            'event_type': HamstersEventTypes.COLLECTIVE_DECISION.value,
                            'telepathic_consensus': decision_data.get('telepathic_consensus', False)
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type=intervention_type,
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=now,
                        user_id=user_id,
                        event_type=HamstersEventTypes.COLLECTIVE_DECISION.value,
                        priority=priority,
                        metadata=to_json_safe({
                            'telepathic_consensus': decision_data.get('telepathic_consensus', False),
                            'beer_consumption': decision_data.get('beer_consumption_estimate', 0),
                            'tools_required': decision_data.get('tools_required', [])
                        }),
                        sql_memory_id=memory_id,
                        confidence_score=confidence,
                        decision_summary=f"Collective: {intervention_type}"
                    )
                    self.logger.debug(f"🐹🔮 Vector embedding queued for {memory_id}")
                except Exception as ve:
                    # Vector write failure doesn't break the decision flow
                    self.logger.warning(f"🐹⚠️ Vector embedding failed (non-critical): {ve}")
                
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
                
                # Convert enums to strings for the query
                event_types = [
                HamstersEventTypes.DISK_CLEANUP.value,  # Use .value
                HamstersEventTypes.DEFRAGMENTATION.value,
                HamstersEventTypes.LOG_ROTATION.value,
                HamstersEventTypes.EMERGENCY_SPACE.value,
                HamstersEventTypes.PARTITION_MANAGEMENT.value,
                HamstersEventTypes.THERMAL_EVENT.value,
                HamstersEventTypes.MYSTERY_NOISE.value,
                HamstersEventTypes.CABLE_MANAGEMENT.value
            ]
            
            query = select(CentralMemoryBank).where(
                and_(
                    CentralMemoryBank.agent_name == AGENT_NAME,
                    CentralMemoryBank.event_type.in_(event_types),  # Now using string values
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
                    event_type=HamstersEventTypes.USER_BEHAVIOR_OBSERVATION.value,
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
                
                await session.close()
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
                        CentralMemoryBank.event_type == HamstersEventTypes.USER_BEHAVIOR_OBSERVATION.value,
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
                
                await session.close()
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
                
                await session.close()
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
                        HamstersEventTypes.DISK_CLEANUP.value,
                        HamstersEventTypes.DEFRAGMENTATION.value,
                        HamstersEventTypes.EMERGENCY_SPACE.value
                    ]),
                    CentralMemoryBank.occurred_at >= observation_time,
                    CentralMemoryBank.occurred_at <= observation_time + timedelta(hours=1)
                )
            ).limit(1)
            
            result = await session.execute(query)
            
            await session.close()
            
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
                    event_type=HamstersEventTypes.PATTERN_LEARNED.value,
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
                
                await session.close()
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