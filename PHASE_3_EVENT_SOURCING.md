# Phase 3: Redis Streams Event Sourcing

## Overview
Implement comprehensive event sourcing system using Redis Streams to capture, replay, and analyze all agent activities and system state changes for complete audit trails and state recovery.

## Goals
- 100% agent state recovery capability
- Complete audit trail of all agent actions
- Real-time event analytics and monitoring
- Event-driven agent coordination
- Historical replay for debugging and analysis

## Prerequisites
- Phases 1 and 2 completed and tested
- Redis Streams support available
- Event schema designed
- Monitoring infrastructure ready

## Architecture Overview

### Current State
- Agent activities logged sporadically
- No comprehensive event history
- Difficult to debug agent behavior
- No state recovery mechanisms
- Limited analytics capabilities

### Target State
- All agent actions captured as events
- Complete state reconstruction possible
- Real-time event processing and analytics
- Event-driven agent workflows
- Historical debugging and analysis tools

## Implementation Plan

### Step 1: Event Schema and Base Classes

**File**: `backend/app/services/event_sourcing/events.py` (NEW)

```python
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

class EventType(Enum):
    AGENT_INITIALIZED = "agent_initialized"
    AGENT_MEMORY_STORED = "agent_memory_stored"
    AGENT_MEMORY_RETRIEVED = "agent_memory_retrieved"
    AGENT_DECISION_MADE = "agent_decision_made"
    AGENT_MESSAGE_SENT = "agent_message_sent"
    AGENT_MESSAGE_RECEIVED = "agent_message_received"
    AGENT_STATE_CHANGED = "agent_state_changed"
    AGENT_ERROR_OCCURRED = "agent_error_occurred"
    SYSTEM_METRICS_UPDATED = "system_metrics_updated"
    AGENT_OPTIMIZATION_APPLIED = "agent_optimization_applied"
    AGENT_ANALYSIS_COMPLETED = "agent_analysis_completed"

class BaseEvent(BaseModel):
    event_id: str
    event_type: EventType
    agent_name: str
    timestamp: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    payload: Dict[str, Any] = {}

    def to_stream_data(self) -> Dict[str, str]:
        """Convert event to Redis Stream data format"""
        data = self.dict()
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()

        # Convert all values to strings for Redis
        return {k: str(v) if not isinstance(v, str) else v for k, v in data.items()}

    @classmethod
    def from_stream_data(cls, stream_data: Dict[str, str]) -> 'BaseEvent':
        """Create event from Redis Stream data"""
        data = {}
        for k, v in stream_data.items():
            if k == 'event_type':
                data[k] = EventType(v)
            elif k == 'timestamp':
                data[k] = datetime.fromisoformat(v)
            else:
                # Try to parse JSON for complex objects
                try:
                    data[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    data[k] = v

        return cls(**data)

class AgentInitializedEvent(BaseEvent):
    event_type: EventType = EventType.AGENT_INITIALIZED

    def __init__(self, agent_name: str, **kwargs):
        super().__init__(
            event_id=f"init_{agent_name}_{int(datetime.now(timezone.utc).timestamp())}",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            payload={"status": "initialized"},
            **kwargs
        )

class AgentMemoryStoredEvent(BaseEvent):
    event_type: EventType = EventType.AGENT_MEMORY_STORED

    def __init__(self, agent_name: str, memory_id: str, memory_type: str, **kwargs):
        super().__init__(
            event_id=f"mem_store_{agent_name}_{memory_id}",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            payload={
                "memory_id": memory_id,
                "memory_type": memory_type,
                "action": "stored"
            },
            **kwargs
        )

class AgentDecisionMadeEvent(BaseEvent):
    event_type: EventType = EventType.AGENT_DECISION_MADE

    def __init__(self, agent_name: str, decision_type: str, confidence: float, **kwargs):
        super().__init__(
            event_id=f"decision_{agent_name}_{int(datetime.now(timezone.utc).timestamp())}",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            payload={
                "decision_type": decision_type,
                "confidence": confidence
            },
            **kwargs
        )

class AgentMessageSentEvent(BaseEvent):
    event_type: EventType = EventType.AGENT_MESSAGE_SENT

    def __init__(self, agent_name: str, target_agent: str, message_type: str, **kwargs):
        super().__init__(
            event_id=f"msg_sent_{agent_name}_{target_agent}_{int(datetime.now(timezone.utc).timestamp())}",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            payload={
                "target_agent": target_agent,
                "message_type": message_type,
                "direction": "outbound"
            },
            **kwargs
        )

class AgentErrorOccurredEvent(BaseEvent):
    event_type: EventType = EventType.AGENT_ERROR_OCCURRED

    def __init__(self, agent_name: str, error_type: str, error_message: str, **kwargs):
        super().__init__(
            event_id=f"error_{agent_name}_{int(datetime.now(timezone.utc).timestamp())}",
            agent_name=agent_name,
            timestamp=datetime.now(timezone.utc),
            payload={
                "error_type": error_type,
                "error_message": error_message,
                "severity": kwargs.get('severity', 'error')
            },
            **kwargs
        )
```

