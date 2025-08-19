import inspect
# from app.utils.redis_compat import redis

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_memory_service import AgentMemoryService
from .memory_cache_mixin import MemoryCacheMixin


class AgentMemoryServiceWithCache(AgentMemoryService):
    def __init__(self, *args, **kwargs):
        # Pull wrapper-only kwargs FIRST so they don't reach the base class
        self.redis_url   = kwargs.pop("redis_url", None)
        self._db_getter  = kwargs.pop("db_getter", None)   # may be async or sync callable
        db_session       = kwargs.pop("db_session", None)  # optional pre-built session

        # Hand only what the base expects
        super().__init__(db_session)

        # If caller gave us a getter but no session, prep for lazy init
        self._pending_db_coro = None
        if self.db is None and self._db_getter is not None:
            maybe = self._db_getter()
            # don't block here; store coroutine for later
            if inspect.isawaitable(maybe):
                self._pending_db_coro = maybe
            else:
                self.db = maybe  # sync factory returned a ready session

    async def ensure_ready(self):
        """Initialize DB session lazily in the event loop."""
        if self.db is None and self._pending_db_coro is not None:
            self.db = await self._pending_db_coro
            self._pending_db_coro = None

    async def retrieve_memories(self, user_id, agent_name, context=None, top_n=10):
        key = self._cache_key(user_id, agent_name)
        cached = await self._get_cached(key)
        if cached:
            return cached

        memories = await super().retrieve_memories(user_id, agent_name, context, top_n=top_n)
        await self._set_cached(key, memories)
        return memories

    async def store_memory(self, user_id, agent_name, memory_type, content, importance=5):
        await super().store_memory(user_id, agent_name, memory_type, content, importance)
        await self._invalidate(self._cache_key(user_id, agent_name))

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
