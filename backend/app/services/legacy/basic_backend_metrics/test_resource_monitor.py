#!/usr/bin/env python3
"""
ResourceMonitor Test Script

This script directly tests the ResourceMonitor class to see if it's collecting
system metrics correctly. It bypasses all the service layers and transformations
to get raw data directly from the source.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the parent directory to the path so we can import the ResourceMonitor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the ResourceMonitor
from app.optimization.resource_monitor import ResourceMonitor


async def test_resource_monitor():
    """Test the ResourceMonitor's ability to collect system metrics"""
    print("\n" + "="*60)
    print(" RESOURCE MONITOR TEST - RAW DATA CHECK")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize ResourceMonitor
    print("\nInitializing ResourceMonitor...")
    monitor = ResourceMonitor()
    await monitor.initialize()
    print(f"ResourceMonitor instance: {monitor}")
    
    # Test collect_metrics method
    print("\n[1] Testing collect_metrics()...")
    try:
        metrics = await monitor.collect_metrics()
        print(f"Metrics collected: {metrics is not None}")
        print(f"Metrics type: {type(metrics)}")
        print(f"Metrics keys: {list(metrics.keys()) if isinstance(metrics, dict) else 'Not a dict'}")
        print(f"Metrics sample: {json.dumps(metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting metrics: {str(e)}")
    
    # Test CPU usage
    print("\n[2] Testing _get_cpu_usage()...")
    try:
        cpu_usage = await monitor._get_cpu_usage()
        print(f"CPU usage: {cpu_usage}")
    except Exception as e:
        print(f"ERROR getting CPU usage: {str(e)}")
    
    # Test memory usage
    print("\n[3] Testing _get_memory_usage()...")
    try:
        memory_usage = monitor._get_memory_usage()
        print(f"Memory usage: {memory_usage}")
    except Exception as e:
        print(f"ERROR getting memory usage: {str(e)}")
    
    # Test disk usage
    print("\n[4] Testing _get_disk_usage()...")
    try:
        disk_usage = monitor._get_disk_usage()
        print(f"Disk usage: {disk_usage}")
    except Exception as e:
        print(f"ERROR getting disk usage: {str(e)}")
    
    # Test network metrics
    print("\n[5] Testing _get_throttled_network_metrics()...")
    try:
        network_metrics = await monitor._get_throttled_network_metrics()
        print(f"Network metrics collected: {network_metrics is not None}")
        print(f"Network metrics type: {type(network_metrics)}")
        print(f"Network metrics keys: {list(network_metrics.keys()) if isinstance(network_metrics, dict) else 'Not a dict'}")
        print(f"Network metrics sample: {json.dumps(network_metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting network metrics: {str(e)}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_resource_monitor())
