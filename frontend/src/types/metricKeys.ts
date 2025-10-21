// Auto-generated from resource_monitor.py using resource_monitor_ast.py
// DO NOT EDIT MANUALLY - Run 'python backend/resource_monitor_ast.py' to regenerate

export const METRIC_KEYS = {
  CPU_USAGE: 'cpu_usage',
  MEMORY_USAGE: 'memory_usage',
  DISK_USAGE: 'disk_usage',
  THROTTLED_NETWORK_METRICS: 'throttled_network_metrics',
  BASIC_NETWORK_STATS: 'basic_network_stats',
  NETWORK_CONNECTIONS: 'network_connections',
  NETWORK_INTERFACES: 'network_interfaces',
  PROTOCOL_BREAKDOWN: 'protocol_breakdown',
  CONNECTION_QUALITY: 'connection_quality',
  DNS_METRICS: 'dns_metrics',
  INTERNET_METRICS: 'internet_metrics',
  DEFAULT_GATEWAY: 'default_gateway',
  ADDITIONAL_METRICS: 'additional_metrics',
  CPU_TEMPERATURE: 'cpu_temperature',
  LOAD_AVERAGE: 'load_average',
  SYSTEM_UPTIME: 'system_uptime',
  STATUS: 'status',
} as const;

export type MetricKey = typeof METRIC_KEYS[keyof typeof METRIC_KEYS];

export interface MetricTypes {
  'cpu_usage': number;
  'memory_usage': number;
  'disk_usage': number;
  'throttled_network_metrics': any;
  'basic_network_stats': any;
  'network_connections': any;
  'network_interfaces': any;
  'protocol_breakdown': any;
  'connection_quality': any;
  'dns_metrics': any;
  'internet_metrics': any;
  'default_gateway': any;
  'additional_metrics': any;
  'cpu_temperature': any;
  'load_average': any;
  'system_uptime': any;
  'status': any;
}

export const METRIC_METADATA = {
  'cpu_usage': {
    key: 'cpu_usage',
    functionName: '_get_cpu_usage',
    isAsync: true,
    type: 'number',
  },
  'memory_usage': {
    key: 'memory_usage',
    functionName: '_get_memory_usage',
    isAsync: false,
    type: 'number',
  },
  'disk_usage': {
    key: 'disk_usage',
    functionName: '_get_disk_usage',
    isAsync: false,
    type: 'number',
  },
  'throttled_network_metrics': {
    key: 'throttled_network_metrics',
    functionName: '_get_throttled_network_metrics',
    isAsync: true,
    type: 'any',
  },
  'basic_network_stats': {
    key: 'basic_network_stats',
    functionName: '_get_basic_network_stats',
    isAsync: false,
    type: 'any',
  },
  'network_connections': {
    key: 'network_connections',
    functionName: '_get_network_connections',
    isAsync: false,
    type: 'any',
  },
  'network_interfaces': {
    key: 'network_interfaces',
    functionName: '_get_network_interfaces',
    isAsync: false,
    type: 'any',
  },
  'protocol_breakdown': {
    key: 'protocol_breakdown',
    functionName: '_get_protocol_breakdown',
    isAsync: false,
    type: 'any',
  },
  'connection_quality': {
    key: 'connection_quality',
    functionName: '_get_connection_quality',
    isAsync: true,
    type: 'any',
  },
  'dns_metrics': {
    key: 'dns_metrics',
    functionName: '_get_dns_metrics',
    isAsync: true,
    type: 'any',
  },
  'internet_metrics': {
    key: 'internet_metrics',
    functionName: '_get_internet_metrics',
    isAsync: true,
    type: 'any',
  },
  'default_gateway': {
    key: 'default_gateway',
    functionName: '_get_default_gateway',
    isAsync: true,
    type: 'any',
  },
  'additional_metrics': {
    key: 'additional_metrics',
    functionName: '_get_additional_metrics',
    isAsync: true,
    type: 'any',
  },
  'cpu_temperature': {
    key: 'cpu_temperature',
    functionName: '_get_cpu_temperature',
    isAsync: false,
    type: 'any',
  },
  'load_average': {
    key: 'load_average',
    functionName: '_get_load_average',
    isAsync: false,
    type: 'any',
  },
  'system_uptime': {
    key: 'system_uptime',
    functionName: '_get_system_uptime',
    isAsync: false,
    type: 'any',
  },
  'status': {
    key: 'status',
    functionName: 'get_status',
    isAsync: true,
    type: 'any',
  },
} as const;