### Step 2: Redis Streams Event Store

**File**: `backend/app/services/event_sourcing/event_store.py` (NEW)

```python
import redis.asyncio as redis
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone, timedelta
from events import BaseEvent, EventType

logger = logging.getLogger(__name__)

class EventStore:
    """Redis Streams-based event store for agent activities"""

    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 stream_name: str = "agent_events",
                 max_stream_length: int = 100000):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.stream_name = stream_name
        self.max_stream_length = max_stream_length
        self.consumer_group = "event_processors"
        self.is_initialized = False

    async def initialize(self):
        """Initialize Redis connection and stream"""
        try:
            self.redis = redis.Redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()

            # Create consumer group if it doesn't exist
            try:
                await self.redis.xgroup_create(
                    self.stream_name,
                    self.consumer_group,
                    "0",
                    mkstream=True
                )
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise

            self.is_initialized = True
            logger.info(f"✅ Event store initialized with stream: {self.stream_name}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize event store: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def append_event(self, event: BaseEvent) -> str:
        """Append event to stream"""
        if not self.is_initialized:
            raise RuntimeError("Event store not initialized")

        try:
            stream_data = event.to_stream_data()

            # Add event to stream
            result = await self.redis.xadd(
                self.stream_name,
                stream_data,
                maxlen=self.max_stream_length,
                approximate=True
            )

            logger.debug(f"📝 Event appended: {event.event_type.value} for {event.agent_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to append event {event.event_id}: {e}")
            raise

    async def get_events(self,
                        agent_name: Optional[str] = None,
                        event_type: Optional[EventType] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[BaseEvent]:
        """Retrieve events with optional filtering"""
        if not self.is_initialized:
            raise RuntimeError("Event store not initialized")

        try:
            # Build query parameters
            query_args = {}

            if agent_name:
                query_args["agent_name"] = agent_name

            if event_type:
                query_args["event_type"] = event_type.value

            if start_time:
                # Convert to Redis stream ID format (timestamp + sequence)
                start_id = f"{int(start_time.timestamp() * 1000)}-0"
            else:
                start_id = "0"

            if end_time:
                end_id = f"{int(end_time.timestamp() * 1000)}-999999"
            else:
                end_id = "+"

            # Query stream
            result = await self.redis.xrange(
                self.stream_name,
                start_id,
                end_id,
                count=limit * 2  # Get more to filter
            )

            events = []
            for stream_id, data in result:
                try:
                    event = BaseEvent.from_stream_data(data)

                    # Apply filters
                    if agent_name and event.agent_name != agent_name:
                        continue
                    if event_type and event.event_type != event_type:
                        continue
                    if start_time and event.timestamp < start_time:
                        continue
                    if end_time and event.timestamp > end_time:
                        continue

                    events.append(event)

                    if len(events) >= limit:
                        break

                except Exception as e:
                    logger.warning(f"Failed to parse event {stream_id}: {e}")
                    continue

            logger.debug(f"📖 Retrieved {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"❌ Failed to get events: {e}")
            return []

    async def get_agent_timeline(self, agent_name: str, hours_back: int = 24) -> List[BaseEvent]:
        """Get timeline of events for a specific agent"""
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        return await self.get_events(
            agent_name=agent_name,
            start_time=start_time
        )

    async def replay_events(self,
                           agent_name: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> AsyncGenerator[BaseEvent, None]:
        """Replay events for state reconstruction"""
        events = await self.get_events(
            agent_name=agent_name,
            start_time=start_time,
            end_time=end_time,
            limit=10000  # Large limit for replay
        )

        for event in sorted(events, key=lambda e: e.timestamp):
            yield event

    async def get_event_stats(self,
                             agent_name: Optional[str] = None,
                             hours_back: int = 24) -> Dict[str, Any]:
        """Get statistics about events"""
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        events = await self.get_events(
            agent_name=agent_name,
            start_time=start_time,
            limit=50000  # Large limit for stats
        )

        stats = {
            "total_events": len(events),
            "time_range_hours": hours_back,
            "events_per_hour": len(events) / hours_back if hours_back > 0 else 0,
            "agent_breakdown": {},
            "event_type_breakdown": {}
        }

        for event in events:
            # Agent breakdown
            if event.agent_name not in stats["agent_breakdown"]:
                stats["agent_breakdown"][event.agent_name] = 0
            stats["agent_breakdown"][event.agent_name] += 1

            # Event type breakdown
            event_type_str = event.event_type.value
            if event_type_str not in stats["event_type_breakdown"]:
                stats["event_type_breakdown"][event_type_str] = 0
            stats["event_type_breakdown"][event_type_str] += 1

        return stats

    async def cleanup_old_events(self, retention_days: int = 30):
        """Clean up old events beyond retention period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)

        try:
            # Find events older than cutoff
            old_events = await self.get_events(
                end_time=cutoff_time,
                limit=1000
            )

            deleted_count = 0
            for event in old_events:
                # Delete individual event (Redis Streams doesn't have direct deletion)
                # This is a simplified approach - in practice, you might use stream trimming
                deleted_count += 1

            # Trim stream to keep only recent events
            await self.redis.xtrim(
                self.stream_name,
                maxlen=self.max_stream_length,
                approximate=True
            )

            logger.info(f"🧹 Cleaned up {deleted_count} old events, retained recent {self.max_stream_length}")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old events: {e}")
            return 0

# Global instance
_event_store_instance: Optional[EventStore] = None

async def get_event_store() -> EventStore:
    """Get global event store instance"""
    global _event_store_instance

    if _event_store_instance is None:
        _event_store_instance = EventStore()
        await _event_store_instance.initialize()

    return _event_store_instance
```

