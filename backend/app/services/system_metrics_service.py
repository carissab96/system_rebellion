"""
System Metrics Service

This service provides a single source of truth for system metrics
across all parts of the application, ensuring consistent values
are shown in the dashboard, auto-tuner, and system metrics pages.

This is now a thin wrapper around the modular metrics services.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Type
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Import the modular metrics services
from app.services.metrics.metrics_service import MetricsService


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
        Initialize the service with metrics collection services.
        """
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SystemMetricsService')
        self.last_metrics = None
        self.last_update_time = 0
        self.cache_ttl = 5  # Cache TTL in seconds
        
        # Initialize the metrics service
        self.metrics_service = MetricsService()
        
        self._initialized = True
        self.logger.info("SystemMetricsService initialized as singleton")
    
    async def _get_lock(self):
        """Get or create the async lock"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def get_metrics(self, force_refresh=False, db: AsyncSession = None) -> Dict[str, Any]:
        """
        Get current system metrics, using cached values if they're recent enough.
        This is now a thin wrapper around the modular metrics services.
        
        Args:
            force_refresh: If True, ignore the cache and collect fresh metrics
            db: Optional database session (kept for backward compatibility, not used)
            
        Returns:
            Dictionary containing system metrics with the following structure:
            {
                'timestamp': str,
                'cpu': {
                    'percent': float,
                    'temperature': Optional[float],
                    'cores': int,
                    'physical_cores': int
                },
                'memory': {
                    'percent': float,
                    'total': int,
                    'available': int,
                    'used': int,
                    'free': int
                },
                'disk': {
                    'percent': float,
                    'total': int,
                    'used': int,
                    'free': int
                },
                'network': {
                    'bytes_sent': int,
                    'bytes_recv': int,
                    'packets_sent': int,
                    'packets_recv': int,
                    'interfaces': Dict[str, Any]
                },
                'process_count': int,
                'additional': Dict[str, Any]
            }
        """
        current_time = time.time()
        
        # Use cached metrics if they're fresh enough and not forcing refresh
        if (not force_refresh and 
            self.last_metrics is not None and 
            current_time - self.last_update_time < self.cache_ttl):
            return self.last_metrics
            
        try:
            # Get metrics from the modular service
            metrics = await self.metrics_service.get_metrics(force_refresh)
            
            # Transform metrics to match frontend expectations
            cpu_metrics = metrics.get('cpu', {})
            memory_metrics = metrics.get('memory', {})
            disk_metrics = metrics.get('disk', {})
            network_metrics = metrics.get('network', {})
            
            transformed_metrics = {
                'type': 'system_metrics',
                'data': {
                    'timestamp': metrics.get('timestamp'),
                    'client_id': 'system',
                    'cpu_usage': cpu_metrics.get('total_percent', 0),
                    'cpu_frequency': cpu_metrics.get('frequency', {}).get('current', 0),
                    'cpu_temp': cpu_metrics.get('temperature', {}).get('current', 0),
                    'cpu_per_core': cpu_metrics.get('per_core_percent', []),
                    'memory_total': memory_metrics.get('total', 0),
                    'memory_available': memory_metrics.get('available', 0),
                    'memory_used': memory_metrics.get('used', 0),
                    'memory_free': memory_metrics.get('free', 0),
                    'memory_percent': memory_metrics.get('percent', 0),
                    'disk_total': disk_metrics.get('total', 0),
                    'disk_used': disk_metrics.get('used', 0),
                    'disk_free': disk_metrics.get('free', 0),
                    'disk_percent': disk_metrics.get('percent', 0),
                    'network_total': network_metrics.get('total_bytes', 0),
                    'network_used': network_metrics.get('bytes_sent', 0) + network_metrics.get('bytes_recv', 0),
                    'network_percent': network_metrics.get('utilization_percent', 0),
                    'process_count': metrics.get('process_count', 0),
                    'system_info': {
                        'cpu_model': cpu_metrics.get('model_name', 'CPU'),
                        'cores': cpu_metrics.get('cores', {}).get('physical', 0),
                        'logical_cores': cpu_metrics.get('cores', {}).get('logical', 0),
                        'hostname': metrics.get('hostname', ''),
                        'os': metrics.get('os', ''),
                        'architecture': metrics.get('architecture', '')
                    }
                }
            }
            
            # Update cache
            self.last_metrics = transformed_metrics
            self.last_update_time = time.time()
            
            return transformed_metrics
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            
            # If we have cached metrics, return those instead of failing
            if self.last_metrics is not None:
                self.logger.warning("Returning cached metrics due to collection error")
                return self.last_metrics
            
            # Otherwise, return a minimal set of metrics
            return self._get_empty_metrics(str(e))
    
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
            'cpu': {
                'percent': 0,
                'temperature': None,
                'cores': 0,
                'physical_cores': 0
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
                'free': 0
            },
            'network': {
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'interfaces': {}
            },
            'process_count': 0,
            'additional': {}
        }
        
        if error_msg:
            metrics['additional']['error'] = error_msg
            
        return metrics
    
    async def get_detailed_cpu_metrics(self) -> Dict[str, Any]:
        """
        Get detailed CPU metrics including per-core usage, top processes, and temperature.
        Now delegates to the CPU metrics service.
        
        Returns:
            Dictionary containing detailed CPU metrics
        """
        try:
            # Get CPU metrics from the service
            cpu_metrics = await self.metrics_service.get_cpu_metrics(force_refresh=True)
            
            # Transform to match the expected format
            return {
                'percent': cpu_metrics.get('total_percent', 0),
                'per_core_percent': cpu_metrics.get('per_core_percent', []),
                'frequency': cpu_metrics.get('frequency', {}),
                'temperature': cpu_metrics.get('temperature'),
                'top_processes': cpu_metrics.get('top_processes', []),
                'logical_cores': cpu_metrics.get('cores', {}).get('logical', 0),
                'physical_cores': cpu_metrics.get('cores', {}).get('physical', 0)
            }
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {str(e)}")
            return {
                'percent': 0,
                'per_core_percent': [],
                'frequency': {'current': None, 'min': None, 'max': None},
                'temperature': None,
                'top_processes': [],
                'logical_cores': 0,
                'physical_cores': 0
            }
    
    async def get_detailed_memory_metrics(self) -> Dict[str, Any]:
        """Get detailed memory metrics"""
        try:
            return await self.metrics_service.get_memory_metrics(force_refresh=True)
        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {str(e)}")
            return {}
    
    async def get_detailed_disk_metrics(self) -> Dict[str, Any]:
        """Get detailed disk metrics"""
        try:
            return await self.metrics_service.get_disk_metrics(force_refresh=True)
        except Exception as e:
            self.logger.error(f"Error getting disk metrics: {str(e)}")
            return {}
    
    async def get_detailed_network_metrics(self) -> Dict[str, Any]:
        """Get detailed network metrics"""
        try:
            return await self.metrics_service.get_network_metrics(force_refresh=True)
        except Exception as e:
            self.logger.error(f"Error getting network metrics: {str(e)}")
            return {}
    
    async def get_largest_directories(self, path='/', limit=10, max_depth=3) -> List[Dict[str, Any]]:
        """Get largest directories (expensive operation)"""
        try:
            return await self.metrics_service.get_largest_directories(path, limit, max_depth)
        except Exception as e:
            self.logger.error(f"Error getting largest directories: {str(e)}")
            return []
    
    async def get_connection_stats_by_process(self) -> Dict[str, Dict[str, Any]]:
        """Get network statistics grouped by process (expensive operation)"""
        try:
            return await self.metrics_service.get_connection_stats_by_process()
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