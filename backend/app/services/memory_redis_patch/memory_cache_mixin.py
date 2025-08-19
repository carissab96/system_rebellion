import json
import redis.asyncio as aioredis

class MemoryCacheMixin:
    def __init__(self, redis_url="redis://localhost:6379", cache_ttl=300):
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

    async def _get_cached(self, key):
        redis = await self._get_redis()
        val = await redis.get(key)
        return json.loads(val) if val else None

    async def _set_cached(self, key, data):
        redis = await self._get_redis()
        await redis.set(key, json.dumps(data), ex=self.cache_ttl)

    async def _invalidate(self, key):
        redis = await self._get_redis()
        await redis.delete(key)
