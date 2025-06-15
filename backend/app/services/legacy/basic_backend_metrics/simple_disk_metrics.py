#!/usr/bin/env python3
"""
Simple Disk Metrics - Direct psutil implementation

This script pulls real disk metrics from a Linux-based system using psutil.
It displays:
- Disk partitions and their mount points
- Disk usage for each partition (total, used, free)
- Disk I/O statistics (read/write counts, bytes, time)
- Disk I/O per partition

No fallback values, sample data, or hard-coded values are used.
All data is collected in real-time from the actual system.
"""

import psutil
import time
from datetime import datetime


def get_disk_partitions():
    """Get all disk partitions"""
    partitions = psutil.disk_partitions(all=False)
    
    result = []
    for partition in partitions:
        partition_info = {
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
            "opts": partition.opts
        }
        
        # Add usage information if available
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partition_info["total_gb"] = round(usage.total / (1024 ** 3), 2)
            partition_info["used_gb"] = round(usage.used / (1024 ** 3), 2)
            partition_info["free_gb"] = round(usage.free / (1024 ** 3), 2)
            partition_info["percent_used"] = usage.percent
        except (PermissionError, FileNotFoundError):
            # Some mountpoints might not be accessible
            partition_info["total_gb"] = None
            partition_info["used_gb"] = None
            partition_info["free_gb"] = None
            partition_info["percent_used"] = None
            
        result.append(partition_info)
        
    return result


def get_disk_io():
    """Get disk I/O statistics"""
    io_stats = psutil.disk_io_counters(perdisk=False)
    
    if io_stats:
        return {
            "read_count": io_stats.read_count,
            "write_count": io_stats.write_count,
            "read_bytes": io_stats.read_bytes,
            "write_bytes": io_stats.write_bytes,
            "read_time_ms": io_stats.read_time,
            "write_time_ms": io_stats.write_time,
            "read_mb": round(io_stats.read_bytes / (1024 ** 2), 2),
            "write_mb": round(io_stats.write_bytes / (1024 ** 2), 2)
        }
    else:
        return None


def get_disk_io_per_disk():
    """Get disk I/O statistics per disk"""
    io_stats = psutil.disk_io_counters(perdisk=True)
    
    result = {}
    if io_stats:
        for disk, stats in io_stats.items():
            result[disk] = {
                "read_count": stats.read_count,
                "write_count": stats.write_count,
                "read_mb": round(stats.read_bytes / (1024 ** 2), 2),
                "write_mb": round(stats.write_bytes / (1024 ** 2), 2),
                "read_time_ms": stats.read_time,
                "write_time_ms": stats.write_time
            }
    
    return result


def display_metrics():
    """Display all collected disk metrics"""
    print("\n" + "="*60)
    print(" SIMPLE DISK METRICS - REAL-TIME SYSTEM DATA")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Disk partitions
    partitions = get_disk_partitions()
    print(f"\nDISK PARTITIONS:")
    print(f"{'DEVICE':<15} {'MOUNTPOINT':<20} {'TYPE':<10} {'TOTAL':<10} {'USED %':<10}")
    print("-" * 60)
    
    for part in partitions:
        total = f"{part['total_gb']:.1f} GB" if part['total_gb'] is not None else "N/A"
        percent = f"{part['percent_used']}%" if part['percent_used'] is not None else "N/A"
        
        print(f"{part['device'][:15]:<15} {part['mountpoint'][:20]:<20} {part['fstype'][:10]:<10} {total:<10} {percent:<10}")
    
    # Overall disk I/O
    io_stats = get_disk_io()
    if io_stats:
        print(f"\nOVERALL DISK I/O:")
        print(f"  Read:  {io_stats['read_count']} operations, {io_stats['read_mb']:.2f} MB")
        print(f"  Write: {io_stats['write_count']} operations, {io_stats['write_mb']:.2f} MB")
        print(f"  Read time:  {io_stats['read_time_ms']} ms")
        print(f"  Write time: {io_stats['write_time_ms']} ms")
    
    # Per-disk I/O
    disk_io = get_disk_io_per_disk()
    if disk_io:
        print(f"\nPER-DISK I/O:")
        print(f"{'DISK':<15} {'READ OPS':<10} {'READ MB':<10} {'WRITE OPS':<10} {'WRITE MB':<10}")
        print("-" * 60)
        
        for disk_name, stats in disk_io.items():
            print(f"{disk_name[:15]:<15} {stats['read_count']:<10} {stats['read_mb']:<10.2f} {stats['write_count']:<10} {stats['write_mb']:<10.2f}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    display_metrics()
