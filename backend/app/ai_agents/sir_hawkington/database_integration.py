"""
Sir Hawkington Von Monitorious III Database Integration
DUAL-WRITE ARCHITECTURE: Agent-Specific Table + Central Memory Bank
NO FAKE DATA POLICY: Real data or graceful failure
"""

import asyncio
import os
import json
import uuid
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete, text
import logging

# Import base class for consistent session management
from app.ai_agents.distributed.base_database_integration import BaseDatabaseIntegration

from app.models.agent_memory_banks import (
    CentralMemoryBank,
    SirHawkingtonMemoryBank
)
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction, PinnedMemory,
    upsert_global_pattern, upsert_user_pattern, record_learning_interaction,
    pin_memory, get_user_patterns, get_global_patterns, check_and_promote_pattern,
    get_pinned_memories, LearningTypes, MemoryTypes
)

from app.ai_agents.constants import AgentNames, PRIORITY_MAP
from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage
from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
from app.ai_agents.sir_hawkington.constants import AGENT_NAME, HawkingtonEventTypes
from app.utils.json_safety import to_json_safe

logger = logging.getLogger("SirHawkington.Database")

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO format string"""
    return dt.isoformat() if dt else None

class HawkingtonDatabaseIntegration(BaseDatabaseIntegration):
    """
    Database integration for Sir Hawkington with DUAL-WRITE architecture
    NO FAKE DATA POLICY: Real data or graceful failure
    """
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter)
        self.engine = None  # Set during initialize for learning helpers
    
    def _get_agent_name(self) -> str:
        """Return agent name for base class"""
        return AGENT_NAME
    
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
    
    async def initialize(self):
        """Initialize Sir Hawkington's distinguished database connection"""
        if self._initialized:
            return
        
        if not self.db_getter:
            raise ValueError("db_getter is required - Sir Hawkington refuses to create his own engine!")
        
        # Verify db_getter works by testing a connection and get engine
        try:
            async with self.get_managed_session() as session:
                # Extract engine from session for learning helpers
                self.engine = session.bind
        except Exception as e:
            logger.error(f"🧐❌ Failed to verify database connection: {e}")
            raise
        
        self._initialized = True
        logger.info("🧐✨ Database integration initialized using shared connection pool")

    # === DUAL-WRITE METHOD 1: STORE DECISION ===
    
    async def store_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
        """
        Store Sir Hawkington's aristocratic decision with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to SirHawkingtonMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            decision: HawkingtonDecision instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required decision data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not decision.decision_id:
            raise ValueError("🧐💥 Missing decision_id - cannot store without real ID")
        if not decision.decision_type:
            raise ValueError("🧐💥 Missing decision_type - cannot store without real decision")
        if decision.confidence is None:
            raise ValueError("🧐💥 Missing confidence - cannot store without real confidence value")
        if not decision.timestamp:
            raise ValueError("🧐💥 Missing timestamp - cannot store without real timestamp")
        
        async with self.get_managed_session() as session:
            try:
                # Generate IDs
                agent_memory_id = str(uuid.uuid4())
                central_memory_id = str(uuid.uuid4())
                
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                metrics = decision.metrics  # Can be None
                
                # Only extract stress_score if metrics actually exist
                stress_score = metrics.get('stress_score') if metrics else None
                
                # Determine memory category from REAL decision type
                memory_category = self._map_decision_type_to_category(decision.decision_type)
                
                # Build data quality pattern ONLY from real metrics
                data_quality_pattern = None
                if metrics:
                    data_quality_pattern = to_json_safe({
                        'cpu_valid': metrics.get('cpu_usage') is not None,
                        'memory_valid': metrics.get('memory_usage') is not None,
                        'disk_valid': metrics.get('disk_usage') is not None,
                        'analysis_depth': metrics.get('analysis_depth') if 'analysis_depth' in metrics else None
                    })
                
                # Build triage context ONLY from real data
                triage_decision_context = to_json_safe({
                    'decision_type': decision.decision_type,
                    'system_impact': decision.system_impact,  # Can be None
                    'confidence': decision.confidence,
                    'stress_score': stress_score  # Can be None
                })
                
                # Quality thresholds - these are REAL thresholds from constants
                # NOT making up data, documenting the actual thresholds used
                quality_threshold_adjustment = to_json_safe({
                    'thresholds_applied': {
                        'concern': 0.65,
                        'alert': 0.85,
                        'critical': 0.95
                    },
                    'decision_alignment': decision.decision_type
                })
                
                # Calculate improvement metrics - REAL or None
                accuracy_improvement = await self._calculate_accuracy_improvement(
                    user_id, decision, session
                )
                false_positive_reduction = await self._calculate_false_positive_reduction(
                    user_id, decision, session
                )
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = SirHawkingtonMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=decision.timestamp,
                    
                    # Hawkington-specific structured fields
                    memory_category=memory_category,
                    
                    # JSON fields - REAL data or None
                    data_quality_pattern=data_quality_pattern,
                    triage_decision_context=triage_decision_context,
                    quality_threshold_adjustment=quality_threshold_adjustment,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    accuracy_improvement=accuracy_improvement,
                    false_positive_reduction=false_positive_reduction,
                    
                    # Link to central memory
                    shared_with_central=True,
                    central_memory_id=central_memory_id
                )
                
                session.add(agent_memory)
                await session.flush()  # Ensure agent memory is written first
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                central_memory = CentralMemoryBank(
                    memory_id=central_memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,
                    occurred_at=decision.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="system_analysis",
                    subject_id=decision.decision_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'decision_id': decision.decision_id,
                        'decision_type': decision.decision_type,
                        'reasoning': decision.reasoning,
                        'system_impact': decision.system_impact,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'aristocratic_seal': True,
                        'decision_quality': 'distinguished',
                        'monocle_state': 'polished',
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=decision.confidence,
                    string_value=decision.decision_type,
                    priority=self._get_priority_for_decision(decision.decision_type),
                    never_forget=(decision.decision_type in ['critical', 'alert']),
                    
                    agent_metadata=to_json_safe({
                        'aristocratic_seal': True,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(central_memory)
                await session.commit()
                await session.refresh(agent_memory)
                await session.refresh(central_memory)
                
                # === WRITE 3: VECTOR EMBEDDING (FIRE-AND-FORGET) ===
                try:
                    decision_text = create_decision_text(
                        agent_name=AGENT_NAME,
                        decision_type=decision.decision_type,
                        description=decision.reasoning if decision.reasoning else f"Aristocratic {decision.decision_type} decision",
                        reasoning=f"System impact: {decision.system_impact}, Confidence: {decision.confidence}",
                        context={
                            'priority': self._get_priority_for_decision(decision.decision_type),
                            'event_type': HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,
                            'affected_agents': []
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type=decision.decision_type,
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=decision.timestamp,
                        user_id=user_id,
                        event_type=HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,
                        priority=self._get_priority_for_decision(decision.decision_type),
                        metadata=to_json_safe({
                            'decision_id': decision.decision_id,
                            'system_impact': decision.system_impact,
                            'monocle_state': 'polished'
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=decision.confidence,
                        decision_summary=f"Hawkington: {decision.decision_type}"
                    )
                    logger.debug(f"🔮 Queued vector embedding for decision {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                logger.info(
                    f"🧐✨ DUAL-WRITE SUCCESS: Decision {decision.decision_type} stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id})"
                )
                
                # Pin critical decisions
                if decision.decision_type in ['critical', 'alert']:
                    await self._pin_critical_decision(user_id, decision, central_memory_id)
                
                return central_memory_id
                
            except ValueError as ve:
                # Data validation error - graceful failure with clear message
                await session.rollback()
                logger.error(f"🧐💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"🧐💥 DUAL-WRITE FAILED: {str(e)}")
                raise Exception(f"🧐💥 Failed to store aristocratic decision: {str(e)}")
    
    # === DUAL-WRITE METHOD 2: STORE TRIAGE DECISION ===
    
    async def store_triage_decision(self, user_id: str, triage_data: Dict[str, Any]) -> str:
        """
        Store triage decision with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        Args:
            user_id: User identifier
            triage_data: Triage decision data with REAL datetime objects
            
        Returns:
            central_memory_id
            
        Raises:
            ValueError: If required triage data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA
        if not triage_data.get('triage_severity'):
            raise ValueError("🧐💥 Missing triage_severity - cannot store without real severity")
        if not triage_data.get('routing_decision'):
            raise ValueError("🧐💥 Missing routing_decision - cannot store without real routing")
        
        async with self.get_managed_session() as session:
            try:
                # Generate IDs
                agent_memory_id = str(uuid.uuid4())
                central_memory_id = str(uuid.uuid4())
                
                # Get timestamp - must be real datetime
                occurred_at_dt = triage_data.get("timestamp")
                if not isinstance(occurred_at_dt, datetime):
                    raise ValueError(f"🧐💥 Invalid timestamp type: {type(occurred_at_dt)}")
                
                # Ensure timezone aware
                if occurred_at_dt.tzinfo is None:
                    occurred_at_dt = occurred_at_dt.replace(tzinfo=timezone.utc)
                
                # Extract confidence - REAL or None
                conf = triage_data.get("confidence")
                confidence_value = None
                if conf is not None and isinstance(conf, (int, float)) and math.isfinite(float(conf)):
                    confidence_value = float(conf)
                
                # Extract processing time - REAL or None
                processing_time = triage_data.get('processing_time')
                if processing_time is not None:
                    if not isinstance(processing_time, (int, float)) or not math.isfinite(float(processing_time)):
                        processing_time = None
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = SirHawkingtonMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=occurred_at_dt,
                    
                    # Triage-specific category
                    memory_category="triage",
                    
                    # Structured triage context - REAL data only
                    triage_decision_context=to_json_safe({
                        'severity': triage_data.get('triage_severity'),
                        'routing': triage_data.get('routing_decision'),
                        'target_agents': triage_data.get('target_agents', []),
                        'reasoning': triage_data.get('reasoning'),
                        'processing_time': processing_time
                    }),
                    
                    # Data quality pattern for triage
                    data_quality_pattern=to_json_safe({
                        'monocle_yeeted': triage_data.get('monocle_yeeted', False),
                        'metrics_complete': not triage_data.get('monocle_yeeted', False),
                        'triage_confidence': confidence_value
                    }),
                    
                    # Quality thresholds ACTUALLY USED (from constants)
                    quality_threshold_adjustment=to_json_safe({
                        'severity_thresholds': {
                            'normal': 0.30,
                            'medium': 0.65,
                            'emergency': 0.85
                        },
                        'applied_severity': triage_data.get('triage_severity')
                    }),
                    
                    # STRUCTURED METRICS - REAL or None
                    accuracy_improvement=confidence_value,  # Triage confidence as accuracy metric
                    false_positive_reduction=None,  # Not applicable for triage decisions
                    
                    # Link to central
                    shared_with_central=True,
                    central_memory_id=central_memory_id
                )
                
                session.add(agent_memory)
                await session.flush()
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                # Priority from severity
                priority_val = self._get_priority_for_triage(triage_data.get("triage_severity"))
                
                # Extract target agents - REAL list or empty
                target_agents = triage_data.get('target_agents', [])
                if not isinstance(target_agents, list):
                    target_agents = [target_agents] if target_agents else []
                
                central_memory = CentralMemoryBank(
                    memory_id=central_memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.TRIAGE_DECISION.value,
                    occurred_at=occurred_at_dt,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="system_triage",
                    
                    # Summary details - REAL data
                    details=to_json_safe({
                        'severity': triage_data.get('triage_severity'),
                        'routing': triage_data.get('routing_decision'),
                        'success': triage_data.get('success'),  # Can be None
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'triage_commander': True,
                        'routing_decision': triage_data.get('routing_decision'),
                        'monocle_yeeted': triage_data.get('monocle_yeeted', False),
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Indexable fields - REAL or None
                    numeric_value=confidence_value,
                    string_value=triage_data.get("triage_severity"),
                    priority=priority_val,
                    never_forget=(triage_data.get("triage_severity") in ("emergency", "high")),
                    
                    # Target agents as JSON array
                    relevant_agents=json.dumps(to_json_safe(target_agents)),
                    
                    agent_metadata=to_json_safe({
                        'triage_commander': True,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(central_memory)
                await session.commit()
                
                # === WRITE 3: VECTOR EMBEDDING (NON-BLOCKING) ===
                # Fire-and-forget vector write - doesn't block triage flow
                try:
                    decision_text = create_decision_text(
                        agent_name=AGENT_NAME,
                        decision_type="triage",
                        description=f"Triage {triage_data.get('triage_severity', 'unknown')} severity",
                        reasoning=triage_data.get('triage_reasoning', 'System triage assessment'),
                        context={
                            'priority': triage_data.get('priority', 3),
                            'severity': triage_data.get('triage_severity'),
                            'escalated': triage_data.get('escalated_to_vic20', False)
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    import asyncio
                    asyncio.create_task(vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="triage",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=triage_data.get('timestamp', utc_now()),
                        user_id=user_id,
                        event_type=HawkingtonEventTypes.TRIAGE_COMPLETED.value,
                        priority=triage_data.get('priority', 3),
                        metadata=to_json_safe({
                            'triage_severity': triage_data.get('triage_severity'),
                            'escalated_to_vic20': triage_data.get('escalated_to_vic20', False),
                            'monocle_state': triage_data.get('monocle_state')
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=triage_data.get('confidence_score'),
                        decision_summary=f"Triage: {triage_data.get('triage_severity')}"
                    ))
                    logger.debug(f"🔮 Queued vector embedding for triage {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                logger.info(
                    f"🧐✨ DUAL-WRITE SUCCESS: Triage {triage_data.get('triage_severity')} stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id})"
                )
                
                                # Pin high-severity triage decisions
                if triage_data.get("triage_severity") in ("emergency", "high"):
                    await self._pin_triage_decision(user_id, triage_data, central_memory_id)
                
                # Record learning
                success_value = triage_data.get("success")
                if success_value is not None:
                    await self.record_triage_learning(
                        user_id,
                        triage_data,
                        float(success_value) if isinstance(success_value, (int, float)) else 1.0,
                        central_memory_id
                    )
                
                return central_memory_id
            
            except ValueError as ve:
                await session.rollback()
                logger.error(f"🧐💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"🧐💥 DUAL-WRITE FAILED: Triage storage error: {str(e)}")
                raise Exception(f"🧐💥 Failed to store triage decision: {str(e)}")
    
    # === DUAL-WRITE METHOD 3: STORE MONOCLE YEET ===
    
    async def store_monocle_yeet_incident(self, user_id: str, incident_data: Dict[str, Any]) -> str:
        """
        Store monocle yeet incident with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        Args:
            user_id: User identifier
            incident_data: Monocle yeet incident details (REAL data)
            
        Returns:
            central_memory_id
            
        Raises:
            ValueError: If required incident data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA
        if not incident_data.get('reason'):
            raise ValueError("🧐💥 Missing yeet reason - cannot store monocle yeet without explanation")
        
        async with self.get_managed_session() as session:
            try:
                # Generate IDs
                agent_memory_id = str(uuid.uuid4())
                central_memory_id = str(uuid.uuid4())
                
                # Get timestamp - REAL or current time
                occurred_at = incident_data.get('timestamp')
                if not isinstance(occurred_at, datetime):
                    occurred_at = utc_now()
                elif occurred_at.tzinfo is None:
                    occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                
                # Extract REAL lists (not making up missing data)
                missing_metrics = incident_data.get('missing_metrics', [])
                invalid_metrics = incident_data.get('invalid_metrics', [])
                
                if not isinstance(missing_metrics, list):
                    missing_metrics = []
                if not isinstance(invalid_metrics, list):
                    invalid_metrics = []
                
                # Yeet intensity - REAL or None
                yeet_intensity = incident_data.get('yeet_intensity')
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = SirHawkingtonMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=occurred_at,
                    
                    # Monocle yeet category
                    memory_category="monocle_yeet",
                    
                    # Data quality pattern showing WHAT FAILED
                    data_quality_pattern=to_json_safe({
                        'missing_metrics': missing_metrics,
                        'invalid_metrics': invalid_metrics,
                        'yeet_reason': incident_data.get('reason'),
                        'data_quality_failure': True
                    }),
                    
                    # Triage context for yeet (what was attempted)
                    triage_decision_context=to_json_safe({
                        'attempted_analysis': True,
                        'data_validation_failed': True,
                        'yeet_intensity': yeet_intensity,
                        'requires_data_quality_review': True
                    }),
                    
                    # Quality thresholds that were violated
                    quality_threshold_adjustment=to_json_safe({
                        'minimum_required_metrics': ['cpu_usage', 'memory_usage', 'disk_usage'],
                        'metrics_present': {
                            'cpu': 'cpu_usage' not in missing_metrics,
                            'memory': 'memory_usage' not in missing_metrics,
                            'disk': 'disk_usage' not in missing_metrics
                        }
                    }),
                    
                    # STRUCTURED METRICS - None for yeets (no valid analysis occurred)
                    accuracy_improvement=None,
                    false_positive_reduction=None,
                    
                    # Link to central
                    shared_with_central=True,
                    central_memory_id=central_memory_id
                )
                
                session.add(agent_memory)
                await session.flush()
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                central_memory = CentralMemoryBank(
                    memory_id=central_memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.MONOCLE_YEET.value,
                    occurred_at=occurred_at,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="data_quality_failure",
                    
                    # Summary details
                    details=to_json_safe({
                        'missing_metrics': missing_metrics,
                        'invalid_metrics': invalid_metrics,
                        'reason': incident_data.get('reason'),
                        'yeet_intensity': yeet_intensity,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'monocle_state': 'yeeted',
                        'aristocratic_horror': True,
                        'data_integrity_enforced': True,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Indexable fields
                    string_value=yeet_intensity if yeet_intensity else 'data_quality_failure',
                    priority=10,  # MAXIMUM - data quality is serious
                    never_forget=True,
                    
                    agent_metadata=to_json_safe({
                        'monocle_state': 'yeeted',
                        'aristocratic_horror': True,
                        'data_integrity_enforced': True,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(central_memory)
                await session.commit()
                
                logger.warning(
                    f"🧐💥 DUAL-WRITE SUCCESS: Monocle yeet stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id}) - "
                    f"Missing: {missing_metrics}, Invalid: {invalid_metrics}"
                )
                
                # Always pin monocle yeets - they're important!
                await self._pin_monocle_yeet(user_id, incident_data, central_memory_id)
                
                return central_memory_id
                
            except ValueError as ve:
                await session.rollback()
                logger.error(f"🧐💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"🧐💥 DUAL-WRITE FAILED: Monocle yeet storage error: {str(e)}")
                raise Exception(f"🧐💥 Failed to store monocle yeet: {str(e)}")
    
    # === KEEP EXISTING RETRIEVAL METHODS (NO CHANGES NEEDED) ===
    
    async def store_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Sir Hawkington doesn't store metrics - he analyzes them"""
        pass
    
    async def store_hawkington_decision(self, user_id: str, decision: HawkingtonDecision) -> str:
        """Alias for store_decision to match websocket expectations"""
        return await self.store_decision(user_id, decision)
    
    async def get_historical_decisions(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get Sir Hawkington's historical decisions from central memory bank"""
        async with self.get_managed_session() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days)
                
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == HawkingtonEventTypes.ARISTOCRATIC_DECISION.value,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
                
                result = await session.execute(query)
                memories = result.scalars().all()
                
                return [
                    {
                        'timestamp': memory.occurred_at,
                        'decision_type': memory.details.get('decision_type'),
                        'confidence_level': memory.numeric_value,
                        'alert_parameters': {
                            'stress_score': memory.details.get('stress_score', 0)
                        },
                        'technical_details': memory.details,
                        'user_acknowledged': False,
                        'issue_resolved': False
                    }
                    for memory in memories
                ]
                
            except Exception as e:
                raise Exception(f"🧐💥 Failed to get historical decisions: {str(e)}")
    
    async def get_triage_statistics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get triage statistics from AGENT TABLE (structured queries!)
        NO FAKE DATA: Real stats or None
        """
        async with self.get_managed_session() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days)
                
                # Query AGENT TABLE for structured triage data
                query = select(SirHawkingtonMemoryBank).where(
                    and_(
                        SirHawkingtonMemoryBank.user_id == user_id,
                        SirHawkingtonMemoryBank.memory_category == 'triage',
                        SirHawkingtonMemoryBank.timestamp >= cutoff_date
                    )
                ).order_by(desc(SirHawkingtonMemoryBank.timestamp))
                
                result = await session.execute(query)
                triage_memories = result.scalars().all()
                
                if not triage_memories:
                    return {
                        'status': 'no_data',
                        'period_days': days,
                        'total_decisions': 0
                    }
                
                # Calculate REAL statistics from structured data
                total_decisions = len(triage_memories)
                monocle_yeets = 0
                routing_counts = {}
                severity_counts = {}
                confidence_values = []
                processing_times = []
                
                for memory in triage_memories:
                    # Extract from structured JSON fields
                    triage_context = memory.triage_decision_context or {}
                    data_quality = memory.data_quality_pattern or {}
                    
                    # Count monocle yeets
                    if data_quality.get('monocle_yeeted'):
                        monocle_yeets += 1
                    
                    # Count routing types
                    routing = triage_context.get('routing')
                    if routing:
                        routing_counts[routing] = routing_counts.get(routing, 0) + 1
                    
                    # Count severities
                    severity = triage_context.get('severity')
                    if severity:
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Collect confidence values (from structured field!)
                    if memory.accuracy_improvement is not None:
                        confidence_values.append(memory.accuracy_improvement)
                    
                    # Collect processing times
                    proc_time = triage_context.get('processing_time')
                    if proc_time is not None and isinstance(proc_time, (int, float)):
                        processing_times.append(proc_time)
                
                # Calculate averages (REAL or None)
                avg_confidence = None
                if confidence_values:
                    avg_confidence = sum(confidence_values) / len(confidence_values)
                
                avg_processing_time = None
                if processing_times:
                    avg_processing_time = sum(processing_times) / len(processing_times)
                
                successful_decisions = total_decisions - monocle_yeets
                
                return {
                    'total_decisions': total_decisions,
                    'successful_decisions': successful_decisions,
                    'success_rate': successful_decisions / total_decisions if total_decisions > 0 else None,
                    'monocle_yeet_count': monocle_yeets,
                    'monocle_yeet_rate': monocle_yeets / total_decisions if total_decisions > 0 else None,
                    'routing_distribution': routing_counts,
                    'severity_distribution': severity_counts,
                    'average_confidence': avg_confidence,
                    'average_processing_time': avg_processing_time,
                    'period_days': days,
                    'latest_decision': triage_memories[0].timestamp.isoformat() if triage_memories else None,
                    'aristocratic_status': 'DISTINGUISHED',
                    'data_source': 'agent_specific_table'
                }
                
            except Exception as e:
                logger.error(f"🧐💥 Failed to get triage statistics: {str(e)}")
                raise Exception(f"🧐💥 Failed to get triage statistics: {str(e)}")
    
    async def get_hawkington_performance_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get Sir Hawkington's performance metrics from AGENT TABLE
        NO FAKE DATA: Real metrics or None
        """
        async with self.get_managed_session() as session:
            try:
                # Query agent table for all memory categories
                query = select(SirHawkingtonMemoryBank).where(
                    SirHawkingtonMemoryBank.user_id == user_id
                )
                
                result = await session.execute(query)
                all_memories = result.scalars().all()
                
                if not all_memories:
                    return {
                        'total_decisions': 0,
                        'status': 'no_data',
                        'hawkington_status': 'AWAITING_FIRST_ANALYSIS'
                    }
                
                # Count by category
                category_breakdown = {}
                total_accuracy_improvements = []
                total_false_positive_reductions = []
                
                for memory in all_memories:
                    category = memory.memory_category
                    category_breakdown[category] = category_breakdown.get(category, 0) + 1
                    
                    # Collect REAL improvement metrics
                    if memory.accuracy_improvement is not None:
                        total_accuracy_improvements.append(memory.accuracy_improvement)
                    if memory.false_positive_reduction is not None:
                        total_false_positive_reductions.append(memory.false_positive_reduction)
                
                # Calculate averages (REAL or None)
                avg_accuracy = None
                if total_accuracy_improvements:
                    avg_accuracy = sum(total_accuracy_improvements) / len(total_accuracy_improvements)
                
                avg_false_positive_reduction = None
                if total_false_positive_reductions:
                    avg_false_positive_reduction = sum(total_false_positive_reductions) / len(total_false_positive_reductions)
                
                return {
                    'total_decisions': len(all_memories),
                    'decision_breakdown': category_breakdown,
                    'monocle_yeets': category_breakdown.get('monocle_yeet', 0),
                    'triage_decisions': category_breakdown.get('triage', 0),
                    'quality_analyses': category_breakdown.get('quality_analysis', 0),
                    'average_accuracy_improvement': avg_accuracy,
                    'average_false_positive_reduction': avg_false_positive_reduction,
                    'aristocratic_effectiveness': avg_accuracy if avg_accuracy else None,
                    'hawkington_status': 'DISTINGUISHED_AND_OPERATIONAL',
                    'data_source': 'agent_specific_table'
                }
                
            except Exception as e:
                logger.error(f"🧐💥 Failed to get performance metrics: {str(e)}")
                raise Exception(f"🧐💥 Failed to get performance metrics: {str(e)}")
    
    # === PATTERN LEARNING OPERATIONS (NO CHANGES - ALREADY GOOD) ===
    
    async def store_user_behavior_observation(
        self, 
        user_id: str, 
        observation_data: Dict[str, Any]
    ) -> None:
        """Store user behavior observation for pattern learning"""
        async with self.get_managed_session() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=HawkingtonEventTypes.BEHAVIOR_OBSERVED.value,
                    occurred_at=utc_now(),
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="behavior_observation",
                    details=to_json_safe(observation_data),
                    metadata_=to_json_safe({
                        'observation_type': 'triage_behavior',
                        'learning_eligible': True
                    }),
                    priority=1,
                    tags=json.dumps(["observation", "learning"])
                )
                
                session.add(memory_entry)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to store observation: {str(e)}")
    
    async def analyze_and_learn_patterns(
        self,
        user_id: str,
        min_observations: int = 25
    ) -> Optional[Dict[str, Any]]:
        """Analyze triage patterns and learn user preferences - NO FAKE DATA"""
        async with self.get_managed_session() as session:
            try:
                cutoff = utc_now() - timedelta(days=30)
                
                # Get observations from CMB
                result = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.user_id == user_id,
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.event_type == HawkingtonEventTypes.BEHAVIOR_OBSERVED.value,
                            CentralMemoryBank.occurred_at >= cutoff
                        )
                    ).order_by(desc(CentralMemoryBank.occurred_at)).limit(min_observations * 2)
                )
                
                observations = result.scalars().all()
                
                if len(observations) < min_observations:
                    logger.info(f"🧐 Insufficient observations for pattern learning: {len(observations)}/{min_observations}")
                    return None
                
                # Analyze REAL patterns (no fake data generation)
                pattern_analysis = self._analyze_triage_patterns(observations)
                
                if pattern_analysis and pattern_analysis.get("confidence", 0) > 0.7:
                    # Create pattern ONLY if confidence is high enough
                    pattern = UserLearningPattern(
                        user_id=user_id,
                        pattern_id=f"{user_id}_hawkington_pattern_{utc_now().strftime('%Y%m%d')}",
                        timestamp=utc_now(),
                        interaction_pattern=pattern_analysis.get("interaction_pattern"),
                        learning_preference=pattern_analysis.get("learning_preference"),
                        response_patterns=pattern_analysis.get("response_patterns"),
                        most_effective_agent=AGENT_NAME,
                        complexity_tolerance=pattern_analysis.get("complexity_score")
                    )
                    
                    await upsert_user_pattern(self.engine, pattern, agent_name=AGENT_NAME)
                    
                    logger.info(f"🧐 Pattern learned with {pattern_analysis['confidence']:.2f} confidence")
                    
                    # Check promotion ONLY if confidence is very high
                    if pattern_analysis.get("confidence", 0) > 0.9:
                        await check_and_promote_pattern(
                            self.engine,
                            pattern.pattern_id,
                            confidence_threshold=0.9,
                            cross_validation_count=5
                        )
                    
                    return pattern_analysis
                
                return None
                
            except Exception as e:
                logger.error(f"Pattern learning failed: {str(e)}")
                return None
    
    async def check_pattern_match(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if current context matches known patterns - NO FAKE DATA"""
        try:
            # Get REAL user patterns
            user_patterns = await get_user_patterns(self.engine, user_id)
            
            # Get REAL global patterns
            global_patterns = await get_global_patterns(self.engine)
            
            best_match = None
            highest_confidence = 0.0
            
            # Check user patterns first
            for pattern in user_patterns:
                if pattern.get("most_effective_agent") == AGENT_NAME:
                    match_score = self._calculate_pattern_match_score(
                        context,
                        pattern.get("interaction_pattern", {})
                    )
                    
                    if match_score > highest_confidence:
                        highest_confidence = match_score
                        best_match = {
                            "pattern_type": "user",
                            "pattern_id": pattern["pattern_id"],
                            "confidence": match_score,
                            "recommendations": self._generate_pattern_recommendations(pattern)
                        }
            
            # Check global patterns if no strong user match
            if highest_confidence < 0.8:
                for pattern_key, pattern_data in global_patterns.items():
                    if "hawkington" in pattern_key.lower():
                        pattern_value = pattern_data.get("value", {})
                        match_score = self._calculate_pattern_match_score(context, pattern_value)
                        
                        if match_score > highest_confidence:
                            highest_confidence = match_score
                            best_match = {
                                "pattern_type": "global",
                                "pattern_key": pattern_key,
                                "confidence": match_score,
                                "recommendations": self._generate_pattern_recommendations(pattern_value)
                            }
            
            # Only return match if confidence is meaningful
            return best_match if highest_confidence > 0.6 else None
            
        except Exception as e:
            logger.error(f"Pattern matching failed: {str(e)}")
            return None
    
    # === CROSS-AGENT LEARNING OPERATIONS (NO CHANGES) ===
    
    async def share_triage_wisdom(
        self,
        target_agent: str,
        wisdom_type: str,
        wisdom_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Share triage wisdom with other agents"""
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            source_agent=AGENT_NAME,
            target_agent=target_agent,
            source_memory_id=source_memory_id,
            learning_type="triage_expertise",
            adaptation_method=to_json_safe({
                "wisdom_type": wisdom_type,
                "triage_approach": wisdom_data.get("approach"),
                "severity_thresholds": wisdom_data.get("thresholds")
            }),
            application_context=to_json_safe({
                "sharing_reason": wisdom_data.get("reason"),
                "expected_benefit": "improved_triage_accuracy"
            }),
            transfer_success=None,
            effectiveness_score=None
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    async def record_triage_learning(
        self,
        user_id: str,
        triage_data: Dict[str, Any],
        effectiveness: float,
        source_memory_id: str
    ) -> None:
        """Record learning from triage decisions"""
        interaction = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            source_agent=AGENT_NAME,
            target_agent="all_agents",
            source_memory_id=source_memory_id,
            learning_type="triage_pattern",
            adaptation_method=to_json_safe({
                "severity": triage_data.get("triage_severity"),
                "routing": triage_data.get("routing_decision"),
                "confidence": triage_data.get("confidence")
            }),
            application_context=to_json_safe({
                "system_state": triage_data.get("system_state"),
                "triage_reasoning": triage_data.get("reasoning")
            }),
            transfer_success=effectiveness > 0.7,
            effectiveness_score=effectiveness,
            validated_by_stick=False,
            cross_validation_count=1
        )
        
        await record_learning_interaction(self.engine, interaction)
    
    # === PINNED MEMORY OPERATIONS (NO CHANGES) ===
    
    async def _pin_critical_decision(
        self,
        user_id: str,
        decision: HawkingtonDecision,
        source_memory_id: str
    ) -> None:
        """Pin critical triage decisions"""
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="critical_triage",
            content=to_json_safe({
                "decision_type": decision.decision_type,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "metrics": decision.metrics,
                "system_impact": decision.system_impact
            }),
            importance=5 if decision.decision_type == "critical" else 4,
            timestamp=decision.timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    async def _pin_monocle_yeet(
        self,
        user_id: str,
        incident_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Pin monocle yeet incidents - they're important!"""
        timestamp = incident_data.get("timestamp")
        if not isinstance(timestamp, datetime):
            timestamp = utc_now()
        
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="monocle_yeet",
            content=to_json_safe({
                "reason": incident_data.get("reason"),
                "missing_metrics": incident_data.get("missing_metrics", []),
                "invalid_metrics": incident_data.get("invalid_metrics", []),
                "yeet_intensity": incident_data.get("yeet_intensity")
            }),
            importance=5,
            timestamp=timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    async def _pin_triage_decision(
        self,
        user_id: str,
        triage_data: Dict[str, Any],
        source_memory_id: str
    ) -> None:
        """Pin important triage decisions"""
        timestamp = triage_data.get("timestamp")
        if not isinstance(timestamp, datetime):
            timestamp = utc_now()
        
        memory = PinnedMemory(
            user_id=user_id,
            agent_name=AGENT_NAME,
            memory_type="triage_decision",
            content=to_json_safe({
                "severity": triage_data.get("triage_severity"),
                "routing": triage_data.get("routing_decision"),
                "target_agents": triage_data.get("target_agents"),
                "reasoning": triage_data.get("reasoning"),
                "confidence": triage_data.get("confidence")
            }),
            importance=4,
            timestamp=timestamp,
            source_memory_id=source_memory_id
        )
        
        await pin_memory(self.engine, memory)
    
    # === METADATA CONTRIBUTION ===
    
    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Contribute Hawkington's memory counts for metadata rollup"""
        async with self.get_managed_session() as session:
            try:
                # Count from AGENT TABLE (structured!)
                result = await session.execute(
                    select(func.count(SirHawkingtonMemoryBank.id)).where(
                        SirHawkingtonMemoryBank.timestamp >= utc_now() - timedelta(minutes=5)
                    )
                )
                
                count = result.scalar() or 0
                
                return {
                    "hawkington_memories": count,
                    "triage_events": count
                }
            except Exception as e:
                logger.error(f"Metadata contribution failed: {str(e)}")
                return {
                    "hawkington_memories": 0,
                    "triage_events": 0
                }
    
    # === HELPER METHODS ===
    
    def _map_decision_type_to_category(self, decision_type: str) -> str:
        """Map decision type to memory category"""
        category_map = {
            'normal': 'quality_analysis',
            'concern': 'quality_analysis',
            'alert': 'quality_alert',
            'critical': 'critical_analysis',
            'monocle_yeeted': 'monocle_yeet'
        }
        return category_map.get(decision_type, 'quality_analysis')
    
    async def _calculate_accuracy_improvement(
        self,
        user_id: str,
        decision: HawkingtonDecision,
        session: AsyncSession
    ) -> Optional[float]:
        """
        Calculate REAL accuracy improvement based on historical data
        NO FAKE DATA: Returns None if insufficient data
        """
        try:
            # Get recent decisions from agent table
            cutoff = utc_now() - timedelta(days=7)
            
            result = await session.execute(
                select(SirHawkingtonMemoryBank).where(
                    and_(
                        SirHawkingtonMemoryBank.user_id == user_id,
                        SirHawkingtonMemoryBank.timestamp >= cutoff,
                        SirHawkingtonMemoryBank.accuracy_improvement.isnot(None)
                    )
                ).order_by(desc(SirHawkingtonMemoryBank.timestamp)).limit(10)
            )
            
            historical = result.scalars().all()
            
            if not historical:
                # First decision - use confidence as baseline
                return decision.confidence if decision.confidence else None
            
            # Calculate REAL improvement
            historical_avg = sum(m.accuracy_improvement for m in historical) / len(historical)
            current_confidence = decision.confidence if decision.confidence else None
            
            if current_confidence is None:
                return None
            
            improvement = current_confidence - historical_avg
            return improvement
            
        except Exception as e:
            logger.error(f"Accuracy calculation failed: {str(e)}")
            return None
    
    async def _calculate_false_positive_reduction(
        self,
        user_id: str,
        decision: HawkingtonDecision,
        session: AsyncSession
    ) -> Optional[float]:
        """
        Calculate REAL false positive reduction
        NO FAKE DATA: Returns None if insufficient data
        """
        try:
            # Get monocle yeet count from agent table
            cutoff = utc_now() - timedelta(days=7)
            
            result = await session.execute(
                select(func.count(SirHawkingtonMemoryBank.id)).where(
                    and_(
                        SirHawkingtonMemoryBank.user_id == user_id,
                        SirHawkingtonMemoryBank.memory_category == 'monocle_yeet',
                        SirHawkingtonMemoryBank.timestamp >= cutoff
                    )
                )
            )
            
            yeet_count = result.scalar() or 0
            
            # Get total decisions
            total_result = await session.execute(
                select(func.count(SirHawkingtonMemoryBank.id)).where(
                    and_(
                        SirHawkingtonMemoryBank.user_id == user_id,
                        SirHawkingtonMemoryBank.timestamp >= cutoff
                    )
                )
            )
            
            total_count = total_result.scalar() or 0
            
            if total_count == 0:
                return None
            
            # Calculate REAL reduction (inverse of yeet rate)
            yeet_rate = yeet_count / total_count
            reduction = 1.0 - yeet_rate
            
            return reduction
            
        except Exception as e:
            logger.error(f"False positive calculation failed: {str(e)}")
            return None
    
    def _get_priority_for_decision(self, decision_type: str) -> int:
        """Determine priority based on decision type"""
        priority_map = {
            'critical': 10,
            'alert': 8,
            'concern': 6,
            'normal': 4,
            'monocle_yeeted': 10
        }
        return priority_map.get(decision_type, 5)
    
    def _get_priority_for_triage(self, severity: str) -> int:
        """Determine priority based on triage severity"""
        priority_map = {
            'emergency': 10,
            'high': 8,
            'medium': 6,
            'normal': 4
        }
        return priority_map.get(severity, 5)
    
    def _analyze_triage_patterns(
        self,
        observations: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze observations for triage patterns
        NO FAKE DATA: Returns None if insufficient real patterns found
        """
        if not observations or len(observations) < 10:
            return None
        
        try:
            severities = []
            confidences = []
            categories = {}
            
            for obs in observations:
                details = obs.details or {}
                
                # Extract REAL severity if present
                severity = details.get("severity")
                if severity:
                    severity_map = {"normal": 1, "medium": 2, "high": 3, "emergency": 4}
                    if severity in severity_map:
                        severities.append(severity_map[severity])
                
                # Extract REAL confidence if present
                confidence = obs.numeric_value
                if confidence is not None:
                    confidences.append(confidence)
                
                # Track categories
                category = details.get("category")
                if category:
                    categories[category] = categories.get(category, 0) + 1
            
            # Only proceed if we have REAL data
            if not severities or not confidences:
                return None
            
            import statistics
            
            # Calculate REAL statistics
            avg_severity = sum(severities) / len(severities)
            avg_confidence = sum(confidences) / len(confidences)
            
            # Calculate confidence in pattern (based on consistency)
            severity_variance = statistics.variance(severities) if len(severities) > 1 else 1.0
            pattern_confidence = max(0.5, min(1.0, 0.9 - (severity_variance * 0.2)))
            
            # Find preferred categories (only if statistically significant)
            preferred_categories = [
                cat for cat, count in categories.items()
                if count > len(observations) * 0.2
            ]
            
            return {
                "confidence": pattern_confidence,
                "interaction_pattern": {
                    "preferred_categories": preferred_categories,
                    "typical_severity": avg_severity
                },
                "learning_preference": {
                    "response_style": "aristocratic",
                    "detail_level": "thorough" if avg_severity > 2.0 else "standard"
                },
                "response_patterns": {
                    "avg_confidence": avg_confidence,
                    "decision_consistency": 1.0 - (severity_variance / 4.0)
                },
                "complexity_score": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            return None
    
    def _calculate_pattern_match_score(
        self,
        context: Dict[str, Any],
        pattern: Dict[str, Any]
    ) -> float:
        """
        Calculate pattern match score
        NO FAKE DATA: Returns 0.0 if insufficient data for comparison
        """
        if not context or not pattern:
            return 0.0
        
        try:
            score = 0.0
            factors = 0.0
            
            # Check severity match if both present
            context_severity = context.get("severity")
            pattern_severity = pattern.get("typical_severity")
            
            if context_severity is not None and pattern_severity is not None:
                severity_diff = abs(context_severity - pattern_severity)
                score += (1.0 - severity_diff / 4.0) * 0.5
                factors += 0.5
            
            # Check metric patterns if present
            context_metrics = context.get("metrics")
            pattern_thresholds = pattern.get("metric_thresholds")
            
            if context_metrics and pattern_thresholds:
                matching = 0
                total = 0
                
                for metric, value in context_metrics.items():
                    if metric in pattern_thresholds:
                        threshold = pattern_thresholds[metric]
                        min_val = threshold.get("min")
                        max_val = threshold.get("max")
                        
                        if min_val is not None and max_val is not None:
                            if min_val <= value <= max_val:
                                matching += 1
                            total += 1
                
                if total > 0:
                    score += (matching / total) * 0.5
                    factors += 0.5
            
            return score / factors if factors > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Pattern match calculation failed: {str(e)}")
            return 0.0
    
    def _generate_pattern_recommendations(
        self,
        pattern: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on REAL pattern data"""
        recommendations = []
        
        if not pattern:
            return recommendations
        
        try:
            interaction_pattern = pattern.get("interaction_pattern", {})
            
            preferred_categories = interaction_pattern.get("preferred_categories", [])
            if preferred_categories:
                recommendations.append(
                    f"Focus on {', '.join(preferred_categories)} issues"
                )
            
            typical_severity = interaction_pattern.get("typical_severity")
            if typical_severity is not None:
                if typical_severity > 2.5:
                    recommendations.append("🧐 Prepare for high-severity triage decisions")
                elif typical_severity < 1.5:
                    recommendations.append("🧐 Expect routine operations")
            
            response_patterns = pattern.get("response_patterns", {})
            avg_confidence = response_patterns.get("avg_confidence")
            
            if avg_confidence is not None and avg_confidence < 0.7:
                recommendations.append("🧐 Historical confidence low - ensure data quality")
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
        
        return recommendations
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """
        Clean up old data with aristocratic precision - keep important memories
        NO FAKE DATA: Only removes low-priority, non-critical REAL memories
        """
        async with self.get_managed_session() as session:
            try:
                cutoff_date = utc_now() - timedelta(days=days_to_keep)
                
                # Clean up from AGENT TABLE - only low priority, non-critical
                await session.execute(
                    delete(SirHawkingtonMemoryBank).where(
                        and_(
                            SirHawkingtonMemoryBank.timestamp < cutoff_date,
                            SirHawkingtonMemoryBank.memory_category.notin_([
                                'monocle_yeet',  # Keep all yeets
                                'triage',  # Keep triage decisions
                                'critical_analysis'  # Keep critical analyses
                            ])
                        )
                    )
                )
                
                # Clean up from CENTRAL MEMORY BANK - only low priority
                await session.execute(
                    delete(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.occurred_at < cutoff_date,
                            CentralMemoryBank.priority < 5,
                            CentralMemoryBank.never_forget.is_(False),
                            CentralMemoryBank.event_type.notin_([
                                HawkingtonEventTypes.MONOCLE_YEET.value,
                                HawkingtonEventTypes.TRIAGE_DECISION.value
                            ])
                        )
                    )
                )
                
                await session.commit()
                logger.info(f"🧐 Cleaned up old memories with aristocratic precision")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"🧐💥 Memory cleanup failed: {str(e)}")
                raise Exception(f"🧐💥 Memory cleanup failed: {str(e)}")
    
    async def get_database_health(self) -> Dict[str, Any]:
        """
        Get database health status
        NO FAKE DATA: Real connection status or error
        """
        try:
            async with self.get_managed_session() as session:
                # Simple health check query
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Get REAL memory counts
                agent_count_result = await session.execute(
                    select(func.count(SirHawkingtonMemoryBank.id))
                )
                agent_count = agent_count_result.scalar() or 0
                
                cmb_count_result = await session.execute(
                    select(func.count(CentralMemoryBank.id)).where(
                        CentralMemoryBank.agent_name == AGENT_NAME
                    )
                )
                cmb_count = cmb_count_result.scalar() or 0
                
                return {
                    "status": "healthy",
                    "connection": "active",
                    "initialized": self._initialized,
                    "dual_write_enabled": True,
                    "agent_table_records": agent_count,
                    "central_table_records": cmb_count,
                    "architecture": "dual_write"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized,
                "dual_write_enabled": False
            }