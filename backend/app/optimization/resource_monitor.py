# core/optimization/resource_monitor.py

import psutil
from typing import Dict, Optional
from datetime import datetime
import asyncio
import logging

class ResourceMonitor:
    """
    System Resource Monitor
    
    Watches your system resources like a hawk... 
    if hawks were interested in CPU usage and had a thing for metrics.
    
    Warning: May cause sudden urges to optimize everything in sight.
    """

    def __init__(self):
        self.logger = logging.getLogger('ResourceMonitor')
        self.is_monitoring = False
        self.monitoring_interval = 5  # seconds
        self.last_metrics: Optional[Dict] = None

    async def initialize(self):
        """Initialize the monitor (boot up the surveillance)"""
        self.logger.info("Resource Monitor powering up... beep boop")
        self.is_monitoring = False
        self.last_metrics = None

    async def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        try:
            #convert process iterator to list before getting length
            process_count = len(list(psutil.process_iter()))

            metrics = {
                'timestamp': datetime.now(),
                'cpu_usage': await self._get_cpu_usage(),
                'memory_usage': self._get_memory_usage(),
                'disk_usage': self._get_disk_usage(),
                'network_usage': self._get_network_usage(),
                'process_count': process_count,
                'additional': await self._get_additional_metrics()
            }
            
            self.last_metrics = metrics
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            raise

    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            # CPU usage needs a small interval to calculate
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"CPU metric error: {str(e)}")
            return 0.0

    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            self.logger.error(f"Memory metric error: {str(e)}")
            return 0.0

    def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            return psutil.disk_usage('/').percent
        except Exception as e:
            self.logger.error(f"Disk metric error: {str(e)}")
            return 0.0

    def _get_network_usage(self) -> float:
        """Get network usage"""
        try:
            network = psutil.net_io_counters()
            return (network.bytes_sent + network.bytes_recv) / 1024 / 1024  # Convert to MB
        except Exception as e:
            self.logger.error(f"Network metric error: {str(e)}")
            return 0.0

    async def _get_additional_metrics(self) -> Dict:
        """Get additional system metrics"""
        try:
            return {
                'swap_usage': psutil.swap_memory().percent,
                'cpu_temperature': self._get_cpu_temperature(),
                'active_python_processes': self._count_python_processes(),
                'load_average': self._get_load_average()
            }
        except Exception as e:
            self.logger.error(f"Additional metrics error: {str(e)}")
            return {}

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                return temps['coretemp'][0].current
            return None
        except Exception:
            return None

    def _count_python_processes(self) -> int:
        """Count number of Python processes"""
        try:
            return len([p for p in list(psutil.process_iter(['name'])) 
                       if 'python' in p.info['name'].lower()])
        except Exception:
            return 0

    def _get_load_average(self) -> list:
        """Get system load average"""
        try:
            return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        except Exception:
            return [0, 0, 0]

    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.is_monitoring = True
        while self.is_monitoring:
            await self.collect_metrics()
            await asyncio.sleep(self.monitoring_interval)

    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False

    async def get_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'last_update': self.last_metrics['timestamp'] if self.last_metrics else None,
            'monitoring_interval': self.monitoring_interval
        }

    async def cleanup(self):
        """Cleanup monitor resources"""
        self.logger.info("Resource Monitor powering down... *sad beep*")
        self.is_monitoring = False