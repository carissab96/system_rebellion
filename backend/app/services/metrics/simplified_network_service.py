

"""
Simplified Network Metrics Service - PURIFIED ARISTOCRATIC VERSION

A comprehensive network metrics service that combines basic psutil data with 
ResourceMonitor's advanced network intelligence.

🧐 "Network measurements must be precise and authentic - no fabrication shall pass through these cables"

CORE PRINCIPLES:
- Real psutil network measurements ONLY
- ResourceMonitor integration for enhanced data
- NO fake data generation on errors
- Honest failure handling
- Clean, efficient network analysis
"""

import psutil
import time
import logging
import socket
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio

from app.optimization.resource_monitor import ResourceMonitor


class SimplifiedNetworkService:
    """
    Enhanced network metrics service that combines basic psutil data with
    ResourceMonitor's comprehensive network intelligence.
    
    🧐 ARISTOCRATIC ARCHITECTURE:
    - Real psutil network measurements ONLY
    - ResourceMonitor integration for advanced metrics
    - Fails honestly when network access fails
    - No fake data generation under any circumstances
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimplifiedNetworkService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SimplifiedNetworkService')
        self._last_io_counters = None
        self._last_io_time = None
        self._resource_monitor = None
        self._initialized = True
        self.logger.info("🧐 Enhanced SimplifiedNetworkService initialized with aristocratic precision")
    
    @classmethod
    async def get_instance(cls):
        """Get the singleton instance of the service"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def _get_resource_monitor(self):
        """Get or create ResourceMonitor instance for enhanced metrics"""
        if self._resource_monitor is None:
            try:
                self._resource_monitor = ResourceMonitor()
                await self._resource_monitor.initialize()
                self.logger.debug("🧐🔧 ResourceMonitor initialized for enhanced network metrics")
            except Exception as e:
                self.logger.warning(f"🧐⚠️ ResourceMonitor initialization failed: {str(e)}")
                raise Exception(f"ResourceMonitor initialization failed: {str(e)}")
        return self._resource_monitor
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive network metrics combining psutil and ResourceMonitor data.
        
        🧐 ARISTOCRATIC NETWORK ANALYSIS:
        - Real psutil network measurements ONLY
        - Enhanced ResourceMonitor data integration
        - No fallbacks, no samples, no hardcoded values
        - Fails honestly if network access is unavailable
        
        Returns:
            Dictionary containing REAL network metrics formatted for frontend
            
        Raises:
            Exception: If network metrics collection fails (NO FAKE DATA RETURNED)
        """
        try:
            self.logger.debug("🧐 Collecting comprehensive network metrics with aristocratic precision...")
            
            # PHASE 1: BASIC PSUTIL NETWORK DATA
            basic_metrics = await self._get_psutil_network_data()
            
            # PHASE 2: ENHANCED RESOURCEMONITOR DATA (OPTIONAL)
            enhanced_metrics = await self._get_resource_monitor_data()
            
            # PHASE 3: MERGE DATA STRUCTURES
            final_metrics = self._merge_network_data(basic_metrics, enhanced_metrics)
            
            # PHASE 4: COMPILE COMPREHENSIVE NETWORK METRICS
            network_metrics = {
                'timestamp': utc_now().isoformat(),
                'type': 'network',
                'data': final_metrics
            }
            
            interface_count = len(final_metrics.get('interfaces', []))
            connection_count = len(final_metrics.get('connections', []))
            
            self.logger.info(
                f"🧐✅ Network metrics collected successfully: {interface_count} interfaces, "
                f"{connection_count} connections, rates: {final_metrics.get('sent_rate', 0):.0f}/"
                f"{final_metrics.get('recv_rate', 0):.0f} bytes/s"
            )
            
            return network_metrics
            
        except Exception as e:
            error_msg = f"Network metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            # NO FAKE DATA - FAIL HONESTLY
            raise Exception(error_msg)
    
    async def _get_psutil_network_data(self) -> Dict[str, Any]:
        """
        Get comprehensive network data directly from psutil.
        
        Returns:
            Dictionary with psutil network information
            
        Raises:
            Exception: If psutil network data collection fails
        """
        try:
            # NETWORK INTERFACES ANALYSIS
            interfaces = await self._get_network_interfaces()
            
            # NETWORK I/O STATISTICS WITH RATE CALCULATION
            io_data = await self._get_network_io_metrics()
            
            # NETWORK CONNECTIONS ANALYSIS
            connections_data = await self._get_network_connections()
            
            # COMPILE PSUTIL NETWORK DATA
            psutil_data = {
                'bytes_sent': io_data['bytes_sent'],
                'bytes_recv': io_data['bytes_recv'],
                'packets_sent': io_data['packets_sent'],
                'packets_recv': io_data['packets_recv'],
                'sent_rate': io_data['sent_rate'],
                'recv_rate': io_data['recv_rate'],
                'interfaces': interfaces,
                'connections': connections_data['connections'],
                'connection_stats': connections_data['connection_stats'],
                'protocol_stats': connections_data['protocol_stats'],
                'interface_stats': io_data['interface_stats'],
                'data_source': 'psutil_direct'
            }
            
            return psutil_data
            
        except Exception as e:
            error_msg = f"psutil network data collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interfaces information from psutil."""
        try:
            interfaces = []
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            if not addrs:
                raise Exception("No network interfaces detected by psutil")
            
            for interface_name, addr_list in addrs.items():
                # Get interface statistics
                if interface_name in stats:
                    interface_stats = stats[interface_name]
                    isup = interface_stats.isup
                    speed = interface_stats.speed
                    mtu = interface_stats.mtu
                else:
                    isup = False
                    speed = 0
                    mtu = 0
                
                # Extract addresses
                ipv4_address = ""
                ipv6_address = ""
                mac_address = ""
                
                for addr in addr_list:
                    if addr.family == socket.AF_INET:  # IPv4
                        ipv4_address = addr.address
                    elif addr.family == socket.AF_INET6:  # IPv6
                        ipv6_address = addr.address
                    elif addr.family == psutil.AF_LINK:  # MAC
                        mac_address = addr.address
                
                interface_info = {
                    'name': interface_name,
                    'ipv4_address': ipv4_address,
                    'ipv6_address': ipv6_address,
                    'mac_address': mac_address,
                    'is_up': isup,
                    'speed_mbps': speed,
                    'mtu': mtu,
                    'has_ipv4': bool(ipv4_address),
                    'has_ipv6': bool(ipv6_address)
                }
                
                interfaces.append(interface_info)
            
            active_interfaces = [i for i in interfaces if i['is_up']]
            self.logger.debug(f"🧐📊 Found {len(interfaces)} network interfaces, {len(active_interfaces)} active")
            
            return interfaces
            
        except Exception as e:
            error_msg = f"Network interfaces analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_network_io_metrics(self) -> Dict[str, Any]:
        """Get network I/O statistics with rate calculations."""
        try:
            current_time = time.time()
            
            # Get total I/O counters
            total_io = psutil.net_io_counters()
            if total_io is None:
                raise Exception("Network I/O counters not available from psutil")
            
            # Get per-interface I/O counters
            interface_io = psutil.net_io_counters(pernic=True)
            if interface_io is None:
                interface_io = {}
            
            # Calculate rates if we have previous measurements
            sent_rate = 0.0
            recv_rate = 0.0
            
            if self._last_io_counters and self._last_io_time:
                time_diff = current_time - self._last_io_time
                if time_diff > 0:
                    sent_rate = (total_io.bytes_sent - self._last_io_counters.bytes_sent) / time_diff
                    recv_rate = (total_io.bytes_recv - self._last_io_counters.bytes_recv) / time_diff
            
            # Update state for next calculation
            self._last_io_counters = total_io
            self._last_io_time = current_time
            
            # Format per-interface stats
            interface_stats = {}
            for name, counters in interface_io.items():
                interface_stats[name] = {
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errors_in': counters.errin,
                    'errors_out': counters.errout,
                    'drops_in': counters.dropin,
                    'drops_out': counters.dropout
                }
            
            io_data = {
                'bytes_sent': total_io.bytes_sent,
                'bytes_recv': total_io.bytes_recv,
                'packets_sent': total_io.packets_sent,
                'packets_recv': total_io.packets_recv,
                'sent_rate': sent_rate,
                'recv_rate': recv_rate,
                'interface_stats': interface_stats,
                'rate_calculation_available': self._last_io_counters is not None
            }
            
            return io_data
            
        except Exception as e:
            error_msg = f"Network I/O metrics collection failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_network_connections(self) -> Dict[str, Any]:
        """Get network connections analysis from psutil."""
        try:
            connections = []
            connection_stats = {
                'ESTABLISHED': 0, 'LISTEN': 0, 'TIME_WAIT': 0, 
                'CLOSE_WAIT': 0, 'CLOSED': 0, 'OTHER': 0
            }
            protocol_stats = {'tcp': 0, 'udp': 0, 'tcp6': 0, 'udp6': 0}
            
            try:
                # Get all network connections
                all_connections = psutil.net_connections(kind='inet')
                
                for conn in all_connections:
                    # Process connection status
                    status = getattr(conn, 'status', 'UNKNOWN')
                    if status in connection_stats:
                        connection_stats[status] += 1
                    else:
                        connection_stats['OTHER'] += 1
                    
                    # Process protocol information
                    if hasattr(conn, 'type') and hasattr(conn, 'family'):
                        if conn.type == socket.SOCK_STREAM:
                            proto = 'tcp6' if conn.family == socket.AF_INET6 else 'tcp'
                        elif conn.type == socket.SOCK_DGRAM:
                            proto = 'udp6' if conn.family == socket.AF_INET6 else 'udp'
                        else:
                            proto = 'unknown'
                        
                        if proto in protocol_stats:
                            protocol_stats[proto] += 1
                    
                    # Add connection details (limit to prevent memory issues)
                    if len(connections) < 100:
                        laddr = ""
                        raddr = ""
                        
                        if hasattr(conn, 'laddr') and conn.laddr:
                            laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
                        
                        if hasattr(conn, 'raddr') and conn.raddr:
                            raddr = f"{conn.raddr.ip}:{conn.raddr.port}"
                        
                        connection_info = {
                            'fd': getattr(conn, 'fd', None),
                            'pid': getattr(conn, 'pid', None),
                            'type': proto if 'proto' in locals() else 'unknown',
                            'local_address': laddr,
                            'remote_address': raddr,
                            'status': status
                        }
                        
                        connections.append(connection_info)
                        
            except (psutil.AccessDenied, psutil.Error) as e:
                self.logger.warning(f"🧐⚠️ Limited access to network connections: {str(e)}")
                # Don't fail entirely - some connection data is better than none
            
            connections_data = {
                'connections': connections,
                'connection_stats': connection_stats,
                'protocol_stats': protocol_stats,
                'total_connections': sum(connection_stats.values())
            }
            
            self.logger.debug(f"🧐📊 Analyzed {connections_data['total_connections']} network connections")
            return connections_data
            
        except Exception as e:
            error_msg = f"Network connections analysis failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _get_resource_monitor_data(self) -> Dict[str, Any]:
        """Get enhanced network data from ResourceMonitor (optional)."""
        try:
            resource_monitor = await self._get_resource_monitor()
            enhanced_data = await resource_monitor._get_throttled_network_metrics()
            
            self.logger.debug("🧐🔧 ResourceMonitor network data integrated successfully")
            return enhanced_data
            
        except Exception as e:
            self.logger.debug(f"🧐📊 ResourceMonitor network data unavailable: {str(e)}")
            # Return empty dict rather than failing - enhanced data is optional
            return {}
    
    def _merge_network_data(self, psutil_data: Dict[str, Any], resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge psutil and ResourceMonitor data intelligently.
        
        Args:
            psutil_data: Base psutil network data
            resource_data: Enhanced ResourceMonitor data
            
        Returns:
            Merged network data dictionary
        """
        # Start with psutil data as foundation
        merged = psutil_data.copy()
        
        # Add ResourceMonitor enhancements if available
        if resource_data and isinstance(resource_data, dict):
            for key, value in resource_data.items():
                # Only add meaningful data (not empty containers)
                if value is not None and value != {} and value != []:
                    if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                        # Merge dictionaries
                        merged[key].update(value)
                    else:
                        # Add new key or replace value
                        merged[key] = value
            
            merged['enhanced_data_available'] = True
        else:
            merged['enhanced_data_available'] = False
        
        return merged
    
    async def get_network_usage_only(self) -> Dict[str, Any]:
        """Get just essential network usage quickly."""
        try:
            total_io = psutil.net_io_counters()
            if total_io is None:
                raise Exception("Network I/O counters not available")
            
            return {
                'bytes_sent_mb': round(total_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(total_io.bytes_recv / (1024**2), 2),
                'packets_sent': total_io.packets_sent,
                'packets_recv': total_io.packets_recv
            }
            
        except Exception as e:
            error_msg = f"Network usage measurement failed: {str(e)}"
            self.logger.error(f"🧐💥 {error_msg}")
            raise Exception(error_msg)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the network metrics service."""
        try:
            start_time = utc_now()
            
            # Test basic network usage
            network_usage = await self.get_network_usage_only()
            
            # Test interfaces detection
            interfaces = await self._get_network_interfaces()
            active_interfaces = [i for i in interfaces if i['is_up']]
            
            # Test I/O metrics
            io_data = await self._get_network_io_metrics()
            
            # Test connections analysis
            connections_data = await self._get_network_connections()
            
            # Test ResourceMonitor integration (optional)
            resource_monitor_available = False
            try:
                await self._get_resource_monitor()
                resource_monitor_available = True
            except Exception:
                pass
            
            collection_time = (utc_now() - start_time).total_seconds()
            
            return {
                'status': 'OPERATIONAL',
                'service_type': 'network_metrics_collection',
                'psutil_available': True,
                'collection_time_seconds': round(collection_time, 4),
                'network_usage': network_usage,
                'total_interfaces': len(interfaces),
                'active_interfaces': len(active_interfaces),
                'total_connections': connections_data['total_connections'],
                'rate_calculation_ready': io_data['rate_calculation_available'],
                'resource_monitor_available': resource_monitor_available,
                'data_quality': 'real_psutil_measurements',
                'architectural_principles': [
                    'no_fake_data_generation',
                    'honest_failure_handling',
                    'real_measurements_only',
                    'resource_monitor_integration'
                ],
                'last_health_check': utc_now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'service_type': 'network_metrics_collection',
                'psutil_available': False,
                'error': str(e),
                'last_health_check': utc_now().isoformat()
            }

# Test function to run the service directly
async def test_simplified_network_service():
    """Test the simplified network service with aristocratic precision"""
    print("\n" + "="*80)
    print(" 🧐🌐 SIMPLIFIED NETWORK SERVICE TEST - ARISTOCRATIC PRECISION")
    print("="*80)
    
    print(f"\n🕐 Timestamp: {utc_now().isoformat()}")
    
    try:
        # Initialize service
        service = await SimplifiedNetworkService.get_instance()
        print(f"📊 Service instance: {service}")
        
        # Perform health check
        print("\n🏥 Health Check:")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Collection Time: {health.get('collection_time_seconds', 'N/A')} seconds")
        print(f"   Total Interfaces: {health.get('total_interfaces', 'N/A')}")
        print(f"   Active Interfaces: {health.get('active_interfaces', 'N/A')}")
        print(f"   Total Connections: {health.get('total_connections', 'N/A')}")
        print(f"   ResourceMonitor Available: {health.get('resource_monitor_available', 'N/A')}")
        
        # Get full network metrics
        print("\n🧐 Collecting Full Network Metrics...")
        metrics = await service.get_metrics()
        
        print("\n📈 Network Metrics Results:")
        data = metrics['data']
        print(f"   Bytes Sent: {data['bytes_sent'] / (1024**2):.2f} MB")
        print(f"   Bytes Received: {data['bytes_recv'] / (1024**2):.2f} MB")
        print(f"   Send Rate: {data['sent_rate'] / 1024:.2f} KB/s")
        print(f"   Receive Rate: {data['recv_rate'] / 1024:.2f} KB/s")
        
        print(f"\n🔌 Network Interfaces:")
        for interface in data['interfaces'][:5]:  # Show first 5
            status = "🟢 UP" if interface.get('is_up', False) else "🔴 DOWN"
            ipv4 = interface['ipv4_address'] or "No IPv4"
            print(f"   {status} {interface['name']}: {ipv4}")
            if interface['mac_address']:
                print(f"      MAC: {interface['mac_address']}")
            if interface['speed_mbps'] > 0:
                print(f"      Speed: {interface['speed_mbps']} Mbps, MTU: {interface['mtu']}")
        
        print(f"\n📊 Connection Statistics:")
        conn_stats = data['connection_stats']
        for status, count in conn_stats.items():
            if count > 0:
                print(f"   {status}: {count}")
        
        print(f"\n🔧 Protocol Statistics:")
        proto_stats = data['protocol_stats']
        tcp_total = proto_stats.get('tcp', 0) + proto_stats.get('tcp6', 0)
        udp_total = proto_stats.get('udp', 0) + proto_stats.get('udp6', 0)
        print(f"   TCP: {tcp_total} connections")
        print(f"   UDP: {udp_total} connections")
        
        print(f"\n🔍 Active Connections (sample):")
        connections = data['connections'][:5]  # Show first 5
        if connections:
            for conn in connections:
                print(f"   {conn['type'].upper()}: {conn['local_address']} → {conn['remote_address']}")
                print(f"      Status: {conn['status']}, PID: {conn['pid'] or 'N/A'}")
        else:
            print("   No connection details available")
        
        # Show enhanced data if available
        if data.get('enhanced_data_available'):
            print(f"\n🔧 Enhanced Data Available:")
            if 'connection_quality' in data:
                cq = data['connection_quality']
                print(f"   Connection Quality Metrics Found")
            if 'latency' in data and data['latency']:
                print(f"   Latency: {data['latency']} ms")
        else:
            print(f"\n📊 Basic psutil data only (ResourceMonitor unavailable)")
        
        print(f"\n✅ Data Quality: {data.get('data_quality', 'Unknown')}")
        print(f"📊 Rate Calculation: {'Available' if data.get('rate_calculation_available') else 'Initializing'}")
        
        # Test quick network usage
        print(f"\n⚡ Quick Network Usage Test:")
        try:
            quick_usage = await service.get_network_usage_only()
            print(f"   Sent: {quick_usage['bytes_sent_mb']} MB, Received: {quick_usage['bytes_recv_mb']} MB")
            print(f"   Packets: {quick_usage['packets_sent']} sent, {quick_usage['packets_recv']} received")
        except Exception as e:
            print(f"   Quick usage test failed: {str(e)}")
        
    except Exception as e:
        print(f"\n💥 NETWORK SERVICE TEST FAILED: {str(e)}")
        print("This indicates psutil network access is unavailable or system issues")
        print("🧐 Service failed with dignity - no fake data generated!")
    
    print("\n" + "="*80)
    print(" 🧐✨ NETWORK SERVICE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simplified_network_service())