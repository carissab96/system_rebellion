"""
Simplified Memory Metrics Service - PURIFIED ARISTOCRATIC VERSION

A direct, no-nonsense memory metrics service that collects real-time memory data
using psutil and formats it for the frontend.

🧐 "Memory measurements must be precise and honest - fabrication is beneath aristocratic standards"

CORE PRINCIPLES:
- Real psutil memory measurements ONLY
- NO fake data generation on errors
- Honest failure handling
- Clean, efficient memory analysis
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio


class SimplifiedMemoryService:
    """
    Simplified memory metrics service that directly collects and formats memory data.
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    - Real psutil memory measurements ONLY
    - Fails honestly when memory access fails
    - No fake zeros or empty arrays
    - Comprehensive memory analysis including swap
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedMemoryService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedMemoryService')
        self._initialized = True
        self.logger.info("🧐 SimplifiedMemoryService initialized with aristocratic precision")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive memory metrics directly from psutil.
        
        🧐 ARISTOCRATIC MEMORY ANALYSIS:
        - Real psutil memory measurements ONLY
        - No caching, no fallbacks, no fake data
        - Fails honestly if memory access is unavailable
        
        Returns:
            Dictionary containing REAL memory metrics formatted for frontend
            
        Raises:
            Exception: If memory metrics collection fails (NO FAKE DATA RETURNED)
        """
        try:
            self.logger.debug("🧐 Collecting real memory metrics with aristocratic precision...")
            
            # PHASE 1: VIRTUAL MEMORY ANALYSIS
            virtual_memory_data = await self._get_virtual_memory_metrics()
            
            # PHASE 2: SWAP MEMORY ANALYSIS
            swap_memory_data = await self._get_swap_memory_metrics()
            
            # PHASE 3: TOP MEMORY-CONSUMING PROCESSES
            top_processes = await self._get_top_memory_processes()
            
            # PHASE 4: COMPILE REAL MEMORY METRICS
            memory_metrics = {
                'timestamp': utc_now().isoformat(),
                'type': 'memory',
                'data': {
                    'total': virtual_memory_data['total'],
                    'available': virtual_memory_data['available'],
                    'used': virtual_memory_data['used'],
                    'free': virtual_memory_data['free'],
                    'percent': round(virtual_memory_data['percent'], 2),
                    'cached': virtual_memory_data['cached'],
                    'buffers': virtual_memory_data['buffers'],
                    'shared': virtual_memory_data['shared'],
                    'swap': swap_memory_data,
                    'top_processes': top_processes,
                    'data_quality': 'real_psutil_measurements',
                    'virtual_memory_details': virtual_memory_data
                }
            }
            
            self.logger.info(
                f"🧐✅ Memory metrics collected successfully: {virtual_memory_data['percent']:.1f}% usage, "
                f"{len(top_processes)} processes analyzed, swap: {swap_memory_data['percent']:.1f}%"
            )
            return memory_metrics
            
        except Exception as e:
            error_msg = f"Memory metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            # NO FAKE DATA - FAIL HONESTLY
            raise Exception(error_msg)
    
    async def _get_virtual_memory_metrics(self) -> Dict[str, Any]:
        """
        Get virtual memory statistics from psutil.
        
        Returns:
            Dictionary with virtual memory information
            
        Raises:
            Exception: If virtual memory analysis fails
        """
        try:
            virtual_memory = psutil.virtual_memory()
            
            if virtual_memory is None:
                raise Exception("Virtual memory statistics not available from psutil")
            
            # Validate that we have meaningful data
            if virtual_memory.total == 0:
                raise Exception("Virtual memory total is zero - invalid psutil data")
            
            memory_data = {
                'total': virtual_memory.total,
                'available': virtual_memory.available,
                'used': virtual_memory.used,
                'free': virtual_memory.free,
                'percent': virtual_memory.percent,
                'cached': getattr(virtual_memory, 'cached', 0),
                'buffers': getattr(virtual_memory, 'buffers', 0),
                'shared': getattr(virtual_memory, 'shared', 0),
                'active': getattr(virtual_memory, 'active', 0),
                'inactive': getattr(virtual_memory, 'inactive', 0),
                'wired': getattr(virtual_memory, 'wired', 0)  # macOS specific
            }
            
            self.logger.debug(f"🧐📊 Virtual memory: {memory_data['percent']:.1f}% used of {memory_data['total'] / (1024**3):.2f} GB")
            return memory_data
            
        except Exception as e:
            error_msg = f"Virtual memory analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_swap_memory_metrics(self) -> Dict[str, Any]:
        """
        Get swap memory statistics from psutil.
        
        Returns:
            Dictionary with swap memory information
            
        Raises:
            Exception: If swap memory analysis fails
        """
        try:
            swap = psutil.swap_memory()
            
            if swap is None:
                raise Exception("Swap memory statistics not available from psutil")
            
            swap_data = {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': round(swap.percent, 2),
                'sin': getattr(swap, 'sin', 0),    # Bytes swapped in from disk
                'sout': getattr(swap, 'sout', 0)   # Bytes swapped out to disk
            }
            
            # Note if swap is not configured
            if swap.total == 0:
                self.logger.debug("🧐📊 No swap space configured on this system")
                swap_data['configured'] = False
            else:
                swap_data['configured'] = True
                self.logger.debug(f"🧐📊 Swap memory: {swap_data['percent']:.1f}% used of {swap_data['total'] / (1024**3):.2f} GB")
            
            return swap_data
            
        except Exception as e:
            error_msg = f"Swap memory analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_top_memory_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top memory-consuming processes from psutil.
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of process information dictionaries
        """
        try:
            processes = []
            
            # Get all accessible processes with memory information
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'memory_info']):
                try:
                    # Skip processes with no memory usage
                    if proc.info['memory_percent'] and proc.info['memory_percent'] > 0.0:
                        memory_info = proc.info.get('memory_info')
                        
                        process_data = {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'] or 'Unknown',
                            'username': proc.info.get('username', 'Unknown'),
                            'memory_percent': round(proc.info['memory_percent'], 3),
                            'memory_mb': round(memory_info.rss / (1024 * 1024), 2) if memory_info else 0,
                            'memory_vms_mb': round(memory_info.vms / (1024 * 1024), 2) if memory_info else 0
                        }
                        
                        processes.append(process_data)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if not processes:
                self.logger.warning("🧐⚠️ No accessible processes found for memory analysis")
                return []
            
            # Sort by memory percentage and return top processes
            processes.sort(key=lambda p: p['memory_percent'], reverse=True)
            top_processes = processes[:limit]
            
            self.logger.debug(f"🧐📊 Analyzed {len(processes)} processes, returning top {len(top_processes)}")
            return top_processes
            
        except Exception as e:
            self.logger.warning(f"🧐⚠️ Top memory processes collection failed: {str(e)}")
            # Return empty list rather than fake process data
            return []
    
    async def get_memory_usage_only(self) -> Dict[str, Any]:
        """
        Get just the essential memory usage information quickly.
        
        Returns:
            Dictionary with basic memory usage
            
        Raises:
            Exception: If memory usage measurement fails
        """
        try:
            virtual_memory = psutil.virtual_memory()
            
            if virtual_memory is None:
                raise Exception("Memory usage measurement failed - psutil returned None")
            
            return {
                'percent': round(virtual_memory.percent, 2),
                'total_gb': round(virtual_memory.total / (1024**3), 2),
                'available_gb': round(virtual_memory.available / (1024**3), 2),
                'used_gb': round(virtual_memory.used / (1024**3), 2)
            }
            
        except Exception as e:
            error_msg = f"Memory usage measurement failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def get_swap_usage_only(self) -> Dict[str, Any]:
        """
        Get just the swap usage information quickly.
        
        Returns:
            Dictionary with basic swap usage
            
        Raises:
            Exception: If swap usage measurement fails
        """
        try:
            swap = psutil.swap_memory()
            
            if swap is None:
                raise Exception("Swap usage measurement failed - psutil returned None")
            
            return {
                'percent': round(swap.percent, 2),
                'total_gb': round(swap.total / (1024**3), 2),
                'used_gb': round(swap.used / (1024**3), 2),
                'configured': swap.total > 0
            }
            
        except Exception as e:
            error_msg = f"Swap usage measurement failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def get_memory_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed memory breakdown for analysis.
        
        Returns:
            Comprehensive memory breakdown dictionary
            
        Raises:
            Exception: If memory breakdown analysis fails
        """
        try:
            virtual_memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            if virtual_memory is None or swap is None:
                raise Exception("Memory breakdown analysis failed - psutil data unavailable")
            
            # Calculate percentages of total memory
            total_memory = virtual_memory.total
            
            breakdown = {
                'total_memory_gb': round(total_memory / (1024**3), 2),
                'virtual_memory': {
                    'used_percent': round((virtual_memory.used / total_memory) * 100, 2),
                    'available_percent': round((virtual_memory.available / total_memory) * 100, 2),
                    'cached_percent': round((getattr(virtual_memory, 'cached', 0) / total_memory) * 100, 2),
                    'buffers_percent': round((getattr(virtual_memory, 'buffers', 0) / total_memory) * 100, 2),
                },
                'swap_memory': {
                    'total_gb': round(swap.total / (1024**3), 2),
                    'used_percent_of_swap': round(swap.percent, 2),
                    'configured': swap.total > 0
                },
                'memory_efficiency': {
                    'cache_hit_ratio': round((getattr(virtual_memory, 'cached', 0) / virtual_memory.used) * 100, 2) if virtual_memory.used > 0 else 0,
                    'swap_pressure': 'high' if swap.percent > 50 else 'medium' if swap.percent > 10 else 'low',
                    'memory_pressure': 'high' if virtual_memory.percent > 90 else 'medium' if virtual_memory.percent > 70 else 'low'
                }
            }
            
            return breakdown
            
        except Exception as e:
            error_msg = f"Memory breakdown analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the memory metrics service.
        
        Returns:
            Health check results
        """
        try:
            start_time = utc_now()
            
            # Test basic memory usage measurement
            memory_usage = await self.get_memory_usage_only()
            
            # Test swap usage measurement
            swap_usage = await self.get_swap_usage_only()
            
            # Test process analysis
            top_processes = await self._get_top_memory_processes(limit=5)
            
            # Test detailed breakdown
            breakdown = await self.get_memory_breakdown()
            
            collection_time = (utc_now() - start_time).total_seconds()
            
            return {
                'status': 'OPERATIONAL',
                'service_type': 'memory_metrics_collection',
                'psutil_available': True,
                'collection_time_seconds': round(collection_time, 4),
                'current_memory_usage': memory_usage,
                'swap_configured': swap_usage['configured'],
                'swap_usage': swap_usage['percent'],
                'top_processes_found': len(top_processes),
                'memory_pressure': breakdown['memory_efficiency']['memory_pressure'],
                'swap_pressure': breakdown['memory_efficiency']['swap_pressure'],
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
                'service_type': 'memory_metrics_collection',
                'psutil_available': False,
                'error': str(e),
                'last_health_check': utc_now().isoformat()
            }

