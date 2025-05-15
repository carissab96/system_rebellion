"""
DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the new metrics service at `app.services.metrics`.

This service provides a single source of truth for system metrics
across all parts of the application, ensuring consistent values
are shown in the dashboard, auto-tuner, and system metrics pages.
"""

import warnings
warnings.warn(
    "The system_metrics_service module is deprecated and will be removed in a future version. "
    "Please use the new metrics service at app.services.metrics.",
    DeprecationWarning,
    stacklevel=2
)

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import the new metrics service
from app.services.metrics.metrics_service import MetricsService

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
        
        # Initialize the new metrics service
        self.metrics_service = MetricsService()
        
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
        try:
            # Delegate to the new metrics service
            metrics = await self.metrics_service.get_metrics(force_refresh)
            
            # Store in our local cache for backward compatibility
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
    
    def _get_detailed_cpu_metrics(self) -> Dict[str, Any]:
        """
        Get detailed CPU metrics including per-core usage, top processes, and temperature.
        
        Returns:
            Dictionary containing detailed CPU metrics
        """
        # Get overall CPU usage with a consistent interval
        total_percent = psutil.cpu_percent(interval=1)
        
        # Get per-core CPU usage
        per_core_percent = psutil.cpu_percent(interval=0, percpu=True)
        
        # Get CPU frequency information
        try:
            cpu_freq = psutil.cpu_freq()
            current_freq = cpu_freq.current if cpu_freq else None
            min_freq = cpu_freq.min if cpu_freq and hasattr(cpu_freq, 'min') else None
            max_freq = cpu_freq.max if cpu_freq and hasattr(cpu_freq, 'max') else None
        except Exception as e:
            self.logger.error(f"Error getting CPU frequency: {str(e)}")
            current_freq, min_freq, max_freq = None, None, None
        
        # Get CPU temperature if available
        cpu_temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try different temperature sensors based on platform
                for sensor_name in ['coretemp', 'k10temp', 'acpitz', 'cpu_thermal']:
                    if sensor_name in temps:
                        cpu_temp = temps[sensor_name][0].current
                        break
        except Exception as e:
            self.logger.error(f"Error getting CPU temperature: {str(e)}")
        
        # Get top CPU-consuming processes
        top_cpu_processes = []
        try:
            # Get all processes and sort by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    # Update CPU usage value
                    proc.cpu_percent(interval=0)
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sleep briefly to allow CPU percent to be measured
            time.sleep(0.1)
            
            # Get CPU percent again and create process info
            for proc in processes:
                try:
                    cpu_usage = proc.cpu_percent(interval=0)
                    if cpu_usage > 0:  # Only include processes actually using CPU
                        top_cpu_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'username': proc.info['username'],
                            'cpu_percent': cpu_usage,
                            'memory_percent': proc.info['memory_percent'],
                            'create_time': datetime.fromtimestamp(proc.info['create_time']).isoformat() if proc.info['create_time'] else None
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by CPU usage (descending) and take top 5
            top_cpu_processes = sorted(top_cpu_processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        except Exception as e:
            self.logger.error(f"Error getting top CPU processes: {str(e)}")
        
        # Get CPU count information
        try:
            logical_cores = psutil.cpu_count()
            physical_cores = psutil.cpu_count(logical=False)
        except Exception as e:
            self.logger.error(f"Error getting CPU count: {str(e)}")
            logical_cores, physical_cores = None, None
        
        return {
            'total_percent': total_percent,
            'per_core_percent': per_core_percent,
            'temperature': cpu_temp,
            'frequency': {
                'current': current_freq,
                'min': min_freq,
                'max': max_freq
            },
            'cores': {
                'logical': logical_cores,
                'physical': physical_cores
            },
            'top_processes': top_cpu_processes
        }
        
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
