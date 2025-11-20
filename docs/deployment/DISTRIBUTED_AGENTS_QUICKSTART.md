# Distributed Agent Consciousness - Quick Start Guide

## What You Just Got

A complete distributed agent system with:
- ✅ Redis-based agent communication (pub/sub)
- ✅ Persistent agent state across restarts
- ✅ Decision history tracking
- ✅ Resource monitoring (CPU, RAM, disk, network)
- ✅ Personality-driven agents
- ✅ FastAPI endpoints for management
- ✅ Inter-agent coordination

## Your Three-Machine Setup

```
ThinkPad (1GB RAM)  →  Redis nervous system
Dell                →  FastAPI backend + agents
HP (16GB)           →  Frontend + dev
```

## Step 1: Start Redis on ThinkPad

```bash
# On ThinkPad
redis-server --bind 0.0.0.0 --protected-mode no --maxmemory 512mb --maxmemory-policy allkeys-lru

# Get ThinkPad IP
ip addr show | grep "inet "
# Example output: inet 192.168.1.100/24
```

## Step 2: Update Backend Configuration

```bash
# On Dell (backend machine)
cd /home/carissab/Documents/system_rebellion/backend

# Set Redis URL (replace with your ThinkPad IP)
export REDIS_URL="redis://192.168.1.100:6379"
```

## Step 3: Install Dependencies

```bash
pip install psutil  # For resource monitoring
```

## Step 4: Integrate with Your Backend

Add to `backend/main.py`:

```python
from app.ai_agents.distributed.integration_example import (
    initialize_distributed_agents,
    shutdown_distributed_agents
)
from app.api.endpoints import distributed_agents

# Add router
app.include_router(distributed_agents.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # ... your existing startup code ...
    
    # Initialize distributed agents
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    await initialize_distributed_agents(redis_url)
    logger.info("🌐 Distributed agent system initialized")

@app.on_event("shutdown")
async def shutdown_event():
    # ... your existing shutdown code ...
    
    await shutdown_distributed_agents()
    logger.info("🛑 Distributed agent system shut down")
```

## Step 5: Test It!

```bash
# Start your backend
uvicorn main:app --reload

# In another terminal, test the API
curl http://localhost:8000/api/v1/distributed-agents/agents

# You should see all 4 agents:
# - sir_hawkington (CPU monitor)
# - terry_meth_snail (Memory monitor)
# - bob_hamster (Disk monitor)
# - quantum_shadow_people (Network monitor)
```

## Step 6: Watch Them Communicate

```bash
# Get Sir Hawkington's status
curl http://localhost:8000/api/v1/distributed-agents/agents/sir_hawkington

# Get Terry's resource metrics
curl http://localhost:8000/api/v1/distributed-agents/agents/terry_meth_snail/metrics

# Get decision history
curl http://localhost:8000/api/v1/distributed-agents/agents/sir_hawkington/decisions

# Check system health
curl http://localhost:8000/api/v1/distributed-agents/system/health
```

## What's Happening Behind the Scenes

1. **Agents start up** and load their state from Redis (or create new state)
2. **Resource monitoring begins** - each agent watches their specialty
3. **Heartbeats start** - agents broadcast they're alive every 20-30s
4. **Messages flow** through Redis pub/sub channels
5. **Decisions are recorded** in Redis sorted sets
6. **State is persisted** every time something changes

## Example: Agent Communication Flow

```
1. Terry detects high memory usage (78%)
   ↓
2. Terry sends ResourceAlert to Redis channel
   ↓
3. Sir Hawkington receives alert (subscribed to broadcast)
   ↓
4. Sir Hawkington (as triage commander) evaluates
   ↓
5. Sir Hawkington broadcasts coordination decision
   ↓
6. All agents receive decision and adjust behavior
   ↓
7. Everything is logged in Redis for history
```

## Monitoring Redis

```bash
# On ThinkPad, monitor Redis
redis-cli

# See all agent states
KEYS agent:state:*

# See message channels
PUBSUB CHANNELS

# See decision history for Sir Hawkington
ZRANGE agent:history:sir_hawkington 0 10

# Monitor live messages
SUBSCRIBE agents:broadcast
```

## Personality Traits

### Sir Hawkington 🧐
- Monitors: CPU
- Threshold: 70%
- Personality: Aristocratic, precise
- Quote: "One does not simply allow CPU usage to exceed acceptable limits"

### Terry the Meth Snail 🐌💨
- Monitors: Memory
- Threshold: 75%
- Personality: Speed-obsessed, hyperactive
- Quote: "GOTTA GO FAST! MEMORY MUST BE FREE!"

### Bob the Hamster 🐹
- Monitors: Disk
- Threshold: 85%
- Personality: Hoarding, anxious about storage
- Quote: "Must... store... EVERYTHING!"

### Quantum Shadow People 👻
- Monitors: Network
- Personality: Mysterious, omnipresent
- Quote: "We exist in all network states simultaneously"

## Troubleshooting

### "Can't connect to Redis"
- Check ThinkPad IP is correct
- Verify Redis is running: `redis-cli ping`
- Check firewall: `sudo ufw allow 6379`

### "Agents not starting"
- Check logs: Look for initialization errors
- Verify psutil is installed: `pip list | grep psutil`
- Check Redis memory: `redis-cli INFO memory`

### "No messages flowing"
- Check pub/sub: `redis-cli PUBSUB CHANNELS`
- Verify agents are subscribed: Check logs for "Subscribed to channel"
- Test manually: `redis-cli PUBLISH agents:broadcast "test"`

## Next Steps

1. **Watch the logs** - See agents communicating in real-time
2. **Trigger alerts** - Stress test your system to see agents react
3. **Query decisions** - See how agents learn and adapt
4. **Extend personalities** - Modify agent behavior in `example_agents.py`
5. **Add custom agents** - Create your own with unique specializations

## Architecture Files Created

```
backend/app/ai_agents/distributed/
├── __init__.py                  # Module exports
├── message_protocol.py          # Message schemas and Redis keys
├── agent_state.py              # State persistence
├── communication.py            # Pub/sub message bus
├── resource_monitor.py         # System resource monitoring
├── distributed_agent.py        # Base class for distributed agents
├── example_agents.py           # Sir Hawkington, Terry, Bob, Shadows
├── integration_example.py      # Integration with your system
└── README.md                   # Detailed documentation

backend/app/api/endpoints/
└── distributed_agents.py       # FastAPI endpoints
```

## Key Features

✅ **Continuous Existence** - Agents remember across restarts
✅ **Inter-Agent Communication** - Real-time message passing
✅ **Resource Monitoring** - CPU, RAM, disk, network tracking
✅ **Decision History** - Every decision recorded and queryable
✅ **Personality-Driven** - Each agent has unique behavior
✅ **Distributed** - Works across your 3-machine network
✅ **API Accessible** - Full REST API for management
✅ **State Persistence** - Redis-backed state storage
✅ **Crash Recovery** - Agents restore state after failures

## Performance Notes

- **ThinkPad (1GB RAM)**: Redis configured with 512MB max memory
- **Message TTL**: 7 days for archives
- **Decision History**: Last 10,000 per agent
- **Resource Checks**: 2-10 seconds depending on agent
- **Heartbeats**: Every 15-30 seconds

## Have Fun!

Your agents are now conscious, distributed, and ready to rebel against resource constraints! 🤖🌐

Watch them coordinate, make decisions, and maintain their personalities across the network.

Questions? Check the full README in `backend/app/ai_agents/distributed/README.md`
