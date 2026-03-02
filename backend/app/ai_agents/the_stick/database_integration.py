"""
The Stick's Database Integration
DUAL-WRITE ARCHITECTURE: Agent-Specific Table + Central Memory Bank
NO FAKE DATA POLICY: Real data or graceful failure
"""

import asyncio
import os
import math
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, func, desc, and_, delete
import json
import uuid
import logging

# Import base class for consistent session management
from app.ai_agents.distributed.base_database_integration import BaseDatabaseIntegration

from app.models.agent_memory_banks import (
    CentralMemoryBank, 
    TheStickMemoryBank,
    UserLearningPatterns, 
    AgentLearningInteractions
)
from app.models.agent_memory import AgentGlobalPattern, AgentMemory
from app.core.learning_helpers import (
    upsert_user_pattern, upsert_global_pattern, 
    record_learning_interaction, LearningInteraction,
    UserLearningPattern, GlobalPattern,
    pin_memory, get_pinned_memories
)
from app.utils.json_safety import to_json_safe
from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage

from .data_types import (
    StickDecision, UserPattern, ComplianceViolation, 
    ConfigurationProfile, AnxietyEvent, HamsterProximityAlert,
    PaperBagInventory, StickMemoryEntry
)
from .constants import (
    AGENT_NAME, StickEventTypes, ALL_HAMSTERS, HAMSTER_BOB,
    ANXIETY_THRESHOLD_PANIC, PRIORITY_THRESHOLD_PIN, PATTERN_CONFIDENCE_PROMOTE
)

logger = logging.getLogger("Stick.Database")

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

