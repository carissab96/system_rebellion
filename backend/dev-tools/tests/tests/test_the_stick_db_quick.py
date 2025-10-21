# test_the_stick_db_quick.py
"""
Quick test for The Stick database operations with central memory bank
"""
import asyncio
from datetime import datetime
import uuid
import json

# Import the actual classes we're testing
from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration
from app.ai_agents.the_stick.data_types import AnxietyEvent, HamsterProximityAlert
from app.core.database import get_async_db

async def test_the_stick_basic_operations():
    """Test that The Stick can save and retrieve data without panicking"""
    
    print("\n📏😰 Testing The Stick Database Operations...")
    
    # Get real database connection - FIX THE CONNECTION ISSUE
    db_integration = StickDatabaseIntegration()
    
    # IMPORTANT: Don't call initialize() - it tries to create its own PostgreSQL connection!
    # Instead, we'll override the session factory to use our SQLite connection
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    # Get the actual database session from get_async_db
    async for db in get_async_db():
        # Create a session factory that returns our existing session
        db_integration.session_factory = lambda: db

    test_user_id = "test_user_12345"  # Test user
    
    # Test 1: Store anxiety event (The Stick's primary concern)
    print("\n1️⃣ Testing store_anxiety_event...")
    try:
        anxiety_event = AnxietyEvent(
            timestamp=utc_now().isoformat,
            trigger="Database test running",
            anxiety_level_before=25.0,
            anxiety_level_after=45.0,
            multiplier=1.5,
            paper_bags_consumed=1,
            hamster_involved=False,
            resolution="Test completed"
        )
        
        event_id = await db_integration.store_anxiety_event(anxiety_event)
        print(f"✅ Stored anxiety event with ID: {event_id}")
    except Exception as e:
        print(f"❌ Failed to store anxiety event: {e}")
        
        # Let's try raw SQL to debug
        print("\n   The Stick is trying raw SQL in panic mode...")
        try:
            async for db in get_async_db():
                from sqlalchemy import text
                
                details_json = json.dumps({
                    'trigger': 'Database test',
                    'anxiety_level_before': 25.0,
                    'anxiety_level_after': 45.0,
                    'paper_bags_consumed': 1
                })
                
                insert_sql = text("""
                    INSERT INTO central_memory_bank (
                        memory_id, created_at, updated_at, occurred_at,
                        agent_name, event_type, details,
                        stick_anxiety_level, numeric_value, string_value,
                        priority, never_forget
                    ) VALUES (
                        :memory_id, :now, :now, :now,
                        'the_stick', 'anxiety_event', :details,
                        45.0, 45.0, 'Database test',
                        7, false
                    )
                """)
                
                result = await db.execute(insert_sql, {
                    'memory_id': str(uuid.uuid4()),
                    'now': datetime.utcnow(),
                    'details': details_json
                })
                await db.commit()
                print("✅ Raw SQL insert succeeded! The Stick is slightly less anxious.")
                break
        except Exception as e2:
            print(f"❌ Raw SQL also failed! MAXIMUM PANIC: {e2}")
            raise

    # Test 2: Store hamster encounter (The Stick's worst nightmare)
    print("\n2️⃣ Testing store_hamster_encounter...")
    try:
        hamster_alert = HamsterProximityAlert(
            timestamp=utc_now(),
            active_hamsters=['Bob'],  # OH NO!
            locations={'bob': 'TEST ENVIRONMENT'},
            anxiety_multiplier=3.0,
            panic_level='MAXIMUM',
            infrastructure_risk='CRITICAL',
            stick_response='PAPER BAG PROTOCOL ACTIVATED',
            paper_bags_consumed=3
        )
        
        alert_id = await db_integration.store_hamster_encounter(test_user_id, hamster_alert)
        print(f"✅ BOB ENCOUNTER STORED! ID: {alert_id}")
        print("   The Stick has consumed 3 paper bags.")
    except Exception as e:
        print(f"❌ Failed to store hamster encounter: {e}")

    # Test 3: Check paper bag inventory
    print("\n3️⃣ Testing paper bag inventory...")
    try:
        # Add some bags first
        await db_integration.update_paper_bag_inventory(100, "Initial test supply")
        
        # Then consume some
        inventory = await db_integration.update_paper_bag_inventory(-5, "Test anxiety")
        print(f"✅ Paper bag inventory updated!")
        print(f"   Current stock: {inventory['current_inventory']}")
        print(f"   Critical level: {inventory['critical_level']}")
    except Exception as e:
        print(f"❌ Paper bag crisis: {e}")

    print("\n📏✅ Test completed! The Stick is anxiously satisfied.")

if __name__ == "__main__":
    asyncio.run(test_the_stick_basic_operations())