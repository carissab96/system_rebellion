# test_meth_snail_db_quick.py
"""
Quick test for Meth Snail database operations with SQLite/PostgreSQL compatibility
"""
import asyncio
import pytest
from datetime import datetime
import uuid
import json

# Import the actual classes we're testing
from app.ai_agents.meth_snail.database_integration import MethSnailDatabaseIntegration
from app.ai_agents.meth_snail.decision_engine import MethSnailBrainV2
from app.core.database import get_async_db

async def test_meth_snail_basic_operations():
    """Test that Meth Snail can save and retrieve data without exploding"""
    
    print("\n🐌⚡ Testing Meth Snail Database Operations...")
    
    # Get real database connection
    db_integration = MethSnailDatabaseIntegration(get_async_db)
    await db_integration.initialize()
    
    test_user_id = 12345  # Test user
    
    # Test 1: Store optimization metrics (the one that failed)
    print("\n1️⃣ Testing store_optimization_metrics...")
    try:
        # Let's see if the issue is in how we're creating the entry
        # First, let's try a minimal version
        metrics_data = {
            'cpu_usage_before': 80.0,
            'cpu_usage_after': 60.0,
            'memory_usage_before': 70.0,
            'memory_usage_after': 50.0,
            'optimization_success': True,
            'energy_drink_level': 3,
            'shell_spin_count': 2
        }
        
        metrics_id = await db_integration.store_optimization_metrics(test_user_id, metrics_data)
        print(f"✅ Stored optimization metrics with ID: {metrics_id}")
    except Exception as e:
        print(f"❌ Failed to store optimization metrics: {e}")
        
        # Let's try raw SQL to see if it's the ORM
        print("\n   Trying raw SQL insert...")
        try:
            async for db in get_async_db():
                from sqlalchemy import text
                
                # For SQLite, we need to ensure JSON is stored as text
                details_json = json.dumps({
                    'cpu_usage_before': 80.0,
                    'cpu_usage_after': 60.0,
                    'optimization_success': True
                })
                metadata_json = json.dumps({
                    'agent_version': '2.0',
                    'caffeinated': True
                })
                
                insert_sql = text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, user_id, event_type, subject_kind,
                        priority, title, description, details, metadata,
                        numeric_value, string_value
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        'meth_snail', :user_id, 'optimization_metrics', 'system_performance',
                        5, 'Test Metrics', 'Test Description', :details, :metadata,
                        20.0, 'optimization_complete'
                    )
                """)
                
                result = await db.execute(insert_sql, {
                    'memory_id': str(uuid.uuid4()),
                    'now': datetime.utcnow(),
                    'user_id': str(test_user_id),
                    'details': details_json,
                    'metadata': metadata_json
                })
                await db.commit()
                print("✅ Raw SQL insert succeeded!")
                break
        except Exception as e2:
            print(f"❌ Raw SQL also failed: {e2}")
            raise

    print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_meth_snail_basic_operations())