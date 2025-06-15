#!/usr/bin/env python3
"""
Simplified Memory Metrics Service

A direct, no-nonsense memory metrics service that collects real-time memory data
using psutil and formats it for the frontend. No complex layers, no caching
issues, just pure data.
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio


class SimplifiedMemoryService:
    """
    Simplified memory metrics service that directly collects and formats memory data.
    No complex layers or transformations, just real data.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedMemoryService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedMemoryService')
        self._initialized = True
        self.logger.info("SimplifiedMemoryService initialized as singleton")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive memory metrics directly from psutil.
        No caching, no fallbacks, just real data.
        
        Returns:
            Dictionary containing memory metrics formatted for the frontend
        """
        try:
            # Get virtual memory statistics
            virtual_memory = psutil.virtual_memory()
            
            # Get swap memory statistics
            swap = psutil.swap_memory()
            
            # Get top memory-consuming processes
            top_processes = []
            try:
                # Get all processes sorted by memory usage
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
                    try:
                        processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Sort by memory usage and get top 10
                processes = sorted(processes, key=lambda p: p.info['memory_percent'], reverse=True)
                for i, proc in enumerate(processes[:10]):
                    try:
                        top_processes.append({
                            'pid': proc.pid,
                            'name': proc.info['name'],
                            'username': proc.info['username'],
                            'memory_percent': proc.info['memory_percent'],
                            'memory_mb': round(proc.info['memory_percent'] * virtual_memory.total / (1024 * 1024), 2)
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception as e:
                self.logger.error(f"Error getting top processes: {str(e)}")
            
            # Format the metrics for the frontend
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'memory',
                'data': {
                    'total': virtual_memory.total,
                    'available': virtual_memory.available,
                    'used': virtual_memory.used,
                    'free': virtual_memory.free,
                    'percent': virtual_memory.percent,
                    'cached': getattr(virtual_memory, 'cached', 0),
                    'buffers': getattr(virtual_memory, 'buffers', 0),
                    'shared': getattr(virtual_memory, 'shared', 0),
                    'swap': {
                        'total': swap.total,
                        'used': swap.used,
                        'free': swap.free,
                        'percent': swap.percent,
                        'sin': getattr(swap, 'sin', 0),
                        'sout': getattr(swap, 'sout', 0)
                    },
                    'top_processes': top_processes
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {str(e)}")
            # Return minimal data structure on error
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'memory',
                'data': {
                    'total': 0,
                    'available': 0,
                    'used': 0,
                    'free': 0,
                    'percent': 0,
                    'cached': 0,
                    'buffers': 0,
                    'shared': 0,
                    'swap': {
                        'total': 0,
                        'used': 0,
                        'free': 0,
                        'percent': 0,
                        'sin': 0,
                        'sout': 0
                    },
                    'top_processes': [],
                    'error': str(e)
                }
            }


# Test function to run the service directly
async def test_simplified_memory_service():
    """Test the simplified memory service"""
    print("\n" + "="*60)
    print(" SIMPLIFIED MEMORY SERVICE TEST")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = await SimplifiedMemoryService.get_instance()
    print(f"Service instance: {service}")
    
    # Get metrics
    metrics = await service.get_metrics()
    print("\nMemory Metrics:")
    print(f"Memory Usage: {metrics['data']['percent']}%")
    print(f"Total Memory: {metrics['data']['total'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Available Memory: {metrics['data']['available'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Used Memory: {metrics['data']['used'] / (1024 * 1024 * 1024):.2f} GB")
    
    print("\nSwap Usage:")
    print(f"Swap Usage: {metrics['data']['swap']['percent']}%")
    print(f"Total Swap: {metrics['data']['swap']['total'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Used Swap: {metrics['data']['swap']['used'] / (1024 * 1024 * 1024):.2f} GB")
    
    print("\nTop Memory-Consuming Processes:")
    for proc in metrics['data']['top_processes'][:5]:  # Show top 5
        print(f"  {proc['name']} (PID {proc['pid']}): {proc['memory_percent']:.2f}% ({proc['memory_mb']:.2f} MB)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_simplified_memory_service())
