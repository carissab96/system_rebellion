#!/usr/bin/env python3
"""
Simplified CPU Metrics Service

A direct, no-nonsense CPU metrics service that collects real-time CPU data
using psutil and formats it for the frontend. No complex layers, no caching
issues, just pure data.
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio


class SimplifiedCPUService:
    """
    Simplified CPU metrics service that directly collects and formats CPU data.
    No complex layers or transformations, just real data.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedCPUService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedCPUService')
        self._initialized = True
        self.logger.info("SimplifiedCPUService initialized as singleton")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive CPU metrics directly from psutil.
        No caching, no fallbacks, just real data.
        
        Returns:
            Dictionary containing CPU metrics formatted for the frontend
        """
        try:
            # Get basic CPU info
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            # Get per-core CPU usage (non-blocking)
            per_core_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Get overall CPU usage (non-blocking)
            overall_percent = psutil.cpu_percent(interval=0.1)
            
            # Get CPU frequency
            freq = psutil.cpu_freq()
            frequency = {
                'current': freq.current if freq else 0,
                'min': freq.min if freq and hasattr(freq, 'min') else 0,
                'max': freq.max if freq and hasattr(freq, 'max') else 0
            }
            
            # Get CPU temperature if available
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps and 'coretemp' in temps:
                    temperature = temps['coretemp'][0].current
            except (AttributeError, IndexError):
                pass
            
            # Get top CPU-consuming processes
            top_processes = []
            try:
                # Get all processes sorted by CPU usage
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                    try:
                        # Update CPU usage
                        proc.cpu_percent(interval=0)
                        processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Short sleep to allow CPU percent to be measured
                await asyncio.sleep(0.1)
                
                # Sort by CPU usage and get top 10
                processes = sorted(processes, key=lambda p: p.cpu_percent(), reverse=True)
                for i, proc in enumerate(processes[:10]):
                    try:
                        top_processes.append({
                            'pid': proc.pid,
                            'name': proc.info['name'],
                            'username': proc.info['username'],
                            'cpu_percent': proc.cpu_percent(),
                            'memory_percent': proc.info['memory_percent']
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception as e:
                self.logger.error(f"Error getting top processes: {str(e)}")
            
            # Format the metrics for the frontend
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'cpu',
                'data': {
                    'usage_percent': overall_percent,
                    'physical_cores': cpu_count_physical,
                    'logical_cores': cpu_count_logical,
                    'frequency_mhz': frequency['current'],
                    'temperature': temperature,
                    'cores': per_core_percent,
                    'top_processes': top_processes,
                    'frequency_details': frequency
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {str(e)}")
            # Return minimal data structure on error
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'cpu',
                'data': {
                    'usage_percent': 0,
                    'physical_cores': 0,
                    'logical_cores': 0,
                    'frequency_mhz': 0,
                    'temperature': None,
                    'cores': [],
                    'top_processes': [],
                    'frequency_details': {'current': 0, 'min': 0, 'max': 0},
                    'error': str(e)
                }
            }


# Test function to run the service directly
async def test_simplified_cpu_service():
    """Test the simplified CPU service"""
    print("\n" + "="*60)
    print(" SIMPLIFIED CPU SERVICE TEST")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = await SimplifiedCPUService.get_instance()
    print(f"Service instance: {service}")
    
    # Get metrics
    metrics = await service.get_metrics()
    print("\nCPU Metrics:")
    print(f"Overall CPU Usage: {metrics['data']['usage_percent']}%")
    print(f"Physical Cores: {metrics['data']['physical_cores']}")
    print(f"Logical Cores: {metrics['data']['logical_cores']}")
    print(f"CPU Frequency: {metrics['data']['frequency_mhz']} MHz")
    print(f"CPU Temperature: {metrics['data']['temperature']} °C")
    
    print("\nPer-Core Usage:")
    for i, usage in enumerate(metrics['data']['cores']):
        print(f"  Core {i}: {usage}%")
    
    print("\nTop CPU-Consuming Processes:")
    for proc in metrics['data']['top_processes'][:5]:  # Show top 5
        print(f"  {proc['name']} (PID {proc['pid']}): {proc['cpu_percent']}% CPU, {proc['memory_percent']:.2f}% Memory")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_simplified_cpu_service())
