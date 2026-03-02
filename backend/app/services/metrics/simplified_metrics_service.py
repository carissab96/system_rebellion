"""
Simplified Metrics Service

A direct, no-nonsense metrics service that combines all individual metrics services
and provides a unified interface for the WebSocket route. No complex layers, no caching
issues, just pure data routed through Sir Hawkington's Triage Engine.

🧐 "One does not simply collect metrics - one triages them with aristocratic precision"
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.core.resilience import get_circuit_breaker

from app.services.metrics.simplified_cpu_service import SimplifiedCPUService
from app.services.metrics.simplified_memory_service import SimplifiedMemoryService
from app.services.metrics.simplified_disk_service import SimplifiedDiskService
from app.services.metrics.simplified_network_service import SimplifiedNetworkService

UTC = timezone.utc

# def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
#     """Convert datetime to ISO format string"""
#     return dt.isoformat() if dt else None

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)
class SimplifiedMetricsService:
    """
    Simplified metrics service that combines all individual metrics services.
    No complex layers or transformations, just real data routed through triage.
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    Raw Metrics → Sir Hawkington's Triage Engine → Enhanced Metrics → WebSocket
    """
    
    _instance = None
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedMetricsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.logger = logging.getLogger('SimplifiedMetricsService')
            self.logger.info("🧐 SimplifiedMetricsService initialized - Ready for aristocratic triage")
    
        # Circuit breakers for individual metrics services
        self.cpu_circuit_breaker = get_circuit_breaker(
            name="simplified_cpu_metrics", 
            max_failures=3,
            reset_timeout=15,
            exponential_backoff_factor=1.5
        )
        self.memory_circuit_breaker = get_circuit_breaker(
            name="simplified_memory_metrics", 
            max_failures=3,
            reset_timeout=15,
            exponential_backoff_factor=1.5
        )
        self.disk_circuit_breaker = get_circuit_breaker(
            name="simplified_disk_metrics", 
            max_failures=3,
            reset_timeout=15,
            exponential_backoff_factor=1.5
        )
        self.network_circuit_breaker = get_circuit_breaker(
            name="simplified_network_metrics", 
            max_failures=3,
            reset_timeout=15,
            exponential_backoff_factor=1.5
        )   

    def reset_circuit_breakers(self):
        """Reset all circuit breakers"""
        self.cpu_circuit_breaker.reset()
        self.memory_circuit_breaker.reset()
        self.disk_circuit_breaker.reset()
        self.network_circuit_breaker.reset()
        self.logger.info("🧐 All circuit breakers reset with aristocratic precision")

    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def _get_lock(self):
        """Get or create the async lock"""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
    
    async def _safe_get_metrics(self, service, circuit_breaker, service_name):
        """ 
        Safely get metrics from a service with circuit breaker protection
        
        Args:
            service: The metrics service to call
            circuit_breaker: The circuit breaker for this service
            service_name: Name of the service for logging
        
        Returns:
            Dictionary with metrics data or raises exception on error
        """
        # Check if circuit breaker allows the call
        if not circuit_breaker.can_attempt_connection():
            error_msg = f"{service_name} circuit breaker is open"
            self.logger.warning(f"🧐⚠️ {error_msg}")
            raise Exception(error_msg)
    
        try:
            metrics = await service.get_metrics()
            # Record success in circuit breaker
            circuit_breaker.record_success()
            return metrics
        except Exception as e:
            # Record failure in circuit breaker
            circuit_breaker.record_failure()
            error_msg = f"Error collecting {service_name} metrics: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
        
    async def get_cpu_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get CPU metrics only"""
        cpu_service = await SimplifiedCPUService.get_instance()
        result = await self._safe_get_metrics(cpu_service, self.cpu_circuit_breaker, "CPU")
        return result.get('data', {})

    async def get_memory_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get memory metrics only"""
        memory_service = await SimplifiedMemoryService.get_instance()
        result = await self._safe_get_metrics(memory_service, self.memory_circuit_breaker, "Memory")
        return result.get('data', {})

    async def get_disk_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get disk metrics only"""
        disk_service = await SimplifiedDiskService.get_instance()
        result = await self._safe_get_metrics(disk_service, self.disk_circuit_breaker, "Disk")
        return result.get('data', {})

    async def get_network_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """Get network metrics only"""
        network_service = await SimplifiedNetworkService.get_instance()
        result = await self._safe_get_metrics(network_service, self.network_circuit_breaker, "Network")
        return result.get('data', {})
    
    async def get_metrics(self, force_refresh=False) -> Dict[str, Any]:
        """
        Get comprehensive system metrics from all services.
        🧐⚡ ROUTES THROUGH SIR HAWKINGTON'S TRIAGE ENGINE EXCLUSIVELY!
        
        THE ARISTOCRATIC DATA FLOW:
        1. Collect real psutil metrics from all services
        2. Route through Sir Hawkington's Triage Engine
        3. Return enhanced metrics with triage decisions
        4. NO FALLBACKS, NO FAKE DATA, NO LIES!
        
        Args:
            force_refresh: Ignored in this implementation (no caching)
        
        Returns:
            Dictionary containing all system metrics WITH TRIAGE ORCHESTRATION
        """
        try:
            # PHASE 1: COLLECT REAL METRICS FROM ALL SERVICES
            self.logger.info("🧐📊 Collecting real system metrics from all services")
            
            # Create tasks for concurrent execution
            cpu_task = asyncio.create_task(self.get_cpu_metrics(force_refresh))
            memory_task = asyncio.create_task(self.get_memory_metrics(force_refresh))
            disk_task = asyncio.create_task(self.get_disk_metrics(force_refresh))
            network_task = asyncio.create_task(self.get_network_metrics(force_refresh))
            
            # Wait for all metrics to be collected
            cpu_data, memory_data, disk_data, network_data = await asyncio.gather(
                cpu_task, memory_task, disk_task, network_task
            )
            
            # PHASE 2: COMPILE RAW METRICS
            # Poll auth failure monitor for real failed_auth_attempts count
            from app.services.auth_failure_monitor import get_auth_failure_monitor
            auth_monitor = get_auth_failure_monitor()
            await auth_monitor.poll()
            failed_auth_count = auth_monitor.get_failed_auth_count()

            raw_metrics = {
                'timestamp': utc_now().isoformat(),
                'cpu_usage': cpu_data.get('usage_percent'),
                'memory_usage': memory_data.get('percent'),
                'disk_usage': disk_data.get('percent'),
                'network_sent_rate': network_data.get('sent_rate'),
                'network_recv_rate': network_data.get('recv_rate'),
                'failed_auth_attempts': failed_auth_count,
                'cpu': cpu_data,
                'memory': memory_data,
                'disk': disk_data,
                'network': network_data,
                'process_count': len(cpu_data.get('top_processes', [])),
                'system_info': {
                    'hostname': network_data.get('hostname'),
                    'physical_cores': cpu_data.get('physical_cores'),
                    'logical_cores': cpu_data.get('logical_cores'),
                    'total_memory': memory_data.get('total'),
                    'total_disk': disk_data.get('total')
                }
            }
            
            self.logger.info(f"🧐✅ Raw metrics collected successfully: CPU {raw_metrics['cpu_usage']}%, Memory {raw_metrics['memory_usage']}%")
            
            # HawkingtonAgent is now self-driven via ResourceMonitor — no manual triage push needed
            self.logger.info("🧐✅ Metrics collected — HawkingtonAgent self-triggers via ResourceMonitor")
            return raw_metrics
                
        except Exception as e:
            self.logger.error(f"🧐💥 SYSTEM METRICS COLLECTION FAILURE: {str(e)}")
            # NO FALLBACKS, NO FAKE DATA - FAIL WITH DIGNITY
            raise Exception(f"METRICS COLLECTION SYSTEM FAILURE: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check of the metrics service
        """
        try:
            # Check all circuit breakers
            circuit_breaker_status = {
                'cpu': self.cpu_circuit_breaker.can_attempt_connection(),
                'memory': self.memory_circuit_breaker.can_attempt_connection(),
                'disk': self.disk_circuit_breaker.can_attempt_connection(),
                'network': self.network_circuit_breaker.can_attempt_connection()
            }
            
            # Try a quick metrics collection
            start_time = utc_now()
            try:
                test_metrics = await self.get_metrics()
                collection_time = (utc_now() - start_time).total_seconds()
                metrics_collection_status = 'OPERATIONAL'
                has_triage_data = 'triage_decision' in test_metrics
            except Exception as e:
                collection_time = (utc_now() - start_time).total_seconds()
                metrics_collection_status = f'FAILED: {str(e)}'
                has_triage_data = False
            
            return {
                'service_status': 'OPERATIONAL',
                'metrics_collection': metrics_collection_status,
                'collection_time_seconds': collection_time,
                'circuit_breakers': circuit_breaker_status,
                'triage_integration': has_triage_data,
                'aristocratic_authority': 'MAINTAINED',
                'last_check': utc_now().isoformat()
            }
            
        except Exception as e:
            return {
                'service_status': 'FAILED',
                'error': str(e),
                'last_check': utc_now().isoformat()
            }

# Test function to run the service directly
async def test_simplified_metrics_service():
    """Test the simplified metrics service with triage integration"""
    print("\n" + "="*80)
    print(" 🧐⚡ SIMPLIFIED METRICS SERVICE TEST - ARISTOCRATIC TRIAGE INTEGRATION")
    print("="*80)
    
    # Get timestamp
    print(f"\n🕐 Timestamp: {utc_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize service
    service = await SimplifiedMetricsService.get_instance()
    print(f"📊 Service instance: {service}")
    
    try:
        # Get metrics through triage
        print("\n🧐 Collecting metrics through Sir Hawkington's Triage Engine...")
        metrics = await service.get_metrics()
        
        # Basic metrics overview
        print("\n📈 System Metrics Overview:")
        print(f"   CPU Usage: {metrics.get('cpu_usage', 'N/A')}%")
        print(f"   Memory Usage: {metrics.get('memory_usage', 'N/A')}%")
        print(f"   Disk Usage: {metrics.get('disk_usage', 'N/A')}%")
        
        if metrics.get('network_sent_rate') and metrics.get('network_recv_rate'):
            print(f"   Network Send Rate: {metrics['network_sent_rate'] / 1024:.2f} KB/s")
            print(f"   Network Receive Rate: {metrics['network_recv_rate'] / 1024:.2f} KB/s")
        
        print(f"   Process Count: {metrics.get('process_count', 'N/A')}")
        
        # Triage information
        if 'triage_decision' in metrics:
            triage = metrics['triage_decision']
            print(f"\n🧐 TRIAGE DECISION:")
            print(f"   Severity: {triage.get('severity', 'N/A')}")
            print(f"   Routing: {triage.get('routing', 'N/A')}")
            print(f"   Target Agents: {triage.get('target_agents', [])}")
            print(f"   Monocle Yeeted: {triage.get('monocle_yeeted', 'N/A')}")
            print(f"   Confidence: {triage.get('confidence', 'N/A')}")
        else:
            print("\n⚠️ No triage data found in metrics")
        
        # System info
        if 'system_info' in metrics:
            print(f"\n💻 System Info:")
            system_info = metrics['system_info']
            for key, value in system_info.items():
                if key in ['total_memory', 'total_disk'] and value:
                    print(f"   {key}: {value / (1024 * 1024 * 1024):.2f} GB")
                else:
                    print(f"   {key}: {value}")
        
        # Health check
        print(f"\n🏥 Health Check:")
        health = await service.health_check()
        print(f"   Service Status: {health.get('service_status', 'N/A')}")
        print(f"   Collection Time: {health.get('collection_time_seconds', 'N/A'):.3f}s")
        print(f"   Triage Integration: {health.get('triage_integration', 'N/A')}")
        print(f"   Aristocratic Authority: {health.get('aristocratic_authority', 'N/A')}")
        
    except Exception as e:
        print(f"\n💥 TEST FAILED: {str(e)}")
        print("This indicates the triage engine or metrics collection has failed")
    
    print("\n" + "="*80)
    print(" 🧐✨ SIMPLIFIED METRICS SERVICE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simplified_metrics_service())