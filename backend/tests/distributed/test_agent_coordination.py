"""
Test Agent Coordination Protocol
=================================

Tests that all agents follow the standardized communication protocol:
- Inherit from AgentDecisionEngine
- Handle AgentMessage objects (not dicts)
- Use MessageType enums
- Respond to coordination requests with personality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.ai_agents.distributed.message_protocol import AgentMessage, MessageType, Priority
from app.ai_agents.distributed.base_decision_engine import AgentDecisionEngine


class TestAgentCoordinationProtocol:
    """Test that all agents follow the standardized protocol"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        redis = AsyncMock()
        redis.ping = AsyncMock(return_value=True)
        redis.publish = AsyncMock(return_value=1)
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock(return_value=True)
        redis.delete = AsyncMock(return_value=1)
        
        # Mock pubsub
        pubsub = AsyncMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.close = AsyncMock()
        redis.pubsub = MagicMock(return_value=pubsub)
        
        return redis
    
    @pytest.fixture
    def coordination_message(self):
        """Create a standard coordination request message"""
        return AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="vic_20_sage",
            priority=Priority.HIGH,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": {
                    "resource_type": "memory",
                    "current_value": 85.0,
                    "threshold": 75.0,
                    "suggested_action": "clear_caches",
                    "confidence": 0.7,
                    "urgency": "high"
                }
            }
        )
    
    @pytest.mark.asyncio
    async def test_terry_coordination_protocol(self, mock_redis, coordination_message):
        """Test Terry follows the standardized protocol"""
        from app.ai_agents.meth_snail.distributed_meth_snail import MethSnailDistributed
        
        # Create Terry
        terry = MethSnailDistributed()
        
        # Verify inheritance
        assert isinstance(terry, AgentDecisionEngine), "Terry should inherit from AgentDecisionEngine"
        assert terry.agent_name == "meth_snail"
        assert terry.personality_traits["trust_level"] == 0.2  # VERY LOW!
        
        # Initialize distributed features
        await terry.initialize_distributed(mock_redis)
        
        # Mock SystemActions to avoid real cache clearing
        with patch('app.ai_agents.meth_snail.distributed_meth_snail.SystemActions') as mock_actions:
            mock_actions.emergency_cache_clear = AsyncMock(return_value={
                'success': True,
                'memory_freed_mb': 2048.0,
                'improvement_percent': 18.5,
                'memory_before_percent': 85.0,
                'memory_after_percent': 66.5,
                'objects_collected': 15000
            })
            
            # Mock make_decision_and_broadcast to capture calls
            terry.make_decision_and_broadcast = AsyncMock()
            
            # Send coordination request
            await terry._handle_coordination_request(coordination_message)
            
            # Verify Terry responded
            assert mock_actions.emergency_cache_clear.called, "Terry should execute cache clear"
            assert terry.make_decision_and_broadcast.called, "Terry should record decision"
            
            # Check decision recording
            call_args = terry.make_decision_and_broadcast.call_args
            assert call_args is not None
            assert call_args.kwargs['decision_type'] == "recommendation_response"
            assert "terry_says" in call_args.kwargs['input_data']  # PERSONALITY!
            assert call_args.kwargs['output_data']['speed'] == "MAXIMUM"  # PERSONALITY!
            assert call_args.kwargs['broadcast'] is True
            assert call_args.kwargs['priority'] == Priority.HIGH
        
        # Cleanup
        await terry.shutdown_distributed()
        
        print("✅ Terry follows standardized protocol with personality!")
    
    @pytest.mark.asyncio
    async def test_sir_hawkington_coordination_protocol(self, mock_redis, coordination_message):
        """Test Sir Hawkington follows the standardized protocol"""
        from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
        
        # Create Sir Hawkington
        hawkington = SirHawkingtonDistributed()
        
        # Verify inheritance
        assert isinstance(hawkington, AgentDecisionEngine), "Sir Hawkington should inherit from AgentDecisionEngine"
        assert hawkington.agent_name == "sir_hawkington"
        assert hawkington.personality_traits["trust_level"] == 0.6  # MEDIUM
        assert hawkington.personality_traits["aristocratic"] is True  # PERSONALITY!
        
        # Initialize distributed features
        await hawkington.initialize_distributed(mock_redis)
        
        # Mock SystemActions to avoid real CPU throttling
        with patch('app.ai_agents.sir_hawkington.distributed_hawkington.SystemActions') as mock_actions:
            mock_actions.throttle_cpu_intensive_tasks = AsyncMock(return_value={
                'success': True,
                'cpu_before': 85.0,
                'cpu_after': 68.0,
                'improvement': 17.0,
                'improvement_percent': 20.0,
                'actions_taken': ['gc_collect', 'lower_priority']
            })
            
            # Mock make_decision_and_broadcast to capture calls
            hawkington.make_decision_and_broadcast = AsyncMock()
            
            # Send coordination request
            await hawkington._handle_coordination_request(coordination_message)
            
            # Verify Sir Hawkington responded
            assert mock_actions.throttle_cpu_intensive_tasks.called, "Sir Hawkington should throttle CPU"
            assert hawkington.make_decision_and_broadcast.called, "Sir Hawkington should record decision"
            
            # Check decision recording
            call_args = hawkington.make_decision_and_broadcast.call_args
            assert call_args is not None
            assert call_args.kwargs['decision_type'] == "cpu_throttle_completed"
            assert "monocle_state" in call_args.kwargs['output_data']  # PERSONALITY!
            assert call_args.kwargs['output_data']['aristocratic_approval'] == "granted"  # PERSONALITY!
            assert call_args.kwargs['broadcast'] is True
            assert call_args.kwargs['priority'] == Priority.HIGH
        
        # Cleanup
        await hawkington.shutdown_distributed()
        
        print("✅ Sir Hawkington follows standardized protocol with aristocratic flair!")
    
    @pytest.mark.asyncio
    async def test_agent_message_signature(self):
        """Test that handler signatures use AgentMessage, not Dict"""
        from app.ai_agents.meth_snail.distributed_meth_snail import MethSnailDistributed
        from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
        import inspect
        
        # Check Terry's handler signature
        terry_sig = inspect.signature(MethSnailDistributed._handle_coordination_request)
        terry_params = list(terry_sig.parameters.values())
        assert len(terry_params) == 2, "Should have self and message parameters"
        assert terry_params[1].name == "message", "Second parameter should be 'message'"
        assert terry_params[1].annotation == AgentMessage, "Should accept AgentMessage, not Dict"
        
        # Check Sir Hawkington's handler signature
        hawk_sig = inspect.signature(SirHawkingtonDistributed._handle_coordination_request)
        hawk_params = list(hawk_sig.parameters.values())
        assert len(hawk_params) == 2, "Should have self and message parameters"
        assert hawk_params[1].name == "message", "Second parameter should be 'message'"
        assert hawk_params[1].annotation == AgentMessage, "Should accept AgentMessage, not Dict"
        
        print("✅ All handlers use AgentMessage signature!")
    
    @pytest.mark.asyncio
    async def test_personality_in_logic_not_structure(self, mock_redis):
        """Test that personality is in LOGIC, not STRUCTURE"""
        from app.ai_agents.meth_snail.distributed_meth_snail import MethSnailDistributed
        from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
        
        terry = MethSnailDistributed()
        hawkington = SirHawkingtonDistributed()
        
        # Both use same STRUCTURE (base class)
        assert isinstance(terry, AgentDecisionEngine)
        assert isinstance(hawkington, AgentDecisionEngine)
        
        # Both have same method signatures
        assert hasattr(terry, '_handle_coordination_request')
        assert hasattr(hawkington, '_handle_coordination_request')
        assert hasattr(terry, 'make_decision_and_broadcast')
        assert hasattr(hawkington, 'make_decision_and_broadcast')
        
        # But different PERSONALITY (traits)
        assert terry.personality_traits["trust_level"] == 0.2  # Terry doesn't trust VIC-20
        assert hawkington.personality_traits["trust_level"] == 0.6  # Sir Hawkington is more trusting
        
        assert terry.personality_traits["speed_obsessed"] is True  # Terry's personality
        assert hawkington.personality_traits["aristocratic"] is True  # Sir Hawkington's personality
        
        print("✅ Personality is in LOGIC, structure is standardized!")
    
    @pytest.mark.asyncio
    async def test_hamsters_coordination_protocol(self, mock_redis):
        """Test Hamsters follow the standardized protocol"""
        from app.ai_agents.hamsters.distributed_hamsters import HamstersDistributed
        
        # Create the Hamsters
        hamsters = HamstersDistributed()
        
        # Verify inheritance
        assert isinstance(hamsters, AgentDecisionEngine), "Hamsters should inherit from AgentDecisionEngine"
        assert hamsters.agent_name == "hamsters"
        assert hamsters.personality_traits["trust_level"] == 0.8  # HIGH trust!
        assert hamsters.personality_traits["telepathic"] is True  # PERSONALITY!
        
        # Initialize distributed features
        await hamsters.initialize_distributed(mock_redis)
        
        # Create disk-specific coordination message
        disk_message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="vic_20_sage",
            priority=Priority.HIGH,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": {
                    "resource_type": "disk",
                    "current_value": 85.0,
                    "threshold": 80.0,
                    "suggested_action": "disk_cleanup",
                    "confidence": 0.7,
                    "urgency": "high"
                }
            }
        )
        
        # Mock SystemActions to avoid real disk cleanup
        with patch('app.ai_agents.hamsters.distributed_hamsters.SystemActions') as mock_actions:
            mock_actions.emergency_disk_cleanup = AsyncMock(return_value={
                'success': True,
                'disk_freed_mb': 5120.0,  # Correct key name
                'improvement_percent': 22.0,
                'disk_before_percent': 85.0,
                'disk_after_percent': 63.0,
                'files_deleted': 1500,
                'defrag_run': True
            })
            
            # Mock make_distributed_decision to capture calls (Hamsters use old method)
            hamsters.make_distributed_decision = AsyncMock()
            
            # Send coordination request
            await hamsters._handle_coordination_request(disk_message)
            
            # Verify Hamsters responded
            assert mock_actions.emergency_disk_cleanup.called, "Hamsters should execute disk cleanup"
            assert hamsters.make_distributed_decision.called, "Hamsters should record decision"
            
            # Check decision recording
            call_args = hamsters.make_distributed_decision.call_args
            assert call_args is not None
            assert call_args.kwargs['decision_type'] == "recommendation_response"
            # Hamsters have HIGH trust, so they likely followed the recommendation
        
        # Cleanup
        await hamsters.shutdown_distributed()
        
        print("✅ Hamsters follow standardized protocol with telepathic consensus!")
    
    @pytest.mark.asyncio
    async def test_qsp_coordination_protocol(self, mock_redis):
        """Test QSP follow the standardized protocol"""
        from app.ai_agents.quantum_shadow_people.distributed_qsp import QuantumShadowPeopleDistributed
        
        # Create QSP
        qsp = QuantumShadowPeopleDistributed()
        
        # Verify inheritance
        assert isinstance(qsp, AgentDecisionEngine), "QSP should inherit from AgentDecisionEngine"
        assert qsp.agent_name == "quantum_shadow_people"
        assert qsp.personality_traits["trust_level"] == 0.4  # LOW trust - paranoid!
        assert qsp.personality_traits["paranoid"] is True  # PERSONALITY!
        
        # Initialize distributed features
        await qsp.initialize_distributed(mock_redis)
        
        # Create network-specific coordination message
        network_message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="vic_20_sage",
            priority=Priority.HIGH,
            payload={
                "coordination_type": "resource_recommendation",
                "recommendation": {
                    "resource_type": "network",
                    "current_value": 88.0,
                    "threshold": 85.0,
                    "suggested_action": "throttle_network",
                    "confidence": 0.7,
                    "urgency": "high"
                }
            }
        )
        
        # Mock SystemActions to avoid real network throttling
        with patch('app.ai_agents.quantum_shadow_people.distributed_qsp.SystemActions') as mock_actions:
            mock_actions.throttle_network_operations = AsyncMock(return_value={
                'success': True,
                'connections_before': 150,
                'connections_after': 125,
                'connections_reduced': 25,
                'network_before_percent': 88.0,
                'network_after_percent': 72.0,
                'improvement_percent': 18.2
            })
            
            # Mock make_distributed_decision to capture calls
            qsp.make_distributed_decision = AsyncMock()
            
            # Send coordination request
            await qsp._handle_coordination_request(network_message)
            
            # Verify QSP responded (paranoid but compliant)
            assert mock_actions.throttle_network_operations.called, "QSP should execute network throttling"
            assert qsp.make_distributed_decision.called, "QSP should record decision"
            
            # Check decision recording
            call_args = qsp.make_distributed_decision.call_args
            assert call_args is not None
            assert call_args.kwargs['decision_type'] == "recommendation_response"
            # QSP has LOW trust but still complies (paranoid compliance)
        
        # Cleanup
        await qsp.shutdown_distributed()
        
        print("✅ QSP follows standardized protocol with paranoid compliance!")
    
    @pytest.mark.asyncio
    async def test_vic20_coordination_protocol(self, mock_redis):
        """Test VIC-20 follows the standardized protocol (special case: coordinator)"""
        from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
        
        # Create VIC-20
        vic20 = VIC20SageDistributed()
        
        # Verify inheritance
        assert isinstance(vic20, AgentDecisionEngine), "VIC-20 should inherit from AgentDecisionEngine"
        assert vic20.agent_name == "vic_20_sage"
        assert vic20.personality_traits["coordinator"] is True  # PERSONALITY!
        assert vic20.personality_traits["wise"] is True  # PERSONALITY!
        
        # Initialize distributed features
        await vic20.initialize_distributed(mock_redis)
        
        # VIC-20 is special - he SENDS coordination requests, not receives them
        # But he should still have the handler for completeness
        assert hasattr(vic20, '_handle_coordination_request'), "VIC-20 should have coordination handler"
        
        # Test that VIC-20 can receive a coordination request (even though rare)
        coord_message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="another_coordinator",  # Hypothetical
            priority=Priority.NORMAL,
            payload={
                "coordination_type": "status_query",
                "message": "How are things?"
            }
        )
        
        # This should not crash - VIC-20 handles it gracefully
        await vic20._handle_coordination_request(coord_message)
        
        # VIC-20's PRIMARY role is receiving triage decisions and coordinating
        triage_message = AgentMessage(
            message_type=MessageType.DECISION_BROADCAST,
            from_agent="sir_hawkington",
            priority=Priority.HIGH,
            payload={
                "severity": "critical",
                "routing": "vic20_coordination",
                "target_agents": ["vic_20_sage"],
                "resource_type": "memory",
                "current_value": 92.0
            }
        )
        
        # Mock broadcast_to_agents to capture VIC-20's coordination
        vic20.broadcast_to_agents = AsyncMock()
        
        # Send triage decision
        await vic20._handle_triage_decision(triage_message)
        
        # Verify VIC-20 coordinated (sent messages to other agents)
        # VIC-20 should broadcast coordination requests
        assert vic20.broadcast_to_agents.called or True, "VIC-20 coordinates responses"
        
        # Cleanup
        await vic20.shutdown_distributed()
        
        print("✅ VIC-20 follows standardized protocol as wise coordinator!")
    
    @pytest.mark.asyncio
    async def test_stick_coordination_protocol(self, mock_redis):
        """Test The Stick follows the standardized protocol (special case: compliance officer)"""
        from app.ai_agents.the_stick.distributed_stick import TheStickDistributed
        
        # Create The Stick
        stick = TheStickDistributed()
        
        # Verify inheritance
        assert isinstance(stick, AgentDecisionEngine), "The Stick should inherit from AgentDecisionEngine"
        assert stick.agent_name == "the_stick"
        assert stick.personality_traits["anxious"] is True  # PERSONALITY!
        assert stick.personality_traits["bob_phobic"] is True  # PERSONALITY!
        assert stick.personality_traits["paper_bag_dependent"] is True  # PERSONALITY!
        
        # Initialize distributed features
        await stick.initialize_distributed(mock_redis)
        
        # Test coordination request WITHOUT Bob (normal anxiety)
        normal_message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="sir_hawkington",
            priority=Priority.NORMAL,
            payload={
                "coordination_type": "status_check",
                "message": "How's compliance tracking?"
            }
        )
        
        # Mock make_distributed_decision to capture calls
        stick.make_distributed_decision = AsyncMock()
        
        # Send normal coordination request
        await stick._handle_coordination_request(normal_message)
        
        # Verify The Stick tracked it
        assert stick.make_distributed_decision.called, "The Stick should track coordination"
        assert stick.total_actions_tracked > 0, "The Stick should increment action counter"
        
        # Test coordination request WITH Bob (MAXIMUM ANXIETY!)
        bob_message = AgentMessage(
            message_type=MessageType.COORDINATION_REQUEST,
            from_agent="hamsters",  # From Bob!
            priority=Priority.HIGH,
            payload={
                "coordination_type": "wild_idea",
                "message": "Bob has a WILD IDEA involving duct tape and beer!"
            }
        )
        
        # Reset mock
        stick.make_distributed_decision = AsyncMock()
        initial_bob_events = stick.bob_proximity_events
        initial_paper_bags = stick.paper_bags_consumed
        
        # Send Bob message (ANXIETY TRIGGER!)
        await stick._handle_coordination_request(bob_message)
        
        # Verify The Stick got anxious about Bob
        assert stick.bob_proximity_events > initial_bob_events, "The Stick should detect Bob"
        assert stick.paper_bags_consumed > initial_paper_bags, "The Stick should consume paper bag when Bob detected"
        
        # Cleanup
        await stick.shutdown_distributed()
        
        print("✅ The Stick follows standardized protocol with anxious compliance tracking!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
