"""
CPU Metrics Transformer

Transforms raw CPU metrics into the format expected by the frontend.
"""

from typing import Dict, Any

def transform_cpu_metrics(raw_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform raw CPU metrics into the format expected by the frontend.
    
    Args:
        raw_metrics: Raw metrics from CPUMetricsService
        
    Returns:
        Transformed metrics matching frontend expectations
    """
    if not raw_metrics:
        return {}
        
    # Transform core data
    cores = []
    if 'per_core_percent' in raw_metrics:
        cores = [
            {
                'id': i,
                'usage_percent': usage
            }
            for i, usage in enumerate(raw_metrics['per_core_percent'])
        ]
    
    # Transform temperature data
    temp = raw_metrics.get('temperature')
    temperature = {
        'current': temp if temp is not None else 0,
        'min': 0,  # These could be configured based on CPU model
        'max': 100,
        'critical': 90,
        'throttle_threshold': 80,
        'unit': 'C'
    }
    
    # Transform frequency data
    freq = raw_metrics.get('frequency', {})
    frequency_mhz = freq.get('current', 0)
    
    # Get core counts
    core_info = raw_metrics.get('cores', {})
    physical_cores = core_info.get('physical', 1)
    logical_cores = core_info.get('logical', 1)
    
    # Build the transformed metrics
    transformed = {
        'type': 'cpu',
        'data': {
            'usage_percent': raw_metrics.get('total_percent', 0),
            'physical_cores': physical_cores,
            'logical_cores': logical_cores,
            'frequency_mhz': frequency_mhz,
            'temperature': temperature['current'],
            'cores': [c['usage_percent'] for c in cores],
            'top_processes': [{
                'pid': p['pid'],
                'name': p['name'],
                'cpu_percent': p['cpu_percent'],
                'memory_percent': p.get('memory_percent', 0)
            } for p in raw_metrics.get('top_processes', [])]
        }
    }
    
    return transformed
