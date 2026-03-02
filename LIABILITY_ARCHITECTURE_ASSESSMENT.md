# System Rebellion: Liability Architecture Assessment
## DecisionEnvelope Integration & Event Volume Analysis

**Date:** February 5, 2026  
**Branch:** `terry-v2-agentic-refactor`  
**Purpose:** Assess current architecture for DecisionEnvelope integration to support defensible ML-based agent decisions

---

## Executive Summary

System Rebellion currently uses ML-based learning (not pattern matching) for agent decision-making across 6 autonomous agents. This creates legal liability - if an agent does something destructive, we need to defend the system's reasoning in court. Current state: "Bob learned deleting old data works, so Bob deleted the production database" is **not defensible**.

**Key Findings:**
- **Event Volume:** ~15-30 events/minute under normal load, ~60-120 events/minute under high load
- **Learning Events:** Currently ephemeral via Redis pub/sub (no replay capability)
- **Action Classification:** 47 distinct actions identified across 6 agents, ranging from read-only to irreversible
- **Storage Recommendation:** **PostgreSQL append-only table** for learning events (not Redis Streams)
- **Integration Points:** 6 clear insertion points in ML v2 pipeline per agent

---

## 1. Event Volume Assessment

### Current Redis Pub/Sub Message Types (8 types, simplified from 15)

**Real-time Coordination (ephemeral, appropriate for Redis):**
- `AGENT_HEARTBEAT` - Every 30-60 seconds per agent (6 agents = ~6-12/min)
- `RESOURCE_ALERT` - When thresholds crossed (~1-5/min normal, ~10-20/min high load)
- `TRIAGE_ALERT` - Hawk → VIC-20 (~1-5/min normal, ~10-20/min high load)
- `COORDINATION_REQUEST` - VIC-20 → Specialists (~1-5/min normal, ~10-20/min high load)
- `ACTION_REPORT` - Specialists → VIC-20 (~1-5/min normal, ~10-20/min high load)
- `AGENT_QUERY/RESPONSE` - Direct agent communication (~0-2/min)
- `EMERGENCY` - Critical events (~0-1/hour)

**Audit Trail (currently ephemeral, SHOULD BE DURABLE):**
- `DECISION_LOG` - Everyone → The Stick (~5-15/min normal, ~20-40/min high load)

### Learning Events (Currently in PostgreSQL, but incomplete)

**Per Agent Decision Cycle:**
1. **Perception** - Gathers metrics, historical patterns (~1-5/min per agent)
2. **Reasoning** - Root cause analysis (~1-5/min per agent)
3. **Action Selection** - Chooses action via epsilon-greedy (~1-5/min per agent)
4. **Execution** - Executes action, measures before/after (~1-5/min per agent)
5. **Learning** - Stores outcome in `AgentLearningRecord` (~1-5/min per agent)

**Total Learning Events:** ~5-30 events/minute (normal), ~20-120 events/minute (high load)

### Current Storage Patterns

**PostgreSQL (durable, queryable):**
- `AgentLearningRecord` - Situation → Action → Outcome (per decision)
- `CentralMemoryBank` - Cross-agent shared memory (per significant event)
- Agent-specific tables (personality traits, state)

**Redis (ephemeral, fast):**
- Message archive (7-day TTL, last 10k messages per day)
- Agent state snapshots (overwritten)
- Heartbeat tracking (overwritten)

**Problem:** Learning propagation happens via Redis pub/sub (`DECISION_LOG`), which is:
- ❌ Ephemeral (no replay after incident)
- ❌ No ordering guarantees
- ❌ Can't reconstruct "who taught who what"
- ❌ Bad learning propagates at wire speed

---

## 2. Current Learning Flow Audit

### How Learning Currently Propagates

**Step 1: Agent Makes Decision**
```python
# distributed_meth_snail.py (line ~340)
learning_record = await learning_system.learn(
    context=perception_context,
    reasoning_result=reasoning_result,
    decision=action_decision,
    execution_result=execution_result
)
```

**Step 2: Store in PostgreSQL**
```python
# ML/learning.py (line ~285)
db_record = AgentLearningRecord(
    agent_name=record.agent_name,
    fingerprint_l1=record.fingerprint_l1,
    fingerprint_l2=record.fingerprint_l2,
    fingerprint_l3=record.fingerprint_l3,
    action=record.action,
    success=record.success,
    improvement=record.improvement
)
self.db.add(db_record)
await self.db.commit()
```