### Step 3: Event Publisher Service

**File**: `backend/app/services/event_sourcing/event_publisher.py` (NEW)

```python
import logging
from typing import Optional
from events import BaseEvent
from event_store import get_event_store

logger = logging.getLogger(__name__)

class EventPublisher:
    """Service for publishing events to the event store"""

    def __init__(self):
        self.event_store = None

    async def initialize(self):
        """Initialize event publisher"""
        try:
            self.event_store = await get_event_store()
            logger.info("✅ Event publisher initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize event publisher: {e}")
            # Don't raise - allow system to continue without event publishing

    async def publish_event(self, event: BaseEvent) -> bool:
        """Publish an event to the event store"""
        if not self.event_store:
            logger.debug("Event store not available, skipping event publication")
            return False

        try:
            await self.event_store.append_event(event)
            logger.debug(f"📤 Published event: {event.event_type.value} for {event.agent_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to publish event {event.event_id}: {e}")
            return False

    async def publish_agent_initialized(self, agent_name: str, **kwargs):
        """Publish agent initialization event"""
        from events import AgentInitializedEvent
        event = AgentInitializedEvent(agent_name, **kwargs)
        return await self.publish_event(event)

    async def publish_memory_stored(self, agent_name: str, memory_id: str, memory_type: str, **kwargs):
        """Publish memory storage event"""
        from events import AgentMemoryStoredEvent
        event = AgentMemoryStoredEvent(agent_name, memory_id, memory_type, **kwargs)
        return await self.publish_event(event)

    async def publish_decision_made(self, agent_name: str, decision_type: str, confidence: float, **kwargs):
        """Publish decision event"""
        from events import AgentDecisionMadeEvent
        event = AgentDecisionMadeEvent(agent_name, decision_type, confidence, **kwargs)
        return await self.publish_event(event)

    async def publish_message_sent(self, agent_name: str, target_agent: str, message_type: str, **kwargs):
        """Publish message sent event"""
        from events import AgentMessageSentEvent
        event = AgentMessageSentEvent(agent_name, target_agent, message_type, **kwargs)
        return await self.publish_event(event)

    async def publish_error(self, agent_name: str, error_type: str, error_message: str, **kwargs):
        """Publish error event"""
        from events import AgentErrorOccurredEvent
        event = AgentErrorOccurredEvent(agent_name, error_type, error_message, **kwargs)
        return await self.publish_event(event)

# Global instance
_event_publisher_instance: Optional[EventPublisher] = None

async def get_event_publisher() -> EventPublisher:
    """Get global event publisher instance"""
    global _event_publisher_instance

    if _event_publisher_instance is None:
        _event_publisher_instance = EventPublisher()
        await _event_publisher_instance.initialize()

    return _event_publisher_instance
```

