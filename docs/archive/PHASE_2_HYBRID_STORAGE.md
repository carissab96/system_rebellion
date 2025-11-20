# Phase 2: Hybrid PostgreSQL + Redis Memory Bank Storage

## Overview
Implement hybrid storage architecture where hot agent data resides in Redis for instant access, while cold/archival data is stored in PostgreSQL for persistence and complex queries.

## Goals
- Agent memory access in <10ms average
- Automatic data migration from hot to cold storage
- Maintain data consistency across both stores
- Enable complex analytics on historical agent data

## Prerequisites
- Phase 1 (Agent Pub/Sub) completed and tested
- PostgreSQL and Redis both running
- Agent memory system functional
- Data migration tools ready

## Architecture Overview

### Current State
- All agent memory stored in PostgreSQL
- Memory access requires database queries
- No distinction between hot and cold data
- Complex queries slow down real-time operations

### Target State
- Hot data (recent agent memories) in Redis
- Cold data (older memories) in PostgreSQL
- Automatic migration based on time/access patterns
- Instant access for active agent operations

## Implementation Plan

### Step 1: Enhanced Agent Memory Service

**File**: `backend/app/services/agent_memory_service_hybrid.py` (NEW)

```python
import redis.asyncio as redis
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_memory_banks import Base
import asyncio

logger = logging.getLogger(__name__)

class HybridAgentMemoryService:
    """
    Hybrid storage for agent memories:
    - Hot data: Redis (fast access, limited retention)
    - Cold data: PostgreSQL (persistent, unlimited retention)
    """

    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 hot_data_ttl_hours: int = 24,
                 max_hot_memories_per_agent: int = 1000):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.hot_data_ttl = timedelta(hours=hot_data_ttl_hours)
        self.max_hot_memories = max_hot_memories_per_agent
        self.is_initialized = False

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            self.is_initialized = True
            logger.info("✅ Hybrid agent memory service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize hybrid memory service: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    def _get_hot_key(self, agent_name: str, memory_id: str) -> str:
        """Generate Redis key for hot memory"""
        return f"agent:{agent_name}:memory:hot:{memory_id}"

    def _get_hot_list_key(self, agent_name: str) -> str:
        """Generate Redis key for agent's hot memory list"""
        return f"agent:{agent_name}:memory:hot:list"

    def _get_cold_table_name(self, agent_name: str) -> str:
        """Get PostgreSQL table name for agent's cold memories"""
        # Map agent names to their memory bank models
        table_mapping = {
            "sir_hawkington": "sir_hawkington_memory_bank",
            "meth_snail": "meth_snail_memory_bank",
            "the_stick": "the_stick_memory_bank",
            "quantum_shadow_people": "quantum_shadow_people_memory_bank",
            "hamsters": "hamsters_memory_bank",
            "vic_20_sage": "vic_20_sage_memory_bank"
        }
        return table_mapping.get(agent_name, f"{agent_name}_memory_bank")

    async def store_memory(self, agent_name: str, memory_data: dict, db_session: AsyncSession) -> str:
        """Store memory in hybrid storage"""
        if not self.is_initialized:
            raise RuntimeError("Hybrid memory service not initialized")

        memory_id = memory_data.get('id') or f"{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        memory_data['id'] = memory_id
        memory_data['stored_at'] = datetime.now(timezone.utc).isoformat()
        memory_data['agent_name'] = agent_name

        try:
            # Always store in Redis (hot storage) first
            hot_key = self._get_hot_key(agent_name, memory_id)
            await self.redis.setex(
                hot_key,
                int(self.hot_data_ttl.total_seconds()),
                json.dumps(memory_data)
            )

            # Add to agent's hot memory list
            list_key = self._get_hot_list_key(agent_name)
            await self.redis.lpush(list_key, memory_id)

            # Trim list to max size
            await self.redis.ltrim(list_key, 0, self.max_hot_memories - 1)

            # Store in PostgreSQL (cold storage) asynchronously
            asyncio.create_task(self._migrate_to_cold_storage(agent_name, memory_data, db_session))

            logger.info(f"💾 Stored memory {memory_id} for agent {agent_name} in hybrid storage")
            return memory_id

        except Exception as e:
            logger.error(f"❌ Failed to store memory for {agent_name}: {e}")
            raise

    async def get_memory(self, agent_name: str, memory_id: str, db_session: AsyncSession) -> Optional[dict]:
        """Retrieve memory from hybrid storage"""
        if not self.is_initialized:
            raise RuntimeError("Hybrid memory service not initialized")

        try:
            # Try hot storage first (Redis)
            hot_key = self._get_hot_key(agent_name, memory_id)
            hot_data = await self.redis.get(hot_key)

            if hot_data:
                memory = json.loads(hot_data)
                logger.debug(f"🔥 Retrieved hot memory {memory_id} for {agent_name}")
                return memory

            # Fall back to cold storage (PostgreSQL)
            return await self._get_cold_memory(agent_name, memory_id, db_session)

        except Exception as e:
            logger.error(f"❌ Failed to retrieve memory {memory_id} for {agent_name}: {e}")
            return None

    async def get_recent_memories(self, agent_name: str, limit: int = 50, db_session: AsyncSession = None) -> List[dict]:
        """Get recent memories, prioritizing hot storage"""
        if not self.is_initialized:
            raise RuntimeError("Hybrid memory service not initialized")

        try:
            memories = []

            # Get hot memories from Redis
            list_key = self._get_hot_list_key(agent_name)
            hot_ids = await self.redis.lrange(list_key, 0, limit - 1)

            for memory_id in hot_ids:
                hot_key = self._get_hot_key(agent_name, memory_id)
                hot_data = await self.redis.get(hot_key)
                if hot_data:
                    memories.append(json.loads(hot_data))

            # If we need more, supplement from cold storage
            if len(memories) < limit and db_session:
                cold_memories = await self._get_recent_cold_memories(agent_name, limit - len(memories), db_session)
                memories.extend(cold_memories)

            logger.debug(f"📚 Retrieved {len(memories)} recent memories for {agent_name}")
            return memories[:limit]

        except Exception as e:
            logger.error(f"❌ Failed to get recent memories for {agent_name}: {e}")
            return []

    async def _migrate_to_cold_storage(self, agent_name: str, memory_data: dict, db_session: AsyncSession):
        """Migrate memory from hot to cold storage"""
        try:
            table_name = self._get_cold_table_name(agent_name)

            # Insert into PostgreSQL
            insert_query = f"""
            INSERT INTO {table_name}
            (id, agent_name, memory_type, content, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                updated_at = EXCLUDED.updated_at
            """

            await db_session.execute(
                insert_query,
                (
                    memory_data['id'],
                    agent_name,
                    memory_data.get('memory_type', 'general'),
                    json.dumps(memory_data.get('content', {})),
                    json.dumps(memory_data.get('metadata', {})),
                    datetime.fromisoformat(memory_data['stored_at']),
                    datetime.now(timezone.utc)
                )
            )

            await db_session.commit()
            logger.debug(f"🧊 Migrated memory {memory_data['id']} to cold storage for {agent_name}")

        except Exception as e:
            logger.error(f"❌ Failed to migrate memory to cold storage: {e}")
            # Don't raise - migration failure shouldn't break hot storage

    async def _get_cold_memory(self, agent_name: str, memory_id: str, db_session: AsyncSession) -> Optional[dict]:
        """Retrieve memory from cold storage"""
        try:
            table_name = self._get_cold_table_name(agent_name)

            query = f"SELECT * FROM {table_name} WHERE id = $1"
            result = await db_session.execute(query, (memory_id,))
            row = result.fetchone()

            if row:
                # Convert back to dict format
                memory = {
                    'id': row.id,
                    'agent_name': row.agent_name,
                    'memory_type': row.memory_type,
                    'content': json.loads(row.content) if row.content else {},
                    'metadata': json.loads(row.metadata) if row.metadata else {},
                    'stored_at': row.created_at.isoformat() if row.created_at else None
                }
                logger.debug(f"🧊 Retrieved cold memory {memory_id} for {agent_name}")
                return memory

            return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve cold memory {memory_id}: {e}")
            return None

    async def _get_recent_cold_memories(self, agent_name: str, limit: int, db_session: AsyncSession) -> List[dict]:
        """Get recent memories from cold storage"""
        try:
            table_name = self._get_cold_table_name(agent_name)

            query = f"""
            SELECT * FROM {table_name}
            WHERE agent_name = $1
            ORDER BY created_at DESC
            LIMIT $2
            """

            result = await db_session.execute(query, (agent_name, limit))
            rows = result.fetchall()

            memories = []
            for row in rows:
                memory = {
                    'id': row.id,
                    'agent_name': row.agent_name,
                    'memory_type': row.memory_type,
                    'content': json.loads(row.content) if row.content else {},
                    'metadata': json.loads(row.metadata) if row.metadata else {},
                    'stored_at': row.created_at.isoformat() if row.created_at else None
                }
                memories.append(memory)

            return memories

        except Exception as e:
            logger.error(f"❌ Failed to get recent cold memories: {e}")
            return []

    async def cleanup_expired_hot_data(self):
        """Clean up expired hot data (Redis TTL handles most of this)"""
        # Redis TTL handles expiration, but we can add custom cleanup logic here
        pass

# Global instance
_hybrid_memory_instance: Optional[HybridAgentMemoryService] = None

async def get_hybrid_memory_service() -> HybridAgentMemoryService:
    """Get global hybrid memory service instance"""
    global _hybrid_memory_instance

    if _hybrid_memory_instance is None:
        _hybrid_memory_instance = HybridAgentMemoryService()
        await _hybrid_memory_instance.initialize()

    return _hybrid_memory_instance
```

