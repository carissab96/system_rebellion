import asyncio
import logging
from typing import Any, Dict, Optional, Callable, Awaitable
from .enhanced_redis import EnhancedRedisCache, RedisUnavailable

class TriageEngineWithRedisMixin:
    def __init__(
        self, 
        *args, 
        redis_url: str = "redis://localhost", 
        cache_namespace: str = "hawk", 
        max_concurrent_db_tasks: int = 10,
        redis_max_connections: int = 20,
        redis_socket_timeout: int = 5,
        redis_connect_timeout: int = 5,
        **kwargs
    ):
        """Initialize the Triage Engine with Redis caching capabilities.
        
        Args:
            redis_url: Redis connection URL
            cache_namespace: Prefix for all Redis keys
            max_concurrent_db_tasks: Maximum concurrent database operations
            redis_max_connections: Maximum Redis connections in the pool
            redis_socket_timeout: Socket timeout in seconds
            redis_connect_timeout: Connection timeout in seconds
        """
        super().__init__(*args, **kwargs)
        self.logger = getattr(self, "logger", logging.getLogger(self.__class__.__name__))
        
        # Initialize enhanced Redis client
        self.redis = EnhancedRedisCache(
            url=redis_url,
            namespace=cache_namespace,
            max_connections=redis_max_connections,
            socket_timeout=redis_socket_timeout,
            socket_connect_timeout=redis_connect_timeout,
            logger=self.logger
        )
        
        # App-level throttle for DB-heavy work
        self._db_semaphore = asyncio.Semaphore(max_concurrent_db_tasks)

    async def initialize(self):
        """Initialize the engine and Redis connection."""
        # Call parent's initialize if it exists
        base_init = getattr(super(), "initialize", None)
        if asyncio.iscoroutinefunction(base_init):
            await base_init()
        elif callable(base_init):
            base_init()

        # Connect to Redis
        try:
            await self.redis.connect()
            self.logger.info(
                "Redis connected for namespace '%s'. Circuit state: %s", 
                self.redis.namespace,
                self.redis.get_circuit_state()['state']
            )
        except RedisUnavailable as e:
            self.logger.warning("Redis unavailable: %s. Operating without cache.", e)

    # ---------- Caching Helpers ----------
    
    async def cache_get_default_onboarding(
        self, 
        producer: Callable[[], Awaitable[Dict]] | Callable[[], Dict], 
        ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Get onboarding data from cache or generate it using the producer.
        
        Args:
            producer: Function that generates the onboarding data
            ttl_seconds: Time-to-live in seconds for the cached data
            
        Returns:
            Cached or newly generated onboarding data
        """
        key = "onboarding:defaults:v1"
        try:
            return await self.redis.get_or_set_json(key, producer, ttl=ttl_seconds)
        except Exception as e:
            self.logger.warning(
                "Cache miss/failure for %s (%s) -> falling back to producer", 
                key, e
            )
            if asyncio.iscoroutinefunction(producer):
                return await producer()
            return producer()

    async def cache_metrics_template(
        self, 
        template_id: str, 
        producer: Callable[[], Awaitable[Dict]] | Callable[[], Dict], 
        ttl_seconds: int = 600
    ) -> Dict[str, Any]:
        """Get metrics template from cache or generate it using the producer.
        
        Args:
            template_id: ID of the metrics template
            producer: Function that generates the template
            ttl_seconds: Time-to-live in seconds for the cached template
            
        Returns:
            Cached or newly generated metrics template
        """
        key = f"metrics:template:{template_id}:v1"
        try:
            return await self.redis.get_or_set_json(key, producer, ttl=ttl_seconds)
        except Exception as e:
            self.logger.warning(
                "Cache miss/failure for %s (%s) -> falling back to producer", 
                key, e
            )
            if asyncio.iscoroutinefunction(producer):
                return await producer()
            return producer()

    # ---------- DB Task Throttling ----------
    async def _throttled_db_task(self, coro):
        """Run a DB task with concurrency control"""
        async with self._db_semaphore:
            return await coro

    # ---------- Circuit Breaker Status ----------
    
    def get_redis_health(self) -> Dict[str, Any]:
        """Get Redis health and circuit breaker status.
        
        Returns:
            Dictionary containing Redis health information
        """
        return {
            "status": "ok" if hasattr(self.redis, '_client') and self.redis._client is not None else "disconnected",
            "circuit_breaker": self.redis.get_circuit_state(),
            "namespace": self.redis.namespace
        }

    # ---------- Context Manager Support ----------
    
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close Redis connection
        if hasattr(self, 'redis') and hasattr(self.redis, 'close'):
            await self.redis.close()
            
        # Call parent's __aexit__ if it exists
        base_exit = getattr(super(), "__aexit__", None)
        if base_exit is not None:
            if asyncio.iscoroutinefunction(base_exit):
                await base_exit(exc_type, exc_val, exc_tb)
            else:
                base_exit(exc_type, exc_val, exc_tb)

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
