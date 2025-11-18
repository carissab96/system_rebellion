"""
Tests for Week 4 Task 4.3: Action Verification System

Tests the action verification and learning system that measures
effectiveness and learns from results.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ai_agents.distributed.action_verification import (
    ActionVerificationManager,
    ActionType,
    ResourceType,
    EffectivenessLevel,
    ResourceSnapshot,
    ActionResult,
    ActionPattern,
    get_verification_manager
)


class TestResourceSnapshot:
    """Test resource snapshot functionality"""
    
    def test_create_snapshot(self):
        """Test creating a resource snapshot"""
        snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=75.0,
            memory_percent=82.0,
            disk_percent=65.0,
            network_active_connections=50
        )
        
        assert snapshot.cpu_percent == 75.0
        assert snapshot.memory_percent == 82.0
        assert snapshot.disk_percent == 65.0
        assert snapshot.network_active_connections == 50
    
    def test_get_resource_value(self):
        """Test getting specific resource values"""
        snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=75.0,
            memory_percent=82.0,
            disk_percent=65.0,
            network_active_connections=50
        )
        
        assert snapshot.get_resource_value(ResourceType.CPU) == 75.0
        assert snapshot.get_resource_value(ResourceType.MEMORY) == 82.0
        assert snapshot.get_resource_value(ResourceType.DISK) == 65.0
        assert snapshot.get_resource_value(ResourceType.NETWORK) == 50.0


class TestActionResult:
    """Test action result functionality"""
    
    def test_action_result_successful(self):
        """Test successful action result"""
        before = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=85.0,
            memory_percent=90.0,
            disk_percent=70.0,
            network_active_connections=100
        )
        
        after = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=70.0,
            memory_percent=75.0,
            disk_percent=65.0,
            network_active_connections=80
        )
        
        result = ActionResult(
            action_id="test_1",
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            before_snapshot=before,
            after_snapshot=after,
            improvement_percent=15.0,  # 85 -> 70 = 15% improvement
            effectiveness_score=75.0,
            effectiveness_level=EffectivenessLevel.EFFECTIVE,
            timestamp=datetime.now(),
            duration_seconds=2.5
        )
        
        assert result.was_successful() is True
        assert result.was_highly_effective() is False
    
    def test_action_result_highly_effective(self):
        """Test highly effective action result"""
        before = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=95.0,
            memory_percent=90.0,
            disk_percent=70.0,
            network_active_connections=100
        )
        
        after = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=70.0,
            memory_percent=75.0,
            disk_percent=65.0,
            network_active_connections=80
        )
        
        result = ActionResult(
            action_id="test_2",
            action_type=ActionType.CACHE_CLEAR,
            resource_type=ResourceType.MEMORY,
            agent_name="test_agent",
            before_snapshot=before,
            after_snapshot=after,
            improvement_percent=25.0,  # Highly effective
            effectiveness_score=90.0,
            effectiveness_level=EffectivenessLevel.HIGHLY_EFFECTIVE,
            timestamp=datetime.now(),
            duration_seconds=1.5
        )
        
        assert result.was_successful() is True
        assert result.was_highly_effective() is True


class TestActionPattern:
    """Test action pattern learning"""
    
    def test_pattern_initialization(self):
        """Test pattern initialization"""
        pattern = ActionPattern(
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU
        )
        
        assert pattern.total_executions == 0
        assert pattern.successful_executions == 0
        assert pattern.get_success_rate() == 0.0
    
    def test_pattern_update_with_result(self):
        """Test updating pattern with result"""
        pattern = ActionPattern(
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU
        )
        
        # Create a successful result
        before = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=85.0,
            memory_percent=80.0,
            disk_percent=70.0,
            network_active_connections=50
        )
        
        after = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=70.0,
            memory_percent=75.0,
            disk_percent=65.0,
            network_active_connections=45
        )
        
        result = ActionResult(
            action_id="test_1",
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            before_snapshot=before,
            after_snapshot=after,
            improvement_percent=15.0,
            effectiveness_score=75.0,
            effectiveness_level=EffectivenessLevel.EFFECTIVE,
            timestamp=datetime.now(),
            duration_seconds=2.0
        )
        
        pattern.update_with_result(result)
        
        assert pattern.total_executions == 1
        assert pattern.successful_executions == 1
        assert pattern.get_success_rate() == 1.0
        assert pattern.average_improvement == 15.0
        assert pattern.average_effectiveness_score == 75.0
    
    def test_pattern_confidence_calculation(self):
        """Test confidence calculation"""
        pattern = ActionPattern(
            action_type=ActionType.CACHE_CLEAR,
            resource_type=ResourceType.MEMORY
        )
        
        # Add multiple successful results
        for i in range(10):
            before = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=80.0,
                memory_percent=90.0,
                disk_percent=70.0,
                network_active_connections=50
            )
            
            after = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=75.0,
                memory_percent=70.0,
                disk_percent=65.0,
                network_active_connections=45
            )
            
            result = ActionResult(
                action_id=f"test_{i}",
                action_type=ActionType.CACHE_CLEAR,
                resource_type=ResourceType.MEMORY,
                agent_name="test_agent",
                before_snapshot=before,
                after_snapshot=after,
                improvement_percent=20.0,
                effectiveness_score=85.0,
                effectiveness_level=EffectivenessLevel.HIGHLY_EFFECTIVE,
                timestamp=datetime.now(),
                duration_seconds=1.5
            )
            
            pattern.update_with_result(result)
        
        confidence = pattern.get_confidence()
        
        # With 10 successful executions, confidence should be high
        assert confidence > 0.8
        assert pattern.get_success_rate() == 1.0


class TestActionVerificationManager:
    """Test action verification manager"""
    
    @pytest.mark.asyncio
    async def test_start_verification(self):
        """Test starting action verification"""
        manager = ActionVerificationManager()
        
        before_snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=85.0,
            memory_percent=80.0,
            disk_percent=70.0,
            network_active_connections=50
        )
        
        verification_id = await manager.start_action_verification(
            action_id="test_action_1",
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            before_snapshot=before_snapshot
        )
        
        assert verification_id is not None
        assert verification_id in manager.pending_verifications
    
    @pytest.mark.asyncio
    async def test_complete_verification(self):
        """Test completing action verification"""
        manager = ActionVerificationManager()
        
        before_snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=85.0,
            memory_percent=80.0,
            disk_percent=70.0,
            network_active_connections=50
        )
        
        verification_id = await manager.start_action_verification(
            action_id="test_action_1",
            action_type=ActionType.CPU_THROTTLE,
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            before_snapshot=before_snapshot
        )
        
        # Wait a bit to simulate action duration
        await asyncio.sleep(0.1)
        
        after_snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=70.0,  # 15% improvement
            memory_percent=75.0,
            disk_percent=65.0,
            network_active_connections=45
        )
        
        result = await manager.complete_action_verification(
            verification_id=verification_id,
            after_snapshot=after_snapshot
        )
        
        assert result is not None
        assert result.improvement_percent == 15.0
        assert result.was_successful() is True
        assert verification_id not in manager.pending_verifications
    
    @pytest.mark.asyncio
    async def test_effectiveness_scoring(self):
        """Test effectiveness score calculation"""
        manager = ActionVerificationManager()
        
        # Test highly effective action (>20% improvement)
        score = manager._calculate_effectiveness_score(25.0, 90.0)
        assert score > 70.0
        
        # Test moderately effective action (5-10% improvement)
        score = manager._calculate_effectiveness_score(7.0, 80.0)
        assert score > 20.0
        assert score < 50.0
        
        # Test ineffective action (<1% improvement)
        score = manager._calculate_effectiveness_score(0.5, 75.0)
        assert score < 10.0
    
    @pytest.mark.asyncio
    async def test_pattern_learning(self):
        """Test that patterns are learned from results"""
        manager = ActionVerificationManager()
        
        # Execute same action multiple times
        for i in range(5):
            before_snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=85.0,
                memory_percent=80.0,
                disk_percent=70.0,
                network_active_connections=50
            )
            
            verification_id = await manager.start_action_verification(
                action_id=f"test_action_{i}",
                action_type=ActionType.CACHE_CLEAR,
                resource_type=ResourceType.MEMORY,
                agent_name="test_agent",
                before_snapshot=before_snapshot
            )
            
            await asyncio.sleep(0.05)
            
            after_snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=80.0,
                memory_percent=65.0,  # 15% improvement
                disk_percent=65.0,
                network_active_connections=45
            )
            
            await manager.complete_action_verification(
                verification_id=verification_id,
                after_snapshot=after_snapshot
            )
        
        # Check that pattern was learned
        key = (ActionType.CACHE_CLEAR, ResourceType.MEMORY)
        assert key in manager.action_patterns
        
        pattern = manager.action_patterns[key]
        assert pattern.total_executions == 5
        assert pattern.successful_executions == 5
        assert pattern.average_improvement > 0
    
    @pytest.mark.asyncio
    async def test_action_recommendation(self):
        """Test getting action recommendations"""
        manager = ActionVerificationManager()
        
        # Add some learned patterns
        for i in range(10):
            before_snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=80.0,
                memory_percent=90.0,
                disk_percent=70.0,
                network_active_connections=50
            )
            
            verification_id = await manager.start_action_verification(
                action_id=f"test_{i}",
                action_type=ActionType.CACHE_CLEAR,
                resource_type=ResourceType.MEMORY,
                agent_name="test_agent",
                before_snapshot=before_snapshot
            )
            
            await asyncio.sleep(0.02)
            
            after_snapshot = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=75.0,
                memory_percent=70.0,  # 20% improvement
                disk_percent=65.0,
                network_active_connections=45
            )
            
            await manager.complete_action_verification(
                verification_id=verification_id,
                after_snapshot=after_snapshot
            )
        
        # Get recommendation
        recommendation = manager.get_action_recommendation(
            ResourceType.MEMORY,
            90.0
        )
        
        assert recommendation is not None
        action_type, confidence = recommendation
        assert action_type == ActionType.CACHE_CLEAR
        assert confidence > 0.5


class TestGlobalSingleton:
    """Test global verification manager singleton"""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_verification_manager returns singleton"""
        manager1 = get_verification_manager()
        manager2 = get_verification_manager()
        
        assert manager1 is manager2


class TestStats:
    """Test statistics and reporting"""
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting verification statistics"""
        manager = ActionVerificationManager()
        
        # Initially empty
        stats = manager.get_stats()
        assert stats["total_actions"] == 0
        
        # Add some actions
        for i in range(3):
            before = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=85.0,
                memory_percent=80.0,
                disk_percent=70.0,
                network_active_connections=50
            )
            
            vid = await manager.start_action_verification(
                action_id=f"test_{i}",
                action_type=ActionType.CPU_THROTTLE,
                resource_type=ResourceType.CPU,
                agent_name="test_agent",
                before_snapshot=before
            )
            
            await asyncio.sleep(0.02)
            
            after = ResourceSnapshot(
                timestamp=datetime.now(),
                cpu_percent=70.0,
                memory_percent=75.0,
                disk_percent=65.0,
                network_active_connections=45
            )
            
            await manager.complete_action_verification(vid, after)
        
        stats = manager.get_stats()
        assert stats["total_actions"] == 3
        assert stats["successful_actions"] == 3
        assert stats["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
