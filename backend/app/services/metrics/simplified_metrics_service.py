#!/usr/bin/env python3
"""
Simplified Metrics Service

A direct, no-nonsense metrics service that combines all individual metrics services
and provides a unified interface for the WebSocket route. No complex layers, no caching
issues, just pure data.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.metrics.simplified_cpu_service import SimplifiedCPUService
from app.services.metrics.simplified_memory_service import SimplifiedMemoryService
from app.services.metrics.simplified_disk_service import SimplifiedDiskService
from app.services.metrics.simplified_network_service import SimplifiedNetworkService


class SimplifiedMetricsService:
    """
    Simplified metrics service that combines all individual metrics services.
    No complex layers or transformations, just real data.
    """
    
    _instance = None
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedMetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedMetricsService')
        self._initialized = True
        self.logger.info("SimplifiedMetricsService initialized as singleton")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def _get_lock(self):
        """Get or create the async lock"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def get_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """
        Get comprehensive system metrics from all services.
        
        Args:
            force_refresh: Ignored in this implementation (no caching)
            
        Returns:
            Dictionary containing all system metrics
        """
        try:
            # Get lock to prevent multiple concurrent collections
            lock = await self._get_lock()
            async with lock:
                # Initialize services
                cpu_service = await SimplifiedCPUService.get_instance()
                memory_service = await SimplifiedMemoryService.get_instance()
                disk_service = await SimplifiedDiskService.get_instance()
                network_service = await SimplifiedNetworkService.get_instance()
                
                # Collect metrics from each service concurrently
                cpu_task = asyncio.create_task(cpu_service.get_metrics())
                memory_task = asyncio.create_task(memory_service.get_metrics())
                disk_task = asyncio.create_task(disk_service.get_metrics())
                network_task = asyncio.create_task(network_service.get_metrics())
                
                # Wait for all metrics to be collected
                cpu_metrics, memory_metrics, disk_metrics, network_metrics = await asyncio.gather(
                    cpu_task, memory_task, disk_task, network_task
                )
                
                # Extract the data from each service
                cpu_data = cpu_metrics['data']
                memory_data = memory_metrics['data']
                disk_data = disk_metrics['data']
                network_data = network_metrics['data']
                
                # Combine all metrics into a single response
                return {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': cpu_data['usage_percent'],
                    'memory_usage': memory_data['percent'],
                    'disk_usage': disk_data['percent'],
                    'network_sent_rate': network_data['sent_rate'],
                    'network_recv_rate': network_data['recv_rate'],
                    'cpu': cpu_data,
                    'memory': memory_data,
                    'disk': disk_data,
                    'network': network_data,
                    'process_count': len(cpu_data.get('top_processes', [])),
                    'system_info': {
                        'hostname': network_data.get('interfaces', [{}])[0].get('name', 'unknown') if network_data.get('interfaces') else 'unknown',
                        'physical_cores': cpu_data.get('physical_cores', 0),
                        'logical_cores': cpu_data.get('logical_cores', 0),
                        'total_memory': memory_data.get('total', 0),
                        'total_disk': disk_data.get('total', 0)
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
            # Return minimal data structure on error
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'network_sent_rate': 0,
                'network_recv_rate': 0,
                'cpu': {},
                'memory': {},
                'disk': {},
                'network': {},
                'process_count': 0,
                'system_info': {},
                'error': str(e)
            }
    
    async def get_cpu_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get CPU metrics only"""
        cpu_service = await SimplifiedCPUService.get_instance()
        return (await cpu_service.get_metrics())['data']
    
    async def get_memory_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get memory metrics only"""
        memory_service = await SimplifiedMemoryService.get_instance()
        return (await memory_service.get_metrics())['data']
    
    async def get_disk_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get disk metrics only"""
        disk_service = await SimplifiedDiskService.get_instance()
        return (await disk_service.get_metrics())['data']
    
    async def get_network_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get network metrics only"""
        network_service = await SimplifiedNetworkService.get_instance()
        return (await network_service.get_metrics())['data']


# Test function to run the service directly
async def test_simplified_metrics_service():
    """Test the simplified metrics service"""
    print("\n" + "="*60)
    print(" SIMPLIFIED METRICS SERVICE TEST")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = await SimplifiedMetricsService.get_instance()
    print(f"Service instance: {service}")
    
    # Get metrics
    metrics = await service.get_metrics()
    print("\nSystem Metrics Overview:")
    print(f"CPU Usage: {metrics['cpu_usage']}%")
    print(f"Memory Usage: {metrics['memory_usage']}%")
    print(f"Disk Usage: {metrics['disk_usage']}%")
    print(f"Network Send Rate: {metrics['network_sent_rate'] / 1024:.2f} KB/s")
    print(f"Network Receive Rate: {metrics['network_recv_rate'] / 1024:.2f} KB/s")
    print(f"Process Count: {metrics['process_count']}")
    
    print("\nSystem Info:")
    for key, value in metrics['system_info'].items():
        if key in ['total_memory', 'total_disk']:
            print(f"  {key}: {value / (1024 * 1024 * 1024):.2f} GB")
        else:
            print(f"  {key}: {value}")
    
    print("\nDetailed Metrics Available:")
    print(f"CPU: {len(metrics['cpu'])} metrics")
    print(f"Memory: {len(metrics['memory'])} metrics")
    print(f"Disk: {len(metrics['disk'])} metrics")
    print(f"Network: {len(metrics['network'])} metrics")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_simplified_metrics_service())
