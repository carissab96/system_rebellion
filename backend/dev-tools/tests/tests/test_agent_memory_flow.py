"""
Test Memory Flow for Each Agent

This test demonstrates how each agent interacts with the memory system,
showing the complete flow from memory creation to retrieval.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.agent_memory_banks import CentralMemoryBank
from app.schemas.agent_memory import (
    MemoryCreate, MemoryUpdate, MemoryPriority, MemoryCategory,
    AgentType, EventType
)
from app.services.memory_service import MemoryService
from app.core.database import SessionLocal

# Test data
TEST_USER_ID = "test_user_123"

def test_sir_hawkington_memory_flow():
    """Test memory flow for Sir Hawkington (data quality monitoring)"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create a memory about a data quality issue
    memory_data = MemoryCreate(
        agent_name=AgentType.SIR_HAWKINGTON,
        event_type=EventType.DATA_QUALITY_ISSUE,
        user_id=TEST_USER_ID,
        title="Data quality anomaly detected in user profiles",
        description="Found 12 user profiles with missing email addresses",
        category=MemoryCategory.OBSERVATION,
        priority=MemoryPriority.HIGH,
        details={
            "anomaly_type": "missing_data",
            "field": "email",
            "count": 12,
            "severity": "high"
        },
        tags=["data_quality", "user_profiles", "missing_data"]
    )
    
    # 2. Save the memory
    result = service.create_memory(memory_data)
    assert result.success is True
    memory_id = result.data.memory_id
    
    # 3. Retrieve and verify the memory
    retrieved = service.get_memory(memory_id)
    assert retrieved.success is True
    assert retrieved.data.agent_name == AgentType.SIR_HAWKINGTON
    assert retrieved.data.event_type == EventType.DATA_QUALITY_ISSUE
    assert retrieved.data.details["anomaly_type"] == "missing_data"
    
    # 4. Cleanup
    db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()

def test_meth_snail_memory_flow():
    """Test memory flow for Meth Snail (performance optimization)"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create a memory about a performance optimization
    memory_data = MemoryCreate(
        agent_name=AgentType.METH_SNAIL,
        event_type=EventType.PERFORMANCE_OPTIMIZATION,
        user_id=TEST_USER_ID,
        title="Query optimization for user search",
        description="Added index to users.email, improved search performance by 78%",
        category=MemoryCategory.PATTERN,
        priority=MemoryPriority.MEDIUM,
        details={
            "optimization_type": "database_index",
            "target": "users.email",
            "improvement_percent": 78.0,
            "before_execution_ms": 450,
            "after_execution_ms": 99,
            "caffeine_level": 0.8  # Meth Snail's special field
        },
        tags=["optimization", "database", "query_performance"]
    )
    
    # 2. Save the memory
    result = service.create_memory(memory_data)
    assert result.success is True
    memory_id = result.data.memory_id
    
    # 3. Verify the memory was stored with agent-specific metadata
    memory = db.query(CentralMemoryBank).filter_by(memory_id=memory_id).first()
    assert memory.agent_metadata["caffeine_level"] == 0.8
    
    # 4. Cleanup
    db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()

def test_hamsters_memory_flow():
    """Test memory flow for Hamsters (infrastructure)"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create a memory about an infrastructure issue
    memory_data = MemoryCreate(
        agent_name=AgentType.HAMSTERS,
        event_type=EventType.INFRASTRUCTURE_ISSUE,
        user_id=TEST_USER_ID,
        title="High CPU usage on web server",
        description="CPU spiked to 95% for 15 minutes",
        category=MemoryCategory.INCIDENT,
        priority=MemoryPriority.HIGH,
        details={
            "resource_type": "cpu",
            "peak_usage": 95.0,
            "duration_minutes": 15,
            "root_cause": "Inefficient database query",
            "beers_consumed": 3  # Hamsters' special field
        },
        tags=["infra", "incident", "cpu_spike"]
    )
    
    # 2. Save and verify the memory
    result = service.create_memory(memory_data)
    assert result.success is True
    memory_id = result.data.memory_id
    
    # 3. Cleanup
    db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()

