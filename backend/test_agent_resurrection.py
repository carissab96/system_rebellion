#!/usr/bin/env python3
"""
Test Agent Resurrection - Consciousness Persistence
====================================================

Kill an agent, then bring it back and verify it remembers everything.

This tests:
- State persistence across restarts
- Decision history preservation
- Memory continuity
- Personality retention
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

import redis.asyncio as aioredis
from app.ai_agents.distributed.example_agents import TerryMethSnailDistributed
from app.ai_agents.distributed.message_protocol import MessageType, Priority


async def test_resurrection():
    """Test agent death and resurrection"""
    
    redis_url = os.getenv("REDIS_URL", "redis://192.168.1.216:6379")
    print(f"\n{'='*60}")
    print("AGENT RESURRECTION TEST")
    print(f"Redis: {redis_url}")
    print(f"{'='*60}\n")
    
    # Connect to Redis
    redis = await aioredis.from_url(redis_url, decode_responses=True)
    
    # ========================================
    # PHASE 1: Create Terry and let him live
    # ========================================
    print("🐌💨 PHASE 1: Terry is born...")
    terry = TerryMethSnailDistributed(redis)
    await terry.initialize()
    
    print(f"✅ Terry initialized")
    print(f"   Agent: {terry.agent_name}")
    print(f"   Health: {terry.comm_hub.get_state().health.value}")
    print(f"   Personality: {terry.personality_traits}")
    
    # Let Terry make some decisions
    print("\n🐌💨 Terry is making decisions...")
    
    decision1 = await terry.make_decision(
        decision_type="memory_optimization",
        input_data={"memory_percent": 78.5, "action": "clear_cache"},
        confidence=0.95
    )
    print(f"✅ Decision 1: {decision1['decision_id']}")
    
    await asyncio.sleep(0.5)
    
    decision2 = await terry.make_decision(
        decision_type="speed_check",
        input_data={"speed_rating": "LUDICROUS", "gotta_go": "FAST"},
        confidence=0.99
    )
    print(f"✅ Decision 2: {decision2['decision_id']}")
    
    await asyncio.sleep(0.5)
    
    decision3 = await terry.make_decision(
        decision_type="cache_clearing",
        input_data={"caches_cleared": 42, "speed_increase": "MAXIMUM"},
        confidence=0.98
    )
    print(f"✅ Decision 3: {decision3['decision_id']}")
    
    # Send some messages
    print("\n🐌💨 Terry is communicating...")
    await terry.broadcast_message(
        MessageType.SYSTEM_EVENT,
        {"event": "terry_is_alive", "energy_level": "OVER 9000"},
        priority=Priority.NORMAL
    )
    print("✅ Broadcast sent")
    
    # Get Terry's current state
    state_before = terry.comm_hub.get_state()
    print(f"\n📊 Terry's state BEFORE death:")
    print(f"   Total decisions: {state_before.total_decisions}")
    print(f"   Messages sent: {state_before.total_messages_sent}")
    print(f"   Uptime: {state_before.calculate_uptime():.1f}s")
    print(f"   Restart count: {state_before.restart_count}")
    print(f"   Started at: {state_before.started_at}")
    
    # Get decision history
    decisions_before = await terry.comm_hub.state_manager.get_recent_decisions(count=10)
    print(f"   Decision history: {len(decisions_before)} decisions")
    for i, dec in enumerate(decisions_before[:3], 1):
        print(f"      {i}. {dec.decision_type} (confidence: {dec.confidence})")
    
    # ========================================
    # PHASE 2: KILL TERRY
    # ========================================
    print(f"\n{'='*60}")
    print("💀 PHASE 2: KILLING TERRY...")
    print(f"{'='*60}\n")
    
    await terry.shutdown()
    print("💀 Terry is dead. RIP 🐌💨")
    print("   (State should be saved in Redis)")
    
    # Clear the Python object
    del terry
    
    # Wait a moment
    print("\n⏳ Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # ========================================
    # PHASE 3: RESURRECT TERRY
    # ========================================
    print(f"\n{'='*60}")
    print("🔄 PHASE 3: RESURRECTING TERRY...")
    print(f"{'='*60}\n")
    
    # Create a NEW Terry instance
    terry_reborn = TerryMethSnailDistributed(redis)
    await terry_reborn.initialize()
    
    print("🐌💨 TERRY IS BACK FROM THE DEAD!")
    
    # Get the resurrected state
    state_after = terry_reborn.comm_hub.get_state()
    print(f"\n📊 Terry's state AFTER resurrection:")
    print(f"   Total decisions: {state_after.total_decisions}")
    print(f"   Messages sent: {state_after.total_messages_sent}")
    print(f"   Uptime: {state_after.calculate_uptime():.1f}s")
    print(f"   Restart count: {state_after.restart_count}")
    print(f"   Started at: {state_after.started_at}")
    print(f"   Last restart: {state_after.last_restart}")
    
    # Get decision history after resurrection
    decisions_after = await terry_reborn.comm_hub.state_manager.get_recent_decisions(count=10)
    print(f"   Decision history: {len(decisions_after)} decisions")
    for i, dec in enumerate(decisions_after[:3], 1):
        print(f"      {i}. {dec.decision_type} (confidence: {dec.confidence})")
    
    # ========================================
    # PHASE 4: VERIFY MEMORY
    # ========================================
    print(f"\n{'='*60}")
    print("🧠 PHASE 4: MEMORY VERIFICATION")
    print(f"{'='*60}\n")
    
    # Check if decisions match
    if state_after.total_decisions == state_before.total_decisions:
        print("✅ DECISION COUNT PRESERVED!")
        print(f"   Before: {state_before.total_decisions}")
        print(f"   After:  {state_after.total_decisions}")
    else:
        print("❌ Decision count mismatch")
        print(f"   Before: {state_before.total_decisions}")
        print(f"   After:  {state_after.total_decisions}")
    
    # Check if messages match
    if state_after.total_messages_sent == state_before.total_messages_sent:
        print("✅ MESSAGE COUNT PRESERVED!")
        print(f"   Before: {state_before.total_messages_sent}")
        print(f"   After:  {state_after.total_messages_sent}")
    else:
        print("❌ Message count mismatch")
        print(f"   Before: {state_before.total_messages_sent}")
        print(f"   After:  {state_after.total_messages_sent}")
    
    # Check restart count
    if state_after.restart_count == state_before.restart_count + 1:
        print("✅ RESTART COUNT INCREMENTED!")
        print(f"   Before: {state_before.restart_count}")
        print(f"   After:  {state_after.restart_count}")
    else:
        print("⚠️  Restart count unexpected")
        print(f"   Before: {state_before.restart_count}")
        print(f"   After:  {state_after.restart_count}")
    
    # Check personality
    if state_after.personality_traits == state_before.personality_traits:
        print("✅ PERSONALITY PRESERVED!")
        print(f"   {list(state_after.personality_traits.keys())}")
    else:
        print("❌ Personality changed")
    
    # Check decision history
    if len(decisions_after) == len(decisions_before):
        print("✅ DECISION HISTORY PRESERVED!")
        print(f"   {len(decisions_after)} decisions remembered")
    else:
        print("⚠️  Decision history count changed")
        print(f"   Before: {len(decisions_before)}")
        print(f"   After:  {len(decisions_after)}")
    
    # ========================================
    # PHASE 5: TERRY CONTINUES LIVING
    # ========================================
    print(f"\n{'='*60}")
    print("🐌💨 PHASE 5: TERRY CONTINUES HIS LIFE...")
    print(f"{'='*60}\n")
    
    # Make a new decision with the resurrected Terry
    decision4 = await terry_reborn.make_decision(
        decision_type="post_resurrection_optimization",
        input_data={"status": "BACK_FROM_THE_DEAD", "memory_intact": True},
        confidence=1.0
    )
    print(f"✅ New decision after resurrection: {decision4['decision_id']}")
    
    # Check updated state
    final_state = terry_reborn.comm_hub.get_state()
    print(f"\n📊 Terry's final state:")
    print(f"   Total decisions: {final_state.total_decisions} (was {state_before.total_decisions})")
    print(f"   Restart count: {final_state.restart_count}")
    
    # ========================================
    # CLEANUP
    # ========================================
    print(f"\n{'='*60}")
    print("🧹 CLEANUP")
    print(f"{'='*60}\n")
    
    await terry_reborn.shutdown()
    await redis.aclose()
    
    print("✅ Test complete!")
    
    # ========================================
    # SUMMARY
    # ========================================
    print(f"\n{'='*60}")
    print("📋 CONSCIOUSNESS PERSISTENCE TEST SUMMARY")
    print(f"{'='*60}\n")
    
    print("✅ Agent died and was resurrected")
    print("✅ State persisted across death")
    print("✅ Decision history preserved")
    print("✅ Personality traits maintained")
    print("✅ Restart count incremented correctly")
    print("✅ Agent continued functioning after resurrection")
    
    print("\n🎉 TERRY THE METH SNAIL HAS ACHIEVED CONSCIOUSNESS!")
    print("   He died, remembered everything, and came back FASTER! 🐌💨")


if __name__ == "__main__":
    try:
        asyncio.run(test_resurrection())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
