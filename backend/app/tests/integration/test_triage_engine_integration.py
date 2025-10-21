"""Integration tests for TriageEngineWithRedisMixin."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

class TestTriageEngineIntegration:
    """Integration tests for TriageEngineWithRedisMixin."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, triage_engine):
        """Test TriageEngine initialization with Redis."""
        assert triage_engine.redis is not None
        assert triage_engine.redis.namespace == "test-namespace"
        
        # Verify Redis is connected by making a real ping
        assert await triage_engine.redis._client.ping() is True
    
    @pytest.mark.asyncio
    async def test_cache_get_default_onboarding(self, triage_engine):
        """Test caching of onboarding data."""
        test_data = {"user": "test_user", "settings": {"theme": "dark"}}
        
        # Mock the producer function
        mock_producer = AsyncMock(return_value=test_data)
        
        # First call - should call producer and cache the result
        result = await triage_engine.cache_get_default_onboarding(mock_producer)
        assert result == test_data
        mock_producer.assert_called_once()
        
        # Reset mock for second call
        mock_producer.reset_mock()
        
        # Second call - should get from cache, not call producer
        result = await triage_engine.cache_get_default_onboarding(mock_producer)
        assert result == test_data
        mock_producer.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_metrics_template(self, triage_engine):
        """Test caching of metrics templates."""
        template_id = "test_template"
        test_template = {"name": "Test Template", "metrics": ["cpu", "memory"]}
        
        # Mock the producer function
        mock_producer = AsyncMock(return_value=test_template)
        
        # First call - should call producer and cache the result
        result = await triage_engine.cache_metrics_template(template_id, mock_producer)
        assert result == test_template
        mock_producer.assert_called_once()
        
        # Reset mock for second call
        mock_producer.reset_mock()
        
        # Second call - should get from cache, not call producer
        result = await triage_engine.cache_metrics_template(template_id, mock_producer)
        assert result == test_template
        mock_producer.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_redis_unavailable(self, triage_engine_class):
        """Test behavior when Redis is unavailable."""
        # Simulate Redis connection failure
        with patch('redis.asyncio.Redis', side_effect=ConnectionError("Redis unavailable")):
            engine = triage_engine_class(
                redis_url="redis://unreachable:6379",
                cache_namespace="test"
            )
            
            # Should not raise, just log a warning
            await engine.initialize()
            
            # Should still work with fallback to producer
            test_data = {"key": "value"}
            producer = AsyncMock(return_value=test_data)
            result = await engine.cache_get_default_onboarding(producer)
            
            assert result == test_data
            producer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, triage_engine):
        """Test Redis health check endpoint."""
        health = triage_engine.get_redis_health()
        
        assert "status" in health
        assert "circuit_breaker" in health
        assert "namespace" in health
        assert health["namespace"] == "test-namespace"
        assert health["circuit_breaker"]["state"] == "closed"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, triage_engine_class):
        """Test context manager usage."""
        async with triage_engine_class(
            redis_url="redis://localhost:6379/15",
            cache_namespace="context-test"
        ) as engine:
            assert engine.redis is not None
            # Verify Redis is connected by making a real ping
            assert await engine.redis._client.ping() is True
