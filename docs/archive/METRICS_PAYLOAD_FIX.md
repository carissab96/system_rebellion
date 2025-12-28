# Metrics Payload Fix - The Missing Data Problem

## ROOT CAUSE IDENTIFIED

Individual metrics services return data in this structure:
```python
{
    'timestamp': '2025-12-22T...',
    'type': 'cpu',  # or 'memory', 'disk', 'network'
    'data': {
        'usage_percent': 45.2,
        'physical_cores': 8,
        'logical_cores': 16,
        'top_processes': [...],
        # ... all the actual metrics
    }
}
```

But `SimplifiedMetricsService.get_metrics()` tries to access them like:
```python
cpu_data.get('usage_percent')  # WRONG - returns None
```

Should be:
```python
cpu_data.get('data', {}).get('usage_percent')  # CORRECT
```

## THE FIX

**File:** `backend/app/services/metrics/simplified_metrics_service.py`  
**Lines:** 133-155, 192-207

### Current (BROKEN):
```python
async def get_cpu_metrics(self, force_refresh=False) -> Dict[str, Any]:
    cpu_service = await SimplifiedCPUService.get_instance()
    result = await self._safe_get_metrics(cpu_service, self.cpu_circuit_breaker, "CPU")
    return result.get('data', {})  # Returns the nested 'data' object

# Then later:
cpu_data = await self.get_cpu_metrics()  # This IS the 'data' object
raw_metrics = {
    'cpu_usage': cpu_data.get('usage_percent'),  # CORRECT - works fine
    'cpu': cpu_data,  # CORRECT - full data object
}
```

Wait... actually this looks correct. Let me re-examine.

## RE-ANALYSIS

Looking at line 136:
```python
result = await self._safe_get_metrics(cpu_service, self.cpu_circuit_breaker, "CPU")
return result.get('data', {})
```

So `get_cpu_metrics()` already unwraps the 'data' field and returns just the metrics.

Then line 192-201:
```python
cpu_data = await self.get_cpu_metrics()  # Already unwrapped
raw_metrics = {
    'cpu_usage': cpu_data.get('usage_percent'),  # Should work
    'cpu': cpu_data,  # Full unwrapped data
}
```

This should work. Let me check if the services are actually returning the structure I think they are...

## ACTUAL PROBLEM

The services return:
```python
{
    'timestamp': '...',
    'type': 'cpu',
    'data': { ... }
}
```

`_safe_get_metrics()` returns the full result.

`get_cpu_metrics()` does `result.get('data', {})` to unwrap.

So `cpu_data` should be the unwrapped data object.

**This structure is correct.**

## SO WHERE'S THE PROBLEM?

The payload IS being sent. Let me check:
1. Is the frontend receiving it?
2. Is the frontend parsing it correctly?
3. Is Redux storing it correctly?

The backend sends:
```python
{
    "type": "system_update",
    "timestamp": "...",
    "metrics": {  # Full enhanced metrics from triage
        'timestamp': '...',
        'cpu_usage': 45.2,
        'memory_usage': 62.1,
        'disk_usage': 78.3,
        'cpu': { ... full CPU data ... },
        'memory': { ... full memory data ... },
        'disk': { ... full disk data ... },
        'network': { ... full network data ... },
        'triage_decision': { ... },
        # etc
    },
    "agents": { ... },
    "recent_insights": [...],
    "recent_events": [...]
}
```

## HYPOTHESIS

The backend is sending the full payload correctly. The problem might be:

1. **Frontend not parsing the nested structure**
2. **Redux not storing the full metrics object**
3. **Components only accessing top-level fields**

Need to check frontend Redux slice and how it handles the `system_update` message.
