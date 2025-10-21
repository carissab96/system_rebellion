# backend/app/core/cache.py
"""Simple in-memory cache for auth performance"""
from typing import Dict, Optional
import asyncio
import json
from datetime import datetime, timedelta

class InMemoryCache:
    def __init__(self):
        self._cache: Dict[str, tuple[dict, datetime]] = {}
        self._lock = asyncio.Lock()
        self._ttl = timedelta(minutes=5)  # 5 minute TTL
    
    async def get(self, key: str) -> Optional[dict]:
        async with self._lock:
            if key in self._cache:
                data, timestamp = self._cache[key]
                if datetime.now() - timestamp < self._ttl:
                    return data
                else:
                    del self._cache[key]  # Remove expired entry
        return None
    
    async def set(self, key: str, value: dict):
        async with self._lock:
            self._cache[key] = (value, datetime.now())
            # Cleanup if cache gets too big
            if len(self._cache) > 100:
                # Remove oldest entries
                sorted_items = sorted(self._cache.items(), key=lambda x: x[1][1])
                for key, _ in sorted_items[:20]:  # Remove oldest 20
                    del self._cache[key]

# Global cache instance
auth_cache = InMemoryCache()