
import asyncio
import logging
from typing import Any, Dict, Optional, Callable, Awaitable
from .redis_cache import RedisCache, RedisUnavailable

# This module shows how to wire Redis into your existing Triage Engine
# without rewriting your agents. Drop-in patterns:
# - cache expensive onboarding lookups
# - throttle concurrent DB-heavy tasks
# - graceful fallback if Redis is down

class TriageEngineWithRedisMixin:
    def __init__(self, *args, redis_url: str = "redis://localhost", cache_namespace: str = "hawk", max_concurrent_db_tasks: int = 10, **kwargs):
        super().__init__(*args, **kwargs)  # let your concrete engine init
        self.logger = getattr(self, "logger", logging.getLogger(self.__class__.__name__))
        self.redis = RedisCache(url=redis_url, namespace=cache_namespace, logger=self.logger)
        # App-level throttle for DB-heavy work (protects pool under spikes)
        self._db_semaphore = asyncio.Semaphore(max_concurrent_db_tasks)

    async def initialize(self):
        # Call the concrete engine's initialize first if it exists
        base_init = getattr(super(), "initialize", None)
        if asyncio.iscoroutinefunction(base_init):
            await base_init()
        elif callable(base_init):
            base_init()

        # Connect Redis (non-fatal if missing)
        try:
            await self.redis.connect()
            self.logger.info("Redis connected for namespace '%s'.", self.redis.namespace)
        except RedisUnavailable as e:
            self.logger.warning("Redis unavailable: %s. Operating without cache.", e)

    # ---------- Caching helpers ----------
    async def cache_get_default_onboarding(self, producer: Callable[[], Awaitable[Dict]] | Callable[[], Dict], ttl_seconds: int = 3600) -> Dict[str, Any]:
        key = "onboarding:defaults:v1"
        try:
            return await self.redis.get_or_set_json(key, producer, ttl=ttl_seconds)
        except Exception as e:
            self.logger.warning("Cache miss/failure for %s (%s) -> falling back to producer", key, e)
            # fallback to DB directly
            if asyncio.iscoroutinefunction(producer):
                return await producer()
            return producer()

    async def cache_metrics_template(self, template_id: str, producer: Callable[[], Awaitable[Dict]] | Callable[[], Dict], ttl_seconds: int = 600) -> Dict[str, Any]:
        key = f"metrics:template:{template_id}:v1"
        try:
            return await self.redis.get_or_set_json(key, producer, ttl=ttl_seconds)
        except Exception as e:
            self.logger.warning("Cache fail for %s: %s", key, e)
            if asyncio.iscoroutinefunction(producer):
                return await producer()
            return producer()

    # ---------- Throttled DB-heavy execution ----------
    async def run_db_heavy(self, coro_factory: Callable[[], Awaitable[Any]]):
        """
        Wrap any DB-heavy coroutine with a semaphore so we don't exceed healthy concurrency.
        Usage: await self.run_db_heavy(lambda: agent.fetch_all_metrics(user_id))
        """
        async with self._db_semaphore:
            return await coro_factory()

    # ---------- Rate limiting (surge control) ----------
    async def allow_signup_burst(self, tenant_key: str, per_10s: int = 8) -> bool:
        """
        Allow up to `per_10s` signups per 10 seconds per tenant/workspace.
        Extra requests should be queued/retried or shown a polite 'please wait'.
        """
        try:
            return await self.redis.allow(f"signup:{tenant_key}", limit=per_10s, window_seconds=10)
        except Exception as e:
            self.logger.warning("Rate limiter failed (%s). Allowing by default.", e)
            return True  # fail-open to avoid false negatives

    async def shutdown(self):
        try:
            await self.redis.close()
        except Exception:
            pass
