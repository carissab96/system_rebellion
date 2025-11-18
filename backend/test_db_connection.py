#!/usr/bin/env python3
"""Quick database connection test"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_db():
    """Test if Postgres is running and accessible"""
    db_url = "postgresql+asyncpg://carissab@localhost:5432/system_rebellion"
    
    print(f"🔍 Testing database connection...")
    print(f"📍 URL: {db_url}")
    
    try:
        # Create engine
        engine = create_async_engine(db_url, echo=False)
        print("✅ Engine created")
        
        # Try to connect
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to Postgres!")
            print(f"📊 Version: {version}")
            
            # Check if central_memory_bank table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'central_memory_bank'
                )
            """))
            table_exists = result.scalar()
            print(f"📋 central_memory_bank table exists: {table_exists}")
            
            if table_exists:
                # Count rows
                result = await conn.execute(text("SELECT COUNT(*) FROM central_memory_bank"))
                count = result.scalar()
                print(f"📊 Rows in central_memory_bank: {count}")
                
                # Get recent entries
                result = await conn.execute(text("""
                    SELECT agent_name, event_type, occurred_at 
                    FROM central_memory_bank 
                    ORDER BY occurred_at DESC 
                    LIMIT 5
                """))
                rows = result.fetchall()
                if rows:
                    print(f"\n📝 Recent entries:")
                    for row in rows:
                        print(f"   - {row[0]}: {row[1]} at {row[2]}")
                else:
                    print("⚠️  No entries found in central_memory_bank")
        
        await engine.dispose()
        print("\n✅ Database is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection FAILED: {e}")
        print(f"\n💡 Possible issues:")
        print(f"   1. Postgres is not running: sudo systemctl status postgresql")
        print(f"   2. Database doesn't exist: createdb system_rebellion")
        print(f"   3. User doesn't have access: check pg_hba.conf")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_db())
    sys.exit(0 if result else 1)
