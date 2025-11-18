import inspect
import logging
# from app.utils.redis_compat import redis

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_memory_service import AgentMemoryService
from .memory_cache_mixin import MemoryCacheMixin
from .task_queue import RedisTaskQueue, Priority
from .redis_client import RedisClient

logger = logging.getLogger(__name__)


class AgentMemoryServiceWithCache(AgentMemoryService, MemoryCacheMixin):
    def __init__(self, *args, **kwargs):
        # Pull wrapper-only kwargs FIRST so they don't reach the base class
        redis_url        = kwargs.pop("redis_url", None)
        self._db_getter  = kwargs.pop("db_getter", None)   # may be async or sync callable
        db_session       = kwargs.pop("db_session", None)  # optional pre-built session
        self.task_queue = None
        self.redis_url = redis_url or "redis://localhost:6379"
        self._shared_redis_client = None

        # Initialize base classes
        AgentMemoryService.__init__(self, db_session)
        MemoryCacheMixin.__init__(self, redis_url=self.redis_url)

        # If caller gave us a getter but no session, we'll use it in ensure_ready()
        self._pending_db_coro = None
        # Don't call db_getter in __init__ - wait for ensure_ready()
        # This prevents issues with session lifecycle

    async def _get_redis(self):
        """Override MemoryCacheMixin's _get_redis to use shared RedisClient singleton"""
        if self._shared_redis_client is None:
            redis_client = await RedisClient.get_instance(redis_url=self.redis_url)
            self._shared_redis_client = redis_client.client
        return self._shared_redis_client

    async def ensure_ready(self):
        """Ensure both DB and Redis are ready"""
        # If we don't have a session yet and have a db_getter, get one now
        if self.db is None and self._db_getter is not None:
            logger.info("🔍 Getting database session from db_getter")
            maybe = self._db_getter()
            if inspect.isawaitable(maybe):
                self.db = await maybe
            else:
                self.db = maybe
            logger.info(f"🔍 DB session acquired: {type(self.db)}")
        
        # Log the database session state
        if self.db is None:
            logger.warning("⚠️ Database session is None - operations will fail")

        if self.task_queue is None:
            # Use the shared RedisClient singleton instead of creating a new connection
            redis_client = await RedisClient.get_instance(redis_url=self.redis_url)
            self.task_queue = RedisTaskQueue(redis_client.client)
            logger.info("✅ Task queue initialized with shared Redis client")
    
    def _cache_key(self, user_id: str, agent_name: str) -> str:
        """Generate cache key for agent memories"""
        return f"agent_memory:{user_id}:{agent_name}"
    
    def _global_key(self, agent_name: str) -> str:
        """Generate cache key for global patterns"""
        return f"agent_global:{agent_name}"
    
    async def _get_cached(self, key: str):
        """Get from cache"""
        return await self.get_cached(key)
    
    async def _set_cached(self, key: str, value):
        """Set in cache"""
        return await self.set_cached(key, value)
    
    async def _invalidate(self, key: str):
        """Invalidate cache key"""
        return await self.delete_cached(key)
    
    async def retrieve_memories(self, user_id, agent_name, context=None, top_n=10):
        key = self._cache_key(user_id, agent_name)
        cached = await self._get_cached(key)
        if cached:
            return cached

        memories = await super().retrieve_memories(user_id, agent_name, context, top_n=top_n)
        await self._set_cached(key, memories)
        return memories

    async def _direct_store(self, user_id, agent_name, memory_type, content, importance=5):
        """Direct store without queueing - used by batch processor"""
        await self.ensure_ready()
        return await super().store_memory(user_id, agent_name, memory_type, content, importance)
    
    async def store_memory(self, user_id, agent_name, memory_type, content, importance=5):
        await self.ensure_ready()
        if self.task_queue:
            await self.task_queue.enqueue(
                'memory_store',
                {
                    'user_id': user_id,
                    'agent_name': agent_name,
                    'memory_type': memory_type,
                    'content': content,
                    'importance': importance
                },
                Priority.LOW if importance < 7 else Priority.NORMAL
            )
        await self._invalidate(self._cache_key(user_id, agent_name))
        return await super().store_memory(user_id, agent_name, memory_type, content, importance)
        
    async def get_global_patterns(self, agent_name):
        key = self._global_key(agent_name)
        cached = await self._get_cached(key)
        if cached:
            return cached

        patterns = await super().get_global_patterns(agent_name)
        await self._set_cached(key, patterns)
        return patterns

    async def store_global_pattern(self, agent_name, pattern_key, value):
        await super().store_global_pattern(agent_name, pattern_key, value)
        await self._invalidate(self._global_key(agent_name))
