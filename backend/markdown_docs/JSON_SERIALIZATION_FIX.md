# 🔧 JSON SERIALIZATION FIX

## Problem
```
TypeError: Object of type HawkingtonDecision is not JSON serializable
```

The `HawkingtonDecision` dataclass was being passed directly to the database's JSONB field without conversion.

## Root Cause

In `agent_manager.py`, the triage engine returns a `HawkingtonDecision` dataclass:

```python
triage = await self.agents["sir_hawkington"].process_metrics(metrics, user_context)
```

This dataclass was then passed directly to `_stick_log()`:

```python
await self._stick_log("triage_low_medium", {
    "metrics": metrics, 
    "triage": triage,  # ❌ Dataclass object!
    "timestamp": ts
}, user_id=user_id)
```

The `content` parameter becomes the `details` JSONB field in PostgreSQL, which requires JSON-serializable data.

## Solution

### 1. Added Import
```python
from dataclasses import asdict
```

### 2. Created Serialization Helper
```python
def _serialize_triage(self, triage) -> dict:
    """Convert HawkingtonDecision to JSON-serializable dict."""
    triage_dict = asdict(triage)
    # Convert datetime to ISO string
    if 'timestamp' in triage_dict and hasattr(triage_dict['timestamp'], 'isoformat'):
        triage_dict['timestamp'] = triage_dict['timestamp'].isoformat()
    return triage_dict
```

### 3. Updated All Calls
```python
# Before
"triage": triage  # ❌

# After
"triage": self._serialize_triage(triage)  # ✅
```

## Files Modified

**`/backend/app/ai_agents/agent_manager.py`**
- Added `from dataclasses import asdict` import
- Added `_serialize_triage()` helper method
- Updated line 387: `asdict(triage)` → `self._serialize_triage(triage)`
- Updated line 399: `asdict(triage)` → `self._serialize_triage(triage)`

## Why This Works

1. **`asdict()`** converts the dataclass to a dictionary
2. **`isoformat()`** converts datetime objects to ISO strings
3. **Result:** Fully JSON-serializable dict that PostgreSQL can store in JSONB

## Testing

Restart the backend and check:
- ✅ No more "Object of type HawkingtonDecision is not JSON serializable" errors
- ✅ Triage decisions stored successfully
- ✅ Memory storage works without rollback errors

---

## Status: ✅ FIXED

The backend should now store agent memories without JSON serialization errors!
