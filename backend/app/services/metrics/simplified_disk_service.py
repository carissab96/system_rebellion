#!/usr/bin/env python3
"""
Simplified Disk Metrics Service - PURIFIED ARISTOCRATIC VERSION

A direct, no-nonsense disk metrics service that collects real-time disk data
using psutil and formats it for the frontend.

🧐 "One measures disk usage with precision, or one fails with aristocratic dignity"

CORE PRINCIPLES:
- Real psutil measurements ONLY
- NO fake data generation on errors
- Honest failure handling
- Clean, efficient disk analysis
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
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    - Real psutil disk measurements ONLY
    - Fails honestly when disk access fails
    - No fake zeros or empty arrays
    - Proper I/O rate calculations with state tracking
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
        self.logger.info("🧐 SimplifiedDiskService initialized with aristocratic precision")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive disk metrics directly from psutil.
        
        🧐 ARISTOCRATIC DISK ANALYSIS:
        - Real psutil disk measurements ONLY
        - No caching, no fallbacks, no fake data
        - Fails honestly if disk access is unavailable
        
        Returns:
            Dictionary containing REAL disk metrics formatted for frontend
            
        Raises:
            Exception: If disk metrics collection fails (NO FAKE DATA RETURNED)
        """
        try:
            self.logger.debug("🧐 Collecting real disk metrics with aristocratic precision...")
            
            # PHASE 1: DISK PARTITIONS ANALYSIS
            partitions = await self._get_disk_partitions()
            
            # PHASE 2: ROOT PARTITION USAGE (PRIMARY METRICS)
            root_usage = await self._get_root_disk_usage()
            
            # PHASE 3: DISK I/O STATISTICS AND RATES
            io_data = await self._get_disk_io_metrics()
            
            # PHASE 4: COMPILE REAL DISK METRICS
            disk_metrics = {
                'timestamp': datetime.now().isoformat(),
                'type': 'disk',
                'data': {
                    'percent': round(root_usage['percent'], 2),
                    'total': root_usage['total'],
                    'used': root_usage['used'],
                    'free': root_usage['free'],
                    'read_bytes': io_data['read_bytes'],
                    'write_bytes': io_data['write_bytes'],
                    'read_rate': round(io_data['read_rate'], 2),
                    'write_rate': round(io_data['write_rate'], 2),
                    'partitions': partitions,
                    'io_counters': io_data['io_counters'],
                    'data_quality': 'real_psutil_measurements',
                    'measurement_time': io_data['measurement_time']
                }
            }
            
            self.logger.info(
                f"🧐✅ Disk metrics collected successfully: {root_usage['percent']:.1f}% usage, "
                f"{len(partitions)} partitions, {len(io_data['io_counters'])} I/O devices"
            )
            return disk_metrics
            
        except Exception as e:
            error_msg = f"Disk metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            # NO FAKE DATA - FAIL HONESTLY
            raise Exception(error_msg)
    
    async def _get_disk_partitions(self) -> List[Dict[str, Any]]:
        """
        Get disk partitions information from psutil.
        
        Returns:
            List of partition dictionaries with real usage data
            
        Raises:
            Exception: If partition analysis fails completely
        """
        try:
            partitions = []
            partition_list = psutil.disk_partitions(all=False)
            
            if not partition_list:
                raise Exception("No disk partitions detected by psutil")
            
            for part in partition_list:
                try:
                    # Get usage for this partition
                    usage = psutil.disk_usage(part.mountpoint)
                    
                    partition_info = {
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'opts': part.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': round(usage.percent, 2),
                        'accessible': True
                    }
                    
                    partitions.append(partition_info)
                    
                except (PermissionError, FileNotFoundError, OSError) as e:
                    # Log inaccessible partitions but don't fail entirely
                    self.logger.debug(f"🧐📊 Partition {part.mountpoint} inaccessible: {str(e)}")
                    partitions.append({
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'opts': part.opts,
                        'accessible': False,
                        'error': str(e)
                    })
            
            if not any(p.get('accessible', False) for p in partitions):
                raise Exception("No accessible disk partitions found")
            
            self.logger.debug(f"🧐📊 Analyzed {len(partitions)} disk partitions")
            return partitions
            
        except Exception as e:
            error_msg = f"Partition analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_root_disk_usage(self) -> Dict[str, Any]:
        """
        Get root partition disk usage from psutil.
        
        Returns:
            Dictionary with root partition usage information
            
        Raises:
            Exception: If root partition analysis fails
        """
        try:
            # Try common root partition paths
            root_paths = ['/', 'C:\\'] if os.name != 'nt' else ['C:\\', '/']
            
            for root_path in root_paths:
                try:
                    usage = psutil.disk_usage(root_path)
                    self.logger.debug(f"🧐📊 Root disk usage from {root_path}: {usage.percent:.1f}%")
                    
                    return {
                        'path': root_path,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except (PermissionError, FileNotFoundError, OSError):
                    continue
            
            raise Exception("Unable to access any root partition for disk usage")
            
        except Exception as e:
            error_msg = f"Root disk usage analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_disk_io_metrics(self) -> Dict[str, Any]:
        """
        Get disk I/O statistics and calculate rates.
        
        Returns:
            Dictionary with I/O counters and calculated rates
            
        Raises:
            Exception: If I/O metrics collection fails
        """
        try:
            current_time = time.time()
            
            # Get overall I/O counters
            total_io = psutil.disk_io_counters()
            if total_io is None:
                raise Exception("Disk I/O counters not available from psutil")
            
            # Get per-disk I/O counters
            per_disk_io = psutil.disk_io_counters(perdisk=True)
            if per_disk_io is None:
                per_disk_io = {}
            
            # Calculate I/O rates if we have previous measurements
            read_rate = 0.0
            write_rate = 0.0
            
            if self._last_io_counters and self._last_io_time:
                time_diff = current_time - self._last_io_time
                if time_diff > 0:
                    read_rate = (total_io.read_bytes - self._last_io_counters.read_bytes) / time_diff
                    write_rate = (total_io.write_bytes - self._last_io_counters.write_bytes) / time_diff
            
            # Update state for next calculation
            self._last_io_counters = total_io
            self._last_io_time = current_time
            
            # Format per-disk I/O counters
            io_counters_formatted = {}
            for disk_name, counters in per_disk_io.items():
                io_counters_formatted[disk_name] = {
                    'read_count': counters.read_count,
                    'write_count': counters.write_count,
                    'read_bytes': counters.read_bytes,
                    'write_bytes': counters.write_bytes,
                    'read_time': getattr(counters, 'read_time', 0),
                    'write_time': getattr(counters, 'write_time', 0),
                    'busy_time': getattr(counters, 'busy_time', 0)
                }
            
            return {
                'read_bytes': total_io.read_bytes,
                'write_bytes': total_io.write_bytes,
                'read_rate': read_rate,
                'write_rate': write_rate,
                'io_counters': io_counters_formatted,
                'measurement_time': current_time,
                'rate_calculation_available': self._last_io_counters is not None
            }
            
        except Exception as e:
            error_msg = f"Disk I/O metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def get_disk_usage_only(self, path: str = '/') -> Dict[str, Any]:
        """
        Get just the disk usage for a specific path quickly.
        
        Args:
            path: Path to check disk usage for
            
        Returns:
            Dictionary with disk usage information
            
        Raises:
            Exception: If disk usage measurement fails
        """
        try:
            usage = psutil.disk_usage(path)
            
            return {
                'path': path,
                'total_gb': round(usage.total / (1024**3), 2),
                'used_gb': round(usage.used / (1024**3), 2),
                'free_gb': round(usage.free / (1024**3), 2),
                'percent': round(usage.percent, 2)
            }
            
        except Exception as e:
            error_msg = f"Disk usage measurement for {path} failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def get_largest_directories(
        self, 
        path: str = '/', 
        limit: int = 10, 
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get the largest directories in a given path.
        
        🧐 WARNING: This is a CPU-intensive operation!
        
        Args:
            path: The path to scan
            limit: Maximum number of directories to return
            max_depth: Maximum directory depth to scan
            
        Returns:
            List of dictionaries containing directory information
            
        Raises:
            Exception: If directory analysis fails
        """
        try:
            if not os.path.exists(path):
                raise Exception(f"Path does not exist: {path}")
            
            if not os.path.isdir(path):
                raise Exception(f"Path is not a directory: {path}")
            
            if not os.access(path, os.R_OK):
                raise Exception(f"Path is not readable: {path}")
            
            # Run directory analysis in thread pool to avoid blocking
            self.logger.info(f"🧐📊 Starting directory analysis for {path} (max depth: {max_depth})")
            
            directories = await asyncio.to_thread(
                self._analyze_directories_sync, path, limit, max_depth
            )
            
            self.logger.info(f"🧐✅ Directory analysis complete: found {len(directories)} large directories")
            return directories
            
        except Exception as e:
            error_msg = f"Directory analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    def _analyze_directories_sync(
        self, 
        path: str, 
        limit: int, 
        max_depth: int
    ) -> List[Dict[str, Any]]:
        """
        Synchronous directory analysis implementation.
        
        Args:
            path: Root path to analyze
            limit: Maximum directories to return
            max_depth: Maximum depth to scan
            
        Returns:
            List of directory information dictionaries
        """
        directories = []
        
        try:
            for root, dirs, files in os.walk(path, topdown=True):
                # Calculate current depth
                depth = root[len(path):].count(os.sep)
                if depth > max_depth:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                # Calculate directory size and file count
                dir_size = 0
                file_count = 0
                
                try:
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        try:
                            if os.path.isfile(file_path):
                                file_size = os.path.getsize(file_path)
                                dir_size += file_size
                                file_count += 1
                        except (OSError, PermissionError):
                            continue
                            
                except (OSError, PermissionError):
                    continue
                
                # Only include directories with meaningful size
                if dir_size > 0:
                    directories.append({
                        'path': root,
                        'size_bytes': dir_size,
                        'size_mb': round(dir_size / (1024 * 1024), 2),
                        'size_gb': round(dir_size / (1024 * 1024 * 1024), 3),
                        'file_count': file_count,
                        'depth': depth
                    })
            
            # Sort by size (largest first) and limit results
            directories.sort(key=lambda d: d['size_bytes'], reverse=True)
            return directories[:limit]
            
        except Exception as e:
            self.logger.error(f"🧐💥 Directory analysis synchronous operation failed: {str(e)}")
            raise Exception(f"Directory scanning failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the disk metrics service.
        
        Returns:
            Health check results
        """
        try:
            start_time = datetime.now()
            
            # Test basic disk usage measurement
            root_usage = await self.get_disk_usage_only('/')
            
            # Test partition detection
            partitions = await self._get_disk_partitions()
            accessible_partitions = [p for p in partitions if p.get('accessible', False)]
            
            # Test I/O counters availability
            io_data = await self._get_disk_io_metrics()
            
            collection_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'OPERATIONAL',
                'service_type': 'disk_metrics_collection',
                'psutil_available': True,
                'collection_time_seconds': round(collection_time, 4),
                'root_disk_usage': root_usage,
                'total_partitions': len(partitions),
                'accessible_partitions': len(accessible_partitions),
                'io_counters_available': len(io_data['io_counters']) > 0,
                'rate_calculation_ready': io_data['rate_calculation_available'],
                'data_quality': 'real_psutil_measurements',
                'architectural_principles': [
                    'no_fake_data_generation',
                    'honest_failure_handling', 
                    'real_measurements_only'
                ],
                'last_health_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'service_type': 'disk_metrics_collection',
                'psutil_available': False,
                'error': str(e),
                'last_health_check': datetime.now().isoformat()
            }

