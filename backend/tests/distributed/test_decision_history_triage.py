"""
Test Decision History with Triage Integration (Task 3.3)
=========================================================

Tests that decisions can be queried by triage severity and routing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ai_agents.distributed.agent_state import (
    DecisionRecord,
    AgentStateManager
)


class TestDecisionHistoryTriage:
    """Test triage-specific decision history queries"""
    
    @pytest.mark.asyncio
    async def test_decision_record_with_triage_fields(self):
        """Test that DecisionRecord accepts triage fields"""
        
        record = DecisionRecord(
            decision_id="test_001",
            agent_name="the_stick",
            decision_type="triage_learning_observation",
            input_data={"severity": "high"},
            output_data={"status": "learning"},
            confidence=1.0,
            triage_severity="high",
            triage_routing="vic20_coordination",
            coordination_id="coord_12345"
        )
        
        assert record.triage_severity == "high"
        assert record.triage_routing == "vic20_coordination"
        assert record.coordination_id == "coord_12345"
    
    @pytest.mark.asyncio
    async def test_decision_record_serialization_with_triage(self):
        """Test that triage fields serialize/deserialize correctly"""
        
        record = DecisionRecord(
            decision_id="test_002",
            agent_name="vic_20_sage",
            decision_type="triage_coordination_received",
            input_data={},
            output_data={},
            confidence=0.95,
            triage_severity="critical",
            triage_routing="vic20_emergency"
        )
        
        # Serialize
        json_str = record.to_json()
        
        # Deserialize
        restored = DecisionRecord.from_json(json_str)
        
        assert restored.triage_severity == "critical"
        assert restored.triage_routing == "vic20_emergency"
        assert restored.decision_id == "test_002"
    
    @pytest.mark.asyncio
    async def test_get_decisions_by_severity(self):
        """Test filtering decisions by triage severity"""
        
        # Create mock Redis client
        mock_redis = AsyncMock()
        
        # Create test decisions with different severities
        decisions = [
            DecisionRecord(
                decision_id=f"test_{i}",
                agent_name="the_stick",
                decision_type="triage_learning_observation",
                input_data={},
                output_data={},
                confidence=1.0,
                triage_severity=severity
            )
            for i, severity in enumerate([
                "normal", "high", "normal", "critical", "high", "emergency"
            ])
        ]
        
        # Mock Redis to return all decisions
        mock_redis.zrevrange = AsyncMock(return_value=[d.to_json() for d in decisions])
        
        # Create state manager
        state_manager = AgentStateManager(mock_redis, "the_stick")
        
        # Query for HIGH severity decisions
        high_decisions = await state_manager.get_decisions_by_severity("high", count=10)
        
        assert len(high_decisions) == 2
        assert all(d.triage_severity == "high" for d in high_decisions)
    
    @pytest.mark.asyncio
    async def test_get_decisions_by_routing(self):
        """Test filtering decisions by triage routing"""
        
        # Create mock Redis client
        mock_redis = AsyncMock()
        
        # Create test decisions with different routings
        decisions = [
            DecisionRecord(
                decision_id=f"test_{i}",
                agent_name="vic_20_sage",
                decision_type="triage_coordination_received",
                input_data={},
                output_data={},
                confidence=0.95,
                triage_routing=routing
            )
            for i, routing in enumerate([
                "stick_direct", "vic20_coordination", "stick_direct", 
                "vic20_emergency", "vic20_coordination"
            ])
        ]
        
        # Mock Redis to return all decisions
        mock_redis.zrevrange = AsyncMock(return_value=[d.to_json() for d in decisions])
        
        # Create state manager
        state_manager = AgentStateManager(mock_redis, "vic_20_sage")
        
        # Query for VIC20_COORDINATION routing
        coord_decisions = await state_manager.get_decisions_by_routing("vic20_coordination", count=10)
        
        assert len(coord_decisions) == 2
        assert all(d.triage_routing == "vic20_coordination" for d in coord_decisions)
    
    @pytest.mark.asyncio
    async def test_get_coordination_decisions(self):
        """Test filtering decisions by coordination ID"""
        
        # Create mock Redis client
        mock_redis = AsyncMock()
        
        # Create test decisions with different coordination IDs
        decisions = [
            DecisionRecord(
                decision_id=f"test_{i}",
                agent_name="the_stick",
                decision_type="coordination_learning_observation",
                input_data={},
                output_data={},
                confidence=1.0,
                coordination_id=coord_id
            )
            for i, coord_id in enumerate([
                "coord_123", "coord_456", "coord_123", "coord_789", "coord_123"
            ])
        ]
        
        # Mock Redis to return all decisions
        mock_redis.zrevrange = AsyncMock(return_value=[d.to_json() for d in decisions])
        
        # Create state manager
        state_manager = AgentStateManager(mock_redis, "the_stick")
        
        # Query for specific coordination
        coord_123_decisions = await state_manager.get_coordination_decisions("coord_123")
        
        assert len(coord_123_decisions) == 3
        assert all(d.coordination_id == "coord_123" for d in coord_123_decisions)
    
    @pytest.mark.asyncio
    async def test_query_critical_decisions_last_week(self):
        """Test the success criteria: 'show me all CRITICAL triage decisions from last week'"""
        
        # Create mock Redis client
        mock_redis = AsyncMock()
        
        # Create test decisions with timestamps
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        
        decisions = [
            DecisionRecord(
                decision_id=f"test_{i}",
                agent_name="the_stick",
                decision_type="triage_learning_observation",
                timestamp=(now - timedelta(days=days)).isoformat(),
                input_data={},
                output_data={},
                confidence=1.0,
                triage_severity=severity
            )
            for i, (days, severity) in enumerate([
                (1, "critical"),  # Recent critical
                (3, "high"),      # Recent high
                (5, "critical"),  # Recent critical
                (10, "critical"), # Old critical (should be filtered out by time)
                (2, "normal"),    # Recent normal
                (4, "critical"),  # Recent critical
            ])
        ]
        
        # Mock Redis to return decisions from last week
        recent_decisions = [d for d in decisions if (now - datetime.fromisoformat(d.timestamp)).days <= 7]
        mock_redis.zrangebyscore = AsyncMock(return_value=[d.to_json() for d in recent_decisions])
        
        # Create state manager
        state_manager = AgentStateManager(mock_redis, "the_stick")
        
        # Query for CRITICAL decisions from last week
        critical_decisions = await state_manager.get_decisions_by_severity(
            "critical",
            count=50,
            since=week_ago
        )
        
        # Should get 3 critical decisions (days 1, 5, 4)
        assert len(critical_decisions) == 3
        assert all(d.triage_severity == "critical" for d in critical_decisions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
