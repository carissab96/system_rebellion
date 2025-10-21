# Auto-generated from resource_monitor.py using resource_monitor_ast.py
# DO NOT EDIT MANUALLY - Run 'python backend/resource_monitor_ast.py' to regenerate

from typing import Literal

# Metric key constants
CPU_USAGE = 'cpu_usage'
MEMORY_USAGE = 'memory_usage'
DISK_USAGE = 'disk_usage'
THROTTLED_NETWORK_METRICS = 'throttled_network_metrics'
BASIC_NETWORK_STATS = 'basic_network_stats'
NETWORK_CONNECTIONS = 'network_connections'
NETWORK_INTERFACES = 'network_interfaces'
PROTOCOL_BREAKDOWN = 'protocol_breakdown'
CONNECTION_QUALITY = 'connection_quality'
DNS_METRICS = 'dns_metrics'
INTERNET_METRICS = 'internet_metrics'
DEFAULT_GATEWAY = 'default_gateway'
ADDITIONAL_METRICS = 'additional_metrics'
CPU_TEMPERATURE = 'cpu_temperature'
LOAD_AVERAGE = 'load_average'
SYSTEM_UPTIME = 'system_uptime'
STATUS = 'status'

# Type alias for all valid metric keys
MetricKey = Literal['cpu_usage', 'memory_usage', 'disk_usage', 'throttled_network_metrics', 'basic_network_stats', 'network_connections', 'network_interfaces', 'protocol_breakdown', 'connection_quality', 'dns_metrics', 'internet_metrics', 'default_gateway', 'additional_metrics', 'cpu_temperature', 'load_average', 'system_uptime', 'status']

# List of all metric keys
ALL_METRIC_KEYS = [
    'cpu_usage',
    'memory_usage',
    'disk_usage',
    'throttled_network_metrics',
    'basic_network_stats',
    'network_connections',
    'network_interfaces',
    'protocol_breakdown',
    'connection_quality',
    'dns_metrics',
    'internet_metrics',
    'default_gateway',
    'additional_metrics',
    'cpu_temperature',
    'load_average',
    'system_uptime',
    'status',
]

# Metadata about each metric
METRIC_METADATA = {
    'cpu_usage': {
        'key': 'cpu_usage',
        'function_name': '_get_cpu_usage',
        'is_async': True,
    },
    'memory_usage': {
        'key': 'memory_usage',
        'function_name': '_get_memory_usage',
        'is_async': False,
    },
    'disk_usage': {
        'key': 'disk_usage',
        'function_name': '_get_disk_usage',
        'is_async': False,
    },
    'throttled_network_metrics': {
        'key': 'throttled_network_metrics',
        'function_name': '_get_throttled_network_metrics',
        'is_async': True,
    },
    'basic_network_stats': {
        'key': 'basic_network_stats',
        'function_name': '_get_basic_network_stats',
        'is_async': False,
    },
    'network_connections': {
        'key': 'network_connections',
        'function_name': '_get_network_connections',
        'is_async': False,
    },
    'network_interfaces': {
        'key': 'network_interfaces',
        'function_name': '_get_network_interfaces',
        'is_async': False,
    },
    'protocol_breakdown': {
        'key': 'protocol_breakdown',
        'function_name': '_get_protocol_breakdown',
        'is_async': False,
    },
    'connection_quality': {
        'key': 'connection_quality',
        'function_name': '_get_connection_quality',
        'is_async': True,
    },
    'dns_metrics': {
        'key': 'dns_metrics',
        'function_name': '_get_dns_metrics',
        'is_async': True,
    },
    'internet_metrics': {
        'key': 'internet_metrics',
        'function_name': '_get_internet_metrics',
        'is_async': True,
    },
    'default_gateway': {
        'key': 'default_gateway',
        'function_name': '_get_default_gateway',
        'is_async': True,
    },
    'additional_metrics': {
        'key': 'additional_metrics',
        'function_name': '_get_additional_metrics',
        'is_async': True,
    },
    'cpu_temperature': {
        'key': 'cpu_temperature',
        'function_name': '_get_cpu_temperature',
        'is_async': False,
    },
    'load_average': {
        'key': 'load_average',
        'function_name': '_get_load_average',
        'is_async': False,
    },
    'system_uptime': {
        'key': 'system_uptime',
        'function_name': '_get_system_uptime',
        'is_async': False,
    },
    'status': {
        'key': 'status',
        'function_name': 'get_status',
        'is_async': True,
    },
}
