# System Rebellion - Architecture Map
**Last Updated:** December 20, 2025  
**Purpose:** Clear overview of how everything actually works

---

## The Big Picture

Your system has **6 AI agents** that monitor system resources and make decisions. They communicate through **Redis pub/sub** and broadcast their activities via **WebSocket** to the frontend.

```
System Metrics (psutil)
    ↓
Sir Hawkington (Triage Officer)
    ↓
VIC-20 Sage (Coordinator)
    ↓
Specialists (Terry, Hamsters, QSP, Stick)
```

---

## The Agents (Who Does What)

### Sir Hawkington 🧐
**Role:** System-wide triage officer  
**Location:** `backend/app/ai_agents/sir_hawkington/`
- Monitors ALL system resources (CPU, memory, disk, network)
- Analyzes metrics and makes triage decisions
- Identifies which resource is the primary problem
- Routes to VIC-20 for coordination OR directly to The Stick for normal operations

**Key Files:**
- `triage_engine.py` - Main triage logic, broadcasts decisions
- `decision_engine.py` - Sir Hawkington's "brain" (stress score calculation)
- `distributed_hawkington.py` - Distributed agent wrapper

### VIC-20 Sage 🖥️
**Role:** Agent coordinator  
**Location:** `backend/app/ai_agents/vic_20_sage/`
- Receives triage alerts from Hawkington
- Routes to appropriate specialist based on resource type:
  - CPU → Terry (Meth Snail)
  - Memory → Terry (Meth Snail)
  - Disk → Hamsters
  - Network → QSP
- Queries historical patterns from vector database
- Broadcasts coordination decisions

**Key Files:**
- `distributed_vic20.py` - Main coordination logic
- `decision_engine.py` - VIC-20's coordination brain

### Terry (Meth Snail) 🐌
**Role:** CPU/Memory specialist  
**Location:** `backend/app/ai_agents/meth_snail/`
- Handles cache clearing
- Manages memory optimization
- Shell spins when stressed

**Key Files:**
- `distributed_meth_snail.py` - Main logic

### The Hamsters 🐹
**Role:** Disk/Storage specialist  
**Location:** `backend/app/ai_agents/hamsters/`
- Steve (careful), Bob (wild), Carl (duct tape genius)
- Telepathic consensus decision-making
- Handle storage operations

**Key Files:**
- `distributed_hamsters.py` - Main logic
- `decision_engine_sbcV3.py` - Hamsters' brain

### QSP (Quantum Shadow People) 👻
**Role:** Network/Security specialist  
**Location:** `backend/app/ai_agents/quantum_shadow_people/`
- Handles network issues
- Security monitoring

**Key Files:**
- `distributed_qsp.py` - Main logic

### The Stick 📝
**Role:** Universal logger and learner  
**Location:** `backend/app/ai_agents/the_stick/`
- Receives ALL decisions from all agents
- Learns patterns over time
- Paper bag consumption when stressed

**Key Files:**
- `distributed_stick.py` - Main logic

---

## The Communication Flow

### 1. Metrics Collection
**Location:** `backend/app/services/metrics/`

```
SimplifiedMetricsService
    ├── SimplifiedCPUService (psutil.cpu_percent)
    ├── SimplifiedMemoryService (psutil.virtual_memory)
    ├── SimplifiedDiskService (psutil.disk_usage)
    └── SimplifiedNetworkService (psutil.net_io_counters)
```

Every 5 seconds, real system metrics are collected using `psutil`.

### 2. Triage Decision (Hawkington)
**Location:** `backend/app/ai_agents/sir_hawkington/triage_engine.py`

```python
# Hawkington receives metrics
metrics = {
    'cpu_usage': 85.0,      # Real psutil data
    'memory_usage': 72.0,
    'disk_usage': 45.0,
    'network_usage': 30.0
}

# Calculates stress score (weighted average)
stress_score = (cpu * 0.25) + (memory * 0.35) + (disk * 0.40)

# Determines severity
if stress_score >= 0.75: EMERGENCY
elif stress_score >= 0.50: HIGH
elif stress_score >= 0.30: MEDIUM
else: NORMAL

# Identifies primary resource (highest value)
primary_resource = 'cpu'  # In this example
current_value = 85.0
threshold = 80.0

# Routes decision
if MEDIUM/HIGH/EMERGENCY:
    → Send TRIAGE_ALERT to VIC-20
else:
    → Send TRIAGE_DECISION to The Stick
```

