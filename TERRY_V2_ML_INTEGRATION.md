# Terry v2: ML Integration with Original Blueprint

## Original Blueprint (5 Layers)

```
Perception → Reasoning → Action Selection → Execution → Learning
```

## How ML Enhances Each Layer

### 1. PERCEPTION LAYER (Enhanced)

**Original:** `perception.py`
- Gathers full metrics
- Queries historical patterns
- Retrieves recent actions

**ML Enhancement:**
```python
class TerryPerception:
    def __init__(self, db_session, agent_state):
        self.db = db_session
        self.agent_state = agent_state
        
        # ADD: ML components for perception
        self.anomaly_detector = AdvancedPatternDetector()
        self.pattern_matcher = PatternMatcher()
    
    async def perceive(self, coordination_request):
        # Original: Get full metrics
        full_metrics = await self._get_full_metrics(coordination_request)
        
        # Original: Query historical patterns
        similar_situations = await self._find_similar_situations(...)
        
        # ML ENHANCEMENT: Detect if this is an anomaly
        is_anomaly = self.anomaly_detector.detect_anomalies(
            np.array([full_metrics['cpu_usage'], 
                     full_metrics['memory_usage']]).reshape(-1, 1)
        )
        
        # ML ENHANCEMENT: Semantic matching as fallback
        if not similar_situations:
            similar_situations = await self.pattern_matcher.match_pattern(
                current_state=full_metrics
            )
        
        # Return enhanced context
        return PerceptionContext(
            full_metrics=full_metrics,
            similar_situations=similar_situations,
            is_anomaly=bool(is_anomaly[-1]),  # ML-detected anomaly
            ...
        )
```

**What ML Adds:**
- Anomaly detection (is this truly unusual?)
- Semantic matching (fallback when exact matches fail)

---

### 2. REASONING LAYER (Enhanced)

**Original:** `reasoning.py`
- Root cause analysis (domain knowledge)
- Historical learning (what worked before)
- Decision synthesis

**ML Enhancement:**
```python
class TerryReasoning:
    def __init__(self, db_session):
        self.db = db_session
        
        # ADD: ML components for reasoning
        self.pattern_validator = PatternValidator()
        self.pattern_learner = PatternLearner()
        self.workload_predictor = WorkloadPredictor()
    
    async def reason(self, context):
        # Original: Root cause analysis (domain knowledge)
        root_cause = await self._analyze_root_cause(context)
        
        # ML ENHANCEMENT: Validate this pattern statistically
        pattern_validation = await self.pattern_validator.validate_pattern(
            pattern={
                'resource_type': context.resource_type,
                'root_cause': root_cause.cause,
                'current_value': context.current_value
            },
            metrics=context.full_metrics
        )
        
        # Only proceed if pattern is validated (85% confidence, 5+ samples)
        if not pattern_validation['is_valid']:
            # Not enough data - use VIC-20's recommendation
            return self._fallback_to_vic20(context)
        
        # ML ENHANCEMENT: Learn temporal patterns
        temporal_patterns = self.pattern_learner.learn_temporal_patterns(
            user_id='system',
            context_vector=np.array([context.current_value, ...])
        )
        
        # ML ENHANCEMENT: Predict future state
        self.workload_predictor.add_observation(
            user_id='system',
            timestamp=utc_now(),
            activity=f"{context.resource_type}_stress",
            resources={'cpu': context.full_metrics['cpu_usage'] / 100.0}
        )
        predictions = self.workload_predictor.predict_workload('system')
        
        # Original: Historical learning
        learning = await self._apply_historical_learning(context, root_cause)
        
        # ML ENHANCEMENT: Adjust confidence based on validation
        learning.confidence_boost += pattern_validation['confidence'] * 0.2
        
        # Original: Decision synthesis
        decision = await self._synthesize_decision(root_cause, learning, context)
        
        # ML ENHANCEMENT: Adjust based on predictions
        if predictions.get('predictions', {}).get('cpu', []):
            future_cpu = predictions['predictions']['cpu']
            if max(future_cpu) > 0.9:
                decision.reasoning += " ML predicts worsening conditions."
                decision.action_confidence += 0.1  # More urgent
        
        return decision
```

**What ML Adds:**
- Pattern validation (requires statistical confidence)
- Temporal clustering (finds recurring patterns)
- Workload prediction (proactive decisions)
- Confidence adjustment (based on ML validation)

