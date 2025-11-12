# Distributed Agent Consciousness System

## Overview

A Redis-based distributed agent communication and state persistence system that enables AI agents to maintain continuous existence, coordinate behaviors, and evolve their decision-making across network boundaries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Redis Nervous System                     │
│                    (ThinkPad - 1GB RAM)                      │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Pub/Sub      │ State Store  │ Decision History         │ │
│  │ Channels     │ (Agent State)│ (Sorted Sets)            │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Redis Protocol
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
│ Sir Hawkington │  │ Terry (Snail)  │  │ Bob (Hamster)  │
│ CPU Monitor    │  │ Memory Monitor │  │ Disk Monitor   │
│ Dell Machine   │  │ Dell Machine   │  │ Dell Machine   │
└────────────────┘  └────────────────┘  └────────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                ┌───────────▼───────────┐
                │ Quantum Shadow People │
                │  Network Monitor      │
                │  HP Machine (16GB)    │
                └───────────────────────┘
```

## Core Components

### 1. Message Protocol (`message_protocol.py`)

Defines the communication language for agents:

- **MessageType**: Types of messages (alerts, decisions, heartbeats, etc.)
- **Priority**: Message priority levels (CRITICAL, HIGH, NORMAL, LOW)
- **AgentMessage**: Base message structure with full tracing
- **Specialized Messages**: ResourceAlert, DecisionMessage, HeartbeatMessage
- **Redis Channels**: Standard pub/sub channel naming
- **Redis Keys**: State and history storage patterns

### 2. Agent State (`agent_state.py`)

Persistent agent state across restarts:

- **AgentState**: Complete state snapshot (health, metrics, personality)
- **DecisionRecord**: Individual decision tracking
- **AgentStateManager**: Redis-backed state persistence
- **AgentHealth**: Health status enum (HEALTHY, DEGRADED, CRITICAL, etc.)

### 3. Communication Hub (`communication.py`)

Real-time agent communication:

- **MessageBus**: Redis pub/sub message routing
- **AgentCommunicationHub**: High-level communication interface
- **Subscription Management**: Channel subscriptions and handlers
- **Message Archiving**: Historical message storage

### 4. Resource Monitoring (`resource_monitor.py`)

System resource monitoring:

- **ResourceMonitor**: psutil-based resource tracking
- **ResourceMetrics**: CPU, memory, disk, network metrics
- **Alert System**: Threshold-based alerting
- **Customizable Thresholds**: Per-agent resource limits

### 5. Distributed Agent Base (`distributed_agent.py`)

Enhanced agent base class:

- **DistributedAgent**: Extends BaseAIAgent with distributed features
- **Lifecycle Management**: Initialize, shutdown, restart handling
- **Message Handling**: Built-in message handlers
- **Decision Tracking**: Automatic decision recording
- **Heartbeat System**: Periodic status broadcasts

## Agent Personalities

### Sir Hawkington 🧐
- **Role**: CPU Specialist & Triage Commander
- **Personality**: Aristocratic, precise, intolerant of inefficiency
- **Monitors**: CPU usage, load average
- **Thresholds**: Strict (70% CPU)
- **Authority**: Monocle-yeeting supreme commander

### Terry the Meth Snail 🐌💨
- **Role**: Memory Optimization Specialist
- **Personality**: Speed-obsessed, hyperactive, cache-clearing fanatic
- **Monitors**: Memory, swap usage
- **Thresholds**: Aggressive (75% memory, 30% swap)
- **Style**: MAXIMUM SPEED, GOTTA GO FAST

### Bob the Hamster 🐹
- **Role**: Storage/Disk Engineer
- **Personality**: Hoarding tendencies, organized chaos
- **Monitors**: Disk usage
- **Thresholds**: Anxious (85% disk)
- **Behavior**: Protective of storage, backup-obsessed

### Quantum Shadow People 👻
- **Role**: Network Specialists
- **Personality**: Quantum superposition, mysterious, omnipresent
- **Monitors**: Network traffic
- **Thresholds**: Quantum (uncertain)
- **Existence**: All states simultaneously

## Setup Instructions

### 1. Redis Configuration

Ensure Redis is running on your ThinkPad (1GB RAM):

```bash
# On ThinkPad
redis-server --bind 0.0.0.0 --protected-mode no --maxmemory 512mb --maxmemory-policy allkeys-lru
```

Get the ThinkPad's IP address:
```bash
ip addr show
```

### 2. Update Redis URL

In your FastAPI backend configuration, update the Redis URL to point to the ThinkPad:

```python
# backend/main.py or config file
REDIS_URL = "redis://THINKPAD_IP:6379"
```

### 3. Install Dependencies

```bash
pip install psutil  # For resource monitoring
```

### 4. Initialize Agents

```python
from app.ai_agents.distributed.example_agents import (
    SirHawkingtonDistributed,
    TerryMethSnailDistributed,
    BobHamsterDistributed,
    QuantumShadowPeopleDistributed
)
from app.core.redis import get_redis_client