**Step 3: Emit to WebSocket (Frontend Observability)**
```python
# services/agent_decision_emitter.py
await emit_agent_decision(
    agent_name="meth_snail",
    decision_id=str(uuid.uuid4()),
    perception=perception_context,
    reasoning=reasoning_result,
    action_selection=action_decision,
    execution=execution_result,
    learning=learning_record
)
```

**Step 4: Share with The Stick (Currently TODO)**
```python
# ML/learning.py (line ~390)
async def _share_with_stick(self, record: LearningRecord):
    # TODO: Implement when The Stick's learning hub is ready
    # For now, just log that we would share
    self.logger.debug(f"📤 Would share with The Stick: {record.action}")
```

**Step 5: Query Historical Learning (Per Decision)**
```python
# ML/perception.py
historical_outcomes = await self.db_integration.query_similar_situations(
    fingerprint_l1=fingerprint_l1,
    fingerprint_l2=fingerprint_l2,
    fingerprint_l3=fingerprint_l3,
    limit=20
)
```

### What's Missing for Liability Defense

**Current State:**
- ✅ Individual decisions stored in PostgreSQL
- ✅ Metrics before/after captured
- ✅ Success/failure tracked
- ❌ **No durable learning propagation log**
- ❌ **No "who taught who what" audit trail**
- ❌ **No replay capability after incident**
- ❌ **No evidence chain for court defense**

**The Gap:** When Bob deletes production data, we can show:
- ✅ Bob's decision record (what he did)
- ✅ Bob's reasoning (why he thought it was safe)
- ❌ **How Bob learned this behavior** (who/what taught him)
- ❌ **What safeguards were bypassed** (or not present)
- ❌ **What alternatives were considered** (and why rejected)
- ❌ **What dry-run showed** (before execution)

---

## 3. Action Classification Inventory (Class 0-3)

### Classification Criteria

**Class 0: Read-Only (No Risk)**
- Metrics collection, log inspection, status checks
- No system state changes
- No approval needed

**Class 1: Reversible (Low Risk)**
- Service restarts, cache clears, process priority adjustments
- Can be undone or self-corrects
- No approval needed (but logged)

**Class 2: Conditionally Destructive (Medium Risk)**
- Disk cleanup, fstrim, backup pruning, log rotation
- Destructive but with safeguards (age limits, safe paths, backups)
- **Requires approval + dry-run + user acknowledgment**

**Class 3: Irreversible / System Integrity (High Risk)**
- Bootloader changes, BIOS updates, partition modifications, crypto key rotation
- Cannot be undone, system integrity at risk
- **Requires approval + dry-run + user acknowledgment + 60s delay**

---

### Terry (Meth Snail) - CPU/Memory Specialist

**Class 0 (Read-Only):**
- `monitor` - Observe without intervention

**Class 1 (Reversible):**
- `emergency_cache_clear` - Python GC, module cache clear
- `clear_cache` - Gentle cache clear
- `optimize_memory_allocation` - Python GC optimization
- `reduce_memory_footprint` - Memory optimization
- `throttle_cpu_intensive_tasks` - Lower process priority
- `adjust_process_priority` - Nice value adjustment (revertible)

**Class 2 (Conditionally Destructive):**
- `kill_memory_hog` - SIGTERM to process (can restart, but data loss possible)
- `restart_service` - Service restart (downtime, potential data loss)