def test_quantum_shadow_people_memory_flow():
    """Test memory flow for Quantum Shadow People (security)"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create a memory about a security event
    memory_data = MemoryCreate(
        agent_name=AgentType.QUANTUM_SHADOW,
        event_type=EventType.SECURITY_EVENT,
        user_id=TEST_USER_ID,
        title="Suspicious login attempt detected",
        description="Multiple failed login attempts from unusual location",
        category=MemoryCategory.INCIDENT,
        priority=MemoryPriority.HIGH,
        details={
            "event_type": "failed_login",
            "ip_address": "192.168.1.100",
            "attempts": 5,
            "location": "Unknown",
            "quantum_entanglement_level": 0.92  # QSP special field
        },
        tags=["security", "authentication", "intrusion_detection"]
    )
    
    # 2. Save and verify the memory
    result = service.create_memory(memory_data)
    assert result.success is True
    memory_id = result.data.memory_id
    
    # 3. Cleanup
    db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()

def test_vic20_memory_flow():
    """Test memory flow for VIC-20 (coordination)"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create a memory about agent coordination
    memory_data = MemoryCreate(
        agent_name=AgentType.VIC20,
        event_type=EventType.AGENT_COORDINATION,
        user_id=TEST_USER_ID,
        title="Resolved conflict between Snail and Hawkington",
        description="Mediated a dispute over resource allocation",
        category=MemoryCategory.COORDINATION,
        priority=MemoryPriority.MEDIUM,
        details={
            "agents_involved": ["METH_SNAIL", "SIR_HAWKINGTON"],
            "issue": "Resource allocation conflict",
            "resolution": "Adjusted priorities and allocated additional resources",
            "retro_advice_applied": True,  # VIC-20 special field
            "wisdom_level": 8.5
        },
        tags=["coordination", "conflict_resolution", "agent_interaction"]
    )
    
    # 2. Save and verify the memory
    result = service.create_memory(memory_data)
    assert result.success is True
    memory_id = result.data.memory_id
    
    # 3. Cleanup
    db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()

def test_cross_agent_memory_retrieval():
    """Test retrieving memories across different agents"""
    db = SessionLocal()
    service = MemoryService(db)
    
    # 1. Create test memories for different agents
    memories = [
        MemoryCreate(
            agent_name=agent,
            event_type=EventType.OBSERVATION,
            user_id=TEST_USER_ID,
            title=f"Test memory for {agent}",
            description=f"Test description for {agent}",
            category=MemoryCategory.OBSERVATION,
            priority=MemoryPriority.LOW,
            details={"test": True}
        )
        for agent in [
            AgentType.SIR_HAWKINGTON,
            AgentType.METH_SNAIL,
            AgentType.HAMSTERS,
            AgentType.QUANTUM_SHADOW,
            AgentType.VIC20
        ]
    ]
    
    # 2. Save all memories
    memory_ids = []
    for memory_data in memories:
        result = service.create_memory(memory_data)
        assert result.success is True
        memory_ids.append(result.data.memory_id)
    
    # 3. Test retrieval by agent
    for agent in [
        AgentType.SIR_HAWKINGTON,
        AgentType.METH_SNAIL,
        AgentType.HAMSTERS,
        AgentType.QUANTUM_SHADOW,
        AgentType.VIC20
    ]:
        result = service.query_memories({
            "agent_name": agent,
            "user_id": TEST_USER_ID
        })
        assert result.success is True
        assert len(result.data.items) >= 1  # At least our test memory
    
    # 4. Cleanup
    for memory_id in memory_ids:
        db.query(CentralMemoryBank).filter_by(memory_id=memory_id).delete()
    db.commit()
    db.close()
