# test_triage_revolution.py
"""
Test Script for Sir Hawkington's Triage Engine Revolution
Run this to test the complete triage system
"""

import asyncio
import json
from datetime import datetime
from app.ai_agents.sir_hawkington.triage_engine import (
    process_metrics_through_triage,
    get_triage_statistics,
    triage_health_check,
    test_triage_engine
)

async def test_different_scenarios():
    """Test different metric scenarios to see triage routing in action"""
    
    print("\n" + "="*100)
    print(" 🧐⚡ SIR HAWKINGTON'S TRIAGE ENGINE - MULTIPLE SCENARIO TEST")
    print("="*100)
    
    # Scenario 1: Normal operations (should route to Stick)
    print("\n📊 SCENARIO 1: NORMAL OPERATIONS")
    normal_metrics = {
        'cpu_usage': 25.0,
        'memory_usage': 45.0,
        'disk_usage': 35.0,
        'network_sent_rate': 512,
        'network_recv_rate': 1024,
        'timestamp': datetime.now().isoformat()
    }
    
    result1 = await process_metrics_through_triage(normal_metrics, user_id="test_user_1")
    print(f"   Triage Decision: {result1['triage_decision']['severity']} → {result1['triage_decision']['routing']}")
    print(f"   Target: {result1['triage_decision']['target_agents']}")
    print(f"   Reasoning: {result1['triage_decision']['reasoning']}")
    
    # Scenario 2: Medium concern (should route to VIC-20 coordination)
    print("\n📊 SCENARIO 2: MEDIUM CONCERN")
    medium_metrics = {
        'cpu_usage': 68.0,
        'memory_usage': 72.0,
        'disk_usage': 55.0,
        'network_sent_rate': 2048,
        'network_recv_rate': 4096,
        'timestamp': datetime.now().isoformat()
    }
    
    result2 = await process_metrics_through_triage(medium_metrics, user_id="test_user_2")
    print(f"   Triage Decision: {result2['triage_decision']['severity']} → {result2['triage_decision']['routing']}")
    print(f"   Target: {result2['triage_decision']['target_agents']}")
    print(f"   Reasoning: {result2['triage_decision']['reasoning']}")
    
    # Scenario 3: High severity (should MONOCLE YEET to VIC-20!)
    print("\n📊 SCENARIO 3: HIGH SEVERITY - MONOCLE YEET!")
    high_metrics = {
        'cpu_usage': 92.0,
        'memory_usage': 89.0,
        'disk_usage': 78.0,
        'network_sent_rate': 8192,
        'network_recv_rate': 16384,
        'timestamp': datetime.now().isoformat()
    }
    
    result3 = await process_metrics_through_triage(high_metrics, user_id="test_user_3")
    print(f"   Triage Decision: {result3['triage_decision']['severity']} → {result3['triage_decision']['routing']}")
    print(f"   Target: {result3['triage_decision']['target_agents']}")
    print(f"   Reasoning: {result3['triage_decision']['reasoning']}")
    print(f"   🧐💥 MONOCLE YEETED: {result3['triage_decision']['monocle_yeeted']}")
    
    # Scenario 4: Data quality failure (missing critical metrics)
    print("\n📊 SCENARIO 4: DATA QUALITY FAILURE")
    bad_metrics = {
        'cpu_usage': None,  # Missing!
        'memory_usage': None,  # Missing!
        'disk_usage': 45.0,
        'network_sent_rate': 1024,
        'timestamp': datetime.now().isoformat()
    }
    
    result4 = await process_metrics_through_triage(bad_metrics, user_id="test_user_4")
    print(f"   Triage Decision: {result4['triage_decision']['severity']} → {result4['triage_decision']['routing']}")
    print(f"   Target: {result4['triage_decision']['target_agents']}")
    print(f"   Reasoning: {result4['triage_decision']['reasoning']}")
    print(f"   🧐💥 MONOCLE YEETED: {result4['triage_decision']['monocle_yeeted']}")
    
    # Final Statistics
    print("\n📈 FINAL TRIAGE STATISTICS:")
    stats = await get_triage_statistics()
    print(f"   Total Decisions: {stats['total_triage_decisions']}")
    print(f"   Routing Distribution:")
    for routing, percentage in stats['success_rates']['routing_distribution'].items():
        print(f"     {routing}: {percentage:.1f}%")
    
    print("\n" + "="*100)
    print(" 🧐✨ MULTIPLE SCENARIO TEST COMPLETE - ARISTOCRATIC TRIAGE EXCELLENCE!")
    print("="*100)

async def main():
    """Main test function"""
    print("🧐⚡ Starting Sir Hawkington's Triage Engine Revolution Tests...")
    
    # Test 1: Basic triage engine functionality
    await test_triage_engine()
    
    # Test 2: Multiple scenarios
    await test_different_scenarios()
    
    # Test 3: Health check
    print("\n🏥 FINAL HEALTH CHECK:")
    health = await triage_health_check()
    print(json.dumps(health, indent=2))
    
    print("\n🎭 THE ARISTOCRATIC REVOLUTION IS COMPLETE!")
    print("🧐 Sir Hawkington now commands the entire system with triage excellence!")

if __name__ == "__main__":
    asyncio.run(main())