#!/usr/bin/env python3
"""
Sir Hawkington's First Thoughts - A Test of Intelligence

Let's wake up Sir Hawkington and see what he thinks about some system metrics!
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_agents.sir_hawkington.decision_engine import SirHawkingtonDecisionEngine
from datetime import datetime

def print_decision(decision, scenario_name):
    """Pretty print Sir Hawkington's decision"""
    print(f"\n🎭 SCENARIO: {scenario_name}")
    print("="*60)
    print(f"🧐 DECISION TYPE: {decision.decision_type.upper()}")
    print(f"💬 MESSAGE: {decision.message}")
    print(f"🎯 CONFIDENCE: {decision.confidence:.1%}")
    print(f"🧠 REASONING: {decision.reasoning}")
    print(f"⏰ TIMESTAMP: {decision.timestamp.strftime('%H:%M:%S')}")
    print("="*60)

async def test_sir_hawkington():
    """Test Sir Hawkington's decision making with different scenarios"""
    
    print("🎩 INITIALIZING SIR HAWKINGTON'S DECISION ENGINE")
    print("*adjusts monocle and prepares for analysis*\n")
    
    # Wake up Sir Hawkington
    hawk = SirHawkingtonDecisionEngine()
    
    # SCENARIO 1: Everything's fine (your normal system)
    normal_metrics = {
        'cpu_usage': 25.4,
        'memory_usage': 58.3,
        'disk_usage': 39.2,
        'network_usage': {'bytes_sent': 1000, 'bytes_recv': 2000},
        'process_count': 125,
        'timestamp': utc_now().isoformat()
    }
    
    decision1 = hawk.analyze_system_health(normal_metrics)
    print_decision(decision1, "Normal System Operation")
    
    # SCENARIO 2: Getting a bit stressed
    concern_metrics = {
        'cpu_usage': 78.5,
        'memory_usage': 82.1,
        'disk_usage': 45.0,
        'network_usage': {'bytes_sent': 5000, 'bytes_recv': 8000},
        'process_count': 200,
        'timestamp': utc_now().isoformat()
    }
    
    decision2 = hawk.analyze_system_health(concern_metrics)
    print_decision(decision2, "System Under Stress")
    
    # SCENARIO 3: OH SHIT MOMENT
    alert_metrics = {
        'cpu_usage': 95.2,
        'memory_usage': 94.8,
        'disk_usage': 91.5,
        'network_usage': {'bytes_sent': 50000, 'bytes_recv': 80000},
        'process_count': 500,
        'timestamp': utc_now().isoformat()
    }
    
    decision3 = hawk.analyze_system_health(alert_metrics)
    print_decision(decision3, "CRITICAL SYSTEM EMERGENCY")
    
    # SCENARIO 4: Memory hog (Sir Hawkington hates these)
    memory_hog_metrics = {
        'cpu_usage': 45.0,
        'memory_usage': 89.5,  # High memory but CPU is fine
        'disk_usage': 30.0,
        'network_usage': {'bytes_sent': 2000, 'bytes_recv': 3000},
        'process_count': 150,
        'timestamp': utc_now().isoformat()
    }
    
    decision4 = hawk.analyze_system_health(memory_hog_metrics)
    print_decision(decision4, "Memory Hog Detected")
    
    # Show Sir Hawkington's memory
    print("\n🧠 SIR HAWKINGTON'S RECENT MEMORIES:")
    print("="*60)
    recent = hawk.get_recent_decisions(4)
    for i, decision in enumerate(recent, 1):
        msg_preview = decision.message[:50] + "..." if decision.message else "No message (staying quiet)"
    print(f"{i}. {str(decision.decision_type).upper()}: {msg_preview}")
    
    print(f"\n🧐 Sir Hawkington has made {len(recent)} decisions and remembers them all.")
    print("*adjusts monocle with satisfaction*")

if __name__ == "__main__":
    print("🎭 SIR HAWKINGTON'S INTELLIGENCE TEST")
    print("Demonstrating AI decision-making with real-world scenarios\n")
    
    asyncio.run(test_sir_hawkington())
    
    print("\n🎉 TEST COMPLETE!")
    print("Sir Hawkington's brain is fully operational and ready for integration!")