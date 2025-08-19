import asyncio
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_memory_service import AgentMemoryService
from .memory_cache_mixin import MemoryCacheMixin


class AgentMemoryServiceWithCache(MemoryCacheMixin, AgentMemoryService):
    def __init__(self, *args, redis_url="redis://localhost:6379", cache_ttl=300, **kwargs):
        MemoryCacheMixin.__init__(self, redis_url=redis_url, cache_ttl=cache_ttl)
        AgentMemoryService.__init__(self, *args, **kwargs)

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
