from typing import Optional, TypeVar, Any, Dict, Union, Type
import asyncio
import logging
import time
import redis.asyncio as aioredis
from redis.exceptions import (
    RedisError, ConnectionError, TimeoutError, 
    ResponseError
)

from app.services.memory_redis_patch.health import RedisHealthMonitor

logger = logging.getLogger(__name__)

# Type variable for Redis client
Redis = TypeVar('Redis', bound=aioredis.Redis)

class ConnectionPoolExhaustedError(RedisError):
    """Raised when no connections are available in the pool"""
    pass
# Add this to redis_client.py before the RedisClient class
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
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

    def can_execute(self):
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

    def get_state(self):
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure
        }
class RedisClient:
    _instance: Optional['RedisClient'] = None
    _client: Optional[aioredis.Redis] = None
    _lock = asyncio.Lock()
    _connection_params: Dict[str, Any] = {}
    _last_connection_attempt: float = 0
    _connection_timeout: int = 5  # seconds
    _max_retries: int = 3
    _retry_delay: float = 0.1  # seconds
    _circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
    
    def __init__(self):
        self.client = None
        self._closed = False
        self._health_check_task = None
        self._circuit_breaker = CircuitBreaker()

    @classmethod
    async def get_instance(
        cls, 
        redis_url: str = "redis://localhost:6379",
        max_connections: int = 20,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30
    ) -> 'RedisClient':
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                cls._connection_params = {
                    'url': redis_url,
                    'max_connections': max_connections,
                    'socket_timeout': socket_timeout,
                    'socket_connect_timeout': socket_connect_timeout,
                    'retry_on_timeout': retry_on_timeout,
                    'health_check_interval': health_check_interval
                }
                await cls._connect()
                # Start health check
                cls._instance._health_check_task = asyncio.create_task(
                    cls._instance._health_check_loop()
                )
        return cls._instance

    @classmethod
    async def _connect(cls):
        """Establish connection to Redis with retry logic"""
        retry_count = 0
        last_error = None
        
        while retry_count < cls._max_retries:
            try:
                if time.time() - cls._last_connection_attempt < 1.0:
                    await asyncio.sleep(cls._retry_delay)
                
                cls._last_connection_attempt = time.time()
                
                cls._client = aioredis.from_url(
                    cls._connection_params['url'],
                    decode_responses=True,
                    encoding="utf-8",
                    max_connections=cls._connection_params['max_connections'],
                    socket_timeout=cls._connection_params['socket_timeout'],
                    socket_connect_timeout=cls._connection_params['socket_connect_timeout'],
                    retry_on_timeout=cls._connection_params['retry_on_timeout'],
                    health_check_interval=cls._connection_params['health_check_interval'],
                    
                )
                
                # Test the connection
                await cls._client.ping()
                cls._instance.client = cls._client
                cls._instance._closed = False
                logger.info("Successfully connected to Redis")
                return
                
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                retry_count += 1
                wait_time = min(2 ** retry_count, 10)  # Exponential backoff, max 10s
                logger.warning(
                    f"Connection attempt {retry_count}/{cls._max_retries} failed. "
                    f"Retrying in {wait_time}s... Error: {str(e)}"
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error connecting to Redis: {str(e)}")
                break
        
        raise ConnectionError(
            f"Failed to connect to Redis after {cls._max_retries} attempts. "
            f"Last error: {str(last_error)}"
        )

    @staticmethod
    async def _handle_connection_error(error: Exception, retry_count: int, timeout: float) -> bool:
        """Handle connection errors with custom logic"""
        logger.warning(f"Connection error (attempt {retry_count}): {str(error)}")
        if retry_count >= 3:
            logger.error("Max retries reached, giving up")
            return False
        return True

    async def _health_check_loop(self):
        """Background task to monitor Redis connection health"""
        while not self._closed:
            try:
                if self.client and not self._closed:
                    await self.client.ping()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Redis health check failed: {str(e)}")
                if not self._closed:
                    await self._reconnect()

    async def _reconnect(self):
        """Attempt to reconnect to Redis"""
        logger.info("Attempting to reconnect to Redis...")
        try:
            await self.close()
            await self._connect()
        except Exception as e:
            logger.error(f"Reconnection failed: {str(e)}")

    @classmethod
    async def close_instance(cls):
        """Safely close Redis connection and cleanup"""
        if cls._instance:
            try:
                cls._instance._closed = True
                if cls._instance._health_check_task:
                    cls._instance._health_check_task.cancel()
                    try:
                        await cls._instance._health_check_task
                    except asyncio.CancelledError:
                        pass
                
                if cls._client:
                    await cls._client.close()
                    logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error during Redis shutdown: {str(e)}")
            finally:
                cls._client = None
                cls._instance = None
                cls._connection_params = {}

    def __getattr__(self, name):
        """Delegate attribute access to the Redis client"""
        if self.client is None:
            raise ConnectionError("Redis client is not connected")
        return getattr(self.client, name)

    @classmethod
    async def execute_command(cls, *args, **kwargs):
        """Execute a Redis command with circuit breaker protection"""
        if not cls._circuit_breaker.can_execute():
            raise RedisError("Circuit breaker is open")
            
        try:
            result = await cls._client.execute_command(*args, **kwargs)
            cls._circuit_breaker.record_success()
            return result
        except (ConnectionError, TimeoutError) as e:
            cls._circuit_breaker.record_failure()
            raise
        except Exception as e:
            raise

    @classmethod
    def get_circuit_state(cls):
        """Get the current circuit breaker state"""
        return cls._circuit_breaker.get_state()