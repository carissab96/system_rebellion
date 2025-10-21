"""Test configuration and fixtures."""
import asyncio
import pytest
import pytest_asyncio
from unittest.mock import MagicMock

import os
import sys

# Add the root directory to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.ai_agents.sir_hawkington.hawk_redis_patch.enhanced_redis import EnhancedRedisCache

# Test configuration - using local Redis with DB 15 (typically safe for testing)
TEST_REDIS_URL = "redis://localhost:6379/15"
TEST_NAMESPACE = "test-namespace"

# Clean up test data before and after tests
@pytest_asyncio.fixture(autouse=True)
async def cleanup_redis():
    """Clean up Redis test database before and after each test."""
    import redis.asyncio as redis
    
    # Connect to the test database
    r = redis.Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    
    # Clean before test
    await r.flushdb()
    
    yield  # Run the test
    
    # Clean after test
    await r.flushdb()
    await r.aclose()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def redis_client(cleanup_redis):
    """Fixture that provides a test instance of EnhancedRedisCache with real Redis."""
    client = EnhancedRedisCache(
        url=TEST_REDIS_URL,
        namespace=TEST_NAMESPACE,
        logger=MagicMock()
    )
    
    await client.connect()
    yield client
    await client.close()

@pytest.fixture
def triage_engine_class():
    """Fixture that provides the TriageEngineWithRedisMixin class with patched Redis."""
    from app.ai_agents.sir_hawkington.hawk_redis_patch.triage_engine_redis_patch import TriageEngineWithRedisMixin
    
    class TestTriageEngine(TriageEngineWithRedisMixin):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = MagicMock()
    
    return TestTriageEngine

@pytest_asyncio.fixture
async def triage_engine(triage_engine_class, cleanup_redis):
    """Fixture that provides a test instance of TriageEngineWithRedisMixin with real Redis."""
    engine = triage_engine_class(
        redis_url=TEST_REDIS_URL,
        cache_namespace=TEST_NAMESPACE,
        max_concurrent_db_tasks=5
    )
    await engine.initialize()
    yield engine
    await engine.__aexit__(None, None, None)
