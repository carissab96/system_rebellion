# Redis Demotion Rule
## Pub/Sub May Wake Agents. It May Never Teach Agents.

**Status:** Architectural Rule (Enforced)  
**Date:** February 5, 2026

---

## The Rule

**Redis pub/sub is for real-time coordination ONLY.**

- ✅ **Allowed:** Wake agents, trigger actions, send alerts, coordinate hierarchy
- ❌ **Forbidden:** Teach agents, propagate learning, share patterns, store decisions

---

## Why This Matters

**The Problem We Solved:**

Before demotion, learning propagation happened via ephemeral Redis pub/sub:
- Bad learning propagated at wire speed
- No replay capability after incidents
- Couldn't reconstruct "who taught who what"
- No audit trail for court defense

**After demotion:**
- Learning stored in PostgreSQL (`LearningEventLog`)
- Durable, queryable, tamper-evident
- Can reconstruct propagation chains
- Court-admissible evidence

---

## What Redis Pub/Sub IS Used For

### 1. Agent Heartbeats
```python
# Agent announces it's alive
await message_bus.publish(AgentMessage(
    message_type=MessageType.AGENT_HEARTBEAT,
    from_agent="hamsters",
    payload={"status": "alive"}
))
```

### 2. Resource Alerts
```python
# Hawk detects high CPU, alerts VIC-20
await message_bus.publish(AgentMessage(
    message_type=MessageType.RESOURCE_ALERT,
    from_agent="sir_hawkington",
    to_agent="vic_20_sage",
    payload={"resource": "cpu", "value": 95.0}
))
```

### 3. Coordination Hierarchy
```python
# VIC-20 routes to specialist
await message_bus.publish(AgentMessage(
    message_type=MessageType.COORDINATION_REQUEST,
    from_agent="vic_20_sage",
    to_agent="meth_snail",
    payload={"action": "investigate_cpu"}
))
```

### 4. Emergency Broadcasts
```python
# Critical system event
await message_bus.publish(AgentMessage(
    message_type=MessageType.EMERGENCY,
    from_agent="sir_hawkington",
    payload={"reason": "disk_critical"}
))
```

---

## What Redis Pub/Sub IS NOT Used For

### ❌ Learning Propagation
```python
# WRONG - Don't do this
await message_bus.publish(AgentMessage(
    message_type=MessageType.LEARNING_UPDATE,  # REMOVED
    payload={"learned": "defrag works on ext4"}
))

# RIGHT - Use PostgreSQL
await db.add(LearningEventLog(
    event_type="learning_propagation",
    source_agent="hamsters",
    target_agent="the_stick",
    event_data={"learned": "defrag works on ext4"}
))
await db.commit()
```

### ❌ Pattern Sharing
```python
# WRONG - Don't do this
await message_bus.publish(AgentMessage(
    message_type=MessageType.PATTERN_DISCOVERED,  # REMOVED
    payload={"pattern": "high_cpu_python"}
))

# RIGHT - Query PostgreSQL
patterns = await db.execute(
    select(AgentLearningRecord)
    .where(AgentLearningRecord.fingerprint_l1 == "cpu_high")
)
```

### ❌ Decision Broadcasting
```python
# WRONG - Don't do this
await message_bus.publish(AgentMessage(
    message_type=MessageType.DECISION_BROADCAST,  # REMOVED
    payload={"decision": "restart_service"}
))

# RIGHT - Use DECISION_LOG to The Stick
await message_bus.publish(AgentMessage(
    message_type=MessageType.DECISION_LOG,
    from_agent="hamsters",
    to_agent="the_stick",
    payload={"envelope_id": envelope_id}
))
# The Stick queries PostgreSQL for full envelope
```

---

## Message Types (Current State)

### Kept (Real-Time Coordination)
- `AGENT_HEARTBEAT` - Agent liveness
- `RESOURCE_ALERT` - System alerts
- `TRIAGE_ALERT` - Hawk → VIC-20
- `COORDINATION_REQUEST` - VIC-20 → Specialists
- `ACTION_REPORT` - Specialists → VIC-20
- `AGENT_QUERY/RESPONSE` - Direct communication
- `DECISION_LOG` - Everyone → The Stick (envelope_id only)
- `EMERGENCY` - Critical events

### Removed (Now in PostgreSQL)
- `AGENT_STATE_CHANGE` - State in database
- `MEMORY_SHARE` - Query database
- `PATTERN_DISCOVERED` - Query database
- `LEARNING_UPDATE` - LearningEventLog
- `DECISION_BROADCAST` - DecisionEnvelope

---

## How to Maintain This Rule

### Code Review Checklist

When reviewing agent code, check for:

1. **No learning in Redis payloads**
   ```python
   # Bad
   payload={"learned_action": "defrag", "success": True}
   
   # Good
   payload={"alert": "disk_high", "value": 87.5}
   ```

2. **No pattern sharing via pub/sub**
   ```python
   # Bad
   await message_bus.publish(pattern_data)
   
   # Good
   await db.add(LearningEventLog(event_data=pattern_data))
   ```

3. **DECISION_LOG only sends envelope_id**
   ```python
   # Bad
   payload={"decision": full_decision_object}
   
   # Good
   payload={"envelope_id": envelope_id}
   # The Stick queries PostgreSQL for full envelope
   ```

### Testing

```python
# Test that learning is NOT in Redis
async def test_no_learning_in_redis():
    # Execute action
    result = await hamsters.execute_action("defrag", params)
    
    # Check Redis messages
    messages = await redis.lrange("messages", 0, -1)
    
    # Assert no learning data in any message
    for msg in messages:
        assert "learned" not in msg
        assert "pattern" not in msg
        assert "success_rate" not in msg
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Redis Pub/Sub (Ephemeral, Fast)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Heartbeats (agent liveness)                            │
│  ✅ Alerts (wake agents)                                   │
│  ✅ Coordination (Hawk → VIC-20 → Specialists)            │
│  ✅ Emergency broadcasts                                   │
│                                                             │
│  ❌ Learning propagation (FORBIDDEN)                       │
│  ❌ Pattern sharing (FORBIDDEN)                            │
│  ❌ Decision details (FORBIDDEN)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ envelope_id only
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL (Durable, Queryable)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ DecisionEnvelope (full audit trail)                   │
│  ✅ LearningEventLog (who taught who what)                │
│  ✅ AgentLearningRecord (situation → action → outcome)    │
│  ✅ CentralMemoryBank (cross-agent memory)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Rule Is Critical for Liability Defense

**In court, you need to prove:**

1. **What the agent learned** → PostgreSQL has full learning records
2. **Who taught the agent** → LearningEventLog has propagation chain
3. **When the learning happened** → Timestamps in database
4. **What evidence supported it** → DecisionEnvelope has full context

**If learning was in Redis:**
- No replay after incident
- No proof of propagation chain
- No tamper-evident trail
- "We don't know what the agent learned" = losing defense

**With learning in PostgreSQL:**
- Complete audit trail
- Queryable propagation chains
- Hash-chain tamper detection
- "Here's exactly what the agent learned and why" = winning defense

---

## Enforcement

**This rule is enforced by:**

1. **Code review** - No learning in Redis payloads
2. **Testing** - Assert no learning data in Redis messages
3. **Architecture** - LearningEventLog is the ONLY way to propagate learning
4. **Documentation** - This file

**If you find learning in Redis pub/sub:**
- Stop
- Move it to PostgreSQL
- Update the agent code
- Add a test to prevent regression

---

## Summary

**Redis pub/sub may wake agents. It may never teach agents.**

This is not a performance optimization. This is a legal defense requirement.

**Status:** Enforced ✅
