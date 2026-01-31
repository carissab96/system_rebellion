# Learned Thresholds System

## Overview

This system replaces hardcoded `ACTION_MAP` category lists with **true autonomous learning**:

- **Thresholds adapt to YOUR system** - Not "85% is critical" but "On THIS system, 88% during business hours becomes critical in 15 minutes"
- **Actions scored by actual outcomes** - Not "restart_service is aggressive" but "restart_service has 94% success when metrics look like THIS"
- **Proactive prediction** - Not "memory is high, react" but "memory will be high in 30 minutes, act now gently to prevent emergency later"

## Architecture

### 1. LearnedThresholds (`learned_thresholds.py`)

**Purpose:** System-specific thresholds that learn from outcomes.

**How it learns:**
- **False alarm** → Threshold was too low, increase it
- **Acted too late** → Threshold was too high, decrease it
- **Successful intervention** → Threshold appropriate, increase confidence

**Example:**
```python
# Start with defaults
warning_threshold = 80.0  # confidence: 0.3

# After 10 false alarms at 82%
warning_threshold = 85.0  # confidence: 0.5

# After 20 successful interventions at 85%
warning_threshold = 85.0  # confidence: 0.8 (confirmed)
```

**Contextual adjustment:**
```python
# Base threshold: 85%
# But at 2am with low growth rate: 88% (learned it's safe)
# But during deployments: 82% (learned it escalates faster)
```

**Database:** `threshold_learning_records` table

### 2. ActionEffectivenessModel (`action_effectiveness.py`)

**Purpose:** Learn which actions work in which metric patterns.

**How it learns:**
- Records every action taken with pre/post metrics
- Creates "pattern fingerprint" of metric state
- Queries similar patterns to score actions

**Example:**
```python
# Pattern: "sev:80|memory_usage:90|cpu_usage:70|growth:high"

# Historical outcomes for restart_service in this pattern:
# - 15 attempts, 14 successes, 1 failure
# - Success rate: 93%
# - Avg improvement: 35%
# - Score: 0.85 (high confidence)

# Historical outcomes for clear_cache in this pattern:
# - 8 attempts, 3 successes, 5 failures
# - Success rate: 37%
# - Avg improvement: 8%
# - Score: 0.32 (low confidence)
```

**Database:** `action_outcome_records` table

### 3. PredictiveEngine (`predictive_engine.py`)

**Purpose:** Forecast future state and recommend proactive action.

**How it works:**

**Linear extrapolation:**
```python
# Recent history: [70%, 72%, 74%, 76%, 78%]
# Growth rate: ~2% per minute
# Forecast 30min: 78% * (1.02)^30 = 141% → capped at 100%
```

**Pattern matching:**
```python
# Current: Tuesday 2pm, memory at 72%
# Query: Similar situations (Tuesday 2pm ±2hr, memory 72% ±5%)
# Found: 8 patterns
# Average outcome: Hit 88% in 35 minutes
# Forecast: 88% in 35 minutes (confidence: 0.7)
```

**Hybrid forecast:**
```python
# Blend linear (40%) + pattern (60%)
# Confidence based on pattern consistency
```

**Proactive recommendation:**
```python
if forecast_30min >= critical_threshold and confidence >= 0.6:
    return ProactiveRecommendation(
        reasoning="Memory at 72% now, will hit critical in 35min. Act now gently."
        recommended_severity=0.6  # Medium severity for proactive
    )
```

**Database:** `metric_pattern_history` table

## Database Schema

### threshold_learning_records
```sql
- system_id: Which system (multi-tenant support)
- metric_name: 'memory_usage', 'cpu_usage', etc.
- metric_value: Value when threshold crossed
- threshold_level: 'warning', 'critical', 'emergency'
- action_taken: Action performed (or NULL if monitored)
- outcome_success: Did it work?
- was_false_alarm: Resolved without intervention
- should_have_acted_sooner: Became critical too fast
- system_state: Other metrics at the time (JSON)
- context: Time of day, day of week, etc. (JSON)
```

### action_outcome_records
```sql
- agent_name: 'meth_snail', 'hamsters', etc.
- action: 'restart_service', 'clear_cache', etc.
- pre_metrics: Metrics before action (JSON)
- post_metrics: Metrics after action (JSON)
- metric_pattern_fingerprint: Hash for similarity matching
- success: Did it improve things?
- improvement: % improvement in primary metric
- severity_score: How severe was the situation
```

### metric_pattern_history
```sql
- system_id: Which system
- metric_name: 'memory_usage', etc.
- starting_value: Value at T0
- value_15min_later: Value at T+15min
- value_30min_later: Value at T+30min
- value_1hr_later: Value at T+60min
- context: Time of day, system load, etc. (JSON)
- context_fingerprint: Hash for pattern matching
```

## Integration with Action Selection

**Before (hardcoded):**
```python
ACTION_MAP = {
    'memory_leak': ['restart_service', 'kill_memory_hog', ...],
    'memory_pressure': ['clear_cache', 'optimize_memory_allocation', ...],
}

# Select from category list
viable_actions = ACTION_MAP.get(root_cause.category, ['monitor'])
```

**After (learned):**
```python
# 1. Assess severity using learned thresholds
severity = await learned_thresholds.assess(metrics, context)

# 2. Check if should act proactively
proactive = await predictive_engine.should_act_proactively(forecasts)

# 3. Score ALL actions using learned effectiveness
action_scores = await action_effectiveness.score_all_actions(
    current_metrics, severity, primary_metric
)

# 4. Select best action
chosen = action_scores[0]  # Highest score

# 5. Record outcome for learning
await action_effectiveness.record_outcome(
    action, pre_metrics, post_metrics, severity, success
)
```

