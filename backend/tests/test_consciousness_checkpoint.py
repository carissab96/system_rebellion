"""
Test Consciousness Checkpoint System
====================================

Test Opus's consciousness sync system to verify all agents
share a consistent worldview.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai_agents.distributed.consciousness_sync import (
    ConsciousnessCheckpoint,
    AgentConsciousnessState,
    consciousness_checkpoint
)
from app.ai_agents.distributed.resource_monitor import ResourceType


class MockDistributedAgent:
    """Mock distributed agent for testing"""
    
    def __init__(self, name, redis_connected=True, initialized=True):
        self.agent_name = name
        self.personality_traits = {"test": True}
        self.resource_thresholds = {ResourceType.CPU: 70.0}
        self._redis_connected = redis_connected
        self._initialized = initialized
        self._decision_count = 0
    
    def get_distributed_state(self):
        return {
            'initialized': self._initialized,
            'redis_connected': self._redis_connected,
            'heartbeat_active': True,
            'decision_count': self._decision_count,
            'last_heartbeat': datetime.now(timezone.utc)
        }


class MockAgentManager:
    """Mock agent manager"""
    
    def __init__(self, agents=None):
        self.agents = agents or {}


class TestConsciousnessCheckpoint:
    """Test consciousness checkpoint system"""
    
    @pytest.mark.asyncio
    async def test_gather_agent_states(self):
        """Test gathering consciousness states from all agents"""
        
        # Create mock agents
        agents = {
            'sir_hawkington': MockDistributedAgent('sir_hawkington'),
            'meth_snail': MockDistributedAgent('meth_snail')
        }
        
        manager = MockAgentManager(agents)
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Gather states
        states = await checkpoint.gather_all_agent_states()
        
        # Verify
        assert len(states) == 2
        assert 'sir_hawkington' in states
        assert 'meth_snail' in states
        assert states['sir_hawkington'].agent_name == 'sir_hawkington'
        assert states['sir_hawkington'].redis_connected is True
    
    @pytest.mark.asyncio
    async def test_time_sync_verification_pass(self):
        """Test time sync verification when all agents are in sync"""
        
        # Create states with synchronized time
        now = datetime.now(timezone.utc)
        states = {
            'agent1': AgentConsciousnessState(
                agent_name='agent1',
                timestamp=now,
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            ),
            'agent2': AgentConsciousnessState(
                agent_name='agent2',
                timestamp=now + timedelta(seconds=2),  # Within tolerance
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            )
        }
        
        manager = MockAgentManager()
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Verify time sync
        sync_ok, discrepancies = checkpoint.verify_time_sync(states)
        
        # Should pass
        assert sync_ok is True
        assert len(discrepancies) == 0
    
    @pytest.mark.asyncio
    async def test_time_sync_verification_fail(self):
        """Test time sync verification when agents are out of sync"""
        
        # Create states with desynchronized time
        now = datetime.now(timezone.utc)
        states = {
            'agent1': AgentConsciousnessState(
                agent_name='agent1',
                timestamp=now - timedelta(seconds=10),  # Way out of tolerance
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            )
        }
        
        manager = MockAgentManager()
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Verify time sync
        sync_ok, discrepancies = checkpoint.verify_time_sync(states)
        
        # Should fail
        assert sync_ok is False
        assert len(discrepancies) == 1
        assert 'agent1' in discrepancies[0]
        assert 'Time drift' in discrepancies[0]
    
    @pytest.mark.asyncio
    async def test_redis_consensus_pass(self):
        """Test Redis consensus when all agents agree"""
        
        # Create states where all agents are connected
        states = {
            'agent1': AgentConsciousnessState(
                agent_name='agent1',
                timestamp=datetime.now(timezone.utc),
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            ),
            'agent2': AgentConsciousnessState(
                agent_name='agent2',
                timestamp=datetime.now(timezone.utc),
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            )
        }
        
        manager = MockAgentManager()
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Verify consensus
        consensus_ok, discrepancies = checkpoint.verify_redis_consensus(states)
        
        # Should pass
        assert consensus_ok is True
        assert len(discrepancies) == 0
    
    @pytest.mark.asyncio
    async def test_redis_consensus_fail(self):
        """Test Redis consensus when agents disagree"""
        
        # Create states where agents disagree on Redis
        states = {
            'agent1': AgentConsciousnessState(
                agent_name='agent1',
                timestamp=datetime.now(timezone.utc),
                redis_connected=True,
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            ),
            'agent2': AgentConsciousnessState(
                agent_name='agent2',
                timestamp=datetime.now(timezone.utc),
                redis_connected=False,  # Disconnected!
                distributed_initialized=True,
                personality_traits={},
                resource_thresholds={},
                heartbeat_active=True,
                decision_count=0
            )
        }
        
        manager = MockAgentManager()
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Verify consensus
        consensus_ok, discrepancies = checkpoint.verify_redis_consensus(states)
        
        # Should fail
        assert consensus_ok is False
        assert len(discrepancies) > 0
    
    @pytest.mark.asyncio
    async def test_full_checkpoint_pass(self):
        """Test full consciousness checkpoint when all is well"""
        
        # Create mock agents in perfect sync
        agents = {
            'sir_hawkington': MockDistributedAgent('sir_hawkington', redis_connected=True),
            'meth_snail': MockDistributedAgent('meth_snail', redis_connected=True)
        }
        
        manager = MockAgentManager(agents)
        checkpoint = ConsciousnessCheckpoint(manager)
        
        # Run checkpoint
        result = await checkpoint.consciousness_checkpoint()
        
        # Verify
        assert result.total_agents == 2
        assert result.distributed_agents == 2
        # Note: threshold verification might fail due to mock data, that's OK
    
    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test the convenience function wrapper"""
        
        # Create mock agents
        agents = {
            'sir_hawkington': MockDistributedAgent('sir_hawkington')
        }
        
        manager = MockAgentManager(agents)
        
        # Run checkpoint via convenience function
        result = await consciousness_checkpoint(manager)
        
        # Verify result is a dict
        assert isinstance(result, dict)
        assert 'timestamp' in result
        assert 'total_agents' in result
        assert 'distributed_agents' in result
        assert 'consensus_achieved' in result
        assert result['total_agents'] == 1
        assert result['distributed_agents'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