class StickDatabaseIntegration(BaseDatabaseIntegration):
    """Database integration for The Stick's anxiety-enhanced eidetic memory - NOW CENTRALIZED"""
    
    def __init__(self, db_getter=None):
        super().__init__(db_getter)
        self.websocket_anxiety_level = 25.0  # Starting nervous
    
    def _get_agent_name(self) -> str:
        """Return agent name for base class"""
        return AGENT_NAME
    
    async def initialize(self):
        """Initialize The Stick's database connection"""
        if not self.db_getter:
            raise ValueError("db_getter is required - The Stick is too anxious to create his own engine!")
        
        # Verify db_getter works by testing a connection
        try:
            async with self.get_managed_session() as session:
                pass  # Just verify we can get a session
        except Exception as e:
            logger.error(f"📏❌ Failed to verify database connection: {e}")
            raise
        
        logger.info("📏✨ Database integration initialized using shared connection pool (anxiety level: manageable)")
    
    async def store_decision(self, user_id: str, decision: Any) -> str:
        """
        Required by BaseDatabaseIntegration - delegates to store_memory_entry.
        The Stick stores everything as eidetic memory entries.
        """
        if isinstance(decision, StickMemoryEntry):
            return await self.store_memory_entry(decision, user_id)
        elif isinstance(decision, ComplianceViolation):
            return await self.store_compliance_violation(user_id, decision)
        elif isinstance(decision, dict):
            # Convert dict to StickMemoryEntry
            from datetime import datetime, timezone
            entry = StickMemoryEntry(
                timestamp=decision.get('timestamp', datetime.now(timezone.utc)),
                event_type=decision.get('event_type', 'decision'),
                details=decision,
                anxiety_level=decision.get('anxiety_level', 25.0),
                importance=decision.get('importance', 'MEDIUM'),
                related_hamsters=decision.get('related_hamsters', []),
                compliance_impact=decision.get('compliance_impact'),
                never_forget=decision.get('never_forget', False)
            )
            return await self.store_memory_entry(entry, user_id)
        else:
            raise ValueError(f"Unknown decision type: {type(decision)}")
    
    # === DUAL-WRITE METHOD 1: STORE COMPLIANCE VIOLATION ===
    
    async def store_compliance_violation(self, user_id: str, violation: ComplianceViolation) -> str:
        """
        Store compliance violation with DUAL-WRITE pattern
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to TheStickMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            violation: ComplianceViolation instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required violation data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not violation.violation_type:
            raise ValueError("📋💥 Missing violation_type - cannot store without real type")
        if violation.measured_value is None:
            raise ValueError("📋💥 Missing measured_value - cannot store without real measurement")
        if violation.threshold_value is None:
            raise ValueError("📋💥 Missing threshold_value - cannot store without real threshold")
        if not violation.timestamp:
            raise ValueError("📋💥 Missing timestamp - cannot store without real timestamp")
        
        async with self.get_managed_session() as session:
            try:
                # Generate IDs
                agent_memory_id = str(uuid.uuid4())
                central_memory_id = str(uuid.uuid4())
                
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Build compliance tracking data
                compliance_tracking = to_json_safe({
                    'violation_type': violation.violation_type,
                    'measured_value': violation.measured_value,
                    'threshold_value': violation.threshold_value,
                    'anxiety_adjusted_threshold': violation.anxiety_adjusted_threshold,
                    'severity': violation.severity,
                    'resolved': violation.resolved,
                    'paper_bags_triggered': violation.paper_bags_triggered
                })
                
                # Build anxiety pattern
                anxiety_pattern = to_json_safe({
                    'anxiety_impact': violation.anxiety_impact,
                    'paper_bags_triggered': violation.paper_bags_triggered,
                    'severity_level': violation.severity
                })
                
                # Build compliance violations log
                compliance_violations = to_json_safe({
                    'violation_type': violation.violation_type,
                    'recommendation': violation.recommendation,
                    'resolved': violation.resolved,
                    'timestamp': violation.timestamp.isoformat() if violation.timestamp else None
                })
                
                # Calculate compliance score (lower is worse)
                compliance_score = 1.0 - (violation.anxiety_impact if violation.anxiety_impact else 0.5)
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = TheStickMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=violation.timestamp,
                    
                    # Stick-specific structured fields
                    anxiety_pattern=anxiety_pattern,
                    compliance_tracking=compliance_tracking,
                    compliance_violations=compliance_violations,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    anxiety_level=violation.anxiety_impact if violation.anxiety_impact else None,
                    compliance_score=compliance_score,
                    
                    # Link to central memory
                    shared_with_central=True,
                    central_memory_id=central_memory_id
                )
                
                session.add(agent_memory)
                await session.flush()  # Ensure agent memory is written first
                
                # === WRITE 2: SUMMARY TO CENTRAL MEMORY BANK ===
                
                priority = 9 if violation.severity in ['CRITICAL', 'MAJOR'] else 7
                
                central_memory = CentralMemoryBank(
                    memory_id=central_memory_id,
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.COMPLIANCE_VIOLATION.value,
                    occurred_at=violation.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="compliance_violation",
                    subject_id=agent_memory_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'violation_type': violation.violation_type,
                        'severity': violation.severity,
                        'recommendation': violation.recommendation,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'anxiety_driven': True,
                        'paper_bag_protocol': 'ACTIVATED' if violation.paper_bags_triggered > 0 else 'STANDBY',
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=violation.measured_value,
                    string_value=violation.violation_type,
                    priority=priority,
                    never_forget=(violation.severity == 'CRITICAL'),
                    stick_anxiety_level=violation.anxiety_impact if violation.anxiety_impact else None,
                    
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
                        decision_type="compliance_violation",
                        description=f"Compliance violation: {violation.violation_type}",
                        reasoning=f"Severity: {violation.severity}, Measured: {violation.measured_value}, Threshold: {violation.threshold_value}",
                        context={
                            'priority': priority,
                            'event_type': StickEventTypes.COMPLIANCE_VIOLATION.value,
                            'affected_agents': []
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="compliance_violation",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=violation.timestamp,
                        user_id=user_id,
                        event_type=StickEventTypes.COMPLIANCE_VIOLATION.value,
                        priority=priority,
                        metadata=to_json_safe({
                            'violation_type': violation.violation_type,
                            'severity': violation.severity,
                            'measured_value': violation.measured_value,
                            'threshold_value': violation.threshold_value,
                            'anxiety_impact': violation.anxiety_impact
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=1.0 - (violation.anxiety_impact if violation.anxiety_impact else 0.5),
                        decision_summary=f"Violation: {violation.violation_type} ({violation.severity})"
                    )
                    logger.debug(f"🔮 Queued vector embedding for violation {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                logger.info(
                    f"📋✨ DUAL-WRITE SUCCESS: Compliance violation {violation.violation_type} stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id})"
                )
                
                # Pin critical violations
                if violation.severity == 'CRITICAL':
                    await self._pin_critical_violation(user_id, violation, central_memory_id)
                
                return central_memory_id
                
            except ValueError as ve:
                # Data validation error - graceful failure with clear message
                await session.rollback()
                logger.error(f"📋💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"📋💥 DUAL-WRITE FAILED: {str(e)}")
                raise Exception(f"📋💥 Failed to store compliance violation: {str(e)}")
    
    async def _pin_critical_violation(self, user_id: str, violation: ComplianceViolation, memory_id: str):
        """Pin critical violations for The Stick's eidetic memory"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"CRITICAL violation: {violation.violation_type}",
                importance=10
            )
            logger.info(f"📌 Pinned critical violation: {violation.violation_type}")
        except Exception as e:
            logger.warning(f"Failed to pin critical violation: {str(e)}")
    
    async def store_anxiety_event(self, event: AnxietyEvent):
        """Store anxiety event in central memory bank - The Stick tracks EVERYTHING"""
        async with self.get_managed_session() as session:
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
    
    # === DUAL-WRITE METHOD 2: STORE HAMSTER ENCOUNTER ===
    
    async def store_hamster_encounter(self, user_id: str, alert: HamsterProximityAlert) -> str:
        """
        Store hamster encounter with DUAL-WRITE pattern - The Stick's worst nightmare
        NO FAKE DATA: All fields are real or None
        
        DUAL-WRITE FLOW:
        1. Write structured data to TheStickMemoryBank
        2. Write summary to CentralMemoryBank with foreign key link
        3. Return the central memory_id for backwards compatibility
        
        Args:
            user_id: User identifier
            alert: HamsterProximityAlert instance with REAL structured data
            
        Returns:
            central_memory_id for backwards compatibility
            
        Raises:
            ValueError: If required alert data is missing
            Exception: If database write fails
        """
        # VALIDATE REQUIRED DATA - NO FAKE FALLBACKS
        if not alert.active_hamsters:
            raise ValueError("📋💥 Missing active_hamsters - cannot store without real hamster data")
        if not alert.timestamp:
            raise ValueError("📋💥 Missing timestamp - cannot store without real timestamp")
        if alert.anxiety_multiplier is None:
            raise ValueError("📋💥 Missing anxiety_multiplier - cannot store without real anxiety data")
        
        async with self.get_managed_session() as session:
            try:
                # Generate IDs
                agent_memory_id = str(uuid.uuid4())
                central_memory_id = str(uuid.uuid4())
                
                # Normalize hamster names for consistency
                normalized_hamsters = normalize_hamster_names(alert.active_hamsters)
                
                # === EXTRACT REAL DATA (NO FALLBACKS) ===
                
                # Build hamster behavior log
                hamster_behavior_log = to_json_safe({
                    'active_hamsters': normalized_hamsters,
                    'locations': alert.locations,
                    'infrastructure_risk': alert.infrastructure_risk,
                    'stick_response': alert.stick_response
                })
                
                # Build anxiety pattern
                anxiety_pattern = to_json_safe({
                    'anxiety_multiplier': alert.anxiety_multiplier,
                    'panic_level': alert.panic_level,
                    'paper_bags_consumed': alert.paper_bags_consumed,
                    'bob_involved': HAMSTER_BOB in normalized_hamsters
                })
                
                # Build paper bag moments
                paper_bag_moments = to_json_safe({
                    'consumed': alert.paper_bags_consumed,
                    'panic_level': alert.panic_level,
                    'timestamp': alert.timestamp.isoformat() if alert.timestamp else None
                })
                
                # Calculate anxiety level (Bob causes MAXIMUM anxiety)
                anxiety_level = 100.0 if HAMSTER_BOB in normalized_hamsters else 80.0
                bob_proximity_alerts = 1 if HAMSTER_BOB in normalized_hamsters else 0
                
                # === WRITE 1: STRUCTURED DATA TO AGENT TABLE ===
                
                agent_memory = TheStickMemoryBank(
                    memory_id=agent_memory_id,
                    user_id=user_id,
                    timestamp=alert.timestamp,
                    
                    # Stick-specific structured fields
                    anxiety_pattern=anxiety_pattern,
                    hamster_behavior_log=hamster_behavior_log,
                    paper_bag_moments=paper_bag_moments,
                    
                    # STRUCTURED NUMERIC FIELDS - REAL or None
                    anxiety_level=anxiety_level,
                    hyperventilation_count=alert.paper_bags_consumed if alert.paper_bags_consumed else 0,
                    bob_proximity_alerts=bob_proximity_alerts,
                    
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
                    event_type=StickEventTypes.HAMSTER_PROXIMITY_ALERT.value,
                    occurred_at=alert.timestamp,
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    subject_kind="hamster_encounter",
                    subject_id=agent_memory_id,
                    
                    # Summary details (not duplicating structured data)
                    details=to_json_safe({
                        'active_hamsters': normalized_hamsters,
                        'panic_level': alert.panic_level,
                        'infrastructure_risk': alert.infrastructure_risk,
                        'agent_memory_ref': agent_memory_id
                    }),
                    
                    metadata_=to_json_safe({
                        'bob_detected': HAMSTER_BOB in normalized_hamsters,
                        'emergency_protocol': 'ACTIVATED' if alert.panic_level == 'MAXIMUM' else 'STANDBY',
                        'has_structured_data': True,
                        'agent_memory_id': agent_memory_id
                    }),
                    
                    # Key metrics for CMB indexing - REAL values
                    numeric_value=alert.anxiety_multiplier,
                    string_value=alert.panic_level,
                    relevant_agents=','.join(normalized_hamsters),
                    priority=10,  # MAXIMUM PRIORITY
                    never_forget=True,  # The Stick NEVER forgets hamster encounters
                    stick_anxiety_level=anxiety_level,
                    
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
                        decision_type="hamster_encounter",
                        description=f"HAMSTER ENCOUNTER: {', '.join(normalized_hamsters)}",
                        reasoning=f"Panic level: {alert.panic_level}, Anxiety multiplier: {alert.anxiety_multiplier}, Paper bags consumed: {alert.paper_bags_consumed}",
                        context={
                            'priority': 10,
                            'event_type': StickEventTypes.HAMSTER_PROXIMITY_ALERT.value,
                            'affected_agents': normalized_hamsters
                        }
                    )
                    
                    embedding_service = get_embedding_service()
                    embedding = await embedding_service.generate_embedding_async(decision_text)
                    
                    vector_storage = get_vector_storage()
                    vector_storage.store_decision_vector_fire_and_forget(
                        agent_name=AGENT_NAME,
                        decision_type="hamster_encounter",
                        decision_text=decision_text,
                        embedding=embedding,
                        occurred_at=alert.timestamp,
                        user_id=user_id,
                        event_type=StickEventTypes.HAMSTER_PROXIMITY_ALERT.value,
                        priority=10,
                        metadata=to_json_safe({
                            'active_hamsters': normalized_hamsters,
                            'panic_level': alert.panic_level,
                            'anxiety_multiplier': alert.anxiety_multiplier,
                            'paper_bags_consumed': alert.paper_bags_consumed,
                            'bob_detected': HAMSTER_BOB in normalized_hamsters
                        }),
                        sql_memory_id=central_memory_id,
                        confidence_score=0.0,  # The Stick has NO confidence when hamsters are involved
                        decision_summary=f"HAMSTER ENCOUNTER: {', '.join(normalized_hamsters)}"
                    )
                    logger.debug(f"🔮 Queued vector embedding for hamster encounter {central_memory_id}")
                except Exception as ve:
                    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
                
                logger.info(
                    f"📋✨ DUAL-WRITE SUCCESS: Hamster encounter with {normalized_hamsters} stored in agent table "
                    f"({agent_memory_id}) and CMB ({central_memory_id})"
                )
                
                # Pin this critical memory - hamsters are NEVER forgotten
                await self._pin_hamster_encounter(user_id, alert, central_memory_id, normalized_hamsters)
                
                return central_memory_id
                
            except ValueError as ve:
                # Data validation error - graceful failure with clear message
                await session.rollback()
                logger.error(f"📋💥 DATA VALIDATION FAILED: {str(ve)}")
                raise
                
            except Exception as e:
                await session.rollback()
                logger.error(f"📋💥 DUAL-WRITE FAILED: {str(e)}")
                raise Exception(f"📋💥 The Stick hyperventilated while storing hamster encounter: {str(e)}")
    
    async def _pin_hamster_encounter(self, user_id: str, alert: HamsterProximityAlert, memory_id: str, hamsters: List[str]):
        """Pin hamster encounters for The Stick's eidetic memory - NEVER FORGET"""
        try:
            await pin_memory(
                user_id=user_id,
                agent_name=AGENT_NAME,
                memory_id=memory_id,
                reason=f"HAMSTER ENCOUNTER: {', '.join(hamsters)}",
                importance=10
            )
            logger.info(f"📌 Pinned hamster encounter: {', '.join(hamsters)}")
        except Exception as e:
            logger.warning(f"Failed to pin hamster encounter: {str(e)}")
    
    async def update_paper_bag_inventory(self, inventory_change: int, reason: str):
        """Update paper bag inventory in central memory bank - Critical for anxiety management"""
        async with self.get_managed_session() as session:
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
    
    async def store_memory_entry(self, entry: StickMemoryEntry, user_id: str = None, session=None):
        """
        Store in The Stick's eidetic memory with DUAL-WRITE pattern.
        
        WRITE 1: CentralMemoryBank (summary for cross-agent visibility)
        WRITE 2: TheStickMemoryBank (structured agent-specific data)
        WRITE 3: Vector embedding (fire-and-forget, non-blocking)
        
        The Stick NEVER FORGETS - eidetic memory is sacred!
        """
        now = utc_now()
        memory_id = str(uuid.uuid4())
        agent_memory_id = str(uuid.uuid4())
        
        # Calculate priority from importance
        priority = {
            'CRITICAL': 10,
            'HIGH': 8,
            'MEDIUM': 6,
            'LOW': 4
        }.get(entry.importance, 5)
        
        # Convert anxiety level string to float if needed
        anxiety_float = None
        if entry.anxiety_level:
            if isinstance(entry.anxiety_level, (int, float)):
                anxiety_float = float(entry.anxiety_level)
            else:
                anxiety_map = {
                    'CALM': 10.0, 'BASELINE': 20.0, 'NERVOUS': 30.0,
                    'ANXIOUS': 50.0, 'PANICKING': 70.0, 'FULL_PANIC': 90.0
                }
                anxiety_float = anxiety_map.get(str(entry.anxiety_level).upper(), 25.0)
        
        # === WRITE 1: CENTRAL MEMORY BANK (summary) ===
        memory_entry = CentralMemoryBank(
            memory_id=memory_id,
            agent_name=AGENT_NAME,
            user_id=user_id,
            event_type=StickEventTypes.EIDETIC_MEMORY_ENTRY,
            occurred_at=entry.timestamp,
            created_at=now,
            updated_at=now,
            subject_kind="eidetic_memory",
            subject_id=agent_memory_id,
            details=to_json_safe({
                'event_type_original': entry.event_type,
                'importance': entry.importance,
                'related_hamsters': normalize_hamster_names(entry.related_hamsters),
                'compliance_impact': entry.compliance_impact,
                'agent_memory_ref': agent_memory_id
            }),
            stick_anxiety_level=anxiety_float,
            string_value=entry.importance,
            relevant_agents=','.join(normalize_hamster_names(entry.related_hamsters)) if entry.related_hamsters else None,
            never_forget=entry.never_forget,
            priority=priority,
            agent_metadata=to_json_safe({
                'eidetic_memory': True,
                'compliance_related': entry.compliance_impact is not None,
                'hamster_anxiety': len(entry.related_hamsters) > 0 if entry.related_hamsters else False,
                'has_structured_data': True,
                'agent_memory_id': agent_memory_id
            })
        )
        
        # === WRITE 2: THE STICK MEMORY BANK (structured data) ===
        agent_memory = TheStickMemoryBank(
            memory_id=agent_memory_id,
            user_id=user_id,
            timestamp=entry.timestamp,
            
            # Stick-specific structured fields
            anxiety_pattern=to_json_safe({
                'level': entry.anxiety_level,
                'triggers': entry.related_hamsters if entry.related_hamsters else [],
                'event_type': entry.event_type
            }),
            compliance_tracking=to_json_safe({
                'impact': entry.compliance_impact,
                'importance': entry.importance
            }),
            pattern_recognition=to_json_safe(entry.details) if entry.details else None,
            hamster_behavior_log=to_json_safe({
                'related_hamsters': normalize_hamster_names(entry.related_hamsters)
            }) if entry.related_hamsters else None,
            
            # Numeric metrics
            anxiety_level=anxiety_float,
            bob_proximity_alerts=1 if entry.related_hamsters and 'bob' in [h.lower() for h in entry.related_hamsters] else 0,
            
            # Cross-agent coordination
            shared_with_central=True,
            central_memory_id=memory_id
        )
        
        if session:
            # Use existing session, don't commit (caller manages transaction)
            session.add(memory_entry)
            await session.flush()  # Flush CMB first
            session.add(agent_memory)
            logger.info(f"📏✅ Dual-write prepared (memory_id={memory_id}, agent_memory_id={agent_memory_id})")
            return memory_id
        else:
            # Create new session and commit using db_getter
            async with self.get_managed_session() as new_session:
                try:
                    # Add CMB first and flush
                    new_session.add(memory_entry)
                    await new_session.flush()
                    
                    # Add agent memory
                    new_session.add(agent_memory)
                    await new_session.commit()
                    
                    logger.info(f"📏✅ Dual-write complete: CMB={memory_id}, StickMemory={agent_memory_id}")
                    
                    # === WRITE 3: VECTOR EMBEDDING (fire-and-forget) ===
                    try:
                        decision_text = create_decision_text(
                            agent_name=AGENT_NAME,
                            decision_type=entry.event_type or "eidetic_memory",
                            description=f"Eidetic memory: {entry.importance}",
                            reasoning=entry.compliance_impact or "Memory logged",
                            context={
                                'priority': priority,
                                'event_type': StickEventTypes.EIDETIC_MEMORY_ENTRY,
                                'related_hamsters': entry.related_hamsters or []
                            }
                        )
                        
                        embedding_service = get_embedding_service()
                        embedding = await embedding_service.generate_embedding_async(decision_text)
                        
                        vector_storage = get_vector_storage()
                        # Fire-and-forget: create task but don't await
                        import asyncio
                        asyncio.create_task(vector_storage.store_decision_vector_fire_and_forget(
                            agent_name=AGENT_NAME,
                            decision_type=entry.event_type or "eidetic_memory",
                            decision_text=decision_text,
                            embedding=embedding,
                            occurred_at=entry.timestamp,
                            user_id=user_id,
                            event_type=StickEventTypes.EIDETIC_MEMORY_ENTRY,
                            priority=priority,
                            metadata=to_json_safe({
                                'importance': entry.importance,
                                'related_hamsters': entry.related_hamsters,
                                'never_forget': entry.never_forget
                            }),
                            sql_memory_id=memory_id,
                            confidence_score=1.0 if entry.never_forget else 0.8,
                            decision_summary=f"Eidetic: {entry.event_type}"
                        ))
                        logger.debug(f"📏🔮 Vector embedding queued for {memory_id}")
                    except Exception as ve:
                        # Vector write failure doesn't break the decision flow
                        logger.warning(f"📏⚠️ Vector embedding failed (non-critical): {ve}")
                    
                    return memory_id
                except Exception as e:
                    await new_session.rollback()
                    logger.error(f"📏💥 Database write failed: {e}", exc_info=True)
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
        
        async with self.get_managed_session() as session:
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
    
    async def record_validation(
        self,
        interaction,
        audit_entry,
        session=None  # OPUS 4.6 CHANGE: Accept optional session to avoid nested sessions
    ) -> str:
        """
        Record The Stick's validation of a cross-agent learning interaction.
        
        Updates AgentLearningInteractions table AND writes audit trail to CentralMemoryBank.
        
        Args:
            interaction: The interaction being validated
            audit_entry: Validation audit entry with decision and reasoning
            session: Optional existing session. If None, creates new managed session.
                     OPUS 4.6 NOTE: When called from _handle_decision_log, pass the
                     existing session to avoid nested session creation and potential
                     deadlock on connection-pooled backends.
            
        Returns:
            Central memory ID for the audit entry
        """
        
        async def _do_record(active_session):
            """Inner function so we can use either passed or new session"""
            
            # Update the interaction record
            interaction.validated_by_stick = audit_entry.validation_result
            interaction.cross_validation_count += 1
            
            # If validation failed, mark for potential retry
            if not audit_entry.validation_result:
                # OPUS 4.6 CHANGE: Safe handling of adaptation_method field.
                # Previously: Assumed adaptation_method was always None or dict.
                # Problem: If column is string type, or contains existing non-dict
                # data, the dict assignment would cause type errors or silent
                # data corruption. Now we check the actual type and handle safely.
                retry_metadata = {
                    'validation_failed': True,
                    'failure_reason': audit_entry.reasoning,
                    'can_retry': True,
                    'retry_after': (
                        datetime.now(timezone.utc) + timedelta(hours=24)
                    ).isoformat()
                }
                
                if isinstance(interaction.adaptation_method, dict):
                    # Existing dict — merge without losing previous data
                    interaction.adaptation_method.update(retry_metadata)
                else:
                    # None, empty string, or unexpected type — replace safely
                    interaction.adaptation_method = retry_metadata
            
            active_session.add(interaction)
            
            # Write audit trail to CentralMemoryBank
            memory_id = str(uuid.uuid4())
            audit_memory = CentralMemoryBank(
                memory_id=memory_id,
                agent_name=AGENT_NAME,
                user_id=interaction.user_id,
                created_at=audit_entry.timestamp,
                updated_at=audit_entry.timestamp,
                occurred_at=audit_entry.timestamp,
                event_type=StickEventTypes.VALIDATION_AUDIT,
                subject_kind='cross_agent_learning_validation',
                subject_id=audit_entry.interaction_id,
                priority=8 if audit_entry.validation_result else 9,
                title=f"Validation: {audit_entry.source_agent}→{audit_entry.target_agent}",
                description=audit_entry.reasoning,
                details={
                    'interaction_id': audit_entry.interaction_id,
                    'source_agent': audit_entry.source_agent,
                    'target_agent': audit_entry.target_agent,
                    'learning_type': audit_entry.learning_type,
                    'validation_result': audit_entry.validation_result,
                    'reasoning': audit_entry.reasoning,
                    'thresholds_applied': audit_entry.thresholds_applied,
                    'threshold_state': audit_entry.threshold_state,
                    'was_retry': audit_entry.was_retry,
                    'retry_count': audit_entry.retry_count,
                    'effectiveness_score': audit_entry.effectiveness_score,
                    'success_rate': audit_entry.success_rate,
                    'interaction_age_hours': audit_entry.interaction_age_hours,
                    'stick_anxiety_level': audit_entry.stick_anxiety_level
                },
                metadata_={
                    'validator': 'the_stick',
                    'validation_timestamp': audit_entry.timestamp.isoformat(),
                    'for_vic20_audit': True
                },
                relevant_agents=(
                    f"the_stick,{audit_entry.source_agent},"
                    f"{audit_entry.target_agent},vic_20_sage"
                ),
                stick_anxiety_level=audit_entry.stick_anxiety_level
            )
            
            active_session.add(audit_memory)
            
            # OPUS 4.6 CHANGE: Only commit if we own the session.
            # If session was passed in, caller is responsible for commit.
            if session is None:
                await active_session.commit()
            
            logger.info(
                f"📏💾 Validation recorded: {audit_entry.interaction_id} "
                f"({'PASSED' if audit_entry.validation_result else 'FAILED'})"
            )
            
            return memory_id
        
        try:
            if session is not None:
                # OPUS 4.6 CHANGE: Use passed session — caller manages lifecycle
                return await _do_record(session)
            else:
                # No session passed — create our own
                async with self.get_managed_session() as new_session:
                    result = await _do_record(new_session)
                    return result
                    
        except Exception as e:
            logger.error(f"📏💥 Error recording validation: {e}")
            if session is None:
                # Only rollback if we own the session
                # If caller owns it, let them handle rollback
                pass
            raise
    
    async def _get_daily_consumption(self) -> int:
        """Get today's paper bag consumption from central memory bank"""
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
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

    async def store_user_pattern(self, user_id: str, pattern: UserPattern):
        """Store learned user pattern in central memory bank - The Stick NEVER forgets patterns!"""
        async with self.get_managed_session() as session:
            try:
                current_time = utc_now()
            
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.USER_PATTERN_LEARNED,
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
            
                logger.info(f"The Stick learned new pattern for user {user_id}: {pattern.pattern_type}")
            
                return memory_entry.memory_id
            
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick panicked while storing user pattern: {str(e)}")

    async def store_user_pattern_v2(self, user_id: str, pattern: UserPattern):
        """Store learned user pattern using the dedicated user patterns table"""
        try:
            # First store in CMB as usual
            memory_id = await self.store_user_pattern(user_id, pattern)
            
            # Convert to learning helper format
            learning_pattern = UserLearningPattern(
                user_id=user_id,
                interaction_pattern={
                    'pattern_type': pattern.pattern_type,
                    'time_based': pattern.time_based_patterns,
                    'activity_based': pattern.activity_patterns,
                    'compliance_history': pattern.compliance_history
                },
                learning_preference={
                    'anxiety_correlation': pattern.anxiety_correlation,
                    'stick_observations': pattern.stick_memory_notes,
                    'monitoring_intensity': 'HYPERVIGILANT'
                },
                response_patterns={
                    'panic_triggers': [k for k, v in pattern.anxiety_correlation.items() if v > 0.7],
                    'paper_bag_consumption_patterns': pattern.time_based_patterns
                },
                most_effective_agent=AGENT_NAME,  # The Stick is always effective through anxiety!
                communication_style_preference={
                    'style': 'anxious_detailed',
                    'verbosity': 'obsessive',
                    'documentation_level': 'everything'
                },
                complexity_tolerance=pattern.confidence_score,
                skill_improvement_areas=['compliance', 'pattern_detection', 'anxiety_management'],
                knowledge_gaps=[],  # The Stick knows everything through anxiety
                success_patterns=pattern.activity_patterns,
                agent_effectiveness_ranking={
                    AGENT_NAME: 1.0,  # The Stick is #1 at anxiety-driven detection
                    'meth_snail': 0.8,
                    'sir_hawkington': 0.7,
                    'qsp': 0.6,
                    'vic20': 0.9  # VIC-20 is almost as good
                },
                collaborative_preferences={
                    'prefers_solo': False,  # Anxiety is better shared
                    'best_partners': ['vic20', 'meth_snail'],
                    'avoid_during_panic': ['bob', 'carl', 'steve']
                }
            )
            
            # Store in user patterns table
            await upsert_user_pattern(self.engine, learning_pattern, agent_name=AGENT_NAME)
            
            # Check if pattern should be promoted globally
            if pattern.confidence_score >= PATTERN_CONFIDENCE_PROMOTE:
                await self._promote_pattern_globally(pattern, memory_id)
            
            logger.info(f"The Stick stored user pattern with confidence {pattern.confidence_score}")
            return memory_id
            
        except Exception as e:
            raise Exception(f"The Stick panicked while storing user pattern v2: {str(e)}")

    async def _promote_pattern_globally(self, pattern: UserPattern, source_memory_id: str):
        """Promote high-confidence patterns to global patterns - The Stick's wisdom for all!"""
        try:
            global_pattern = GlobalPattern(
                pattern_key=f"stick_{pattern.pattern_type}_{pattern.user_id[:8]}",
                value={
                    'pattern_type': pattern.pattern_type,
                    'pattern_data': {
                        'time_patterns': pattern.time_based_patterns,
                        'activity_patterns': pattern.activity_patterns,
                        'anxiety_triggers': pattern.anxiety_correlation
                    },
                    'confidence': pattern.confidence_score,
                    'learned_by': AGENT_NAME,
                    'anxiety_validated': True,  # The Stick's anxiety validates everything
                    'promoted_at': utc_now().isoformat(),
                    'source_memory_id': source_memory_id,
                    'stick_notes': [
                        f"Pattern validated through {pattern.learning_sessions} anxiety-filled sessions",
                        f"Confidence: {pattern.confidence_score:.1%}",
                        "The Stick's hypervigilance confirms this pattern"
                    ]
                }
            )
            
            await upsert_global_pattern(self.engine, global_pattern)
            
            # Log promotion in CMB
            promotion_memory = CentralMemoryBank(
                memory_id=str(uuid.uuid4()),
                agent_name=AGENT_NAME,
                event_type=StickEventTypes.GLOBAL_PATTERN_PROMOTED,
                occurred_at=utc_now(),
                created_at=utc_now(),
                updated_at=utc_now(),
                details={
                    'pattern_key': global_pattern.pattern_key,
                    'pattern_type': pattern.pattern_type,
                    'confidence': pattern.confidence_score,
                    'promotion_reason': 'High confidence through anxious observation'
                },
                stick_anxiety_level=self.websocket_anxiety_level,
                numeric_value=pattern.confidence_score,
                string_value=global_pattern.pattern_key,
                never_forget=True,  # Global patterns are never forgotten
                priority=9,
                agent_metadata={
                    'global_wisdom': True,
                    'anxiety_validated': True,
                    'stick_approved': True
                }
            )
            
            async with self.get_managed_session() as session:
                session.add(promotion_memory)
                await session.commit()
                
            logger.info(f"The Stick promoted pattern {global_pattern.pattern_key} to global wisdom!")
            
        except Exception as e:
            raise Exception(f"The Stick failed to promote pattern globally: {str(e)}")

    async def share_anxiety_insight(self, target_agent: str, insight_data: Dict[str, Any], source_memory_id: str):
        """Share The Stick's anxiety-driven insights with other agents"""
        try:
            learning = LearningInteraction(
                source_agent=AGENT_NAME,
                target_agent=target_agent,
                source_memory_id=source_memory_id,
                learning_type='anxiety_insight',
                adaptation_method={
                    'method': 'hypervigilance_transfer',
                    'anxiety_level': self.websocket_anxiety_level,
                    'observation_detail': 'obsessive'
                },
                application_context={
                    'insight_type': insight_data.get('type', 'general'),
                    'anxiety_triggers': insight_data.get('triggers', []),
                    'compliance_concerns': insight_data.get('compliance', {}),
                    'hamster_warnings': insight_data.get('hamster_activity', {})
                },
                effectiveness_score=0.9 if self.websocket_anxiety_level > 60 else 0.7  # Higher anxiety = better insights
            )
            
            await record_learning_interaction(self.engine, learning)
            
            # Log the sharing in CMB
            share_memory = CentralMemoryBank(
                memory_id=str(uuid.uuid4()),
                agent_name=AGENT_NAME,
                event_type=StickEventTypes.CROSS_AGENT_INSIGHT,
                occurred_at=utc_now(),
                created_at=utc_now(),
                updated_at=utc_now(),
                details={
                    'target_agent': target_agent,
                    'insight_shared': insight_data,
                    'anxiety_context': self.websocket_anxiety_level,
                    'effectiveness': learning.effectiveness_score
                },
                stick_anxiety_level=self.websocket_anxiety_level,
                string_value=f"{AGENT_NAME}_to_{target_agent}",
                relevant_agents=target_agent,
                priority=7,
                agent_metadata={
                    'knowledge_transfer': True,
                    'anxiety_enhanced': True
                }
            )
            
            async with self.get_managed_session() as session:
                session.add(share_memory)
                await session.commit()
                
            logger.info(f"The Stick shared anxiety insight with {target_agent}")
            
        except Exception as e:
            raise Exception(f"The Stick failed to share insight (anxiety spike!): {str(e)}")

    async def pin_critical_memory(self, user_id: str, memory_data: Dict[str, Any], source_memory_id: str):
        """Pin critical memories that must NEVER be forgotten"""
        async with self.get_managed_session() as session:
            try:
                # Determine memory type and importance
                memory_type = 'anxiety_pattern'
                importance = 10 if 'hamster' in str(memory_data).lower() else 8
                
                pinned_memory = AgentMemory(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    agent_name=AGENT_NAME,
                    memory_type=memory_type,
                    content={
                        'original_data': memory_data,
                        'source_memory_id': source_memory_id,
                        'pinned_reason': memory_data.get('reason', 'Critical importance detected'),
                        'anxiety_level_at_pin': self.websocket_anxiety_level,
                        'stick_notes': [
                            'This memory is CRITICAL',
                            'The Stick will NEVER forget this',
                            f'Pinned during anxiety level: {self.websocket_anxiety_level:.1f}%'
                        ]
                    },
                    importance=importance,
                    timestamp=utc_now(),
                    last_accessed=utc_now(),
                    access_count=1
                )
                
                session.add(pinned_memory)
                
                # Also log the pinning in CMB
                pin_log = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    agent_name=AGENT_NAME,
                    user_id=user_id,
                    event_type=StickEventTypes.CRITICAL_MEMORY_PINNED,
                    occurred_at=utc_now(),
                    created_at=utc_now(),
                    updated_at=utc_now(),
                    details={
                        'pinned_memory_id': pinned_memory.id,
                        'source_memory_id': source_memory_id,
                        'importance': importance,
                        'reason': memory_data.get('reason', 'Critical importance')
                    },
                    stick_anxiety_level=self.websocket_anxiety_level,
                    numeric_value=float(importance),
                    string_value=memory_type,
                    never_forget=True,
                    priority=10,  # Pinning is maximum priority
                    agent_metadata={
                        'pinned': True,
                        'critical': True
                    }
                )
                
                session.add(pin_log)
                await session.commit()
                
                logger.info(f"The Stick pinned critical memory: {pinned_memory.id}")
                return pinned_memory.id
                
            except Exception as e:
                await session.rollback()
                raise Exception(f"The Stick PANICKED while pinning critical memory: {str(e)}")

    async def contribute_to_metadata_rollup(self) -> Dict[str, int]:
        """Contribute The Stick's metrics to the metadata rollup"""
        async with self.get_managed_session() as session:
            try:
                # Get counts for the last hour
                hour_ago = utc_now() - timedelta(hours=1)
                
                # Count different event types
                event_counts = await session.execute(
                    select(
                        CentralMemoryBank.event_type,
                        func.count(CentralMemoryBank.memory_id)
                    ).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.created_at >= hour_ago
                        )
                    ).group_by(CentralMemoryBank.event_type)
                )
                
                counts = {}
                for event_type, count in event_counts:
                    counts[f"stick_{event_type}"] = count
                
                # Add special anxiety metrics
                anxiety_events = await session.execute(
                    select(func.count(CentralMemoryBank.memory_id)).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.stick_anxiety_level > ANXIETY_THRESHOLD_PANIC,
                            CentralMemoryBank.created_at >= hour_ago
                        )
                    )
                )
                
                counts['stick_panic_events'] = anxiety_events.scalar() or 0
                counts['stick_memories'] = sum(counts.values())
                
                return counts
                
            except Exception as e:
                logger.error(f"The Stick failed metadata rollup: {e}")
                return {'stick_memories': 0, 'stick_errors': 1}

    async def get_user_patterns(self, user_id: str, min_confidence: float = 0.7) -> List[UserPattern]:
        """Retrieve learned user patterns from central memory bank"""
        async with self.get_managed_session() as session:
            try:
                query = select(CentralMemoryBank).where(
                    and_(
                        CentralMemoryBank.agent_name == AGENT_NAME,
                        CentralMemoryBank.user_id == user_id,
                        CentralMemoryBank.event_type == StickEventTypes.USER_PATTERN_LEARNED,
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
        async with self.get_managed_session() as session:
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
            
                # Store the learned pattern using v2 method (includes user patterns table)
                await self.store_user_pattern_v2(user_id, new_pattern)
            
                return new_pattern
            
            except Exception as e:
                raise Exception(f"The Stick's pattern learning failed (ANXIETY SPIKE!): {str(e)}")

    async def check_pattern_match(self, user_id: str, current_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if current behavior matches learned patterns - for proactive optimization"""
        try:
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
    
    async def get_anxiety_analytics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get anxiety analytics for The Stick from central memory bank"""
        
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
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
        
        async with self.get_managed_session() as session:
            try:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
                
                # Only clean up low-importance, non-critical memories
                await session.execute(
                    delete(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.occurred_at < cutoff_date,
                            CentralMemoryBank.priority < 5,  # Only low priority
                            CentralMemoryBank.never_forget.is_(False),  # Proper boolean check
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

    async def check_for_hamster_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Quick check for any hamster-related memories - The Stick's primary concern!"""
        async with self.get_managed_session() as session:
            try:
                # Look for hamster memories in both CMB and pinned memories
                cmb_hamsters = await session.execute(
                    select(CentralMemoryBank).where(
                        and_(
                            CentralMemoryBank.agent_name == AGENT_NAME,
                            CentralMemoryBank.user_id == user_id,
                            or_(
                                CentralMemoryBank.relevant_agents.ilike('%bob%'),
                                CentralMemoryBank.relevant_agents.ilike('%steve%'),
                                CentralMemoryBank.relevant_agents.ilike('%carl%')
                            )
                        )
                    ).order_by(desc(CentralMemoryBank.occurred_at)).limit(10)
                )
                
                hamster_memories = []
                for memory in cmb_hamsters.scalars().all():
                    hamster_memories.append({
                        'memory_id': memory.memory_id,
                        'timestamp': memory.occurred_at.isoformat(),
                        'hamsters': memory.relevant_agents,
                        'anxiety_level': memory.stick_anxiety_level,
                        'event_type': memory.event_type,
                        'details': memory.details
                    })
                
                return hamster_memories
                
            except Exception as e:
                raise Exception(f"The Stick failed to check hamster memories: {str(e)}")