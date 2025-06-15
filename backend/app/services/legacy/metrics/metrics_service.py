"""
Metrics Service

This service is the main orchestrator for collecting system metrics.
It combines data from specialized metric services for CPU, Memory, Disk, and Network.
"""

import asyncio
import logging
import time
import psutil
import socket
import platform
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.metrics.cpu_metrics_service import CPUMetricsService
from app.services.metrics.memory_metrics_service import MemoryMetricsService
from app.services.metrics.disk_metrics_service import DiskMetricsService
from app.services.metrics.network_metrics_service import NetworkMetricsService

class MetricsService:
    """Main service for collecting and combining system metrics"""
    
    _instance = None
    _lock = None
    
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
    
    async def _get_lock(self):
        """Get or create the async lock"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
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
        lock = await self._get_lock()
        async with lock:
            # Double-check if another thread already updated metrics while we were waiting
            current_time = time.time()  # Refresh time after waiting for lock
            if (not force_refresh and 
                self.last_metrics is not None and 
                current_time - self.last_update_time < self.cache_ttl):
                return self.last_metrics
                
            # Collect fresh metrics
            try:
                # Collect metrics from each specialized service concurrently
                cpu_task = asyncio.create_task(self._get_cpu_metrics())
                memory_task = asyncio.create_task(self._get_memory_metrics())
                disk_task = asyncio.create_task(self._get_disk_metrics())
                network_task = asyncio.create_task(self.network_service.get_metrics())
                
                # Wait for all metrics to be collected
                cpu_metrics, memory_metrics, disk_metrics, network_metrics = await asyncio.gather(
                    cpu_task, memory_task, disk_task, network_task
                )
                
                # Get system info
                system_info = {
                    'hostname': socket.gethostname(),
                    'os': platform.system(),
                    'architecture': platform.machine(),
                    'platform': platform.platform()
                }
                
                # Build combined metrics dictionary with real system data
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system_info': system_info,
                    
                    # CPU metrics directly from cpu_metrics
                    'cpu_usage': cpu_metrics.get('total_percent'),
                    'cpu': cpu_metrics,
                    
                    # Memory metrics directly from memory_metrics
                    'memory_usage': memory_metrics.get('percent'),
                    'memory': memory_metrics,
                    
                    # Disk metrics directly from disk_metrics
                    'disk_usage': disk_metrics.get('percent'),
                    'disk': disk_metrics,
                    
                    # Network metrics directly from network_metrics
                    'network_usage': network_metrics.get('io_stats', {}).get('total_rate'),
                    'network': network_metrics,
                    
                    # Process count from actual process list
                    'process_count': len(psutil.pids())
                }
                
                # Update cache
                self.last_metrics = metrics
                self.last_update_time = time.time()
                
                return metrics
                
            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {str(e)}")
                
                # If we have cached metrics, return those instead of failing
                if self.last_metrics is not None:
                    self.logger.warning("Returning cached metrics due to collection error")
                    return self.last_metrics
                
                # Otherwise, return None for all metrics
                return {
                    'timestamp': datetime.now().isoformat(),
                    'system_info': {
                        'hostname': socket.gethostname(),
                        'os': platform.system(),
                        'architecture': platform.machine(),
                        'platform': platform.platform()
                    },
                    'cpu_usage': None,
                    'cpu': {},
                    'memory_usage': None,
                    'memory': {},
                    'disk_usage': None,
                    'disk': {},
                    'network_usage': None,
                    'network': {},
                    'process_count': None,
                    'error': str(e)
                }
    
    async def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Async wrapper for CPU metrics"""
        try:
            return self.cpu_service.get_metrics()
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
            return {}
    
    async def _get_memory_metrics(self) -> Dict[str, Any]:
        """Async wrapper for memory metrics"""
        try:
            return self.memory_service.get_metrics()
        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {e}")
            return {}
    
    async def _get_disk_metrics(self) -> Dict[str, Any]:
        """Async wrapper for disk metrics"""
        try:
            return self.disk_service.get_metrics()
        except Exception as e:
            self.logger.error(f"Error getting disk metrics: {e}")
            return {}
    
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
        try:
            return await asyncio.create_task(
                asyncio.to_thread(self.disk_service.get_largest_directories, path, limit, max_depth)
            )
        except Exception as e:
            self.logger.error(f"Error getting largest directories: {e}")
            return []
    
    async def get_connection_stats_by_process(self) -> Dict[str, Dict[str, Any]]:
        """Get network statistics grouped by process (expensive operation)"""
        try:
            return await asyncio.create_task(
                asyncio.to_thread(self.network_service.get_connection_stats_by_process)
            )
        except Exception as e:
            self.logger.error(f"Error getting connection stats by process: {e}")
            return {}
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
