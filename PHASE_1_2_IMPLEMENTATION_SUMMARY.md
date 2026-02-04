# Phase 1 & 2 Implementation Summary

## Overview
Implemented Phase 1 (learning events + linear tables) and began Phase 2 (vector similarity) for the learned thresholds system. This provides real-time learning visibility and enables vector-based decision making.

---

## Phase 1: Learning Events & Database Links ✅

### 1. Database Model Updates

**File:** `backend/app/models/learned_thresholds.py`
- Added `central_memory_id` column to `ActionOutcomeRecord` model
- Links action outcomes back to `CentralMemoryBank` for vector similarity queries
- Enables Phase 2 to connect: vector search → CentralMemoryBank → ActionOutcomeRecord

**Migration:** `backend/alembic/versions/2026_02_04_1350-add_central_memory_id_to_action_outcomes.py`
- Adds `central_memory_id` column (nullable, indexed)
- Reversible migration for safety

### 2. Learning Event Emission

**File:** `backend/app/services/agent_decision_emitter.py`
- Added `emit_learning_event()` function for real-time learning broadcasts
- Event types:
  - `threshold_adjusted` - Threshold changed based on outcomes
  - `action_scored` - Action effectiveness recorded
  - `pattern_recorded` - Forecasting pattern stored
  - `forecast_generated` - Proactive action recommended
- WebSocket broadcast to frontend (type: `learning_event`)
- Non-blocking, fails gracefully if no connections

### 3. Integration: LearnedThresholds

**File:** `backend/app/ai_agents/meth_snail/ML/learned_thresholds.py`
- Modified `record_outcome()` to:
  - Accept `user_id` parameter for event emission
  - Compare old vs new threshold before/after recording
  - Emit `threshold_adjusted` event if threshold changed >2%
  - Include reason (false alarms, too late actions)
  - Include confidence and total records
- **Throttling:** Only emits on significant changes (>2%)

### 4. Integration: ActionEffectiveness

**File:** `backend/app/ai_agents/meth_snail/ML/action_effectiveness.py`
- Modified `record_outcome()` to:
  - Accept `central_memory_id` parameter (links to CentralMemoryBank)
  - Accept `user_id` parameter for event emission
  - Store `central_memory_id` in ActionOutcomeRecord
  - Compare old vs new action score before/after recording
  - Emit `action_scored` event if score changed >0.1 or first time
  - Include success rate, sample size, improvement average
- **Throttling:** Only emits on significant changes or first use

### 5. What's NOT Done (Deferred)

**PredictiveEngine integration:**
- Can add `pattern_recorded` and `forecast_generated` events later
- Not critical for initial Phase 1 functionality

**API Endpoints:**
- `/api/learning/status` - Deferred to Phase 3
- `/api/learning/timeline/{agent}` - Deferred to Phase 3
- Frontend can be built once backend is tested

---

## Phase 2: Vector Similarity Search (IN PROGRESS)

### Current State

**Vector Infrastructure (Already Exists):**
- `agent_decision_vectors` table with HNSW index
- `agent_pattern_vectors` table with HNSW index
- `EmbeddingService` (all-MiniLM-L6-v2, 384 dimensions)
- `VectorStorageService` with async operations
- All 6 agents writing to vector tables

**The Gap:**
- Agents write embeddings but never read them
- No similarity search in action selection
- Vector tables accumulating data but not being used for decisions

### What Needs to Be Done

**1. Add Vector Similarity to Action Selection**

In `action_selection_v2.py`, when Terry faces a decision:

```python
# Current system state
current_state_text = create_decision_text(
    agent_name="meth_snail",
    decision_type="optimization",
    description=f"{primary_metric} at {current_value}%",
    reasoning=reasoning_result.root_cause,
    context=current_metrics
)

# Generate embedding
embedding_service = get_embedding_service()
current_embedding = await embedding_service.generate_embedding_async(current_state_text)

# Find similar past situations
vector_storage = get_vector_storage()
similar_decisions = await vector_storage.search_similar_decisions(
    query_embedding=current_embedding,
    agent_name="meth_snail",
    limit=10,
    similarity_threshold=0.7
)

# For each similar decision, get the outcome
for decision in similar_decisions:
    # Follow sql_memory_id → CentralMemoryBank → ActionOutcomeRecord
    outcome = await db.query(ActionOutcomeRecord).filter_by(
        central_memory_id=decision.sql_memory_id
    ).first()
    
    if outcome:
        # Weight by: similarity * success_rate
        score = decision.similarity * (1.0 if outcome.success else 0.0)
        # Use this to inform action selection
```

