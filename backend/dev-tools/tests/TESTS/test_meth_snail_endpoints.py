# test_meth_snail_endpoints.py
"""
Meth Snail API Endpoints Test Suite
Testing the high-energy optimization endpoints

Tests cover:
- Jitter level data retrieval
- Optimization metrics endpoints
- Aggregated statistics
- Error handling and validation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.core.database import Base
from app.models.meth_snail_model import MethSnailJitterLevels, MethSnailOptimizationStats

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# Test client
client = TestClient(app)

# Test data
TEST_JITTER_DATA = {
    "current_jitter_level": 0.75,
    "peak_jitter_level": 0.85,
    "baseline_jitter_level": 0.45,
    "caffeine_level_mg": 150.0,
    "is_decaffeinated": False,
    "shell_spin_probability": 0.9,
    "optimization_effectiveness": 0.8,
    "focus_level": 0.85,
    "hypercaffeinated": True,
    "requires_stick_intervention": False,
    "vic20_mediation_requested": False,
    "energy_source": "Triple Espresso",
    "jitter_trend": "increasing",
    "raw_jitter_data": {"samples": [0.7, 0.72, 0.75]}
}

TEST_OPTIMIZATION_DATA = {
    "optimization_success": True,
    "shell_spins_executed": 3,
    "cpu_usage_before": 75.5,
    "cpu_usage_after": 45.2,
    "memory_usage_before": 1024.5,
    "memory_usage_after": 768.3,
    "energy_drink_level": 0.8,
    "raw_metrics": {"cpu_cores_utilized": 4}
}

@pytest.fixture(scope="module")
async def test_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a test session
    db = TestingSessionLocal()
    
    # Add test data
    jitter_entry = MethSnailJitterLevels(
        **TEST_JITTER_DATA,
        timestamp=datetime.utcnow() - timedelta(minutes=30)
    )
    db.add(jitter_entry)
    
    optimization_entry = MethSnailOptimizationStats(
        **TEST_OPTIMIZATION_DATA,
        timestamp=datetime.utcnow() - timedelta(minutes=15)
    )
    db.add(optimization_entry)
    await db.commit()
    
    yield db
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db.close()

@pytest.mark.asyncio
async def test_get_jitter_levels(test_db):
    """Test retrieving jitter level data"""
    response = client.get("/api/meth-snail/jitter-levels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there's data, validate its structure
        assert "current_jitter_level" in data[0]
        assert "caffeine_level_mg" in data[0]
        assert "timestamp" in data[0]

@pytest.mark.asyncio
async def test_get_optimization_metrics(test_db):
    """Test retrieving optimization metrics"""
    response = client.get("/api/meth-snail/optimization-metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "optimization_success" in data[0]
        assert "shell_spins_executed" in data[0]
        assert "timestamp" in data[0]

@pytest.mark.asyncio
async def test_get_jitter_aggregates(test_db):
    """Test retrieving aggregated jitter statistics"""
    response = client.get("/api/meth-snail/jitter-aggregates?time_range=24h")
    assert response.status_code == 200
    data = response.json()
    assert "time_range" in data
    assert "avg_jitter" in data
    assert "max_jitter" in data
    assert "min_jitter" in data
    assert "avg_caffeine" in data
    assert "sample_count" in data

@pytest.mark.asyncio
async def test_invalid_time_range(test_db):
    """Test validation of time range parameter"""
    response = client.get("/api/meth-snail/jitter-aggregates?time_range=invalid")
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
