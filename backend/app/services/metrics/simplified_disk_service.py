#!/usr/bin/env python3
"""
Simplified Disk Metrics Service

A direct, no-nonsense disk metrics service that collects real-time disk data
using psutil and formats it for the frontend. No complex layers, no caching
issues, just pure data.
"""

import psutil
import time
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio


class SimplifiedDiskService:
    """
    Simplified disk metrics service that directly collects and formats disk data.
    No complex layers or transformations, just real data.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedDiskService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedDiskService')
        self._last_io_counters = None
        self._last_io_time = None
        self._initialized = True
        self.logger.info("SimplifiedDiskService initialized as singleton")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive disk metrics directly from psutil.
        No caching, no fallbacks, just real data.
        
        Returns:
            Dictionary containing disk metrics formatted for the frontend
        """
        try:
            # Get disk partitions
            partitions = []
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions.append({
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'opts': part.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except (PermissionError, FileNotFoundError):
                    # Skip partitions that can't be accessed
                    continue
            
            # Get overall disk usage (using root partition as reference)
            root_usage = psutil.disk_usage('/')
            
            # Get disk I/O statistics
            io_counters = psutil.disk_io_counters(perdisk=True)
            
            # Calculate I/O rates if we have previous measurements
            read_bytes = 0
            write_bytes = 0
            read_rate = 0
            write_rate = 0
            
            current_time = time.time()
            total_io = psutil.disk_io_counters()
            
            if total_io:
                read_bytes = total_io.read_bytes
                write_bytes = total_io.write_bytes
                
                if self._last_io_counters and self._last_io_time:
                    time_diff = current_time - self._last_io_time
                    if time_diff > 0:
                        read_rate = (total_io.read_bytes - self._last_io_counters.read_bytes) / time_diff
                        write_rate = (total_io.write_bytes - self._last_io_counters.write_bytes) / time_diff
            
            # Update last values for next calculation
            self._last_io_counters = total_io
            self._last_io_time = current_time
            
            # Format the metrics for the frontend
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'disk',
                'data': {
                    'percent': root_usage.percent,
                    'total': root_usage.total,
                    'used': root_usage.used,
                    'free': root_usage.free,
                    'read_bytes': read_bytes,
                    'write_bytes': write_bytes,
                    'read_rate': read_rate,
                    'write_rate': write_rate,
                    'partitions': partitions,
                    'io_counters': {
                        disk: {
                            'read_count': counters.read_count,
                            'write_count': counters.write_count,
                            'read_bytes': counters.read_bytes,
                            'write_bytes': counters.write_bytes,
                            'read_time': getattr(counters, 'read_time', 0),
                            'write_time': getattr(counters, 'write_time', 0),
                            'busy_time': getattr(counters, 'busy_time', 0)
                        } for disk, counters in io_counters.items()
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {str(e)}")
            # Return minimal data structure on error
            return {
                'timestamp': datetime.now().isoformat(),
                'type': 'disk',
                'data': {
                    'percent': 0,
                    'total': 0,
                    'used': 0,
                    'free': 0,
                    'read_bytes': 0,
                    'write_bytes': 0,
                    'read_rate': 0,
                    'write_rate': 0,
                    'partitions': [],
                    'io_counters': {},
                    'error': str(e)
                }
            }
    
    async def get_largest_directories(self, path='/', limit=10, max_depth=3) -> List[Dict[str, Any]]:
        """
        Get the largest directories in a given path.
        This is an expensive operation and should be used sparingly.
        
        Args:
            path: The path to scan
            limit: Maximum number of directories to return
            max_depth: Maximum directory depth to scan
            
        Returns:
            List of dictionaries containing directory information
        """
        try:
            # This is a CPU-intensive operation, run it in a separate thread
            return await asyncio.to_thread(self._get_largest_directories_sync, path, limit, max_depth)
        except Exception as e:
            self.logger.error(f"Error getting largest directories: {str(e)}")
            return []
    
    def _get_largest_directories_sync(self, path='/', limit=10, max_depth=3) -> List[Dict[str, Any]]:
        """Synchronous implementation of get_largest_directories"""
        result = []
        
        try:
            # Check if path exists and is accessible
            if not os.path.exists(path) or not os.path.isdir(path):
                return result
                
            # Walk the directory tree
            for root, dirs, files in os.walk(path, topdown=True):
                # Check depth
                depth = root[len(path):].count(os.sep)
                if depth > max_depth:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                # Calculate directory size
                dir_size = 0
                file_count = 0
                try:
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            dir_size += os.path.getsize(file_path)
                            file_count += 1
                except (PermissionError, FileNotFoundError):
                    continue
                
                # Add to result
                if dir_size > 0:
                    result.append({
                        'path': root,
                        'size': dir_size,
                        'size_mb': dir_size / (1024 * 1024),
                        'file_count': file_count
                    })
            
            # Sort by size and limit results
            result = sorted(result, key=lambda x: x['size'], reverse=True)[:limit]
            return result
            
        except Exception as e:
            self.logger.error(f"Error in _get_largest_directories_sync: {str(e)}")
            return []


# Test function to run the service directly
async def test_simplified_disk_service():
    """Test the simplified disk service"""
    print("\n" + "="*60)
    print(" SIMPLIFIED DISK SERVICE TEST")
    print("="*60)
    
    # Get timestamp
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = await SimplifiedDiskService.get_instance()
    print(f"Service instance: {service}")
    
    # Get metrics
    metrics = await service.get_metrics()
    print("\nDisk Metrics:")
    print(f"Overall Disk Usage: {metrics['data']['percent']}%")
    print(f"Total Disk Space: {metrics['data']['total'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Used Disk Space: {metrics['data']['used'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Free Disk Space: {metrics['data']['free'] / (1024 * 1024 * 1024):.2f} GB")
    print(f"Read Rate: {metrics['data']['read_rate'] / (1024 * 1024):.2f} MB/s")
    print(f"Write Rate: {metrics['data']['write_rate'] / (1024 * 1024):.2f} MB/s")
    
    print("\nDisk Partitions:")
    for part in metrics['data']['partitions']:
        print(f"  {part['device']} mounted on {part['mountpoint']} ({part['fstype']})")
        print(f"    {part['used'] / (1024 * 1024 * 1024):.2f} GB used of {part['total'] / (1024 * 1024 * 1024):.2f} GB ({part['percent']}%)")
    
    print("\nDisk I/O Counters:")
    for disk, counters in list(metrics['data']['io_counters'].items())[:3]:  # Show first 3
        print(f"  {disk}:")
        print(f"    Read: {counters['read_bytes'] / (1024 * 1024):.2f} MB in {counters['read_count']} operations")
        print(f"    Write: {counters['write_bytes'] / (1024 * 1024):.2f} MB in {counters['write_count']} operations")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_simplified_disk_service())