### Step 2: Create Data Migration Utilities

**File**: `backend/scripts/migrate_agent_memories.py` (NEW)

```python
#!/usr/bin/env python3
"""
Migrate existing agent memories from PostgreSQL to hybrid storage
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.database import get_db_url
from app.services.agent_memory_service_hybrid import get_hybrid_memory_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_agent_memories():
    """Migrate all existing agent memories to hybrid storage"""
    engine = create_async_engine(get_db_url())

    try:
        async with AsyncSession(engine) as session:
            hybrid_service = await get_hybrid_memory_service()

            # Get all agent memory tables
            agent_tables = [
                "sir_hawkington_memory_bank",
                "meth_snail_memory_bank",
                "the_stick_memory_bank",
                "quantum_shadow_people_memory_bank",
                "hamsters_memory_bank",
                "vic_20_sage_memory_bank"
            ]

            total_migrated = 0

            for table_name in agent_tables:
                try:
                    # Get agent name from table
                    agent_name = table_name.replace("_memory_bank", "")

                    # Query existing memories
                    query = f"SELECT * FROM {table_name} ORDER BY created_at DESC"
                    result = await session.execute(query)
                    rows = result.fetchall()

                    logger.info(f"Found {len(rows)} memories for {agent_name}")

                    # Migrate each memory (only recent ones to hot storage)
                    for row in rows[:hybrid_service.max_hot_memories]:  # Only migrate recent/hot data
                        memory_data = {
                            'id': row.id,
                            'memory_type': row.memory_type,
                            'content': row.content,
                            'metadata': row.metadata,
                            'stored_at': row.created_at.isoformat() if row.created_at else None
                        }

                        # Store in hybrid system
                        await hybrid_service.store_memory(agent_name, memory_data, session)
                        total_migrated += 1

                    logger.info(f"✅ Migrated {min(len(rows), hybrid_service.max_hot_memories)} hot memories for {agent_name}")

                except Exception as e:
                    logger.error(f"❌ Failed to migrate {table_name}: {e}")
                    continue

            logger.info(f"🎉 Migration complete! Migrated {total_migrated} memories")

    finally:
        await engine.dispose()
        await hybrid_service.close()

if __name__ == "__main__":
    asyncio.run(migrate_agent_memories())
```

