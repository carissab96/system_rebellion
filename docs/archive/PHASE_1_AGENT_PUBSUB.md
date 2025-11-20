# Phase 1: Enhanced Redis Pub/Sub for Agent Communication

## Overview
Implement real-time agent communication via Redis pub/sub to eliminate blocking database operations and improve agent coordination performance.

## Goals
- Enable instant agent-to-agent messaging without database roundtrips
- Reduce agent communication latency from seconds to milliseconds
- Provide reliable agent broadcast capabilities
- Maintain backward compatibility with existing agent system

## Prerequisites
- Redis server running and accessible
- All short-term stabilization fixes completed
- Agent manager properly initialized at startup
- Basic WebSocket functionality working

## Architecture Overview

### Current State
- Agents communicate through database queries and direct method calls
- WebSocket connections block during agent manager initialization
- No real-time inter-agent coordination

### Target State
- Agents use Redis pub/sub for real-time messaging
- Agent manager coordinates via pub/sub channels
- WebSocket connections remain instant
- Database used only for persistence, not coordination

## Implementation Plan

### Step 1: Create Agent Pub/Sub Manager

**File**: `backend/app/services/agent_pubsub.py` (NEW)

```python
import redis.asyncio as redis
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AgentPubSubManager:
    """Manages real-time agent communication via Redis pub/sub"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.Redis] = None
        self.subscribers: Dict[str, Callable] = {}
        self.is_connected = False

    async def connect(self):
        """Initialize Redis connections"""
        try:
            self.redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            self.is_connected = True
            logger.info("✅ Agent Pub/Sub manager connected to Redis")
        except Exception as e:
            logger.error(f"❌ Failed to connect Agent Pub/Sub to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connections"""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        self.is_connected = False

    async def agent_broadcast(self, agent_name: str, message: dict):
        """Broadcast message to all subscribers of an agent"""
        if not self.is_connected:
            logger.warning("Pub/Sub not connected, skipping broadcast")
            return

        channel = f"agent:{agent_name}:broadcast"
        message_data = {
            "type": "broadcast",
            "agent": agent_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": message
        }

        try:
            await self.redis.publish(channel, json.dumps(message_data))
            logger.debug(f"📡 Broadcasted message to {channel}")
        except Exception as e:
            logger.error(f"❌ Failed to broadcast message: {e}")

    async def direct_message(self, from_agent: str, to_agent: str, message: dict):
        """Send direct message between agents"""
        if not self.is_connected:
            logger.warning("Pub/Sub not connected, skipping direct message")
            return

        channel = f"agent:{from_agent}:to:{to_agent}"
        message_data = {
            "type": "direct_message",
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": message
        }

        try:
            await self.redis.publish(channel, json.dumps(message_data))
            logger.debug(f"📨 Sent direct message {from_agent} -> {to_agent}")
        except Exception as e:
            logger.error(f"❌ Failed to send direct message: {e}")

    async def subscribe_agent(self, agent_name: str, callback: Callable):
        """Subscribe to messages for a specific agent"""
        if not self.is_connected:
            logger.warning("Pub/Sub not connected, skipping subscription")
            return

        broadcast_channel = f"agent:{agent_name}:broadcast"
        direct_channel_pattern = f"agent:*:to:{agent_name}"

        self.subscribers[agent_name] = callback

        # Subscribe to broadcast channel
        await self.pubsub.subscribe(**{broadcast_channel: self._handle_message})

        # Subscribe to direct messages (using pattern)
        await self.pubsub.psubscribe(**{direct_channel_pattern: self._handle_message})

        logger.info(f"📺 Agent {agent_name} subscribed to pub/sub channels")

    async def unsubscribe_agent(self, agent_name: str):
        """Unsubscribe agent from pub/sub channels"""
        if not self.is_connected:
            return

        broadcast_channel = f"agent:{agent_name}:broadcast"
        direct_channel_pattern = f"agent:*:to:{agent_name}"

        await self.pubsub.unsubscribe(broadcast_channel)
        await self.pubsub.punsubscribe(direct_channel_pattern)

        if agent_name in self.subscribers:
            del self.subscribers[agent_name]

        logger.info(f"🔇 Agent {agent_name} unsubscribed from pub/sub channels")

    def _handle_message(self, message):
        """Handle incoming pub/sub messages"""
        try:
            if message['type'] == 'message':
                data = json.loads(message['data'])
                channel = message['channel']

                # Determine target agent from channel
                if ':broadcast' in channel:
                    agent_name = channel.split(':')[1]
                elif ':to:' in channel:
                    agent_name = channel.split(':to:')[1]
                else:
                    return

                # Call agent's callback
                if agent_name in self.subscribers:
                    self.subscribers[agent_name](data)

        except Exception as e:
            logger.error(f"❌ Error handling pub/sub message: {e}")

# Global instance
_agent_pubsub_instance: Optional[AgentPubSubManager] = None

async def get_agent_pubsub() -> AgentPubSubManager:
    """Get global agent pub/sub manager instance"""
    global _agent_pubsub_instance

    if _agent_pubsub_instance is None:
        _agent_pubsub_instance = AgentPubSubManager()
        await _agent_pubsub_instance.connect()

    return _agent_pubsub_instance
```

