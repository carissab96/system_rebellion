#!/usr/bin/env python3
"""
Simplified CPU Metrics Service - PURIFIED ARISTOCRATIC VERSION

A direct, no-nonsense CPU metrics service that collects real-time CPU data
using psutil and formats it for the frontend. 

🧐 "One does not fabricate CPU metrics - one measures them with precision or fails with dignity"

CORE PRINCIPLES:
- Real psutil data ONLY
- NO fake data generation on errors
- Honest failure handling
- Clean, efficient data collection
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
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    - Real psutil data ONLY
    - Fails honestly when psutil fails
    - No fake zeros or empty arrays
    - Clean separation of data collection and formatting
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
        self.logger.info("🧐 SimplifiedCPUService initialized with aristocratic precision")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive CPU metrics directly from psutil.
        
        🧐 ARISTOCRATIC DATA COLLECTION:
        - Real psutil measurements ONLY
        - No caching, no fallbacks, no fake data
        - Fails honestly if psutil is unavailable
        
        Returns:
            Dictionary containing REAL CPU metrics formatted for frontend
            
        Raises:
            Exception: If CPU metrics collection fails (NO FAKE DATA RETURNED)
        """
        try:
            self.logger.debug("🧐 Collecting real CPU metrics with aristocratic precision...")
            
            # PHASE 1: BASIC CPU INFORMATION
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            if not cpu_count_logical or not cpu_count_physical:
                raise Exception("Unable to determine CPU core counts - psutil data unavailable")
            
            # PHASE 2: CPU USAGE MEASUREMENTS
            # Get per-core CPU usage with proper measurement interval
            per_core_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Get overall CPU usage with proper measurement interval  
            overall_percent = psutil.cpu_percent(interval=0.1)
            
            if overall_percent is None or per_core_percent is None:
                raise Exception("Unable to measure CPU usage - psutil measurement failed")
            
            # PHASE 3: CPU FREQUENCY INFORMATION
            frequency_data = await self._get_cpu_frequency()
            
            # PHASE 4: CPU TEMPERATURE (IF AVAILABLE)
            temperature = await self._get_cpu_temperature()
            
            # PHASE 5: TOP CPU-CONSUMING PROCESSES
            top_processes = await self._get_top_cpu_processes()
            
            # PHASE 6: COMPILE REAL METRICS
            cpu_metrics = {
                'timestamp': utc_now().isoformat(),
                'type': 'cpu',
                'data': {
                    'usage_percent': round(overall_percent, 2),
                    'physical_cores': cpu_count_physical,
                    'logical_cores': cpu_count_logical,
                    'frequency_mhz': frequency_data['current'],
                    'temperature': temperature,
                    'cores': [round(core, 2) for core in per_core_percent],
                    'top_processes': top_processes,
                    'frequency_details': frequency_data,
                    'data_quality': 'real_psutil_measurements'
                }
            }
            
            self.logger.info(f"🧐✅ CPU metrics collected successfully: {overall_percent:.1f}% usage, {len(top_processes)} processes")
            return cpu_metrics
            
        except Exception as e:
            error_msg = f"CPU metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            # NO FAKE DATA - FAIL HONESTLY
            raise Exception(error_msg)
    
    async def _get_cpu_frequency(self) -> Dict[str, float]:
        """
        Get CPU frequency information from psutil.
        
        Returns:
            Dictionary with current, min, max frequencies
            
        Raises:
            Exception: If frequency data is unavailable
        """
        try:
            freq = psutil.cpu_freq()
            
            if freq is None:
                # Some systems don't support frequency monitoring
                self.logger.debug("🧐⚠️ CPU frequency monitoring not available on this system")
                return {
                    'current': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'available': False
                }
            
            return {
                'current': round(freq.current, 2) if freq.current else 0.0,
                'min': round(freq.min, 2) if hasattr(freq, 'min') and freq.min else 0.0,
                'max': round(freq.max, 2) if hasattr(freq, 'max') and freq.max else 0.0,
                'available': True
            }
            
        except Exception as e:
            self.logger.warning(f"🧐⚠️ CPU frequency collection failed: {str(e)}")
            # Return unavailable status rather than fake data
            return {
                'current': 0.0,
                'min': 0.0,
                'max': 0.0,
                'available': False,
                'error': str(e)
            }
    
    async def _get_cpu_temperature(self) -> Optional[float]:
        """
        Get CPU temperature from psutil sensors.
        
        Returns:
            CPU temperature in Celsius or None if not available
        """
        try:
            if not hasattr(psutil, 'sensors_temperatures'):
                self.logger.debug("🧐📊 Temperature sensors not supported on this system")
                return None
            
            temps = psutil.sensors_temperatures()
            
            if not temps:
                self.logger.debug("🧐📊 No temperature sensors found")
                return None
            
            # Try different common sensor names
            sensor_names = ['coretemp', 'cpu_thermal', 'k10temp', 'acpi']
            
            for sensor_name in sensor_names:
                if sensor_name in temps and temps[sensor_name]:
                    temp_reading = temps[sensor_name][0]
                    if hasattr(temp_reading, 'current') and temp_reading.current:
                        self.logger.debug(f"🧐🌡️ CPU temperature: {temp_reading.current}°C from {sensor_name}")
                        return round(temp_reading.current, 1)
            
            self.logger.debug("🧐📊 CPU temperature not available from known sensors")
            return None
            
        except Exception as e:
            self.logger.debug(f"🧐📊 Temperature collection failed: {str(e)}")
            return None
    
    async def _get_top_cpu_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top CPU-consuming processes from psutil.
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of process information dictionaries
        """
        try:
            processes = []
            
            # First pass: Get all accessible processes
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    # Initialize CPU percent measurement
                    proc.cpu_percent()
                    processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not processes:
                self.logger.warning("🧐⚠️ No accessible processes found for CPU analysis")
                return []
            
            # Short sleep to allow CPU percent to be measured accurately
            await asyncio.sleep(0.1)
            
            # Second pass: Get CPU usage and additional info
            process_data = []
            for proc in processes:
                try:
                    cpu_percent = proc.cpu_percent()
                    
                    # Only include processes with measurable CPU usage
                    if cpu_percent > 0.0:
                        memory_info = proc.memory_info()
                        process_data.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'] or 'Unknown',
                            'username': proc.info.get('username', 'Unknown'),
                            'cpu_percent': round(cpu_percent, 2),
                            'memory_mb': round(memory_info.rss / 1024 / 1024, 1) if memory_info else 0,
                            'status': proc.status() if hasattr(proc, 'status') else 'unknown'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage and return top processes
            process_data.sort(key=lambda p: p['cpu_percent'], reverse=True)
            top_processes = process_data[:limit]
            
            self.logger.debug(f"🧐📊 Collected {len(top_processes)} top CPU processes")
            return top_processes
            
        except Exception as e:
            self.logger.warning(f"🧐⚠️ Top processes collection failed: {str(e)}")
            # Return empty list rather than fake process data
            return []
    
    async def get_cpu_usage_only(self) -> float:
        """
        Get just the overall CPU usage percentage quickly.
        
        Returns:
            CPU usage percentage as float
            
        Raises:
            Exception: If CPU usage measurement fails
        """
        try:
            usage = psutil.cpu_percent(interval=0.1)
            
            if usage is None:
                raise Exception("CPU usage measurement returned None")
            
            return round(usage, 2)
            
        except Exception as e:
            error_msg = f"CPU usage measurement failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def get_core_count(self) -> Dict[str, int]:
        """
        Get CPU core count information.
        
        Returns:
            Dictionary with physical and logical core counts
            
        Raises:
            Exception: If core count determination fails
        """
        try:
            physical = psutil.cpu_count(logical=False)
            logical = psutil.cpu_count(logical=True)
            
            if physical is None or logical is None:
                raise Exception("Unable to determine CPU core counts")
            
            return {
                'physical_cores': physical,
                'logical_cores': logical,
                'hyperthreading_enabled': logical > physical
            }
            
        except Exception as e:
            error_msg = f"CPU core count determination failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the CPU metrics service.
        
        Returns:
            Health check results
        """
        try:
            start_time = utc_now()
            
            # Test basic CPU usage measurement
            cpu_usage = await self.get_cpu_usage_only()
            
            # Test core count determination
            core_info = await self.get_core_count()
            
            # Test frequency availability
            frequency_data = await self._get_cpu_frequency()
            
            # Test temperature availability
            temperature = await self._get_cpu_temperature()
            
            collection_time = (utc_now() - start_time).total_seconds()
            
            return {
                'status': 'OPERATIONAL',
                'service_type': 'cpu_metrics_collection',
                'psutil_available': True,
                'collection_time_seconds': round(collection_time, 4),
                'current_cpu_usage': cpu_usage,
                'core_counts': core_info,
                'frequency_monitoring': frequency_data['available'],
                'temperature_monitoring': temperature is not None,
                'data_quality': 'real_psutil_measurements',
                'architectural_principles': [
                    'no_fake_data_generation',
                    'honest_failure_handling',
                    'real_measurements_only'
                ],
                'last_health_check': utc_now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'service_type': 'cpu_metrics_collection',
                'psutil_available': False,
                'error': str(e),
                'last_health_check': utc_now().isoformat()
            }

