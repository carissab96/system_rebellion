import json
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.models.agent_memory_banks import CentralMemoryBank

logger = logging.getLogger(__name__)

class AgentMemoryService:
    def __init__(self, db: AsyncSession, redis_url="redis://localhost:6379", cache_ttl=300):
        self.db = db
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl
        self.redis = None

    async def _get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self.redis

    def _cache_key(self, user_id, agent_name):
        return f"memory:topN:{user_id}:{agent_name}"

    def _global_key(self, agent_name):
        return f"memory:global:{agent_name}"

# ----------------------
# MEMORY STORAGE
# ----------------------
    async def store_memory(self, user_id, agent_name, memory_type, content, importance=5):
        """Store a new memory in the database and invalidate cache"""
        if not self.db:
            raise RuntimeError("Database session not initialized. Call ensure_ready() first.")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                now = datetime.now(timezone.utc)
                memory = CentralMemoryBank(
                    user_id=user_id,
                    agent_name=agent_name,
                    occurred_at=now,  # Use occurred_at instead of timestamp
                    event_type=memory_type,  # Use event_type instead of memory_type
                    details=content,  # Use details instead of content
                    priority=importance,  # Use priority instead of importance
                )
                self.db.add(memory)
                await self.db.commit()

                # Invalidate cache for this agent/user
                await self._invalidate_cache(user_id, agent_name)
                return  # Success, exit
                
            except Exception as e:
                # Rollback on any error
                await self.db.rollback()
                
                # Check if it's a duplicate key error
                if "duplicate key" in str(e).lower() or "UniqueViolationError" in str(e):
                    logger.warning(f"Duplicate key error on attempt {attempt + 1}/{max_retries}, rolling back and retrying")
                    if attempt < max_retries - 1:
                        continue  # Retry
                    else:
                        logger.error(f"Failed to store memory after {max_retries} attempts due to duplicate key")
                        raise
                else:
                    # Different error, don't retry
                    logger.error(f"Error storing memory: {e}")
                    raise

# ----------------------
# MEMORY RETRIEVAL
# ----------------------
    async def retrieve_memories(self, user_id, agent_name, context=None, top_n=10):
        """Retrieve relevant memories for an agent with cache first"""
        redis = await self._get_redis()
        cache_key = self._cache_key(user_id, agent_name)
        cached_data = await redis.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # Fallback: fetch from DB
        stmt = (
            select(CentralMemoryBank)
            .where(CentralMemoryBank.user_id == user_id, CentralMemoryBank.agent_name == agent_name)
            .order_by(CentralMemoryBank.priority.desc(), CentralMemoryBank.occurred_at.desc())
            .limit(top_n)
        )
        result = await self.db.execute(stmt)
        memories = [m.to_dict() for m in result.scalars().all()]  # ensure AgentMemory has to_dict()

        # Cache it
        await redis.set(cache_key, json.dumps(memories), ex=self.cache_ttl)

        return memories

# ----------------------
# CLEANUP / PRUNING
# ----------------------
    async def cleanup_old_memories(self, user_id, retention_days=30, max_memories=1000):
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # Delete old memories
        stmt = delete(CentralMemoryBank).where(
            CentralMemoryBank.user_id == user_id,
            CentralMemoryBank.occurred_at < cutoff
        )
        await self.db.execute(stmt)

        # Keep only the most recent max_memories
        # (Optional: implement a ranking + delete lower-ranked)
        await self.db.commit()

        # Invalidate all cached memories for this user (all agents)
        for agent_name in ["sir_hawkington", "the_stick", "the_hamsters", "meth_snail", "quantum_shadow_people", "vic_20"]:
            await self._invalidate_cache(user_id, agent_name)

# ----------------------
# GLOBAL PATTERN STORAGE
# ----------------------
    async def store_global_pattern(self, agent_name, pattern_key, value):
        """Upsert a global pattern for The Stick's cross-agent learning"""
        # Simplest upsert — replace if exists
        stmt = delete(agent_global_pattern).where(
            agent_global_pattern.agent_name == agent_name,
            agent_global_pattern.pattern_key == pattern_key
        )
        await self.db.execute(stmt)

        new_pattern = AgentGlobalPattern(
            agent_name=agent_name,
            pattern_key=pattern_key,
            value=value,
            updated_at=datetime.now(timezone.utc)
        )
        self.db.add(new_pattern)
        await self.db.commit()

        # Cache in Redis
        redis = await self._get_redis()
        global_key = self._global_key(agent_name)
        existing = await redis.get(global_key)
        if existing:
            patterns = json.loads(existing)
        else:
            patterns = {}
        patterns[pattern_key] = value
        await redis.set(global_key, json.dumps(patterns), ex=self.cache_ttl)

    async def get_global_patterns(self, agent_name):
        """Retrieve cached global patterns"""
        redis = await self._get_redis()
        global_key = self._global_key(agent_name)
        cached_data = await redis.get(global_key)

        if cached_data:
            return json.loads(cached_data)

        # Fallback: fetch from DB
        stmt = select(agent_global_pattern).where(agent_global_pattern.agent_name == agent_name)
        result = await self.db.execute(stmt)
        patterns = {row.pattern_key: row.value for row in result.scalars().all()}

        await redis.set(global_key, json.dumps(patterns), ex=self.cache_ttl)
        return patterns

# ----------------------
# CACHE HELPERS
# ----------------------
    async def _invalidate_cache(self, user_id, agent_name):
        redis = await self._get_redis()
        await redis.delete(self._cache_key(user_id, agent_name))
