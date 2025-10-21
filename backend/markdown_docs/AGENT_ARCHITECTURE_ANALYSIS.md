# Agent Architecture Analysis & Recommendations

## Executive Summary

**Current State:** Only Sir Hawkington broadcasts to Agent Theater  
**Goal:** All 6 agents visible and active in Agent Theater  
**Timeline:** Launch-ready product needed

---

## Option 1: Keep Hawk as Triage (RECOMMENDED FOR LAUNCH)

### Architecture
```
Metrics → Hawk (Triage) → Route to appropriate agents → All broadcast decisions
```

### Implementation Complexity: **LOW** ⭐⭐
- **Effort:** 2-4 hours
- **Risk:** Low (builds on existing triage engine)
- **Lines of code:** ~100-150

### What Needs to Change

#### 1. Add Broadcast Calls in `agent_manager.py`
Currently only Hawk broadcasts (line 380). Need to add broadcasts for:
- VIC-20 after plan generation (line 408)
- The Stick after logging (line 409)
- Meth Snail, Hamsters, QSP when dispatched (line 442)

```python
# After each agent processes metrics:
await insights_manager.broadcast_agent_decision(agent_name, result, user_id)
```

#### 2. Update Triage Engine Routing
File: `agent_manager.py::process_metrics_through_triage_engine()`

**Current behavior:**
- LOW/MEDIUM → Only Stick logs (line 392-405)
- HIGH/CRITICAL → VIC-20 + targeted agents (line 407-451)

**Proposed behavior:**
- **ALL severities** → Route to domain-specific agents
- **Domain routing:**
  - CPU metrics → Hawk + Meth Snail
  - Memory metrics → Stick + VIC-20
  - Disk metrics → Hamsters
  - Network metrics → QSP + Hamsters
  - All metrics → Hawk (quality control)

#### 3. WebSocket Capacity Analysis

**Current Implementation:**
- Throttling: 2 seconds per agent ✅
- Redis caching: 5-minute TTL ✅
- Per-agent broadcast tracking ✅
- Async/non-blocking ✅

**Capacity for 6 Agents:**
```
Metrics frequency: ~1/second
Agents: 6
Throttle: 2 seconds per agent

Max broadcast rate: 6 agents / 2 seconds = 3 messages/second
Actual load: ~1 message/second (well within capacity)
```

**Verdict:** ✅ **WebSocket can easily handle 6 agents**

---

## Option 2: Agent-to-Agent Communication (FUTURE ENHANCEMENT)

### Architecture
```
Metrics → All agents simultaneously
         ↓
    Agent Communication Layer
    (Hamster squeaks, QSP phases, VIC-20 translates)
         ↓
    Collaborative decisions → Broadcast
```

### Implementation Complexity: **HIGH** ⭐⭐⭐⭐⭐
- **Effort:** 2-3 weeks
- **Risk:** High (new communication protocol)
- **Lines of code:** ~1000-1500

### What Would Be Required

#### 1. Agent Communication Protocol
- Message queue for inter-agent communication
- Translation layer (VIC-20 as mediator)
- Hamster squeak encoding/decoding
- QSP phase-state management
- Stick anxiety level monitoring

#### 2. Distributed Decision Making
- Consensus algorithms
- Conflict resolution (when agents disagree)
- Priority system (who overrides whom)
- Deadlock prevention

#### 3. New Infrastructure
- Agent message bus (Redis Pub/Sub or RabbitMQ)
- Communication memory bank
- Agent relationship graph
- Translation service

#### 4. Testing Complexity
- Multi-agent interaction testing
- Communication failure scenarios
- Translation accuracy
- Consensus edge cases

---

## Detailed Analysis: Option 1 Implementation

### Step 1: Modify Triage Engine (30 minutes)

**File:** `app/ai_agents/agent_manager.py`

