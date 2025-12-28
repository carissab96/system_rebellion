# WebSocket Payload Analysis - Where's the Data?

## Current Payload Structure (Line 754-761)

```python
out_msg = {
    "type": "system_update",
    "timestamp": _now_iso(),
    "metrics": metrics,  # Full metrics from SimplifiedMetricsService
    "agents": agent_insights,  # Agent memory banks and triage data
    "recent_insights": recent_insights,  # Last 10 inter-agent communications
    "recent_events": recent_events,  # Last 10 personality events
}
```

## What `metrics` Contains (from SimplifiedMetricsService.get_metrics())

**Location:** `simplified_metrics_service.py:190-225`

```python
raw_metrics = {
    'timestamp': utc_now().isoformat(),
    'cpu_usage': cpu_data.get('usage_percent'),
    'memory_usage': memory_data.get('percent'),
    'disk_usage': disk_data.get('percent'),
    'network_sent_rate': network_data.get('sent_rate'),
    'network_recv_rate': network_data.get('recv_rate'),
    'cpu': cpu_data,           # FULL CPU DATA
    'memory': memory_data,     # FULL MEMORY DATA
    'disk': disk_data,         # FULL DISK DATA
    'network': network_data,   # FULL NETWORK DATA
    'process_count': len(cpu_data.get('top_processes', [])),
    'system_info': {
        'hostname': network_data.get('hostname'),
        'physical_cores': cpu_data.get('physical_cores'),
        'logical_cores': cpu_data.get('logical_cores'),
        'total_memory': memory_data.get('total'),
        'total_disk': disk_data.get('total')
    }
}

# Then enhanced with triage data
enhanced_metrics = await process_metrics_through_triage(raw_metrics, ...)
```

## What's in Each Service's Data?

### CPU Data (SimplifiedCPUService)
- `usage_percent`
- `physical_cores`
- `logical_cores`
- `per_core_usage`
- `top_processes` (list of process details)
- `load_average`
- `context_switches`
- `interrupts`

### Memory Data (SimplifiedMemoryService)
- `percent` (usage)
- `total`
- `available`
- `used`
- `free`
- `active`
- `inactive`
- `buffers`
- `cached`
- `shared`
- `swap_total`
- `swap_used`
- `swap_free`
- `swap_percent`

### Disk Data (SimplifiedDiskService)
- `percent` (usage)
- `total`
- `used`
- `free`
- `read_count`
- `write_count`
- `read_bytes`
- `write_bytes`
- `read_time`
- `write_time`
- `partitions` (list)

### Network Data (SimplifiedNetworkService)
- `hostname`
- `sent_rate`
- `recv_rate`
- `bytes_sent`
- `bytes_recv`
- `packets_sent`
- `packets_recv`
- `errin`
- `errout`
- `dropin`
- `dropout`
- `connections` (list)

## What `agent_insights` Contains

**Built from multiple sources:**

1. **Agent Memory Banks** (from PostgreSQL `central_memory_bank`)
   - Latest memory for each agent
   - Event type, details, priority
   - Timestamp, metadata

2. **Distributed Agent Status** (from `agent.get_agent_status()`)
   - Current personality metrics
   - Shell spin count, monocle state, beer level, etc.
   - Real-time agent state

3. **Triage Data** (from Sir Hawkington)
   - Triage decision
   - Disposition
   - Confidence
   - Routing information

## THE PROBLEM

The payload structure exists and is comprehensive. But let me check what the individual service files actually return:

### Need to verify:
1. Are the individual services (`SimplifiedCPUService`, etc.) returning ALL the data?
2. Is the triage engine preserving all the metrics when it enhances them?
3. Is the frontend receiving and parsing this correctly?

## Next Steps

1. Check what `SimplifiedCPUService.get_metrics()` actually returns
2. Check what `SimplifiedMemoryService.get_metrics()` actually returns
3. Check what `SimplifiedDiskService.get_metrics()` actually returns
4. Check what `SimplifiedNetworkService.get_metrics()` actually returns
5. Verify triage engine doesn't strip data
6. Check frontend Redux parsing

The structure is there. The question is: **Is the data actually being collected and sent?**