**2. Store Patterns in Both Tables**

When recording patterns in `predictive_engine.py`:

```python
# Linear table (for timeline/stats)
pattern_record = MetricPatternHistory(...)
db.add(pattern_record)
db.commit()

# Vector table (for similarity search)
pattern_text = create_pattern_text(
    agent_name="meth_snail",
    pattern_type="metric_progression",
    pattern_name=f"{metric_name}_progression",
    description=f"{metric_name}: {starting_value}% → {predicted_value}% in {time_window}min"
)
embedding = await embedding_service.generate_embedding_async(pattern_text)
await vector_storage.store_pattern_vector_fire_and_forget(
    agent_name="meth_snail",
    pattern_type="metric_progression",
    pattern_text=pattern_text,
    embedding=embedding,
    first_observed=datetime.utcnow(),
    last_observed=datetime.utcnow(),
    user_id=user_id,
    sql_pattern_id=str(pattern_record.id)
)
```

---

## Benefits of This Architecture

### Hybrid Approach

**Linear Tables (audit trail):**
- `threshold_learning_records` - What thresholds were crossed, outcomes
- `action_outcome_records` - What actions were taken, results
- `metric_pattern_history` - What patterns were observed
- Used for: Timeline, stats, confidence calculations, frontend display

**Vector Tables (decision making):**
- `agent_decision_vectors` - Semantic similarity of situations
- `agent_pattern_vectors` - Pattern matching across dimensions
- Used for: "What worked in SIMILAR situations?" queries

**The Link:**
- `central_memory_id` connects vector embeddings → CentralMemoryBank → ActionOutcomeRecord
- Phase 2 can query: "Find similar situations" → "What happened in those situations?"

### Real-Time Learning Visibility

**Frontend will see:**
```
[12:34:56] TERRY    Threshold adjusted: memory_usage warning 80% → 85% (5 false alarms)
[12:35:12] TERRY    Action scored: restart_service = 0.87 for cpu_high_memory_thrashing
[12:35:45] HAMSTERS Pattern recorded: disk_usage 82% → 91% in 40min
[12:36:03] TERRY    PROACTIVE: memory will hit critical in 28min (confidence: 0.75)
```

**Learning status cards:**
- Total records, confidence levels
- Top performing actions
- Learning phase (Cold Start → Learning → Established → Expert)

---

## Testing Plan

### Phase 1 Testing (On Dell)

1. **Run migration:**
   ```bash
   alembic upgrade head
   ```

2. **Trigger learning events:**
   - Let Terry make decisions
   - Watch for threshold adjustments (after false alarms/too late)
   - Watch for action scoring (after action executions)

3. **Verify WebSocket emissions:**
   - Frontend should receive `learning_event` messages
   - Check browser console for incoming events

4. **Verify database:**
   ```sql
   SELECT * FROM action_outcome_records WHERE central_memory_id IS NOT NULL;
   ```

### Phase 2 Testing (After Implementation)

1. **Verify vector similarity search:**
   - Terry faces similar situation to past
   - Should find similar decisions via vector search
   - Should retrieve outcomes via central_memory_id link

2. **Compare performance:**
   - Heuristic-only decisions vs vector-informed decisions
   - Measure: success rate, improvement percentage

---

## Files Modified

### Phase 1
- `backend/app/models/learned_thresholds.py` - Added central_memory_id FK
- `backend/alembic/versions/2026_02_04_1350-add_central_memory_id_to_action_outcomes.py` - Migration
- `backend/app/services/agent_decision_emitter.py` - Added emit_learning_event()
- `backend/app/ai_agents/meth_snail/ML/learned_thresholds.py` - Integrated emission
- `backend/app/ai_agents/meth_snail/ML/action_effectiveness.py` - Integrated emission

### Phase 2 (Pending)
- `backend/app/ai_agents/meth_snail/ML/action_selection_v2.py` - Add vector similarity
- `backend/app/ai_agents/meth_snail/ML/predictive_engine.py` - Store in vector tables

---

## Next Steps

1. **Complete Phase 2 vector similarity implementation**
2. **Test on Dell with real data**
3. **Build Phase 3 (API endpoints)**
4. **Build Phase 4 (Frontend UI)**

---

## Commit
- `37b4bc6` - Phase 1 (partial): Add central_memory_id FK, emit_learning_event function, integrate into learned_thresholds and action_effectiveness