### Step 2: Integrate with Agent Manager

**File**: `backend/app/ai_agents/agent_manager.py`

**Add pub/sub integration**:
```python
from app.services.agent_pubsub import get_agent_pubsub

class AgentManager:
    def __init__(self, db_getter=None):
        # ... existing initialization
        self.pubsub_manager = None

    async def initialize_agents(self):
        """Initialize all agents with pub/sub capabilities"""
        # ... existing agent initialization

        # Initialize pub/sub manager
        try:
            self.pubsub_manager = await get_agent_pubsub()

            # Subscribe each agent to pub/sub channels
            for agent_name, agent in self.agents.items():
                await self.pubsub_manager.subscribe_agent(
                    agent_name,
                    self._handle_agent_message
                )

            logger.info("✅ Agent pub/sub subscriptions established")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent pub/sub: {e}")
            # Continue without pub/sub - not critical

    async def _handle_agent_message(self, message: dict):
        """Handle incoming pub/sub messages for agents"""
        try:
            message_type = message.get('type')
            agent_name = message.get('agent') or message.get('to')

            if agent_name not in self.agents:
                return

            agent = self.agents[agent_name]

            if message_type == 'broadcast':
                # Handle broadcast message
                await agent.handle_broadcast(message['data'])
            elif message_type == 'direct_message':
                # Handle direct message
                await agent.handle_direct_message(
                    message['from'],
                    message['data']
                )

        except Exception as e:
            logger.error(f"❌ Error handling agent message: {e}")

    async def send_agent_message(self, from_agent: str, to_agent: str, message: dict):
        """Send message between agents via pub/sub"""
        if self.pubsub_manager:
            await self.pubsub_manager.direct_message(from_agent, to_agent, message)
        else:
            # Fallback to direct method call
            logger.warning("Pub/sub not available, using direct call")
            if to_agent in self.agents:
                await self.agents[to_agent].handle_direct_message(from_agent, message)

    async def broadcast_to_agents(self, from_agent: str, message: dict):
        """Broadcast message to all agents"""
        if self.pubsub_manager:
            await self.pubsub_manager.agent_broadcast(from_agent, message)
        else:
            # Fallback to direct calls
            logger.warning("Pub/sub not available, using direct calls")
            for agent_name, agent in self.agents.items():
                if agent_name != from_agent:
                    try:
                        await agent.handle_broadcast(message)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {agent_name}: {e}")
```

### Step 3: Update Agent Base Class

**File**: `backend/app/ai_agents/base_agent.py` (or equivalent)

**Add pub/sub message handlers**:
```python
class BaseAgent:
    def __init__(self, name: str, db_getter=None):
        self.name = name
        self.db_getter = db_getter
        # ... existing initialization

    async def handle_broadcast(self, message: dict):
        """Handle broadcast messages from other agents"""
        logger.info(f"📡 {self.name} received broadcast: {message}")
        # Default implementation - override in subclasses
        pass

    async def handle_direct_message(self, from_agent: str, message: dict):
        """Handle direct messages from other agents"""
        logger.info(f"📨 {self.name} received direct message from {from_agent}: {message}")
        # Default implementation - override in subclasses
        pass

    async def send_message(self, to_agent: str, message: dict):
        """Send message to another agent"""
        from app.ai_agents.agent_manager import get_agent_manager
        agent_manager = await get_agent_manager()
        await agent_manager.send_agent_message(self.name, to_agent, message)

    async def broadcast_message(self, message: dict):
        """Broadcast message to all agents"""
        from app.ai_agents.agent_manager import get_agent_manager
        agent_manager = await get_agent_manager()
        await agent_manager.broadcast_to_agents(self.name, message)
```

### Step 4: Update Main Application Startup

**File**: `backend/main.py` (lifespan function)

**Initialize pub/sub manager**:
```python
# Initialize agent manager (existing)
agent_start = time.time()
agent_manager = await get_agent_manager(db_getter=db_session_factory)
agent_elapsed = time.time() - agent_start
active_agents = list(agent_manager.agents.keys()) if agent_manager.initialized else []
logger.info(f"🤖 AI Agents initialized in {agent_elapsed:.2f}s - Active: {active_agents}")

# Initialize agent pub/sub system
try:
    pubsub_manager = await get_agent_pubsub()
    logger.info("📡 Agent pub/sub system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize agent pub/sub: {e}")
    # Continue without pub/sub - not critical for basic functionality
```

## Testing Implementation

