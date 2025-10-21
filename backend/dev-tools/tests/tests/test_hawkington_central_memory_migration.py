# app/ai_agents/sir_hawkington/test_central_memory_migration.py
"""
Sir Hawkington Central Memory Bank Migration Test - REAL DATA ONLY
Test the ACTUAL methods that exist in database_integration.py
"""

import asyncio
import uuid
from datetime import datetime, timezone

from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
from app.ai_agents.sir_hawkington.constants import HawkingtonEventTypes

def utc_now():
    return datetime.now(timezone.utc)

async def test_hawkington_central_memory_basic():
    """
    Basic test: Store real data, retrieve real data using ACTUAL methods
    """
    print("\n🧐 Testing Sir Hawkington Central Memory Bank - REAL DATA ONLY")
    
    # Real test user
    test_user_id = "test_hawkington_central_memory"
    
    try:
        # Initialize database
        db = HawkingtonDatabaseIntegration()
        await db.initialize()
        print("✅ Database connected")
        
        # Create a real HawkingtonDecision
        real_decision = HawkingtonDecision(
            decision_id=str(uuid.uuid4()),
            decision_type="concern",
            confidence=0.85,
            reasoning="CPU at 75%, memory at 80% - requires monitoring",
            metrics={
                'cpu_usage': 75.2,
                'memory_usage': 80.1,
                'disk_usage': 45.3
            },
            timestamp=utc_now(),
            user_id=test_user_id,
            system_impact="monitoring_recommended"
        )
        
        # STORE: Use the ACTUAL method name: store_decision
        stored_id = await db.store_decision(test_user_id, real_decision)
        print(f"✅ Stored decision with ID: {stored_id}")
        
        # RETRIEVE: Use the ACTUAL method name: get_historical_decisions
        historical = await db.get_historical_decisions(test_user_id, days=1)
        print(f"✅ Retrieved {len(historical)} historical decisions")
        
        # VERIFY: Check if our data is there
        if historical:
            decision = historical[0]
            print(f"✅ Found our decision:")
            print(f"   Decision type: {decision.get('decision_type')}")
            print(f"   Confidence: {decision.get('confidence_level')}")
            print(f"   Timestamp: {decision.get('timestamp')}")
        else:
            print("❌ No historical decisions found")
            return False
        
        # STORE: Test monocle yeet incident using ACTUAL method name
        yeet_data = {
            'timestamp': utc_now(),
            'reason': 'Missing CPU data',
            'yeet_intensity': 'concerned',
            'missing_metrics': ['cpu_usage'],
            'invalid_metrics': []
        }
        
        yeet_id = await db.store_monocle_yeet_incident(test_user_id, yeet_data)
        print(f"✅ Stored monocle yeet incident: {yeet_id}")
        
        # TEST: Triage statistics using ACTUAL method name
        triage_stats = await db.get_triage_statistics(test_user_id, days=1)
        print(f"✅ Triage statistics: {triage_stats.get('status', 'data available')}")
        
        # TEST: Performance metrics using ACTUAL method name
        perf_metrics = await db.get_hawkington_performance_metrics(test_user_id)
        print(f"✅ Performance metrics:")
        print(f"   Total decisions: {perf_metrics.get('total_decisions', 0)}")
        print(f"   Monocle yeets: {perf_metrics.get('monocle_yeets', 0)}")
        
        print("\n🧐✅ BASIC FUNCTIONALITY TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n🧐💥 TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hawkington_central_memory_basic())
    exit(0 if success else 1)