# app/core/redis.py
import redis.asyncio as redis
from typing import Optional
import os

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global Redis client instances
_redis_client: Optional[redis.Redis] = None
_sync_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get async Redis client - Sir Hawkington's Cache Squadron"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        # Test connection
        await _redis_client.ping()
        print("🎯 Redis connected successfully - The Meth Snail approves!")
    return _redis_client

def get_sync_redis_client() -> redis.Redis:
    """Get sync Redis client for non-async contexts"""
    global _sync_redis_client
    if _sync_redis_client is None:
        import redis as sync_redis
        _sync_redis_client = sync_redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        _sync_redis_client.ping()
        print("🎯 Sync Redis connected - Sir Hawkington's backup squadron ready!")
    return _sync_redis_client

async def close_redis():
    """Cleanup Redis connections"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

# Dependency for FastAPI
async def get_redis() -> redis.Redis:
    """FastAPI dependency for Redis"""
    return await get_redis_client()