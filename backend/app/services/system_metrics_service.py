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
from app.services.metrics.metrics_service import MetricsService as MetricsOrchestrator

class SystemMetricsService:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemMetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, metrics_service_class: Type[MetricsOrchestrator] = None):
        """
        Initialize the service with a metrics service class.
        
        Args:
            metrics_service_class: The metrics service class to use. If None, will use MetricsOrchestrator.
        """
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SystemMetricsService')
        self.metrics_service_class = metrics_service_class or MetricsOrchestrator
        self.last_metrics = None
        self.last_update_time = 0
        self.cache_ttl = 5  # Cache TTL in seconds
        
        # Initialize the metrics service
        self.metrics_service = self.metrics_service_class()
        
        self._initialized = True
        self.logger.info("SystemMetricsService initialized as singleton (using modular metrics services)")
    
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
            
            # Transform to match the expected format
            transformed_metrics = {
                'timestamp': metrics.get('timestamp', datetime.now().isoformat()),
                'cpu': {
                    'percent': metrics.get('cpu_usage', 0),
                    'temperature': metrics.get('cpu', {}).get('temperature'),
                    'cores': len(metrics.get('cpu', {}).get('per_core_percent', [])),
                    'physical_cores': metrics.get('cpu', {}).get('cores', {}).get('physical', 0)
                },
                'memory': {
                    'percent': metrics.get('memory_usage', 0),
                    'total': metrics.get('memory', {}).get('total', 0),
                    'available': metrics.get('memory', {}).get('available', 0),
                    'used': metrics.get('memory', {}).get('used', 0),
                    'free': metrics.get('memory', {}).get('free', 0)
                },
                'disk': {
                    'percent': metrics.get('disk_usage', 0),
                    'total': metrics.get('disk', {}).get('partitions', [{}])[0].get('total', 0) if metrics.get('disk', {}).get('partitions') else 0,
                    'used': metrics.get('disk', {}).get('partitions', [{}])[0].get('used', 0) if metrics.get('disk', {}).get('partitions') else 0,
                    'free': metrics.get('disk', {}).get('partitions', [{}])[0].get('free', 0) if metrics.get('disk', {}).get('partitions') else 0
                },
                'network': {
                    'bytes_sent': metrics.get('network', {}).get('io_stats', {}).get('bytes_sent', 0),
                    'bytes_recv': metrics.get('network', {}).get('io_stats', {}).get('bytes_recv', 0),
                    'packets_sent': metrics.get('network', {}).get('io_stats', {}).get('packets_sent', 0),
                    'packets_recv': metrics.get('network', {}).get('io_stats', {}).get('packets_recv', 0),
                    'interfaces': {}
                },
                'process_count': metrics.get('process_count', 0),
                'additional': metrics.get('additional', {})
            }
            
            # Store in our local cache for backward compatibility
            self.last_metrics = transformed_metrics
            self.last_update_time = time.time()
            
            return transformed_metrics
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            
            # If we have cached metrics, return those instead of failing
            if self.last_metrics is not None:
                return self.last_metrics
            
            # Otherwise, return a minimal set of metrics
            return {
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
                'additional': {
                    'error': str(e)
                }
            }
    
    async def _get_detailed_cpu_metrics(self) -> Dict[str, Any]:
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
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = SystemMetricsService()
        return cls._instance