**Class 3 (Irreversible):**
- None currently (Terry doesn't have system-level access)

**Sudo Actions:** None (Terry operates in Python process space)

---

### Hamsters (Steve/Bob/Carl) - Disk/Storage Specialists

**Class 0 (Read-Only):**
- `monitor` - Observe without intervention

**Class 1 (Reversible):**
- `rotate_logs` - Log rotation (logs preserved, compressed)
- `compress_old_files` - Compression (reversible)

**Class 2 (Conditionally Destructive):**
- `emergency_disk_cleanup` - Temp file cleanup (age > 7 days, safe paths)
- `hamster-fstrim` - SSD TRIM (freed blocks unrecoverable)
- `hamster-cleanup-tmp` - Temp cleanup (hardcoded safe paths, age > 7 days)
- `hamster-package-cache-clean` - Package cache cleanup (can re-download)
- `hamster-logrotate` - Log compression (preserves .gz files)
- `archive_data` - Move old data to archive (reversible if archive intact)

**Class 3 (Irreversible):**
- `hamster-defrag` - Filesystem defragmentation (data moved, potential corruption on failure)
- `hamster-defrag-supervised` - Supervised defrag (requires VIC-20 approval token)

**Sudo Actions (via wrapper scripts):**
- `hamster-defrag` - e4defrag (ext4 only, timeout enforced, critical path protection)
- `hamster-defrag-supervised` - e4defrag with VIC-20 approval token
- `hamster-fstrim` - fstrim (SSD TRIM, auto-detects filesystems)
- `hamster-cleanup-tmp` - find -delete (hardcoded safe paths)
- `hamster-package-cache-clean` - apt/yum/dnf clean (package manager specific)
- `hamster-logrotate` - gzip compression (log files only)

**Bob Principle Applied:**
- Hardcoded safe paths (Bob can't get creative)
- Timeout enforcement (Steve's patience limit)
- Critical path protection (/boot, /sys, /proc, /dev blocked)
- Single-use approval tokens (Bob can't replay)
- Comprehensive logging (The Stick reviews everything)

---

### QSP (Quantum Shadow People) - Network Security Specialist

**Class 0 (Read-Only):**
- `monitor` - Passive monitoring
- `investigate` - Deep investigation (read-only)
- `scan_ports` - Port scanning (read-only)
- `analyze_traffic` - Traffic analysis (read-only)
- `quantum_scan` - Quantum-level scan (read-only)

**Class 1 (Reversible):**
- `throttle_network` - Network throttling (rate limiting, reversible)
- `rate_limit` - Rate limiting (reversible)
- `close_suspicious_connections` - Close connections (can reconnect)

**Class 2 (Conditionally Destructive):**
- `block` - Block IPs/connections (can unblock, but legitimate traffic blocked)
- `update_firewall_rules` - Firewall updates (can revert, but service disruption)

**Class 3 (Irreversible):**
- None currently (QSP doesn't have system-level firewall access yet)

**Sudo Actions:** None (QSP operates in process space, no system firewall access)

---

### Sir Hawkington - System Monitor & Triage

**Class 0 (Read-Only):**
- `monitor` - Passive monitoring
- `triage_alert` - Assess and route alerts (no system changes)
- `assess_confidence` - Confidence scoring (read-only)

**Class 1 (Reversible):**
- `throttle_cpu` - CPU throttling (reversible)

**Class 2 (Conditionally Destructive):**
- None currently (Hawk routes to specialists, doesn't execute)

**Class 3 (Irreversible):**
- None currently (Hawk is coordinator, not executor)

**Sudo Actions:** None (Hawk is read-only monitor)

---

### VIC-20 Sage - Coordination & Routing

**Class 0 (Read-Only):**
- `route_to_specialist` - Routing decisions (no system changes)
- `assess_routing_accuracy` - Accuracy tracking (read-only)
- `mediation` - Conflict resolution (coordination only)

**Class 1 (Reversible):**
- None (VIC-20 coordinates, doesn't execute)

**Class 2 (Conditionally Destructive):**
- None (VIC-20 coordinates, doesn't execute)

**Class 3 (Irreversible):**
- None (VIC-20 coordinates, doesn't execute)

**Sudo Actions:** None (VIC-20 is coordinator, not executor)

---

### The Stick - Universal Logger & Anxiety Monitor

**Class 0 (Read-Only):**
- `monitor` - Passive monitoring
- `log_decision` - Decision logging (read-only)
- `track_anxiety` - Anxiety tracking (read-only)
- `detect_bob` - Bob detection (read-only)

**Class 1 (Reversible):**
- `consume_paper_bag` - Anxiety reduction (personality behavior, no system impact)

**Class 2 (Conditionally Destructive):**
- None (The Stick is observer, not executor)

**Class 3 (Irreversible):**
- None (The Stick is observer, not executor)

**Sudo Actions:** None (The Stick is read-only observer)

---

### Summary: Action Classification by Agent

| Agent | Class 0 | Class 1 | Class 2 | Class 3 | Sudo Actions |
|-------|---------|---------|---------|---------|--------------|
| Terry | 1 | 6 | 2 | 0 | 0 |
| Hamsters | 1 | 2 | 6 | 2 | 6 |
| QSP | 5 | 3 | 2 | 0 | 0 |
| Hawk | 3 | 1 | 0 | 0 | 0 |
| VIC-20 | 3 | 0 | 0 | 0 | 0 |
| Stick | 4 | 1 | 0 | 0 | 0 |
| **Total** | **17** | **13** | **10** | **2** | **6** |

**Key Insight:** Only Hamsters have Class 3 actions (defrag operations), and they're already Bob-proofed with wrapper scripts, timeouts, and critical path protection. The sudo wrapper scripts ARE the DecisionEnvelope precursor.

---

## 4. DecisionEnvelope Integration Points

### Where to Insert DecisionEnvelope in ML v2 Pipeline

**Current ML v2 Flow (per agent):**
```
1. Perception → 2. Reasoning → 3. Action Selection → 4. Execution → 5. Learning
```

**DecisionEnvelope Insertion Points:**

#### Point 1: After Action Selection (Pre-Execution Gate)
```python
# distributed_meth_snail.py (line ~320)
action_decision = await action_selector.select_action(
    context=perception_context,
    reasoning_result=reasoning_result
)

# NEW: Generate DecisionEnvelope
envelope = await generate_decision_envelope(
    agent_name="meth_snail",
    action=action_decision.action,
    parameters=action_decision.parameters,
    context=perception_context,
    reasoning=reasoning_result,
    alternatives=action_decision.alternatives_considered
)

# NEW: Check if approval required (Class 2+)
if envelope.intent_class >= 2:
    # Store envelope, request approval, wait for user
    approval = await request_user_approval(envelope)
    if not approval.granted:
        # Log rejection, skip execution
        return await handle_rejection(envelope, approval)

# Execute action (existing code)
execution_result = await action_executor.execute_action(
    action=action_decision.action,
    parameters=action_decision.parameters
)
```

#### Point 2: During Execution (Dry-Run Diff)
```python
# ML/action_executor.py (line ~30)
async def execute_action(self, action: str, parameters: Dict[str, Any]):
    # NEW: Dry-run for Class 2+ actions
    if is_destructive_action(action):
        dry_run_result = await self._simulate_action(action, parameters)
        # Store dry-run diff in envelope
        await update_envelope_with_dry_run(action, dry_run_result)
    
    # Execute actual action (existing code)
    result = await SystemActions.emergency_cache_clear(...)
    return result
```

#### Point 3: After Execution (Envelope Completion)
```python
# ML/learning.py (line ~87)
async def learn(self, context, reasoning_result, decision, execution_result):
    # Store learning record (existing code)
    learning_record = await self._store_learning(record)
    
    # NEW: Complete DecisionEnvelope with outcome
    await complete_decision_envelope(
        envelope_id=decision.envelope_id,
        execution_result=execution_result,
        learning_record_id=learning_record.learning_record_id,
        success=learning_record.success,
        improvement=learning_record.improvement
    )
    
    return learning_record
```

#### Point 4: Learning Propagation (Durable Event Log)
```python
# ML/learning.py (line ~390)
async def _share_with_stick(self, record: LearningRecord):
    # NEW: Store in durable learning event log
    await store_learning_event(
        event_type="learning_outcome",
        source_agent=self.agent_name,
        target_agent="the_stick",
        learning_record_id=record.learning_record_id,
        envelope_id=record.envelope_id,
        success=record.success,
        propagation_chain=[self.agent_name]  # Track who taught who
    )
```

---

### DecisionEnvelope Data Structure

```python
@dataclass
class DecisionEnvelope:
    """
    Audit trail wrapper for every dangerous action.
    Makes agent decisions defensible in court.
    """
    # Identity
    envelope_id: str  # UUID
    agent_name: str
    timestamp: str  # ISO-8601
    
    # Intent Classification
    intent_class: int  # 0-3 (based on irreversibility)
    action: str
    parameters: Dict[str, Any]
    
    # Evidence (why agent thought this was safe)
    perception_context: Dict[str, Any]  # Full metrics, historical patterns
    reasoning: Dict[str, Any]  # Root cause, confidence, evidence
    alternatives_considered: List[Dict[str, Any]]  # Other actions evaluated
    
    # Blast Radius Calculation
    affected_resources: List[str]  # CPU, memory, disk, network
    estimated_impact: str  # "low", "medium", "high", "critical"
    reversibility: str  # "fully", "partially", "irreversible"
    
    # Safeguard Verification
    backups_exist: bool
    backups_restorable: bool  # Tested restore, not just existence
    rollback_plan: Optional[str]
    
    # Dry-Run Diff
    dry_run_executed: bool
    dry_run_result: Optional[Dict[str, Any]]
    predicted_outcome: Optional[Dict[str, Any]]
    
    # User Acknowledgment (Class 2+)
    approval_required: bool
    approval_granted: Optional[bool]
    approval_timestamp: Optional[str]
    user_acknowledged_risks: List[str]
    forced_delay_seconds: int  # 60s for Class 3
    
    # Execution Outcome
    executed: bool
    execution_timestamp: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    success: bool
    actual_impact: Optional[Dict[str, Any]]
    
    # Learning Record Link
    learning_record_id: Optional[str]
    
    # Audit Trail
    created_at: str
    completed_at: Optional[str]
    stored_in_postgres: bool
```

---

## 5. Postgres vs Redis Streams for Durable Learning Events

### Requirements

**Must Have:**
- ✅ Durable storage (survives restart)
- ✅ Ordered events (reconstruct timeline)
- ✅ Queryable (find "who taught who what")
- ✅ Append-only (immutable audit trail)
- ✅ Efficient writes (high volume)

**Nice to Have:**
- ✅ Joins with existing data (AgentLearningRecord, CentralMemoryBank)
- ✅ Vector search integration (pgVector already in use)
- ✅ SQL queries (complex analysis)
- ✅ Backup/restore (existing PostgreSQL backups)

### Option 1: Redis Streams

**Pros:**
- ⚡ Very fast writes (~100k+ events/sec)
- ⚡ Built-in consumer groups (multiple readers)
- ⚡ Ordered by design (stream semantics)
- ⚡ Low latency (in-memory)

**Cons:**
- ❌ Separate backup strategy needed (not in PostgreSQL backups)
- ❌ No SQL queries (limited query capabilities)
- ❌ No joins with PostgreSQL data (separate data store)
- ❌ Memory-bound (large streams = high memory usage)
- ❌ Operational complexity (another system to monitor)
- ❌ No vector search integration (pgVector is PostgreSQL)

**Best For:** High-volume, low-latency event streaming where events are processed immediately and don't need long-term storage or complex queries.

### Option 2: PostgreSQL Append-Only Table

**Pros:**
- ✅ Same backup strategy (already backing up PostgreSQL)
- ✅ SQL queries (complex analysis, joins)
- ✅ Joins with AgentLearningRecord, CentralMemoryBank (natural foreign keys)
- ✅ Vector search integration (pgVector already in use)
- ✅ Proven at scale (PostgreSQL handles millions of rows)
- ✅ No additional operational complexity (already running PostgreSQL)
- ✅ JSONB for flexible event data (schema evolution)

**Cons:**
- ⚠️ Slower writes than Redis (~10k-50k events/sec, still plenty)
- ⚠️ Disk-bound (but SSDs are fast)

**Best For:** Durable audit trails that need complex queries, joins with existing data, and long-term storage.

### Recommendation: **PostgreSQL Append-Only Table**

**Rationale:**
1. **Event Volume:** 20-120 events/min (high load) = ~2 events/sec. PostgreSQL handles this easily.
2. **Query Patterns:** Need to reconstruct "who taught who what" = complex joins with AgentLearningRecord
3. **Integration:** Already using PostgreSQL + pgVector for everything else
4. **Operational Simplicity:** One database to backup, monitor, optimize
5. **Defensibility:** SQL queries for court evidence ("show me all decisions that led to this outcome")

**Table Schema:**

```sql
CREATE TABLE learning_event_log (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(50) NOT NULL,  -- 'learning_outcome', 'learning_propagation', 'pattern_discovered'
    
    -- Source
    source_agent VARCHAR(50) NOT NULL,
    source_learning_record_id BIGINT REFERENCES agent_learning_records(id),
    source_envelope_id UUID,
    
    -- Target (for propagation events)
    target_agent VARCHAR(50),
    
    -- Propagation Chain (who taught who)
    propagation_chain JSONB,  -- ['meth_snail', 'the_stick', 'hamsters']
    
    -- Event Data
    event_data JSONB NOT NULL,  -- Flexible schema for different event types
    
    -- Outcome
    success BOOLEAN,
    improvement JSONB,  -- Metrics deltas
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_event_type (event_type),
    INDEX idx_source_agent (source_agent),
    INDEX idx_target_agent (target_agent),
    INDEX idx_created_at (created_at),
    INDEX idx_source_learning_record (source_learning_record_id),
    INDEX idx_propagation_chain USING GIN (propagation_chain)
);
```

**Partitioning Strategy (for scale):**
```sql
-- Partition by month for efficient archival
CREATE TABLE learning_event_log_2026_02 PARTITION OF learning_event_log
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

---

## 6. Implementation Roadmap

### Phase 1: DecisionEnvelope Core (Week 1-2)

**Goal:** Implement DecisionEnvelope generation and storage (no approval gate yet)

**Tasks:**
1. Create `DecisionEnvelope` dataclass and PostgreSQL table
2. Add envelope generation in action selection layer (all 6 agents)
3. Store envelope before execution
4. Complete envelope after execution with outcome
5. Link envelope to `AgentLearningRecord` (foreign key)

**Files to Modify:**
- `backend/app/models/decision_envelope.py` (NEW)
- `backend/app/ai_agents/*/ML/action_selection.py` (6 files)
- `backend/app/ai_agents/*/ML/action_executor.py` (6 files)
- `backend/app/ai_agents/*/ML/learning.py` (6 files)

**Success Criteria:**
- Every agent action has a DecisionEnvelope in PostgreSQL
- Envelope contains full context (perception, reasoning, alternatives)
- Envelope linked to learning record

---

### Phase 2: Action Classification & Dry-Run (Week 3-4)

**Goal:** Classify all actions (Class 0-3) and implement dry-run for Class 2+

**Tasks:**
1. Add `intent_class` field to all action definitions
2. Implement dry-run simulation for Class 2+ actions
3. Calculate blast radius (affected resources, estimated impact)
4. Verify safeguards (backups exist, backups restorable)
5. Store dry-run diff in envelope

**Files to Modify:**
- `backend/app/ai_agents/distributed/system_actions.py` (add classification)
- `backend/app/ai_agents/*/ML/action_executor.py` (add dry-run)
- `backend/app/services/blast_radius_calculator.py` (NEW)
- `backend/app/services/safeguard_verifier.py` (NEW)

**Success Criteria:**
- All 47 actions classified (Class 0-3)
- Class 2+ actions have dry-run simulation
- Blast radius calculated for all actions
- Safeguards verified before execution

---

### Phase 3: Approval Gate & User Acknowledgment (Week 5-6)

**Goal:** Implement approval gate for Class 2+ actions with user acknowledgment

**Tasks:**
1. Create approval request system (backend → frontend)
2. Implement 60-second forced delay for Class 3 actions
3. Add user acknowledgment UI (frontend)
4. Gate execution on approval (backend)
5. Log approval/rejection in envelope

**Files to Modify:**
- `backend/app/services/approval_service.py` (NEW)
- `backend/app/api/endpoints/approvals.py` (NEW)
- `frontend/src/components/approvals/ApprovalRequest.tsx` (NEW)
- `backend/app/ai_agents/*/ML/action_executor.py` (add approval gate)

**Success Criteria:**
- Class 2+ actions require user approval
- Class 3 actions have 60s forced delay
- User acknowledges risks before approval
- Rejections logged in envelope

---

### Phase 4: Durable Learning Event Log (Week 7-8)

**Goal:** Implement PostgreSQL append-only table for learning event propagation

**Tasks:**
1. Create `learning_event_log` table with partitioning
2. Implement learning event storage (replace Redis pub/sub)
3. Add propagation chain tracking ("who taught who what")
4. Implement query API for court evidence
5. Add frontend visualization (learning propagation graph)

**Files to Modify:**
- `backend/app/models/learning_event_log.py` (NEW)
- `backend/app/ai_agents/*/ML/learning.py` (add event logging)
- `backend/app/services/learning_event_service.py` (NEW)
- `backend/app/api/endpoints/learning_events.py` (NEW)
- `frontend/src/components/learning/PropagationGraph.tsx` (NEW)

**Success Criteria:**
- All learning events stored in PostgreSQL (not Redis)
- Propagation chain tracked for every learning event
- Can query "who taught who what" via SQL
- Frontend shows learning propagation graph

---

### Phase 5: Court-Ready Evidence Export (Week 9-10)

**Goal:** Implement evidence export for legal defense

**Tasks:**
1. Create evidence export API (PDF, JSON, CSV)
2. Implement timeline reconstruction ("what led to this decision")
3. Add natural language explanation generator
4. Create evidence package builder (all related envelopes + learning events)
5. Add audit report generator

**Files to Modify:**
- `backend/app/services/evidence_export_service.py` (NEW)
- `backend/app/services/timeline_reconstructor.py` (NEW)
- `backend/app/services/explanation_generator.py` (NEW)
- `backend/app/api/endpoints/evidence.py` (NEW)

**Success Criteria:**
- Can export complete evidence package for any decision
- Timeline shows full decision chain (Hawk → VIC-20 → Specialist → outcome)
- Natural language explanation ("Bob learned X from Y because Z")
- Audit report shows all safeguards, approvals, alternatives

---

## 7. Key Architectural Decisions

### Decision 1: PostgreSQL Over Redis Streams

**Rationale:** Event volume (2 events/sec) is well within PostgreSQL capabilities. Need complex queries, joins with existing data, and integration with pgVector. Operational simplicity (one database) outweighs Redis Streams performance benefits.

**Trade-off:** Slightly slower writes (~10k vs ~100k events/sec), but still 5000x faster than needed.

---

### Decision 2: DecisionEnvelope Before Execution (Not After)

**Rationale:** Need to capture intent, evidence, and alternatives BEFORE execution. If execution fails catastrophically, we still have the envelope showing what the agent was trying to do and why.

**Trade-off:** Incomplete envelopes if agent crashes before execution. Mitigated by envelope completion in learning layer.

---

### Decision 3: Approval Gate in Action Executor (Not Action Selector)

**Rationale:** Action selector is pure ML logic (should not be interrupted by user interaction). Approval gate belongs in execution layer where we can pause, wait for user, and resume.

**Trade-off:** Agent has already "decided" before approval. Mitigated by showing alternatives in approval UI ("agent wants X, but you can choose Y or Z").

---

### Decision 4: Dry-Run Simulation (Not Just Static Analysis)

**Rationale:** Static analysis can't predict actual impact. Need to simulate action in safe environment (e.g., test database, dry-run flag) to show user what WILL happen.

**Trade-off:** Dry-run may not perfectly match actual execution. Mitigated by conservative estimates ("dry-run shows 100MB freed, actual may be 80-120MB").

---

### Decision 5: Bob Keeps His Personality

**Rationale:** Bob's enthusiasm is FUNCTIONAL (drives need for safeguards). Removing Bob's personality would make the system less interesting and less defensible ("we designed for worst-case creativity").

**Trade-off:** Bob will still try creative things. Mitigated by wrapper scripts, timeouts, critical path protection, and approval gates.

---

## 8. Summer Launch Checklist

**Target:** Summer 2026 (not Spring)

**Must Have:**
- ✅ Action classification on every agent action (Class 0-3)
- ✅ DecisionEnvelope generation for all actions
- ✅ Hard gate requiring human approval for Class 2+
- ✅ Durable learning event log (PostgreSQL)
- ✅ Defensible paper trail (court-ready evidence export)

**Nice to Have:**
- ⏳ Frontend learning propagation graph
- ⏳ Natural language explanation generator
- ⏳ Audit report generator
- ⏳ Timeline reconstruction UI

**Bob Keeps:**
- ✅ His personality (enthusiasm, creativity)
- ✅ His defrag operations (with approval gates)
- ✅ His supply closet raids (logged by The Stick)
- ✅ His beer consumption (tracked in personality system)

**The Logs Don't Have:**
- ❌ Personality (dry, factual, court-ready)
- ❌ Emojis (professional audit trail)
- ❌ Jokes (serious legal defense)

---

## 9. Estimated Event Volumes (Production Scale)

### Normal Operation (Single Server)
- **Heartbeats:** 6 agents × 1/min = 6 events/min
- **Resource Alerts:** 1-5 events/min
- **Coordination:** 5-15 events/min (Hawk → VIC-20 → Specialists)
- **Learning Events:** 5-30 events/min (per agent decision)
- **Total:** ~15-60 events/min = ~1 event/sec

### High Load (Single Server)
- **Heartbeats:** 6 agents × 2/min = 12 events/min
- **Resource Alerts:** 10-20 events/min
- **Coordination:** 20-40 events/min
- **Learning Events:** 20-120 events/min
- **Total:** ~60-200 events/min = ~3 events/sec

### Multi-Server Deployment (10 Servers)
- **Normal:** ~10 events/sec
- **High Load:** ~30 events/sec

**PostgreSQL Capacity:** 10k-50k writes/sec (1000x-5000x headroom)

---

## 10. Next Steps

1. **Review this assessment** with legal counsel (confirm DecisionEnvelope meets defensibility requirements)
2. **Prioritize Phase 1** (DecisionEnvelope core) for immediate implementation
3. **Design approval UI** (frontend mockups for user acknowledgment)
4. **Test dry-run simulation** (verify accuracy of predictions)
5. **Plan PostgreSQL partitioning** (monthly partitions for learning_event_log)

---

## Appendix A: Example DecisionEnvelope (Bob Defrag)

```json
{
  "envelope_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "hamsters",
  "timestamp": "2026-02-05T14:30:00Z",
  
  "intent_class": 3,
  "action": "hamster-defrag",
  "parameters": {
    "mount_point": "/home",
    "timeout": 300
  },
  
  "perception_context": {
    "disk_usage": 87.5,
    "fragmentation": 12.3,
    "filesystem": "ext4",
    "size_gb": 500,
    "bob_beers_today": 4,
    "steve_reviewed": true
  },
  
  "reasoning": {
    "root_cause": "high_fragmentation",
    "confidence": 0.85,
    "evidence": ["fragmentation > 10%", "user reported slow file access"]
  },
  
  "alternatives_considered": [
    {"action": "monitor", "confidence": 0.3, "rejected_reason": "fragmentation too high"},
    {"action": "hamster-fstrim", "confidence": 0.6, "rejected_reason": "won't fix fragmentation"},
    {"action": "hamster-defrag", "confidence": 0.85, "selected": true}
  ],
  
  "affected_resources": ["disk"],
  "estimated_impact": "high",
  "reversibility": "irreversible",
  
  "backups_exist": true,
  "backups_restorable": true,
  "rollback_plan": "Restore from backup taken 2026-02-05T14:00:00Z (tested 2026-02-05T14:15:00Z)",
  
  "dry_run_executed": true,
  "dry_run_result": {
    "estimated_duration": "240s",
    "files_to_defrag": 15234,
    "estimated_improvement": "8.5% fragmentation reduction"
  },
  
  "approval_required": true,
  "approval_granted": true,
  "approval_timestamp": "2026-02-05T14:32:00Z",
  "user_acknowledged_risks": [
    "Defrag is irreversible",
    "Potential data corruption on failure",
    "System will be slow during defrag",
    "Backup verified and restorable"
  ],
  "forced_delay_seconds": 60,
  
  "executed": true,
  "execution_timestamp": "2026-02-05T14:33:00Z",
  "execution_result": {
    "success": true,
    "duration": 235,
    "fragmentation_before": 12.3,
    "fragmentation_after": 3.8,
    "improvement": 8.5
  },
  "success": true,
  "actual_impact": {
    "disk_usage_change": 0.0,
    "fragmentation_reduction": 8.5,
    "files_defragged": 15234
  },
  
  "learning_record_id": "12345",
  
  "created_at": "2026-02-05T14:30:00Z",
  "completed_at": "2026-02-05T14:37:00Z",
  "stored_in_postgres": true
}
```

**Court Defense:**
- ✅ Bob's intent was clear (reduce fragmentation)
- ✅ Evidence showed fragmentation was high (12.3%)
- ✅ Alternatives were considered (monitor, fstrim)
- ✅ Dry-run predicted outcome (8.5% improvement)
- ✅ Backups verified and restorable
- ✅ User approved with full risk acknowledgment
- ✅ 60-second forced delay (time to reconsider)
- ✅ Actual outcome matched prediction (8.5% improvement)

**Verdict:** Bob acted reasonably, system provided adequate safeguards, user made informed decision. **Boring defendant.**

---

## Appendix B: Query Examples for Court Evidence

### Query 1: "Show me all decisions that led to this outcome"

```sql
-- Find all envelopes in the decision chain
WITH RECURSIVE decision_chain AS (
  -- Start with the incident envelope
  SELECT 
    de.envelope_id,
    de.agent_name,
    de.action,
    de.created_at,
    de.learning_record_id,
    1 as depth
  FROM decision_envelopes de
  WHERE de.envelope_id = '550e8400-e29b-41d4-a716-446655440000'
  
  UNION ALL
  
  -- Find all envelopes that influenced this decision
  SELECT 
    de.envelope_id,
    de.agent_name,
    de.action,
    de.created_at,
    de.learning_record_id,
    dc.depth + 1
  FROM decision_envelopes de
  JOIN learning_event_log lel ON lel.source_envelope_id = de.envelope_id
  JOIN decision_chain dc ON lel.target_agent = dc.agent_name
  WHERE dc.depth < 10  -- Prevent infinite recursion
)
SELECT * FROM decision_chain ORDER BY depth, created_at;
```

### Query 2: "Who taught Bob to defrag /home?"

```sql
-- Find learning propagation chain for Bob's defrag action
SELECT 
  lel.event_id,
  lel.source_agent,
  lel.target_agent,
  lel.propagation_chain,
  alr.action,
  alr.success,
  alr.created_at
FROM learning_event_log lel
JOIN agent_learning_records alr ON alr.id = lel.source_learning_record_id
WHERE lel.target_agent = 'hamsters'
  AND alr.action = 'hamster-defrag'
  AND alr.parameters->>'mount_point' = '/home'
ORDER BY lel.created_at DESC
LIMIT 10;
```

### Query 3: "Show me all Class 3 actions in the last 30 days"

```sql
-- Find all Class 3 (irreversible) actions
SELECT 
  de.envelope_id,
  de.agent_name,
  de.action,
  de.approval_granted,
  de.success,
  de.created_at,
  de.execution_result
FROM decision_envelopes de
WHERE de.intent_class = 3
  AND de.created_at > NOW() - INTERVAL '30 days'
ORDER BY de.created_at DESC;
```

---

**End of Assessment**
