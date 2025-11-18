"""
Tests for Week 4 Task 4.4: Cross-Agent Coordination System

Tests the coordination system that enables multiple agents to work together.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ai_agents.distributed.coordination import (
    CoordinationManager,
    CoordinationPriority,
    ResourceType,
    CoordinationStatus,
    AgentCapability,
    CoordinationRequest,
    AgentLock,
    get_coordination_manager
)


class TestAgentCapability:
    """Test agent capability functionality"""
    
    def test_create_capability(self):
        """Test creating an agent capability"""
        capability = AgentCapability(
            agent_name="meth_snail",
            resource_type=ResourceType.MEMORY,
            estimated_improvement=20.0,
            confidence=0.85,
            estimated_duration=2.0,
            action_name="cache_clear"
        )
        
        assert capability.agent_name == "meth_snail"
        assert capability.estimated_improvement == 20.0
        assert capability.confidence == 0.85
    
    def test_capability_score(self):
        """Test capability score calculation"""
        capability = AgentCapability(
            agent_name="test_agent",
            resource_type=ResourceType.CPU,
            estimated_improvement=15.0,
            confidence=0.8,
            estimated_duration=1.5,
            action_name="throttle"
        )
        
        score = capability.get_score()
        # Score = improvement * confidence = 15.0 * 0.8 = 12.0
        assert score == 12.0


class TestCoordinationRequest:
    """Test coordination request functionality"""
    
    def test_create_request(self):
        """Test creating a coordination request"""
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.MEMORY,
            current_value=92.0,
            threshold=85.0,
            priority=CoordinationPriority.HIGH,
            requesting_agent="sir_hawkington"
        )
        
        assert request.request_id == "test_123"
        assert request.status == CoordinationStatus.PENDING
        assert request.resource_type == ResourceType.MEMORY
    
    def test_get_best_capabilities(self):
        """Test getting best capabilities"""
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.MEMORY,
            current_value=90.0,
            threshold=85.0,
            priority=CoordinationPriority.NORMAL,
            requesting_agent="test_agent"
        )
        
        # Add capabilities with different scores
        request.capabilities = [
            AgentCapability("agent1", ResourceType.MEMORY, 10.0, 0.5, 1.0, "action1"),  # Score: 5.0
            AgentCapability("agent2", ResourceType.MEMORY, 20.0, 0.8, 1.5, "action2"),  # Score: 16.0
            AgentCapability("agent3", ResourceType.MEMORY, 15.0, 0.9, 2.0, "action3"),  # Score: 13.5
        ]
        
        best = request.get_best_capabilities(limit=2)
        
        assert len(best) == 2
        assert best[0].agent_name == "agent2"  # Highest score
        assert best[1].agent_name == "agent3"  # Second highest
    
    def test_request_expiration(self):
        """Test request expiration check"""
        # Create old request
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.CPU,
            current_value=85.0,
            threshold=80.0,
            priority=CoordinationPriority.NORMAL,
            requesting_agent="test_agent"
        )
        
        # Set created_at to 10 minutes ago
        request.created_at = datetime.now() - timedelta(minutes=10)
        
        # Should be expired with 5 minute timeout
        assert request.is_expired(timeout_seconds=300) is True
        
        # Should not be expired with 15 minute timeout
        assert request.is_expired(timeout_seconds=900) is False


class TestAgentLock:
    """Test agent lock functionality"""
    
    def test_create_lock(self):
        """Test creating an agent lock"""
        lock = AgentLock(
            agent_name="meth_snail",
            resource_type=ResourceType.MEMORY,
            locked_by="request_123",
            locked_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        
        assert lock.agent_name == "meth_snail"
        assert lock.is_expired() is False
    
    def test_lock_expiration(self):
        """Test lock expiration"""
        lock = AgentLock(
            agent_name="test_agent",
            resource_type=ResourceType.CPU,
            locked_by="request_123",
            locked_at=datetime.now() - timedelta(seconds=120),
            expires_at=datetime.now() - timedelta(seconds=60)
        )
        
        assert lock.is_expired() is True


class TestCoordinationManager:
    """Test coordination manager"""
    
    @pytest.mark.asyncio
    async def test_register_agent_capability(self):
        """Test registering agent capabilities"""
        manager = CoordinationManager()
        
        async def test_callback(resource_type, current_value):
            return AgentCapability(
                agent_name="test_agent",
                resource_type=resource_type,
                estimated_improvement=10.0,
                confidence=0.8,
                estimated_duration=1.0,
                action_name="test_action"
            )
        
        manager.register_agent_capability("test_agent", test_callback)
        
        assert "test_agent" in manager.agent_capabilities
    
    @pytest.mark.asyncio
    async def test_request_coordination(self):
        """Test requesting coordination"""
        manager = CoordinationManager()
        
        # Register some agents
        async def agent1_callback(resource_type, current_value):
            return AgentCapability(
                agent_name="agent1",
                resource_type=resource_type,
                estimated_improvement=15.0,
                confidence=0.85,
                estimated_duration=1.5,
                action_name="action1"
            )
        
        async def agent2_callback(resource_type, current_value):
            return AgentCapability(
                agent_name="agent2",
                resource_type=resource_type,
                estimated_improvement=20.0,
                confidence=0.9,
                estimated_duration=2.0,
                action_name="action2"
            )
        
        manager.register_agent_capability("agent1", agent1_callback)
        manager.register_agent_capability("agent2", agent2_callback)
        
        # Request coordination
        request_id = await manager.request_coordination(
            resource_type=ResourceType.MEMORY,
            current_value=92.0,
            threshold=85.0,
            priority=CoordinationPriority.HIGH,
            requesting_agent="test_requester"
        )
        
        assert request_id is not None
        assert request_id in manager.active_requests
        
        # Wait for coordination to complete
        await asyncio.sleep(1.0)
        
        # Check request status
        status = manager.get_request_status(request_id)
        assert status is not None
        assert status["status"] in ["executing", "completed"]
    
    @pytest.mark.asyncio
    async def test_negotiation(self):
        """Test capability negotiation"""
        manager = CoordinationManager()
        
        # Register agents with different capabilities
        async def strong_agent(resource_type, current_value):
            return AgentCapability(
                agent_name="strong_agent",
                resource_type=resource_type,
                estimated_improvement=25.0,
                confidence=0.95,
                estimated_duration=1.0,
                action_name="strong_action"
            )
        
        async def weak_agent(resource_type, current_value):
            return AgentCapability(
                agent_name="weak_agent",
                resource_type=resource_type,
                estimated_improvement=5.0,
                confidence=0.5,
                estimated_duration=3.0,
                action_name="weak_action"
            )
        
        manager.register_agent_capability("strong_agent", strong_agent)
        manager.register_agent_capability("weak_agent", weak_agent)
        
        # Create request
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.CPU,
            current_value=90.0,
            threshold=80.0,
            priority=CoordinationPriority.NORMAL,
            requesting_agent="test_requester"
        )
        
        # Negotiate
        await manager._negotiate_capabilities(request)
        
        # Should have received 2 bids
        assert len(request.capabilities) == 2
        
        # Get best capabilities
        best = request.get_best_capabilities(limit=1)
        
        # Strong agent should be selected
        assert best[0].agent_name == "strong_agent"
    
    @pytest.mark.asyncio
    async def test_agent_locking(self):
        """Test agent locking mechanism"""
        manager = CoordinationManager()
        
        # Create a lock
        lock = AgentLock(
            agent_name="test_agent",
            resource_type=ResourceType.MEMORY,
            locked_by="request_1",
            locked_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        
        manager.agent_locks[("test_agent", ResourceType.MEMORY)] = lock
        
        # Check if locked
        is_locked = manager._is_agent_locked("test_agent", ResourceType.MEMORY)
        assert is_locked is True
        
        # Different resource should not be locked
        is_locked = manager._is_agent_locked("test_agent", ResourceType.CPU)
        assert is_locked is False
    
    @pytest.mark.asyncio
    async def test_lock_acquisition(self):
        """Test acquiring locks for agents"""
        manager = CoordinationManager()
        
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.MEMORY,
            current_value=90.0,
            threshold=85.0,
            priority=CoordinationPriority.NORMAL,
            requesting_agent="test_requester"
        )
        
        capabilities = [
            AgentCapability("agent1", ResourceType.MEMORY, 15.0, 0.8, 1.0, "action1"),
            AgentCapability("agent2", ResourceType.MEMORY, 20.0, 0.9, 1.5, "action2"),
        ]
        
        # Acquire locks
        success = await manager._acquire_locks(request, capabilities)
        
        assert success is True
        assert len(manager.agent_locks) == 2
        
        # Check that agents are locked
        assert manager._is_agent_locked("agent1", ResourceType.MEMORY) is True
        assert manager._is_agent_locked("agent2", ResourceType.MEMORY) is True
    
    @pytest.mark.asyncio
    async def test_lock_release(self):
        """Test releasing locks"""
        manager = CoordinationManager()
        
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.CPU,
            current_value=85.0,
            threshold=80.0,
            priority=CoordinationPriority.NORMAL,
            requesting_agent="test_requester"
        )
        
        # Create some locks
        manager.agent_locks[("agent1", ResourceType.CPU)] = AgentLock(
            agent_name="agent1",
            resource_type=ResourceType.CPU,
            locked_by="test_123",
            locked_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        
        manager.agent_locks[("agent2", ResourceType.CPU)] = AgentLock(
            agent_name="agent2",
            resource_type=ResourceType.CPU,
            locked_by="test_123",
            locked_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        
        # Release locks
        await manager._release_locks(request)
        
        # Locks should be gone
        assert len(manager.agent_locks) == 0
    
    @pytest.mark.asyncio
    async def test_coordinated_execution(self):
        """Test coordinated action execution"""
        manager = CoordinationManager()
        
        request = CoordinationRequest(
            request_id="test_123",
            resource_type=ResourceType.MEMORY,
            current_value=90.0,
            threshold=85.0,
            priority=CoordinationPriority.HIGH,
            requesting_agent="test_requester"
        )
        
        capabilities = [
            AgentCapability("agent1", ResourceType.MEMORY, 10.0, 0.8, 1.0, "action1"),
            AgentCapability("agent2", ResourceType.MEMORY, 15.0, 0.9, 1.5, "action2"),
        ]
        
        # Execute
        success = await manager._execute_coordinated_actions(request, capabilities)
        
        assert success is True
        assert request.total_improvement == 25.0  # 10 + 15
        assert request.final_value == 65.0  # 90 - 25
        assert len(request.execution_plan) == 2
    
    @pytest.mark.asyncio
    async def test_stats(self):
        """Test getting coordination statistics"""
        manager = CoordinationManager()
        
        stats = manager.get_stats()
        
        assert "total_coordinations" in stats
        assert "successful" in stats
        assert "failed" in stats
        assert "success_rate" in stats
        assert "active_requests" in stats


class TestGlobalSingleton:
    """Test global coordination manager singleton"""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_coordination_manager returns singleton"""
        manager1 = get_coordination_manager()
        manager2 = get_coordination_manager()
        
        assert manager1 is manager2


class TestPriorityHandling:
    """Test priority-based coordination"""
    
    @pytest.mark.asyncio
    async def test_emergency_priority(self):
        """Test emergency priority requests"""
        manager = CoordinationManager()
        
        # Register an agent
        async def emergency_responder(resource_type, current_value):
            return AgentCapability(
                agent_name="emergency_agent",
                resource_type=resource_type,
                estimated_improvement=30.0,
                confidence=1.0,
                estimated_duration=0.5,
                action_name="emergency_action"
            )
        
        manager.register_agent_capability("emergency_agent", emergency_responder)
        
        # Request with emergency priority
        request_id = await manager.request_coordination(
            resource_type=ResourceType.MEMORY,
            current_value=98.0,
            threshold=95.0,
            priority=CoordinationPriority.EMERGENCY,
            requesting_agent="system"
        )
        
        assert request_id is not None
        
        # Wait for coordination
        await asyncio.sleep(1.0)
        
        status = manager.get_request_status(request_id)
        assert status is not None
        assert status["priority"] == "emergency"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
