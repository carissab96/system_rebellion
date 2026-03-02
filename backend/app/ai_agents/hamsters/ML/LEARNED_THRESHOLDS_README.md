# Hamsters' Learned Thresholds System

## Overview

The Hamsters' learned threshold system adapts storage intervention thresholds based on observed outcomes. Instead of using hardcoded values for when disk usage or fragmentation becomes problematic, the system learns from experience.

## Components

### 1. LearnedThresholds (`learned_thresholds.py`)

Manages adaptive thresholds for storage metrics:
- **Disk usage** (warning: 80%, critical: 90% default)
- **Fragmentation** (warning: 20%, critical: 40% default)
- **Inode usage** (warning: 80%, critical: 90% default)

**Learning Logic:**
- **False alarms** (triggered unnecessarily) → raise threshold (less sensitive)
- **Missed actions** (should have acted sooner) → lower threshold (more sensitive)
- **Successful interventions** → reinforce current threshold

**Collective Learning:**
Thresholds are collective across Steve, Bob, and Carl. The threshold for "disk usage is a problem" doesn't change based on which hamster notices it. Individual hamster tendencies affect execution (Bob's aggressive approach vs Steve's cautious one), not detection.

### 2. ActionEffectivenessModel (`action_effectiveness.py`)

Learns which storage fix works best for which pattern:
- `cleanup_temp_files` vs `cleanup_logs` vs `defrag` vs `emergency_measures`
- Pattern fingerprints: `disk_gradual_growth`, `disk_sudden_spike`, `fragmentation_high`, etc.

**Scoring:**
- 60% weighted success rate (recent outcomes matter more)
- 40% improvement magnitude (how much did it help?)
- Confidence based on sample size (10+ samples = full confidence)

**Collective Learning:**
Action effectiveness is collective unless hamster identity is already captured in execution data. If hamster identity is tracked, the model can learn that "Bob's aggressive defrag outperforms Steve's cautious approach above 30% fragmentation" without explicitly being told to track it.

## Integration with The Stick

Both systems integrate with The Stick's validation layer:

### Threshold Validation
```python
await learned_thresholds.request_stick_validation(
    metric_name='disk_usage',
    threshold_level='warning',
    learned_value=85.0,
    default_value=80.0
)
```

**The Stick validates:**
1. Sample size >= min_threshold_sample_size (5 initial, 10 mature)
2. Shift magnitude <= max_threshold_shift_magnitude (0.15)
3. Direction consistency with trigger reason (false alarms → UP, missed actions → DOWN)

### Action Effectiveness Validation
```python
await action_effectiveness.request_stick_validation(
    action='defrag',
    metric_pattern='fragmentation_high_warning'
)
```

**The Stick validates:**
1. Sample size >= min_action_sample_size (3 initial, 5 mature)
2. Score volatility <= max_action_score_volatility (0.3)
3. Score consistency with raw data (catches model drift)

## Database Schema

Reuses Terry's tables with `agent_name='hamsters'`:
- `threshold_learning_records` - Stores threshold adjustment outcomes
- `action_outcome_records` - Stores action execution outcomes

No new migrations needed - tables are agent-agnostic.

## Usage Example

```python
from app.ai_agents.hamsters.ML.learned_thresholds import LearnedThresholds
from app.ai_agents.hamsters.ML.action_effectiveness import ActionEffectivenessModel

# Initialize
learned_thresholds = LearnedThresholds(db, system_id="production")
action_effectiveness = ActionEffectivenessModel(db, system_id="production")

# Get learned threshold
disk_warning = await learned_thresholds.get_threshold('disk_usage', 'warning')

# Score actions for a pattern
action_scores = await action_effectiveness.score_all_actions('disk_gradual_growth_warning')
best_action = action_scores[0]  # Highest score

# Record outcome
await learned_thresholds.record_outcome(
    metric_name='disk_usage',
    metric_value=85.0,
    threshold_level='warning',
    was_successful=True,
    was_false_alarm=False
)

await action_effectiveness.record_outcome(
    action='cleanup_temp_files',
    pre_metrics={'disk_usage_percent': 85.0},
    post_metrics={'disk_usage_percent': 75.0},
    severity='warning',
    success=True
)

# Request validation from The Stick
await learned_thresholds.request_stick_validation(
    metric_name='disk_usage',
    threshold_level='warning',
    learned_value=85.0,
    default_value=80.0,
    db_getter=get_async_db
)
```

## Key Differences from Terry

| Aspect | Terry (Meth Snail) | Hamsters |
|--------|-------------------|----------|
| **Metrics** | CPU, memory, network | Disk, fragmentation, inodes |
| **Actions** | restart_service, scale_up | cleanup_temp, cleanup_logs, defrag |
| **Personality** | Energy drinks, jitter | Beer, duct tape, consensus |
| **Complexity** | Individual agent | Telepathic consensus (Steve/Bob/Carl) |
| **Defaults** | CPU/memory specific | Storage specific (industry standard) |

## Personality vs Learning

**NOT in ML features:**
- Duct tape usage (tracked in personality layer only)
- Bob chaos factor (tracked in audit trail metadata only)
- Beer consumption (tracked in personality layer only)

**Reason:** Personality metrics muddy the learning signal during cold start. The effectiveness model needs clean data about what action worked for what pattern. After 30+ days of data, if genuine correlations emerge, they can be added as features.

**Audit Trail Metadata:**
```python
'execution_metadata': {
    'lead_hamster': 'bob',
    'consensus_reached': True,
    'consensus_dissent': ['steve'],
    'beer_consumed': 4,
    'duct_tape_used': 2.5
}
```

This allows The Stick and VIC-20 to notice patterns ("Bob-led fixes have higher variance") without contaminating the learning model.

## Cold Start Strategy

1. **Start with conservative defaults** (industry standard)
2. **Collect data for 30 days** before major adjustments
3. **Validate every adjustment** with The Stick
4. **Gradually increase confidence** as sample size grows
5. **Never auto-promote** to autonomous without explicit policy approval

## Validation Timing

Same as Terry:
- **Real-time validation** after every threshold adjustment
- **Real-time validation** after every action execution
- **Two-hour sweep** as fallback (already implemented in The Stick)

Consistency across specialists matters. One pattern. One expectation. One audit trail format.

## Session Management

**CRITICAL:** The `request_stick_validation()` methods use `db_getter` to obtain The Stick's database session. This prevents nested session creation, which causes deadlocks.

```python
# CORRECT: Use db_getter to get The Stick's session
async for db in db_getter():
    stick_learning = StickLearning(db, user_id)
    # ... validation logic

# WRONG: Don't create nested sessions
# This will deadlock!
```

This pattern was fixed in Terry's implementation and must be followed here.