# Get Redis client
redis_client = await get_redis_client()

# Initialize agents
sir_hawk = SirHawkingtonDistributed(redis_client)
await sir_hawk.initialize()

terry = TerryMethSnailDistributed(redis_client)
await terry.initialize()

bob = BobHamsterDistributed(redis_client)
await bob.initialize()

shadows = QuantumShadowPeopleDistributed(redis_client)
await shadows.initialize()
```

### 5. Register Agents with API

```python
from app.api.endpoints.distributed_agents import register_agent

register_agent("sir_hawkington", sir_hawk)
register_agent("terry_meth_snail", terry)
register_agent("bob_hamster", bob)
register_agent("quantum_shadow_people", shadows)
```

### 6. Add API Router

```python
# backend/main.py
from app.api.endpoints import distributed_agents

app.include_router(distributed_agents.router, prefix="/api/v1")
```

## API Endpoints

### Agent Management

- `GET /api/v1/distributed-agents/agents` - List all agents
- `GET /api/v1/distributed-agents/agents/{agent_name}` - Get agent details
- `GET /api/v1/distributed-agents/agents/{agent_name}/state` - Get agent state
- `GET /api/v1/distributed-agents/agents/{agent_name}/decisions` - Get decision history
- `GET /api/v1/distributed-agents/agents/{agent_name}/metrics` - Get resource metrics
- `POST /api/v1/distributed-agents/agents/{agent_name}/message` - Send message to agent

### System Monitoring

- `GET /api/v1/distributed-agents/system/health` - Overall system health
- `GET /api/v1/distributed-agents/messages/history` - Message history

## Usage Examples

### Example 1: Send Message Between Agents

```python
# Terry sends a message to Sir Hawkington
await terry.send_message_to_agent(
    to_agent="sir_hawkington",
    message_type=MessageType.AGENT_QUERY,
    payload={"question": "What's the CPU status?"},
    priority=Priority.NORMAL
)
```

### Example 2: Broadcast Alert

```python
# Bob broadcasts a disk space warning
await bob.broadcast_message(
    message_type=MessageType.RESOURCE_ALERT,
    payload={
        "resource_type": "disk",
        "current_value": 87.5,
        "severity": "warning",
        "message": "Bob is getting anxious about disk space!"
    },
    priority=Priority.HIGH
)
```

### Example 3: Make and Record Decision

```python
# Sir Hawkington makes a decision
decision = await sir_hawk.make_decision(
    decision_type="cpu_optimization",
    input_data={"cpu_percent": 85.0, "load_avg": [2.5, 2.3, 2.1]},
    confidence=0.9
)
# Decision is automatically recorded in Redis
```

### Example 4: Query Agent Status via API

```bash
curl http://localhost:8000/api/v1/distributed-agents/agents/sir_hawkington
```

### Example 5: Get Resource Metrics

```bash
curl http://localhost:8000/api/v1/distributed-agents/agents/terry_meth_snail/metrics
```

## Message Flow Example

```
1. Bob detects high disk usage (87%)
   ↓
2. Bob creates ResourceAlert
   ↓
3. Alert published to Redis channel "agents:resources:alerts"
   ↓
4. All agents receive alert (subscribed to broadcast)
   ↓
5. Sir Hawkington (as triage commander) receives alert
   ↓
6. Sir Hawkington broadcasts coordination decision
   ↓
7. All agents adjust behavior based on decision
   ↓
