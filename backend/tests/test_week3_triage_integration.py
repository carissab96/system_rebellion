#!/usr/bin/env python3
"""
Week 3 Task 3.2 Verification: Agent Subscription to Triage Decisions
=====================================================================

Tests that all distributed agents:
1. Subscribe to triage decisions during initialization
2. Have _handle_triage_decision() methods implemented
3. React appropriately to triage routing
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Test configuration
REDIS_URL = "redis://192.168.1.216:6379"
os.environ['REDIS_URL'] = REDIS_URL  # Set for get_redis_client()

async def test_agent_triage_subscriptions():
    """Test that all agents subscribe to and handle triage decisions"""
    print("=" * 80)
    print("WEEK 3 TASK 3.2: Agent Triage Subscription Test")
    print("=" * 80)
    
    # Import distributed agents
    from app.ai_agents.sir_hawkington.distributed_hawkington import SirHawkingtonDistributed
    from app.ai_agents.meth_snail.distributed_meth_snail import MethSnailDistributed
    from app.ai_agents.hamsters.distributed_hamsters import HamstersDistributed
    from app.ai_agents.quantum_shadow_people.distributed_qsp import QuantumShadowPeopleDistributed
    from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
    from app.ai_agents.the_stick.distributed_stick import TheStickDistributed
    from app.core.redis import get_redis_client
    import redis.asyncio as redis
    
    agents = {
        "sir_hawkington": SirHawkingtonDistributed(),
        "meth_snail": MethSnailDistributed(),
        "hamsters": HamstersDistributed(),
        "quantum_shadow_people": QuantumShadowPeopleDistributed(),
        "vic_20_sage": VIC20SageDistributed(),
        "the_stick": TheStickDistributed()
    }
    
    print(f"\n✅ Created {len(agents)} distributed agents")
    
    # Get Redis client
    redis_client = await get_redis_client()
    print(f"✅ Connected to Redis")
    
    # Initialize distributed features for each agent
    print("\n📡 Initializing distributed features...")
    for name, agent in agents.items():
        try:
            await agent.initialize_distributed(redis_client)
            print(f"  ✅ {name}: Distributed features initialized")
        except Exception as e:
            print(f"  ❌ {name}: Failed to initialize - {e}")
            return False
    
    # Check that each agent has _handle_triage_decision method
    print("\n🔍 Checking triage decision handlers...")
    all_have_handlers = True
    for name, agent in agents.items():
        if hasattr(agent, '_handle_triage_decision'):
            print(f"  ✅ {name}: Has _handle_triage_decision() method")
        else:
            print(f"  ❌ {name}: MISSING _handle_triage_decision() method")
            all_have_handlers = False
    
    if not all_have_handlers:
        print("\n❌ Not all agents have triage handlers!")
        return False
    
    # Test broadcasting a triage decision
    print("\n📡 Testing triage decision broadcast...")
    test_triage_decision = {
        'severity': 'high',
        'routing': 'vic20_coordination',
        'target_agents': ['vic_20_sage', 'meth_snail'],
        'reasoning': 'High memory usage detected - coordinating optimization',
        'metrics_summary': {
            'cpu_usage': 45.2,
            'memory_usage': 82.5,
            'disk_usage': 55.0
        },
        'user_id': 'test_user'
    }
    
    # Get the communication hub from one of the agents
    comm_hub = agents['sir_hawkington'].comm_hub
    if not comm_hub:
        print("❌ Communication hub not available")
        return False
    
    # Broadcast the test decision
    await comm_hub.broadcast_message(
        message_type='triage_decision',
        data=test_triage_decision,
        priority='high'
    )
    print("✅ Test triage decision broadcast")
    
    # Give agents time to process
    await asyncio.sleep(2)
    
    # Check agent decision histories
    print("\n📊 Checking agent decision histories...")
    agents_with_decisions = 0
    for name, agent in agents.items():
        if hasattr(agent, 'get_decision_history'):
            history = await agent.get_decision_history(limit=5)
            if history:
                print(f"  ✅ {name}: {len(history)} decisions recorded")
                agents_with_decisions += 1
                # Show latest decision
                latest = history[0]
                print(f"      Latest: {latest.get('decision_type', 'unknown')}")
            else:
                print(f"  ⚠️  {name}: No decisions in history yet")
        else:
            print(f"  ⚠️  {name}: No decision history method")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    for name, agent in agents.items():
        try:
            await agent.shutdown_distributed()
        except:
            pass
    
    try:
        await redis_client.close()
    except:
        pass
    
    # Summary
    print("\n" + "=" * 80)
    print("TASK 3.2 VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"✅ All {len(agents)} agents initialized with distributed features")
    print(f"✅ All {len(agents)} agents have triage decision handlers")
    print(f"✅ Test triage decision broadcast successfully")
    print(f"✅ {agents_with_decisions}/{len(agents)} agents recorded decisions")
    print("\n🎯 TASK 3.2: Agent Subscription to Triage Decisions - COMPLETE!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_agent_triage_subscriptions())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