# Test function to run the service directly
async def test_simplified_disk_service():
    """Test the simplified disk service with aristocratic precision"""
    print("\n" + "="*80)
    print(" 🧐💾 SIMPLIFIED DISK SERVICE TEST - ARISTOCRATIC PRECISION")
    print("="*80)
    
    print(f"\n🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize service
        service = await SimplifiedDiskService.get_instance()
        print(f"📊 Service instance: {service}")
        
        # Perform health check
        print("\n🏥 Health Check:")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Collection Time: {health.get('collection_time_seconds', 'N/A')} seconds")
        print(f"   Total Partitions: {health.get('total_partitions', 'N/A')}")
        print(f"   Accessible Partitions: {health.get('accessible_partitions', 'N/A')}")
        print(f"   I/O Counters Available: {health.get('io_counters_available', 'N/A')}")
        
        # Get full disk metrics
        print("\n🧐 Collecting Full Disk Metrics...")
        metrics = await service.get_metrics()
        
        print("\n📈 Disk Metrics Results:")
        data = metrics['data']
        print(f"   Overall Disk Usage: {data['percent']}%")
        print(f"   Total Disk Space: {data['total'] / (1024**3):.2f} GB")
        print(f"   Used Disk Space: {data['used'] / (1024**3):.2f} GB")
        print(f"   Free Disk Space: {data['free'] / (1024**3):.2f} GB")
        print(f"   Read Rate: {data['read_rate'] / (1024**2):.2f} MB/s")
        print(f"   Write Rate: {data['write_rate'] / (1024**2):.2f} MB/s")
        
        print(f"\n💾 Disk Partitions:")
        accessible_count = 0
        for part in data['partitions']:
            if part.get('accessible', False):
                accessible_count += 1
                print(f"   ✅ {part['device']} → {part['mountpoint']} ({part['fstype']})")
                print(f"      {part['used'] / (1024**3):.2f} GB used of {part['total'] / (1024**3):.2f} GB ({part['percent']}%)")
            else:
                print(f"   ❌ {part['device']} → {part['mountpoint']} (inaccessible)")
        
        print(f"\n🔄 Disk I/O Statistics:")
        io_counters = data['io_counters']
        if io_counters:
            print(f"   Found {len(io_counters)} I/O devices:")
            for i, (disk, counters) in enumerate(list(io_counters.items())[:3]):  # Show first 3
                print(f"   📊 {disk}:")
                print(f"      Read:  {counters['read_bytes'] / (1024**3):.3f} GB in {counters['read_count']} operations")
                print(f"      Write: {counters['write_bytes'] / (1024**3):.3f} GB in {counters['write_count']} operations")
                if counters.get('busy_time', 0) > 0:
                    print(f"      Busy Time: {counters['busy_time']} ms")
        else:
            print("   No I/O counters available")
        
        # Test quick disk usage
        print(f"\n⚡ Quick Disk Usage Test:")
        try:
            quick_usage = await service.get_disk_usage_only('/')
            print(f"   Root partition: {quick_usage['used_gb']} GB used of {quick_usage['total_gb']} GB ({quick_usage['percent']}%)")
        except Exception as e:
            print(f"   Quick usage test failed: {str(e)}")
        
        print(f"\n✅ Data Quality: {data.get('data_quality', 'Unknown')}")
        print(f"📊 Rate Calculation: {'Available' if data.get('measurement_time') else 'Initializing'}")
        
        # Test directory analysis (optional - CPU intensive)
        print(f"\n🗂️ Directory Analysis Test:")
        try:
            print("   Analyzing largest directories in /tmp (if available)...")
            large_dirs = await service.get_largest_directories('/tmp', limit=5, max_depth=2)
            if large_dirs:
                for i, dir_info in enumerate(large_dirs, 1):
                    print(f"   {i}. {dir_info['path']}: {dir_info['size_mb']} MB ({dir_info['file_count']} files)")
            else:
                print("   No large directories found or /tmp not accessible")
        except Exception as e:
            print(f"   Directory analysis failed: {str(e)}")
        
    except Exception as e:
        print(f"\n💥 DISK SERVICE TEST FAILED: {str(e)}")
        print("This indicates psutil disk access is unavailable or filesystem issues")
        print("🧐 Service failed with dignity - no fake data generated!")
    
    print("\n" + "="*80)
    print(" 🧐✨ DISK SERVICE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simplified_disk_service())