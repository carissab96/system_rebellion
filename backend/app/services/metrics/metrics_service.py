"""
Metrics Service

This service is the main orchestrator for collecting system metrics.
It combines data from specialized metric services for CPU, Memory, Disk, and Network.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.metrics.cpu_metrics_service import CPUMetricsService
from app.services.metrics.memory_metrics_service import MemoryMetricsService
from app.services.metrics.disk_metrics_service import DiskMetricsService
from app.services.metrics.network_metrics_service import NetworkMetricsService

class MetricsService:
    """Main service for collecting and combining system metrics"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('MetricsService')
        self.last_metrics = None
        self.last_update_time = 0
        self.cache_ttl = 2  # seconds - how long to cache metrics before refreshing
        
        # Initialize specialized metric services
        self.cpu_service = CPUMetricsService()
        self.memory_service = MemoryMetricsService()
        self.disk_service = DiskMetricsService()
        self.network_service = NetworkMetricsService()
        
        self._initialized = True
        self.logger.info("MetricsService initialized as singleton")
    
    async def get_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """
        Get current system metrics, using cached values if they're recent enough.
        
        Args:
            force_refresh: If True, ignore the cache and collect fresh metrics
            
        Returns:
            Dictionary containing system metrics
        """
        current_time = time.time()
        
        # Use cached metrics if they're fresh enough and not forcing refresh
        if (not force_refresh and 
            self.last_metrics is not None and 
            current_time - self.last_update_time < self.cache_ttl):
            return self.last_metrics
        
        # Acquire lock to prevent multiple concurrent metric collections
        async with self._lock:
            # Double-check if another thread already updated metrics while we were waiting
            if (not force_refresh and 
                self.last_metrics is not None and 
                current_time - self.last_update_time < self.cache_ttl):
                return self.last_metrics
                
            # Collect fresh metrics
            try:
                # Collect metrics from each specialized service
                cpu_metrics = self.cpu_service.get_metrics()
                memory_metrics = self.memory_service.get_metrics()
                disk_metrics = self.disk_service.get_metrics()
                network_metrics = await self.network_service.get_metrics()
                
                # Build combined metrics dictionary
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    
                    # Basic metrics for backward compatibility
                    'cpu_usage': cpu_metrics['total_percent'],
                    'memory_usage': memory_metrics['percent'],
                    'disk_usage': disk_metrics['partitions'][0]['percent'] if disk_metrics['partitions'] else 0,
                    'network_usage': network_metrics['io_stats']['sent_rate'] + network_metrics['io_stats']['recv_rate'],
                    'process_count': len(cpu_metrics['top_processes']),
                    
                    # Detailed metrics
                    'cpu': cpu_metrics,
                    'memory': memory_metrics,
                    'disk': disk_metrics,
                    'network': network_metrics
                }
                
                # Update cache
                self.last_metrics = metrics
                self.last_update_time = time.time()
                
                return metrics
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {str(e)}")
                
                # If we have cached metrics, return those instead of failing
                if self.last_metrics is not None:
                    return self.last_metrics
                
                # Otherwise, return a minimal set of metrics
                return {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'disk_usage': 0,
                    'network_usage': 0,
                    'process_count': 0,
                    'error': str(e)
                }
    
    async def get_cpu_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get CPU metrics only"""
        metrics = await self.get_metrics(force_refresh)
        return metrics.get('cpu', {})
    
    async def get_memory_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get memory metrics only"""
        metrics = await self.get_metrics(force_refresh)
        return metrics.get('memory', {})
    
    async def get_disk_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get disk metrics only"""
        metrics = await self.get_metrics(force_refresh)
        return metrics.get('disk', {})
    
    async def get_network_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get network metrics only"""
        metrics = await self.get_metrics(force_refresh)
        return metrics.get('network', {})
    
    async def get_largest_directories(self, path='/', limit=10, max_depth=3) -> List[Dict[str, Any]]:
        """Get largest directories (expensive operation)"""
        return self.disk_service.get_largest_directories(path, limit, max_depth)
    
    async def get_connection_stats_by_process(self) -> Dict[str, Dict[str, Any]]:
        """Get network statistics grouped by process (expensive operation)"""
        return self.network_service.get_connection_stats_by_process()
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
