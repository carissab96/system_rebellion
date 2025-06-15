"""
System Metrics Service

This service provides a single source of truth for system metrics
across all parts of the application, ensuring consistent values
are shown in the dashboard, auto-tuner, and system metrics pages.

This now uses the ResourceMonitor for comprehensive metrics collection.
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Type
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Import the ResourceMonitor for comprehensive metrics collection
from app.optimization.resource_monitor import ResourceMonitor


class SystemMetricsService:
    """
    System-wide metrics service that provides a unified interface
    for accessing system metrics across the application.
    """
    
    _instance = None
    _lock = None
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemMetricsService, cls).__new__(cls)
            cls._instance._initialized = False
            return cls._instance
        
    def __init__(self):
        """
        Initialize the service with the ResourceMonitor for comprehensive metrics collection.
        """
        if self._initialized:
            return
                
        self.logger = logging.getLogger('SystemMetricsService')
        self.last_metrics = None
        self.last_update_time = 0
        self.cache_ttl = 5  # Cache TTL in seconds
            
        # Initialize the ResourceMonitor for comprehensive metrics
        self.resource_monitor = ResourceMonitor()
            
        self._initialized = True
        self.logger.info("SystemMetricsService initialized with ResourceMonitor as singleton")
        
    async def _get_lock(self):
        """Get or create the async lock"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
        
    async def get_metrics(self, force_refresh=False, db: AsyncSession = None) -> Dict[str, Any]:
        """
        Get current system metrics, using cached values if they're recent enough.
        This now uses the ResourceMonitor for comprehensive metrics collection.
            
        Args:
            force_refresh: If True, ignore the cache and collect fresh metrics
            db: Optional database session (kept for backward compatibility, not used)
                
        Returns:
            Dictionary containing comprehensive system metrics
            """
        current_time = time.time()
            
        # Use cached metrics if they're fresh enough and not forcing refresh
        if (not force_refresh and 
            self.last_metrics is not None and 
            current_time - self.last_update_time < self.cache_ttl):
            return self.last_metrics
                
        try:
            # Acquire lock to prevent multiple concurrent metric collections
            lock = await self._get_lock()
            async with lock:
                # Double-check if another thread already updated metrics while we were waiting
                current_time = time.time()  # Refresh time after waiting for lock
                if (not force_refresh and 
                    self.last_metrics is not None and 
                    current_time - self.last_update_time < self.cache_ttl):
                    return self.last_metrics
                    
                # Get metrics from the ResourceMonitor
                raw_metrics = await self.resource_monitor.collect_metrics()
                    
                # Extract and format metrics for frontend
                formatted_metrics = {
                    'timestamp': raw_metrics.get('timestamp', datetime.now().isoformat()),
                    'cpu_usage': raw_metrics.get('cpu_usage', 0),
                    'memory_usage': raw_metrics.get('memory_usage', 0),
                    'disk_usage': raw_metrics.get('disk_usage', 0),
                    'cpu': {
                            'percent': raw_metrics.get('cpu_usage', 0),
                            'temperature': raw_metrics.get('cpu_temperature', None),
                            'cores': raw_metrics.get('cpu_cores', {}).get('logical', 0),
                            'physical_cores': raw_metrics.get('cpu_cores', {}).get('physical', 0),
                            'frequency_mhz': raw_metrics.get('cpu_frequency', {}).get('current', 0)
                        },
                        'memory': {
                            'percent': raw_metrics.get('memory_usage', 0),
                            'total': raw_metrics.get('memory', {}).get('total', 0),
                            'available': raw_metrics.get('memory', {}).get('available', 0),
                            'used': raw_metrics.get('memory', {}).get('used', 0),
                            'free': raw_metrics.get('memory', {}).get('free', 0)
                        },
                        'disk': {
                            'percent': raw_metrics.get('disk_usage', 0),
                            'total': raw_metrics.get('disk', {}).get('total', 0),
                            'used': raw_metrics.get('disk', {}).get('used', 0),
                            'free': raw_metrics.get('disk', {}).get('free', 0),
                            'read_bytes': raw_metrics.get('disk', {}).get('read_bytes', 0),
                            'write_bytes': raw_metrics.get('disk', {}).get('write_bytes', 0)
                        },
                        'network': raw_metrics.get('network', {
                            'bytes_sent': 0,
                            'bytes_recv': 0,
                            'packets_sent': 0,
                            'packets_recv': 0,
                            'sent_rate': 0,
                            'recv_rate': 0,
                            'interfaces': {}
                        }),
                        'process_count': raw_metrics.get('process_count', 0),
                        'additional': raw_metrics.get('additional', {})
                    }
                
                # Update cache
                self.last_metrics = formatted_metrics
                self.last_update_time = current_time
                
                return formatted_metrics
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
                
            # If we have cached metrics, return those instead of failing
            if self.last_metrics is not None:
                self.logger.warning("Returning cached metrics due to collection error")
                return self.last_metrics
                
            # Otherwise, return empty metrics structure with error
            error_msg = f"Failed to collect metrics: {str(e)}"
            return self._get_empty_metrics(error_msg)
        
    def _safe_get_disk_value(self, metrics: Dict[str, Any], key: str) -> int:
            """Safely extract disk values from metrics"""
            try:
                partitions = metrics.get('disk', {}).get('partitions', [])
                if partitions and len(partitions) > 0:
                    return partitions[0].get(key, 0)
                return 0
            except Exception:
                return 0
    
    def _get_empty_metrics(self, error_msg: str = None) -> Dict[str, Any]:
        """Return empty metrics structure with optional error"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'cpu': {
                'percent': 0,
                'temperature': None,
                'cores': 0,
                'physical_cores': 0,
                'frequency_mhz': 0
            },
            'memory': {
                'percent': 0,
                'total': 0,
                'available': 0,
                'used': 0,
                'free': 0
            },
            'disk': {
                'percent': 0,
                'total': 0,
                'used': 0,
                'free': 0,
                'read_bytes': 0,
                'write_bytes': 0
            },
            'network': {
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'sent_rate': 0,
                'recv_rate': 0,
                'interfaces': {}
            },
            'process_count': 0,
            'additional': {
                'error': error_msg if error_msg else 'Unknown error'
            }
        }
        
        return metrics
        
    async def get_detailed_cpu_metrics(self) -> Dict[str, Any]:
        """
        Get detailed CPU metrics including per-core usage, top processes, and temperature.
        Now uses the ResourceMonitor for comprehensive metrics collection.
        
        Returns:
            Dictionary containing detailed CPU metrics
        """
        try:
            # Get metrics from the ResourceMonitor
            raw_metrics = await self.resource_monitor.collect_metrics()
                
            # Extract CPU-specific metrics
            return {
                'percent': raw_metrics.get('cpu_usage', 0),
                'per_core_percent': [core.get('usage', 0) for core in raw_metrics.get('cpu_cores_detailed', [])],
                'frequency': raw_metrics.get('cpu_frequency', {'current': 0, 'min': 0, 'max': 0}),
                'temperature': raw_metrics.get('cpu_temperature'),
                'top_processes': raw_metrics.get('top_processes', []),
                'logical_cores': raw_metrics.get('cpu_cores', {}).get('logical', 0),
                'physical_cores': raw_metrics.get('cpu_cores', {}).get('physical', 0),
                'cores': [{
                        'id': core.get('id', i),
                        'usage': core.get('usage', 0),
                        'frequency_mhz': raw_metrics.get('cpu_frequency', {}).get('current', 0)
                    } for i, core in enumerate(raw_metrics.get('cpu_cores_detailed', []))]
                }
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {str(e)}")
            return {
                'percent': 0,
                'per_core_percent': [],
                'frequency': {'current': 0, 'min': 0, 'max': 0},
                'temperature': None,
                'top_processes': [],
                'logical_cores': 0,
                'physical_cores': 0,
                'cores': []
            }
        
    async def get_detailed_memory_metrics(self) -> Dict[str, Any]:
        """Get detailed memory metrics from the ResourceMonitor"""
        try:
            # Get metrics from the ResourceMonitor
            raw_metrics = await self.resource_monitor.collect_metrics()
                
            # Extract memory-specific metrics
            return {
                    'percent': raw_metrics.get('memory_usage', 0),
                    'total': raw_metrics.get('memory', {}).get('total', 0),
                    'available': raw_metrics.get('memory', {}).get('available', 0),
                    'used': raw_metrics.get('memory', {}).get('used', 0),
                    'free': raw_metrics.get('memory', {}).get('free', 0),
                    'swap': raw_metrics.get('memory', {}).get('swap', {}),
                    'processes': raw_metrics.get('memory_processes', [])
                }
        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {str(e)}")
            return {
                    'percent': 0,
                    'total': 0,
                    'available': 0,
                    'used': 0,
                    'free': 0,
                    'swap': {},
                    'processes': []
                }
        
    async def get_detailed_disk_metrics(self) -> Dict[str, Any]:
        """Get detailed disk metrics from the ResourceMonitor"""
        try:
            # Get metrics from the ResourceMonitor
            raw_metrics = await self.resource_monitor.collect_metrics()
                
            # Extract disk-specific metrics
            return {
                    'percent': raw_metrics.get('disk_usage', 0),
                    'total': raw_metrics.get('disk', {}).get('total', 0),
                    'used': raw_metrics.get('disk', {}).get('used', 0),
                    'free': raw_metrics.get('disk', {}).get('free', 0),
                    'read_bytes': raw_metrics.get('disk', {}).get('read_bytes', 0),
                    'write_bytes': raw_metrics.get('disk', {}).get('write_bytes', 0),
                    'partitions': raw_metrics.get('disk_partitions', []),
                    'io_counters': raw_metrics.get('disk_io', {})
                }
        except Exception as e:
            self.logger.error(f"Error getting disk metrics: {str(e)}")
            return {
                    'percent': 0,
                    'total': 0,
                    'used': 0,
                    'free': 0,
                    'read_bytes': 0,
                    'write_bytes': 0,
                    'partitions': [],
                    'io_counters': {}
                }
        
    async def get_detailed_network_metrics(self) -> Dict[str, Any]:
        """Get detailed network metrics from the ResourceMonitor"""
        try:
            # Get metrics from the ResourceMonitor
            raw_metrics = await self.resource_monitor.collect_metrics()
                
            # Extract network-specific metrics
            network_data = raw_metrics.get('network', {})
            return {
                    'bytes_sent': network_data.get('bytes_sent', 0),
                    'bytes_recv': network_data.get('bytes_recv', 0),
                    'packets_sent': network_data.get('packets_sent', 0),
                    'packets_recv': network_data.get('packets_recv', 0),
                    'sent_rate': network_data.get('sent_rate', 0),
                    'recv_rate': network_data.get('recv_rate', 0),
                    'interfaces': network_data.get('interfaces', {}),
                    'connections': raw_metrics.get('network_connections', []),
                    'connection_stats': raw_metrics.get('connection_stats', {}),
                    'protocol_stats': raw_metrics.get('protocol_stats', {}),
                    'latency': raw_metrics.get('network_latency', {}),
                    'connection_quality': raw_metrics.get('connection_quality', {})
                }
        except Exception as e:
            self.logger.error(f"Error getting network metrics: {str(e)}")
            return {
                    'bytes_sent': 0,
                    'bytes_recv': 0,
                    'packets_sent': 0,
                    'packets_recv': 0,
                    'sent_rate': 0,
                    'recv_rate': 0,
                    'interfaces': {},
                    'connections': [],
                    'connection_stats': {},
                    'protocol_stats': {},
                    'latency': {},
                    'connection_quality': {}
                }
        
    async def get_largest_directories(self, path='/', limit=10, max_depth=3) -> List[Dict[str, Any]]:
        """Get largest directories using the ResourceMonitor (expensive operation)"""
        try:
            # Get disk usage analysis from the ResourceMonitor
            return await self.resource_monitor.get_directory_sizes(path, limit, max_depth)
        except Exception as e:
            self.logger.error(f"Error getting largest directories: {str(e)}")
            return []
        
    async def get_connection_stats_by_process(self) -> Dict[str, Dict[str, Any]]:
        """Get network statistics grouped by process using ResourceMonitor (expensive operation)"""
        try:
            # Get network connection stats by process from the ResourceMonitor
            return await self.resource_monitor.get_process_network_stats()
        except Exception as e:
            self.logger.error(f"Error getting connection stats by process: {str(e)}")
            return {}
        
    @classmethod
    async def get_instance(cls, db: AsyncSession = None) -> 'SystemMetricsService':
        """
            Get the singleton instance of the service
            
            Args:
                db: Optional database session (kept for backward compatibility, not used)
                
            Returns:
                SystemMetricsService: The singleton instance
            """
        if cls._instance is None:
            # Create a temporary instance to get the lock
            temp_instance = cls()
            lock = await temp_instance._get_lock()
            async with lock:
                if cls._instance is None:
                    cls._instance = cls()
            return cls._instance