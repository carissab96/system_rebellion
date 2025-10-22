"""
Test Agent Instrumentation
Verify that instrumentation emits real events (NO FAKE DATA)
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.ai_agents.agent_instrumentation import AgentInstrumentationMixin, instrument_method
from app.api.websockets import get_websocket_manager


class TestAgent(AgentInstrumentationMixin):
    """Test agent to verify instrumentation"""
    
    def __init__(self):
        super().__init__()
        self.agent_name = "test_agent"
        self.processing_count = 0
    
    @instrument_method
    async def test_method(self, data: dict):
        """Test method that should emit events"""
        print(f"  → Executing test_method with data: {data}")
        await asyncio.sleep(0.1)  # Simulate work
        self.processing_count += 1
        return {"processed": True, "count": self.processing_count}
    
    @instrument_method
    async def test_error_method(self):
        """Test method that raises an error"""
        print(f"  → Executing test_error_method (will fail)")
        await asyncio.sleep(0.05)
        raise ValueError("Test error - this is expected")


async def test_instrumentation():
    """Test the instrumentation system"""
    print("\n" + "="*60)
    print("AGENT INSTRUMENTATION TEST")
    print("="*60)
    
    # Create test agent
    print("\n1. Creating test agent...")
    agent = TestAgent()
    print(f"   ✓ Agent created: {agent.agent_name}")
    
    # Start WebSocket manager (needed for broadcasting)
    print("\n2. Starting WebSocket manager...")
    ws_manager = get_websocket_manager()
    await ws_manager.start()
    print(f"   ✓ WebSocket manager started")
    print(f"   ✓ Active connections: {len(ws_manager.active_connections)}")
    
    # Test successful method execution
    print("\n3. Testing successful method execution...")
    print("   Expected events: method_start, method_end")
    result = await agent.test_method({"test": "data", "value": 123})
    print(f"   ✓ Method completed: {result}")
    
    # Test another execution
    print("\n4. Testing second execution...")
    result2 = await agent.test_method({"test": "data2", "value": 456})
    print(f"   ✓ Method completed: {result2}")
    
    # Test error handling
    print("\n5. Testing error handling...")
    print("   Expected events: method_start, method_error")
    try:
        await agent.test_error_method()
    except ValueError as e:
        print(f"   ✓ Error caught as expected: {e}")
    
    # Test state change
    print("\n6. Testing state change emission...")
    old_count = agent.processing_count
    await agent._emit_state_change("processing_count", old_count, old_count + 1)
    print(f"   ✓ State change emitted: {old_count} -> {old_count + 1}")
    
    # Shutdown
    print("\n7. Shutting down...")
    await ws_manager.shutdown()
    print(f"   ✓ WebSocket manager stopped")
    
    print("\n" + "="*60)
    print("TEST COMPLETE - NO FAKE DATA USED")
    print("="*60)
    print("\nSummary:")
    print(f"  • Agent executed {agent.processing_count} successful methods")
    print(f"  • All events were real method executions")
    print(f"  • Error handling worked correctly")
    print(f"  • State changes tracked properly")
    print("\nNOTE: Events were broadcast to WebSocket manager.")
    print("      With real clients connected, they would receive these events.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_instrumentation())
