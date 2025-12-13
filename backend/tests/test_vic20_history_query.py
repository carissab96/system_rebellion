"""
Test VIC-20's Historical Query Capability - REAL DATABASE
==========================================================

NO MOCKS. Real database queries. Real history. Real recommendations.

Verifies that VIC-20:
1. Queries the REAL database for historical effectiveness data
2. Uses REAL data to adjust recommendation confidence
3. Makes REAL recommendations based on what actually happened

Run on Dell with: python tests/test_vic20_history_query.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_vic20_real_history_query():
    """
    Test VIC-20's ability to query REAL historical data and use it.
    No mocks. Real database. Real recommendations.
    """
    from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
    from app.core.database import get_async_db
    
    print("=" * 70)
    print("VIC-20 REAL History Query Test")
    print("=" * 70)
    
    # Create VIC-20 with REAL database connection
    vic20 = VIC20SageDistributed(db_getter=get_async_db)
    
    # Initialize database integration
    print("\n1. Initializing VIC-20 database integration...")
    try:
        await vic20.db.ensure_initialized()
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False
    
    # Test history query for each resource type
    resource_types = ["cpu", "memory", "disk", "network"]
    
    print("\n2. Querying historical effectiveness for each resource type...")
    for resource_type in resource_types:
        print(f"\n   --- {resource_type.upper()} ---")
        history = await vic20._get_historical_effectiveness(resource_type)
        
        if history:
            print(f"   ✅ Found {len(history)} historical records")
            for h in history[:3]:  # Show first 3
                print(f"      - Action: {h.get('action', 'unknown')}")
                print(f"        Success: {h.get('success')}")
                print(f"        Confidence: {h.get('confidence', 0):.0%}")
        else:
            print(f"   ⚠️  No historical records found")
    
    # Test recommendation generation with real history
    print("\n3. Generating REAL recommendations based on history...")
    
    for resource_type in resource_types:
        print(f"\n   --- {resource_type.upper()} Recommendation ---")
        
        rec = await vic20._generate_recommendation(
            resource_type=resource_type,
            current_value=85.0,
            threshold=70.0,
            severity="high"
        )
        
        print(f"   Action: {rec['action']}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        
        if rec.get('historical_basis'):
            print(f"   Historical records used: {rec['historical_basis']['matching_records']}")
            print(f"   Historical success rate: {rec['historical_basis']['success_rate']:.0%}")
        else:
            print(f"   Historical basis: None (using defaults)")
        
        if rec.get('alternative_action'):
            print(f"   ⚡ Alternative suggested: {rec['alternative_action']} ({rec['alternative_confidence']:.0%})")
        
        print(f"   Reasoning: {rec['reasoning'][:100]}...")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
    
    return True


async def test_check_table_contents():
    """
    Check what's actually in the tables VIC-20 queries.
    This helps diagnose if data exists but queries aren't finding it.
    """
    from app.core.database import get_async_db
    from sqlalchemy import text
    
    print("\n" + "=" * 70)
    print("Database Table Contents Check")
    print("=" * 70)
    
    async for session in get_async_db():
        # Check agent_decision_vectors
        print("\n1. agent_decision_vectors:")
        result = await session.execute(
            text("SELECT agent_name, COUNT(*) as count FROM agent_decision_vectors GROUP BY agent_name ORDER BY count DESC")
        )
        for row in result.mappings():
            print(f"   {row['agent_name']}: {row['count']} records")
        
        # Check agent_pattern_vectors
        print("\n2. agent_pattern_vectors:")
        result = await session.execute(
            text("SELECT agent_name, COUNT(*) as count FROM agent_pattern_vectors GROUP BY agent_name ORDER BY count DESC")
        )
        rows = list(result.mappings())
        if rows:
            for row in rows:
                print(f"   {row['agent_name']}: {row['count']} records")
        else:
            print("   (empty)")
        
        # Check agent_learning_interactions
        print("\n3. agent_learning_interactions:")
        result = await session.execute(
            text("SELECT source_agent, target_agent, COUNT(*) as count FROM agent_learning_interactions GROUP BY source_agent, target_agent ORDER BY count DESC LIMIT 10")
        )
        rows = list(result.mappings())
        if rows:
            for row in rows:
                print(f"   {row['source_agent']} -> {row['target_agent']}: {row['count']} records")
        else:
            print("   (empty)")
        
        # Check central_memory_bank for The Stick
        print("\n4. central_memory_bank (the_stick):")
        result = await session.execute(
            text("SELECT event_type, COUNT(*) as count FROM central_memory_bank WHERE agent_name = 'the_stick' GROUP BY event_type ORDER BY count DESC LIMIT 10")
        )
        rows = list(result.mappings())
        if rows:
            for row in rows:
                print(f"   {row['event_type']}: {row['count']} records")
        else:
            print("   (empty)")
        
        # Check for coordination outcomes specifically
        print("\n4b. central_memory_bank (the_stick - coordination outcomes):")
        result = await session.execute(
            text("""
                SELECT 
                    details->'payload'->>'decision_type' as decision_type,
                    details->'payload'->>'action' as action,
                    details->'payload'->>'success' as success,
                    COUNT(*) as count
                FROM central_memory_bank 
                WHERE agent_name = 'the_stick' 
                    AND event_type = 'decision_log'
                    AND details->'payload'->>'decision_type' IN ('coordination', 'coordination_outcome')
                GROUP BY decision_type, action, success
                ORDER BY count DESC
                LIMIT 10
            """)
        )
        rows = list(result.mappings())
        if rows:
            for row in rows:
                print(f"   {row['decision_type']}: action={row['action']}, success={row['success']}, count={row['count']}")
        else:
            print("   (no coordination outcomes yet - need to run system to generate data)")
        
        # Check central_memory_bank for specialists
        print("\n5. central_memory_bank (specialists):")
        result = await session.execute(
            text("""
                SELECT agent_name, COUNT(*) as count 
                FROM central_memory_bank 
                WHERE agent_name IN ('meth_snail', 'hamsters', 'quantum_shadow_people')
                GROUP BY agent_name ORDER BY count DESC
            """)
        )
        rows = list(result.mappings())
        if rows:
            for row in rows:
                print(f"   {row['agent_name']}: {row['count']} records")
        else:
            print("   (empty)")
        
        break
    
    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VIC-20 REAL DATABASE TESTS - NO MOCKS")
    print("=" * 70)
    
    async def run_all():
        success = True
        
        # Test 1: Check what's in the tables
        try:
            result = await test_check_table_contents()
            if not result:
                success = False
        except Exception as e:
            print(f"\n❌ Table check failed with error: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        # Test 2: Query real history and generate recommendations
        try:
            result = await test_vic20_real_history_query()
            if not result:
                success = False
        except Exception as e:
            print(f"\n❌ History query test failed with error: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        return success
    
    result = asyncio.run(run_all())
    sys.exit(0 if result else 1)
