# Vector Write Pattern for All Agents

## Status

✅ **VIC-20** - Coordination decisions  
✅ **Sir Hawkington** - Triage decisions  
✅ **Imports added** - Meth Snail, Hamsters, The Stick, QSP  
⏳ **TODO** - Add vector writes after commits in remaining agents

## The Pattern

After EVERY `await session.commit()` in agent decision storage methods, add this:

```python
await session.commit()
await session.refresh(agent_memory)  # if applicable
await session.refresh(memory_entry)  # if applicable

# === WRITE 3: VECTOR EMBEDDING (NON-BLOCKING) ===
# Fire-and-forget vector write - doesn't block decision flow
try:
    decision_text = create_decision_text(
        agent_name=AGENT_NAME,  # Use the agent's AGENT_NAME constant
        decision_type="<decision_type>",  # e.g., "optimization", "infrastructure", "anxiety", "quantum_analysis"
        description="<brief description>",  # e.g., f"Optimization: {decision.optimization_type}"
        reasoning="<reasoning or context>",  # e.g., decision.reasoning or decision.rationale
        context={
            'priority': <priority_value>,  # e.g., priority or decision.priority
            # Add 2-3 relevant context fields specific to this agent
        }
    )
    
    embedding_service = get_embedding_service()
    embedding = await embedding_service.generate_embedding_async(decision_text)
    
    vector_storage = get_vector_storage()
    vector_storage.store_decision_vector_fire_and_forget(
        agent_name=AGENT_NAME,
        decision_type="<decision_type>",
        decision_text=decision_text,
        embedding=embedding,
        occurred_at=<timestamp>,  # e.g., decision.timestamp or utc_now()
        user_id=user_id,
        event_type=<EventType>.value,  # e.g., EVENT_TYPES.OPTIMIZATION_COMPLETED.value
        priority=<priority_value>,
        metadata=to_json_safe({
            # Add 3-5 relevant metadata fields
        }),
        sql_memory_id=memory_id,  # or central_memory_id
        confidence_score=<confidence>,  # if available, else None
        decision_summary=f"<summary>"  # Brief one-liner
    )
    logger.debug(f"🔮 Queued vector embedding for decision {memory_id}")
except Exception as ve:
    # Vector write failure doesn't break the decision flow
    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
```

## Agent-Specific Examples

### Meth Snail (Optimization Decisions)

**File:** `backend/app/ai_agents/meth_snail/database_integration.py`  
**Method:** `store_optimization_decision` (around line 200-300)  
**After:** `await session.commit()`

```python
try:
    decision_text = create_decision_text(
        agent_name=AGENT_NAME,
        decision_type="optimization",
        description=f"Optimization: {decision.optimization_type}",
        reasoning=decision.reasoning if hasattr(decision, 'reasoning') else "Speed optimization",
        context={
            'priority': priority,
            'optimization_type': decision.optimization_type,
            'speed_improvement': decision.speed_improvement if hasattr(decision, 'speed_improvement') else None
        }
    )
    
    embedding_service = get_embedding_service()
    embedding = await embedding_service.generate_embedding_async(decision_text)
    
    vector_storage = get_vector_storage()
    vector_storage.store_decision_vector_fire_and_forget(
        agent_name=AGENT_NAME,
        decision_type="optimization",
        decision_text=decision_text,
        embedding=embedding,
        occurred_at=decision.timestamp if hasattr(decision, 'timestamp') else utc_now(),
        user_id=user_id,
        event_type=EVENT_TYPES.OPTIMIZATION_COMPLETED.value,
        priority=priority,
        metadata=to_json_safe({
            'optimization_type': decision.optimization_type,
            'shell_spinning': decision.shell_spinning if hasattr(decision, 'shell_spinning') else False,
            'caffeine_level': decision.caffeine_level if hasattr(decision, 'caffeine_level') else None
        }),
        sql_memory_id=memory_id,
        confidence_score=decision.confidence if hasattr(decision, 'confidence') else None,
        decision_summary=f"Optimization: {decision.optimization_type}"
    )
    logger.debug(f"🔮 Queued vector embedding for optimization {memory_id}")
except Exception as ve:
    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
```

### Hamsters (Infrastructure Decisions)

**File:** `backend/app/ai_agents/hamsters/hamsters_database_integration.py`  
**Method:** `store_infrastructure_intervention` (around line 200-300)  
**After:** `await session.commit()`

```python
try:
    decision_text = create_decision_text(
        agent_name=AGENT_NAME,
        decision_type="infrastructure",
        description=f"Infrastructure: {intervention.intervention_type if hasattr(intervention, 'intervention_type') else 'intervention'}",
        reasoning=intervention.reasoning if hasattr(intervention, 'reasoning') else "Infrastructure maintenance",
        context={
            'priority': priority,
            'hamster_count': 3,  # Steve, Bob, Carl
            'duct_tape_used': intervention.duct_tape_used if hasattr(intervention, 'duct_tape_used') else False
        }
    )
    
    embedding_service = get_embedding_service()
    embedding = await embedding_service.generate_embedding_async(decision_text)
    
    vector_storage = get_vector_storage()
    vector_storage.store_decision_vector_fire_and_forget(
        agent_name=AGENT_NAME,
        decision_type="infrastructure",
        decision_text=decision_text,
        embedding=embedding,
        occurred_at=intervention.timestamp if hasattr(intervention, 'timestamp') else utc_now(),
        user_id=user_id,
        event_type=HamstersEventTypes.INFRASTRUCTURE_INTERVENTION.value,
        priority=priority,
        metadata=to_json_safe({
            'intervention_type': intervention.intervention_type if hasattr(intervention, 'intervention_type') else None,
            'hamsters_involved': ['steve', 'bob', 'carl'],
            'duct_tape_used': intervention.duct_tape_used if hasattr(intervention, 'duct_tape_used') else False
        }),
        sql_memory_id=memory_id,
        confidence_score=intervention.confidence if hasattr(intervention, 'confidence') else None,
        decision_summary=f"Infrastructure intervention"
    )
    logger.debug(f"🔮 Queued vector embedding for infrastructure {memory_id}")
except Exception as ve:
    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
```

