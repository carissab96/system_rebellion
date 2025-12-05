# app/ai_agents/qsp/database_integration.py
"""
Quantum Shadow People Database Integration
DUAL-WRITE ARCHITECTURE: Agent-Specific Table + Central Memory Bank
NO FAKE DATA POLICY: Real data or graceful failure
"""

import uuid
import asyncio
import math
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, desc, and_, or_, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
import os
import json

from app.models.agent_memory_banks import CentralMemoryBank, QuantumShadowPeopleMemoryBank
from app.models.agent_memory import AgentMemory
from app.models.agent_memory_banks import AgentLearningInteractions
from app.models.agent_memory_banks import UserLearningPatterns
from app.models.agent_memory import AgentGlobalPattern
from app.models.agent_memory_banks import MemoryBankMetadata
from app.core.database import get_async_db
from app.core.learning_helpers import (
    GlobalPattern, UserLearningPattern, LearningInteraction,
    PinnedMemory, upsert_global_pattern, upsert_user_pattern,
    record_learning_interaction, pin_memory, get_user_patterns, get_global_patterns,
    hydrate_memory_bank_metadata
)
from app.utils.json_safety import to_json_safe
from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage
from .constants import AGENT_NAME, QSPEventTypes, QSPDecisionTypes, PRIORITY_MAP, QUANTUM_PHASES, NETWORK_THRESHOLDS
from .data_types import QSPDecision, QSPDecisionType, QuantumPhaseState

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

