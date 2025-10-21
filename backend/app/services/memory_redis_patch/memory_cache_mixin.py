import redis.asyncio as aioredis
import asyncio
import json
import logging
from typing import Any, Optional, Dict, TypeVar, Type, Callable, Awaitable
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')

def handle_redis_errors(max_retries: int = 3, backoff_factor: float = 0.1):
    """
    Decorator to handle Redis errors with retry logic and automatic reconnection.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Backoff factor for exponential delay between retries
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except (aioredis.ConnectionError, aioredis.TimeoutError) as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}")
                        break
                    
                    # Exponential backoff
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Redis connection error in {func.__name__} (attempt {attempt + 1}/{max_retries}): "
                        f"{str(e)}. Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    
                    # Attempt to reconnect
                    if hasattr(self, '_redis') and self._redis:
                        try:
                            await self._redis.ping()
                        except:
                            await self._get_redis()  # Reconnect
                except aioredis.RedisError as e:
                    logger.error(f"Redis error in {func.__name__}: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    raise
            
            # If we get here, all retries failed
            error_msg = f"Operation {func.__name__} failed after {max_retries} attempts"
            logger.error(f"{error_msg}. Last error: {str(last_exception)}")
            raise type(last_exception)(f"{error_msg}: {str(last_exception)}") from last_exception
        return wrapper
    return decorator

class MemoryCacheMixin:
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        cache_ttl: int = 300,
        max_connections: int = 10,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5
    ):
        self.redis_url = redis_url
        self.cache_ttl = cache_ttl
        self._redis = None
        self._redis_lock = asyncio.Lock()
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout

    async def _get_redis(self) -> aioredis.Redis:
        """Thread-safe Redis client getter with connection pooling"""
        if self._redis is None:
            async with self._redis_lock:
                if self._redis is None:  # Double-checked locking
                    try:
                        self._redis = aioredis.from_url(
                            self.redis_url,
                            decode_responses=True,
                            max_connections=self.max_connections,
                            socket_timeout=self.socket_timeout,
                            socket_connect_timeout=self.socket_connect_timeout,
                            retry_on_timeout=True,
                            health_check_interval=30
                        )
                        # Test the connection
                        await self._redis.ping()
                    except Exception as e:
                        self._redis = None
                        logger.error(f"Failed to connect to Redis: {str(e)}")
                        raise
        return self._redis

    @handle_redis_errors()
    async def get_cached(self, key: str) -> Optional[Any]:
        """Get a value from cache with error handling"""
        redis = await self._get_redis()
        value = await redis.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in cache for key: {key}")
                await redis.delete(key)  # Clean up invalid data
        return None

    @handle_redis_errors()
    async def set_cached(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value in cache with error handling"""
        if value is None:
            return False
            
        redis = await self._get_redis()
        ttl = ttl if ttl is not None else self.cache_ttl
        
        try:
            serialized = json.dumps(value)
            return await redis.set(
                key, 
                serialized, 
                ex=timedelta(seconds=ttl) if ttl > 0 else None
            )
        except (TypeError, OverflowError) as e:
            logger.error(f"Failed to serialize value for key {key}: {str(e)}")
            return False

    @handle_redis_errors()
    async def delete_cached(self, *keys: str) -> int:
        """Delete one or more keys from cache"""
        if not keys:
            return 0
        redis = await self._get_redis()
        return await redis.delete(*keys)

    @handle_redis_errors()
    async def clear_cache(self, pattern: str = "*") -> int:
        """Clear cache entries matching a pattern"""
        redis = await self._get_redis()
        keys = await redis.keys(pattern)
        if keys:
            return await redis.delete(*keys)
        return 0

    async def close(self):
        """Close the Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None