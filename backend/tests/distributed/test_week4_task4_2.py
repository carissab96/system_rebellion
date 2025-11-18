"""
Tests for Week 4 Task 4.2: Alert Escalation System

Tests the smart alert management system that prevents spam and provides
intelligent escalation based on severity, rate of change, and cooldown periods.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ai_agents.distributed.alert_escalation import (
    AlertEscalationManager,
    AlertLevel,
    ResourceType,
    AlertEvent,
    EscalationState,
    get_escalation_manager
)


class TestAlertLevels:
    """Test alert level calculation"""
    
    def test_alert_level_thresholds(self):
        """Test that alert levels are calculated correctly based on thresholds"""
        manager = AlertEscalationManager()
        
        # INFO level (60-70%)
        level = manager.calculate_alert_level(65.0, 60.0)
        assert level == AlertLevel.INFO
        
        # WARNING level (70-80%)
        level = manager.calculate_alert_level(75.0, 70.0)
        assert level == AlertLevel.WARNING
        
        # ALERT level (80-90%)
        level = manager.calculate_alert_level(85.0, 80.0)
        assert level == AlertLevel.ALERT
        
        # CRITICAL level (90-95%)
        level = manager.calculate_alert_level(92.0, 90.0)
        assert level == AlertLevel.CRITICAL
        
        # EMERGENCY level (95%+)
        level = manager.calculate_alert_level(97.0, 95.0)
        assert level == AlertLevel.EMERGENCY
    
    def test_rate_of_change_escalation(self):
        """Test that rapid rate of change escalates alert level"""
        manager = AlertEscalationManager()
        
        # Normal rate of change
        level = manager.calculate_alert_level(75.0, 70.0, rate_of_change=2.0)
        assert level == AlertLevel.WARNING
        
        # Rapid rate of change (>5% per minute) escalates
        level = manager.calculate_alert_level(75.0, 70.0, rate_of_change=6.0)
        assert level == AlertLevel.ALERT  # Escalated from WARNING


class TestCooldownPeriods:
    """Test cooldown period enforcement"""
    
    @pytest.mark.asyncio
    async def test_cooldown_prevents_duplicate_alerts(self):
        """Test that cooldown prevents duplicate alerts"""
        manager = AlertEscalationManager()
        
        # First alert should go through
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert should_alert is True
        assert level == AlertLevel.ALERT
        
        # Immediate second alert should be suppressed (in cooldown)
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert should_alert is False
        assert "cooldown" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_escalation_bypasses_cooldown(self):
        """Test that escalation to higher level bypasses cooldown"""
        manager = AlertEscalationManager()
        
        # First alert at ALERT level
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert should_alert is True
        assert level == AlertLevel.ALERT
        
        # Escalation to CRITICAL should bypass cooldown
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            92.0,
            80.0
        )
        assert should_alert is True
        assert level == AlertLevel.CRITICAL
        assert "escalated" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_emergency_always_alerts(self):
        """Test that EMERGENCY level always alerts"""
        manager = AlertEscalationManager()
        
        # First alert at EMERGENCY
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            97.0,
            80.0
        )
        assert should_alert is True
        assert level == AlertLevel.EMERGENCY
        
        # Second EMERGENCY should also alert (critical situation)
        should_alert, level, reason = manager.should_alert(
            ResourceType.CPU,
            "test_agent",
            98.0,
            80.0
        )
        assert should_alert is True
        assert level == AlertLevel.EMERGENCY


class TestRateOfChange:
    """Test rate of change calculation"""
    
    def test_rate_of_change_calculation(self):
        """Test that rate of change is calculated correctly"""
        state = EscalationState(
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            current_level=AlertLevel.INFO,
            last_alert_time=datetime.now()
        )
        
        # Add values over time
        state.add_value(70.0)
        state.add_value(75.0)
        state.add_value(80.0)
        
        # Should have positive rate of change
        rate = state.get_rate_of_change()
        assert rate is not None
        assert rate > 0  # Increasing
    
    def test_rate_of_change_with_single_value(self):
        """Test that rate of change returns None with insufficient data"""
        state = EscalationState(
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            current_level=AlertLevel.INFO,
            last_alert_time=datetime.now()
        )
        
        state.add_value(70.0)
        
        # Should return None with only one value
        rate = state.get_rate_of_change()
        assert rate is None


class TestAlertAggregation:
    """Test alert aggregation and system health"""
    
    @pytest.mark.asyncio
    async def test_system_health_score(self):
        """Test system health score calculation"""
        manager = AlertEscalationManager()
        
        # No alerts = perfect health
        health = manager.get_system_health_score()
        assert health == 100.0
        
        # Add some alerts
        await manager.process_resource_alert(
            ResourceType.CPU,
            "agent1",
            85.0,
            80.0
        )
        
        await manager.process_resource_alert(
            ResourceType.MEMORY,
            "agent2",
            92.0,
            85.0
        )
        
        # Health should decrease
        health = manager.get_system_health_score()
        assert health < 100.0
        assert health > 0.0
    
    @pytest.mark.asyncio
    async def test_aggregated_alert_summary(self):
        """Test aggregated alert summary"""
        manager = AlertEscalationManager()
        
        # Add multiple alerts
        await manager.process_resource_alert(
            ResourceType.CPU,
            "agent1",
            85.0,
            80.0
        )
        
        await manager.process_resource_alert(
            ResourceType.MEMORY,
            "agent2",
            92.0,
            85.0
        )
        
        summary = manager.get_aggregated_alert_summary()
        
        assert summary["total_alerts"] > 0
        assert "health_score" in summary
        assert "by_level" in summary
        assert "affected_agents" in summary
        assert "affected_resources" in summary
        assert "agent1" in summary["affected_agents"]
        assert "agent2" in summary["affected_agents"]


class TestEscalationState:
    """Test escalation state management"""
    
    def test_cooldown_check(self):
        """Test cooldown period checking"""
        state = EscalationState(
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            current_level=AlertLevel.WARNING,
            last_alert_time=datetime.now(),
            cooldown_until=datetime.now() + timedelta(minutes=5)
        )
        
        # Should be in cooldown
        assert state.is_in_cooldown() is True
        
        # Set cooldown to past
        state.cooldown_until = datetime.now() - timedelta(minutes=1)
        assert state.is_in_cooldown() is False
    
    def test_historical_values_limit(self):
        """Test that historical values are limited"""
        state = EscalationState(
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            current_level=AlertLevel.INFO,
            last_alert_time=datetime.now()
        )
        
        # Add more than max_history values
        for i in range(20):
            state.add_value(float(i))
        
        # Should only keep last 10
        assert len(state.historical_values) == 10


class TestAlertProcessing:
    """Test end-to-end alert processing"""
    
    @pytest.mark.asyncio
    async def test_process_resource_alert(self):
        """Test processing a resource alert"""
        manager = AlertEscalationManager()
        
        # Process first alert
        alert = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        
        assert alert is not None
        assert alert.resource_type == ResourceType.CPU
        assert alert.agent_name == "test_agent"
        assert alert.current_value == 85.0
        assert alert.level == AlertLevel.ALERT
    
    @pytest.mark.asyncio
    async def test_suppressed_alert_returns_none(self):
        """Test that suppressed alerts return None"""
        manager = AlertEscalationManager()
        
        # First alert
        alert1 = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert alert1 is not None
        
        # Second alert (should be suppressed)
        alert2 = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert alert2 is None


class TestResetEscalation:
    """Test escalation reset functionality"""
    
    @pytest.mark.asyncio
    async def test_reset_escalation(self):
        """Test resetting escalation state"""
        manager = AlertEscalationManager()
        
        # Create an alert
        await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            92.0,
            80.0
        )
        
        # Reset escalation
        manager.reset_escalation(ResourceType.CPU, "test_agent")
        
        # Should be able to alert again immediately
        alert = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        assert alert is not None


class TestClearResolvedAlerts:
    """Test clearing old resolved alerts"""
    
    @pytest.mark.asyncio
    async def test_clear_old_alerts(self):
        """Test that old alerts are cleared"""
        manager = AlertEscalationManager()
        
        # Create an alert
        alert = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        
        assert len(manager.active_alerts) > 0
        
        # Manually set timestamp to old
        for alert in manager.active_alerts:
            alert.timestamp = datetime.now() - timedelta(minutes=15)
        
        # Clear old alerts (max_age=10 minutes)
        manager.clear_resolved_alerts(max_age_minutes=10)
        
        # Should be empty now
        assert len(manager.active_alerts) == 0


class TestGlobalSingleton:
    """Test global escalation manager singleton"""
    
    def test_singleton_returns_same_instance(self):
        """Test that get_escalation_manager returns singleton"""
        manager1 = get_escalation_manager()
        manager2 = get_escalation_manager()
        
        assert manager1 is manager2


class TestAlertMessage:
    """Test alert message generation"""
    
    @pytest.mark.asyncio
    async def test_alert_message_includes_rate_of_change(self):
        """Test that alert messages include rate of change"""
        manager = AlertEscalationManager()
        
        # Add some history first
        key = (ResourceType.CPU, "test_agent")
        manager.escalation_states[key] = EscalationState(
            resource_type=ResourceType.CPU,
            agent_name="test_agent",
            current_level=AlertLevel.INFO,
            last_alert_time=datetime.now() - timedelta(hours=1)
        )
        
        # Add historical values
        manager.escalation_states[key].add_value(70.0)
        manager.escalation_states[key].add_value(75.0)
        manager.escalation_states[key].add_value(80.0)
        
        # Process alert
        alert = await manager.process_resource_alert(
            ResourceType.CPU,
            "test_agent",
            85.0,
            80.0
        )
        
        assert alert is not None
        assert "test_agent" in alert.message
        assert "CPU" in alert.message
        assert "85.0%" in alert.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