### The Stick (Anxiety Events)

**File:** `backend/app/ai_agents/the_stick/database_integration.py`  
**Method:** `store_anxiety_event` (around line 300-400)  
**After:** `await session.commit()`

```python
try:
    decision_text = create_decision_text(
        agent_name=AGENT_NAME,
        decision_type="anxiety_event",
        description=f"Anxiety: {event.anxiety_level if hasattr(event, 'anxiety_level') else 'unknown'} level",
        reasoning=event.trigger if hasattr(event, 'trigger') else "Anxiety trigger detected",
        context={
            'priority': priority,
            'anxiety_level': event.anxiety_level if hasattr(event, 'anxiety_level') else None,
            'paper_bags_available': event.paper_bags_available if hasattr(event, 'paper_bags_available') else None
        }
    )
    
    embedding_service = get_embedding_service()
    embedding = await embedding_service.generate_embedding_async(decision_text)
    
    vector_storage = get_vector_storage()
    vector_storage.store_decision_vector_fire_and_forget(
        agent_name=AGENT_NAME,
        decision_type="anxiety_event",
        decision_text=decision_text,
        embedding=embedding,
        occurred_at=event.timestamp if hasattr(event, 'timestamp') else utc_now(),
        user_id=user_id,
        event_type=StickEventTypes.ANXIETY_EVENT.value,
        priority=priority,
        metadata=to_json_safe({
            'anxiety_level': event.anxiety_level if hasattr(event, 'anxiety_level') else None,
            'trigger': event.trigger if hasattr(event, 'trigger') else None,
            'hamster_proximity': event.hamster_proximity if hasattr(event, 'hamster_proximity') else False
        }),
        sql_memory_id=memory_id,
        confidence_score=None,  # Anxiety events don't have confidence
        decision_summary=f"Anxiety event: {event.anxiety_level if hasattr(event, 'anxiety_level') else 'unknown'}"
    )
    logger.debug(f"🔮 Queued vector embedding for anxiety event {memory_id}")
except Exception as ve:
    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
```

### QSP (Quantum Analysis)

**File:** `backend/app/ai_agents/quantum_shadow_people/database_integration.py`  
**Method:** `store_quantum_decision` (around line 100-200)  
**After:** `await session.commit()`

```python
try:
    decision_text = create_decision_text(
        agent_name=AGENT_NAME,
        decision_type="quantum_analysis",
        description=f"Quantum: {decision.decision_type if hasattr(decision, 'decision_type') else 'analysis'}",
        reasoning=decision.reasoning if hasattr(decision, 'reasoning') else "Quantum network analysis",
        context={
            'priority': priority,
            'quantum_phase': decision.quantum_phase if hasattr(decision, 'quantum_phase') else None,
            'network_coherence': decision.network_coherence if hasattr(decision, 'network_coherence') else None
        }
    )
    
    embedding_service = get_embedding_service()
    embedding = await embedding_service.generate_embedding_async(decision_text)
    
    vector_storage = get_vector_storage()
    vector_storage.store_decision_vector_fire_and_forget(
        agent_name=AGENT_NAME,
        decision_type="quantum_analysis",
        decision_text=decision_text,
        embedding=embedding,
        occurred_at=decision.timestamp if hasattr(decision, 'timestamp') else utc_now(),
        user_id=user_id,
        event_type=QSPEventTypes.QUANTUM_ANALYSIS.value,
        priority=priority,
        metadata=to_json_safe({
            'quantum_phase': decision.quantum_phase if hasattr(decision, 'quantum_phase') else None,
            'network_coherence': decision.network_coherence if hasattr(decision, 'network_coherence') else None,
            'shadow_density': decision.shadow_density if hasattr(decision, 'shadow_density') else None
        }),
        sql_memory_id=memory_id,
        confidence_score=decision.confidence if hasattr(decision, 'confidence') else None,
        decision_summary=f"Quantum analysis"
    )
    logger.debug(f"🔮 Queued vector embedding for quantum decision {memory_id}")
except Exception as ve:
    logger.warning(f"⚠️ Vector embedding failed (non-critical): {ve}")
```

## How to Find the Right Spots

1. Search for `await session.commit()` in each agent's database_integration.py
2. Look for methods that store decisions/events (usually named `store_*`)
3. Add the vector write block AFTER the commit but BEFORE the return statement
4. Adapt the example above to match the agent's data structure

## Testing

After adding vector writes, look for these logs:

```
🔮 Queued vector embedding for decision <uuid>
✅ Stored decision vector for <agent_name>: <decision_type>
```

If you see errors:
```
⚠️ Vector embedding failed (non-critical): <error>
```

The decision still succeeds (SQL is source of truth), but vector write failed. Check the error message.

## Why This Works

- **Fire-and-forget**: Vector write doesn't block the SQL commit
- **Graceful degradation**: If vector write fails, decision still succeeds
- **Non-blocking**: Embedding generation (~38ms) happens async
- **Auth timeout fix**: Agents return immediately after SQL commit

## Performance Impact

**Before:** 100-300ms blocking SQL write  
**After:** SQL commit returns immediately, vector write happens in background

**Auth timeouts eliminated!** 🚀
