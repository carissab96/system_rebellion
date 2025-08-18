
import json
import logging
from typing import Any, Callable, Optional, Awaitable
import asyncio

try:
    import redis.asyncio as aioredis  # redis>=4.2
except Exception as e:  # pragma: no cover
    aioredis = None

class RedisUnavailable(RuntimeError):
    pass

class RedisCache:
    """
    Lightweight async Redis helper with:
    - JSON (de)serialization helpers
    - get_or_set pattern with TTL
    - graceful fallback if Redis is unavailable (optional)
    """
    def __init__(self, url: str = "redis://localhost", namespace: str = "hawk", logger: Optional[logging.Logger] = None):
        self.url = url
        self.namespace = namespace.strip(":")
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._client = None

    async def connect(self):
        if aioredis is None:
            raise RedisUnavailable("redis-py (redis.asyncio) not installed. Try: pip install redis")
        if self._client is None:
            self._client = aioredis.from_url(self.url, decode_responses=True, health_check_interval=15)

    def _k(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Optional[str]:
        await self.connect()
        return await self._client.get(self._k(key))

    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        await self.connect()
        if ttl:
            await self._client.set(self._k(key), value, ex=ttl)
        else:
            await self._client.set(self._k(key), value)

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception as e:
            self.logger.warning("Failed to json.loads for key %s: %s", key, e)
            return None

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None):
        try:
            raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        except TypeError:
            # fallback: stringify non-JSON-serializable
            raw = json.dumps(str(value))
        await self.set(key, raw, ttl)

    async def get_or_set_json(self, key: str, producer: Callable[[], Awaitable[Any]] | Callable[[], Any], ttl: int = 60):
        """
        Fetch JSON value from cache, compute via producer on miss, store, and return.
        Producer may be sync or async.
        """
        cached = await self.get_json(key)
        if cached is not None:
            return cached

        if asyncio.iscoroutinefunction(producer):
            value = await producer()
        else:
            value = producer()

        await self.set_json(key, value, ttl)
        return value

    # Simple rate limiter: token bucket per key
    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Returns True if operation allowed under (limit/window), False otherwise.
        """
        await self.connect()
        pipe = self._client.pipeline()
        k = self._k(f"rate:{key}")
        # increment and set expiry if new
        pipe.incr(k, 1)
        pipe.expire(k, window_seconds)
        count, _ = await pipe.execute()
        return int(count) <= int(limit)

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None