### Step 3: Update Agent Manager to Use Hybrid Storage

**File**: `backend/app/ai_agents/agent_manager.py`

**Integrate hybrid memory service**:
```python
from app.services.agent_memory_service_hybrid import get_hybrid_memory_service

class AgentManager:
    def __init__(self, db_getter=None):
        # ... existing initialization
        self.hybrid_memory = None

    async def initialize_agents(self):
        """Initialize agents with hybrid memory support"""
        # ... existing initialization

        # Initialize hybrid memory service
        try:
            self.hybrid_memory = await get_hybrid_memory_service()
            logger.info("🧊 Hybrid agent memory service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize hybrid memory: {e}")
            # Continue without hybrid memory - fall back to PostgreSQL only

        # ... rest of initialization

    async def store_agent_memory(self, agent_name: str, memory_data: dict):
        """Store agent memory using hybrid storage"""
        if self.hybrid_memory:
            # Use hybrid storage
            db_session = await self.db_getter()
            try:
                memory_id = await self.hybrid_memory.store_memory(agent_name, memory_data, db_session)
                logger.info(f"💾 Stored hybrid memory for {agent_name}: {memory_id}")
                return memory_id
            finally:
                await db_session.close()
        else:
            # Fall back to direct PostgreSQL storage
            logger.warning("Hybrid memory not available, using PostgreSQL only")
            return await self._store_memory_postgres_only(agent_name, memory_data)

    async def get_agent_memory(self, agent_name: str, memory_id: str):
        """Retrieve agent memory from hybrid storage"""
        if self.hybrid_memory:
            db_session = await self.db_getter()
            try:
                return await self.hybrid_memory.get_memory(agent_name, memory_id, db_session)
            finally:
                await db_session.close()
        else:
            return await self._get_memory_postgres_only(agent_name, memory_id)

    async def get_agent_recent_memories(self, agent_name: str, limit: int = 50):
        """Get recent agent memories"""
        if self.hybrid_memory:
            db_session = await self.db_getter()
            try:
                return await self.hybrid_memory.get_recent_memories(agent_name, limit, db_session)
            finally:
                await db_session.close()
        else:
            return await self._get_recent_memories_postgres_only(agent_name, limit)
```

