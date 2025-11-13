"""
Test Triage Broadcasting
========================

Test that Sir Hawkington's triage engine broadcasts decisions
to all distributed agents via Redis.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.sir_hawkington.triage_engine import (
    TriageDecision,
    TriageSeverity,
    TriageRouting
)


class MockCommHub:
    """Mock communication hub"""
    
    def __init__(self):
        self.broadcast_calls = []
    
    async def broadcast_message(self, message_type, data, priority):
        self.broadcast_calls.append({
            'message_type': message_type,
            'data': data,
            'priority': priority
        })


class TestTriageBroadcasting:
    """Test triage decision broadcasting"""
    
    @pytest.mark.asyncio
    async def test_broadcast_triage_decision(self):
        """Test that triage decisions are broadcast via comm_hub"""
        
        # Create mock triage engine
        from app.ai_agents.sir_hawkington.triage_engine import SirHawkingtonTriageEngine
        
        # Mock db_getter
        async def mock_db_getter():
            return None
        
        # Create engine
        engine = SirHawkingtonTriageEngine(db_getter=mock_db_getter)
        
        # Set mock comm_hub
        mock_hub = MockCommHub()
        engine.set_comm_hub(mock_hub)
        
        # Create test triage decision
        triage_decision = TriageDecision(
            severity=TriageSeverity.HIGH,
            routing=TriageRouting.VIC20_EMERGENCY,
            target_agents=['vic_20_sage', 'meth_snail'],
            reasoning="System stress critical - emergency protocols activated",
            monocle_yeeted=False,
            hawkington_decision=None,
            confidence=0.95
        )
        
        # Create test metrics
        metrics_data = {
            'cpu_usage': 95.0,
            'memory_usage': 90.0,
            'disk_usage': 75.0,
            'network_usage': 60.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast the decision
        await engine._broadcast_triage_decision(triage_decision, metrics_data, user_id='test_user')
        
        # Verify broadcast was called
        assert len(mock_hub.broadcast_calls) == 1
        
        # Verify broadcast content
        broadcast = mock_hub.broadcast_calls[0]
        assert broadcast['message_type'] == 'triage_decision'
        assert broadcast['data']['severity'] == 'high'
        assert broadcast['data']['routing'] == 'vic20_emergency'
        assert 'vic_20_sage' in broadcast['data']['target_agents']
        assert 'meth_snail' in broadcast['data']['target_agents']
        assert broadcast['data']['metrics_summary']['cpu_usage'] == 95.0
    
    @pytest.mark.asyncio
    async def test_broadcast_priority_mapping(self):
        """Test that severity maps to correct priority"""
        
        from app.ai_agents.sir_hawkington.triage_engine import SirHawkingtonTriageEngine
        from app.ai_agents.distributed.message_protocol import Priority
        
        # Mock db_getter
        async def mock_db_getter():
            return None
        
        # Create engine
        engine = SirHawkingtonTriageEngine(db_getter=mock_db_getter)
        
        # Set mock comm_hub
        mock_hub = MockCommHub()
        engine.set_comm_hub(mock_hub)
        
        # Test EMERGENCY severity -> CRITICAL priority
        triage_decision = TriageDecision(
            severity=TriageSeverity.EMERGENCY,
            routing=TriageRouting.VIC20_EMERGENCY,
            target_agents=['all'],
            reasoning="EMERGENCY!",
            monocle_yeeted=True,
            hawkington_decision=None,
            confidence=1.0
        )
        
        await engine._broadcast_triage_decision(triage_decision, {}, user_id=None)
        
        # Verify CRITICAL priority
        assert mock_hub.broadcast_calls[0]['priority'] == Priority.CRITICAL
    
    @pytest.mark.asyncio
    async def test_broadcast_without_comm_hub(self):
        """Test that broadcasting gracefully skips when no comm_hub"""
        
        from app.ai_agents.sir_hawkington.triage_engine import SirHawkingtonTriageEngine
        
        # Mock db_getter
        async def mock_db_getter():
            return None
        
        # Create engine WITHOUT comm_hub
        engine = SirHawkingtonTriageEngine(db_getter=mock_db_getter)
        
        # Create test triage decision
        triage_decision = TriageDecision(
            severity=TriageSeverity.NORMAL,
            routing=TriageRouting.STICK_DIRECT,
            target_agents=['the_stick'],
            reasoning="Normal operations",
            monocle_yeeted=False,
            hawkington_decision=None,
            confidence=0.8
        )
        
        # Should not raise exception
        await engine._broadcast_triage_decision(triage_decision, {}, user_id=None)
        
        # Verify no errors (test passes if we get here)
        assert True
    
    @pytest.mark.asyncio
    async def test_set_comm_hub_method_exists(self):
        """Test that triage engine has set_comm_hub method"""
        
        from app.ai_agents.sir_hawkington.triage_engine import SirHawkingtonTriageEngine
        
        # Mock db_getter
        async def mock_db_getter():
            return None
        
        # Create engine
        engine = SirHawkingtonTriageEngine(db_getter=mock_db_getter)
        
        # Verify set_comm_hub method exists
        assert hasattr(engine, 'set_comm_hub')
        assert callable(engine.set_comm_hub)
        
        # Test setting comm_hub
        mock_hub = MockCommHub()
        engine.set_comm_hub(mock_hub)
        
        # Verify it was set
        assert engine._comm_hub is mock_hub


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