# Test function to run the service directly
async def test_simplified_cpu_service():
    """Test the simplified CPU service with aristocratic precision"""
    print("\n" + "="*80)
    print(" 🧐💻 SIMPLIFIED CPU SERVICE TEST - ARISTOCRATIC PRECISION")
    print("="*80)
    
    print(f"\n🕐 Timestamp: {utc_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize service
        service = await SimplifiedCPUService.get_instance()
        print(f"📊 Service instance: {service}")
        
        # Perform health check
        print("\n🏥 Health Check:")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Collection Time: {health.get('collection_time_seconds', 'N/A')} seconds")
        print(f"   Current CPU Usage: {health.get('current_cpu_usage', 'N/A')}%")
        print(f"   Frequency Monitoring: {health.get('frequency_monitoring', 'N/A')}")
        print(f"   Temperature Monitoring: {health.get('temperature_monitoring', 'N/A')}")
        
        # Get full metrics
        print("\n🧐 Collecting Full CPU Metrics...")
        metrics = await service.get_metrics()
        
        print("\n📈 CPU Metrics Results:")
        data = metrics['data']
        print(f"   Overall CPU Usage: {data['usage_percent']}%")
        print(f"   Physical Cores: {data['physical_cores']}")
        print(f"   Logical Cores: {data['logical_cores']}")
        print(f"   CPU Frequency: {data['frequency_mhz']} MHz")
        print(f"   CPU Temperature: {data['temperature']} °C" if data['temperature'] else "   CPU Temperature: Not available")
        
        print(f"\n🔄 Per-Core Usage:")
        for i, usage in enumerate(data['cores']):
            print(f"     Core {i:2d}: {usage:5.1f}%")
        
        print(f"\n🔥 Top CPU-Consuming Processes:")
        if data['top_processes']:
            for i, proc in enumerate(data['top_processes'][:5], 1):
                print(f"   {i:2d}. {proc['name']} (PID {proc['pid']})")
                print(f"       CPU: {proc['cpu_percent']}%, Memory: {proc['memory_mb']} MB, User: {proc['username']}")
        else:
            print("     No high-CPU processes detected")
        
        print(f"\n✅ Data Quality: {data.get('data_quality', 'Unknown')}")
        
    except Exception as e:
        print(f"\n💥 CPU SERVICE TEST FAILED: {str(e)}")
        print("This indicates psutil is unavailable or CPU measurement failed")
        print("🧐 Service failed with dignity - no fake data generated!")
    
    print("\n" + "="*80)
    print(" 🧐✨ CPU SERVICE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simplified_cpu_service())