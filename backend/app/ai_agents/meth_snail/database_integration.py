"""
Meth Snail Database Integration
DUAL-WRITE ARCHITECTURE: Agent-Specific Table + Central Memory Bank
NO FAKE DATA POLICY: Real data or graceful failure
"""
import asyncio
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union
import json
import uuid

from sqlalchemy import select, func, desc, and_, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Import base class
from app.ai_agents.distributed.base_database_integration import BaseDatabaseIntegration, utc_now

# Import all required models
from app.models.agent_memory_banks import (
    CentralMemoryBank,
    MethSnailMemoryBank,
    UserLearningPatterns, 
    AgentLearningInteractions,
)
from app.models.agent_memory import (
    AgentGlobalPattern,
    AgentMemory
)
from app.ai_agents.meth_snail.constants import (
    AGENT_NAME,
    MIN_OBSERVATIONS_FOR_PATTERN,
    PATTERN_CONFIDENCE_THRESHOLD,
    PRIORITY_SHELL_SPIN,
    PRIORITY_HIGH_CONFIDENCE_DECISION,
    PRIORITY_HYPERCAFFEINATED,
    LEARNING_TYPES,
    PATTERN_CATEGORIES,
    EVENT_TYPES
)
from app.core.learning_helpers import (
    get_learning_effectiveness,
    get_user_patterns,
    pin_memory,
)
from app.utils.json_safety import to_json_safe
from app.ai_agents.meth_snail.data_types import OptimizationDecision, ShellSpinIncident
from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage

logger = logging.getLogger("MethSnail.Database")


