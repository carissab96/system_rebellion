"""
Network Metrics Service

This service is responsible for collecting detailed network metrics including:
- Network interface statistics
- Network connections
- Network I/O rates
- Per-connection bandwidth usage
- Protocol-specific metrics (TCP, UDP, HTTP)
- Connection quality metrics (latency, packet loss)
- Per-process network usage
"""

import psutil
import socket
import logging
import subprocess
import re
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

class NetworkMetricsService:
    """Service for collecting detailed network metrics"""
    
    def __init__(self):
        """Initialize the network metrics service"""
        self.logger = logging.getLogger('NetworkMetricsService')
        self._previous_io_counters = None
        self._previous_io_time = None
        self._previous_connections_stats = {}
        self._previous_protocol_stats = {}
        self._previous_latency_checks = {}
        self._connection_history = defaultdict(list)  # Track connection history for quality metrics
        self._packet_loss_history = {}  # Track packet loss over time
        self._interface_stats_history = defaultdict(list)  # Track per-interface stats over time
        self._dns_query_history = []  # Track DNS query performance
        self._protocol_breakdown_cache = {}  # Cache for protocol breakdown analysis
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get detailed network metrics.
        
        Returns:
            Dictionary containing detailed network metrics
        """
        try:
            # Get network interfaces statistics
            interfaces = self._get_network_interfaces()
            
            # Get overall network I/O statistics
            io_stats = self._get_network_io_stats()
            
            # Get active connections
            connections = self._get_network_connections()
            
            # Get protocol-specific metrics
            protocol_stats = await self._get_protocol_metrics()
            
            # Get connection quality metrics (latency, packet loss)
            connection_quality = await self._get_connection_quality_metrics()
            
            # Get top bandwidth consumers by process
            top_bandwidth_processes = await self._get_top_bandwidth_processes(5)
            
            # Get per-interface statistics
            interface_stats = self._get_per_interface_stats()
            
            # Get DNS performance metrics
            dns_metrics = await self._get_dns_metrics()
            
            # Get internet connectivity metrics
            internet_metrics = await self._get_internet_connectivity_metrics()
            
            # Get protocol breakdown by connection type
            protocol_breakdown = self._get_protocol_breakdown()
            
            return {
                'interfaces': interfaces,
                'io_stats': io_stats,
                'connections': connections,
                'protocol_stats': protocol_stats,
                'connection_quality': connection_quality,
                'top_bandwidth_processes': top_bandwidth_processes,
                'interface_stats': interface_stats,
                'dns_metrics': dns_metrics,
                'internet_metrics': internet_metrics,
                'protocol_breakdown': protocol_breakdown
            }
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {str(e)}")
            # Return empty dict on error
            return {
                'interfaces': [],
                'io_stats': {},
                'connections': [],
                'protocol_stats': {},
                'connection_quality': {},
                'top_bandwidth_processes': [],
                'interface_stats': {},
                'dns_metrics': {},
                'internet_metrics': {},
                'protocol_breakdown': {
                    'tcp': 0,
                    'udp': 0,
                    'http': 0,
                    'file_transfer': 0,
                    'other': 0
                }
            }    
    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get information about network interfaces"""
        interfaces_info = []
        try:
            # Get all network interfaces
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in net_if_addrs.items():
                # Skip loopback interfaces if desired
                # if interface_name.startswith('lo'):
                #     continue
                
                interface_info = {
                    'name': interface_name,
                    'addresses': [],
                    'isup': False,
                    'duplex': '',
                    'speed': 0,
                    'mtu': 0
                }
                
                # Add addresses
                for addr in addrs:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': getattr(addr, 'netmask', None),
                        'broadcast': getattr(addr, 'broadcast', None)
                    }
                    interface_info['addresses'].append(addr_info)
                
                # Add interface stats if available
                if interface_name in net_if_stats:
                    stats = net_if_stats[interface_name]
                    interface_info['isup'] = stats.isup
                    interface_info['duplex'] = stats.duplex
                    interface_info['speed'] = stats.speed
                    interface_info['mtu'] = stats.mtu
                
                interfaces_info.append(interface_info)
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {str(e)}")
        
        return interfaces_info
    
    def _get_network_io_stats(self) -> Dict[str, Any]:
        """Get network I/O statistics including send/receive rates"""
        try:
            # Get current network I/O counters
            io_counters = psutil.net_io_counters()
            current_time = datetime.now().timestamp()
            
            # Initialize rates
            sent_rate = 0
            recv_rate = 0
            
            # Calculate rates if we have previous measurements
            if self._previous_io_counters is not None and self._previous_io_time is not None:
                time_diff = current_time - self._previous_io_time
                
                if time_diff > 0:
                    bytes_sent_diff = io_counters.bytes_sent - self._previous_io_counters.bytes_sent
                    bytes_recv_diff = io_counters.bytes_recv - self._previous_io_counters.bytes_recv
                    packets_sent_diff = io_counters.packets_sent - self._previous_io_counters.packets_sent
                    packets_recv_diff = io_counters.packets_recv - self._previous_io_counters.packets_recv
                    
                    # Only update rates if we have positive differences
                    if bytes_sent_diff >= 0:
                        sent_rate = bytes_sent_diff / time_diff
                    if bytes_recv_diff >= 0:
                        recv_rate = bytes_recv_diff / time_diff
                    
                    # Calculate packet rates
                    packets_sent_rate = packets_sent_diff / time_diff if packets_sent_diff >= 0 else 0
                    packets_recv_rate = packets_recv_diff / time_diff if packets_recv_diff >= 0 else 0
            else:
                packets_sent_rate = 0
                packets_recv_rate = 0
            
            # Store current values for next calculation
            self._previous_io_counters = io_counters
            self._previous_io_time = current_time
            
            # Convert to more readable units
            sent_rate_kbps = sent_rate / 1024
            recv_rate_kbps = recv_rate / 1024
            total_rate_kbps = sent_rate_kbps + recv_rate_kbps
            
            # Convert to Mbps for easier reading
            rate_mbps = (sent_rate + recv_rate) / (1024 * 1024)
            
            # Calculate packet size averages if we have packets
            avg_sent_packet_size = 0
            avg_recv_packet_size = 0
            
            if io_counters.packets_sent > 0:
                avg_sent_packet_size = io_counters.bytes_sent / io_counters.packets_sent
            
            if io_counters.packets_recv > 0:
                avg_recv_packet_size = io_counters.bytes_recv / io_counters.packets_recv
            
            # Calculate error and drop rates
            error_rate = 0
            drop_rate = 0
            
            if hasattr(io_counters, 'errin') and hasattr(io_counters, 'errout'):
                error_rate = (io_counters.errin + io_counters.errout) / (io_counters.packets_sent + io_counters.packets_recv) * 100 if (io_counters.packets_sent + io_counters.packets_recv) > 0 else 0
            
            if hasattr(io_counters, 'dropin') and hasattr(io_counters, 'dropout'):
                drop_rate = (io_counters.dropin + io_counters.dropout) / (io_counters.packets_sent + io_counters.packets_recv) * 100 if (io_counters.packets_sent + io_counters.packets_recv) > 0 else 0
            
            return {
                'bytes_sent': io_counters.bytes_sent,
                'bytes_recv': io_counters.bytes_recv,
                'packets_sent': io_counters.packets_sent,
                'packets_recv': io_counters.packets_recv,
                'errin': getattr(io_counters, 'errin', 0),
                'errout': getattr(io_counters, 'errout', 0),
                'dropin': getattr(io_counters, 'dropin', 0),
                'dropout': getattr(io_counters, 'dropout', 0),
                'sent_rate': sent_rate,
                'recv_rate': recv_rate,
                'sent_rate_kbps': sent_rate_kbps,
                'recv_rate_kbps': recv_rate_kbps,
                'total_rate_kbps': total_rate_kbps,
                'rate_mbps': rate_mbps,
                'packets_sent_rate': packets_sent_rate,
                'packets_recv_rate': packets_recv_rate,
                'avg_sent_packet_size': avg_sent_packet_size,
                'avg_recv_packet_size': avg_recv_packet_size,
                'error_rate_percent': error_rate,
                'drop_rate_percent': drop_rate
            }
        except Exception as e:
            self.logger.error(f"Error getting network I/O stats: {str(e)}")
            return {
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'errin': 0,
                'errout': 0,
                'dropin': 0,
                'dropout': 0,
                'sent_rate': 0,
                'recv_rate': 0,
                'sent_rate_kbps': 0,
                'recv_rate_kbps': 0,
                'total_rate_kbps': 0,
                'rate_mbps': 0,
                'packets_sent_rate': 0,
                'packets_recv_rate': 0,
                'avg_sent_packet_size': 0,
                'avg_recv_packet_size': 0,
                'error_rate_percent': 0,
                'drop_rate_percent': 0
            }
    
    def _get_network_connections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get active network connections"""
        connections_info = []
        try:
            # Get all network connections
            connections = psutil.net_connections(kind='inet')
            
            # Process connection information
            for conn in connections:
                try:
                    # Skip connections with no PID (system connections)
                    if conn.pid is None:
                        continue
                    
                    # Get process information
                    try:
                        process = psutil.Process(conn.pid)
                        process_name = process.name()
                        username = process.username()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_name = "Unknown"
                        username = "Unknown"
                    
                    # Format local and remote addresses
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    
                    # Try to resolve remote hostname
                    remote_host = "N/A"
                    if conn.raddr:
                        try:
                            remote_host = socket.gethostbyaddr(conn.raddr.ip)[0]
                        except (socket.herror, socket.gaierror):
                            remote_host = "Unresolved"
                    
                    connection_info = {
                        'fd': conn.fd,
                        'family': conn.family,
                        'type': conn.type,
                        'local_address': laddr,
                        'remote_address': raddr,
                        'remote_host': remote_host,
                        'status': conn.status,
                        'pid': conn.pid,
                        'process_name': process_name,
                        'username': username
                    }
                    
                    connections_info.append(connection_info)
                except Exception as e:
                    self.logger.error(f"Error processing connection: {str(e)}")
            
            # Sort by status (ESTABLISHED first) and take top N
            connections_info = sorted(
                connections_info,
                key=lambda x: (0 if x['status'] == 'ESTABLISHED' else 1, x['process_name'])
            )[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting network connections: {str(e)}")
        
        return connections_info
    
    async def _get_protocol_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get protocol-specific metrics (TCP, UDP, HTTP, etc.)
        
        Returns:
            Dictionary containing protocol-specific metrics
        """
        protocol_stats = {
            'tcp': {'active': 0, 'listening': 0, 'established': 0, 'time_wait': 0, 'close_wait': 0},
            'udp': {'active': 0},
            'http': {'connections': 0, 'servers': []},
            'dns': {'queries': 0},
            'ssl': {'connections': 0}
        }
        
        try:
            # Get TCP connection states
            connections = psutil.net_connections(kind='tcp')
            for conn in connections:
                protocol_stats['tcp']['active'] += 1
                
                if conn.status == 'LISTEN':
                    protocol_stats['tcp']['listening'] += 1
                elif conn.status == 'ESTABLISHED':
                    protocol_stats['tcp']['established'] += 1
                elif conn.status == 'TIME_WAIT':
                    protocol_stats['tcp']['time_wait'] += 1
                elif conn.status == 'CLOSE_WAIT':
                    protocol_stats['tcp']['close_wait'] += 1
                
                # Check for HTTP servers (common ports)
                if hasattr(conn, 'laddr') and conn.laddr:
                    port = None
                    if hasattr(conn.laddr, 'port'):
                        port = conn.laddr.port
                    elif len(conn.laddr) >= 2:
                        port = conn.laddr[1]
                    
                    if port in [80, 443, 8000, 8080, 8443, 3000]:
                        protocol_stats['http']['connections'] += 1
                        if conn.status == 'LISTEN':
                            server_info = {'port': port, 'pid': conn.pid}
                            if server_info not in protocol_stats['http']['servers']:
                                protocol_stats['http']['servers'].append(server_info)
                    
                    # Check for SSL/TLS connections
                    if port == 443 or port == 8443:
                        protocol_stats['ssl']['connections'] += 1
            
            # Get UDP connection count
            udp_connections = psutil.net_connections(kind='udp')
            protocol_stats['udp']['active'] = len(udp_connections)
            
            # Check for DNS queries (UDP port 53)
            for conn in udp_connections:
                if hasattr(conn, 'raddr') and conn.raddr:
                    port = None
                    if hasattr(conn.raddr, 'port'):
                        port = conn.raddr.port
                    elif len(conn.raddr) >= 2:
                        port = conn.raddr[1]
                    
                    if port == 53:
                        protocol_stats['dns']['queries'] += 1
            
        except Exception as e:
            self.logger.error(f"Error getting protocol metrics: {str(e)}")
        
        return protocol_stats
    
    async def _get_connection_quality_metrics(self) -> Dict[str, Any]:
        """
        Get connection quality metrics (latency, packet loss, etc.)
        
        Returns:
            Dictionary containing connection quality metrics
        """
        quality_metrics = {
            'average_latency': 0,  # in ms
            'packet_loss_percent': 0,
            'connection_stability': 100,  # 0-100 score
            'gateway_latency': 0,  # in ms
            'dns_latency': 0,  # in ms
            'internet_latency': 0,  # in ms
            'latency_history': [],
            'packet_loss_history': []
        }
        
        try:
            # Get default gateway
            gateway = None
            try:
                # Try to get the default gateway
                interfaces = psutil.net_if_addrs()
                for interface, addrs in interfaces.items():
                    if interface != 'lo':  # Skip loopback
                        for addr in addrs:
                            if addr.family == socket.AF_INET:  # IPv4
                                # This is a simplification - in a real implementation,
                                # we'd use a library or command to get the actual gateway
                                gateway = addr.address.rsplit('.', 1)[0] + '.1'
                                break
                        if gateway:
                            break
            except Exception as e:
                self.logger.debug(f"Could not determine default gateway: {str(e)}")
            
            # Measure gateway latency if we found one
            if gateway:
                try:
                    # Use ping to measure latency to gateway
                    ping_output = subprocess.run(
                        ['ping', '-c', '3', '-W', '1', gateway],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    # Parse ping output for latency and packet loss
                    if ping_output.returncode == 0:
                        # Extract average latency
                        latency_match = re.search(r'min/avg/max.*?= [\d.]+/([\d.]+)/[\d.]+', ping_output.stdout)
                        if latency_match:
                            quality_metrics['gateway_latency'] = float(latency_match.group(1))
                        
                        # Extract packet loss
                        loss_match = re.search(r'(\d+)% packet loss', ping_output.stdout)
                        if loss_match:
                            gateway_loss = float(loss_match.group(1))
                            quality_metrics['packet_loss_percent'] = gateway_loss
                except Exception as e:
                    self.logger.debug(f"Error measuring gateway latency: {str(e)}")
            
            # Measure DNS latency
            try:
                dns_start = time.time()
                socket.gethostbyname('www.google.com')
                dns_end = time.time()
                quality_metrics['dns_latency'] = (dns_end - dns_start) * 1000  # Convert to ms
            except Exception as e:
                self.logger.debug(f"Error measuring DNS latency: {str(e)}")
            
            # Measure internet latency (to a reliable host like 8.8.8.8)
            try:
                ping_output = subprocess.run(
                    ['ping', '-c', '3', '-W', '2', '8.8.8.8'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if ping_output.returncode == 0:
                    # Extract average latency
                    latency_match = re.search(r'min/avg/max.*?= [\d.]+/([\d.]+)/[\d.]+', ping_output.stdout)
                    if latency_match:
                        quality_metrics['internet_latency'] = float(latency_match.group(1))
                        quality_metrics['average_latency'] = float(latency_match.group(1))
                    
                    # Extract packet loss
                    loss_match = re.search(r'(\d+)% packet loss', ping_output.stdout)
                    if loss_match:
                        internet_loss = float(loss_match.group(1))
                        if quality_metrics['packet_loss_percent'] == 0:  # Only use if we didn't get from gateway
                            quality_metrics['packet_loss_percent'] = internet_loss
            except Exception as e:
                self.logger.debug(f"Error measuring internet latency: {str(e)}")
            
            # Calculate connection stability score (100 - packet loss - normalized latency penalty)
            latency_penalty = min(quality_metrics['average_latency'] / 10, 50) if quality_metrics['average_latency'] > 0 else 0
            quality_metrics['connection_stability'] = max(0, 100 - quality_metrics['packet_loss_percent'] - latency_penalty)
            
            # Store history for trending
            current_time = datetime.now().isoformat()
            
            # Latency history
            latency_entry = {
                'timestamp': current_time,
                'value': quality_metrics['average_latency']
            }
            self._connection_history['latency'].append(latency_entry)
            # Keep only last 100 entries
            quality_metrics['latency_history'] = self._connection_history['latency'][-100:]
            
            # Packet loss history
            loss_entry = {
                'timestamp': current_time,
                'value': quality_metrics['packet_loss_percent']
            }
            self._connection_history['packet_loss'].append(loss_entry)
            # Keep only last 100 entries
            quality_metrics['packet_loss_history'] = self._connection_history['packet_loss'][-100:]
            
        except Exception as e:
            self.logger.error(f"Error getting connection quality metrics: {str(e)}")
        
        return quality_metrics
    
    async def _get_top_bandwidth_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top processes consuming network bandwidth
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of dictionaries containing process information
        """
        try:
            # Get connection stats by process
            process_stats = await self.get_connection_stats_by_process()
            
            # Sort processes by total bandwidth (read_rate + write_rate)
            sorted_processes = []
            for process_name, stats in process_stats.items():
                if 'total_rate' in stats:
                    sorted_processes.append({
                        'name': process_name,
                        'pid': stats['pid'],
                        'total_rate': stats['total_rate'],
                        'read_rate': stats.get('read_rate', 0),
                        'write_rate': stats.get('write_rate', 0),
                        'connection_count': stats['connection_count'],
                        'protocols': stats.get('protocols', {})
                    })
            
            # Sort by total_rate in descending order
            sorted_processes.sort(key=lambda x: x['total_rate'], reverse=True)
            
            # Return top processes limited by limit
            return sorted_processes[:limit]
        except Exception as e:
            self.logger.error(f"Error getting top bandwidth processes: {str(e)}")
            return []
    
    async def get_connection_stats_by_process(self) -> Dict[str, Dict[str, Any]]:
        """
        Get network statistics grouped by process.
        This is an expensive operation and should be called separately when needed.
        
        Returns:
            Dictionary mapping process names to their network statistics
        """
        process_stats = {}
        process_connections = {}
        
        try:
            # Get all connections with process information
            connections = psutil.net_connections(kind='all')
            
            # Group connections by process
            for conn in connections:
                if conn.pid is None:
                    continue
                
                try:
                    process = psutil.Process(conn.pid)
                    process_name = process.name()
                    
                    if process_name not in process_connections:
                        process_connections[process_name] = {
                            'pid': conn.pid,
                            'connections': [],
                            'connection_count': 0,
                            'established_count': 0,
                            'remote_addresses': set(),
                            'local_ports': set(),
                            'protocols': {'tcp': 0, 'udp': 0, 'unix': 0}
                        }
                    
                    process_connections[process_name]['connections'].append(conn)
                    process_connections[process_name]['connection_count'] += 1
                    
                    # Track connection status
                    if conn.status == 'ESTABLISHED':
                        process_connections[process_name]['established_count'] += 1
                    
                    # Track remote addresses
                    if hasattr(conn, 'raddr') and conn.raddr:
                        if hasattr(conn.raddr, 'ip'):
                            process_connections[process_name]['remote_addresses'].add(conn.raddr.ip)
                        elif len(conn.raddr) >= 1:
                            process_connections[process_name]['remote_addresses'].add(str(conn.raddr[0]))
                    
                    # Track local ports
                    if hasattr(conn, 'laddr') and conn.laddr:
                        if hasattr(conn.laddr, 'port'):
                            process_connections[process_name]['local_ports'].add(conn.laddr.port)
                        elif len(conn.laddr) >= 2:
                            process_connections[process_name]['local_ports'].add(conn.laddr[1])
                    
                    # Track protocol
                    if hasattr(conn, 'type'):
                        if conn.type == socket.SOCK_STREAM:
                            process_connections[process_name]['protocols']['tcp'] += 1
                        elif conn.type == socket.SOCK_DGRAM:
                            process_connections[process_name]['protocols']['udp'] += 1
                        elif conn.type == socket.SOCK_SEQPACKET:
                            process_connections[process_name]['protocols']['unix'] += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Get per-process network I/O if available
            current_time = datetime.now().timestamp()
            
            for process_name, info in process_connections.items():
                try:
                    process = psutil.Process(info['pid'])
                    
                    # Some platforms support per-process network stats
                    try:
                        net_io = process.io_counters()
                        read_bytes = getattr(net_io, 'read_bytes', None)
                        write_bytes = getattr(net_io, 'write_bytes', None)
                        
                        # Calculate rates if we have previous measurements
                        read_rate = None
                        write_rate = None
                        
                        if process_name in self._previous_connections_stats and 'time' in self._previous_connections_stats[process_name]:
                            prev_stats = self._previous_connections_stats[process_name]
                            time_diff = current_time - prev_stats['time']
                            
                            if time_diff > 0:
                                if read_bytes is not None and 'read_bytes' in prev_stats:
                                    read_diff = read_bytes - prev_stats['read_bytes']
                                    if read_diff >= 0:
                                        read_rate = read_diff / time_diff
                                        
                                if write_bytes is not None and 'write_bytes' in prev_stats:
                                    write_diff = write_bytes - prev_stats['write_bytes']
                                    if write_diff >= 0:
                                        write_rate = write_diff / time_diff
                        
                        # Store current values for next calculation
                        if process_name not in self._previous_connections_stats:
                            self._previous_connections_stats[process_name] = {}
                        
                        if read_bytes is not None:
                            self._previous_connections_stats[process_name]['read_bytes'] = read_bytes
                        if write_bytes is not None:
                            self._previous_connections_stats[process_name]['write_bytes'] = write_bytes
                            
                        self._previous_connections_stats[process_name]['time'] = current_time
                        
                        # Build process stats with only available metrics
                        process_stats[process_name] = {
                            'pid': info['pid'],
                            'connection_count': info['connection_count'],
                            'established_count': info['established_count'],
                            'remote_addresses': list(info['remote_addresses']),
                            'local_ports': list(info['local_ports']),
                            'protocols': info['protocols']
                        }
                        
                        if read_bytes is not None:
                            process_stats[process_name]['read_bytes'] = read_bytes
                        if write_bytes is not None:
                            process_stats[process_name]['write_bytes'] = write_bytes
                        if read_rate is not None:
                            process_stats[process_name]['read_rate'] = read_rate
                        if write_rate is not None:
                            process_stats[process_name]['write_rate'] = write_rate
                        if read_rate is not None and write_rate is not None:
                            process_stats[process_name]['total_rate'] = read_rate + write_rate
                            
                    except (psutil.AccessDenied, AttributeError):
                        # Fall back to just connection counts if I/O stats aren't available
                        process_stats[process_name] = {
                            'pid': info['pid'],
                            'connection_count': info['connection_count'],
                            'established_count': info['established_count'],
                            'remote_addresses': list(info['remote_addresses']),
                            'local_ports': list(info['local_ports']),
                            'protocols': info['protocols']
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
        except Exception as e:
            self.logger.error(f"Error getting connection stats by process: {str(e)}")
        
        return process_stats