---

### 3. ACTION SELECTION LAYER (Enhanced)

**Original:** `action_selection.py`
- Maps root causes to actions
- Scores actions by historical success
- Applies personality bias

**ML Enhancement:**
```python
class TerryActionSelection:
    def __init__(self):
        self.logger = logger
        
        # ADD: ML for action optimization
        self.resource_optimizer = ResourceOptimizer()
    
    async def select_action(self, reasoning_result, context):
        # Original: Get viable actions for root cause
        viable_actions = self.ACTION_MAP.get(reasoning_result.root_cause, [])
        
        # Original: Score actions by historical success
        action_scores = self._score_actions(viable_actions, reasoning_result)
        
        # ML ENHANCEMENT: Get optimization suggestions
        ml_suggestions = self.resource_optimizer.suggest_optimizations(
            patterns=reasoning_result.temporal_patterns,
            current_usage={
                'cpu': context.full_metrics['cpu_usage'] / 100.0,
                'memory': context.full_metrics['memory_usage'] / 100.0
            }
        )
        
        # ML ENHANCEMENT: Boost actions that ML recommends
        for suggestion in ml_suggestions:
            suggested_action = suggestion.get('action')
            if suggested_action in action_scores:
                action_scores[suggested_action] *= (1 + suggestion['confidence'])
        
        # Original: Apply personality bias
        if 'emergency_cache_clear' in action_scores:
            action_scores['emergency_cache_clear'] *= 1.2
        
        # Original: Select best action
        best_action = max(action_scores.items(), key=lambda x: x[1])
        
        return ActionDecision(
            action=best_action[0],
            confidence=min(0.95, best_action[1]),
            ...
        )
```

**What ML Adds:**
- Resource optimization suggestions
- ML-based action scoring
- Confidence adjustment based on ML recommendations

---

### 4. EXECUTION LAYER (Unchanged)

**Original:** Execute action via SystemActions
- No ML enhancement needed here
- Execution is execution

---

### 5. LEARNING LAYER (Enhanced)

**Original:** `learning.py`
- Stores situation → action → outcome
- Calculates improvement
- Updates confidence

**ML Enhancement:**
```python
class TerryLearning:
    def __init__(self, db_session, agent_state):
        self.db = db_session
        self.agent_state = agent_state
        
        # ADD: ML for learning validation
        self.pattern_validator = PatternValidator()
        self.pattern_learner = PatternLearner()
    
    async def learn(self, context, reasoning_result, decision, execution_result):
        # Original: Generate fingerprints
        fingerprints = SituationFingerprint.generate(...)
        
        # Original: Calculate improvement
        improvement = self._calculate_improvement(
            execution_result['metrics_before'],
            execution_result['metrics_after'],
            context.resource_type
        )
        
        # Original: Determine success
        overall_success = execution_result['success'] and improvement < 0
        
        # ML ENHANCEMENT: Add to pattern learner
        context_vector = np.array([
            context.current_value,
            context.full_metrics['cpu_usage'],
            context.full_metrics['memory_usage']
        ])
        
        temporal_patterns = self.pattern_learner.learn_temporal_patterns(
            user_id='system',
            context_vector=context_vector
        )
        
        # Original: Create learning record
        record = LearningRecord(
            fingerprint_l1=fingerprints['level_1'],
            fingerprint_l2=fingerprints['level_2'],
            fingerprint_l3=fingerprints['level_3'],
            action=decision.action,
            success=overall_success,
            improvement=improvement,
            ...
        )
        
        # ML ENHANCEMENT: Validate pattern before storing
        pattern_validation = await self.pattern_validator.validate_pattern(
            pattern={
                'fingerprint': fingerprints['level_3'],
                'action': decision.action,
                'success': overall_success
            },
            metrics=context.full_metrics
        )
        
        # Only store if pattern is valid OR if it's a failure (learn from failures)
        if pattern_validation['is_valid'] or not overall_success:
            await self._store_learning(record)
        
        # Original: Update agent state
        await self._update_agent_state(record, decision)
        
        # Original: Share with The Stick
        await self._share_with_stick(record)
        
        return record
```

**What ML Adds:**
- Pattern validation before storage (prevents noise)
- Temporal pattern learning (recurring patterns)
- ML-validated confidence updates

---

## Complete Integration Flow

