import json
import logging
import time
import asyncio
from typing import Any, Callable, Optional, Awaitable, TypeVar, Dict
import redis.asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError, TimeoutError, ResponseError

T = TypeVar('T')

class RedisUnavailable(RuntimeError):
    """Raised when Redis is not available or misconfigured"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern for Redis operations"""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"  # "closed", "open", or "half-open"
        self.last_failure = None

    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        elif self.state == "open":
            # Check if we should move to half-open
            if (time.time() - self.last_failure) > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def get_state(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure
        }

class EnhancedRedisCache:
    """Enhanced Redis client with circuit breaking, connection pooling, and caching patterns.
    
    Combines the robustness of the RedisClient with the simplicity of the original RedisCache.
    """
    def __init__(
        self, 
        url: str = "redis://localhost", 
        namespace: str = "hawk",
        max_connections: int = 20,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        self.url = url
        self.namespace = namespace.strip(":")
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._client = None
        self._circuit_breaker = CircuitBreaker()
        self._connection_params = {
            'max_connections': max_connections,
            'socket_timeout': socket_timeout,
            'socket_connect_timeout': socket_connect_timeout,
            'retry_on_timeout': retry_on_timeout,
            'health_check_interval': health_check_interval
        }
        self._closed = False

    def _k(self, key: str) -> str:
        """Add namespace prefix to key"""
        return f"{self.namespace}:{key}"

    async def connect(self):
        """Initialize Redis connection"""
        if self._client is None or self._closed:
            if not self._circuit_breaker.can_execute():
                raise RedisUnavailable("Circuit breaker is open")
                
            try:
                self._client = aioredis.from_url(
                    self.url,
                    decode_responses=True,
                    encoding="utf-8",
                    **self._connection_params
                )
                # Test connection
                await self._client.ping()
                self._closed = False
                self._circuit_breaker.record_success()
                self.logger.info(f"Connected to Redis at {self.url}")
            except (ConnectionError, TimeoutError) as e:
                self._circuit_breaker.record_failure()
                self.logger.error(f"Redis connection failed: {e}")
                raise RedisUnavailable(f"Failed to connect to Redis: {e}")

    async def close(self):
        """Close the Redis connection"""
        if self._client and not self._closed:
            await self._client.aclose()
            self._closed = True
            self.logger.info("Redis connection closed")

    async def execute_command(self, *args, **kwargs) -> Any:
        """Execute a Redis command with circuit breaker protection"""
        if not self._circuit_breaker.can_execute():
            raise RedisUnavailable("Circuit breaker is open")
            
        try:
            await self.connect()
            result = await self._client.execute_command(*args, **kwargs)
            self._circuit_breaker.record_success()
            return result
        except (ConnectionError, TimeoutError) as e:
            self._circuit_breaker.record_failure()
            self.logger.error(f"Redis command failed: {e}")
            raise RedisUnavailable(f"Redis operation failed: {e}")

    # ---- High-level caching methods ----

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value from Redis"""
        try:
            value = await self.execute_command('GET', self._k(key))
            return value if value is not None else default
        except RedisUnavailable:
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in Redis with optional TTL"""
        try:
            if ttl:
                return await self.execute_command('SET', self._k(key), value, 'EX', ttl)
            return await self.execute_command('SET', self._k(key), value)
        except RedisUnavailable:
            return False

    async def get_json(self, key: str, default: Any = None) -> Any:
        """Get a JSON value from Redis"""
        value = await self.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON in cache for key: {key}")
            return default

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a JSON value in Redis"""
        try:
            return await self.set(key, json.dumps(value), ttl=ttl)
        except (TypeError, OverflowError) as e:
            self.logger.error(f"Failed to serialize value for key {key}: {e}")
            return False

    async def get_or_set(
        self, 
        key: str, 
        producer: Callable[[], Awaitable[Any]] | Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get a value from cache, or set it using the producer function if not found"""
        # Try to get from cache first
        value = await self.get(key)
        if value is not None:
            return value
            
        # Not in cache, call producer
        try:
            if asyncio.iscoroutinefunction(producer):
                value = await producer()
            else:
                value = producer()
                
            if value is not None:
                await self.set(key, value, ttl=ttl)
                
            return value
        except Exception as e:
            self.logger.warning(f"Producer failed for key {key}: {e}")
            raise

    async def get_or_set_json(
        self, 
        key: str, 
        producer: Callable[[], Awaitable[Any]] | Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get a JSON value from cache, or set it using the producer function if not found"""
        # Try to get from cache first
        value = await self.get_json(key)
        if value is not None:
            return value
            
        # Not in cache, call producer
        try:
            if asyncio.iscoroutinefunction(producer):
                value = await producer()
            else:
                value = producer()
                
            if value is not None:
                await self.set_json(key, value, ttl=ttl)
                
            return value
        except Exception as e:
            self.logger.warning(f"JSON producer failed for key {key}: {e}")
            raise

    # ---- Circuit breaker status ----
    
    def get_circuit_state(self) -> Dict[str, Any]:
        """Get the current circuit breaker state"""
        return self._circuit_breaker.get_state()

    # ---- Context manager support ----
    
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
