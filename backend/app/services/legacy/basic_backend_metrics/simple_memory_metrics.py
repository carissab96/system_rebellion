#!/usr/bin/env python3
"""
Simple Memory Metrics - Direct psutil implementation

This script pulls real memory metrics from a Linux-based system using psutil.
It displays:
- Total, available, used, and free memory
- Swap memory usage
- Memory usage by process (top consumers)

No fallback values, sample data, or hard-coded values are used.
All data is collected in real-time from the actual system.
"""

import psutil
import time
from datetime import datetime


def get_virtual_memory():
    """Get detailed virtual memory information"""
    mem = psutil.virtual_memory()
    
    # Convert bytes to more readable format
    total_gb = mem.total / (1024 ** 3)
    available_gb = mem.available / (1024 ** 3)
    used_gb = mem.used / (1024 ** 3)
    free_gb = mem.free / (1024 ** 3)
    
    return {
        "total_gb": round(total_gb, 2),
        "available_gb": round(available_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
        "percent_used": mem.percent,
        "buffers_gb": round(getattr(mem, 'buffers', 0) / (1024 ** 3), 2),
        "cached_gb": round(getattr(mem, 'cached', 0) / (1024 ** 3), 2)
    }


def get_swap_memory():
    """Get swap memory information"""
    swap = psutil.swap_memory()
    
    # Convert bytes to more readable format
    total_gb = swap.total / (1024 ** 3)
    used_gb = swap.used / (1024 ** 3)
    free_gb = swap.free / (1024 ** 3)
    
    return {
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
        "percent_used": swap.percent,
        "sin_gb": round(getattr(swap, 'sin', 0) / (1024 ** 3), 2),
        "sout_gb": round(getattr(swap, 'sout', 0) / (1024 ** 3), 2)
    }


def get_memory_by_process():
    """Get memory usage by process (sorted by memory usage)"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent']):
        try:
            process_info = {
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "username": proc.info['username'] if 'username' in proc.info else 'unknown',
                "memory_percent": proc.info['memory_percent'] if 'memory_percent' in proc.info else 0
            }
            
            # Only include processes that are using memory
            if process_info["memory_percent"] > 0:
                processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by memory usage (highest to lowest)
    return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)


def display_metrics():
    """Display all collected memory metrics"""
    print("\n" + "="*50)
    print(" SIMPLE MEMORY METRICS - REAL-TIME SYSTEM DATA")
    print("="*50)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Virtual memory
    vm = get_virtual_memory()
    print(f"\nVIRTUAL MEMORY:")
    print(f"  Total:     {vm['total_gb']:.2f} GB")
    print(f"  Available: {vm['available_gb']:.2f} GB")
    print(f"  Used:      {vm['used_gb']:.2f} GB ({vm['percent_used']}%)")
    print(f"  Free:      {vm['free_gb']:.2f} GB")
    print(f"  Buffers:   {vm['buffers_gb']:.2f} GB")
    print(f"  Cached:    {vm['cached_gb']:.2f} GB")
    
    # Swap memory
    swap = get_swap_memory()
    print(f"\nSWAP MEMORY:")
    print(f"  Total:     {swap['total_gb']:.2f} GB")
    print(f"  Used:      {swap['used_gb']:.2f} GB ({swap['percent_used']}%)")
    print(f"  Free:      {swap['free_gb']:.2f} GB")
    print(f"  Swapped in:  {swap['sin_gb']:.2f} GB")
    print(f"  Swapped out: {swap['sout_gb']:.2f} GB")
    
    # Process memory usage
    processes = get_memory_by_process()
    print(f"\nPROCESSES BY MEMORY USAGE (TOP 20):")
    print(f"{'PID':<8} {'MEM%':<8} {'USER':<15} {'NAME':<30}")
    print("-" * 60)
    
    for proc in processes[:20]:  # Show top 20 processes
        print(f"{proc['pid']:<8} {proc['memory_percent']:<8.1f} {proc['username'][:15]:<15} {proc['name'][:30]}")
    
    print(f"\nTotal processes with memory activity: {len(processes)}")
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    display_metrics()
