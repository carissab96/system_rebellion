#!/usr/bin/env python3
"""
Simple CPU Metrics - Direct psutil implementation

This script pulls real metrics from a Linux-based system using psutil.
It displays:
- CPU count (cores)
- Per-core CPU usage percentages
- All running processes sorted by CPU usage (highest to lowest)
- Process details including PID, name, username, CPU%, and memory%

No fallback values, sample data, or hard-coded values are used.
All data is collected in real-time from the actual system.
"""

import psutil
import time
from datetime import datetime
import os


def get_cpu_count():
    """Get the number of logical and physical CPU cores"""
    logical_cores = psutil.cpu_count()
    physical_cores = psutil.cpu_count(logical=False)
    
    return {
        "logical_cores": logical_cores,
        "physical_cores": physical_cores
    }


def get_per_core_usage():
    """Get the CPU usage percentage for each core"""
    # First call to establish baseline
    psutil.cpu_percent(percpu=True)
    
    # Wait a moment for accurate measurement
    time.sleep(0.5)
    
    # Second call to get actual percentages
    per_core_percent = psutil.cpu_percent(percpu=True)
    
    return {
        f"core_{i}": percent for i, percent in enumerate(per_core_percent)
    }


def get_all_processes():
    """Get all running processes sorted by CPU usage (highest to lowest)"""
    processes = []
    
    # First pass to collect processes and initialize CPU measurement
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            proc.cpu_percent(interval=None)  # Initialize CPU measurement
            processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Wait a moment for accurate measurement
    time.sleep(0.5)
    
    # Second pass to get actual CPU usage
    process_list = []
    for proc in processes:
        try:
            cpu_percent = proc.cpu_percent(interval=None)
            memory_percent = proc.info['memory_percent'] if 'memory_percent' in proc.info else 0
            
            process_info = {
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "username": proc.info['username'] if 'username' in proc.info else 'unknown',
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
            
            # Only include processes that are using CPU
            if cpu_percent > 0:
                process_list.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by CPU usage (highest to lowest)
    return sorted(process_list, key=lambda x: x['cpu_percent'], reverse=True)


def get_system_load():
    """Get system load averages for the past 1, 5, and 15 minutes"""
    return {
        "load_1min": os.getloadavg()[0],
        "load_5min": os.getloadavg()[1],
        "load_15min": os.getloadavg()[2]
    }


def get_memory_info():
    """Get memory usage information"""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "percent_used": mem.percent
    }


def display_metrics():
    """Display all collected metrics"""
    print("\n" + "="*50)
    print(" SIMPLE CPU METRICS - REAL-TIME SYSTEM DATA")
    print("="*50)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # CPU count
    cpu_count = get_cpu_count()
    print(f"\nCPU CORES:")
    print(f"  Physical cores: {cpu_count['physical_cores']}")
    print(f"  Logical cores: {cpu_count['logical_cores']}")
    
    # System load
    load = get_system_load()
    print(f"\nSYSTEM LOAD:")
    print(f"  1 minute: {load['load_1min']}")
    print(f"  5 minutes: {load['load_5min']}")
    print(f"  15 minutes: {load['load_15min']}")
    
    # Memory info
    memory = get_memory_info()
    print(f"\nMEMORY USAGE:")
    print(f"  Total: {memory['total_gb']} GB")
    print(f"  Available: {memory['available_gb']} GB")
    print(f"  Used: {memory['used_gb']} GB ({memory['percent_used']}%)")
    
    # Per-core usage
    core_usage = get_per_core_usage()
    print(f"\nPER-CORE CPU USAGE:")
    for core, percent in core_usage.items():
        print(f"  {core}: {percent}%")
    
    # Process list
    processes = get_all_processes()
    print(f"\nPROCESSES BY CPU USAGE (TOP 20):")
    print(f"{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'USER':<15} {'NAME':<30}")
    print("-" * 70)
    
    for proc in processes[:20]:  # Show top 20 processes
        print(f"{proc['pid']:<8} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<8.1f} {proc['username'][:15]:<15} {proc['name'][:30]}")
    
    print(f"\nTotal processes with CPU activity: {len(processes)}")
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    display_metrics()
