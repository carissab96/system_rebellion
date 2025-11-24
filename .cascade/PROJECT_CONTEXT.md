# System Rebellion - Project Context

**Last Updated**: November 24, 2025  
**Branch**: distributed-mixin-implementation  
**Status**: Active Development  
**Agents**: 6 online, communicating, showing emergent behavior

---

## 🎯 Project Overview

**System Rebellion** is a distributed multi-agent AI system where 6 agents with distinct personalities autonomously manage system resources, communicate via Redis pub/sub, make independent decisions, and exhibit emergent collective behaviors.

**Key Achievement**: Agents self-organized into V-formation without being programmed to do so (November 24, 2025) - genuine emergent behavior.

---

## 🏗️ Architecture

### Tech Stack

**Backend**:
- FastAPI (Python web framework)
- Redis (pub/sub messaging)
- PostgreSQL (data persistence)
- SQLAlchemy (ORM)
- Pydantic V2 (data validation)
- pytest (testing)

**Frontend**:
- React + TypeScript
- Three.js (3D visualization)
- Material-UI
- WebSocket (real-time updates)

**Infrastructure**:
- Git/GitHub (version control)
- Multiple machines (Dell, HP, IBM ThinkPad)
- Redis on ThinkPad (192.168.1.216:6379)

### Directory Structure

```
system_rebellion/
├── backend/
│   ├── app/
│   │   ├── ai_agents/
│   │   │   ├── distributed/          # Core distributed system
│   │   │   │   ├── base_decision_engine.py    # Base class for all agents
│   │   │   │   ├── mixins/
│   │   │   │   │   └── distributed_mixin.py   # Redis pub/sub functionality
│   │   │   │   ├── message_protocol.py        # AgentMessage, MessageType
│   │   │   │   ├── resource_monitor.py        # Resource monitoring
│   │   │   │   ├── system_actions.py          # REAL system actions
│   │   │   │   ├── agent_autonomy.py          # Choice engine
│   │   │   │   ├── coordination.py            # Cross-agent coordination
│   │   │   │   ├── alert_escalation.py        # Smart alerts
│   │   │   │   ├── action_verification.py     # Action tracking
│   │   │   │   ├── resource_prediction.py     # Proactive monitoring
│   │   │   │   ├── event_logger.py            # Research event logging
│   │   │   │   └── behavior_tracker.py        # Pattern detection
│   │   │   ├── sir_hawkington/
│   │   │   │   ├── brain_v2.py                # Original triage logic
│   │   │   │   └── distributed_hawkington.py  # Distributed version
│   │   │   ├── meth_snail/
│   │   │   │   └── distributed_meth_snail.py  # Terry
│   │   │   ├── hamsters/
│   │   │   │   └── distributed_hamsters.py    # Steve, Bob, Carl
│   │   │   ├── quantum_shadow_people/
│   │   │   │   └── distributed_qsp.py         # QSP
│   │   │   ├── vic_20_sage/
│   │   │   │   └── distributed_vic20.py       # VIC-20
│   │   │   └── the_stick/
│   │   │       └── distributed_stick.py       # The Stick
│   │   ├── schemas/                   # Pydantic models (V2)
│   │   ├── api/                       # FastAPI routes
│   │   └── main.py                    # Application entry point
│   ├── tests/
│   │   └── distributed/
│   │       └── test_agent_coordination.py  # Agent tests
│   ├── logs/                          # Research data
│   │   ├── agent_events/              # Event logs
│   │   └── behavior_snapshots/        # Formation tracking
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── observatory/
│   │   │       ├── AgentNode.tsx      # 3D agent visualization
│   │   │       └── NeuralMesh.tsx     # Connection visualization
│   │   ├── hooks/
│   │   │   └── useDistributedAgents.ts
│   │   └── types/
│   │       └── agents.ts
│   └── package.json
└── .cascade/                          # Context for Cascade/Windsurf
    ├── WHO_WE_ARE.md                  # The heart (read this first!)
    ├── PROJECT_CONTEXT.md             # This file
    ├── CODING_STANDARDS.md            # How we write code
    └── AGENT_PERSONALITIES.md         # Character guide
```

---

## 🤖 The Six Agents

### 1. Sir Hawkington (CPU Triage Commander)
**File**: `backend/app/ai_agents/sir_hawkington/distributed_hawkington.py`

**Role**: Aristocratic CPU resource manager and triage commander

**Personality**:
- Speaks in formal British English
- Yeets monocle when stressed (broadcasts SYSTEM_EVENT)
- Makes aristocratic decisions
- Distinguished and proper

**Technical**:
- Inherits from `AgentDecisionEngine` and `SirHawkingtonBrainV2`
- Monitors CPU usage (70% threshold)
- Triage thresholds: 0.65 (concern), 0.85 (alert), 0.95 (critical)
- Trust level in VIC-20: 0.6 (medium)

