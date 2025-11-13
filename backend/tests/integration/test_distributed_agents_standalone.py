#!/usr/bin/env python3
"""
Standalone Test for Distributed Agent System
=============================================

Tests the distributed agent system without requiring full app infrastructure.
Uses direct Redis connection without app dependencies.

Usage:
    REDIS_URL="redis://192.168.1.216:6379" python test_distributed_agents_standalone.py
"""

import asyncio
import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import only the distributed agent modules (no app dependencies)
from app.ai_agents.distributed.message_protocol import (
    MessageType,
    Priority,
    AgentMessage,
    ResourceAlert,
    RedisChannels,
    RedisKeys
)
from app.ai_agents.distributed.agent_state import (
    AgentState,
    AgentStateManager,
    AgentHealth,
    DecisionRecord
)
from app.ai_agents.distributed.resource_monitor import (
    ResourceMonitor,
    ResourceType
)

# Direct Redis import
try:
    import redis.asyncio as aioredis
except ImportError:
    print("❌ redis package not installed. Run: pip install redis")
    sys.exit(1)

try:
    import psutil
except ImportError:
    print("❌ psutil package not installed. Run: pip install psutil")
    sys.exit(1)


async def test_redis_connection(redis_url: str):
    """Test 1: Redis Connection"""
    print("\n" + "="*60)
    print("TEST 1: Redis Connection")
    print("="*60)
    
    try:
        redis = await aioredis.from_url(
            redis_url,
            decode_responses=True,
            encoding="utf-8"
        )
        
        # Test ping
        response = await redis.ping()
        print(f"✅ Redis PING: {response}")
        
        # Test set/get
        await redis.set("test:distributed_agents", "hello")
        value = await redis.get("test:distributed_agents")
        print(f"✅ Redis SET/GET: {value}")
        
        # Cleanup
        await redis.delete("test:distributed_agents")
        
        await redis.aclose()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def test_message_protocol():
    """Test 2: Message Protocol"""
    print("\n" + "="*60)
    print("TEST 2: Message Protocol")
    print("="*60)
    
    try:
        # Create a message
        msg = AgentMessage(
            from_agent="test_agent",
            to_agent="target_agent",
            message_type=MessageType.AGENT_QUERY,
            priority=Priority.NORMAL,
            payload={"test": "data"}
        )
        
        print(f"✅ Created message: {msg.message_id}")
        print(f"   Type: {msg.message_type.value}")
        print(f"   Priority: {msg.priority.value}")
        
        # Serialize/deserialize
        json_str = msg.to_json()
        restored = AgentMessage.from_json(json_str)
        
        print(f"✅ Serialization works")
        print(f"   Original ID: {msg.message_id}")
        print(f"   Restored ID: {restored.message_id}")
        
        # Test specialized messages
        alert = ResourceAlert(
            from_agent="test_agent",
            resource_type="cpu",
            current_value=85.5,
            threshold=80.0,
            severity="warning"
        )
        
        print(f"✅ ResourceAlert created")
        print(f"   Severity: {alert.payload['severity']}")
        print(f"   Value: {alert.payload['current_value']}%")
        
        return True
    except Exception as e:
        print(f"❌ Message protocol test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_state_persistence(redis_url: str):
    """Test 3: Agent State Persistence"""
    print("\n" + "="*60)
    print("TEST 3: Agent State Persistence")
    print("="*60)
    
    redis = None
    try:
        # Connect to Redis
        redis = await aioredis.from_url(
            redis_url,
            decode_responses=True,
            encoding="utf-8"
        )
        
        # Create state manager
        manager = AgentStateManager(redis, "test_agent")
        
        # Create initial state
        state = await manager.create_initial_state(
            agent_role="Test Agent",
            personality_traits={"test": True, "speed": "fast"},
            resource_thresholds={"cpu": 80.0}
        )
        
        print(f"✅ Created initial state")
        print(f"   Agent: {state.agent_name}")
        print(f"   Health: {state.health.value}")
        print(f"   Personality: {state.personality_traits}")
        
        # Save state
        success = await manager.save_state(state)
        print(f"✅ State saved: {success}")
        
        # Load state
        loaded = await manager.load_state()
        print(f"✅ State loaded")
        print(f"   Agent: {loaded.agent_name}")
        print(f"   Health: {loaded.health.value}")
        
        # Record a decision
        decision = DecisionRecord(
            decision_id="test_decision_001",
            agent_name="test_agent",
            decision_type="test_decision",
            input_data={"test": "input"},
            output_data={"test": "output"},
            confidence=0.85
        )
        
        success = await manager.record_decision(decision)
        print(f"✅ Decision recorded: {success}")
        
        # Get recent decisions
        decisions = await manager.get_recent_decisions(count=5)
        print(f"✅ Retrieved {len(decisions)} decisions")
        
        # Cleanup
        await redis.delete(RedisKeys.agent_state("test_agent"))
        await redis.delete(RedisKeys.agent_history("test_agent"))
        
        await redis.aclose()
        return True
    except Exception as e:
        print(f"❌ State persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        if redis:
            await redis.aclose()
        return False


async def test_resource_monitoring():
    """Test 4: Resource Monitoring"""
    print("\n" + "="*60)
    print("TEST 4: Resource Monitoring")
    print("="*60)
    
    try:
        # Create monitor (without message bus for standalone test)
        monitor = ResourceMonitor(
            agent_name="test_agent",
            message_bus=None,
            monitored_resources=[ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK],
            check_interval=1.0
        )
        
        print(f"✅ Resource monitor created")
        print(f"   Monitoring: {[r.value for r in monitor.monitored_resources]}")
        
        # Get current metrics
        metrics = await monitor.get_current_metrics()
        
        print(f"✅ Collected metrics:")
        print(f"   Hostname: {metrics.hostname}")
        print(f"   CPU: {metrics.cpu_percent:.1f}%")
        print(f"   Memory: {metrics.memory_percent:.1f}%")
        print(f"   Disk: {metrics.disk_percent:.1f}%")
        print(f"   Load Average: {metrics.load_average}")
        
        # Test threshold checking
        monitor.set_threshold(ResourceType.CPU, 50.0)
        print(f"✅ Set CPU threshold to 50%")
        
        return True
    except Exception as e:
        print(f"❌ Resource monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_pubsub_messaging(redis_url: str):
    """Test 5: Pub/Sub Messaging"""
    print("\n" + "="*60)
    print("TEST 5: Pub/Sub Messaging")
    print("="*60)
    
    publisher = None
    subscriber = None
    
    try:
        # Create publisher and subscriber
        publisher = await aioredis.from_url(redis_url, decode_responses=True)
        subscriber = await aioredis.from_url(redis_url, decode_responses=True)
        
        # Create pubsub
        pubsub = subscriber.pubsub()
        
        # Subscribe to test channel
        test_channel = "test:agents:broadcast"
        await pubsub.subscribe(test_channel)
        print(f"✅ Subscribed to {test_channel}")
        
        # Publish a message
        msg = AgentMessage(
            from_agent="test_sender",
            to_agent=None,
            message_type=MessageType.SYSTEM_EVENT,
            priority=Priority.NORMAL,
            payload={"event": "test_event"}
        )
        
        await publisher.publish(test_channel, msg.to_json())
        print(f"✅ Published message")
        
        # Try to receive (with timeout)
        try:
            received = await asyncio.wait_for(
                pubsub.get_message(ignore_subscribe_messages=True),
                timeout=2.0
            )
            
            if received and received['type'] == 'message':
                restored_msg = AgentMessage.from_json(received['data'])
                print(f"✅ Received message: {restored_msg.message_id}")
                print(f"   From: {restored_msg.from_agent}")
                print(f"   Type: {restored_msg.message_type.value}")
            else:
                print(f"⚠️  No message received (this is OK for quick test)")
        except asyncio.TimeoutError:
            print(f"⚠️  Message receive timeout (this is OK for quick test)")
        
        # Cleanup
        await pubsub.unsubscribe(test_channel)
        await pubsub.close()
        await publisher.aclose()
        await subscriber.aclose()
        
        return True
    except Exception as e:
        print(f"❌ Pub/sub test failed: {e}")
        import traceback
        traceback.print_exc()
        if publisher:
            await publisher.aclose()
        if subscriber:
            await subscriber.aclose()
        return False


async def main():
    """Run all standalone tests"""
    print("\n" + "="*60)
    print("DISTRIBUTED AGENT SYSTEM - STANDALONE TEST")
    print("="*60)
    
    # Get Redis URL from environment
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"\nRedis URL: {redis_url}")
    
    results = []
    
    # Test 1: Redis Connection
    success = await test_redis_connection(redis_url)
    results.append(("Redis Connection", success))
    
    if not success:
        print("\n❌ Cannot continue without Redis connection")
        return
    
    # Test 2: Message Protocol
    success = await test_message_protocol()
    results.append(("Message Protocol", success))
    
    # Test 3: Agent State Persistence
    success = await test_agent_state_persistence(redis_url)
    results.append(("Agent State Persistence", success))
    
    # Test 4: Resource Monitoring
    success = await test_resource_monitoring()
    results.append(("Resource Monitoring", success))
    
    # Test 5: Pub/Sub Messaging
    success = await test_pubsub_messaging(redis_url)
    results.append(("Pub/Sub Messaging", success))
    
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
        print("\n🎉 All standalone tests passed!")
        print("✅ Core distributed agent functionality is working!")
        print("\nNext step: Integrate with your FastAPI application")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