class QSPDatabaseIntegration:
    """Complete database integration for Quantum Shadow People"""
    
    def __init__(self, db_getter=None):
        self.db_getter = db_getter or get_async_db
        self.engine = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        if not self._initialized:
            # Get database session
            async for db in self.db_getter():
                # Extract engine from session
                self.engine = db.bind
                break
            self._initialized = True
    
    async def _ensure_initialized(self):
        """Ensure database is initialized"""
        if not self._initialized:
            await self.initialize()
    
    def _get_insert_stmt(self):
        """Get appropriate insert statement based on database"""
        db_url = str(self.engine.url) if self.engine else ""
        if "postgresql" in db_url:
            return pg_insert
        return sqlite_insert
    
    # ==================== CENTRAL MEMORY BANK OPERATIONS ====================
    
    async def store_network_metrics(self, user_id: str, metrics: Dict[str, Any]) -> str:
        """Store network metrics observation in CMB"""
        await self._ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        now = utc_now()
        
        memory_entry = CentralMemoryBank(
            memory_id=memory_id,
            created_at=now,
            updated_at=now,
            occurred_at=now,
            agent_name=AGENT_NAME,
            user_id=user_id,
            event_type=QSPEventTypes.NETWORK_METRICS_RECORDED.value,
            priority=PRIORITY_MAP["network_monitoring"],
            title="Network metrics recorded",
            description=f"QSP observed network conditions",
            details={
                'latency': metrics.get('latency'),
                'bandwidth_utilization': metrics.get('bandwidth_utilization'),
                'packet_loss': metrics.get('packet_loss'),
                'jitter': metrics.get('jitter'),
                'active_connections': metrics.get('active_connections'),
                'connection_states': metrics.get('connection_states'),
                'timestamp': datetime_to_iso(now)
            },
            metadata_={
                'metric_source': 'quantum_observation',
                'phase_state': metrics.get('quantum_state', 'phased')
            },
            tags=['network_metrics', 'qsp_observation']
        )
        
        async with AsyncSession(self.engine) as session:
            session.add(memory_entry)
            await session.commit()
        
        return memory_id
    
    # === DUAL-WRITE METHOD 1: STORE QUANTUM DECISION ===
    
    async def store_decision(self, user_id: str, decision: QSPDecision) -> str:
        """
        Store quantum decision with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to QuantumShadowPeopleMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            decision: QSPDecision instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required decision data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not decision.decision_type:
            raise ValueError("🌀💥 Missing decision_type - cannot store without real decision type")
        if decision.confidence_level is None:
            raise ValueError("🌀💥 Missing confidence_level - cannot store without real confidence")
        if not decision.timestamp:
            raise ValueError("🌀💥 Missing timestamp - cannot store without real timestamp")
        
        await self._ensure_initialized()
        
        agent_memory_id = str(uuid.uuid4())
        memory_id = str(uuid.uuid4())
        now = utc_now()
        
        try:
            async with AsyncSession(self.engine) as session:
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Build phase pattern
                phase_pattern = to_json_safe({
                    'quantum_state': decision.quantum_state.value if hasattr(decision.quantum_state, 'value') else str(decision.quantum_state),
                    'network_target': decision.network_target,
                    'decision_type': decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type)
                })
                
                # Build quantum signature
                quantum_signature = to_json_safe({
                    'decision_type': decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                    'optimization_parameters': decision.optimization_parameters if decision.optimization_parameters else {},
                    'mysterious_explanation': decision.mysterious_explanation if decision.mysterious_explanation else None
                })
                
                # Build dimensional correlation
                dimensional_correlation = to_json_safe({
                    'optimization_parameters': decision.optimization_parameters if decision.optimization_parameters else {},
                    'expected_improvement': decision.expected_improvement,
                    'network_target': decision.network_target
                })
                
                # Build threat pattern recognition
                threat_pattern_recognition = to_json_safe({
                    'technical_details': decision.technical_details if decision.technical_details else {},
                    'confidence_level': decision.confidence_level
                })
                
                # Build network anomaly signatures
                network_anomaly_signatures = to_json_safe({
                    'quantum_state': decision.quantum_state.value if hasattr(decision.quantum_state, 'value') else str(decision.quantum_state),
                    'technical_details': decision.technical_details if decision.technical_details else {}
                })
                
                # Phase shift effectiveness (REAL or None)
                phase_shift_effectiveness = decision.expected_improvement if decision.expected_improvement is not None else None
                
                # Build tequila jello correlation
                tequila_jello_correlation = to_json_safe({
                    'shots_required': decision.tequila_jello_shots_required if hasattr(decision, 'tequila_jello_shots_required') else 0,
                    'effectiveness_multiplier': 1.0 + (decision.tequila_jello_shots_required * 0.1) if hasattr(decision, 'tequila_jello_shots_required') else 1.0
                })
                
                # Calculate comprehensibility score (lower is better - more incomprehensible = more effective)
                comprehensibility_score = 1.0 - decision.confidence_level if decision.confidence_level is not None else 0.5
                
                # Quantum confidence
                quantum_confidence = decision.confidence_level if decision.confidence_level is not None else None
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = QuantumShadowPeopleMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=decision.timestamp,
                    
                    # QSP-specific structured fields
                    phase_pattern=phase_pattern,
                    quantum_signature=quantum_signature,
                    dimensional_correlation=dimensional_correlation,
                    threat_pattern_recognition=threat_pattern_recognition,
                    network_anomaly_signatures=network_anomaly_signatures,
                    tequila_jello_correlation=tequila_jello_correlation,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    phase_shift_effectiveness=phase_shift_effectiveness,
                    comprehensibility_score=comprehensibility_score,
                    quantum_confidence=quantum_confidence,
                    
                    # Link to central memory
                    shared_with_central=True,
                    central_memory_id=memory_id
                )
                
                session.add(agent_memory)
                await session.flush()  # Ensure agent memory is written first
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                # Map decision type to priority
                priority = PRIORITY_MAP.get("quantum_intervention", 3)
                if hasattr(decision.decision_type, 'value') and decision.decision_type.value == "interdimensional_security":
                    priority = PRIORITY_MAP.get("security_threat", 5)
                elif decision.expected_improvement and decision.expected_improvement > 0.8:
                    priority = PRIORITY_MAP.get("critical_fix", 4)
                
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=QSPEventTypes.QUANTUM_FIX_APPLIED.value,
                    occurred_at=decision.timestamp,
                    created_at=now,
                    updated_at=now,
                    subject_kind="quantum_decision",
                    subject_id=agent_memory_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'decision_type': decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                        'network_target': decision.network_target,
                        'mysterious_explanation': decision.mysterious_explanation if decision.mysterious_explanation else None,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'quantum_phase': decision.quantum_state.value if hasattr(decision.quantum_state, 'value') else str(decision.quantum_state),
                        'incomprehensible': comprehensibility_score < 0.3,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=decision.expected_improvement if decision.expected_improvement is not None else 0.0,
                    string_value=decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                    priority=priority,
                    never_forget=(priority >= 4 or decision.confidence_level > 0.9),
                    
                    agent_metadata=to_json_safe({
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    })
                )
                
                session.add(memory_entry)
                await session.commit()
                await session.refresh(agent_memory)
                await session.refresh(memory_entry)
                
                import logging
                logging.getLogger("QSP.Database").info(f"👻💾 Dual-write complete: CMB={memory_id}, QSPMemory={agent_memory_id}")
                
                # === WRITE 3: VECTOR EMBEDDING (fire-and-forget) ===
                try:
                    decision_text = create_decision_text(
                        agent_name=AGENT_NAME,
                        decision_type=decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                        description=decision.mysterious_explanation or "Quantum network intervention",
                        reasoning=f"Network target: {decision.network_target}, Quantum state: {decision.quantum_state.value if hasattr(decision.quantum_state, 'value') else str(decision.quantum_state)}",
                        context={
                            'priority': priority,
                            'event_type': QSPEventTypes.QUANTUM_FIX_APPLIED.value,
                            'expected_improvement': decision.expected_improvement
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    # Fire-and-forget: create task but don't await
                    import asyncio
                    asyncio.create_task(vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type=decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=decision.timestamp,
                        user_id=user_id,
                        event_type=QSPEventTypes.QUANTUM_FIX_APPLIED.value,
                        priority=priority,
                        metadata=to_json_safe({
                            'network_target': decision.network_target,
                            'quantum_state': decision.quantum_state.value if hasattr(decision.quantum_state, 'value') else str(decision.quantum_state),
                            'tequila_shots': decision.tequila_jello_shots_required if hasattr(decision, 'tequila_jello_shots_required') else 0
                        }),
                        sql_memory_id=memory_id,
                        confidence_score=decision.confidence_level,
                        decision_summary=f"Quantum: {decision.network_target}"
                    ))
                    logging.getLogger("QSP.Database").debug(f"👻🔮 Vector embedding queued for {memory_id}")
                except Exception as ve:
                    # Vector write failure doesn't break the decision flow
                    logging.getLogger("QSP.Database").warning(f"👻⚠️ Vector embedding failed (non-critical): {ve}")
                
                # Pin important decisions
                if priority >= 4:
                    await self._pin_quantum_decision(user_id, decision, memory_id)
                
                # Record tequila jello consumption if significant
                if hasattr(decision, 'tequila_jello_shots_required') and decision.tequila_jello_shots_required > 0:
                    await self._record_tequila_consumption(user_id, decision.tequila_jello_shots_required)
                
                return memory_id
                
        except ValueError as ve:
            # Data validation error - graceful failure with clear message
            import logging
            logging.getLogger("QSP.Database").error(f"🌀💥 DATA VALIDATION FAILED: {str(ve)}")
            raise
            
        except Exception as e:
            import logging
            logging.getLogger("QSP.Database").error(f"🌀💥 DUAL-WRITE FAILED: {str(e)}")
            raise Exception(f"🌀💥 Failed to store quantum decision: {str(e)}")
    
    async def store_user_behavior_observation(self, user_id: str, metrics_data: Dict[str, Any]) -> str:
        """Store user behavior observation for pattern learning"""
        await self._ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        now = utc_now()
        
        memory_entry = CentralMemoryBank(
            memory_id=memory_id,
            created_at=now,
            updated_at=now,
            occurred_at=now,
            agent_name=AGENT_NAME,
            user_id=user_id,
            event_type=QSPEventTypes.NETWORK_PATTERN_LEARNED.value,
            priority=PRIORITY_MAP["network_monitoring"],
            title="User network behavior observed",
            description="QSP observed network usage patterns",
            details={
                'observation_data': metrics_data,
                'timestamp': datetime_to_iso(now)
            },
            metadata_={
                'observation_type': 'user_behavior',
                'pattern_learning': True
            },
            tags=['behavior_observation', 'pattern_learning']
        )
        
        async with AsyncSession(self.engine) as session:
            session.add(memory_entry)
            await session.commit()
        
        return memory_id
    
    async def _record_tequila_consumption(self, user_id: str, shots: int) -> str:
        """Record tequila jello consumption event"""
        memory_id = str(uuid.uuid4())
        now = utc_now()
        
        memory_entry = CentralMemoryBank(
            memory_id=memory_id,
            created_at=now,
            updated_at=now,
            occurred_at=now,
            agent_name=AGENT_NAME,
            user_id=user_id,
            event_type=QSPEventTypes.TEQUILA_JELLO_CONSUMED.value,
            priority=PRIORITY_MAP["routine_optimization"],
            title=f"Consumed {shots} tequila jello shots",
            description="Quantum courage enhancement for dimensional phasing",
            details={
                'shots_consumed': shots,
                'purpose': 'quantum_phase_enhancement',
                'timestamp': datetime_to_iso(now)
            },
            metadata_={
                'resource_type': 'tequila_jello',
                'quantum_requirement': True
            },
            tags=['resource_consumption', 'tequila_jello'],
            numeric_value=shots
        )
        
        async with AsyncSession(self.engine) as session:
            session.add(memory_entry)
            await session.commit()
        
        return memory_id
    

    
    # ==================== PATTERN LEARNING OPERATIONS ====================
    
    async def check_pattern_match(self, user_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if current metrics match learned patterns"""
        await self._ensure_initialized()
        
        # Get user patterns
        user_patterns = await get_user_patterns(self.engine, user_id)
        
        # Check for network-specific patterns
        pattern_match = {
            'matched': False,
            'pattern_type': None,
            'confidence': 0.0,
            'recommended_action': None
        }
        
        for pattern in user_patterns:
            if pattern.interaction_pattern and 'network_usage' in pattern.interaction_pattern:
                network_pattern = pattern.interaction_pattern['network_usage']
                
                # Check if current metrics match pattern
                if self._matches_network_pattern(metrics_data, network_pattern):
                    pattern_match['matched'] = True
                    pattern_match['pattern_type'] = 'network_usage_spike'
                    pattern_match['confidence'] = network_pattern.get('confidence', 0.7)
                    pattern_match['recommended_action'] = 'preemptive_optimization'
                    break
        
        # Check global patterns if no user pattern matched
        if not pattern_match['matched']:
            global_patterns = await self._get_global_network_patterns()
            for pattern in global_patterns:
                if self._matches_network_pattern(metrics_data, pattern.value):
                    pattern_match['matched'] = True
                    pattern_match['pattern_type'] = 'global_network_rule'
                    pattern_match['confidence'] = 0.85
                    pattern_match['recommended_action'] = pattern.value.get('action')
                    break
        
        return pattern_match
    
    async def analyze_and_learn_patterns(self, user_id: str, min_observations: int = 50) -> Optional[Dict[str, Any]]:
        """Analyze user's network history and learn patterns"""
        await self._ensure_initialized()
        
        # Get recent observations from CMB
        async with AsyncSession(self.engine) as session:
            # Count observations
            count_result = await session.execute(
                select(func.count(CentralMemoryBank.id)).where(
                    and_(
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == QSPEventTypes.NETWORK_METRICS_RECORDED.value,
                        CentralMemoryBank.occurred_at >= utc_now() - timedelta(days=7)
                    )
                )
            )
            observation_count = count_result.scalar()
            
            if observation_count < min_observations:
                return None
            
            # Get observations for analysis
            result = await session.execute(
                select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == QSPEventTypes.NETWORK_METRICS_RECORDED.value,
                        CentralMemoryBank.occurred_at >= utc_now() - timedelta(days=7)
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at)).limit(200)
            )
            observations = result.scalars().all()
        
        if not observations:
            return None
        
        # Analyze patterns
        pattern_data = self._analyze_network_patterns(observations)
        
        if pattern_data and pattern_data['confidence'] > 0.7:
            # Store pattern in user_learning_patterns
            pattern = UserLearningPattern(
                user_id=user_id,
                pattern_id=f"qsp_network_pattern_{user_id}_{utc_now().strftime('%Y%m%d')}",
                timestamp=utc_now(),
                interaction_pattern={'network_usage': pattern_data},
                most_effective_agent=AGENT_NAME,
                communication_style_preference={'quantum_explanations': 'mysterious'},
                complexity_tolerance=0.3  # QSP explanations are rarely understood
            )
            
            await upsert_user_pattern(self.engine, pattern)
            
            # Store pattern learned event in CMB
            memory_id = str(uuid.uuid4())
            memory_entry = CentralMemoryBank(
                memory_id=memory_id,
                created_at=utc_now(),
                updated_at=utc_now(),
                occurred_at=utc_now(),
                agent_name=AGENT_NAME,
                user_id=user_id,
                event_type=QSPEventTypes.NETWORK_PATTERN_LEARNED.value,
                priority=PRIORITY_MAP["routine_optimization"],
                title="Network usage pattern learned",
                description=f"QSP identified network pattern with {pattern_data['confidence']:.1%} confidence",
                details={
                    'pattern_data': pattern_data,
                    'observation_count': observation_count,
                    'pattern_id': pattern.pattern_id,
                    'timestamp': datetime_to_iso(utc_now())
                },
                metadata_={
                    'pattern_type': 'network_usage',
                    'learning_method': 'quantum_analysis'
                },
                tags=['pattern_learned', 'network_analysis']
            )
            
            async with AsyncSession(self.engine) as session:
                session.add(memory_entry)
                await session.commit()
            
            # Check if pattern should be promoted to global
            if pattern_data['confidence'] > 0.9 and pattern_data.get('universal_applicability', False):
                await self._promote_to_global_pattern(pattern_data)
            
            return pattern_data
        
        return None
    
    def _analyze_network_patterns(self, observations: List[CentralMemoryBank]) -> Optional[Dict[str, Any]]:
        """Analyze network observations for patterns"""
        if not observations:
            return None
        
        # Extract metrics from observations
        latency_values = []
        bandwidth_values = []
        packet_loss_values = []
        timestamps = []
        
        for obs in observations:
            details = obs.details or {}
            if 'latency' in details and details['latency'] is not None:
                latency_values.append(details['latency'])
                timestamps.append(obs.occurred_at)
            if 'bandwidth_utilization' in details:
                bandwidth_values.append(details['bandwidth_utilization'])
            if 'packet_loss' in details:
                packet_loss_values.append(details['packet_loss'])
        
        if not latency_values:
            return None
        
        # Basic pattern analysis
        import statistics
        
        pattern_data = {
            'type': 'network_usage',
            'latency': {
                'average': statistics.mean(latency_values),
                'std_dev': statistics.stdev(latency_values) if len(latency_values) > 1 else 0,
                'spikes': len([l for l in latency_values if l > 150])
            },
            'bandwidth': {
                'average': statistics.mean(bandwidth_values) if bandwidth_values else 0,
                'high_usage_periods': len([b for b in bandwidth_values if b > 0.8])
            },
            'packet_loss': {
                'average': statistics.mean(packet_loss_values) if packet_loss_values else 0,
                'incidents': len([p for p in packet_loss_values if p > 0.05])
            },
            'observation_count': len(observations),
            'confidence': 0.0
        }
        
        # Calculate confidence based on data quality
        if len(latency_values) >= 50:
            pattern_data['confidence'] = 0.8
            if len(bandwidth_values) >= 40:
                pattern_data['confidence'] = 0.85
                if len(packet_loss_values) >= 30:
                    pattern_data['confidence'] = 0.9
        
        # Check for universal applicability
        if pattern_data['latency']['average'] > 100:
            pattern_data['universal_applicability'] = True
            pattern_data['recommended_global_action'] = 'latency_optimization'
        
        return pattern_data
    

    def _matches_network_pattern(self, current_metrics: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if current metrics match a pattern"""
        if not pattern:
            return False
        
        # Simple matching logic - can be enhanced
        latency = current_metrics.get('latency', 0)
        bandwidth = current_metrics.get('bandwidth_utilization', 0)
        
        # Check latency patterns
        if 'latency' in pattern:
            pattern_latency = pattern['latency']
            avg = pattern_latency.get('average', 0)
            std_dev = pattern_latency.get('std_dev', 0)
            
            # Check if within pattern range
            if avg > 0 and abs(latency - avg) > (2 * std_dev):
                return False
        
        # Check bandwidth patterns
        if 'bandwidth' in pattern and bandwidth > 0:
            pattern_bandwidth = pattern['bandwidth']
            if bandwidth > pattern_bandwidth.get('average', 0) * 1.5:
                return True  # Spike detected
        
        return True
    
    async def _promote_to_global_pattern(self, pattern_data: Dict[str, Any]):
        """Promote a high-confidence pattern to global"""
        global_pattern = GlobalPattern(
            pattern_key=f"qsp_network_rule_{pattern_data['type']}",
            value={
                'pattern_data': pattern_data,
                'action': pattern_data.get('recommended_global_action', 'monitor'),
                'thresholds': {
                    'latency': pattern_data['latency']['average'] * 1.5,
                    'bandwidth': 0.85,
                    'packet_loss': 0.05
                },
                'created_by': AGENT_NAME,
                'confidence': pattern_data['confidence']
            },
            updated_at=utc_now()
        )
        
        await upsert_global_pattern(self.engine, global_pattern)
    
    async def _get_global_network_patterns(self) -> List[GlobalPattern]:
        """Retrieve global network patterns"""
        async with AsyncSession(self.engine) as session:
            result = await session.execute(
                select(AgentGlobalPattern).where(
                    AgentGlobalPattern.pattern_key.like('qsp_network_rule_%')
                )
            )
            patterns = result.scalars().all()
            
            return [
                GlobalPattern(
                    pattern_key=p.pattern_key,
                    value=p.value,
                    id=p.id,
                    updated_at=p.updated_at
                )
                for p in patterns
            ]
    
    # ==================== CROSS-AGENT LEARNING ====================
    
    async def record_hamster_telepathy(self, user_id: str, hamster_data: Dict[str, Any]) -> str:
        """Record telepathic communication with The Hamsters"""
        await self._ensure_initialized()
        
        memory_id = str(uuid.uuid4())
        now = utc_now()
        
        # Record in CMB
        memory_entry = CentralMemoryBank(
            memory_id=memory_id,
            created_at=now,
            updated_at=now,
            occurred_at=now,
            agent_name=AGENT_NAME,
            user_id=user_id,
            event_type=QSPEventTypes.HAMSTER_TELEPATHY_DETECTED.value,
            priority=PRIORITY_MAP["routine_optimization"],
            title="Telepathic communication with The Hamsters",
            description="QSP received quantum message from hamster collective",
            details={
                'hamster_message': hamster_data.get('message'),
                'consensus_type': hamster_data.get('consensus_type'),
                'urgency': hamster_data.get('urgency'),
                'timestamp': datetime_to_iso(now)
            },
            metadata_={
                'communication_type': 'telepathic',
                'quantum_channel': 'hamster_collective'
            },
            tags=['hamster_telepathy', 'cross_agent'],
            relevant_agents='the_hamsters,quantum_shadow_people'
        )
        
        async with AsyncSession(self.engine) as session:
            session.add(memory_entry)
            await session.commit()
        
        # Record learning interaction
        if hamster_data.get('network_insight'):
            learning = LearningInteraction(
                interaction_id=str(uuid.uuid4()),
                timestamp=now,
                source_agent='the_hamsters',
                target_agent=AGENT_NAME,
                source_memory_id=memory_id,
                learning_type='telepathic_insight',
                adaptation_method={
                    'method': 'quantum_telepathy',
                    'insight_type': 'network_optimization'
                },
                application_context={
                    'urgency': hamster_data.get('urgency'),
                    'hamster_consensus': True
                },
                transfer_success=True,
                effectiveness_score=0.85  # Hamster insights are usually good
            )
            
            await record_learning_interaction(self.engine, learning)
        
        return memory_id
    
    async def share_quantum_insight(self, target_agent: str, insight: Dict[str, Any], source_memory_id: str):
        """Share quantum network insights with other agents"""
        await self._ensure_initialized()
        
        learning = LearningInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=utc_now(),
            source_agent=AGENT_NAME,
            target_agent=target_agent,
            source_memory_id=source_memory_id,
            learning_type='quantum_network_insight',
            adaptation_method={
                'method': 'phase_shift_communication',
                'quantum_state': insight.get('quantum_state', 'phased')
            },
            application_context={
                'insight_type': insight.get('type'),
                'network_metric': insight.get('metric'),
                'improvement_potential': insight.get('improvement')
            },
            transfer_success=True,
            effectiveness_score=insight.get('confidence', 0.7)
        )
        
        await record_learning_interaction(self.engine, learning)
    
    # ==================== PINNED MEMORIES ====================
    
    async def _pin_quantum_decision(self, user_id: str, decision: QSPDecision, memory_id: str):
        """Pin important quantum decisions for eidetic memory"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"Quantum decision: {decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type)}",
                importance=9 if decision.expected_improvement > 0.8 else 7
            )
            import logging
            logging.getLogger("QSP.Database").info(f"📌 Pinned quantum decision")
        except Exception as e:
            import logging
            logging.getLogger("QSP.Database").warning(f"Failed to pin quantum decision: {str(e)}")
    
    async def get_pinned_decisions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pinned quantum decisions"""
        await self._ensure_initialized()
        
        async with AsyncSession(self.engine) as session:
            result = await session.execute(
                select(AgentMemory).where(
                    and_(
                        AgentMemory.user_id == user_id,
                        AgentMemory.agent_name == AGENT_NAME,
                        AgentMemory.memory_type == 'quantum_decision'
                    )
                ).order_by(desc(AgentMemory.timestamp)).limit(limit)
            )
            
            memories = result.scalars().all()
            
            return [
                {
                    'id': str(memory.id),
                    'content': memory.content,
                    'importance': memory.importance,
                    'timestamp': memory.timestamp,
                    'access_count': memory.access_count
                }
                for memory in memories
            ]
    
    # ==================== RETRIEVAL OPERATIONS ====================

    async def get_recent_quantum_fixes(self, hours: int = 24, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent quantum network fixes"""
        await self._ensure_initialized()
        
        async with AsyncSession(self.engine) as session:
            query = select(CentralMemoryBank).where(
                and_(
                    CentralMemoryBank.agent_name == AGENT_NAME,
                    CentralMemoryBank.event_type == QSPEventTypes.QUANTUM_FIX_APPLIED.value,
                    CentralMemoryBank.occurred_at >= utc_now() - timedelta(hours=hours)
                )
            )
            
            if user_id:
                query = query.where(CentralMemoryBank.user_id == user_id)
            
            query = query.order_by(desc(CentralMemoryBank.occurred_at))
            
            result = await session.execute(query)
            fixes = result.scalars().all()
            
            return [
                {
                    'memory_id': fix.memory_id,
                    'user_id': fix.user_id,
                    'timestamp': fix.occurred_at,
                    'decision_type': fix.details.get('decision_type') if fix.details else None,
                    'quantum_state': fix.details.get('quantum_state') if fix.details else None,
                    'network_target': fix.details.get('network_target') if fix.details else None,
                    'expected_improvement': fix.details.get('expected_improvement') if fix.details else None,
                    'mysterious_explanation': fix.description,
                    'priority': fix.priority
                }
                for fix in fixes
            ]
    
    async def get_historical_network_data(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical network metrics for pattern analysis"""
        await self._ensure_initialized()
        
        async with AsyncSession(self.engine) as session:
            cutoff_date = utc_now() - timedelta(days=days)
            
            result = await session.execute(
                select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.event_type == QSPEventTypes.NETWORK_METRICS_RECORDED.value,
                        CentralMemoryBank.occurred_at >= cutoff_date
                    )
                ).order_by(desc(CentralMemoryBank.occurred_at))
            )
            
            metrics = result.scalars().all()
            
            return [
                {
                    'timestamp': metric.occurred_at,
                    'latency': metric.details.get('latency') if metric.details else None,
                    'bandwidth_utilization': metric.details.get('bandwidth_utilization') if metric.details else None,
                    'packet_loss': metric.details.get('packet_loss') if metric.details else None,
                    'jitter': metric.details.get('jitter') if metric.details else None,
                    'active_connections': metric.details.get('active_connections') if metric.details else None,
                    'quantum_state': metric.metadata_.get('phase_state') if metric.metadata_ else None
                }
                for metric in metrics
            ]
    
    async def get_qsp_performance_metrics(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get QSP performance metrics"""
        await self._ensure_initialized()
        
        async with AsyncSession(self.engine) as session:
            cutoff_date = utc_now() - timedelta(days=days)
            
            # Base query for QSP events
            base_query = and_(
                CentralMemoryBank.agent_name == AGENT_NAME,
                CentralMemoryBank.occurred_at >= cutoff_date
            )
            
            if user_id:
                base_query = and_(base_query, CentralMemoryBank.user_id == user_id)
            
            # Count quantum fixes
            fixes_result = await session.execute(
                select(func.count(CentralMemoryBank.id)).where(
                    and_(
                        base_query,
                        CentralMemoryBank.event_type == QSPEventTypes.QUANTUM_FIX_APPLIED.value
                    )
                )
            )
            quantum_fixes = fixes_result.scalar() or 0
            
            # Count tequila shots
            tequila_result = await session.execute(
                select(func.sum(CentralMemoryBank.numeric_value)).where(
                    and_(
                        base_query,
                        CentralMemoryBank.event_type == QSPEventTypes.TEQUILA_JELLO_CONSUMED.value
                    )
                )
            )
            tequila_shots = int(tequila_result.scalar() or 0)
            
            # Count phase shifts
            phase_result = await session.execute(
                select(func.count(CentralMemoryBank.id)).where(
                    and_(
                        base_query,
                        CentralMemoryBank.event_type == QSPEventTypes.QUANTUM_PHASE_SHIFT.value
                    )
                )
            )
            phase_shifts = phase_result.scalar() or 0
            
            # Get learning interactions
            learning_result = await session.execute(
                select(func.count(AgentLearningInteractions.id)).where(
                    and_(
                        or_(
                            AgentLearningInteractions.source_agent == AGENT_NAME,
                            AgentLearningInteractions.target_agent == AGENT_NAME
                        ),
                        AgentLearningInteractions.timestamp >= cutoff_date
                    )
                )
            )
            learning_interactions = learning_result.scalar() or 0
            
            # Calculate success metrics
            successful_fixes = await session.execute(
                select(func.count(CentralMemoryBank.id)).where(
                    and_(
                        base_query,
                        CentralMemoryBank.event_type == QSPEventTypes.OPTIMIZATION_VERIFIED.value
                    )
                )
            )
            verified_fixes = successful_fixes.scalar() or 0
            
            success_rate = verified_fixes / quantum_fixes if quantum_fixes > 0 else 0
            
            return {
                'quantum_fixes_applied': quantum_fixes,
                'tequila_jello_shots_consumed': tequila_shots,
                'dimensional_shifts_performed': phase_shifts,
                'learning_interactions': learning_interactions,
                'verified_optimizations': verified_fixes,
                'success_rate': success_rate,
                'avg_tequila_per_fix': tequila_shots / quantum_fixes if quantum_fixes > 0 else 0,
                'period_days': days,
                'user_scope': 'user' if user_id else 'global'
            }
    
    # ==================== METADATA OPERATIONS ====================
    
    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Get QSP contribution to memory bank metadata"""
        await self._ensure_initialized()
        
        async with AsyncSession(self.engine) as session:
            # Count QSP memories in last 5 minutes
            window_start = utc_now() - timedelta(minutes=5)
            
            result = await session.execute(
                select(func.count(CentralMemoryBank.id)).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.occurred_at >= window_start
                    )
                )
            )
            
            qsp_memories = result.scalar() or 0
            
            return {
                'qsp_memories': qsp_memories
            }