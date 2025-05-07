"""
Disk Metrics Service

This service is responsible for collecting detailed disk metrics including:
- Overall disk usage by partition
- Disk I/O statistics
- Disk read/write speeds
- Largest directories (optional, as this can be expensive)
"""

import os
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class DiskMetricsService:
    """Service for collecting detailed disk metrics"""
    
    def __init__(self):
        """Initialize the disk metrics service"""
        self.logger = logging.getLogger('DiskMetricsService')
        self._previous_io_counters = None
        self._previous_io_time = None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get detailed disk metrics.
        
        Returns:
            Dictionary containing detailed disk metrics
        """
        try:
            # Get disk partitions
            partitions = self._get_disk_partitions()
            
            # Get disk I/O statistics
            io_stats = self._get_disk_io_stats()
            
            return {
                'partitions': partitions,
                'io_stats': io_stats
            }
        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {str(e)}")
            return {
                'partitions': [],
                'io_stats': {
                    'read_bytes': 0,
                    'write_bytes': 0,
                    'read_count': 0,
                    'write_count': 0,
                    'read_time': 0,
                    'write_time': 0,
                    'read_speed': 0,
                    'write_speed': 0
                }
            }
    
    def _get_disk_partitions(self) -> List[Dict[str, Any]]:
        """Get information about disk partitions"""
        partitions_info = []
        try:
            # Get all disk partitions
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                try:
                    # Skip non-fixed drives on Windows
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    partitions_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except (PermissionError, FileNotFoundError) as e:
                    # Skip partitions that cannot be accessed
                    self.logger.warning(f"Cannot access partition {partition.mountpoint}: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error getting usage for partition {partition.mountpoint}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error getting disk partitions: {str(e)}")
        
        return partitions_info
    
    def _get_disk_io_stats(self) -> Dict[str, Any]:
        """Get disk I/O statistics including read/write speeds"""
        try:
            # Get current disk I/O counters
            io_counters = psutil.disk_io_counters()
            current_time = datetime.now().timestamp()
            
            # Initialize with default values
            io_stats = {
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes,
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
                'read_time': getattr(io_counters, 'read_time', 0),
                'write_time': getattr(io_counters, 'write_time', 0),
                'read_speed': 0,  # bytes per second
                'write_speed': 0  # bytes per second
            }
            
            # Calculate read/write speeds if we have previous measurements
            if self._previous_io_counters and self._previous_io_time:
                time_diff = current_time - self._previous_io_time
                
                if time_diff > 0:
                    # Calculate read speed in bytes per second
                    read_bytes_diff = io_counters.read_bytes - self._previous_io_counters.read_bytes
                    if read_bytes_diff >= 0:  # Ensure non-negative value
                        io_stats['read_speed'] = read_bytes_diff / time_diff
                    
                    # Calculate write speed in bytes per second
                    write_bytes_diff = io_counters.write_bytes - self._previous_io_counters.write_bytes
                    if write_bytes_diff >= 0:  # Ensure non-negative value
                        io_stats['write_speed'] = write_bytes_diff / time_diff
            
            # Store current values for next calculation
            self._previous_io_counters = io_counters
            self._previous_io_time = current_time
            
            return io_stats
        except Exception as e:
            self.logger.error(f"Error getting disk I/O stats: {str(e)}")
            return {
                'read_bytes': 0,
                'write_bytes': 0,
                'read_count': 0,
                'write_count': 0,
                'read_time': 0,
                'write_time': 0,
                'read_speed': 0,
                'write_speed': 0
            }
    
    def get_largest_directories(self, path: str = '/', limit: int = 10, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Get the largest directories under the specified path.
        Note: This can be an expensive operation and should be used cautiously.
        
        Args:
            path: The starting directory path
            limit: Maximum number of directories to return
            max_depth: Maximum directory depth to scan
            
        Returns:
            List of dictionaries containing directory information
        """
        # This is a separate method that can be called explicitly when needed
        # rather than including it in the regular metrics collection
        largest_dirs = []
        
        try:
            dir_sizes = []
            
            # Walk through directories up to max_depth
            for root, dirs, files in os.walk(path):
                # Check depth
                depth = root.count(os.sep) - path.count(os.sep)
                if depth > max_depth:
                    dirs.clear()  # Don't go deeper
                    continue
                
                # Calculate directory size
                dir_size = sum(os.path.getsize(os.path.join(root, f)) for f in files if os.path.isfile(os.path.join(root, f)))
                
                dir_sizes.append({
                    'path': root,
                    'size': dir_size
                })
            
            # Sort by size (descending) and take top N
            largest_dirs = sorted(dir_sizes, key=lambda x: x['size'], reverse=True)[:limit]
            
            # Add human-readable size
            for dir_info in largest_dirs:
                dir_info['size_human'] = self._format_bytes(dir_info['size'])
        
        except Exception as e:
            self.logger.error(f"Error getting largest directories: {str(e)}")
        
        return largest_dirs
    
    def _format_bytes(self, size: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size < 1024 or unit == 'PB':
                return f"{size:.2f} {unit}"
            size /= 1024