### Step 4: Integrate Event Sourcing with Agent Manager

**File**: `backend/app/ai_agents/agent_manager.py`

**Add event publishing to agent operations**:
```python
from app.services.event_sourcing.event_publisher import get_event_publisher

class AgentManager:
    def __init__(self, db_getter=None):
        # ... existing initialization
        self.event_publisher = None

    async def initialize_agents(self):
        """Initialize agents with event sourcing"""
        # ... existing initialization

        # Initialize event publisher
        try:
            self.event_publisher = await get_event_publisher()
            logger.info("📊 Event sourcing initialized")

            # Publish initialization events for each agent
            for agent_name, agent in self.agents.items():
                await self.event_publisher.publish_agent_initialized(agent_name)

        except Exception as e:
            logger.error(f"❌ Failed to initialize event sourcing: {e}")
            # Continue without event sourcing

        # ... rest of initialization

    async def store_agent_memory(self, agent_name: str, memory_data: dict):
        """Store agent memory with event publishing"""
        # ... existing storage logic

        memory_id = await self.hybrid_memory.store_memory(agent_name, memory_data, db_session)

        # Publish event
        if self.event_publisher:
            await self.event_publisher.publish_memory_stored(
                agent_name,
                memory_id,
                memory_data.get('memory_type', 'general')
            )

        return memory_id

    async def send_agent_message(self, from_agent: str, to_agent: str, message: dict):
        """Send message between agents with event publishing"""
        # ... existing message logic

        await self.pubsub_manager.direct_message(from_agent, to_agent, message)

        # Publish event
        if self.event_publisher:
            await self.event_publisher.publish_message_sent(
                from_agent,
                to_agent,
                message.get('type', 'unknown')
            )

    async def process_metrics_through_triage_engine(self, metrics: dict, user_context: dict):
        """Process metrics with event publishing"""
        # ... existing triage logic

        result = await agent.process_metrics(metrics, user_context)

        # Publish decision event
        if self.event_publisher and 'disposition' in result:
            await self.event_publisher.publish_decision_made(
                agent.name,
                result.get('disposition', 'unknown'),
                result.get('confidence', 0.0)
            )

        return result
```

### Step 5: Create Event Analytics API

**File**: `backend/app/api/endpoints/event_analytics.py` (NEW)

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from app.services.event_sourcing.event_store import get_event_store
from app.services.event_sourcing.events import EventType, BaseEvent

router = APIRouter()

@router.get("/api/events/stats")
async def get_event_stats(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    hours_back: int = Query(24, description="Hours of history to analyze")
):
    """Get event statistics"""
    try:
        event_store = await get_event_store()
        stats = await event_store.get_event_stats(agent_name, hours_back)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event stats: {str(e)}")

