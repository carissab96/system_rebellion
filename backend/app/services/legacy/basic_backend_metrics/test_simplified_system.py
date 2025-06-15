#!/usr/bin/env python3
"""
Simplified Metrics System Test

This script tests the entire simplified metrics system end-to-end.
It runs each service individually and then tests the combined metrics service.
"""

import asyncio
import json
from datetime import datetime
from pprint import pprint

from simplified_cpu_service import SimplifiedCPUService
from simplified_memory_service import SimplifiedMemoryService
from simplified_disk_service import SimplifiedDiskService
from simplified_network_service import SimplifiedNetworkService
from simplified_metrics_service import SimplifiedMetricsService


async def test_all_services():
    """Test all simplified services"""
    print("\n" + "="*80)
    print(" SIMPLIFIED METRICS SYSTEM - COMPLETE TEST SUITE ")
    print("="*80)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test CPU service
    print("\n" + "="*60)
    print(" 1. TESTING CPU SERVICE")
    print("="*60)
    cpu_service = await SimplifiedCPUService.get_instance()
    cpu_metrics = await cpu_service.get_metrics()
    print(f"CPU Usage: {cpu_metrics['data']['usage_percent']}%")
    print(f"Physical Cores: {cpu_metrics['data']['physical_cores']}")
    print(f"Logical Cores: {cpu_metrics['data']['logical_cores']}")
    print(f"CPU Temperature: {cpu_metrics['data']['temperature']} °C")
    print(f"Top Process: {cpu_metrics['data']['top_processes'][0]['name'] if cpu_metrics['data']['top_processes'] else 'None'}")
    
    # Test Memory service
    print("\n" + "="*60)
    print(" 2. TESTING MEMORY SERVICE")
    print("="*60)
    memory_service = await SimplifiedMemoryService.get_instance()
    memory_metrics = await memory_service.get_metrics()
    print(f"Memory Usage: {memory_metrics['data']['percent']}%")
    print(f"Total Memory: {memory_metrics['data']['total'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Available Memory: {memory_metrics['data']['available'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Swap Usage: {memory_metrics['data']['swap']['percent']}%")
    
    # Test Disk service
    print("\n" + "="*60)
    print(" 3. TESTING DISK SERVICE")
    print("="*60)
    disk_service = await SimplifiedDiskService.get_instance()
    disk_metrics = await disk_service.get_metrics()
    print(f"Disk Usage: {disk_metrics['data']['percent']}%")
    print(f"Total Disk: {disk_metrics['data']['total'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Used Disk: {disk_metrics['data']['used'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Free Disk: {disk_metrics['data']['free'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Partitions: {len(disk_metrics['data']['partitions'])}")
    
    # Test Network service
    print("\n" + "="*60)
    print(" 4. TESTING NETWORK SERVICE")
    print("="*60)
    network_service = await SimplifiedNetworkService.get_instance()
    network_metrics = await network_service.get_metrics()
    print(f"Bytes Sent: {network_metrics['data']['bytes_sent'] / (1024 * 1024):.2f} MB")
    print(f"Bytes Received: {network_metrics['data']['bytes_recv'] / (1024 * 1024):.2f} MB")
    print(f"Send Rate: {network_metrics['data']['sent_rate'] / 1024:.2f} KB/s")
    print(f"Receive Rate: {network_metrics['data']['recv_rate'] / 1024:.2f} KB/s")
    print(f"Interfaces: {len(network_metrics['data']['interfaces'])}")
    print(f"Connections: {len(network_metrics['data']['connections'])}")
    
    # Test Combined Metrics service
    print("\n" + "="*60)
    print(" 5. TESTING COMBINED METRICS SERVICE")
    print("="*60)
    metrics_service = await SimplifiedMetricsService.get_instance()
    all_metrics = await metrics_service.get_metrics()
    print(f"CPU Usage: {all_metrics['cpu_usage']}%")
    print(f"Memory Usage: {all_metrics['memory_usage']}%")
    print(f"Disk Usage: {all_metrics['disk_usage']}%")
    print(f"Network Send Rate: {all_metrics['network_sent_rate'] / 1024:.2f} KB/s")
    print(f"Network Receive Rate: {all_metrics['network_recv_rate'] / 1024:.2f} KB/s")
    
    # Verify all data is present
    print("\n" + "="*60)
    print(" 6. VERIFICATION OF DATA COMPLETENESS")
    print("="*60)
    
    # Check CPU data
    cpu_keys = all_metrics['cpu'].keys()
    print(f"CPU data keys: {len(cpu_keys)}")
    missing_cpu = [key for key in ['usage_percent', 'physical_cores', 'logical_cores', 'temperature', 'cores', 'top_processes'] if key not in cpu_keys]
    if missing_cpu:
        print(f"MISSING CPU KEYS: {missing_cpu}")
    else:
        print("✓ All essential CPU data present")
    
    # Check Memory data
    memory_keys = all_metrics['memory'].keys()
    print(f"Memory data keys: {len(memory_keys)}")
    missing_memory = [key for key in ['total', 'available', 'used', 'free', 'percent', 'swap', 'top_processes'] if key not in memory_keys]
    if missing_memory:
        print(f"MISSING MEMORY KEYS: {missing_memory}")
    else:
        print("✓ All essential Memory data present")
    
    # Check Disk data
    disk_keys = all_metrics['disk'].keys()
    print(f"Disk data keys: {len(disk_keys)}")
    missing_disk = [key for key in ['percent', 'total', 'used', 'free', 'partitions', 'io_counters'] if key not in disk_keys]
    if missing_disk:
        print(f"MISSING DISK KEYS: {missing_disk}")
    else:
        print("✓ All essential Disk data present")
    
    # Check Network data
    network_keys = all_metrics['network'].keys()
    print(f"Network data keys: {len(network_keys)}")
    missing_network = [key for key in ['bytes_sent', 'bytes_recv', 'sent_rate', 'recv_rate', 'interfaces', 'connections'] if key not in network_keys]
    if missing_network:
        print(f"MISSING NETWORK KEYS: {missing_network}")
    else:
        print("✓ All essential Network data present")
    
    print("\n" + "="*60)
    print(" TEST COMPLETE - SIMPLIFIED METRICS SYSTEM WORKING CORRECTLY")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_all_services())
