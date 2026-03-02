# Pre-Launch Issues & Technical Debt

Running list of issues identified during ML pipeline review that cannot be fixed immediately.
Update this file as new issues are found. Clear items when resolved.

---

## Database / Models

### [DB-01] `ActionOutcomeRecord` has no `system_id` column
- **File:** `backend/app/models/learned_thresholds.py`
- **Impact:** `ActionEffectivenessModel` cannot filter learning records by system. In a multi-system deployment, one system's learning pollutes another's scores.
- **Fix:** Add `system_id = Column(String(255), nullable=False, index=True)` to `ActionOutcomeRecord`, generate Alembic migration, add filter in `_score_action()` and `get_action_statistics()` in `action_effectiveness.py`.
- **Severity:** Medium — no impact in single-system deployment, critical in multi-system.

---

## Hamsters ML Pipeline

### [HAM-01] `_generate_pattern_fingerprint` thresholds are coarse buckets, not learned
- **File:** `backend/app/ai_agents/hamsters/ML/action_effectiveness.py`
- **Context:** Intentionally left as stable bucket boundaries (see comment in code). However, if the system's learned thresholds drift significantly from the bucket edges, fingerprint groupings may not represent real situation clusters well.
- **Fix:** Post-launch, evaluate whether fingerprint buckets should be periodically recalibrated against learned threshold values.
- **Severity:** Low — acceptable for launch, monitor over time.

### [HAM-02] `StickLearning` cache on `self._stick_learning` is session-scoped but `db` session may change
- **File:** `backend/app/ai_agents/hamsters/ML/action_effectiveness.py` — `request_stick_validation()`
- **Context:** `_stick_learning` is cached on the instance after first call. If the `db` session passed via `db_getter` changes between calls (e.g. session expiry), the cached `StickLearning` instance holds a stale session reference.
- **Fix:** Either invalidate cache on session change, or pass `db` into `StickLearning` on each call and accept the instantiation cost.
- **Severity:** Low — only matters if validation is called repeatedly across session boundaries.

### [HAM-03] `_estimate_duration` is fully hardcoded
- **File:** `backend/app/ai_agents/hamsters/ML/action_selection.py`
- **Context:** `TODO(post-launch)` comment already in place. Actual execution times from `action_executor` outcomes should inform these estimates over time.
- **Fix:** Extend `ActionEffectivenessModel` or add a separate duration learning model. Feed actual execution times from `action_executor` outcomes back as training data.
- **Severity:** Low — wrong estimates affect scheduling decisions and system availability windows.

### [HAM-04] `action_effectiveness.py` docstring still references old action names
- **File:** `backend/app/ai_agents/hamsters/ML/action_effectiveness.py` — module docstring (lines 5-7)
- **Context:** Docstring says `cleanup_temp_files vs cleanup_logs vs defrag vs emergency_measures` — these are the old ghost action names, not the current `STORAGE_ACTIONS` list.
- **Fix:** Update module docstring to reflect current action set.
- **Severity:** Low — documentation only, no runtime impact.

---

## Cross-Agent / Architecture

### [ARCH-01] `meth_snail` and `quantum_shadow_people` `action_effectiveness.py` have the same bugs
- **Files:** 
  - `backend/app/ai_agents/meth_snail/ML/action_effectiveness.py`
  - `backend/app/ai_agents/quantum_shadow_people/ML/action_effectiveness.py`
- **Context:** All three agent `action_effectiveness.py` files share the same origin. The bugs fixed in Hamsters (wrong import path, `.query()` syntax, `datetime.utcnow()`, `commit` vs `flush`, silent validation bypass, missing `Any` import) almost certainly exist in Terry's and QSP's versions too.
- **Fix:** Apply the same fixes to both files. Do this before any of the three agents go live.
- **Severity:** High — Terry and QSP will have runtime failures on first learning record write.

### [ARCH-02] `DecisionEnvelopeService` not yet wired — executors not wrapped
- **Context:** Full architecture designed and validated (see memory). DB tables don't exist, executors not wrapped, no approval UI.
- **Fix:** After ML fixes complete: generate migration on Dell, wire `DecisionEnvelopeService`, wrap Hamsters executor first, test Class 2 (fstrim) then Class 3 (defrag with approval), expand to other agents.
- **Severity:** High for production — liability/audit trail incomplete without this.

### [ARCH-03] `LearningPromotionPolicy` not called by any agent learning system
- **Context:** Service exists (`backend/app/services/learning_promotion_policy.py`) but no agent calls it. Successful outcomes can currently promote to default without gating.
- **Fix:** Wire into each agent's learning layer after ML fixes complete.
- **Severity:** Medium — learning without promotion gating means bad patterns could become doctrine.