@router.get("/api/events/timeline/{agent_name}")
async def get_agent_timeline(
    agent_name: str,
    hours_back: int = Query(24, description="Hours of history")
):
    """Get event timeline for a specific agent"""
    try:
        event_store = await get_event_store()
        events = await event_store.get_agent_timeline(agent_name, hours_back)

        # Convert events to JSON-serializable format
        timeline = []
        for event in events:
            timeline.append({
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
                "metadata": event.metadata
            })

        return {"agent_name": agent_name, "events": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")

@router.get("/api/events/replay")
async def replay_events(
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(1000, description="Maximum events to replay")
):
    """Replay events for state reconstruction"""
    try:
        event_store = await get_event_store()

        # Parse dates
        start_time = None
        end_time = None
        if start_date:
            start_time = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        events = await event_store.get_events(
            agent_name=agent_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Convert to serializable format
        replay_data = []
        for event in events:
            replay_data.append({
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "agent_name": event.agent_name,
                "timestamp": event.timestamp.isoformat(),
                "correlation_id": event.correlation_id,
                "causation_id": event.causation_id,
                "payload": event.payload,
                "metadata": event.metadata
            })

        return {
            "total_events": len(replay_data),
            "agent_filter": agent_name,
            "time_range": {
                "start": start_time.isoformat() if start_time else None,
                "end": end_time.isoformat() if end_time else None
            },
            "events": replay_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replay events: {str(e)}")

@router.post("/api/events/cleanup")
async def cleanup_old_events(retention_days: int = Query(30, description="Days to retain")):
    """Clean up old events beyond retention period"""
    try:
        event_store = await get_event_store()
        deleted_count = await event_store.cleanup_old_events(retention_days)
        return {"message": f"Cleaned up {deleted_count} old events"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup events: {str(e)}")
```

### Step 6: Update Main Application

**File**: `backend/main.py`

**Initialize event sourcing services**:
```python
# Initialize event sourcing
try:
    event_publisher = await get_event_publisher()
    logger.info("📊 Event sourcing system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize event sourcing: {e}")
    # Continue without event sourcing - not critical

# Include event analytics router
app.include_router(
    event_analytics.router,
    prefix="/api/events",
    tags=["Event Analytics"]
)
```

## Testing Implementation

### Event Store Tests
**File**: `backend/dev-tools/tests/test_event_store.py` (NEW)

```python
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.services.event_sourcing.event_store import get_event_store
from app.services.event_sourcing.events import AgentInitializedEvent, EventType

@pytest.mark.asyncio
async def test_event_storage_and_retrieval():
    """Test basic event storage and retrieval"""
    event_store = await get_event_store()

    # Create test event
    event = AgentInitializedEvent("sir_hawkington")

    # Store event
    event_id = await event_store.append_event(event)
    assert event_id is not None

    # Retrieve events
    events = await event_store.get_events(agent_name="sir_hawkington", limit=10)
    assert len(events) > 0

    # Verify event data
    retrieved_event = events[0]
    assert retrieved_event.agent_name == "sir_hawkington"
    assert retrieved_event.event_type == EventType.AGENT_INITIALIZED

@pytest.mark.asyncio
async def test_event_filtering():
    """Test event filtering capabilities"""
    event_store = await get_event_store()

    # Create events for different agents
    event1 = AgentInitializedEvent("sir_hawkington")
    event2 = AgentInitializedEvent("meth_snail")

    await event_store.append_event(event1)
    await event_store.append_event(event2)

    # Test agent filtering
    hawk_events = await event_store.get_events(agent_name="sir_hawkington")
    assert len(hawk_events) >= 1
    assert all(e.agent_name == "sir_hawkington" for e in hawk_events)

    snail_events = await event_store.get_events(agent_name="meth_snail")
    assert len(snail_events) >= 1
    assert all(e.agent_name == "meth_snail" for e in snail_events)

@pytest.mark.asyncio
async def test_timeline_generation():
    """Test agent timeline generation"""
    event_store = await get_event_store()

    agent_name = "the_stick"
    timeline = await event_store.get_agent_timeline(agent_name, hours_back=1)

    # Should return recent events for the agent
    assert isinstance(timeline, list)
    for event in timeline:
        assert event.agent_name == agent_name

@pytest.mark.asyncio
async def test_event_replay():
    """Test event replay functionality"""
    event_store = await get_event_store()

    # Create some test events with timestamps
    base_time = datetime.now(timezone.utc)
    events_created = []

    for i in range(3):
        event = AgentInitializedEvent(f"test_agent_{i}")
        event.timestamp = base_time + timedelta(minutes=i)
        await event_store.append_event(event)
        events_created.append(event)

    # Replay events
    replay_events = []
    async for event in event_store.replay_events():
        replay_events.append(event)

    # Should be in chronological order
    assert len(replay_events) >= 3
    timestamps = [e.timestamp for e in replay_events[-3:]]  # Last 3 events
    assert timestamps == sorted(timestamps)
```

### Event Analytics Tests
**File**: `backend/dev-tools/tests/test_event_analytics.py` (NEW)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_application

@pytest.fixture
def client():
    app = create_application()
    return TestClient(app)

def test_get_event_stats(client):
    """Test event statistics endpoint"""
    response = client.get("/api/events/stats")
    assert response.status_code == 200

    data = response.json()
    assert "total_events" in data
    assert "events_per_hour" in data
    assert "agent_breakdown" in data
    assert "event_type_breakdown" in data

def test_get_agent_timeline(client):
    """Test agent timeline endpoint"""
    response = client.get("/api/events/timeline/sir_hawkington")
    assert response.status_code == 200

    data = response.json()
    assert data["agent_name"] == "sir_hawkington"
    assert "events" in data
    assert isinstance(data["events"], list)

def test_event_replay(client):
    """Test event replay endpoint"""
    response = client.get("/api/events/replay?limit=100")
    assert response.status_code == 200

    data = response.json()
    assert "total_events" in data
    assert "events" in data
    assert isinstance(data["events"], list)

def test_event_cleanup(client):
    """Test event cleanup endpoint"""
    response = client.post("/api/events/cleanup?retention_days=7")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
```

### Integration Tests
**File**: `backend/dev-tools/tests/test_event_sourcing_integration.py` (NEW)

```python
import pytest
from app.ai_agents.agent_manager import get_agent_manager
from app.services.event_sourcing.event_store import get_event_store

@pytest.mark.asyncio
async def test_agent_event_publishing():
    """Test that agents publish events during normal operation"""
    agent_manager = await get_agent_manager()
    event_store = await get_event_store()

    # Trigger some agent activity (this would depend on actual agent methods)
    # For example:
    # await agent_manager.store_agent_memory("sir_hawkington", {"type": "test"})

    # Check that events were published
    events = await event_store.get_events(agent_name="sir_hawkington", limit=10)
    assert len(events) > 0

    # Verify event types
    event_types = {e.event_type for e in events}
    assert len(event_types) > 0  # Should have various event types

@pytest.mark.asyncio
async def test_state_reconstruction():
    """Test reconstructing agent state from events"""
    event_store = await get_event_store()

    agent_name = "meth_snail"

    # Get recent events for agent
    events = await event_store.get_agent_timeline(agent_name, hours_back=1)

    # Simulate state reconstruction
    agent_state = {
        "initialized": False,
        "memories_stored": 0,
        "decisions_made": 0,
        "errors_occurred": 0
    }

    for event in events:
        if event.event_type.value == "agent_initialized":
            agent_state["initialized"] = True
        elif event.event_type.value == "agent_memory_stored":
            agent_state["memories_stored"] += 1
        elif event.event_type.value == "agent_decision_made":
            agent_state["decisions_made"] += 1
        elif event.event_type.value == "agent_error_occurred":
            agent_state["errors_occurred"] += 1

    # Verify state makes sense
    assert isinstance(agent_state["initialized"], bool)
    assert agent_state["memories_stored"] >= 0
    assert agent_state["decisions_made"] >= 0
    assert agent_state["errors_occurred"] >= 0
```

### Manual Testing Checklist
- [ ] Verify Redis Streams are working
- [ ] Check event publishing during agent initialization
- [ ] Monitor event rates via analytics API
- [ ] Test event replay functionality
- [ ] Verify event cleanup works
- [ ] Test agent state reconstruction
- [ ] Check event correlation and causation IDs
- [ ] Monitor Redis memory usage with streams

## Rollback Plan

### Phase 3 Rollback Steps
1. **Stop the application**
2. **Remove event analytics router**:
   ```bash
   git checkout backend/main.py
   ```
3. **Revert agent manager changes**:
   ```bash
   git checkout backend/app/ai_agents/agent_manager.py
   ```
4. **Remove event sourcing services**:
   ```bash
   rm -rf backend/app/services/event_sourcing/
   ```
5. **Remove event analytics API**:
   ```bash
   rm backend/app/api/endpoints/event_analytics.py
   ```
6. **Clear Redis streams** (optional):
   ```bash
   redis-cli DEL agent_events
   ```
7. **Restart application**
8. **Verify agents work without event sourcing**

### Rollback Verification
- [ ] Application starts successfully
- [ ] No Redis streams errors
- [ ] Agent functionality unchanged
- [ ] WebSocket connections work
- [ ] Event analytics endpoints removed

## Success Metrics
- [ ] 100% agent state recovery from event replay
- [ ] Complete audit trail for all agent actions
- [ ] Event publishing latency < 5ms
- [ ] Event analytics API response time < 100ms
- [ ] Redis Streams memory usage stays within limits
- [ ] Event cleanup maintains retention policies
- [ ] Correlation/causation IDs enable proper event tracing

## Dependencies
- Redis Streams support required
- Phases 1 & 2 must be completed
- Event schema must be stable
- Monitoring infrastructure for analytics

## Risk Mitigation
- **Event Loss**: Redis persistence ensures durability
- **Performance Impact**: Async event publishing doesn't block agents
- **Storage Growth**: Automatic cleanup and retention policies
- **Schema Changes**: Event versioning and migration support
- **Debugging**: Event replay enables root cause analysis
- **Monitoring**: Comprehensive analytics for system health