### 3. Redis Pub/Sub Broadcasting
**Location:** `backend/app/ai_agents/distributed/message_protocol.py`

When Hawkington makes a decision, he broadcasts it to Redis:

```python
# Redis channel: 'agents:broadcast'
message = {
    'type': 'TRIAGE_ALERT',
    'from_agent': 'sir_hawkington',
    'to_agent': 'vic_20_sage',
    'resource_type': 'cpu',
    'current_value': 85.0,
    'threshold': 80.0,
    'severity': 'medium',
    'confidence': 0.85
}
```

**All agents subscribe to Redis channels:**
- `agents:broadcast` - General messages
- `agents:decisions` - Triage decisions
- `agents:emergency` - Emergency alerts
- `agents:heartbeats` - Agent health checks

### 4. VIC-20 Coordination
**Location:** `backend/app/ai_agents/vic_20_sage/distributed_vic20.py`

```python
# VIC-20 receives TRIAGE_ALERT from Redis
# Determines specialist based on resource_type
if resource_type == 'cpu' or resource_type == 'memory':
    specialist = 'meth_snail'
elif resource_type == 'disk':
    specialist = 'hamsters'
elif resource_type == 'network':
    specialist = 'quantum_shadow_people'

# Queries historical patterns from vector database
historical_patterns = query_vector_db(resource_type)

# Generates recommendation
recommendation = {
    'action': 'investigate',
    'confidence': 0.75,
    'reasoning': 'Based on 10 similar past incidents'
}

# Sends COORDINATION_REQUEST to specialist
broadcast_to_redis({
    'type': 'COORDINATION_REQUEST',
    'to_agent': specialist,
    'recommendation': recommendation
})
```

### 5. Specialist Action
**Example: Terry receives coordination request**

```python
# Terry receives COORDINATION_REQUEST from Redis
# Decides whether to follow VIC-20's recommendation
if should_follow_recommendation:
    execute_cache_clear()
    shell_spin_count += 1
else:
    # Override with own decision
    pass

# Reports back to VIC-20
broadcast_to_redis({
    'type': 'ACTION_REPORT',
    'action_taken': 'cache_clear_executed',
    'memory_freed_mb': 250.5
})
```

### 6. WebSocket Broadcasting
**Location:** `backend/app/api/websockets.py`

Redis messages are forwarded to WebSocket clients (frontend):

```python
# WebSocketManager subscribes to Redis channels
# Forwards messages to connected frontend clients

# Two types of messages:
1. system_update (every 5 seconds)
   - Agent status
   - System metrics
   
2. Individual messages (real-time)
   - triage_decision
   - coordination_request
   - agent_message
   - agent_insight
```

---

## The Database Layer

### PostgreSQL Tables
**Location:** `backend/app/models/`

1. **agent_memory_banks** - Structured agent decisions
   - `sir_hawkington_memory_bank` - Hawkington's triage decisions
   - `vic20_memory_bank` - VIC-20's coordination decisions
   - `the_stick_memory_bank` - The Stick's learned patterns

2. **Vector Tables** (pgvector extension)
   - `decision_vectors` - Embeddings of past decisions
   - `pattern_vectors` - Learned patterns from The Stick
   - `agent_interaction_vectors` - Agent communication patterns

### How Vector Search Works

```python
# VIC-20 queries for similar past incidents
query = "High CPU usage at 85%"
query_embedding = generate_embedding(query)

# Search vector database for similar decisions
similar_decisions = vector_search(
    query_embedding,
    limit=10,
    threshold=0.7  # Similarity threshold
)

# Returns past decisions with similar characteristics
# Used to generate recommendations
```

---

## The Frontend Connection

### WebSocket Hook
**Location:** `frontend/src/hooks/useWebSocketConnection.ts`

```typescript
// Connects to backend WebSocket
ws://192.168.1.127:8000/ws/simplified-metrics

// Receives two types of messages:
1. system_update - Every 5 seconds
   {
     type: 'system_update',
     metrics: { cpu_usage, memory_usage, ... },
     agents: { sir_hawkington: {...}, vic20_sage: {...}, ... }
   }

2. Real-time messages
   {
     type: 'triage_decision',
     data: { from_agent, to_agent, resource_type, ... }
   }
```

