# Component Field Analysis Report

## Summary

### CPU Metrics

**Total fields accessed:** 17

**Main component expects:**
- `cpu`
- `cpu_core_count`
- `cpu_frequency`
- `cpu_model`
- `cpu_temperature`
- `cpu_thread_count`
- `cpu_usage`

**Subcomponents:**
- **CPUOverviewTab**: cores, frequency_mhz, model_name, overall_usage, process_count ... +3 more
- **CPUThermalTab**: length, reduce

**Expected Structure:**
```json
{
  "cores": {
    "type": "object",
    "children": [
      "length",
      "map",
      "slice"
    ]
  },
  "cpu": {
    "type": "value"
  },
  "cpu_core_count": {
    "type": "value"
  },
  "cpu_frequency": {
    "type": "value"
  },
  "cpu_model": {
    "type": "value"
  },
  "cpu_temperature": {
    "type": "value"
  },
  "cpu_thread_count": {
    "type": "value"
  },
  "cpu_usage": {
    "type": "value"
  },
  "frequency_mhz": {
    "type": "value"
  },
  "length": {
    "type": "value"
  },
  "model_name": {
    "type": "value"
  },
  "overall_usage": {
    "type": "object",
    "children": [
      "toFixed"
    ]
  },
  "process_count": {
    "type": "value"
  },
  "reduce": {
    "type": "value"
  },
  "temperature": {
    "type": "object",
    "children": [
      "critical",
      "current",
      "max",
      "min",
      "throttle_threshold",
      "unit"
    ]
  },
  "thread_count": {
    "type": "value"
  },
  "top_processes": {
    "type": "object",
    "children": [
      "length",
      "slice"
    ]
  }
}
```

**WebSocket Transformer Code:**
```python
    # Transform CPU metrics
    if "cpu" in metrics:
        cpu_data = metrics["cpu"]
        
        transformed["cpu_fields"] = {
            "cpu": cpu_data.get("cpu", 
                      cpu_data.get("cpu", 0)),
            "cpu_core_count": cpu_data.get("cpu_core_count", 
                      cpu_data.get("core_count", 0)),
            "cpu_frequency": cpu_data.get("cpu_frequency", 
                      cpu_data.get("frequency", 0)),
            "cpu_model": cpu_data.get("cpu_model", 
                      cpu_data.get("model", 0)),
            "cpu_temperature": cpu_data.get("cpu_temperature", 
                      cpu_data.get("temperature", 0)),
            "cpu_thread_count": cpu_data.get("cpu_thread_count", 
                      cpu_data.get("thread_count", 0)),
            "cpu_usage": cpu_data.get("cpu_usage", 
                      cpu_data.get("usage", 0)),
            "frequency_mhz": cpu_data.get("frequency_mhz", 
                      cpu_data.get("frequency_mhz", 0)),
            "length": cpu_data.get("length", 
                      cpu_data.get("length", 0)),
            "model_name": cpu_data.get("model_name", 
                      cpu_data.get("model_name", 0)),
            "process_count": cpu_data.get("process_count", 
                      cpu_data.get("process_count", 0)),
            "reduce": cpu_data.get("reduce", 
                      cpu_data.get("reduce", 0)),
            "thread_count": cpu_data.get("thread_count", 
                      cpu_data.get("thread_count", 0)),
        }
        
        # Nested cores object
        transformed["cores"] = {
            "length": cpu_data.get("cores", {}).get("length", []),
            "map": cpu_data.get("cores", {}).get("map", []),
            "slice": cpu_data.get("cores", {}).get("slice", []),
        }
        # Nested overall_usage object
        transformed["overall_usage"] = {
            "toFixed": cpu_data.get("overall_usage", {}).get("toFixed", []),
        }
        # Nested temperature object
        transformed["temperature"] = {
            "critical": cpu_data.get("temperature", {}).get("critical", []),
            "current": cpu_data.get("temperature", {}).get("current", []),
            "max": cpu_data.get("temperature", {}).get("max", []),
            "min": cpu_data.get("temperature", {}).get("min", []),
            "throttle_threshold": cpu_data.get("temperature", {}).get("throttle_threshold", []),
            "unit": cpu_data.get("temperature", {}).get("unit", []),
        }
        # Nested top_processes object
        transformed["top_processes"] = {
            "length": cpu_data.get("top_processes", {}).get("length", []),
            "slice": cpu_data.get("top_processes", {}).get("slice", []),
        }
```

---

### Network Metrics

**Total fields accessed:** 1

**Main component expects:**
- `network`

**Subcomponents:**

**Expected Structure:**
```json
{
  "network": {
    "type": "value"
  }
}
```

**WebSocket Transformer Code:**
```python
    # Transform Network metrics
    if "network" in metrics:
        network_data = metrics["network"]
        
        transformed["network_fields"] = {
            "network": network_data.get("network", 
                      network_data.get("network", 0)),
        }
        
```

---