### [ARCH-04] `distributed_hamsters.py` still calls `action_executor.py` — **BLOCKING before Phase 2**
- **File:** `backend/app/ai_agents/hamsters/distributed_hamsters.py` — lines 306-308
- **Context:** The call chain is broken. `distributed_hamsters.py` still does:
  ```python
  from app.ai_agents.hamsters.ML.action_executor import HamstersActionExecutor
  executor = HamstersActionExecutor()
  cleanup_result = await executor.execute_action(action.action_type, {})
  ```
  `action.action_type` no longer exists (renamed to `action.goal`). `HamstersActionExecutor` is the old static routing table. The new `HamsterPrimitiveExecutor` + `HamsterExecutionPlanner` are not wired in at all. The entire intelligent executor refactor is unreachable until this is updated.
- **Also:** Lines 269, 394, 435, 441, 489, 511 still reference `action.action_type` — all must become `action.goal`.
- **Also:** Lines 476-482 call `request_stick_validation(action=action.action_type, ...)` — must become `action.goal`.
- **Also:** Lines 489 and 511 call `action_selector.update_defrag_bias(action.action_type, ...)` — `update_defrag_bias()` is now a no-op stub; these calls should be removed.
- **Fix:** Wire `HamsterExecutionPlanner` into `_handle_coordination_request()`. Replace `HamstersActionExecutor` call with `planner.compose_plan()` + `planner.execute_plan()`. Call `learning.record_sequence_outcome(execution_result)` after execution. Remove `action_executor.py` import. Remove `update_defrag_bias()` calls.
- **Severity:** **Blocking** — must complete before Phase 2. Dead code with a pulse will cause import errors and attribute errors at runtime.

### [ARCH-05] `flush()` in `learning.py` confirmed safe — outer transaction commits on `async for` loop exit
- **File:** `backend/app/ai_agents/hamsters/ML/learning.py`, called from `distributed_hamsters.py`
- **Context:** Verified. `get_async_db()` is `async with AsyncSessionLocal() as session: yield session`. SQLAlchemy's `async_sessionmaker` context manager commits on clean exit, rolls back on exception. `distributed_hamsters.py` exits the `async for db in db_gen` loop via `break` at line 517, which triggers the generator's `finally`, which triggers the `async with` cleanup — commit fires. The `flush()` calls in `learning.py` and `action_effectiveness.py` are correct: they write to the DB buffer and let the outer transaction own the commit boundary.
- **Action required:** None — confirmed correct. Documented here for audit trail.
- **Severity:** Resolved / informational.

---

## The Stick Validation

### [STICK-01] `record_validation(None, audit_entry)` passes `None` as interaction
- **File:** `backend/app/ai_agents/hamsters/ML/action_effectiveness.py` — `request_stick_validation()`
- **Context:** `await stick_db.record_validation(None, audit_entry)` — the first argument is `None`. Unclear if `StickDatabaseIntegration.record_validation()` handles `None` gracefully or will raise.
- **Fix:** Verify `record_validation` signature and either pass a real interaction object or confirm `None` is a valid no-op sentinel.
- **Severity:** Medium — validation audit trail may be silently incomplete.

### ~~[STICK-02] `user_id` pulled from `records[0].user_id` but `ActionOutcomeRecord` has no `user_id` column~~ ✅ RESOLVED
- Learning is system-level, not user-level. `user_id` removed; `StickLearning` now instantiated with `"system"` unconditionally.

---

## Migrations Required Before Launch

### [MIG-01] `learned_sequences` table does not exist in the database
- **Model:** `backend/app/models/learned_thresholds.py` — `LearnedSequence`
- **Context:** `LearnedSequence` model added during intelligent executor refactor. The table is defined in the ORM but has no Alembic migration yet. The ExecutionPlanner and `record_sequence_outcome()` in `learning.py` will fail at runtime until this table exists.
- **Fix:** Generate Alembic migration on Dell: `alembic revision --autogenerate -m "add_learned_sequences_table"`, review, then `alembic upgrade head`.
- **Severity:** Critical — Hamsters cannot learn sequences without this table.

### ~~[MIG-02] `action_outcome_records` primitive vocabulary mismatch~~ ✅ RESOLVED (no migration needed)
- **Decision:** Old rows with composite names (`cleanup`, `defrag_only`, etc.) are inert. `score_all_actions()` only iterates `STORAGE_ACTIONS` (primitive vocabulary) and queries by exact action name — it never asks for `cleanup` or `defrag_only`, so those rows are never returned and cannot contaminate scores. `record_outcome()` now rejects non-primitive action names at write time with a hard exception. Old rows will age out of the 60-day scoring window naturally. No data migration needed.

---

*Last updated: Feb 18, 2026 — Opus review addressed: ARCH-04 (distributed_hamsters wiring, blocking), ARCH-05 (flush/commit verified safe), defrag_bias split-brain removed, MIG-02 resolved (no migration needed)*
*Next: Wire distributed_hamsters.py to new planner (ARCH-04), then learned_thresholds.py, perception.py, reasoning.py pipeline review*
