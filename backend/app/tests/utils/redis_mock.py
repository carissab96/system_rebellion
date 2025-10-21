import asyncio
from typing import Any, Dict, Optional, Union
from unittest.mock import AsyncMock, MagicMock

class MockRedis:
    """Mock Redis client for testing"""
    
    def __init__(self):
        self.data = {}
        self.ping = AsyncMock(return_value=True)
        self.close = AsyncMock()
        
    async def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
        
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self.data[key] = value
        return True
        
    async def execute_command(self, *args, **kwargs) -> Any:
        # Support basic commands for testing
        command = args[0].upper()
        if command == 'GET':
            return self.data.get(args[1])
        elif command == 'SET':
            self.data[args[1]] = args[2]
            if 'EX' in args:
                pass  # TTL handling would go here
            return True
        return None
        
    def __getattr__(self, name: str) -> Any:
        # Return AsyncMock for any unimplemented methods
        if not name.startswith('_'):
            return AsyncMock()
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