```
1. PERCEPTION (Enhanced)
   ├─ Get full metrics (original)
   ├─ Query historical patterns (original)
   ├─ Detect anomalies (ML)
   └─ Semantic matching fallback (ML)

2. REASONING (Enhanced)
   ├─ Root cause analysis (original domain knowledge)
   ├─ Validate pattern statistically (ML)
   ├─ Learn temporal patterns (ML)
   ├─ Predict future state (ML)
   ├─ Historical learning (original)
   └─ Decision synthesis with ML confidence (enhanced)

3. ACTION SELECTION (Enhanced)
   ├─ Map root cause to actions (original)
   ├─ Score by historical success (original)
   ├─ Get ML optimization suggestions (ML)
   ├─ Apply personality bias (original)
   └─ Select best action (enhanced)

4. EXECUTION
   └─ Execute via SystemActions (unchanged)

5. LEARNING (Enhanced)
   ├─ Generate fingerprints (original)
   ├─ Calculate improvement (original)
   ├─ Add to pattern learner (ML)
   ├─ Validate before storage (ML)
   ├─ Store learning record (original)
   └─ Update agent state (original)
```

---

## Dependencies to Install

```bash
# On Dell (where backend runs)
pip install scikit-learn==1.3.0
pip install tensorflow==2.15.0
pip install sentence-transformers==2.2.2
pip install numpy==1.24.3
```

**Why these versions:**
- scikit-learn 1.3.0: DBSCAN, IsolationForest, StandardScaler
- tensorflow 2.15.0: LSTM for sequence prediction
- sentence-transformers 2.2.2: Semantic similarity matching
- numpy 1.24.3: Array operations (already installed)

---

## Files to Modify

### 1. Uncomment ML Imports

**Files:**
- `backend/app/ml/context/pattern_learning.py`
- `backend/app/ml/context/advanced_patterns.py`
- `backend/app/ml/pattern_recognition/pattern_matcher.py`

**Change:**
```python
# FROM:
#from sklearn.cluster import DBSCAN
#from sklearn.preprocessing import StandardScaler
#import tensorflow as tf

# TO:
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
```

### 2. Add Missing Utility

**File:** `backend/app/ml/context/pattern_learning.py`

**Add at top:**
```python
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)
```

### 3. Update Terry's Reasoning

**File:** `backend/app/ai_agents/meth_snail/reasoning.py`

**Option A: Replace with ML version**
- Use `ml_reasoning.py` instead of `reasoning.py`

**Option B: Enhance existing**
- Add ML components to existing `reasoning.py`
- Keep domain knowledge, add ML validation

**Recommendation: Option B** (keep domain knowledge, add ML)

---

## Implementation Steps

1. **Install dependencies on Dell**
   ```bash
   pip install scikit-learn tensorflow sentence-transformers
   ```

2. **Uncomment ML imports**
   - pattern_learning.py
   - advanced_patterns.py
   - pattern_matcher.py

3. **Add utc_now() utility**
   - pattern_learning.py
   - advanced_patterns.py

4. **Test ML components**
   ```python
   # Test script
   from app.ml.context.pattern_learning import PatternLearner
   learner = PatternLearner()
   # Verify it initializes without errors
   ```

5. **Integrate into reasoning.py**
   - Add ML components to __init__
   - Enhance each method with ML validation
   - Keep original domain logic

6. **Test with real metrics**
   - Run backend
   - Trigger coordination
   - Verify ML validation works

---

## Benefits of This Integration

### Keeps Original Blueprint
- ✅ Perception still gathers context
- ✅ Reasoning still does root cause analysis
- ✅ Action selection still maps causes to actions
- ✅ Learning still stores outcomes

### Adds ML Intelligence
- ✅ Statistical validation (85% confidence, 5+ samples)
- ✅ Anomaly detection (signal vs noise)
- ✅ Temporal clustering (recurring patterns)
- ✅ Predictive capabilities (proactive decisions)
- ✅ Semantic matching (fallback similarity)

### Best of Both Worlds
- Domain knowledge (our understanding of systems)
- Statistical rigor (ML validation)
- Predictive capabilities (LSTM forecasting)
- Confidence scoring (know when to trust)

---

## Next Steps

1. Install dependencies on Dell
2. Uncomment ML imports
3. Test ML components work
4. Integrate into reasoning.py (enhance, don't replace)
5. Test with real coordination requests
6. Verify ML validation improves decisions

**The blueprint stays. ML makes it smarter.**