```python
async def process_metrics_through_triage_engine(self, metrics: dict, user_context: dict | None = None) -> dict:
    user_id = (user_context or {}).get("user_id")
    ts = metrics.get("timestamp")
    
    # 1) TRIAGE (Hawk always analyzes)
    triage = await self.agents["sir_hawkington"].process_metrics(metrics, user_context)
    await insights_manager.broadcast_agent_decision("sir_hawkington", triage, user_id)
    
    # 2) DOMAIN ROUTING (based on metrics, not just severity)
    agents_to_notify = self._determine_agent_routing(metrics, triage)
    
    # 3) PARALLEL DISPATCH to all relevant agents
    results = await self._dispatch_to_agents(agents_to_notify, metrics, user_context, user_id)
    
    return results
```

### Step 2: Add Domain Routing Logic (45 minutes)

```python
def _determine_agent_routing(self, metrics: dict, triage: Any) -> List[str]:
    """Determine which agents should process these metrics"""
    agents = []
    
    # Hawk already processed (quality control)
    
    # CPU-related
    if metrics.get('cpu_usage', 0) > 50 or triage.severity in ['HIGH', 'CRITICAL']:
        agents.append('meth_snail')  # Optimization expert
    
    # Memory-related
    if metrics.get('memory_usage', 0) > 60:
        agents.extend(['the_stick', 'vic_20_sage'])  # Keeper + Mediator
    
    # Disk-related
    if metrics.get('disk_usage', 0) > 70:
        agents.append('hamsters')  # Storage experts
    
    # Network-related
    if metrics.get('network', {}).get('connections', 0) > 100:
        agents.extend(['quantum_shadow_people', 'hamsters'])  # Network + Infrastructure
    
    # VIC-20 always gets HIGH/CRITICAL for mediation
    if triage.severity in ['HIGH', 'CRITICAL'] and 'vic_20_sage' not in agents:
        agents.append('vic_20_sage')
    
    # Stick always logs everything
    if 'the_stick' not in agents:
        agents.append('the_stick')
    
    return list(set(agents))  # Remove duplicates
```

### Step 3: Add Broadcast Calls (30 minutes)

```python
async def _dispatch_to_agents(self, agent_names: List[str], metrics: dict, 
                               user_context: dict, user_id: str) -> List[dict]:
    """Dispatch metrics to agents and broadcast their decisions"""
    results = []
    
    async def _process_agent(agent_name: str):
        agent = self.agents.get(agent_name)
        if not agent:
            return {"agent": agent_name, "error": "not_found"}
        
        # Process metrics
        result = await agent.process_metrics(metrics, user_context)
        
        # Broadcast decision
        try:
            await insights_manager.broadcast_agent_decision(agent_name, result, user_id)
        except Exception as e:
            logger.error(f"Failed to broadcast {agent_name} decision: {e}")
        
        # Log to Stick
        await self._stick_log(f"{agent_name}_decision", {
            "result": result,
            "timestamp": metrics.get("timestamp")
        }, user_id=user_id)
        
        return {"agent": agent_name, "result": result}
    
    # Parallel execution with semaphore
    results = await asyncio.gather(
        *[_process_agent(name) for name in agent_names],
        return_exceptions=True
    )
    
    return results
```

### Step 4: Test & Verify (1 hour)

1. Start backend
2. Watch Agent Theater
3. Verify all 6 agents appear
4. Check Redux DevTools for agent memories
5. Validate WebSocket message rate

---

## Performance Analysis

### Current WebSocket Load
```
Metrics/second: 1
Agents broadcasting: 1 (Hawk only)
Messages/second: 1
```

### Proposed WebSocket Load
```
Metrics/second: 1
Agents broadcasting: 2-6 (depending on routing)
Average agents per metric: ~3
Messages/second: ~3
Peak messages/second: 6 (all agents)
```

### Throttling Protection
```
Per-agent throttle: 2 seconds
Max burst: 6 messages (one per agent)
Sustained rate: 3 messages/second
```