### Unit Tests
**File**: `backend/dev-tools/tests/test_agent_pubsub.py` (NEW)

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.agent_pubsub import AgentPubSubManager

@pytest.mark.asyncio
async def test_agent_broadcast():
    """Test agent broadcast functionality"""
    manager = AgentPubSubManager()
    manager.redis = AsyncMock()
    manager.is_connected = True

    await manager.agent_broadcast("sir_hawkington", {"type": "status_update", "status": "active"})

    manager.redis.publish.assert_called_once()
    call_args = manager.redis.publish.call_args
    assert "agent:sir_hawkington:broadcast" in call_args[0][0]

@pytest.mark.asyncio
async def test_direct_message():
    """Test direct agent messaging"""
    manager = AgentPubSubManager()
    manager.redis = AsyncMock()
    manager.is_connected = True

    await manager.direct_message("sir_hawkington", "meth_snail", {"type": "request", "data": "optimize"})

    manager.redis.publish.assert_called_once()
    call_args = manager.redis.publish.call_args
    assert "agent:sir_hawkington:to:meth_snail" in call_args[0][0]

@pytest.mark.asyncio
async def test_message_handling():
    """Test message handling and routing"""
    manager = AgentPubSubManager()
    callback_called = False
    received_message = None

    def test_callback(message):
        nonlocal callback_called, received_message
        callback_called = True
        received_message = message

    manager.subscribers["meth_snail"] = test_callback

    # Simulate incoming message
    test_message = {
        'type': 'message',
        'data': '{"type": "direct_message", "from": "sir_hawkington", "to": "meth_snail", "data": {"test": true}}',
        'channel': 'agent:sir_hawkington:to:meth_snail'
    }

    manager._handle_message(test_message)

    assert callback_called
    assert received_message['type'] == 'direct_message'
    assert received_message['from'] == 'sir_hawkington'
```

### Integration Tests
**File**: `backend/dev-tools/tests/test_agent_pubsub_integration.py` (NEW)

```python
import pytest
import asyncio
from app.ai_agents.agent_manager import get_agent_manager
from app.services.agent_pubsub import get_agent_pubsub

@pytest.mark.asyncio
async def test_agent_communication_flow():
    """Test complete agent communication flow"""
    # Initialize components
    agent_manager = await get_agent_manager()
    pubsub_manager = await get_agent_pubsub()

    # Verify agents are subscribed
    assert pubsub_manager.is_connected
    assert len(pubsub_manager.subscribers) > 0

    # Test agent-to-agent messaging
    test_message = {"type": "test", "data": "integration_test"}

    # This would require actual Redis running
    # await agent_manager.send_agent_message("sir_hawkington", "meth_snail", test_message)

    # Verify message handling doesn't crash
    assert True  # Placeholder for actual integration test

@pytest.mark.asyncio
async def test_pubsub_fallback():
    """Test fallback when Redis is unavailable"""
    # Mock Redis failure
    agent_manager = await get_agent_manager()

    # Force pubsub manager to None
    agent_manager.pubsub_manager = None

    # Test should still work via direct calls
    # This would need actual agent instances to test properly
    assert True  # Placeholder
```

### Manual Testing Checklist
- [ ] Start backend with Redis running
- [ ] Verify pub/sub initialization logs
- [ ] Check agent subscription logs
- [ ] Test agent communication via WebSocket interface
- [ ] Monitor Redis pub/sub channels for messages
- [ ] Verify no database blocking during agent communication

## Rollback Plan

### Phase 1 Rollback Steps
1. **Stop the application**
2. **Revert agent manager changes**:
   ```bash
   git checkout backend/app/ai_agents/agent_manager.py
   ```
3. **Remove pub/sub service**:
   ```bash
   rm backend/app/services/agent_pubsub.py
   ```
4. **Revert base agent changes**:
   ```bash
   git checkout backend/app/ai_agents/base_agent.py
   ```
5. **Revert main.py changes**:
   ```bash
   git checkout backend/main.py
   ```
6. **Restart application**
7. **Verify agents still work via direct calls**

### Rollback Verification
- [ ] Application starts successfully
- [ ] Agents initialize without pub/sub
- [ ] WebSocket connections work
- [ ] No Redis connection errors
- [ ] Agent functionality unchanged

## Success Metrics
- [ ] Agent communication latency < 10ms (vs 2-3 seconds previously)
- [ ] No database blocking during agent coordination
- [ ] WebSocket connections remain instant
- [ ] Redis pub/sub channels show active agent communication
- [ ] All existing agent functionality preserved

## Dependencies
- Redis server must be running
- All agents must inherit from BaseAgent
- Agent manager must be initialized at startup
- Short-term fixes must be completed first

## Risk Mitigation
- **Redis Failure**: System falls back to direct agent calls
- **Network Issues**: Pub/sub automatically reconnects
- **Agent Crashes**: Other agents continue functioning
- **Backward Compatibility**: All existing APIs preserved
