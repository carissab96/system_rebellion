"""
CPU Metrics Service

This service is responsible for collecting detailed CPU metrics including:
- Overall CPU usage
- Per-core CPU usage
- CPU temperature
- CPU frequency information
- Top CPU-consuming processes
- CPU core information
"""

import time
import psutil
import logging
from typing import Dict, Any, List
from datetime import datetime
from .transformers.cpu_metrics_transformer import transform_cpu_metrics

class CPUMetricsService:
    """Service for collecting detailed CPU metrics"""
    
    def __init__(self):
        """Initialize the CPU metrics service"""
        self.logger = logging.getLogger('CPUMetricsService')
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get detailed CPU metrics including per-core usage, top processes, and temperature.
        
        Returns:
            Dictionary containing detailed CPU metrics
        """
        try:
            # Get overall CPU usage with a consistent interval
            total_percent = psutil.cpu_percent(interval=1)
            
            # Get per-core CPU usage
            per_core_percent = psutil.cpu_percent(interval=0, percpu=True)
            
            # Get CPU frequency information
            cpu_freq_info = self._get_cpu_frequency()
            
            # Get CPU temperature
            cpu_temp = self._get_cpu_temperature()
            
            # Get top CPU-consuming processes
            top_processes = self._get_top_cpu_processes()
            
            # Get CPU count information
            cpu_cores = self._get_cpu_cores()
            
            # Collect raw metrics
            metrics = {}
            if total_percent is not None:
                metrics['total_percent'] = total_percent
            if per_core_percent:
                metrics['per_core_percent'] = per_core_percent
            if cpu_temp is not None:
                metrics['temperature'] = cpu_temp
            if cpu_freq_info:
                metrics['frequency'] = cpu_freq_info
            if cpu_cores:
                metrics['cores'] = cpu_cores
            if top_processes:
                metrics['top_processes'] = top_processes
                
            # Transform metrics to frontend format
            return transform_cpu_metrics(metrics)
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {str(e)}")
            # Return None for all metrics on error
            return {}
    
    def _get_cpu_frequency(self) -> Dict[str, Any]:
        """Get CPU frequency information"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                'current': cpu_freq.current if cpu_freq else None,
                'min': cpu_freq.min if cpu_freq and hasattr(cpu_freq, 'min') else None,
                'max': cpu_freq.max if cpu_freq and hasattr(cpu_freq, 'max') else None
            }
        except Exception as e:
            self.logger.error(f"Error getting CPU frequency: {str(e)}")
            return {'current': None, 'min': None, 'max': None}
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try different temperature sensors based on platform
                for sensor_name in ['coretemp', 'k10temp', 'acpitz', 'cpu_thermal']:
                    if sensor_name in temps:
                        return temps[sensor_name][0].current
            return None
        except Exception as e:
            self.logger.error(f"Error getting CPU temperature: {str(e)}")
            return None
    
    def _get_top_cpu_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top CPU-consuming processes"""
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
            
            # Sort by CPU usage (descending) and take top N
            top_cpu_processes = sorted(top_cpu_processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        except Exception as e:
            self.logger.error(f"Error getting top CPU processes: {str(e)}")
        
        return top_cpu_processes
    
    def _get_cpu_cores(self) -> Dict[str, int]:
        """Get CPU core information"""
        try:
            return {
                'logical': psutil.cpu_count(),
                'physical': psutil.cpu_count(logical=False)
            }
        except Exception as e:
            self.logger.error(f"Error getting CPU count: {str(e)}")
            return {'logical': None, 'physical': None}
