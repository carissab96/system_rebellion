import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db
from app.models.user import User
from app.core.security import get_password_hash

async def create_test_user():
    """Create a test user for development purposes"""
    print("🧐 Sir Hawkington is preparing your test user credentials...")
    
    # Get database session
    async for db in get_async_db():
        try:
            # Check if test user already exists
            result = await db.execute("SELECT * FROM users WHERE username = 'testuser' OR email = 'test@example.com'")
            existing_user = result.first()
            
            if existing_user:
                print("🧐 Sir Hawkington notes that a test user already exists!")
                return
            
            # Create new test user
            password_hash = get_password_hash("password123")
            new_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=password_hash,
                is_active=True,
                is_superuser=True
            )
            
            db.add(new_user)
            await db.commit()
            
            print("✅ Test user created successfully!")
            print("Username: testuser")
            print("Password: password123")
            print("The Meth Snail approves of these credentials.")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating test user: {e}")
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
