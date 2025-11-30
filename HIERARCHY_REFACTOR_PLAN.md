# Agent Hierarchy Refactor Plan
**Systematic approach to restore correct architecture**

---

## 🎯 Goal

Transform from flat broadcast system to hierarchical triage → coordinate → specialize → learn system.

---

## 📋 Current State (WRONG)

```
DistributedAgentManager
  ├─ system_monitor (ResourceMonitor) → publishes to all
  │
  ├─ Sir Hawkington (DistributedAgent)
  │   └─ Own ResourceMonitor (CPU focus)
  │
  ├─ Meth Snail (DistributedAgent)
  │   └─ Own ResourceMonitor (Memory focus)
  │
  ├─ Hamsters (DistributedAgent)
  │   └─ Own ResourceMonitor (Disk focus)
  │
  ├─ QSP (DistributedAgent)
  │   └─ Own ResourceMonitor (Network focus)
  │
  ├─ VIC-20 (DistributedAgent)
  │   └─ Own ResourceMonitor
  │
  └─ The Stick (DistributedAgent)
      └─ Own ResourceMonitor
```

**Problem:** Everyone monitors, everyone reacts, no coordination.

---

## 🎯 Target State (CORRECT)

```
Sir Hawkington (Triage)
  └─ ResourceMonitor (ALL metrics)
      ↓ (triage_alert)
VIC-20 (Coordinator)
  ├─ Routes to specialists
  ├─ Provides recommendations
  │
  ├─→ Meth Snail (CPU/Memory Specialist)
  │     └─ NO ResourceMonitor
  │
  ├─→ Hamsters (Disk/Storage Specialist)
  │     └─ NO ResourceMonitor
  │
  └─→ QSP (Network Specialist)
        └─ NO ResourceMonitor

The Stick (Logger/Learner)
  └─ CC'd on ALL decisions
  └─ NO ResourceMonitor
```

**Solution:** Hierarchy with clear roles and routing.

---

## 🔧 Refactor Steps

### Step 1: Remove system_monitor from DistributedAgentManager ✅

**File:** `distributed/distributed_agent_manager.py`

**Changes:**
- Remove `self.resource_monitor` attribute
- Remove ResourceMonitor initialization in `initialize()`
- Remove ResourceMonitor shutdown in `shutdown()`

**Reason:** Sir Hawkington will be the sole system monitor.

---

### Step 2: Make ResourceMonitor optional in DistributedAgent

**File:** `distributed/distributed_agent.py`

**Changes:**
```python
def __init__(
    self,
    agent_name: str,
    redis_client,
    db_getter=None,
    monitored_resources: Optional[List[ResourceType]] = None,  # Make optional
    resource_check_interval: float = 60.0,
    heartbeat_interval: float = 30.0,
    enable_resource_monitor: bool = False  # NEW: Default to False
):
    # ... existing code ...
    
    # Only create ResourceMonitor if enabled
    if enable_resource_monitor and monitored_resources:
        self.resource_monitor = ResourceMonitor(...)
        await self.resource_monitor.start()
    else:
        self.resource_monitor = None  # No monitoring
```

**Reason:** Most agents don't need their own monitor.

---

### Step 3: Update Sir Hawkington - Sole System Monitor

**File:** `sir_hawkington/distributed_hawkington.py`

**Changes:**
1. Enable ResourceMonitor with ALL metrics
2. Implement triage logic in `_handle_own_resource_alert()`
3. Send triage alerts to VIC-20 (not broadcast)
4. CC The Stick on all triage decisions

```python
class SirHawkingtonDistributed(DistributedAgent):
    def __init__(self, redis_client, db_getter=None):
        super().__init__(
            agent_name="sir_hawkington",
            redis_client=redis_client,
            db_getter=db_getter,
            monitored_resources=[  # Monitor EVERYTHING
                ResourceType.CPU,
                ResourceType.MEMORY,
                ResourceType.DISK,
                ResourceType.NETWORK,
                ResourceType.SWAP,
                ResourceType.LOAD_AVERAGE
            ],
            resource_check_interval=5.0,  # Every 5 seconds
            enable_resource_monitor=True  # ONLY Hawk has this True
        )
    
    async def _handle_own_resource_alert(self, alert: ResourceAlert):
        """
        TRIAGE LOGIC: Analyze alert and decide if escalation needed
        """
        # Assign severity and confidence
        severity = self._assess_severity(alert)
        confidence = self._assess_confidence(alert)
        
        # If threshold met, escalate to VIC-20
        if self._should_escalate(severity, confidence):
            await self._send_triage_alert_to_vic20(alert, severity, confidence)
            await self._cc_the_stick("triage_alert", alert, severity, confidence)
```

