"""Unit tests for EnhancedRedisCache"""
import pytest
import json
import asyncio

from app.ai_agents.sir_hawkington.hawk_redis_patch.enhanced_redis import (
    EnhancedRedisCache,
    RedisUnavailable,
    CircuitBreaker
)

class TestEnhancedRedisCache:
    """Test suite for EnhancedRedisCache."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, redis_client):
        """Test successful Redis connection."""
        assert redis_client._client is not None
        assert await redis_client._client.ping() is True
    
    @pytest.mark.asyncio
    async def test_set_get(self, redis_client):
        """Test basic set and get operations."""
        await redis_client.set("test_key", "test_value")
        result = await redis_client.get("test_key")
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_set_get_json(self, redis_client):
        """Test JSON serialization."""
        test_data = {"key": "value", "number": 42}
        await redis_client.set_json("json_key", test_data)
        result = await redis_client.get_json("json_key")
        assert result == test_data
    
    @pytest.mark.asyncio
    async def test_get_or_set(self, redis_client):
        """Test get_or_set with producer function."""
        async def producer():
            return "produced_value"
            
        # First call should call producer
        result = await redis_client.get_or_set("new_key", producer)
        assert result == "produced_value"
        
        # Second call should get from cache
        result = await redis_client.get("new_key")
        assert result == "produced_value"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """Test circuit breaker functionality with real connection failures."""
        # Create a client pointing to a non-existent Redis server
        bad_client = EnhancedRedisCache(
            url="redis://localhost:9999",  # Non-existent Redis port
            namespace="test"
        )
        
        # Configure circuit breaker with lower thresholds for testing
        bad_client._circuit_breaker.failure_threshold = 1
        bad_client._circuit_breaker.recovery_timeout = 1
        
        try:
            # First failure - should trigger circuit breaker with real connection error
            with pytest.raises(RedisUnavailable):
                await bad_client.execute_command('GET', 'test')
    
            # Verify circuit is open after real failure
            assert bad_client._circuit_breaker.state == "open"
    
            # Should fail fast with RedisUnavailable (circuit breaker prevents execution)
            with pytest.raises(RedisUnavailable):
                await bad_client.execute_command('GET', 'any_key')
    
            # Wait for recovery timeout
            await asyncio.sleep(1.5)
    
            # Check if circuit breaker can execute (this triggers state transition)
            can_exec = bad_client._circuit_breaker.can_execute()
            assert can_exec is True
            
            # Should be in half-open state now after can_execute() call
            assert bad_client._circuit_breaker.state == "half-open"
    
            # Try again with bad connection - should fail and reopen circuit
            with pytest.raises(RedisUnavailable):
                await bad_client.execute_command('GET', 'test')
            
            # Circuit should be open again after failure in half-open state
            assert bad_client._circuit_breaker.state == "open"
            
        finally:
            # Clean up
            if bad_client._client:
                await bad_client.close()


    class TestCircuitBreaker:
        """Test suite for CircuitBreaker class."""
    
    def test_initial_state(self):
        """Test initial circuit breaker state."""
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb.failures == 0
        assert cb.last_failure is None
    
    def test_record_failure(self):
        """Test recording failures."""
        cb = CircuitBreaker(failure_threshold=2)
        
        # First failure
        cb.record_failure()
        assert cb.state == "closed"
        assert cb.failures == 1
        
        # Second failure should trip the circuit
        cb.record_failure()
        assert cb.state == "open"
    
    def test_record_success(self):
        """Test recording success resets the circuit."""
        cb = CircuitBreaker()
        cb.record_failure()
        cb.record_success()
        
        assert cb.state == "closed"
        assert cb.failures == 0
    
    def test_can_execute(self):
        """Test can_execute method."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        
        # Initially should be able to execute
        assert cb.can_execute() is True
        
        # After failure, circuit should be open
        cb.record_failure()
        assert cb.can_execute() is False
        
        # After recovery timeout, should move to half-open
        import time
        time.sleep(0.2)
        assert cb.can_execute() is True
        assert cb.state == "half-open"
