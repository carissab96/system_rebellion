#!/usr/bin/env python3
"""
SimplifiedMetricsService Test Script

This script directly tests the SimplifiedMetricsService class to see if it's collecting
and processing system metrics correctly using the new simplified architecture.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add the parent directory to the path so we can import the SimplifiedMetricsService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the SimplifiedMetricsService
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService


async def test_simplified_metrics_service():
    """Test the SimplifiedMetricsService's ability to collect and process system metrics"""
    print("\n" + "="*60)
    print(" SIMPLIFIED METRICS SERVICE TEST - RAW DATA CHECK")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize SimplifiedMetricsService
    print("\nInitializing SimplifiedMetricsService...")
    service = await SimplifiedMetricsService.get_instance()
    print(f"SimplifiedMetricsService instance: {service}")
    
    # Test get_metrics
    print("\n[1] Testing get_metrics()...")
    try:
        metrics = await service.get_metrics(force_refresh=True)
        print(f"Metrics collected: {metrics is not None}")
        print(f"Metrics type: {type(metrics)}")
        print(f"Metrics keys: {list(metrics.keys()) if isinstance(metrics, dict) else 'Not a dict'}")
        print(f"Metrics sample: {json.dumps(metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting metrics: {str(e)}")
    
    # Test get_cpu_metrics
    print("\n[2] Testing get_cpu_metrics()...")
    try:
        cpu_metrics = await service.get_cpu_metrics()
        print(f"CPU metrics collected: {cpu_metrics is not None}")
        print(f"CPU metrics type: {type(cpu_metrics)}")
        print(f"CPU metrics keys: {list(cpu_metrics.keys()) if isinstance(cpu_metrics, dict) else 'Not a dict'}")
        print(f"CPU metrics sample: {json.dumps(cpu_metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting CPU metrics: {str(e)}")
    
    # Test get_memory_metrics
    print("\n[3] Testing get_memory_metrics()...")
    try:
        memory_metrics = await service.get_memory_metrics()
        print(f"Memory metrics collected: {memory_metrics is not None}")
        print(f"Memory metrics type: {type(memory_metrics)}")
        print(f"Memory metrics keys: {list(memory_metrics.keys()) if isinstance(memory_metrics, dict) else 'Not a dict'}")
        print(f"Memory metrics sample: {json.dumps(memory_metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting memory metrics: {str(e)}")
    
    # Test get_disk_metrics
    print("\n[4] Testing get_disk_metrics()...")
    try:
        disk_metrics = await service.get_disk_metrics()
        print(f"Disk metrics collected: {disk_metrics is not None}")
        print(f"Disk metrics type: {type(disk_metrics)}")
        print(f"Disk metrics keys: {list(disk_metrics.keys()) if isinstance(disk_metrics, dict) else 'Not a dict'}")
        print(f"Disk metrics sample: {json.dumps(disk_metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting disk metrics: {str(e)}")
    
    # Test get_network_metrics
    print("\n[5] Testing get_network_metrics()...")
    try:
        network_metrics = await service.get_network_metrics()
        print(f"Network metrics collected: {network_metrics is not None}")
        print(f"Network metrics type: {type(network_metrics)}")
        print(f"Network metrics keys: {list(network_metrics.keys()) if isinstance(network_metrics, dict) else 'Not a dict'}")
        print(f"Network metrics sample: {json.dumps(network_metrics, indent=2)[:500]}...")
    except Exception as e:
        print(f"ERROR collecting network metrics: {str(e)}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_simplified_metrics_service())