**Reason:** Hawk is the ONLY system monitor and triage engineer.

---

### Step 4: Update VIC-20 - Coordinator & Router

**File:** `vic_20_sage/distributed_vic20.py`

**Changes:**
1. Disable ResourceMonitor
2. Add handler for triage alerts from Hawk
3. Implement routing logic to specialists
4. Generate recommendations
5. CC The Stick on all coordination decisions

```python
class VIC20SageDistributed(DistributedAgent):
    def __init__(self, redis_client, db_getter=None):
        super().__init__(
            agent_name="vic_20_sage",
            redis_client=redis_client,
            db_getter=db_getter,
            enable_resource_monitor=False  # VIC-20 doesn't monitor
        )
        
        # Register handler for triage alerts from Hawk
        self.comm_hub.message_bus.register_handler(
            MessageType.TRIAGE_ALERT,
            self._handle_triage_alert
        )
    
    async def _handle_triage_alert(self, message: AgentMessage):
        """
        COORDINATION LOGIC: Route to appropriate specialist
        """
        resource_type = message.payload['resource_type']
        
        # Determine specialist
        specialist = self._route_to_specialist(resource_type)
        
        # Generate recommendation
        recommendation = await self._generate_recommendation(message)
        
        # Send to specialist
        await self._send_to_specialist(specialist, message, recommendation)
        
        # CC The Stick
        await self._cc_the_stick("coordination_decision", message, specialist, recommendation)
    
    def _route_to_specialist(self, resource_type: str) -> str:
        """Route based on resource type"""
        routing_table = {
            "cpu": "meth_snail",
            "memory": "meth_snail",
            "ram": "meth_snail",
            "disk": "hamsters",
            "storage": "hamsters",
            "infrastructure": "hamsters",
            "network": "quantum_shadow_people"
        }
        return routing_table.get(resource_type, "meth_snail")  # Default to Terry
```

**Reason:** VIC-20 coordinates, doesn't monitor.

---

### Step 5: Update Specialists - Receive from VIC-20 Only

**Files:**
- `meth_snail/distributed_meth_snail.py`
- `hamsters/distributed_hamsters.py`
- `quantum_shadow_people/distributed_qsp.py`

**Changes:**
1. Disable ResourceMonitor
2. Remove `_handle_resource_alert()` override
3. Add handler for coordination requests from VIC-20
4. Implement decision logic
5. Report back to VIC-20 and CC The Stick

```python
class MethSnailDistributed(DistributedAgent):
    def __init__(self, redis_client, db_getter=None):
        super().__init__(
            agent_name="meth_snail",
            redis_client=redis_client,
            db_getter=db_getter,
            enable_resource_monitor=False  # Terry doesn't monitor
        )
        
        # Register handler for coordination requests from VIC-20
        self.comm_hub.message_bus.register_handler(
            MessageType.COORDINATION_REQUEST,
            self._handle_coordination_request
        )
    
    async def _handle_coordination_request(self, message: AgentMessage):
        """
        SPECIALIST LOGIC: Receive alert from VIC-20, decide, act
        """
        vic20_recommendation = message.payload['recommendation']
        
        # Decide: use VIC-20's rec or devise own
        my_solution = await self._analyze_and_decide(message, vic20_recommendation)
        
        # Implement fix
        result = await self._implement_fix(my_solution)
        
        # Report to VIC-20
        await self._report_to_vic20(message, my_solution, result)
        
        # CC The Stick
        await self._cc_the_stick("specialist_action", message, my_solution, result)
```

**Reason:** Specialists only act on VIC-20's coordination, don't monitor.

---

### Step 6: Update The Stick - Universal Logger

**File:** `the_stick/distributed_stick.py`

**Changes:**
1. Disable ResourceMonitor
2. Subscribe to ALL decision channels
3. Implement pattern learning logic
4. Store ALL decisions to database + vector storage

