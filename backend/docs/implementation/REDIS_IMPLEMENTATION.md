# Redis Implementation Guide

## Overview
This document covers the Redis implementation details, including the enhanced Redis client, circuit breaker pattern, and integration with the Triage Engine.

## Table of Contents
1. [Features](#features)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Circuit Breaker](#circuit-breaker)
5. [Health Monitoring](#health-monitoring)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Features

### EnhancedRedisCache
- Connection pooling
- Circuit breaker pattern
- Automatic reconnection
- Health monitoring
- JSON serialization
- Namespace support
- Context manager support

### TriageEngine Integration
- Automatic Redis initialization
- Caching helpers
- Health monitoring endpoint
- Graceful degradation

## Setup

### Dependencies
```bash
pip install redis prometheus-client
```

### Configuration
```python
from app.ai_agents.sir_hawkington.hawk_redis_patch.enhanced_redis import EnhancedRedisCache

redis = EnhancedRedisCache(
    url="redis://localhost:6379",
    namespace="hawk",
    max_connections=20,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)
```

## Usage

### Basic Operations
```python
# Set a value
await redis.set("key", "value", ttl=60)

# Get a value
value = await redis.get("key")

# JSON operations
await redis.set_json("user:1", {"name": "Sir Hawkington"})
user = await redis.get_json("user:1")

# Get or set pattern
data = await redis.get_or_set(
    "expensive:data",
    producer=lambda: expensive_database_query(),
    ttl=300  # 5 minutes
)
```

### TriageEngine Integration
```python
class MyTriageEngine(TriageEngineWithRedisMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            redis_url="redis://localhost:6379",
            cache_namespace="myapp",
            max_concurrent_db_tasks=10,
            **kwargs
        )

# Get Redis health status
health = engine.get_redis_health()
```

## Circuit Breaker

The circuit breaker has three states:
1. **Closed**: Normal operation
2. **Open**: Circuit is open, failing fast
3. **Half-Open**: Testing if service has recovered

### Configuration
```python
# Default values
circuit_breaker = CircuitBreaker(
    failure_threshold=5,    # Number of failures before opening
    recovery_timeout=30     # Seconds before trying to recover
)
```

## Health Monitoring

### Endpoint
```python
@app.get("/health/redis")
async def get_redis_health():
    return engine.get_redis_health()
```

### Response Format
```json
{
  "status": "ok",
  "circuit_breaker": {
    "state": "closed",
    "failures": 0,
    "last_failure": null
  },
  "namespace": "hawk"
}
```

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, patch
from app.ai_agents.sir_hawkington.hawk_redis_patch.enhanced_redis import EnhancedRedisCache

@pytest.mark.asyncio
async def test_redis_set_get():
    redis = EnhancedRedisCache()
    await redis.connect()
    
    # Test set and get
    await redis.set("test_key", "test_value")
    value = await redis.get("test_key")
    assert value == "test_value"
    
    await redis.close()
```

### Integration Tests
```python
@pytest.mark.integration
async def test_circuit_breaker():
    redis = EnhancedRedisCache()
    
    # Simulate failures
    with patch.object(redis, '_client', side_effect=ConnectionError):
        for _ in range(5):  # failure_threshold
            with pytest.raises(RedisUnavailable):
                await redis.get("test")
    
    # Circuit should be open now
    assert redis.get_circuit_state()["state"] == "open"
    
    await redis.close()
```

## Troubleshooting

### Common Issues

#### Connection Issues
1. **Error**: `RedisUnavailable: Failed to connect to Redis`
   - Check if Redis server is running
   - Verify connection URL and credentials
   - Check network connectivity

#### Circuit Breaker Tripped
1. **Symptom**: All Redis commands failing with `CircuitBreakerOpen`
   - Check Redis server status
   - Monitor circuit breaker state
   - Wait for recovery timeout or reset circuit breaker

#### Performance Issues
1. **Symptom**: High latency or timeouts
   - Check Redis server load
   - Review connection pool settings
   - Monitor network latency

### Logs
Enable debug logging for detailed information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Connection Management**
   - Always use context managers or explicit close()
   - Set appropriate timeouts
   - Monitor connection pool usage

2. **Error Handling**
   - Always handle RedisUnavailable
   - Implement fallback mechanisms
   - Log errors with context

3. **Performance**
   - Use pipelining for multiple commands
   - Set appropriate TTLs
   - Monitor Redis metrics

## Monitoring

### Metrics
- `redis_commands_total`: Total number of commands
- `redis_errors_total`: Number of errors
- `redis_connection_pool_size`: Current pool size
- `redis_circuit_state`: Current circuit breaker state

### Alerts
- Circuit breaker open
- High error rate
- Connection pool exhaustion
- High latency