### Redux Store
**Location:** `frontend/src/store/slices/`

- `agentsSlice.ts` - Agent status and personality traits
- `communicationSlice.ts` - Agent messages and coordination
- `metricsSlice.ts` - System metrics

### Key Components
**Location:** `frontend/src/components/distributed/`

1. **DistributedAgentDashboard** - Main agent cards display
2. **AgentMonitorDashboard** - Backend log viewer (Redis, Postgres, Vector, System)
3. **AgentCoordinationFlow** - Visualizes decision chains (currently not populating)
4. **SystemHealthNarrative** - Real-time agent story

---

## What You Need to Know

### Redis Pub/Sub (The Part You Lost Track Of)

**What it is:** A messaging system where agents publish messages to channels, and other agents subscribe to those channels.

**Why we use it:** 
- Agents can communicate without knowing about each other
- Messages are broadcast to all interested parties
- Decouples agent logic from communication

**How it works in your system:**

```python
# Agent publishes a message
await redis_client.publish(
    channel='agents:broadcast',
    message=json.dumps({
        'type': 'TRIAGE_ALERT',
        'from_agent': 'sir_hawkington',
        'data': {...}
    })
)

# Other agents subscribe to the channel
pubsub = redis_client.pubsub()
await pubsub.subscribe('agents:broadcast')

# They receive the message
async for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        # Handle the message
```

**In your system:**
- Hawkington publishes triage decisions → Redis
- VIC-20 subscribes to triage alerts → receives from Redis
- VIC-20 publishes coordination requests → Redis
- Specialists subscribe to coordination requests → receive from Redis
- WebSocket manager subscribes to all channels → forwards to frontend

It's like a bulletin board where agents post messages and others read them.

---

## The Critical Path (What Happens When CPU Spikes)

1. **psutil detects CPU at 85%**
2. **SimplifiedMetricsService** collects all metrics
3. **Hawkington** receives metrics, calculates stress score
4. **Hawkington** identifies CPU as primary problem
5. **Hawkington** broadcasts TRIAGE_ALERT to Redis (`agents:broadcast` channel)
6. **VIC-20** receives TRIAGE_ALERT from Redis subscription
7. **VIC-20** queries vector database for similar past CPU incidents
8. **VIC-20** determines Terry (meth_snail) is the CPU specialist
9. **VIC-20** broadcasts COORDINATION_REQUEST to Redis
10. **Terry** receives COORDINATION_REQUEST from Redis subscription
11. **Terry** decides to execute cache clear
12. **Terry** broadcasts ACTION_REPORT to Redis
13. **The Stick** receives all messages, logs for learning
14. **WebSocket manager** forwards all Redis messages to frontend
15. **Frontend** displays agent activities in real-time

---

## File Structure (Where Everything Lives)

