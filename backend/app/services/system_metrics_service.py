"""
Centralized System Metrics Service

This service provides a single source of truth for system metrics
across all parts of the application, ensuring consistent values
are shown in the dashboard, auto-tuner, and system metrics pages.
"""

import psutil
import logging
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
import time

class SystemMetricsService:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemMetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SystemMetricsService')
        self.last_metrics = None
        self.last_update_time = 0
        self.cache_ttl = 2  # seconds - how long to cache metrics before refreshing
        self._initialized = True
        self.logger.info("SystemMetricsService initialized as singleton")
    
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
                # Use a consistent interval for CPU measurements
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network_io = psutil.net_io_counters()
                
                # Get process count
                try:
                    process_count = len(list(psutil.process_iter()))
                except Exception as e:
                    self.logger.error(f"Error counting processes: {str(e)}")
                    process_count = 0
                
                # Get CPU temperature if available
                try:
                    temps = psutil.sensors_temperatures()
                    if temps and 'coretemp' in temps:
                        cpu_temp = temps['coretemp'][0].current
                    else:
                        cpu_temp = None
                except Exception:
                    cpu_temp = None
                
                # Get load average
                try:
                    load_avg = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
                except Exception:
                    load_avg = [0, 0, 0]
                
                # Count Python processes
                try:
                    python_processes = len([p for p in list(psutil.process_iter(['name'])) 
                                           if 'python' in p.info['name'].lower()])
                except Exception:
                    python_processes = 0
                
                # Calculate network rate (bytes per second)
                # Store previous network values for rate calculation
                current_time = time.time()
                current_bytes_total = network_io.bytes_sent + network_io.bytes_recv
                
                # Initialize network rate
                network_rate_mbps = 0
                
                # If we have previous values, calculate the rate
                if hasattr(self, '_prev_network_time') and hasattr(self, '_prev_network_bytes'):
                    time_diff = current_time - self._prev_network_time
                    if time_diff > 0:  # Avoid division by zero
                        bytes_diff = current_bytes_total - self._prev_network_bytes
                        network_rate_mbps = (bytes_diff / time_diff) / (1024 * 1024)  # MB/s
                
                # Store current values for next calculation
                self._prev_network_time = current_time
                self._prev_network_bytes = current_bytes_total
                
                # Build metrics dictionary
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'network_usage': network_rate_mbps,  # MB/s (real-time rate)
                    'process_count': process_count,
                    'additional': {
                        'swap_usage': psutil.swap_memory().percent,
                        'cpu_temperature': cpu_temp,
                        'active_python_processes': python_processes,
                        'load_average': load_avg,
                        'network_details': {
                            'bytes_sent': network_io.bytes_sent,
                            'bytes_recv': network_io.bytes_recv,
                            'packets_sent': network_io.packets_sent,
                            'packets_recv': network_io.packets_recv,
                            'rate_mbps': network_rate_mbps
                        }
                    }
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
                    'additional': {
                        'error': str(e)
                    }
                }
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
