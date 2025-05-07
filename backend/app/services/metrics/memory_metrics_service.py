"""
Memory Metrics Service

This service is responsible for collecting detailed memory metrics including:
- Overall memory usage
- Memory type breakdown (used, available, cached, buffers)
- Swap usage
- Top memory-consuming processes
"""

import psutil
import logging
from typing import Dict, Any, List
from datetime import datetime

class MemoryMetricsService:
    """Service for collecting detailed memory metrics"""
    
    def __init__(self):
        """Initialize the memory metrics service"""
        self.logger = logging.getLogger('MemoryMetricsService')
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get detailed memory metrics.
        
        Returns:
            Dictionary containing detailed memory metrics
        """
        try:
            # Get virtual memory information
            virtual_memory = psutil.virtual_memory()
            
            # Get swap memory information
            swap_memory = psutil.swap_memory()
            
            # Get top memory-consuming processes
            top_processes = self._get_top_memory_processes()
            
            return {
                'total': virtual_memory.total,
                'available': virtual_memory.available,
                'used': virtual_memory.used,
                'free': virtual_memory.free,
                'percent': virtual_memory.percent,
                'cached': getattr(virtual_memory, 'cached', None),
                'buffers': getattr(virtual_memory, 'buffers', None),
                'shared': getattr(virtual_memory, 'shared', None),
                'swap': {
                    'total': swap_memory.total,
                    'used': swap_memory.used,
                    'free': swap_memory.free,
                    'percent': swap_memory.percent,
                    'sin': getattr(swap_memory, 'sin', None),  # Swap in (bytes)
                    'sout': getattr(swap_memory, 'sout', None)  # Swap out (bytes)
                },
                'top_processes': top_processes
            }
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {str(e)}")
            return {
                'total': 0,
                'available': 0,
                'used': 0,
                'free': 0,
                'percent': 0,
                'cached': None,
                'buffers': None,
                'shared': None,
                'swap': {
                    'total': 0,
                    'used': 0,
                    'free': 0,
                    'percent': 0,
                    'sin': None,
                    'sout': None
                },
                'top_processes': []
            }
    
    def _get_top_memory_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top memory-consuming processes"""
        top_memory_processes = []
        try:
            # Get all processes with memory info
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'memory_info', 'create_time']):
                try:
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Create process info dictionaries
            for proc in processes:
                try:
                    memory_percent = proc.info['memory_percent']
                    if memory_percent > 0:  # Only include processes actually using memory
                        memory_info = proc.info['memory_info']
                        top_memory_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'username': proc.info['username'],
                            'memory_percent': memory_percent,
                            'rss': memory_info.rss if memory_info else None,  # Resident Set Size
                            'vms': memory_info.vms if memory_info else None,  # Virtual Memory Size
                            'create_time': datetime.fromtimestamp(proc.info['create_time']).isoformat() if proc.info['create_time'] else None
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by memory usage (descending) and take top N
            top_memory_processes = sorted(top_memory_processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
        except Exception as e:
            self.logger.error(f"Error getting top memory processes: {str(e)}")
        
        return top_memory_processes