## Cold Start Problem

**Q:** What happens when there's no learning data yet?

**A:** Graceful degradation to heuristics:

1. **Thresholds:** Start with conservative defaults (warning: 80%, critical: 90%)
2. **Actions:** Heuristic scoring based on severity and action type
3. **Forecasting:** Linear extrapolation only (no pattern matching)

As data accumulates:
- Thresholds adjust to system-specific values
- Action scoring becomes evidence-based
- Forecasting gains pattern-matching confidence

**Confidence tracking:**
```python
threshold_confidence = min(1.0, sample_size / 50.0)
# 0 samples = 0.3 confidence (defaults)
# 25 samples = 0.5 confidence (learning)
# 50+ samples = 1.0 confidence (established)
```

## Learning Feedback Loops

### Threshold Learning Loop
```
1. Threshold crossed → Action taken
2. Outcome observed (success/failure, false alarm, too late)
3. Record stored in threshold_learning_records
4. Next time threshold is queried:
   - Analyze recent records
   - Adjust threshold based on outcomes
   - Update confidence
```

### Action Effectiveness Loop
```
1. Action selected based on current scores
2. Pre-metrics captured
3. Action executed
4. Post-metrics captured
5. Success/improvement calculated
6. Record stored in action_outcome_records
7. Next time similar situation occurs:
   - Query similar patterns
   - Score actions by historical success
   - Higher confidence with more data
```

### Predictive Learning Loop
```
1. Current metrics recorded with context
2. Pattern stored in metric_pattern_history
3. 15min later: Update with actual value
4. 30min later: Update with actual value
5. 1hr later: Update with actual value
6. Next time similar situation occurs:
   - Query similar patterns
   - Forecast based on what happened before
   - Confidence based on pattern consistency
```

## Example Scenario

**Initial state (Day 1):**
```
Memory: 82%
Learned threshold: None (using default 80%)
Action scores: Heuristic-based
Forecast: Linear extrapolation only
Decision: clear_cache (heuristic score: 0.7)
Outcome: Success, 15% improvement
```

**After 30 days:**
```
Memory: 82%
Learned threshold: 85% (confidence: 0.8)
  - 5 false alarms at 82% → threshold raised
  - 15 successful interventions at 85% → confirmed
Action scores: Evidence-based
  - clear_cache: 0.65 (8 attempts, 62% success)
  - restart_service: 0.85 (12 attempts, 91% success)
Forecast: Hybrid (linear + 8 pattern matches)
  - Will hit 88% in 25 minutes (confidence: 0.75)
Decision: restart_service (evidence-based score: 0.85)
  OR: Proactive clear_cache now to prevent hitting 88%
```

## Metrics and Monitoring

**Learning status:**
```python
summary = await learned_thresholds.get_learning_summary('memory_usage')
# {
#   'total_records': 45,
#   'false_alarms': 5,
#   'acted_too_late': 2,
#   'successful_interventions': 38,
#   'current_thresholds': {'warning': 85.0, 'critical': 92.0},
#   'confidence': {'warning': 0.75, 'critical': 0.68},
#   'learning_status': 'active'
# }
```

**Action statistics:**
```python
stats = await action_effectiveness.get_action_statistics('restart_service')
# {
#   'total_uses': 23,
#   'success_rate': 0.87,
#   'avg_improvement': 0.32,
#   'status': 'active'
# }
```

**Forecast accuracy:**
```python
accuracy = await predictive_engine.get_forecast_accuracy('memory_usage')
# {
#   'avg_error_15min': 3.2,  # Average error in percentage points
#   'sample_size': 67,
#   'accuracy': 'good'
# }
```

## Migration Instructions

**1. Run migration on Dell:**
```bash
cd /home/carissa/Documents/system_rebellion/backend
alembic upgrade head
```

**2. Verify tables created:**
```sql
\dt threshold_learning_records
\dt action_outcome_records
\dt metric_pattern_history
```

**3. Integration will be in next commit** (action_selection.py update)

## Next Steps

1. ✅ Database models created
2. ✅ Migration file ready
3. ✅ LearnedThresholds implemented
4. ✅ ActionEffectivenessModel implemented
5. ✅ PredictiveEngine implemented
6. ⏳ Integrate with action_selection.py
7. ⏳ Test with real metrics
8. ⏳ Monitor learning progress
9. ⏳ Apply pattern to Hamsters and QSP

## Key Differences from Old System

| Old System | New System |
|------------|------------|
| Hardcoded ACTION_MAP | Dynamic action scoring |
| Category-based filtering | Metric pattern matching |
| Universal thresholds | System-specific learned thresholds |
| Reactive only | Proactive + reactive |
| No learning from outcomes | Continuous learning loops |
| "memory_leak" → list of actions | "metrics look like THIS" → scored actions |
| Same for all systems | Adapts to each deployment |

## Philosophy

**"Autonomous learning agents" means:**
- Thresholds learned from YOUR system's behavior
- Actions scored by actual outcomes, not assumptions
- Predictions based on historical patterns
- Continuous improvement from every decision
- System-specific adaptation, not universal rules

**This is what devs expect when they hear "AI agents that learn your system."**