```
backend/
├── app/
│   ├── ai_agents/
│   │   ├── distributed/
│   │   │   ├── distributed_agent.py          # Base class for all agents
│   │   │   ├── distributed_agent_manager.py  # Manages all agents
│   │   │   ├── message_protocol.py           # Message types and Redis pub/sub
│   │   │   └── communication_hub.py          # Redis broadcasting logic
│   │   │
│   │   ├── sir_hawkington/
│   │   │   ├── triage_engine.py              # Main triage logic
│   │   │   ├── decision_engine.py            # Hawkington's brain
│   │   │   └── distributed_hawkington.py     # Distributed wrapper
│   │   │
│   │   ├── vic_20_sage/
│   │   │   ├── distributed_vic20.py          # Main coordination logic
│   │   │   └── decision_engine.py            # VIC-20's brain
│   │   │
│   │   ├── meth_snail/
│   │   │   └── distributed_meth_snail.py     # Terry's logic
│   │   │
│   │   ├── hamsters/
│   │   │   ├── distributed_hamsters.py       # Hamsters' logic
│   │   │   └── decision_engine_sbcV3.py      # Hamsters' brain
│   │   │
│   │   ├── quantum_shadow_people/
│   │   │   └── distributed_qsp.py            # QSP's logic
│   │   │
│   │   └── the_stick/
│   │       └── distributed_stick.py          # The Stick's logic
│   │
│   ├── services/
│   │   ├── metrics/
│   │   │   ├── simplified_metrics_service.py # Main metrics collector
│   │   │   ├── simplified_cpu_service.py     # CPU metrics (psutil)
│   │   │   ├── simplified_memory_service.py  # Memory metrics (psutil)
│   │   │   ├── simplified_disk_service.py    # Disk metrics (psutil)
│   │   │   └── simplified_network_service.py # Network metrics (psutil)
│   │   │
│   │   └── agent_insight_emitter.py          # WebSocket broadcasting helper
│   │
│   ├── api/
│   │   ├── websockets.py                     # WebSocket manager (Redis → WebSocket)
│   │   └── simplified_websocket_routes.py    # WebSocket endpoints
│   │
│   └── models/
│       └── agent_memory_banks.py             # PostgreSQL table definitions
│
frontend/
├── src/
│   ├── hooks/
│   │   └── useWebSocketConnection.ts         # WebSocket client
│   │
│   ├── store/slices/
│   │   ├── agentsSlice.ts                    # Agent state
│   │   ├── communicationSlice.ts             # Messages
│   │   └── metricsSlice.ts                   # System metrics
│   │
│   └── components/distributed/
│       ├── DistributedAgentDashboard.tsx     # Main dashboard
│       ├── AgentMonitorDashboard.tsx         # Log viewer
│       ├── AgentCoordinationFlow.tsx         # Decision chains
│       └── SystemHealthNarrative.tsx         # Agent story
```

---

## Common Patterns

### How to Add a New Agent Action

1. **Agent detects condition** (in `distributed_<agent>.py`)
2. **Agent broadcasts to Redis** (using `communication_hub`)
3. **Agent emits insight for WebSocket** (using `emit_agent_insight`)
4. **Frontend receives and displays** (via WebSocket → Redux → Component)

### How to Query Historical Data

```python
# In any agent's distributed file
from app.core.database import get_async_db

async with get_async_db() as db:
    # Query vector database
    similar_decisions = await db.execute(
        select(DecisionVectors)
        .order_by(DecisionVectors.embedding.cosine_distance(query_embedding))
        .limit(10)
    )
```

### How to Broadcast a Message

```python
# In any agent's distributed file
from app.ai_agents.distributed.message_protocol import MessageType, Priority

await self.broadcast_to_agents(
    message_type=MessageType.COORDINATION_REQUEST,
    payload={
        'resource_type': 'cpu',
        'action': 'investigate'
    },
    priority=Priority.HIGH
)
```

---

## What's Actually Complex (And What's Not)

### Complex:
- **Vector database queries** - Similarity search for past decisions
- **Redis pub/sub** - Asynchronous message passing between agents
- **WebSocket real-time updates** - Bidirectional communication with frontend

### Not Complex:
- **Metrics collection** - Just psutil calls every 5 seconds
- **Agent decision logic** - Simple if/else based on thresholds
- **Database storage** - Standard PostgreSQL inserts

### The Key Insight:
Most of the "complexity" is just **message passing**. Agents don't directly call each other - they publish messages to Redis, and interested agents subscribe. This keeps them decoupled but makes the flow harder to trace.

---

## Debugging Tips

### To see what's happening in Redis:
```bash
# On Dell or IBM ThinkPad
redis-cli
> SUBSCRIBE agents:broadcast
> SUBSCRIBE agents:decisions
```

### To see what's in the database:
```bash
# On Dell
psql -U postgres system_rebellion
> SELECT * FROM sir_hawkington_memory_bank ORDER BY created_at DESC LIMIT 10;
```

### To see WebSocket messages:
Open browser console → Network tab → WS → Click on WebSocket connection → Messages tab

---

## The Bottom Line

Your system is a **distributed agent network** where:
- Agents monitor system resources
- Agents communicate via Redis pub/sub
- Agents store decisions in PostgreSQL
- Agents learn from past decisions via vector search
- Frontend displays everything in real-time via WebSocket

The "magic" is just message passing. Once you understand that agents publish to Redis and subscribe to Redis, the rest falls into place.

You built something sophisticated, but it's not magic - it's just well-structured message passing with some vector search on top.