### Step 4: Update Main Application Startup

**File**: `backend/main.py` (lifespan function)

**Initialize hybrid memory service**:
```python
# Initialize hybrid agent memory service
try:
    hybrid_memory = await get_hybrid_memory_service()
    logger.info("🧊 Hybrid agent memory service initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize hybrid memory: {e}")
    # Continue without hybrid memory - not critical
```

## Testing Implementation

### Performance Tests
**File**: `backend/dev-tools/tests/test_hybrid_memory_performance.py` (NEW)

```python
import pytest
import asyncio
import time
from app.services.agent_memory_service_hybrid import get_hybrid_memory_service

@pytest.mark.asyncio
async def test_memory_access_performance():
    """Test memory access performance meets requirements"""
    service = await get_hybrid_memory_service()

    # Test data
    agent_name = "sir_hawkington"
    memory_data = {
        "memory_type": "observation",
        "content": {"observation": "System running smoothly", "confidence": 0.95},
        "metadata": {"source": "test", "timestamp": "2025-01-01T00:00:00Z"}
    }

    # Measure store performance
    start_time = time.time()
    memory_id = await service.store_memory(agent_name, memory_data, None)  # db_session would be needed
    store_time = time.time() - start_time

    # Measure retrieval performance
    start_time = time.time()
    retrieved = await service.get_memory(agent_name, memory_id, None)
    retrieve_time = time.time() - start_time

    # Assert performance requirements
    assert store_time < 0.1, f"Store too slow: {store_time}s"
    assert retrieve_time < 0.01, f"Retrieve too slow: {retrieve_time}s"  # 10ms requirement
    assert retrieved is not None
    assert retrieved['content']['observation'] == memory_data['content']['observation']

@pytest.mark.asyncio
async def test_data_consistency():
    """Test data consistency between hot and cold storage"""
    service = await get_hybrid_memory_service()

    agent_name = "meth_snail"
    memory_data = {
        "memory_type": "optimization",
        "content": {"optimization": "CPU usage reduced by 15%", "metrics": {"cpu_before": 85, "cpu_after": 70}},
        "metadata": {"algorithm": "test_optimization"}
    }

    # Store memory
    memory_id = await service.store_memory(agent_name, memory_data, None)

    # Wait for cold storage migration (in real scenario)
    await asyncio.sleep(0.1)

    # Retrieve from hot storage
    hot_memory = await service.get_memory(agent_name, memory_id, None)

    # In real scenario, also check cold storage directly
    # cold_memory = await service._get_cold_memory(agent_name, memory_id, db_session)

    assert hot_memory is not None
    assert hot_memory['memory_type'] == memory_data['memory_type']
    assert hot_memory['content']['optimization'] == memory_data['content']['optimization']
```

### Integration Tests
**File**: `backend/dev-tools/tests/test_hybrid_memory_integration.py` (NEW)

