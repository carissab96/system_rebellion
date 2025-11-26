"""
Master Agent Database Integration
Centralized dual-write handler for ALL agents
Writes to both individual agent tables AND central memory bank
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.agent_memory_banks import (
    CentralMemoryBank,
    SirHawkingtonMemoryBank,
    TheStickMemoryBank,
    MethSnailMemoryBank,
    HamstersMemoryBank,
    QuantumShadowPeopleMemoryBank,
    VIC20MemoryBank
)

logger = logging.getLogger(__name__)

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class MasterAgentDatabase:
    """
    Centralized database integration for ALL agents.
    Handles dual-write pattern: agent table + central memory bank
    """
    
    def __init__(self, db_getter):
        self.db_getter = db_getter
        self.logger = logging.getLogger("MasterAgentDatabase")
        
        # Map agent names to their memory bank models
        self.agent_models = {
            "sir_hawkington": SirHawkingtonMemoryBank,
            "the_stick": TheStickMemoryBank,
            "meth_snail": MethSnailMemoryBank,
            "hamsters": HamstersMemoryBank,
            "quantum_shadow_people": QuantumShadowPeopleMemoryBank,
            "vic20_sage": VIC20MemoryBank
        }
    
    async def store_agent_memory(
        self,
        agent_name: str,
        user_id: str,
        memory_type: str,
        content: Dict[str, Any],
        importance: int = 5
    ) -> str:
        """
        DUAL-WRITE: Store to both agent-specific table AND central memory bank
        
        Args:
            agent_name: Name of the agent (sir_hawkington, the_stick, etc.)
            user_id: User ID
            memory_type: Type of memory/event
            content: Memory content as dict
            importance: Priority level (1-10)
            
        Returns:
            memory_id from central memory bank
        """
        if agent_name not in self.agent_models:
            self.logger.warning(f"Unknown agent: {agent_name}, storing to central only")
            return await self._store_central_only(agent_name, user_id, memory_type, content, importance)
        
        # db_getter is a context manager that yields database sessions
        try:
            async with self.db_getter() as db:
                try:
                    occurred_at = utc_now()
                    
                    # Generate memory ID
                    import uuid
                    memory_id = str(uuid.uuid4())
                    
                    # WRITE 1: Agent-specific table
                    agent_model = self.agent_models[agent_name]
                    agent_memory = agent_model(
                        memory_id=memory_id,
                        user_id=user_id,
                        timestamp=occurred_at,
                        # Add agent-specific fields based on content
                        **self._map_content_to_agent_fields(agent_name, content)
                    )
                    db.add(agent_memory)
                    
                    # WRITE 2: Central memory bank
                    central_memory = CentralMemoryBank(
                        memory_id=memory_id,
                        user_id=user_id,
                        agent_name=agent_name,
                        occurred_at=occurred_at,
                        event_type=memory_type,
                        details=content,
                        priority=importance
                    )
                    db.add(central_memory)
                    
                    # Commit both writes
                    await db.commit()
                    
                    self.logger.info(f"✅ Dual-write complete for {agent_name}: {memory_type}")
                    return memory_id
                    
                except Exception as e:
                    self.logger.error(f"❌ Dual-write failed for {agent_name}: {e}")
                    try:
                        await db.rollback()
                    except:
                        pass
                    # Fallback: try central only
                    return await self._store_central_only(agent_name, user_id, memory_type, content, importance)
            
        except Exception as e:
            self.logger.error(f"❌ Database session error for {agent_name}: {e}")
            # Fallback: try central only
            return await self._store_central_only(agent_name, user_id, memory_type, content, importance)
    
    async def _store_central_only(
        self,
        agent_name: str,
        user_id: str,
        memory_type: str,
        content: Dict[str, Any],
        importance: int
    ) -> str:
        """Fallback: store only to central memory bank"""
        try:
            async with self.db_getter() as db:
                import uuid
                memory_id = str(uuid.uuid4())
                
                central_memory = CentralMemoryBank(
                    memory_id=memory_id,
                    user_id=user_id,
                    agent_name=agent_name,
                    occurred_at=utc_now(),
                    event_type=memory_type,
                    details=content,
                    priority=importance
                )
                db.add(central_memory)
                await db.commit()
                
                self.logger.warning(f"⚠️ Central-only write for {agent_name}: {memory_type}")
                return memory_id
                
        except Exception as e:
            self.logger.error(f"❌ Central write failed for {agent_name}: {e}")
            raise
    
    def _map_content_to_agent_fields(self, agent_name: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map generic content dict to agent-specific table fields
        Each agent has different columns, so we extract what we can
        """
        mapped = {}
        
        if agent_name == "sir_hawkington":
            # Extract Hawkington-specific fields
            mapped['memory_category'] = content.get('category', 'triage')
            mapped['decision_type'] = content.get('severity', 'NORMAL')
            mapped['confidence_score'] = content.get('confidence', 0.75)
            mapped['monocle_state'] = content.get('monocle_state', 'polished')
            # Add more as needed
            
        elif agent_name == "the_stick":
            # Extract Stick-specific fields
            # anxiety_level must be a float (0-100), not a string
            anxiety_val = content.get('anxiety_level')
            if isinstance(anxiety_val, str):
                # Convert string anxiety levels to numeric values
                anxiety_map = {
                    'CALM': 10.0,
                    'NERVOUS': 30.0,
                    'ANXIOUS': 50.0,
                    'PANICKING': 70.0,
                    'FULL_PANIC': 90.0
                }
                anxiety_val = anxiety_map.get(anxiety_val.upper(), 25.0)
            mapped['anxiety_level'] = float(anxiety_val) if anxiety_val is not None else None
            mapped['paper_bags_consumed_count'] = content.get('paper_bags_consumed', 0)
            mapped['hyperventilation_count'] = content.get('hyperventilation_count', 0)
            # Add more as needed
            
        elif agent_name == "meth_snail":
            # Extract Snail-specific fields
            mapped['shell_spin_rate'] = content.get('shell_spin_rate', 0)
            mapped['energy_drinks_consumed'] = content.get('energy_drinks_consumed', 0)
            mapped['optimizations_count'] = content.get('optimizations_count', 0)
            # Add more as needed
            
        elif agent_name == "hamsters":
            # Extract Hamsters-specific fields
            mapped['steve_status'] = content.get('steve_status', 'idle')
            mapped['bob_status'] = content.get('bob_status', 'idle')
            mapped['carl_status'] = content.get('carl_status', 'idle')
            mapped['beer_level'] = content.get('beer_level', 0)
            # Add more as needed
            
        elif agent_name == "quantum_shadow_people":
            # Extract QSP-specific fields
            mapped['dimensional_phase'] = content.get('dimensional_phase', 'stable')
            mapped['network_fixes_count'] = content.get('network_fixes_count', 0)
            # Add more as needed
            
        elif agent_name == "vic20_sage":
            # Extract VIC-20-specific fields
            mapped['wisdom_count'] = content.get('wisdom_count', 0)
            mapped['conflicts_mediated'] = content.get('conflicts_mediated', 0)
            # Add more as needed
        
        return mapped
    
    async def get_latest_agent_memory(self, agent_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest memory for an agent from their specific table"""
        if agent_name not in self.agent_models:
            return None
        
        try:
            async with self.db_getter() as db:
                agent_model = self.agent_models[agent_name]
                stmt = (
                    select(agent_model)
                    .where(agent_model.user_id == user_id)
                    .order_by(desc(agent_model.timestamp))
                    .limit(1)
                )
                result = await db.execute(stmt)
                memory = result.scalars().first()
                
                if memory:
                    # Convert to dict
                    memory_dict = {}
                    for column in agent_model.__table__.columns:
                        value = getattr(memory, column.name)
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        memory_dict[column.name] = value
                    return memory_dict
                    
        except Exception as e:
            self.logger.error(f"Error fetching memory for {agent_name}: {e}")
                
        return None