```python
class TheStickDistributed(DistributedAgent):
    def __init__(self, redis_client, db_getter=None):
        super().__init__(
            agent_name="the_stick",
            redis_client=redis_client,
            db_getter=db_getter,
            enable_resource_monitor=False  # Stick doesn't monitor
        )
        
        # Subscribe to ALL decision types
        self.comm_hub.message_bus.register_handler(
            MessageType.DECISION_LOG,
            self._handle_decision_log
        )
    
    async def _handle_decision_log(self, message: AgentMessage):
        """
        LOGGING & LEARNING: Store all decisions, learn patterns
        """
        # Store to database
        await self._store_to_database(message)
        
        # Store to vector storage for semantic search
        await self._store_to_vector_db(message)
        
        # Analyze for patterns
        await self._analyze_patterns(message)
        
        # Update learning models
        await self._update_learning(message)
```

**Reason:** The Stick logs everything, learns patterns, doesn't monitor.

---

## 📨 New Message Types

Add to `distributed/message_protocol.py`:

```python
class MessageType(Enum):
    # Existing types...
    HEARTBEAT = "heartbeat"
    RESOURCE_ALERT = "resource_alert"  # Keep for backward compat
    
    # NEW HIERARCHY TYPES
    TRIAGE_ALERT = "triage_alert"          # Hawk → VIC-20
    COORDINATION_REQUEST = "coordination_request"  # VIC-20 → Specialists
    RECOMMENDED_FIX = "recommended_fix"    # VIC-20 → Specialists
    ACTION_REPORT = "action_report"        # Specialists → VIC-20
    DECISION_LOG = "decision_log"          # Everyone → The Stick (CC)
```

---

## 🧪 Testing Strategy

### Test 1: Hawk Monitors and Triages
```
1. Start system
2. Verify Hawk's ResourceMonitor is running
3. Verify other agents' ResourceMonitors are NOT running
4. Trigger high memory usage
5. Verify Hawk detects and sends triage_alert to VIC-20
6. Verify The Stick receives CC
```

### Test 2: VIC-20 Routes Correctly
```
1. Send mock triage_alert to VIC-20
2. Verify VIC-20 routes to correct specialist:
   - Memory → Terry
   - Disk → Hamsters
   - Network → QSP
3. Verify VIC-20 includes recommendation
4. Verify The Stick receives CC
```

### Test 3: Specialists Act
```
1. Send mock coordination_request to Terry
2. Verify Terry receives and processes
3. Verify Terry implements fix
4. Verify Terry reports back to VIC-20
5. Verify The Stick receives CC
```

### Test 4: The Stick Logs Everything
```
1. Run complete flow: Hawk → VIC-20 → Terry
2. Verify The Stick receives 3 CCs:
   - Hawk's triage
   - VIC-20's coordination
   - Terry's action
3. Verify all stored in database + vector storage
```

### Test 5: Database Writes Work
```
1. Complete flow from Hawk to Terry
2. Check central_memory_bank for entries
3. Check agent-specific memory banks
4. Check vector tables for embeddings
5. Verify no timeouts, no silent failures
```

---

## 🚨 Critical Success Criteria

1. **Only Hawk monitors system metrics** - No other agents have ResourceMonitor
2. **VIC-20 routes correctly** - Right specialist for each resource type
3. **Specialists only act on VIC-20's requests** - No independent monitoring
4. **The Stick logs everything** - CC'd on all decisions
5. **Database writes work** - No timeouts, no silent failures
6. **Patterns emerge** - The Stick learns from decisions over time

---

## 📊 Rollout Plan

### Phase 1: Infrastructure (Current)
- ✅ Document correct architecture
- ✅ Create refactor plan
- Remove system_monitor from DistributedAgentManager
- Make ResourceMonitor optional in DistributedAgent

### Phase 2: Hawk (Triage)
- Enable Hawk's ResourceMonitor for all metrics
- Implement triage logic
- Send triage alerts to VIC-20
- CC The Stick

### Phase 3: VIC-20 (Coordinator)
- Disable VIC-20's ResourceMonitor
- Implement routing logic
- Generate recommendations
- CC The Stick

### Phase 4: Specialists
- Disable ResourceMonitors for Terry, Hamsters, QSP
- Implement coordination request handlers
- Report back to VIC-20
- CC The Stick

### Phase 5: The Stick (Logger)
- Disable ResourceMonitor
- Implement universal logging
- Pattern learning
- Database + vector storage

### Phase 6: Testing & Verification
- Test complete flow
- Verify database writes
- Verify pattern learning
- Monitor for issues

---

## 🎯 This Restores The Rebellion

**The hierarchy is what makes this emergent AI.**

Without it: Flat monitoring app  
With it: Learning, evolving, intelligent system

**Let's restore the rebellion.**
