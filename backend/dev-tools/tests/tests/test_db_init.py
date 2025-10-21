import asyncio
from sqlalchemy import text
from app.core.database import async_engine, Base

async def test_db():
    print("Testing database connection...")
    
    # Test connection
    async with async_engine.connect() as conn:
        print("✓ Successfully connected to database")
        
        # Check if database is writable
        try:
            await conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"))
            await conn.commit()
            print("✓ Successfully created test table")
            
            # Check if we can write and read data
            await conn.execute(text("INSERT INTO test_table (name) VALUES ('test')"))
            await conn.commit()
            print("✓ Successfully inserted test data")
            
            result = await conn.execute(text("SELECT * FROM test_table"))
            rows = result.fetchall()
            print(f"✓ Successfully read test data: {rows}")
            
        except Exception as e:
            print(f"❌ Error testing database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_db())
