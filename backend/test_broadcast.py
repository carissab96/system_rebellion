#!/usr/bin/env python3
"""
Quick test script to manually trigger a triage broadcast
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_broadcast():
    from app.ai_agents.agent_manager import get_agent_manager
    
    # Get agent manager
    agent_manager = await get_agent_manager()
    
    # Create test metrics
    test_metrics = {
        "cpu_percent": 75.0,
        "memory_percent": 60.0,
        "disk_percent": 50.0,
        "network_bytes_sent": 1000000,
        "network_bytes_recv": 2000000,
        "timestamp": "2025-01-14T16:00:00Z"
    }
    
    # Test user context
    user_context = {
        "user_id": "d0717a72-9e05-4907-a990-bd7e79ce5b6b",
        "email": "testuser@hawkington-tech.com",
        "client_id": "test_client"
    }
    
    print("🧪 Testing triage broadcast...")
    result = await agent_manager.process_metrics_through_triage_engine(test_metrics, user_context)
    print(f"✅ Triage result: {result}")

if __name__ == "__main__":
    asyncio.run(test_broadcast())