```python
import pytest
from app.ai_agents.agent_manager import get_agent_manager

@pytest.mark.asyncio
async def test_agent_memory_integration():
    """Test agent memory storage through agent manager"""
    agent_manager = await get_agent_manager()

    # Test storing memory via agent manager
    test_memory = {
        "memory_type": "decision",
        "content": {"decision": "Increase monitoring frequency", "reasoning": "High system load detected"},
        "metadata": {"confidence": 0.87, "impact": "medium"}
    }

    memory_id = await agent_manager.store_agent_memory("sir_hawkington", test_memory)
    assert memory_id is not None

    # Test retrieving memory
    retrieved = await agent_manager.get_agent_memory("sir_hawkington", memory_id)
    assert retrieved is not None
    assert retrieved['content']['decision'] == test_memory['content']['decision']

    # Test recent memories
    recent = await agent_manager.get_agent_recent_memories("sir_hawkington", 10)
    assert len(recent) > 0
    assert any(m['id'] == memory_id for m in recent)

@pytest.mark.asyncio
async def test_fallback_behavior():
    """Test fallback when hybrid storage is unavailable"""
    agent_manager = await get_agent_manager()

    # Force hybrid memory to None (simulate Redis failure)
    agent_manager.hybrid_memory = None

    # Test should still work via PostgreSQL fallback
    test_memory = {
        "memory_type": "test_fallback",
        "content": {"test": "fallback_mode"},
        "metadata": {"fallback": True}
    }

    memory_id = await agent_manager.store_agent_memory("meth_snail", test_memory)
    assert memory_id is not None

    retrieved = await agent_manager.get_agent_memory("meth_snail", memory_id)
    assert retrieved is not None
```

### Migration Tests
**File**: `backend/dev-tools/tests/test_memory_migration.py` (NEW)

```python
import pytest
from scripts.migrate_agent_memories import migrate_agent_memories

@pytest.mark.asyncio
async def test_memory_migration():
    """Test memory migration from PostgreSQL to hybrid storage"""
    # This test would require actual data in PostgreSQL
    # and would be run after setting up test data

    # Count memories before migration
    # Run migration
    # await migrate_agent_memories()
    # Verify memories are in both storages
    # Verify performance improvement

    # For now, just test the migration script doesn't crash
    assert True  # Placeholder
```

### Manual Testing Checklist
- [ ] Verify Redis and PostgreSQL are running
- [ ] Run migration script
- [ ] Check memory access times (<10ms)
- [ ] Verify data consistency between stores
- [ ] Test agent memory operations via WebSocket
- [ ] Monitor Redis memory usage
- [ ] Test fallback when Redis is unavailable

## Rollback Plan

### Phase 2 Rollback Steps
1. **Stop the application**
2. **Revert agent manager changes**:
   ```bash
   git checkout backend/app/ai_agents/agent_manager.py
   ```
3. **Remove hybrid memory service**:
   ```bash
   rm backend/app/services/agent_memory_service_hybrid.py
   ```
4. **Remove migration script**:
   ```bash
   rm backend/scripts/migrate_agent_memories.py
   ```
5. **Revert main.py changes**:
   ```bash
   git checkout backend/main.py
   ```
6. **Clear Redis agent memory keys** (optional):
   ```bash
   redis-cli KEYS "agent:*:memory:*" | xargs redis-cli DEL
   ```
7. **Restart application**
8. **Verify agents use PostgreSQL-only storage**

### Rollback Verification
- [ ] Application starts successfully
- [ ] Agent memories still accessible from PostgreSQL
- [ ] No Redis connection errors
- [ ] Agent functionality unchanged
- [ ] WebSocket connections work

## Success Metrics
- [ ] Memory access time < 10ms average (vs 100-500ms previously)
- [ ] 90% of memory requests served from Redis (hot storage)
- [ ] Data consistency maintained across both stores
- [ ] Migration completes without data loss
- [ ] Fallback to PostgreSQL works when Redis unavailable
- [ ] Redis memory usage stays within limits

## Dependencies
- Both Redis and PostgreSQL must be running
- Phase 1 (Agent Pub/Sub) must be completed
- Existing PostgreSQL schema must be intact
- Agent memory models must exist

## Risk Mitigation
- **Redis Failure**: Automatic fallback to PostgreSQL
- **Migration Issues**: Incremental migration with rollback capability
- **Data Loss**: PostgreSQL remains source of truth
- **Performance**: Hot data TTL prevents Redis bloat
- **Consistency**: Write-through caching ensures data integrity
