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
            
            # Only return metrics that were successfully collected
            metrics = {}
            
            # Virtual memory metrics
            if virtual_memory:
                metrics.update({
                    'total': virtual_memory.total,
                    'available': virtual_memory.available,
                    'used': virtual_memory.used,
                    'free': virtual_memory.free,
                    'percent': virtual_memory.percent
                })
                
                # Optional virtual memory metrics
                cached = getattr(virtual_memory, 'cached', None)
                if cached is not None:
                    metrics['cached'] = cached
                    
                buffers = getattr(virtual_memory, 'buffers', None)
                if buffers is not None:
                    metrics['buffers'] = buffers
                    
                shared = getattr(virtual_memory, 'shared', None)
                if shared is not None:
                    metrics['shared'] = shared
            
            # Swap memory metrics
            if swap_memory:
                swap_metrics = {
                    'total': swap_memory.total,
                    'used': swap_memory.used,
                    'free': swap_memory.free,
                    'percent': swap_memory.percent
                }
                
                # Optional swap metrics
                sin = getattr(swap_memory, 'sin', None)
                if sin is not None:
                    swap_metrics['sin'] = sin
                    
                sout = getattr(swap_memory, 'sout', None)
                if sout is not None:
                    swap_metrics['sout'] = sout
                    
                metrics['swap'] = swap_metrics
            
            # Process metrics
            if top_processes:
                metrics['top_processes'] = top_processes
                
            return metrics
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {str(e)}")
            # Return empty dict on error
            return {}
    
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