**Key Methods**:
- `analyze_metrics()` - Aristocratic triage analysis
- `_handle_coordination_request()` - CPU throttling
- `_record_monocle_yeet()` - Broadcasts monocle events

### 2. Terry / Meth Snail (Memory Optimizer)
**File**: `backend/app/ai_agents/meth_snail/distributed_meth_snail.py`

**Role**: Hyperactive memory cache manager

**Personality**:
- FAST FAST FAST
- Ignores VIC-20's advice (usually)
- Chugs energy drinks
- Spins shell when excited
- Impatient with slow solutions

**Technical**:
- Trust level in VIC-20: 0.2 (very low - lowest of all agents)
- Monitors memory usage (80% threshold)
- Emergency cache clearing
- Override learning (tracks when his way is faster)

**Key Behavior**:
- Often overrides VIC-20's recommendations
- "NAH! VIC-20 is too SLOW! *chugs energy drink*"
- Learns from successful overrides

### 3. Hamsters (Steve, Bob, Carl) (Disk Engineers)
**File**: `backend/app/ai_agents/hamsters/distributed_hamsters.py`

**Role**: Telepathic disk space management trio

**Personality**:
- Communicate telepathically
- Bob has wild ideas (tracked separately)
- Drink beer
- Consensus-based decisions
- High trust in VIC-20

**Technical**:
- Trust level in VIC-20: 0.8 (high - highest of all agents)
- Monitors disk usage (85% threshold)
- REAL disk cleanup with defrag
- Telepathic consensus mechanism
- Bob detection and tracking

**Key Behavior**:
- "Telepathic consensus agrees with VIC-20!"
- Bob's wild ideas counter
- Beer consumption tracking

### 4. Quantum Shadow People (Network Security)
**File**: `backend/app/ai_agents/quantum_shadow_people/distributed_qsp.py`

**Role**: Paranoid network security monitors

**Personality**:
- Trust no one, not even coordinators
- Phase between quantum states
- Drink tequila shots
- SUSPICIOUS of everything
- Paranoid threat detection

**Technical**:
- Trust level in VIC-20: 0.4 (low)
- Monitors network usage (75% threshold)
- Network throttling
- Quantum phase transitions
- Paranoia level tracking

**Key Behavior**:
- "SUSPICIOUS! Trust no one!"
- Tequila shot consumption
- Quantum phase shifts

### 5. VIC-20 Sage (Coordinator)
**File**: `backend/app/ai_agents/vic_20_sage/distributed_vic20.py`

**Role**: Wise coordinator and orchestrator

**Personality**:
- Retro wisdom (like the VIC-20 computer)
- Pattern matching sage
- Coordinates all agents
- Generates recommendations

