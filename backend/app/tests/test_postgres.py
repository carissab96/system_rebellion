import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def test_connection():
    # Update with your actual password
    DATABASE_URL = "postgresql+asyncpg://rebellion_user:ChangeThisPassword123!@localhost:5432/system_rebellion"
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Test basic query
        result = await conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"\n✅ PostgreSQL connected!")
        print(f"Version: {version}")
        
        # Test TimescaleDB
        result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'"))
        ext = result.scalar()
        if ext:
            print(f"✅ TimescaleDB extension enabled!")
        else:
            print(f"⚠️ TimescaleDB not enabled (PostgreSQL will still work)")
        
        # List tables
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = result.fetchall()
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
    
    await engine.dispose()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_connection())