class MethSnailDatabaseIntegration(BaseDatabaseIntegration):
    """
    Database integration for Meth Snail's optimization engine.
    
    Now with full pattern learning capabilities!
    Inherits from BaseDatabaseIntegration for consistent session management.
    """
    
    def _get_agent_name(self) -> str:
        """Return agent name for base class"""
        return AGENT_NAME
    
    async def store_decision(self, user_id: str, decision: OptimizationDecision) -> str:
        """
        Required by base class - alias for store_optimization_decision
        """
        return await self.store_optimization_decision(user_id, decision)
    
    # === DUAL-WRITE METHOD 1: STORE OPTIMIZATION DECISION ===
    
    async def store_optimization_decision(self, user_id: str, decision: OptimizationDecision) -> str:
        """
        Store optimization decision with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to MethSnailMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            decision: OptimizationDecision instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required decision data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not decision.priority:
            raise ValueError("🐌💥 Missing priority - cannot store without real priority")
        if decision.confidence is None:
            raise ValueError("🐌💥 Missing confidence - cannot store without real confidence value")
        if not decision.timestamp:
            raise ValueError("🐌💥 Missing timestamp - cannot store without real timestamp")
        
        await self.ensure_initialized()
        
        # Generate IDs
        agent_memory_id = str(uuid.uuid4())
        central_memory_id = str(uuid.uuid4())
        
        # Use self.get_session() from base class
        async for session in self.get_session():
            try:
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Build optimization pattern
                optimization_pattern = to_json_safe({
                    'priority': decision.priority.value if hasattr(decision.priority, 'value') else str(decision.priority),
                    'actions': decision.actions,
                    'urgency': decision.urgency,
                    'estimated_impact': decision.estimated_impact
                })
                
                # Build caffeine level context
                caffeine_level_context = decision.caffeine_level_mg if decision.caffeine_level_mg else None
                
                # Build shell spin correlation
                shell_spin_correlation = to_json_safe({
                    'shell_spin_count': decision.shell_spin_count,
                    'data_quality_score': decision.data_quality_score,
                    'analysis_depth': decision.analysis_depth.value if hasattr(decision.analysis_depth, 'value') else str(decision.analysis_depth)
                })
                
                # Build jitter threshold learning
                jitter_threshold_learning = to_json_safe({
                    'current_jitter_level': decision.current_jitter_level,
                    'is_decaffeinated': decision.is_decaffeinated,
                    'requires_energy_drink': decision.requires_energy_drink
                })
                
                # Calculate performance improvement (REAL or None)
                performance_improvement = None
                if decision.estimated_impact and 'performance_gain' in decision.estimated_impact:
                    performance_improvement = decision.estimated_impact['performance_gain']
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = MethSnailMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=decision.timestamp,
                    
                    # Snail-specific structured fields
                    optimization_pattern=optimization_pattern,
                    caffeine_level_context=caffeine_level_context,
                    shell_spin_correlation=shell_spin_correlation,
                    jitter_threshold_learning=jitter_threshold_learning,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    performance_improvement=performance_improvement,
                    confidence_level=decision.confidence,
                    
                    # Link to central memory
                    shared_with_central=True,
                    central_memory_id=central_memory_id
                )
                
                session.add(agent_memory)
                await session.flush()  # Ensure agent memory is written first
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                priority = PRIORITY_HIGH_CONFIDENCE_DECISION if decision.confidence > 0.8 else 5
                
                central_memory = CentralMemoryBank(
                    memory_id=central_memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=EVENT_TYPES["OPTIMIZATION_APPLIED"],
                    occurred_at=decision.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="optimization_decision",
                    subject_id=agent_memory_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'priority': decision.priority.value if hasattr(decision.priority, 'value') else str(decision.priority),
                        'urgency': decision.urgency,
                        'rationale': decision.rationale,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'caffeinated': not decision.is_decaffeinated,
                        'shell_spinning': decision.shell_spin_count > 0,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=decision.confidence,
                    string_value=decision.urgency,
                    priority=priority,
                    never_forget=(decision.confidence > 0.9),
                    
                    agent_metadata=to_json_safe({
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
                        decision_type="optimization",
                        description=decision.urgency,
                        reasoning=decision.rationale if decision.rationale else "Memory optimization",
                        context={
                            'priority': priority,
                            'confidence': decision.confidence,
                            'caffeinated': not decision.is_decaffeinated
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="optimization",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=decision.timestamp,
                        user_id=user_id,
                        event_type=EVENT_TYPES["OPTIMIZATION_APPLIED"],
                        priority=priority,
                        metadata=to_json_safe({
                            'urgency': decision.urgency,
                            'confidence': decision.confidence,
                            'caffeinated': not decision.is_decaffeinated
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=decision.confidence,
                        decision_summary=f"Optimization: {decision.urgency}"
                    )
                    logger.debug(f"🔮 Queued vector embedding for optimization {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                await self.log_dual_write_success(
                    "optimization_decision", 
                    agent_memory_id, 
                    central_memory_id
                )
                
                # Pin high confidence decisions
                if decision.confidence > 0.9:
                    await self._pin_optimization(user_id, decision, central_memory_id)
                
                return central_memory_id
                
            except ValueError as ve:
                await session.rollback()
                await self.log_dual_write_failure("optimization_decision", ve)
                raise
                
            except Exception as e:
                await session.rollback()
                await self.log_dual_write_failure("optimization_decision", e)
                raise
    
    async def _pin_optimization(self, user_id: str, decision: OptimizationDecision, memory_id: str):
        """Pin high confidence optimizations"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"High confidence optimization: {decision.confidence:.2f}",
                importance=9
            )
            logger.info(f"📌 Pinned optimization: confidence {decision.confidence:.2f}")
        except Exception as e:
            logger.warning(f"Failed to pin optimization: {str(e)}")
    
    # === DUAL-WRITE METHOD 2: STORE SHELL SPIN INCIDENT ===
    
    async def store_shell_spin_incident(self, user_id: str, incident: ShellSpinIncident) -> str:
        """
        Store shell spin incident with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to MethSnailMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            incident: ShellSpinIncident instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required incident data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not incident.reason:
            raise ValueError("🐌💥 Missing reason - cannot store without real reason")
        if not incident.timestamp:
            raise ValueError("🐌💥 Missing timestamp - cannot store without real timestamp")
        
        await self.ensure_initialized()
        
        # Generate IDs
        agent_memory_id = str(uuid.uuid4())
        central_memory_id = str(uuid.uuid4())
        
        # Use self.get_session() from base class
        async for session in self.get_session():
            try:
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Build shell spin correlation
                shell_spin_correlation = to_json_safe({
                    'missing_metrics': incident.missing_metrics if incident.missing_metrics else [],
                    'invalid_metrics': incident.invalid_metrics if incident.invalid_metrics else [],
                    'reason': incident.reason
                })
                
                # Build optimization pattern (what was attempted)
                optimization_pattern = to_json_safe({
                    'attempted_analysis': True,
                    'data_validation_failed': True,
                    'requires_real_data': True
                })
                
                # Calculate data quality score
                total_metrics = len(incident.missing_metrics if incident.missing_metrics else []) + len(incident.invalid_metrics if incident.invalid_metrics else [])
                data_quality_score = 0.0 if total_metrics > 0 else 1.0
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = MethSnailMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=incident.timestamp,
                    
                    # Snail-specific structured fields
                    optimization_pattern=optimization_pattern,
                    shell_spin_correlation=shell_spin_correlation,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    performance_improvement=None,  # No optimization occurred
                    confidence_level=0.0,  # No confidence in fake data
                    
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
                    event_type=EVENT_TYPES["SHELL_SPIN_DETECTED"],
                    occurred_at=incident.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="shell_spin_incident",
                    subject_id=agent_memory_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'reason': incident.reason,
                        'missing_count': len(incident.missing_metrics) if incident.missing_metrics else 0,
                        'invalid_count': len(incident.invalid_metrics) if incident.invalid_metrics else 0,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'shell_spinning': True,
                        'data_quality_failure': True,
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=data_quality_score,
                    string_value='shell_spin',
                    priority=PRIORITY_SHELL_SPIN,
                    never_forget=True,  # Always remember data quality issues
                    
                    agent_metadata=to_json_safe({
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
                        decision_type="shell_spin",
                        description=f"Shell spin: {incident.reason}",
                        reasoning=f"Data quality failure - Missing: {len(incident.missing_metrics) if incident.missing_metrics else 0}, Invalid: {len(incident.invalid_metrics) if incident.invalid_metrics else 0}",
                        context={
                            'priority': PRIORITY_SHELL_SPIN,
                            'event_type': EVENT_TYPES["SHELL_SPIN_DETECTED"],
                            'affected_agents': []
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="shell_spin",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=incident.timestamp,
                        user_id=user_id,
                        event_type=EVENT_TYPES["SHELL_SPIN_DETECTED"],
                        priority=PRIORITY_SHELL_SPIN,
                        metadata=to_json_safe({
                            'reason': incident.reason,
                            'missing_metrics': incident.missing_metrics if incident.missing_metrics else [],
                            'invalid_metrics': incident.invalid_metrics if incident.invalid_metrics else []
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=0.0,
                        decision_summary=f"Shell spin: {incident.reason}"
                    )
                    logger.debug(f"🔮 Queued vector embedding for shell spin {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                logger.info(
                    f"🐌✨ DUAL-WRITE SUCCESS: Shell spin incident stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id})"
                )
                
                # Pin shell spin incidents - they're important for learning
                await self._pin_shell_spin(user_id, incident, central_memory_id)
                
                return central_memory_id
                
            except ValueError as ve:
                # Data validation error - graceful failure with clear message
                await session.rollback()
                logger.error(f"🐌💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"🐌💥 DUAL-WRITE FAILED: {str(e)}")
                raise Exception(f"🐌💥 Failed to store shell spin incident: {str(e)}")
    
    async def _pin_shell_spin(self, user_id: str, incident: ShellSpinIncident, memory_id: str):
        """Pin shell spin incidents for learning"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"Shell spin: {incident.reason}",
                importance=8
            )
            logger.info(f"📌 Pinned shell spin incident")
        except Exception as e:
            logger.warning(f"Failed to pin shell spin: {str(e)}")

    async def store_optimization_metrics(self, user_id: str, metrics_data: dict) -> str:
        """Store optimization metrics in central memory bank and check for patterns."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Calculate improvement metrics if available
            cpu_improvement = None
            memory_improvement = None
            
            if metrics_data.get('cpu_usage_before') is not None and metrics_data.get('cpu_usage_after') is not None:
                cpu_improvement = metrics_data['cpu_usage_before'] - metrics_data['cpu_usage_after']
            if metrics_data.get('memory_usage_before') is not None and metrics_data.get('memory_usage_after') is not None:
                memory_improvement = metrics_data['memory_usage_before'] - metrics_data['memory_usage_after']
            
            # Determine priority based on optimization success
            priority = PRIORITY_OPTIMIZATION_SUCCESS if metrics_data.get('optimization_success', False) else 5
            
            # Create memory_id first
            memory_id = str(uuid.uuid4())
            
            # Create the details dict
            details_dict = {
                "cpu_usage_before": metrics_data.get('cpu_usage_before'),
                "cpu_usage_after": metrics_data.get('cpu_usage_after'),
                "memory_usage_before": metrics_data.get('memory_usage_before'),
                "memory_usage_after": metrics_data.get('memory_usage_after'),
                "optimization_success": metrics_data.get('optimization_success', False),
                "energy_drink_level": metrics_data.get('energy_drink_level', 0),
                "shell_spin_count": metrics_data.get('shell_spin_count', 0),
                "raw_metrics": metrics_data.get('raw_metrics', {})
            }
            
            metadata_dict = {
                "agent_version": "2.0",
                "caffeinated": metrics_data.get('energy_drink_level', 0) > 0,
                "foil_hat_equipped": True,
                "pattern_learning_enabled": True
            }
            
            # Create central memory bank entry
            memory_entry = CentralMemoryBank(
                memory_id=memory_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                occurred_at=datetime.now(),
                agent_name=self.agent_name,
                user_id=user_id,
                event_type=EventTypes.METRICS_ANALYZED.value,
                subject_kind="system_performance",
                subject_id=user_id,
                priority=priority,
                title="Meth Snail Optimization Metrics",
                description=f"Optimization metrics - Success: {metrics_data.get('optimization_success', False)}",
                details=details_dict,
                metadata_=metadata_dict,
                numeric_value=float(memory_improvement or cpu_improvement or 0.0),
                string_value="optimization_complete" if metrics_data.get('optimization_success') else "optimization_failed",
                tags=json.dumps(["optimization", "performance", "meth_snail"]),
                agent_metadata={"shell_spin_count": metrics_data.get('shell_spin_count', 0)},
                relevant_agents="meth_snail,the_stick",
                cross_agent_validated=False,
                validation_count=0,
                stick_anxiety_level=0.0,
                never_forget=metrics_data.get('shell_spin_count', 0) > 5,
                times_referenced=0,
                successful_applications=1 if metrics_data.get('optimization_success') else 0
            )
            
            self.session.add(memory_entry)
            await self.session.commit()
            
            # Check for patterns after storing metrics
            await self._check_for_optimization_patterns(user_id, memory_id)
            
            # If high shell spin count, share with other agents
            # If high shell spin count, share with other agents
            if metrics_data.get('shell_spin_count', 0) > 3:
                await self._share_shell_spin_pattern(user_id, memory_id, metrics_data)
            
            return memory_id
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to store optimization metrics: {e}")
            raise

    async def get_historical_performance(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get historical performance data from central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.METRICS_ANALYZED.value)
                .where(CentralMemoryBank.occurred_at >= cutoff_date)
                .order_by(desc(CentralMemoryBank.occurred_at))
            )
            
            historical_data = result.scalars().all()
            
            if not historical_data:
                return {
                    'status': 'no_data',
                    'message': "No historical data available",
                    'data': []
                }
            
            # Apply learned patterns to enhance historical data
            enhanced_data = []
            for record in historical_data:
                data_point = {
                    'timestamp': record.occurred_at,
                    'cpu_improvement': record.details.get('cpu_usage_before', 0) - record.details.get('cpu_usage_after', 0) 
                        if record.details.get('cpu_usage_before') and record.details.get('cpu_usage_after') else None,
                    'memory_improvement': record.details.get('memory_usage_before', 0) - record.details.get('memory_usage_after', 0) 
                        if record.details.get('memory_usage_before') and record.details.get('memory_usage_after') else None,
                    'optimization_success': record.details.get('optimization_success', False),
                    'energy_drink_level': record.details.get('energy_drink_level', 0),
                    'shell_spin_count': record.details.get('shell_spin_count', 0)
                }
                enhanced_data.append(data_point)
            
            # Get learned patterns for context
            patterns = await get_learning_effectiveness(
                self.session,
                user_id,
                self.agent_name,
                pattern_type="optimization"
            )
            
            return {
                'status': 'success',
                'data': enhanced_data,
                'learned_patterns': patterns,
                'pattern_insights': await self._analyze_historical_patterns(enhanced_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get historical performance: {e}")
            raise

    async def store_decision(self, user_id: str, decision_data: dict) -> str:
        """Store an optimization decision in central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        async for session in self.db_getter():
            try:
                memory_id = str(uuid.uuid4())
                
                # Determine priority based on confidence
                priority = PRIORITY_HIGH_CONFIDENCE_DECISION if decision_data.get('confidence_level', 0) > 0.8 else 5
                
                memory_entry = CentralMemoryBank(
                    memory_id=memory_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=datetime.utcnow(),
                    agent_name=self.agent_name,
                    user_id=user_id,
                    event_type="decision_made",  # Fixed: EventTypes doesn't exist
                    subject_kind="optimization_decision",
                    subject_id=memory_id,
                    priority=priority,
                    title=f"Meth Snail Decision: {decision_data.get('decision_type', 'unknown')}",
                    description=decision_data.get('context', str(decision_data)),
                    details=decision_data,
                    metadata_={
                        "confidence_level": decision_data.get('confidence_level', 0),
                        "energy_drink_consumed": decision_data.get('energy_drink_consumed', False),
                        "optimization_applied": decision_data.get('optimization_applied', False),
                        "shell_spinning_triggered": decision_data.get('shell_spinning_triggered', False)
                    },
                    numeric_value=decision_data.get('confidence_level', 0),
                    string_value=decision_data.get('decision_type', 'unknown'),
                    tags=json.dumps(["decision", "optimization", "meth_snail"]),
                    agent_metadata={
                        "caffeinated": decision_data.get('energy_drink_consumed', False),
                        "shell_spinning": decision_data.get('shell_spinning_triggered', False)
                    },
                    relevant_agents="meth_snail,vic20,the_stick",
                    cross_agent_validated=False,
                    validation_count=0,
                    stick_anxiety_level=0.1 if decision_data.get('shell_spinning_triggered') else 0.0,
                    never_forget=decision_data.get('confidence_level', 0) > 0.9,
                    times_referenced=0,
                    successful_applications=0
                )
                
                session.add(memory_entry)
                await session.commit()
                
                self.logger.info(f"🐌💾 Stored decision to PostgreSQL: {memory_id}")
                return memory_id
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to store decision: {e}")
                raise

    async def increment_shell_spin_count(self, user_id: str) -> None:
        """Record a shell spin incident in central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        try:
            memory_id = str(uuid.uuid4())
            
            # Shell spins are always high priority
            memory_entry = CentralMemoryBank(
                memory_id=memory_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                occurred_at=datetime.utcnow(),
                agent_name=self.agent_name,
                user_id=user_id,
                event_type=EventTypes.ANOMALY_DETECTED.value,
                subject_kind="data_quality_issue",
                subject_id=user_id,
                priority=PRIORITY_SHELL_SPIN,
                title="Meth Snail Shell Spin Detected",
                description="Shell spinning due to insufficient or invalid data",
                details={
                    "incident_type": "shell_spin",
                    "cause": "insufficient_data",
                    "timestamp": datetime.utcnow().isoformat()
                },
                metadata_={
                    "requires_attention": True,
                    "data_quality_issue": True
                },
                numeric_value=1.0,
                string_value="shell_spin",
                tags=json.dumps(["shell_spin", "data_quality", "incident", "meth_snail"]),
                agent_metadata={
                    "spinning": True,
                    "foil_hat_status": "wobbling"
                },
                relevant_agents="meth_snail,sir_hawkington,the_stick",
                cross_agent_validated=False,
                validation_count=0,
                stick_anxiety_level=0.5,
                never_forget=True,
                times_referenced=0,
                successful_applications=0
            )
            
            self.session.add(memory_entry)
            await self.session.commit()
            
            # Pin shell spin memory (priority >= 8)
            await self._pin_shell_spin_memory(user_id, memory_id)
            
            # Check for shell spin patterns
            await self._check_for_shell_spin_patterns(user_id, memory_id)
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to record shell spin incident: {e}")
            raise

    async def get_jitter_levels(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent jitter level history from central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.STATE_CHANGED.value)
                .where(CentralMemoryBank.subject_kind == "jitter_level")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(limit)
            )
            
            jitter_records = result.scalars().all()
            
            # Apply learned patterns to jitter data
            jitter_patterns = await get_agent_learned_patterns(
                self.session,
                user_id,
                self.agent_name,
                pattern_type="caffeine_management"
            )
            
            return [
                {
                    'timestamp': record.occurred_at,
                    'current_jitter_level': record.details.get('current_jitter_level', 0.0),
                    'caffeine_level_mg': record.details.get('caffeine_level_mg', 0.0),
                    'focus_level': record.details.get('focus_level', 0.5),
                    'energy_source': record.details.get('energy_source', 'none'),
                    'jitter_trend': record.details.get('jitter_trend', 'stable'),
                    'pattern_match': self._check_jitter_pattern_match(
                        record.details.get('current_jitter_level', 0.0),
                        jitter_patterns
                    )
                } for record in jitter_records
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get jitter levels: {e}")
            raise
    
    async def update_jitter_levels(self, user_id: str, jitter_data: Dict[str, Any]) -> str:
        """Store jitter level update in central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        try:
            memory_id = str(uuid.uuid4())
            
            # Determine jitter severity for priority
            jitter_level = jitter_data.get('current_jitter_level', 0.0)
            if jitter_level > 0.8:
                priority = PRIORITY_HYPERCAFFEINATED
                jitter_status = "HYPERCAFFEINATED"
            elif jitter_level > 0.6:
                priority = 7
                jitter_status = "JITTERY"
            else:
                priority = 5
                jitter_status = "NORMAL"
            
            memory_entry = CentralMemoryBank(
                memory_id=memory_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                occurred_at=datetime.utcnow(),
                agent_name=self.agent_name,
                user_id=user_id,
                event_type=EventTypes.STATE_CHANGED.value,
                subject_kind="jitter_level",
                subject_id=self.agent_name,
                priority=priority,
                title=f"Meth Snail Jitter Level: {jitter_status}",
                description=f"Jitter level update - {jitter_data.get('jitter_trend', 'stable')} trend",
                details=jitter_data,
                metadata_={
                    "requires_stick_intervention": jitter_data.get('requires_stick_intervention', False),
                    "vic20_mediation_requested": jitter_data.get('vic20_mediation_requested', False),
                    "hypercaffeinated": jitter_data.get('hypercaffeinated', False),
                    "is_decaffeinated": jitter_data.get('is_decaffeinated', False)
                },
                numeric_value=jitter_level,
                string_value=jitter_status,
                tags=json.dumps(["jitter", "caffeine", "agent_state", "meth_snail"]),
                agent_metadata={
                    "caffeine_level_mg": jitter_data.get('caffeine_level_mg', 0.0),
                    "shell_spin_probability": jitter_data.get('shell_spin_probability', 0.05),
                    "optimization_effectiveness": jitter_data.get('optimization_effectiveness', 0.9),
                    "foil_hat_status": "secure" if jitter_level < 0.6 else "vibrating"
                },
                relevant_agents="meth_snail,sir_hawkington,the_stick,vic20" if jitter_data.get('vic20_mediation_requested') else "meth_snail,the_stick",
                cross_agent_validated=False,
                validation_count=0,
                stick_anxiety_level=jitter_level * 0.8,
                never_forget=jitter_level > 0.9,
                times_referenced=0,
                successful_applications=0
            )
            
            self.session.add(memory_entry)
            await self.session.commit()
            
            # Pin extreme jitter events
            if priority >= 8:
                await self._pin_jitter_memory(user_id, memory_id, jitter_data)
            
            # Check for jitter patterns
            await self._check_for_jitter_patterns(user_id, memory_id)
            
            return memory_id
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to update jitter levels: {e}")
            raise

    async def get_optimization_history(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent optimization history from central memory bank."""
        if not self._initialized:
            await self.initialize()
            
        try:
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.DECISION_MADE.value)
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(limit)
            )
            
            decisions = result.scalars().all()
            return [
                {
                    'id': decision.memory_id,
                    'timestamp': decision.occurred_at,
                    'decision_type': decision.string_value,
                    'confidence_level': decision.numeric_value,
                    'optimization_applied': decision.metadata_.get('optimization_applied', False),
                    'shell_spinning_triggered': decision.metadata_.get('shell_spinning_triggered', False)
                } for decision in decisions
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {e}")
            raise

    async def store_energy_consumption(self, user_id: str, energy_drink_type: str, 
                                     caffeine_mg: float, consumption_time: datetime, 
                                     authorization_id: str) -> str:
        """Store energy drink consumption in central memory bank"""
        if not self._initialized:
            await self.initialize()
            
        try:
            memory_id = str(uuid.uuid4())
            
            memory_entry = CentralMemoryBank(
                memory_id=memory_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                occurred_at=consumption_time,
                agent_name=self.agent_name,
                user_id=user_id,
                event_type=EventTypes.ACTION_TAKEN.value,
                subject_kind="caffeine_intake",
                subject_id=authorization_id,
                priority=6,
                title=f"Meth Snail Energy Drink: {energy_drink_type}",
                description=f"Consumed {caffeine_mg}mg caffeine via {energy_drink_type}",
                details={
                    "energy_drink_type": energy_drink_type,
                    "caffeine_mg": caffeine_mg,
                    "authorization_id": authorization_id,
                    "consumption_time": consumption_time.isoformat()
                },
                metadata_={
                    "authorized": True,
                    "bromance_approved": "sir_hawkington" in authorization_id
                },
                numeric_value=caffeine_mg,
                string_value=energy_drink_type,
                tags=json.dumps(["energy_drink", "caffeine", "consumption", "meth_snail"]),
                agent_metadata={
                    "caffeinated": True,
                    "energy_source": energy_drink_type
                },
                relevant_agents="meth_snail,sir_hawkington,the_stick",
                cross_agent_validated=True,
                validation_count=1,
                stick_anxiety_level=0.2,
                never_forget=caffeine_mg > 200,
                times_referenced=0,
                successful_applications=0
            )
            
            self.session.add(memory_entry)
            await self.session.commit()
            
            # Check for caffeine patterns
            await self._check_for_caffeine_patterns(user_id, memory_id)
            
            return memory_id
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to store energy consumption: {e}")
            raise

    async def get_recent_jitter_levels(self, user_id: str, hours: int = 1) -> Dict[str, Any]:
        """Get recent jitter levels for safety checks"""
        if not self._initialized:
            await self.initialize()
            
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.STATE_CHANGED.value)
                .where(CentralMemoryBank.subject_kind == "jitter_level")
                .where(CentralMemoryBank.occurred_at >= cutoff_time)
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(1)
            )
            
            latest_jitter = result.scalar_one_or_none()
            
            if latest_jitter:
                return {
                    'status': 'success',
                    'current_jitter': latest_jitter.numeric_value,
                    'jitter_levels': [latest_jitter.details]
                }
            else:
                return {
                    'status': 'no_data',
                    'message': 'No recent jitter data available'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get recent jitter levels: {e}")
            raise

    async def get_energy_consumption_history(self, user_id: str, days: int = 1) -> Dict[str, Any]:
        """Get energy drink consumption history"""
        if not self._initialized:
            await self.initialize()
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ACTION_TAKEN.value)
                .where(CentralMemoryBank.subject_kind == "caffeine_intake")
                .where(CentralMemoryBank.occurred_at >= cutoff_date)
                .order_by(desc(CentralMemoryBank.occurred_at))
            )
            
            consumptions = result.scalars().all()
            
            if consumptions:
                return {
                    'status': 'success',
                    'total_consumed': len(consumptions),
                    'consumption_history': [
                        {
                            'consumption_time': record.occurred_at.isoformat(),
                            'energy_drink_type': record.string_value,
                            'caffeine_mg': record.numeric_value
                        } for record in consumptions
                    ]
                }
            else:
                return {
                    'status': 'success',
                    'total_consumed': 0,
                    'consumption_history': []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get energy consumption history: {e}")
            raise

    async def get_energy_drink_consumption(self, user_id: str, days: int = 1) -> Dict[str, Any]:
        """Wrapper method for compatibility - calls get_energy_consumption_history"""
        return await self.get_energy_consumption_history(user_id, days)

    async def store_jitter_level(self, user_id: str, jitter_level: float, 
                                caffeine_level_mg: float, timestamp: datetime) -> None:
        """Store a jitter level measurement"""
        await self.update_jitter_levels(user_id, {
            'current_jitter_level': jitter_level,
            'caffeine_level_mg': caffeine_level_mg,
            'jitter_trend': 'stable',
            'timestamp': timestamp.isoformat()
        })

    # === PATTERN LEARNING METHODS ===
    
    async def _check_for_optimization_patterns(self, user_id: str, source_memory_id: str):
        """Check for optimization patterns and store them"""
        try:
            # Analyze patterns using learning helper
            patterns = await analyze_and_learn_patterns(
                self.session,
                user_id,
                self.agent_name,
                min_observations=MIN_OBSERVATIONS_FOR_PATTERN
            )
            
            if patterns and patterns.get('confidence', 0) > 0.7:
                # Store user learning pattern
                pattern_entry = UserLearningPattern(
                    pattern_id=str(uuid.uuid4()),
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    interaction_pattern={
                        "pattern_type": "optimization",
                        "metrics": patterns
                    },
                    learning_preference={"prefers_optimization": True},
                    response_patterns=patterns.get('response_patterns', {}),
                    most_effective_agent=self.agent_name,
                    communication_style_preference={},
                    complexity_tolerance=0.8,
                    skill_improvement_areas=["system_optimization"],
                    knowledge_gaps=[],
                    success_patterns=patterns,
                    agent_effectiveness_ranking={self.agent_name: patterns.get('effectiveness', 0.8)},
                    collaborative_preferences={"shares_with": ["the_stick", "vic20"]}
                )
                
                self.session.add(pattern_entry)
                await self.session.commit()
                
                # Check if pattern should be promoted to global
                if patterns.get('confidence', 0) >= PATTERN_CONFIDENCE_THRESHOLD:
                    await self._promote_to_global_pattern(patterns, source_memory_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to check for optimization patterns: {e}")

    async def _check_for_shell_spin_patterns(self, user_id: str, source_memory_id: str):
        """Check for shell spin patterns"""
        try:
            # Get recent shell spins
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ANOMALY_DETECTED.value)
                .where(CentralMemoryBank.string_value == "shell_spin")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(50)
            )
            
            shell_spins = result.scalars().all()
            
            if len(shell_spins) >= 10:  # Enough data for pattern
                # Analyze shell spin patterns
                pattern_data = {
                    "pattern_type": "shell_spinning",
                    "occurrences": len(shell_spins),
                    "frequency": self._calculate_spin_frequency(shell_spins),
                    "common_causes": self._analyze_spin_causes(shell_spins),
                    "confidence": min(len(shell_spins) / 50, 1.0)
                }
                
                # Store pattern
                pattern_entry = UserLearningPattern(
                    pattern_id=str(uuid.uuid4()),
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    interaction_pattern=pattern_data,
                    learning_preference={"monitors_data_quality": True},
                    response_patterns={"shell_spins_when": pattern_data["common_causes"]},
                    most_effective_agent=self.agent_name,
                    communication_style_preference={},
                    complexity_tolerance=0.5,
                    skill_improvement_areas=["data_quality"],
                    knowledge_gaps=["missing_metrics"],
                    success_patterns={},
                    agent_effectiveness_ranking={},
                    collaborative_preferences={"alerts": ["sir_hawkington", "the_stick"]}
                )
                
                self.session.add(pattern_entry)
                await self.session.commit()
                
                # Share with Hawkington for triage
                await share_learning_with_agent(
                    self.session,
                    source_agent=self.agent_name,
                    target_agent="sir_hawkington",
                    source_memory_id=source_memory_id,
                    learning_type=LEARNING_TYPES["shell_spin_pattern"],
                    learning_content=pattern_data,
                    effectiveness_score=0.9
                )
                
        except Exception as e:
            self.logger.error(f"Failed to check for shell spin patterns: {e}")

    async def _check_for_decision_patterns(self, user_id: str, source_memory_id: str):
        """Check for decision-making patterns"""
        try:
            patterns = await analyze_and_learn_patterns(
                self.session,
                user_id,
                self.agent_name,
                min_observations=20  # Fewer observations needed for decisions
            )
            
            if patterns and patterns.get('confidence', 0) > 0.7:
                # Store decision pattern
                pattern_entry = UserLearningPattern(
                    pattern_id=str(uuid.uuid4()),
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    interaction_pattern={
                        "pattern_type": "decision_making",
                        "patterns": patterns
                    },
                    learning_preference=patterns.get('learning_preference', {}),
                    response_patterns=patterns.get('response_patterns', {}),
                    most_effective_agent=self.agent_name,
                    communication_style_preference={},
                    complexity_tolerance=patterns.get('complexity_tolerance', 0.7),
                    skill_improvement_areas=[],
                    knowledge_gaps=[],
                    success_patterns=patterns,
                    agent_effectiveness_ranking={self.agent_name: patterns.get('effectiveness', 0.8)},
                    collaborative_preferences={}
                )
                
                self.session.add(pattern_entry)
                await self.session.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to check for decision patterns: {e}")

    async def _check_for_jitter_patterns(self, user_id: str, source_memory_id: str):
        """Check for jitter/caffeine patterns"""
        try:
            # Get recent jitter levels
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.STATE_CHANGED.value)
                .where(CentralMemoryBank.subject_kind == "jitter_level")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(100)
            )
            
            jitter_records = result.scalars().all()
            
            if len(jitter_records) >= 20:
                # Analyze jitter patterns
                pattern_data = {
                    "pattern_type": "caffeine_management",
                    "average_jitter": sum(r.numeric_value for r in jitter_records) / len(jitter_records),
                    "peak_jitter": max(r.numeric_value for r in jitter_records),
                    "jitter_trends": self._analyze_jitter_trends(jitter_records),
                    "caffeine_correlation": self._analyze_caffeine_correlation(jitter_records),
                    "confidence": min(len(jitter_records) / 100, 1.0)
                }
                
                # Store jitter pattern
                pattern_entry = UserLearningPattern(
                    pattern_id=str(uuid.uuid4()),
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    interaction_pattern=pattern_data,
                    learning_preference={"caffeine_sensitivity": pattern_data["caffeine_correlation"]},
                    response_patterns={"jitter_response": pattern_data["jitter_trends"]},
                    most_effective_agent=self.agent_name,
                    communication_style_preference={},
                    complexity_tolerance=0.7,
                    skill_improvement_areas=["caffeine_management"],
                    knowledge_gaps=[],
                    success_patterns={},
                    agent_effectiveness_ranking={},
                    collaborative_preferences={"monitors": ["sir_hawkington"]}
                )
                
                self.session.add(pattern_entry)
                await self.session.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to check for jitter patterns: {e}")

    async def _check_for_caffeine_patterns(self, user_id: str, source_memory_id: str):
        """Check for caffeine consumption patterns"""
        try:
            # Get recent energy drink consumption
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.user_id == user_id)
                .where(CentralMemoryBank.event_type == EventTypes.ACTION_TAKEN.value)
                .where(CentralMemoryBank.subject_kind == "caffeine_intake")
                .order_by(desc(CentralMemoryBank.occurred_at))
                .limit(50)
            )
            
            consumptions = result.scalars().all()
            
            if len(consumptions) >= 10:
                pattern_data = {
                    "pattern_type": "caffeine_consumption",
                    "average_caffeine_mg": sum(c.numeric_value for c in consumptions) / len(consumptions),
                    "preferred_type": self._get_most_common_drink(consumptions),
                    "consumption_frequency": self._calculate_consumption_frequency(consumptions),
                    "effectiveness_correlation": await self._correlate_caffeine_with_performance(user_id),
                    "confidence": min(len(consumptions) / 50, 1.0)
                }
                
                # Store pattern
                pattern_entry = UserLearningPattern(
                    pattern_id=str(uuid.uuid4()),
                    user_id=user_id,
                    timestamp=datetime.utcnow(),
                    interaction_pattern=pattern_data,
                    learning_preference={"preferred_caffeine": pattern_data["preferred_type"]},
                    response_patterns={"caffeine_effectiveness": pattern_data["effectiveness_correlation"]},
                    most_effective_agent=self.agent_name,
                    communication_style_preference={},
                    complexity_tolerance=0.8,
                    skill_improvement_areas=[],
                    knowledge_gaps=[],
                    success_patterns=pattern_data,
                    agent_effectiveness_ranking={},
                    collaborative_preferences={}
                )
                
                self.session.add(pattern_entry)
                await self.session.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to check for caffeine patterns: {e}")

    async def _pin_important_memory(self, user_id: str, memory_id: str, decision_data: dict):
        """Pin important memories for permanent retention"""
        try:
            pinned_memory = AgentMemory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                agent_name=self.agent_name,
                memory_type="high_confidence_decision",
                content={
                    "decision_type": decision_data.get('decision_type'),
                    "confidence_level": decision_data.get('confidence_level'),
                    "context": decision_data.get('context'),
                    "source_memory_id": memory_id
                },
                importance=10,
                timestamp=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=0
            )
            
            self.session.add(pinned_memory)
            await self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to pin important memory: {e}")

    async def _pin_shell_spin_memory(self, user_id: str, memory_id: str):
        """Pin shell spin incidents"""
        try:
            pinned_memory = AgentMemory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                agent_name=self.agent_name,
                memory_type="shell_spin_incident",
                content={
                    "incident_type": "shell_spin",
                    "source_memory_id": memory_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                importance=10,
                timestamp=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=0
            )
            
            self.session.add(pinned_memory)
            await self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to pin shell spin memory: {e}")

    async def _pin_jitter_memory(self, user_id: str, memory_id: str, jitter_data: dict):
        """Pin extreme jitter events"""
        try:
            pinned_memory = AgentMemory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                agent_name=self.agent_name,
                memory_type="extreme_jitter_event",
                content={
                    "jitter_level": jitter_data.get('current_jitter_level'),
                    "caffeine_level": jitter_data.get('caffeine_level_mg'),
                    "source_memory_id": memory_id,
                    "requires_intervention": jitter_data.get('requires_stick_intervention', False)
                },
                importance=10,
                timestamp=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=0
            )
            
            self.session.add(pinned_memory)
            await self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to pin jitter memory: {e}")

    async def _promote_to_global_pattern(self, pattern_data: dict, source_memory_id: str):
        """Promote high-confidence patterns to global"""
        try:
            global_pattern = AgentGlobalPattern(
                id=str(uuid.uuid4()),
                pattern_key=f"{self.agent_name}_optimization_{datetime.utcnow().timestamp()}",
                value={
                    "pattern_data": pattern_data,
                    "source_memory_id": source_memory_id,
                    "agent": self.agent_name,
                    "confidence": pattern_data.get('confidence', 0.9)
                },
                updated_at=datetime.utcnow()
            )
            
            self.session.add(global_pattern)
            await self.session.commit()
            
            # Share with other agents
            await share_learning_with_agent(
                self.session,
                source_agent=self.agent_name,
                target_agent="the_stick",
                source_memory_id=source_memory_id,
                learning_type=LEARNING_TYPES["optimization_insight"],
                learning_content=pattern_data,
                effectiveness_score=pattern_data.get('effectiveness', 0.85)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to promote to global pattern: {e}")

    async def _share_shell_spin_pattern(self, user_id: str, memory_id: str, metrics_data: dict):
        """Share shell spin patterns with other agents"""
        try:
            pattern_data = {
                "shell_spin_count": metrics_data.get('shell_spin_count', 0),
                "missing_data": metrics_data.get('missing_metrics', []),
                "invalid_data": metrics_data.get('invalid_metrics', [])
            }
            
            # Share with Hawkington for triage
            await share_learning_with_agent(
                self.session,
                source_agent=self.agent_name,
                target_agent="sir_hawkington",
                source_memory_id=memory_id,
                learning_type=LEARNING_TYPES["shell_spin_pattern"],
                learning_content=pattern_data,
                effectiveness_score=1.0  # Critical for data quality
            )
            
            # Share with Stick for memory
            await share_learning_with_agent(
                self.session,
                source_agent=self.agent_name,
                target_agent="the_stick",
                source_memory_id=memory_id,
                learning_type=LEARNING_TYPES["shell_spin_pattern"],
                learning_content=pattern_data,
                effectiveness_score=1.0
            )
            
        except Exception as e:
            self.logger.error(f"Failed to share shell spin pattern: {e}")

    # === HELPER METHODS ===
    
    async def _analyze_historical_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze historical data for patterns"""
        if not data:
            return {}
            
        return {
            "average_improvement": sum(d.get('cpu_improvement', 0) or 0 for d in data) / len(data),
            "success_rate": sum(1 for d in data if d.get('optimization_success')) / len(data),
            "shell_spin_frequency": sum(d.get('shell_spin_count', 0) for d in data) / len(data)
        }
    
    def _check_jitter_pattern_match(self, jitter_level: float, patterns: List[Dict]) -> Optional[str]:
        """Check if current jitter matches known patterns"""
        for pattern in patterns:
            if abs(pattern.get('average_jitter', 0) - jitter_level) < 0.1:
                return pattern.get('pattern_name', 'matched')
        return None
    
    def _calculate_spin_frequency(self, shell_spins: List) -> float:
        """Calculate shell spin frequency"""
        if len(shell_spins) < 2:
            return 0.0
            
        time_diffs = []
        for i in range(1, len(shell_spins)):
            diff = (shell_spins[i-1].occurred_at - shell_spins[i].occurred_at).total_seconds() / 3600
            time_diffs.append(diff)
            
        return len(shell_spins) / sum(time_diffs) if time_diffs else 0.0
    
    def _analyze_spin_causes(self, shell_spins: List) -> Dict[str, int]:
        """Analyze common causes of shell spins"""
        causes = {}
        for spin in shell_spins:
            cause = spin.details.get('cause', 'unknown')
            causes[cause] = causes.get(cause, 0) + 1
        return causes
    
    def _analyze_jitter_trends(self, jitter_records: List) -> Dict[str, Any]:
        """Analyze jitter level trends"""
        if not jitter_records:
            return {}
            
        levels = [r.numeric_value for r in jitter_records]
        return {
            "average": sum(levels) / len(levels),
            "peak": max(levels),
            "minimum": min(levels),
            "volatility": max(levels) - min(levels)
        }
    
    def _analyze_caffeine_correlation(self, jitter_records: List) -> float:
        """Analyze correlation between caffeine and jitter"""
        # Simplified correlation - in reality would be more complex
        caffeine_levels = [r.details.get('caffeine_level_mg', 0) for r in jitter_records]
        jitter_levels = [r.numeric_value for r in jitter_records]
        
        if not caffeine_levels or not jitter_levels:
            return 0.0
            
        # Simple correlation coefficient (would use numpy/scipy in production)
        avg_caffeine = sum(caffeine_levels) / len(caffeine_levels)
        avg_jitter = sum(jitter_levels) / len(jitter_levels)
        
        numerator = sum((c - avg_caffeine) * (j - avg_jitter) 
                       for c, j in zip(caffeine_levels, jitter_levels))
        denominator_c = sum((c - avg_caffeine) ** 2 for c in caffeine_levels) ** 0.5
        denominator_j = sum((j - avg_jitter) ** 2 for j in jitter_levels) ** 0.5
        
        if denominator_c * denominator_j == 0:
            return 0.0
            
        return numerator / (denominator_c * denominator_j)
    
    def _get_most_common_drink(self, consumptions: List) -> str:
        """Get most commonly consumed energy drink type"""
        drink_counts = {}
        for c in consumptions:
            drink_type = c.string_value
            drink_counts[drink_type] = drink_counts.get(drink_type, 0) + 1
        
        if not drink_counts:
            return "unknown"
            
        return max(drink_counts, key=drink_counts.get)
    
    def _calculate_consumption_frequency(self, consumptions: List) -> float:
        """Calculate energy drink consumption frequency (per day)"""
        if len(consumptions) < 2:
            return 0.0
            
        time_span = (consumptions[0].occurred_at - consumptions[-1].occurred_at).days
        if time_span == 0:
            return len(consumptions)  # All in same day
            
        return len(consumptions) / time_span
    
    async def _correlate_caffeine_with_performance(self, user_id: str) -> float:
        """Correlate caffeine consumption with optimization performance"""
        # This would involve complex analysis of optimization success rates
        # vs caffeine levels - simplified for now
        return 0.75  # Placeholder

    async def cleanup_old_memories(self, days_to_keep: int = 30):
        """Clean up old memories except those marked never_forget"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old memories that aren't marked to never forget
            result = await self.session.execute(
                select(CentralMemoryBank)
                .where(CentralMemoryBank.agent_name == self.agent_name)
                .where(CentralMemoryBank.created_at < cutoff_date)
                .where(CentralMemoryBank.never_forget == False)
                .where(CentralMemoryBank.priority < 8)  # Don't delete high priority
            )
            
            memories_to_delete = result.scalars().all()
            
            for memory in memories_to_delete:
                await self.session.delete(memory)
            
            await self.session.commit()
            
            self.logger.info(f"Cleaned up {len(memories_to_delete)} old memories")
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to cleanup old memories: {e}")