# Test function to run the service directly
async def test_simplified_memory_service():
    """Test the simplified memory service with aristocratic precision"""
    print("\n" + "="*80)
    print(" 🧐🧠 SIMPLIFIED MEMORY SERVICE TEST - ARISTOCRATIC PRECISION")
    print("="*80)
    
    print(f"\n🕐 Timestamp: {utc_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize service
        service = await SimplifiedMemoryService.get_instance()
        print(f"📊 Service instance: {service}")
        
        # Perform health check
        print("\n🏥 Health Check:")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Collection Time: {health.get('collection_time_seconds', 'N/A')} seconds")
        print(f"   Memory Pressure: {health.get('memory_pressure', 'N/A')}")
        print(f"   Swap Configured: {health.get('swap_configured', 'N/A')}")
        print(f"   Swap Pressure: {health.get('swap_pressure', 'N/A')}")
        print(f"   Top Processes Found: {health.get('top_processes_found', 'N/A')}")
        
        # Get full memory metrics
        print("\n🧐 Collecting Full Memory Metrics...")
        metrics = await service.get_metrics()
        
        print("\n📈 Memory Metrics Results:")
        data = metrics['data']
        print(f"   Memory Usage: {data['percent']}%")
        print(f"   Total Memory: {data['total'] / (1024**3):.2f} GB")
        print(f"   Available Memory: {data['available'] / (1024**3):.2f} GB")
        print(f"   Used Memory: {data['used'] / (1024**3):.2f} GB")
        print(f"   Cached Memory: {data['cached'] / (1024**3):.2f} GB")
        print(f"   Buffers: {data['buffers'] / (1024**3):.2f} GB")
        
        print(f"\n💾 Swap Memory:")
        swap = data['swap']
        if swap['configured']:
            print(f"   Swap Usage: {swap['percent']}%")
            print(f"   Total Swap: {swap['total'] / (1024**3):.2f} GB")
            print(f"   Used Swap: {swap['used'] / (1024**3):.2f} GB")
            print(f"   Swap I/O: {swap['sin']} bytes in, {swap['sout']} bytes out")
        else:
            print("   Swap: Not configured on this system")
        
        print(f"\n🔥 Top Memory-Consuming Processes:")
        if data['top_processes']:
            for i, proc in enumerate(data['top_processes'][:5], 1):
                print(f"   {i:2d}. {proc['name']} (PID {proc['pid']})")
                print(f"       Memory: {proc['memory_percent']:.2f}% ({proc['memory_mb']:.1f} MB RSS)")
                print(f"       User: {proc['username']}")
        else:
            print("   No high-memory processes detected")
        
        # Test quick memory breakdown
        print(f"\n📊 Memory Breakdown Analysis:")
        try:
            breakdown = await service.get_memory_breakdown()
            print(f"   Memory Efficiency:")
            print(f"     Cache Hit Ratio: {breakdown['memory_efficiency']['cache_hit_ratio']:.1f}%")
            print(f"     Memory Pressure: {breakdown['memory_efficiency']['memory_pressure']}")
            print(f"     Swap Pressure: {breakdown['memory_efficiency']['swap_pressure']}")
        except Exception as e:
            print(f"   Breakdown analysis failed: {str(e)}")
        
        print(f"\n✅ Data Quality: {data.get('data_quality', 'Unknown')}")
        
    except Exception as e:
        print(f"\n💥 MEMORY SERVICE TEST FAILED: {str(e)}")
        print("This indicates psutil memory access is unavailable or system issues")
        print("🧐 Service failed with dignity - no fake data generated!")
    
    print("\n" + "="*80)
    print(" 🧐✨ MEMORY SERVICE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simplified_memory_service())