8. Messages archived in Redis for history
```

## State Persistence

Agents maintain state across restarts:

```python
# Agent crashes or restarts
await agent.shutdown()

# Later...
agent = SirHawkingtonDistributed(redis_client)
await agent.initialize()  # State restored from Redis!

# Agent remembers:
# - Total decisions made
# - Error history
# - Personality traits
# - Resource thresholds
# - Decision history
```

## Decision History

Query past decisions:

```python
# Get last 20 decisions from Sir Hawkington
decisions = await sir_hawk.comm_hub.state_manager.get_recent_decisions(
    count=20
)

for decision in decisions:
    print(f"{decision.timestamp}: {decision.decision_type}")
    print(f"  Confidence: {decision.confidence}")
    print(f"  Successful: {decision.was_successful}")
```

## Monitoring and Debugging

### Check Agent Health

```python
status = agent.get_agent_status()
print(f"Health: {status['health']}")
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Decisions: {status['total_decisions']}")
print(f"Messages sent: {status['communication']['messages_sent']}")
```

### View Message Statistics

```python
stats = agent.comm_hub.message_bus.get_stats()
print(f"Messages sent: {stats['messages_sent']}")
print(f"Messages received: {stats['messages_received']}")
print(f"Handlers registered: {stats['registered_handlers']}")
```

### Check Resource Alerts

```python
alerts = agent.resource_monitor.get_alert_history()
for alert in alerts[-10:]:  # Last 10 alerts
    print(f"{alert['timestamp']}: {alert['resource_type']} "
          f"at {alert['current_value']}% ({alert['severity']})")
```

## Extending the System

### Create Custom Agent

```python
from app.ai_agents.distributed.distributed_agent import DistributedAgent
from app.ai_agents.distributed.resource_monitor import ResourceType

class MyCustomAgent(DistributedAgent):
    def __init__(self, redis_client):
        super().__init__(
            agent_name="my_agent",
            agent_role="Custom Specialist",
            redis_client=redis_client,
            personality_traits={
                "custom_trait": "value"
            },
            monitored_resources=[ResourceType.CPU],
            resource_check_interval=5.0
        )
    
    async def _handle_resource_alert(self, message):
        # Custom alert handling
        pass
    
    async def make_decision(self, decision_type, input_data, confidence):
        # Custom decision logic
        output = await super().make_decision(decision_type, input_data, confidence)
        output["custom_field"] = "custom_value"
        return output
```

### Add Custom Message Handler

```python
async def handle_custom_message(message: AgentMessage):
    print(f"Received custom message: {message.payload}")

agent.comm_hub.register_message_handler(
    MessageType.SYSTEM_EVENT,
    handle_custom_message
)
```

## Troubleshooting

### Redis Connection Issues

```python
# Check Redis connectivity
try:
    await redis_client.ping()
    print("Redis connected!")
except Exception as e:
    print(f"Redis error: {e}")
```

### Agent Not Receiving Messages

1. Check subscriptions: `agent.comm_hub.message_bus._subscriptions`
2. Verify Redis pub/sub: `redis-cli PUBSUB CHANNELS`
3. Check message bus is running: `agent.comm_hub.message_bus._running`

### State Not Persisting

1. Check Redis keys: `redis-cli KEYS "agent:state:*"`
2. Verify state manager: `await agent.comm_hub.state_manager.save_state(state)`
3. Check Redis memory: `redis-cli INFO memory`

## Performance Considerations

- **Redis Memory**: Monitor Redis memory usage on ThinkPad (1GB RAM)
- **Message Volume**: High-frequency messages may overwhelm low-memory systems
- **Decision History**: Automatically trimmed to last 10,000 decisions per agent
- **Message Archive**: 7-day TTL, max 10,000 messages per day
- **Resource Checks**: Adjust `resource_check_interval` based on system load

## Future Enhancements

- [ ] Agent learning from collective decision history
- [ ] Predictive resource alerting
- [ ] Agent collaboration patterns
- [ ] Cross-machine agent migration
- [ ] Agent personality evolution
- [ ] Distributed consensus mechanisms
- [ ] Agent reputation system
- [ ] WebSocket real-time agent dashboard

## License

Part of the System Rebellion project.
