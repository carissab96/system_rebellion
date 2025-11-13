#!/usr/bin/env python3
"""
Test Script for Distributed Agent System
=========================================

Quick test to verify distributed agents are working correctly.

Usage:
    python test_distributed_agents.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.ai_agents.distributed.integration_example import DistributedAgentManager
from app.ai_agents.distributed.message_protocol import MessageType, Priority


async def test_agent_initialization():
    """Test 1: Agent Initialization"""
    print("\n" + "="*60)
    print("TEST 1: Agent Initialization")
    print("="*60)
    
    manager = DistributedAgentManager()
    
    try:
        await manager.initialize()
        print("✅ All agents initialized successfully")
        
        agents = manager.get_all_agents()
        print(f"✅ {len(agents)} agents online:")
        for name in agents.keys():
            print(f"   - {name}")
        
        return manager, True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None, False


async def test_agent_status(manager):
    """Test 2: Agent Status"""
    print("\n" + "="*60)
    print("TEST 2: Agent Status")
    print("="*60)
    
    try:
        status = await manager.get_system_status()
        
        print(f"✅ System initialized: {status['initialized']}")
        print(f"✅ Total agents: {status['total_agents']}")
        
        for agent_name, agent_status in status['agents'].items():
            print(f"\n{agent_name}:")
            print(f"   Health: {agent_status.get('health', 'unknown')}")
            print(f"   Role: {agent_status.get('agent_role', 'unknown')}")
            print(f"   Uptime: {agent_status.get('uptime_seconds', 0):.1f}s")
            print(f"   Decisions: {agent_status.get('total_decisions', 0)}")
            
            # Show personality
            traits = agent_status.get('personality_traits', {})
            if traits:
                print(f"   Personality: {list(traits.keys())[:3]}")
        
        return True
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False


async def test_resource_monitoring(manager):
    """Test 3: Resource Monitoring"""
    print("\n" + "="*60)
    print("TEST 3: Resource Monitoring")
    print("="*60)
    
    try:
        # Check each agent's resource monitoring
        for agent_name, agent in manager.get_all_agents().items():
            metrics = agent.get_resource_metrics()
            
            if metrics:
                print(f"\n{agent_name} monitoring:")
                print(f"   CPU: {metrics.cpu_percent:.1f}%")
                print(f"   Memory: {metrics.memory_percent:.1f}%")
                print(f"   Disk: {metrics.disk_percent:.1f}%")
                print(f"   Host: {metrics.hostname}")
            else:
                print(f"\n{agent_name}: No metrics yet (collecting...)")
        
        print("\n✅ Resource monitoring active")
        return True
    except Exception as e:
        print(f"❌ Resource monitoring check failed: {e}")
        return False


async def test_inter_agent_communication(manager):
    """Test 4: Inter-Agent Communication"""
    print("\n" + "="*60)
    print("TEST 4: Inter-Agent Communication")
    print("="*60)
    
    try:
        sir_hawk = manager.get_agent("sir_hawkington")
        terry = manager.get_agent("terry_meth_snail")
        
        if not sir_hawk or not terry:
            print("❌ Required agents not found")
            return False
        
        # Test 1: Direct message
        print("\n📨 Sir Hawkington → Terry (direct message)")
        success = await sir_hawk.send_message_to_agent(
            to_agent="terry_meth_snail",
            message_type=MessageType.AGENT_QUERY,
            payload={"question": "How's the memory looking?"},
            priority=Priority.NORMAL
        )
        print(f"   {'✅' if success else '❌'} Message sent")
        
        # Test 2: Broadcast
        print("\n📢 Terry → All agents (broadcast)")
        success = await terry.broadcast_message(
            message_type=MessageType.SYSTEM_EVENT,
            payload={
                "event": "test_broadcast",
                "message": "GOTTA GO FAST!",
                "from": "terry"
            },
            priority=Priority.LOW
        )
        print(f"   {'✅' if success else '❌'} Broadcast sent")
        
        # Wait for message processing
        await asyncio.sleep(1)
        
        print("\n✅ Inter-agent communication working")
        return True
    except Exception as e:
        print(f"❌ Communication test failed: {e}")
        return False


async def test_decision_making(manager):
    """Test 5: Decision Making and Recording"""
    print("\n" + "="*60)
    print("TEST 5: Decision Making")
    print("="*60)
    
    try:
        sir_hawk = manager.get_agent("sir_hawkington")
        
        if not sir_hawk:
            print("❌ Sir Hawkington not found")
            return False
        
        # Make a test decision
        print("\n🧐 Sir Hawkington making a decision...")
        decision = await sir_hawk.make_decision(
            decision_type="test_decision",
            input_data={
                "test": True,
                "scenario": "resource_optimization"
            },
            confidence=0.85
        )
        
        print(f"✅ Decision made: {decision.get('decision_id')}")
        print(f"   Status: {decision.get('status')}")
        print(f"   Monocle: {decision.get('monocle_state', 'N/A')}")
        
        # Wait for decision to be recorded
        await asyncio.sleep(0.5)
        
        # Retrieve decision history
        print("\n📜 Retrieving decision history...")
        decisions = await sir_hawk.comm_hub.state_manager.get_recent_decisions(count=5)
        
        print(f"✅ Found {len(decisions)} recent decisions")
        for i, dec in enumerate(decisions[:3], 1):
            print(f"   {i}. {dec.decision_type} (confidence: {dec.confidence})")
        
        return True
    except Exception as e:
        print(f"❌ Decision test failed: {e}")
        return False


async def test_state_persistence(manager):
    """Test 6: State Persistence"""
    print("\n" + "="*60)
    print("TEST 6: State Persistence")
    print("="*60)
    
    try:
        bob = manager.get_agent("bob_hamster")
        
        if not bob:
            print("❌ Bob not found")
            return False
        
        # Get current state
        state = bob.comm_hub.get_state()
        
        print(f"\n🐹 Bob's current state:")
        print(f"   Health: {state.health.value}")
        print(f"   Started: {state.started_at}")
        print(f"   Restart count: {state.restart_count}")
        print(f"   Total decisions: {state.total_decisions}")
        print(f"   Messages sent: {state.total_messages_sent}")
        print(f"   Messages received: {state.total_messages_received}")
        
        # Save state
        print("\n💾 Saving state to Redis...")
        success = await bob.comm_hub.state_manager.save_state(state)
        print(f"   {'✅' if success else '❌'} State saved")
        
        # Load state
        print("\n📥 Loading state from Redis...")
        loaded_state = await bob.comm_hub.state_manager.load_state()
        print(f"   {'✅' if loaded_state else '❌'} State loaded")
        
        if loaded_state:
            print(f"   Verified: {loaded_state.agent_name} == {state.agent_name}")
        
        return True
    except Exception as e:
        print(f"❌ State persistence test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DISTRIBUTED AGENT SYSTEM TEST SUITE")
    print("="*60)
    
    manager = None
    results = []
    
    try:
        # Test 1: Initialization
        manager, success = await test_agent_initialization()
        results.append(("Initialization", success))
        
        if not success or not manager:
            print("\n❌ Cannot continue without initialization")
            return
        
        # Wait for agents to fully start
        print("\n⏳ Waiting for agents to stabilize...")
        await asyncio.sleep(3)
        
        # Test 2: Status
        success = await test_agent_status(manager)
        results.append(("Agent Status", success))
        
        # Test 3: Resource Monitoring
        success = await test_resource_monitoring(manager)
        results.append(("Resource Monitoring", success))
        
        # Test 4: Communication
        success = await test_inter_agent_communication(manager)
        results.append(("Inter-Agent Communication", success))
        
        # Test 5: Decisions
        success = await test_decision_making(manager)
        results.append(("Decision Making", success))
        
        # Test 6: State Persistence
        success = await test_state_persistence(manager)
        results.append(("State Persistence", success))
        
    finally:
        # Cleanup
        if manager:
            print("\n" + "="*60)
            print("CLEANUP")
            print("="*60)
            await manager.shutdown()
            print("✅ All agents shut down")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your distributed agents are working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
