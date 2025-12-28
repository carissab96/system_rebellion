#!/usr/bin/env python3
"""
Week 4 Integration Demo

Demonstrates all Week 4 systems working together:
1. Alert Escalation (Task 4.2)
2. Action Verification (Task 4.3)
3. Cross-Agent Coordination (Task 4.4)
4. Resource Prediction (Task 4.5)

Shows a complete workflow from prediction → alert → coordination → action → verification
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai_agents.distributed.alert_escalation import (
    get_escalation_manager,
    AlertLevel,
    ResourceType as EscalationResourceType
)
from app.ai_agents.distributed.action_verification import (
    get_verification_manager,
    ActionType,
    ResourceType as VerificationResourceType,
    ResourceSnapshot
)
from app.ai_agents.distributed.coordination import (
    get_coordination_manager,
    CoordinationPriority,
    ResourceType as CoordinationResourceType,
    AgentCapability
)
from app.ai_agents.distributed.resource_prediction import (
    get_resource_predictor,
    ResourceType as PredictionResourceType,
    TrendDirection
)


def print_header(title: str):
    """Print a fancy header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print a section header"""
    print(f"\n--- {title} ---\n")


async def demo_prediction():
    """Demo: Resource Prediction"""
    print_header("🔮 TASK 4.5: RESOURCE PREDICTION")
    
    predictor = get_resource_predictor()
    
    print("Simulating memory usage trend...")
    print("Adding 10 measurements showing increasing memory usage:\n")
    
    # Simulate increasing memory usage
    base_time = datetime.now() - timedelta(minutes=5)
    for i in range(10):
        timestamp = base_time + timedelta(minutes=i * 0.5)
        value = 70.0 + (i * 2.0)  # Increasing by 4%/min
        predictor.add_measurement(PredictionResourceType.MEMORY, value, timestamp)
        print(f"  {i+1}. Time: {timestamp.strftime('%H:%M:%S')}, Memory: {value:.1f}%")
    
    print_section("Making Prediction")
    
    # Make prediction
    prediction = predictor.predict(
        PredictionResourceType.MEMORY,
        threshold=85.0,
        prediction_minutes=10.0
    )
    
    if prediction:
        print(f"📊 Current Memory: {prediction.current_value:.1f}%")
        print(f"📈 Trend: {prediction.trend_direction.value.upper()} ({prediction.trend_rate:+.2f}%/min)")
        print(f"🔮 Predicted in 10 min: {prediction.predicted_value:.1f}%")
        print(f"🎯 Confidence: {prediction.confidence:.0%}")
        
        if prediction.will_exceed_threshold:
            print(f"\n⚠️  WARNING: Will exceed {prediction.threshold_value}% threshold")
            print(f"⏰ Time to threshold: {prediction.time_to_threshold:.1f} minutes")
            print(f"🚨 PROACTIVE ALERT TRIGGERED!")
            return prediction
    
    return None


async def demo_alert_escalation(current_value: float):
    """Demo: Alert Escalation"""
    print_header("🚨 TASK 4.2: ALERT ESCALATION")
    
    manager = get_escalation_manager()
    
    print(f"Checking if we should alert for memory at {current_value:.1f}%...")
    
    should_alert, level, reason = manager.should_alert(
        EscalationResourceType.MEMORY,
        "demo_agent",
        current_value,
        85.0  # threshold
    )
    
    print(f"\n📋 Alert Decision: {'✅ ALERT' if should_alert else '🔇 SUPPRESS'}")
    print(f"📊 Alert Level: {level.upper() if level else 'N/A'}")
    print(f"💬 Reason: {reason}")
    
    if should_alert:
        print(f"\n🔥 {level.upper()} ALERT TRIGGERED!")
        print(f"   Memory: {current_value:.1f}% (threshold: 85.0%)")
        return level
    
    return None


async def demo_coordination(alert_level: str):
    """Demo: Cross-Agent Coordination"""
    print_header("🤝 TASK 4.4: CROSS-AGENT COORDINATION")
    
    manager = get_coordination_manager()
    
    # Register mock agent capabilities
    print("Registering agent capabilities...\n")
    
    async def terry_capability(resource_type, current_value):
        if resource_type == CoordinationResourceType.MEMORY:
            print("  🐌 Terry (Meth Snail): 'I can clear 20% memory!' (confidence: 85%)")
            return AgentCapability(
                agent_name="meth_snail",
                resource_type=resource_type,
                estimated_improvement=20.0,
                confidence=0.85,
                estimated_duration=2.0,
                action_name="cache_clear"
            )
        return None
    
    async def hamsters_capability(resource_type, current_value):
        if resource_type == CoordinationResourceType.MEMORY:
            print("  🐹 Hamsters: 'We can free 5% memory...' (confidence: 60%)")
            return AgentCapability(
                agent_name="hamsters",
                resource_type=resource_type,
                estimated_improvement=5.0,
                confidence=0.60,
                estimated_duration=3.0,
                action_name="disk_cleanup"
            )
        return None
    
    async def hawkington_capability(resource_type, current_value):
        print("  🧐 Sir Hawkington: 'Not my specialty, old chap.'")
        return None
    
    manager.register_agent_capability("meth_snail", terry_capability)
    manager.register_agent_capability("hamsters", hamsters_capability)
    manager.register_agent_capability("sir_hawkington", hawkington_capability)
    
    print_section("Requesting Coordination")
    
    # Map alert level to priority
    priority_map = {
        "info": CoordinationPriority.LOW,
        "warning": CoordinationPriority.NORMAL,
        "alert": CoordinationPriority.HIGH,
        "critical": CoordinationPriority.CRITICAL,
        "emergency": CoordinationPriority.EMERGENCY
    }
    
    priority = priority_map.get(alert_level, CoordinationPriority.NORMAL)
    
    print(f"📢 Requesting help: Memory crisis (priority: {priority.value})")
    
    request_id = await manager.request_coordination(
        resource_type=CoordinationResourceType.MEMORY,
        current_value=88.0,
        threshold=85.0,
        priority=priority,
        requesting_agent="demo_system"
    )
    
    print(f"📝 Coordination request ID: {request_id[:8]}...")
    
    # Wait for coordination to complete
    print("\n⏳ Waiting for coordination...")
    await asyncio.sleep(2.0)
    
    # Check status
    status = manager.get_request_status(request_id)
    
    if status:
        print(f"\n✅ Coordination Status: {status['status'].upper()}")
        print(f"👥 Selected Agents: {', '.join(status['selected_agents'])}")
        if status['total_improvement']:
            print(f"📈 Total Improvement: {status['total_improvement']:.1f}%")
        
        return status['selected_agents'][0] if status['selected_agents'] else None
    
    return None


async def demo_action_verification(agent_name: str):
    """Demo: Action Verification"""
    print_header("✅ TASK 4.3: ACTION VERIFICATION")
    
    manager = get_verification_manager()
    
    print(f"Agent '{agent_name}' is executing cache_clear action...\n")
    
    # Create before snapshot
    before_snapshot = ResourceSnapshot(
        timestamp=datetime.now(),
        cpu_percent=75.0,
        memory_percent=88.0,
        disk_percent=65.0,
        network_active_connections=50
    )
    
    print(f"📸 Before Snapshot:")
    print(f"   Memory: {before_snapshot.memory_percent:.1f}%")
    
    # Start verification
    verification_id = await manager.start_action_verification(
        action_id=f"demo_action_{datetime.now().timestamp()}",
        action_type=ActionType.CACHE_CLEAR,
        resource_type=VerificationResourceType.MEMORY,
        agent_name=agent_name,
        before_snapshot=before_snapshot
    )
    
    print(f"\n⏳ Executing action...")
    await asyncio.sleep(1.0)
    
    # Create after snapshot (simulating improvement)
    after_snapshot = ResourceSnapshot(
        timestamp=datetime.now(),
        cpu_percent=73.0,
        memory_percent=66.0,  # 22% improvement!
        disk_percent=64.0,
        network_active_connections=48
    )
    
    print(f"📸 After Snapshot:")
    print(f"   Memory: {after_snapshot.memory_percent:.1f}%")
    
    # Complete verification
    result = await manager.complete_action_verification(
        verification_id=verification_id,
        after_snapshot=after_snapshot
    )
    
    if result:
        print(f"\n📊 Verification Results:")
        print(f"   Improvement: {result.improvement_percent:.1f}%")
        print(f"   Effectiveness Score: {result.effectiveness_score:.0f}/100")
        print(f"   Effectiveness Level: {result.effectiveness_level.value.upper()}")
        print(f"   Duration: {result.duration_seconds:.2f}s")
        
        if result.was_highly_effective():
            print(f"\n🌟 HIGHLY EFFECTIVE! Agent is getting better!")
        
        return result
    
    return None


async def demo_full_integration():
    """Run the complete integration demo"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "WEEK 4 INTEGRATION DEMO" + " " * 35 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Demonstrating all 4 systems working together:" + " " * 27 + "║")
    print("║" + "  1. Resource Prediction (Task 4.5)" + " " * 43 + "║")
    print("║" + "  2. Alert Escalation (Task 4.2)" + " " * 46 + "║")
    print("║" + "  3. Cross-Agent Coordination (Task 4.4)" + " " * 38 + "║")
    print("║" + "  4. Action Verification (Task 4.3)" + " " * 43 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Step 1: Prediction
        prediction = await demo_prediction()
        
        if not prediction or not prediction.will_exceed_threshold:
            print("\n❌ No threshold crossing predicted. Demo requires increasing trend.")
            return
        
        await asyncio.sleep(1)
        
        # Step 2: Alert Escalation
        alert_level = await demo_alert_escalation(prediction.current_value)
        
        if not alert_level:
            print("\n❌ No alert triggered. Demo requires alert.")
            return
        
        await asyncio.sleep(1)
        
        # Step 3: Coordination
        selected_agent = await demo_coordination(alert_level)
        
        if not selected_agent:
            print("\n❌ No agent selected. Demo requires coordination.")
            return
        
        await asyncio.sleep(1)
        
        # Step 4: Verification
        result = await demo_action_verification(selected_agent)
        
        if not result:
            print("\n❌ Verification failed.")
            return
        
        # Final Summary
        print_header("🎉 INTEGRATION COMPLETE!")
        
        print("📋 Summary of Complete Workflow:\n")
        print(f"1. 🔮 PREDICTION detected memory will hit {prediction.threshold_value}% in {prediction.time_to_threshold:.1f}m")
        print(f"2. 🚨 ESCALATION triggered {alert_level.upper()} alert")
        print(f"3. 🤝 COORDINATION selected '{selected_agent}' as best responder")
        print(f"4. ✅ VERIFICATION confirmed {result.improvement_percent:.1f}% improvement ({result.effectiveness_level.value})")
        
        print(f"\n💪 Result: Crisis PREVENTED through proactive teamwork!")
        print(f"   Memory: {prediction.current_value:.1f}% → {result.after_snapshot.memory_percent:.1f}%")
        print(f"   Status: ✅ HEALTHY")
        
        print("\n" + "=" * 80)
        print("  ALL WEEK 4 SYSTEMS WORKING PERFECTLY! 🚀")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Week 4 Integration Demo...\n")
    asyncio.run(demo_full_integration())
