import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import redis.asyncio as aioredis
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

@dataclass
class RedisHealthMetrics:
    """Container for Redis health metrics"""
    is_healthy: bool = False
    latency_ms: float = 0.0
    last_check: Optional[datetime] = None
    error: Optional[str] = None
    version: Optional[str] = None
    used_memory: int = 0
    connected_clients: int = 0
    total_connections_received: int = 0
    total_commands_processed: int = 0
    keyspace_hits: int = 0
    keyspace_misses: int = 0

class RedisHealthMonitor:
    """Monitor Redis server health and collect metrics"""
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        check_interval: float = 30.0,
        timeout: float = 5.0
    ):
        self.redis = redis_client
        self.check_interval = check_interval
        self.timeout = timeout
        self.metrics = RedisHealthMetrics()
        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        
        # Prometheus metrics
        self.health_gauge = Gauge(
            'redis_health',
            'Redis health status (1=healthy, 0=unhealthy)'
        )
        self.latency_gauge = Gauge(
            'redis_latency_seconds',
            'Redis command latency in seconds'
        )
        self.memory_usage_gauge = Gauge(
            'redis_memory_usage_bytes',
            'Total memory used by Redis in bytes'
        )
        self.clients_gauge = Gauge(
            'redis_connected_clients',
            'Number of connected clients'
        )
        self.commands_processed_counter = Counter(
            'redis_commands_processed_total',
            'Total number of commands processed by Redis'
        )
        self.keyspace_hits_counter = Counter(
            'redis_keyspace_hits_total',
            'Total number of successful key lookups'
        )
        self.keyspace_misses_counter = Counter(
            'redis_keyspace_misses_total',
            'Total number of failed key lookups'
        )
        self.command_latency = Histogram(
            'redis_command_duration_seconds',
            'Redis command latency in seconds',
            ['command']
        )

    async def start(self):
        """Start the health monitoring loop"""
        if self._monitor_task is None or self._monitor_task.done():
            self._stop_event.clear()
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Redis health monitor started")

    async def stop(self):
        """Stop the health monitoring loop"""
        if self._monitor_task:
            self._stop_event.set()
            await asyncio.wait_for(self._monitor_task, timeout=5.0)
            self._monitor_task = None
            logger.info("Redis health monitor stopped")

    async def _monitor_loop(self):
        """Background task to monitor Redis health"""
        while not self._stop_event.is_set():
            try:
                await self._check_health()
            except Exception as e:
                logger.error(f"Error in Redis health check: {str(e)}")
            
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.check_interval
                )
            except asyncio.TimeoutError:
                pass

    async def _check_health(self):
        """Perform health check and update metrics"""
        start_time = time.monotonic()
        error = None
        info = {}
        
        try:
            # Check basic connectivity
            with self.command_latency.labels('PING').time():
                await asyncio.wait_for(self.redis.ping(), timeout=self.timeout)
            
            # Get server info
            with self.command_latency.labels('INFO').time():
                info_result = await asyncio.wait_for(
                    self.redis.info(),
                    timeout=self.timeout
                )
                # Redis client returns dict directly, not a string
                if isinstance(info_result, dict):
                    info = info_result
                else:
                    info = self._parse_info(info_result)
            
            # Update metrics
            latency_ms = (time.monotonic() - start_time) * 1000
            self.metrics = RedisHealthMetrics(
                is_healthy=True,
                latency_ms=latency_ms,
                last_check=datetime.now(timezone.utc),
                version=info.get('redis_version'),
                used_memory=int(info.get('used_memory', 0)),
                connected_clients=int(info.get('connected_clients', 0)),
                total_connections_received=int(info.get('total_connections_received', 0)),
                total_commands_processed=int(info.get('total_commands_processed', 0)),
                keyspace_hits=int(info.get('keyspace_hits', 0)),
                keyspace_misses=int(info.get('keyspace_misses', 0))
            )
            
            # Update Prometheus metrics
            self.health_gauge.set(1)
            self.latency_gauge.set(latency_ms / 1000)  # Convert to seconds
            self.memory_usage_gauge.set(self.metrics.used_memory)
            self.clients_gauge.set(self.metrics.connected_clients)
            self.commands_processed_counter.inc(
                max(0, self.metrics.total_commands_processed - 
                    self.commands_processed_counter._value.get())
            )
            self.keyspace_hits_counter.inc(
                max(0, self.metrics.keyspace_hits - 
                    self.keyspace_hits_counter._value.get())
            )
            self.keyspace_misses_counter.inc(
                max(0, self.metrics.keyspace_misses - 
                    self.keyspace_misses_counter._value.get())
            )
            
            logger.debug(
                f"Redis health check OK - "
                f"version={self.metrics.version} "
                f"latency={self.metrics.latency_ms:.2f}ms "
                f"memory={self.metrics.used_memory / (1024*1024):.2f}MB"
            )
            
        except asyncio.TimeoutError:
            error = "Health check timed out"
        except Exception as e:
            error = str(e)
        
        if error:
            self.metrics = RedisHealthMetrics(
                is_healthy=False,
                error=error,
                last_check=datetime.now(timezone.utc)
            )
            self.health_gauge.set(0)
            logger.warning(f"Redis health check failed: {error}")

    @staticmethod
    def _parse_info(info_str: str) -> Dict[str, Any]:
        """Parse Redis INFO command output into a dictionary"""
        result = {}
        for line in info_str.split('\r\n'):
            if line and ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                result[key] = value
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            'status': 'healthy' if self.metrics.is_healthy else 'unhealthy',
            'version': self.metrics.version,
            'latency_ms': round(self.metrics.latency_ms, 2),
            'last_check': self.metrics.last_check.isoformat() if self.metrics.last_check else None,
            'memory_used_mb': round(self.metrics.used_memory / (1024 * 1024), 2) if self.metrics.used_memory else None,
            'connected_clients': self.metrics.connected_clients,
            'error': self.metrics.error
        }