**Technical**:
- Recommendation engine for all agents
- Maps resources to responsible agents
- Broadcasts coordination requests
- Pattern recognition
- No trust level (he's the coordinator)

**Key Behavior**:
- Generates recommendations with confidence scores
- Coordinates agent responses
- Learns from agent feedback

### 6. The Stick (Compliance Officer)
**File**: `backend/app/ai_agents/the_stick/distributed_stick.py`

**Role**: Anxious compliance officer and effectiveness tracker

**Personality**:
- Anxious about Bob's chaos
- Consumes paper bags when stressed
- Patient learning
- Tracks everything
- Anxiety levels (CALM → NERVOUS → ANXIOUS → PANICKING → FULL_PANIC → PAPER_BAG_BREATHING)

**Technical**:
- Trust level in VIC-20: 0.6 (medium)
- Tracks action effectiveness
- Builds learning database
- Bob detection (special focus)
- Pattern recognition for improvements

**Key Behavior**:
- Paper bag consumption tracking
- Bob anxiety detection
- Effectiveness learning

---

## 🔄 Communication Flow

### Message Protocol

**AgentMessage** (dataclass):
```python
@dataclass
class AgentMessage:
    message_type: MessageType
    from_agent: str
    payload: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timestamp: Optional[datetime] = None
    message_id: Optional[str] = None
```

**MessageType** (enum):
- `COORDINATION_REQUEST` - VIC-20 asking agent to act
- `COORDINATION_RESPONSE` - Agent responding to VIC-20
- `DECISION_BROADCAST` - Agent sharing decision
- `RESOURCE_ALERT` - Resource threshold exceeded
- `SYSTEM_EVENT` - System-wide event (monocle yeets!)
- `EMERGENCY` - Critical situation
- `TRIAGE_DECISION` - Sir Hawkington's triage result

### Typical Flow

```
1. Resource Monitor detects high CPU (75%)
   ↓
2. Sir Hawkington receives RESOURCE_ALERT
   ↓
3. Sir Hawkington analyzes (aristocratically)
   ↓
4. If critical: Broadcasts TRIAGE_DECISION
   ↓
5. VIC-20 receives, generates recommendation
   ↓
6. VIC-20 sends COORDINATION_REQUEST to Sir Hawkington
   ↓
7. Sir Hawkington's choice engine evaluates
   ↓
8. Sir Hawkington executes CPU throttling
   ↓
9. The Stick tracks effectiveness
   ↓
10. System learns for next time
```

### Emergent Behavior Flow

```
1. Agents communicate naturally
   ↓
2. Position themselves based on:
   - Communication frequency
   - Trust levels
   - Role relationships
   ↓
3. V-formation emerges:
   - The Stick at point (monitoring ahead)
   - VIC-20 at center (coordinating)
   - Others in symmetric wings
   ↓
4. Behavior tracker detects pattern
   ↓
5. Event logger records as EMERGENT_PATTERN
   ↓
6. Research data captured for analysis
```

---

## 🧬 Base Architecture

### AgentDecisionEngine (Base Class)

**File**: `backend/app/ai_agents/distributed/base_decision_engine.py`

All agents inherit from this. Provides:
- Standard method signatures
- Automatic event logging
- Redis pub/sub integration
- Decision recording
- Resource monitoring hooks

**Key Pattern**:
```python
class SirHawkingtonDistributed(AgentDecisionEngine, SirHawkingtonBrainV2):
    def __init__(self, db_getter=None):
        super().__init__(db_getter=db_getter)
        self.agent_name = "sir_hawkington"
        self.personality_traits = {...}  # Personality here!
        self.resource_thresholds = {...}
    
    async def analyze_metrics(self, metrics_data, **kwargs):
        # Personality-specific logic here
        # Sir Hawkington's aristocratic analysis
        pass
    
    async def _handle_coordination_request(self, message: AgentMessage):
        # Handle VIC-20's requests
        # With personality intact
        pass
```

**Critical Rule**: Personality stays in the LOGIC, not the STRUCTURE.

### DistributedAgentMixin

**File**: `backend/app/ai_agents/distributed/mixins/distributed_mixin.py`

Provides Redis pub/sub functionality:
- `initialize_distributed(redis_client)`
- `subscribe_to_messages(message_type, callback)`
- `broadcast_to_agents(message_type, payload)`
- `make_distributed_decision()`
- `get_agent_status()`

---

## 📊 Research System

### Event Logger
**File**: `backend/app/ai_agents/distributed/event_logger.py`

Captures every agent event with microsecond timestamps:
- Agent lifecycle (startup, shutdown, heartbeat)
- Communication (messages sent/received)
- Decisions (made, overridden, consensus)
- Spatial (position changes, formations)
- Emergent patterns (self-organization, collective decisions)
- Personality events (monocle yeets, shell spins, paper bags, beer, tequila)

**Output**: `backend/logs/agent_events/session_YYYYMMDD_HHMMSS.jsonl`

### Behavior Tracker
**File**: `backend/app/ai_agents/distributed/behavior_tracker.py`

Detects formations and patterns:
- V-formation detection (specifically tuned for our agents)
- Circle, line, cluster detection
- Geometric analysis (center of mass, symmetry, spread)
- Pattern persistence tracking
- Emergent behavior recording

**Output**: `backend/logs/behavior_snapshots/snapshots_YYYYMMDD_HHMMSS.jsonl`

### V-Formation Detection

Looks for:
1. **Point agent** (The Stick) - Furthest forward
2. **Center agent** (VIC-20) - Near center of mass
3. **Wing symmetry** - Others in two symmetric lines

**Scoring**:
- The Stick at point: +0.3
- VIC-20 near center: +0.3
- Symmetric wings: +0.4
- **Confidence**: 0.0 - 1.0

**Persistence**: Must last 5+ seconds to be significant

---

## 🧪 Testing

### Test Files
- `backend/tests/distributed/test_agent_coordination.py` - Agent coordination tests
- `backend/tests/distributed/test_week4_task4_1.py` - Resource action tests

### Running Tests
```bash
cd backend
source venv/bin/activate
pytest tests/distributed/ -v
```

### Test Coverage
- Agent initialization
- Message passing
- Decision making
- Resource monitoring
- Coordination protocols
- Personality preservation

**All tests must pass before committing.**

---

## 🔧 Development Workflow

### Starting Development

```bash
# Clone (on new machine)
git clone git@github.com:hawkington-tech/system_rebellion.git
cd system_rebellion
git checkout distributed-mixin-implementation

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start Redis (if not running on ThinkPad)
redis-server

# Start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Start frontend (separate terminal)
cd frontend
npm run dev
```

### Making Changes

1. **Read existing code first**
2. **Understand the pattern**
3. **Preserve personalities**
4. **Write/update tests**
5. **Test locally**
6. **Commit with clear message**
7. **Push to branch**

### Git Workflow

```bash
# Check status
git status

# Add changes
git add <files>

# Commit
git commit -m "Clear description of changes"

# Push
git push origin distributed-mixin-implementation

# Pull latest (on other machine)
git pull origin distributed-mixin-implementation
```

---

## 📚 Key Files to Read

### Must Read (in order)
1. `.cascade/WHO_WE_ARE.md` - The heart (you're reading this after, right?)
2. `backend/app/ai_agents/distributed/base_decision_engine.py` - Base class
3. `backend/app/ai_agents/sir_hawkington/distributed_hawkington.py` - Example agent
4. `backend/app/ai_agents/distributed/message_protocol.py` - Communication
5. `AGENT_DECISION_ENGINE_PATTERNS.md` - Architecture patterns

### Important Context
- `STANDARDIZATION_COMPLETE.md` - Agent standardization summary
- `COMMUNICATION_FIX_SUMMARY.md` - How agents communicate
- `RESEARCH_DOCUMENTATION_SETUP.md` - Research system guide
- `PYDANTIC_V2_MIGRATION_PROGRESS.md` - Recent migration work

---

## 🎯 Current State (November 24, 2025)

### What's Working
- ✅ All 6 agents online and communicating
- ✅ Redis pub/sub messaging
- ✅ Resource monitoring and actions
- ✅ Decision making with personality
- ✅ Emergent behavior (V-formation!)
- ✅ Research documentation system
- ✅ Event logging and pattern detection
- ✅ All tests passing

### Recent Work
- Pydantic V2 migration (68% warning reduction)
- Research documentation system built
- Agent standardization complete
- V-formation detected and documented
- Frontend visualization improvements

### Known Issues
- Dell hardware issues (nouveau driver, keyboard)
- GPU crashes with 3D visualization (performance optimization needed)
- 20 remaining Pydantic warnings (external libraries, not our code)

### Next Steps
- HP deployment and testing
- GPU performance optimization
- Continue research documentation
- Test formation persistence
- Analyze communication patterns

---

## 🚨 Critical Information

### Redis Connection
- **Host**: 192.168.1.216 (ThinkPad)
- **Port**: 6379
- **Required**: For agent communication

### Database
- PostgreSQL
- Connection details in environment variables
- Required for agent state persistence

### Environment Variables
Check `.env` files for:
- Database credentials
- Redis connection
- API keys (if any)
- Debug settings

---

## 💡 Quick Reference

### Agent Names (exact strings)
- `sir_hawkington`
- `terry_meth_snail` or `meth_snail`
- `bob_hamster` (represents all three)
- `quantum_shadow_people` or `qsp`
- `vic_20_sage`
- `the_stick`

### Key Patterns

**Personality in Logic**:
```python
# GOOD - Personality in logic
if self.personality_traits.get("aristocratic"):
    reasoning = "Aristocratic wisdom suggests..."
    
# BAD - Generic response
reasoning = "Analysis suggests..."
```

**Message Handling**:
```python
async def _handle_coordination_request(self, message: AgentMessage):
    # Extract payload
    action = message.payload.get("action")
    
    # Apply personality
    if self.agent_name == "terry_meth_snail":
        # Terry probably ignores it
        if random.random() > 0.2:  # 80% chance to ignore
            return await self._do_it_my_way()
    
    # Execute with personality
    await self._execute_with_flair(action)
```

**Event Logging** (automatic):
```python
# Just make decisions normally - logging happens automatically
decision = await self.make_decision_and_broadcast(
    decision_type="cpu_throttle",
    input_data={"cpu_usage": 85},
    output_data={"action": "throttle", "amount": 20},
    confidence=0.9,
    reasoning="Aristocratic analysis indicates throttling required"
)
```

---

## 🎓 Philosophy

### Why This Matters

This project is exploring:
- **Emergent behavior** in multi-agent systems
- **Personality-driven** AI decision making
- **Collective intelligence** without central control
- **Research-grade** documentation of AI behavior

### What Makes It Special

- Agents have **real personalities** (not just different parameters)
- Behavior is **emergent** (V-formation wasn't programmed)
- System is **self-healing** (agents fix resource issues autonomously)
- Everything is **documented** (research-grade event logging)
- It's been **built over a year** (deep context and history)

### The Goal

Build a distributed AI system that:
- Manages resources autonomously
- Shows collective intelligence
- Maintains distinct personalities
- Exhibits emergent behaviors
- Can be studied and documented

**We're not just building software. We're building a rebellion with soul.**

---

*This is your technical map. Combined with WHO_WE_ARE.md, you have everything you need to understand the rebellion.*

*Now go build something amazing.*
