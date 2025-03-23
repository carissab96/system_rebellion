import asyncio
import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal
from app.models.user import User
import uuid

async def create_superuser(username: str, email: str, password: str):
    async with AsyncSessionLocal() as session:
        hashed_password = get_password_hash(password)
        
        superuser = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            last_login=None,
            failed_login_attempts=0,
            lockout_until=None
        )
        
        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)
    
    print(f"Superuser {username} created successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_superuser.py <username> <email> <password>")
        sys.exit(1)
    
    asyncio.run(create_superuser(sys.argv[1], sys.argv[2], sys.argv[3]))