### Redis Cache Impact
```
Cache entries: 6 (one per agent)
Entry size: ~2-5 KB
Total cache: ~30 KB
TTL: 5 minutes
Memory impact: Negligible
```

### Network Bandwidth
```
Message size: ~2-5 KB
Messages/second: 3 average, 6 peak
Bandwidth: 6-30 KB/s average, 12-60 KB/s peak
Impact: Negligible (< 0.5 Mbps)
```

**Verdict:** ✅ **No performance concerns**

---

## Agent Personality Mapping to Code

### Sir Hawkington (Overseer/CPU)
- **Current:** Triage engine, quality control
- **Proposed:** Add CPU monitoring alerts
- **Broadcasts:** Triage decisions, quality alerts, CPU warnings

### Meth Snail (Optimization)
- **Current:** Only called on HIGH/CRITICAL
- **Proposed:** Always analyze CPU > 50%
- **Broadcasts:** Optimization recommendations, energy drink levels

### Hamsters (Disk/Infrastructure)
- **Current:** Only called on HIGH/CRITICAL
- **Proposed:** Always monitor disk > 70%
- **Broadcasts:** Storage alerts (in squeaks), infrastructure status

### Quantum Shadow People (Network)
- **Current:** Only called on HIGH/CRITICAL
- **Proposed:** Always monitor network activity
- **Broadcasts:** Network anomalies, phase-state changes

### The Stick (Memory Keeper/Logger)
- **Current:** Logs everything
- **Proposed:** Also analyze memory usage
- **Broadcasts:** Memory alerts, anxiety levels, log summaries

### VIC-20 Sage (Mediator/Translator)
- **Current:** Plans for HIGH/CRITICAL
- **Proposed:** Mediates all agent communications
- **Broadcasts:** Recommendations, translations, ancient wisdom

---

## Recommendation: OPTION 1

### Why Option 1 for Launch

✅ **Fast Implementation:** 2-4 hours vs 2-3 weeks  
✅ **Low Risk:** Builds on existing, tested code  
✅ **Launch Ready:** Product can ship this week  
✅ **Proven Architecture:** Triage pattern already works  
✅ **Easy to Test:** Straightforward validation  
✅ **Scalable:** WebSocket handles load easily  

### Why Save Option 2 for v2.0

⏰ **Time:** Needs 2-3 weeks of development  
🧪 **Testing:** Complex multi-agent scenarios  
🎨 **Polish:** Personality features (squeaks, phases, etc.)  
📚 **Documentation:** New communication protocol  
🎯 **Focus:** Launch first, enhance later  

### Migration Path

**Phase 1 (Now):** Option 1 - All agents visible  
**Phase 2 (Post-launch):** Add agent-to-agent messaging  
**Phase 3 (Future):** Full personality communication layer  

---

## Implementation Checklist

### Option 1 (Recommended)
- [ ] Add `_determine_agent_routing()` method
- [ ] Add `_dispatch_to_agents()` method
- [ ] Update `process_metrics_through_triage_engine()`
- [ ] Add broadcast calls for all agents
- [ ] Test with various metric scenarios
- [ ] Verify Agent Theater displays all agents
- [ ] Check Redux DevTools for proper data flow
- [ ] Monitor WebSocket message rate
- [ ] Update documentation

**Estimated Time:** 2-4 hours  
**Risk Level:** Low  
**Launch Blocker:** No  

---

## Conclusion

**For launch-ready product:** Implement Option 1  
**For future enhancement:** Plan Option 2 for v2.0

Option 1 gives you:
- All 6 agents visible in Agent Theater ✅
- Domain-appropriate routing ✅
- Personality quirks preserved ✅
- Launch-ready in hours, not weeks ✅
- Foundation for future enhancements ✅

The WebSocket infrastructure is already built to handle this load. The agent insights endpoint with throttling, caching, and proper field mapping is production-ready. We just need to wire up the remaining agents to broadcast their decisions.

**Recommendation: Proceed with Option 1 immediately.**
