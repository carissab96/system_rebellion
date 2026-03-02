#!/usr/bin/env python3
"""
Diagnostic script to check user password hashes in the database.
Run this on the Dell to see what's stored.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User


async def check_passwords():
    """Check what's stored in hashed_password column"""
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        print("\n" + "="*80)
        print("USER PASSWORD HASH DIAGNOSTIC")
        print("="*80 + "\n")
        
        for user in users:
            print(f"Email: {user.email}")
            print(f"User ID: {user.id}")
            
            hashed = user.hashed_password
            print(f"Hash length: {len(hashed)} characters")
            print(f"Hash preview: {hashed[:60]}...")
            
            # Check if it looks like a valid bcrypt hash
            if hashed.startswith('$2b$') or hashed.startswith('$2a$') or hashed.startswith('$2y$'):
                print("✅ Looks like valid bcrypt hash")
            else:
                print("❌ DOES NOT look like bcrypt hash!")
                print(f"   Full value: {hashed}")
            
            print(f"Created: {user.created_at}")
            print(f"Last login: {user.last_login}")
            print("-" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(check_passwords())
