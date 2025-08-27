"""
Meth Snail Database Integration - Now with Central Memory Bank!

Handles all database operations with zero tolerance for fake data.
Redirects all storage to central_memory_bank while maintaining the same interface.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import json
import uuid

from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models.agent_memory_banks import CentralMemoryBank
from app.schemas.agent_memory import MemoryType, MemoryPriority
from .data_types import OptimizationDecision, JitterLevel

logger = logging.getLogger("MethSnail.Database")

class MethSnailDatabaseIntegration:
    """
    Database integration for Meth Snail's optimization engine.
    
    Now stores everything in central_memory_bank for cross-agent learning!
    """
    
    def __init__(self, db_getter=None):
        """Initialize with an optional database getter function"""
        self.db_getter = db_getter
        self.engine = None
        self.session_factory = None
        self._initialized = False
        self.logger = logging.getLogger("MethSnail.Database.Integration")
        self.agent_name = "meth_snail"  # For central memory bank

    async def initialize(self):
        """Initialize database connection with optimization precision"""
        if self._initialized:
            return
            
        if self.db_getter:
            # Use the provided database getter
            # Get the async generator
            db_gen = self.db_getter()
            # Get the first (and only) session from the generator
            session = await anext(db_gen)
            
            # Get the bind URL from the session
            db_url = str(session.get_bind().url)
            await session.close()  # Close the session as we only needed the URL
            
            self.engine = create_async_engine(
                db_url,
                future=True
            )
        else:
            # Fallback to direct engine creation (for testing/backward compatibility)
            from app.core.database import DATABASE_URL
            self.engine = create_async_engine(DATABASE_URL)
        
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self._initialized = True
        self.logger.info("Database integration initialized with Central Memory Bank")

    async def store_optimization_metrics(self, user_id: int, metrics_data: dict) -> int:
        """Store optimization metrics in central memory bank."""
        if not self._initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                # For SQLite compatibility, ensure JSON fields are properly formatted
                import json
                # Calculate improvement metrics if available
                cpu_improvement = None
                memory_improvement = None
            
                # Calculate improvements BEFORE using them
                if metrics_data.get('cpu_usage_before') is not None and metrics_data.get('cpu_usage_after') is not None:
                    cpu_improvement = metrics_data['cpu_usage_before'] - metrics_data['cpu_usage_after']
                if metrics_data.get('memory_usage_before') is not None and metrics_data.get('memory_usage_after') is not None:
                    memory_improvement = metrics_data['memory_usage_before'] - metrics_data['memory_usage_after']
            
       
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
                    "foil_hat_equipped": True  # Always true for the bromance 🎩
                }
            
                # Create central memory bank entry
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=datetime.utcnow(),
                    agent_name=self.agent_name,
                    user_id=str(user_id),
                    event_type="optimization_metrics",
                    subject_kind="system_performance",
                    subject_id=str(user_id),
                    priority=5,
                    title="Meth Snail Optimization Metrics",
                    description=f"Optimization metrics - Success: {metrics_data.get('optimization_success', False)}",
                    details=details_dict,  # Pass as dict, let PG_JSONB handle conversion
                    metadata_=metadata_dict,  # Note: using metadata_ not metadata
                    numeric_value=float(memory_improvement or cpu_improvement or 0.0),
                    string_value="optimization_complete" if metrics_data.get('optimization_success') else "optimization_failed",
                    tags=["optimization", "performance", "meth_snail"],  # Pass as list
                    agent_metadata={"shell_spin_count": metrics_data.get('shell_spin_count', 0)},
                    relevant_agents="meth_snail,the_stick",
                    cross_agent_validated=False,
                    validation_count=0,
                    stick_anxiety_level=0.0,
                    never_forget=metrics_data.get('shell_spin_count', 0) > 5,
                    times_referenced=0,
                    successful_applications=1 if metrics_data.get('optimization_success') else 0
                ) 
                session.add(memory_entry)
            
                await session.commit()
                return memory_entry.id
            
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to store optimization metrics: {e}")
                raise

    async def get_historical_performance(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get historical performance data from central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(CentralMemoryBank)
                    .where(CentralMemoryBank.agent_name == self.agent_name)
                    .where(CentralMemoryBank.user_id == str(user_id))
                    .where(CentralMemoryBank.event_type == "optimization_metrics")
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
                
                return {
                    'status': 'success',
                    'data': [
                        {
                            'timestamp': record.occurred_at,
                            'cpu_improvement': record.details.get('cpu_usage_before', 0) - record.details.get('cpu_usage_after', 0) 
                                if record.details.get('cpu_usage_before') and record.details.get('cpu_usage_after') else None,
                            'memory_improvement': record.details.get('memory_usage_before', 0) - record.details.get('memory_usage_after', 0) 
                                if record.details.get('memory_usage_before') and record.details.get('memory_usage_after') else None,
                            'optimization_success': record.details.get('optimization_success', False),
                            'energy_drink_level': record.details.get('energy_drink_level', 0),
                            'shell_spin_count': record.details.get('shell_spin_count', 0)
                        } for record in historical_data
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get historical performance: {e}")
            raise

    async def store_decision(self, user_id: int, decision_data: dict) -> int:
        """
        Store an optimization decision in central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=datetime.utcnow(),
                    agent_name=self.agent_name,
                    user_id=str(user_id),
                    event_type="optimization_decision",
                    subject_kind="decision",
                    subject_id=str(uuid.uuid4()),  # Unique decision ID
                    priority=7 if decision_data.get('confidence_level', 0) > 0.8 else 5,  # Higher priority for high confidence
                    title=f"Meth Snail Decision: {decision_data.get('decision_type', 'unknown')}",
                    description=decision_data.get('context', 'Optimization decision'),
                    details=decision_data,
                    metadata={
                        "confidence_level": decision_data.get('confidence_level', 0),
                        "energy_drink_consumed": decision_data.get('energy_drink_consumed', False),
                        "optimization_applied": decision_data.get('optimization_applied', False),
                        "shell_spinning_triggered": decision_data.get('shell_spinning_triggered', False)
                    },
                    numeric_value=decision_data.get('confidence_level', 0),
                    string_value=decision_data.get('decision_type', 'unknown'),
                    tags=["decision", "optimization", "meth_snail"],
                    agent_metadata={
                        "caffeinated": decision_data.get('energy_drink_consumed', False),
                        "shell_spinning": decision_data.get('shell_spinning_triggered', False)
                    },
                    relevant_agents="meth_snail,vic20,the_stick",  # VIC-20 mediates, Stick remembers
                    cross_agent_validated=False,
                    validation_count=0,
                    stick_anxiety_level=0.1 if decision_data.get('shell_spinning_triggered') else 0.0,
                    never_forget=decision_data.get('confidence_level', 0) > 0.9,  # Remember high confidence decisions
                    times_referenced=0,
                    successful_applications=0
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.id
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to store decision: {e}")
                raise

    async def increment_shell_spin_count(self, user_id: int) -> None:
        """
        Record a shell spin incident in central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                # Create shell spin incident entry
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=datetime.utcnow(),
                    agent_name=self.agent_name,
                    user_id=str(user_id),
                    event_type="shell_spin_incident",
                    subject_kind="performance_issue",
                    subject_id=str(user_id),
                    priority=8,  # High priority - indicates data quality issues
                    title="Meth Snail Shell Spin Detected",
                    description="Shell spinning due to insufficient or invalid data",
                    details={
                        "incident_type": "shell_spin",
                        "cause": "insufficient_data",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    metadata={
                        "requires_attention": True,
                        "data_quality_issue": True
                    },
                    numeric_value=1.0,  # Count as 1 incident
                    string_value="shell_spin",
                    tags=["shell_spin", "data_quality", "incident", "meth_snail"],
                    agent_metadata={
                        "spinning": True,
                        "foil_hat_status": "wobbling"  # The foil hat wobbles during shell spins
                    },
                    relevant_agents="meth_snail,sir_hawkington,the_stick",  # Hawk might help, Stick tracks
                    cross_agent_validated=False,
                    validation_count=0,
                    stick_anxiety_level=0.5,  # Shell spins make Stick anxious
                    never_forget=True,  # Always remember shell spin incidents
                    times_referenced=0,
                    successful_applications=0
                )
                
                session.add(memory_entry)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to record shell spin incident: {e}")
                raise

    async def get_jitter_levels(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent jitter level history from central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(CentralMemoryBank)
                    .where(CentralMemoryBank.agent_name == self.agent_name)
                    .where(CentralMemoryBank.user_id == str(user_id))
                    .where(CentralMemoryBank.event_type == "jitter_level_update")
                    .order_by(desc(CentralMemoryBank.occurred_at))
                    .limit(limit)
                )
                
                jitter_records = result.scalars().all()
                return [
                    {
                        'timestamp': record.occurred_at,
                        'current_jitter_level': record.details.get('current_jitter_level', 0.0),
                        'caffeine_level_mg': record.details.get('caffeine_level_mg', 0.0),
                        'focus_level': record.details.get('focus_level', 0.5),
                        'energy_source': record.details.get('energy_source', 'none'),
                        'jitter_trend': record.details.get('jitter_trend', 'stable')
                    } for record in jitter_records
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get jitter levels: {e}")
            raise
            
    async def update_jitter_levels(self, user_id: int, jitter_data: Dict[str, Any]) -> int:
        """
        Store jitter level update in central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                # Determine jitter severity for priority
                jitter_level = jitter_data.get('current_jitter_level', 0.0)
                if jitter_level > 0.8:
                    priority = 9  # HYPERCAFFEINATED - high priority
                    jitter_status = "HYPERCAFFEINATED"
                elif jitter_level > 0.6:
                    priority = 7  # JITTERY - medium-high priority
                    jitter_status = "JITTERY"
                else:
                    priority = 5  # Normal priority
                    jitter_status = "NORMAL"
                
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=datetime.utcnow(),
                    agent_name=self.agent_name,
                    user_id=str(user_id),
                    event_type="jitter_level_update",
                    subject_kind="agent_state",
                    subject_id=self.agent_name,
                    priority=priority,
                    title=f"Meth Snail Jitter Level: {jitter_status}",
                    description=f"Jitter level update - {jitter_data.get('jitter_trend', 'stable')} trend",
                    details=jitter_data,  # Store all jitter data
                    metadata={
                        "requires_stick_intervention": jitter_data.get('requires_stick_intervention', False),
                        "vic20_mediation_requested": jitter_data.get('vic20_mediation_requested', False),
                        "hypercaffeinated": jitter_data.get('hypercaffeinated', False),
                        "is_decaffeinated": jitter_data.get('is_decaffeinated', False)
                    },
                    numeric_value=jitter_level,
                    string_value=jitter_status,
                    tags=["jitter", "caffeine", "agent_state", "meth_snail"],
                    agent_metadata={
                        "caffeine_level_mg": jitter_data.get('caffeine_level_mg', 0.0),
                        "shell_spin_probability": jitter_data.get('shell_spin_probability', 0.05),
                        "optimization_effectiveness": jitter_data.get('optimization_effectiveness', 0.9),
                        "foil_hat_status": "secure" if jitter_level < 0.6 else "vibrating"
                    },
                    relevant_agents="meth_snail,sir_hawkington,the_stick,vic20" if jitter_data.get('vic20_mediation_requested') else "meth_snail,the_stick",
                    cross_agent_validated=False,
                    validation_count=0,
                    stick_anxiety_level=jitter_level * 0.8,  # Stick's anxiety correlates with jitter
                    never_forget=jitter_level > 0.9,  # Remember extreme jitter events
                    times_referenced=0,
                    successful_applications=0
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.id
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to update jitter levels: {e}")
                raise

    async def get_optimization_history(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent optimization history from central memory bank.
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(CentralMemoryBank)
                    .where(CentralMemoryBank.agent_name == self.agent_name)
                    .where(CentralMemoryBank.user_id == str(user_id))
                    .where(CentralMemoryBank.event_type == "optimization_decision")
                    .order_by(desc(CentralMemoryBank.occurred_at))
                    .limit(limit)
                )
                
                decisions = result.scalars().all()
                return [
                    {
                        'id': decision.id,
                        'timestamp': decision.occurred_at,
                        'decision_type': decision.string_value,
                        'confidence_level': decision.numeric_value,
                        'optimization_applied': decision.metadata.get('optimization_applied', False),
                        'shell_spinning_triggered': decision.metadata.get('shell_spinning_triggered', False)
                    } for decision in decisions
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get optimization history: {e}")
            raise

    # New methods for central memory bank integration
    async def store_energy_consumption(self, user_id: int, energy_drink_type: str, 
                                     caffeine_mg: float, consumption_time: datetime, 
                                     authorization_id: str) -> int:
        """Store energy drink consumption in central memory bank"""
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                memory_entry = CentralMemoryBank(
                    memory_id=str(uuid.uuid4()),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    occurred_at=consumption_time,
                    agent_name=self.agent_name,
                    user_id=str(user_id),
                    event_type="energy_drink_consumption",
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
                    metadata={
                        "authorized": True,  # Must be authorized to get here
                        "bromance_approved": "sir_hawkington" in authorization_id  # Hawk approved?
                    },
                    numeric_value=caffeine_mg,
                    string_value=energy_drink_type,
                    tags=["energy_drink", "caffeine", "consumption", "meth_snail"],
                    agent_metadata={
                        "caffeinated": True,
                        "energy_source": energy_drink_type
                    },
                    relevant_agents="meth_snail,sir_hawkington,the_stick",  # Hawk authorizes, Stick tracks
                    cross_agent_validated=True,  # Hawk validated
                    validation_count=1,
                    stick_anxiety_level=0.2,  # Mild anxiety about caffeine consumption
                    never_forget=caffeine_mg > 200,  # Remember high doses
                    times_referenced=0,
                    successful_applications=0
                )
                
                session.add(memory_entry)
                await session.commit()
                return memory_entry.id
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Failed to store energy consumption: {e}")
                raise

    async def get_recent_jitter_levels(self, user_id: int, hours: int = 1) -> Dict[str, Any]:
        """Get recent jitter levels for safety checks"""
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                
                result = await session.execute(
                    select(CentralMemoryBank)
                    .where(CentralMemoryBank.agent_name == self.agent_name)
                    .where(CentralMemoryBank.user_id == str(user_id))
                    .where(CentralMemoryBank.event_type == "jitter_level_update")
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

    async def get_energy_consumption_history(self, user_id: int, days: int = 1) -> Dict[str, Any]:
        """Get energy drink consumption history"""
        if not self._initialized:
            await self.initialize()
            
        try:
            async with self.session_factory() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                result = await session.execute(
                    select(CentralMemoryBank)
                    .where(CentralMemoryBank.agent_name == self.agent_name)
                    .where(CentralMemoryBank.user_id == str(user_id))
                    .where(CentralMemoryBank.event_type == "energy_drink_consumption")
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

    async def get_energy_drink_consumption(self, user_id: int, days: int = 1) -> Dict[str, Any]:
        """Wrapper method for compatibility - calls get_energy_consumption_history"""
        return await self.get_energy_consumption_history(user_id, days)

    async def store_jitter_level(self, user_id: int, jitter_level: float, 
                                caffeine_level_mg: float, timestamp: datetime) -> None:
        """Store a jitter level measurement"""
        await self.update_jitter_levels(user_id, {
            'current_jitter_level': jitter_level,
            'caffeine_level_mg': caffeine_level_mg,
            'jitter_trend': 'stable',  # Will be calculated based on history
            'timestamp': timestamp.isoformat()
        })