// frontend/src/components/metrics/NetworkMetrics/utils/networkDataProcessor.ts

import { SystemMetric } from '../../../../types/metrics';
import { NetworkInterface, NetworkIOStats, ConnectionQuality, ProtocolStats } from '../tabs/types';

interface NetworkData {
  interfaces: NetworkInterface[];
  io_stats: NetworkIOStats;
  connection_quality: ConnectionQuality;
  protocol_stats: ProtocolStats;
  protocol_breakdown: {
    web: number;
    email: number;
    streaming: number;
    gaming: number;
    file_transfer: number;
    other: number;
  };
  top_bandwidth_processes: Array<{
    name: string;
    pid: number;
    upload: number;
    download: number;
  }>;
  dns_metrics?: {
    query_time_ms: number;
    [key: string]: any;
  };
  internet_metrics?: {
    isp_latency: number;
    [key: string]: any;
  };
  timestamp: string;
  [key: string]: any; // Allow additional properties
}


/**
 * Processes raw network data from a system metric into a structured format
 */
export function processNetworkData(currentMetric: SystemMetric | null): { 
  networkData: NetworkData | null; 
  error: string | null 
} {
  if (!currentMetric) {
    return { networkData: null, error: 'No metrics data available' };
  }
  
  // Find network data in expected locations
  const rawNetworkData = currentMetric.network || currentMetric.additional?.network_details;
  
  if (!rawNetworkData) {
    return { networkData: null, error: 'No network data found in metrics' };
  }
  
  try {
    // Check for required data
    if (!rawNetworkData.io_stats && 
        !(rawNetworkData.bytes_sent !== undefined && 
          rawNetworkData.bytes_recv !== undefined)) {
      throw new Error('Missing network I/O statistics');
    }
    
    // Process interfaces data which might be in different formats
    const interfaces = processInterfacesData(rawNetworkData.interfaces);
    
    // Build the network data structure from raw data
    const processedData: NetworkData = {
      interfaces: interfaces, // Add the processed interfaces
      timestamp: new Date().toISOString(), // Add default timestamp
      io_stats: {
        bytes_sent: rawNetworkData.io_stats?.bytes_sent ?? rawNetworkData.bytes_sent ?? 0,
        bytes_recv: rawNetworkData.io_stats?.bytes_recv ?? rawNetworkData.bytes_recv ?? 0,
        sent_rate: rawNetworkData.io_stats?.sent_rate ?? rawNetworkData.sent_rate_bps ?? 0,
        recv_rate: rawNetworkData.io_stats?.recv_rate ?? rawNetworkData.recv_rate_bps ?? 0
      },
      connection_quality: {
        connection_stability: rawNetworkData.connection_quality?.connection_stability ?? 0,
        average_latency: rawNetworkData.connection_quality?.average_latency ?? 0,
        packet_loss_percent: rawNetworkData.connection_quality?.packet_loss_percent ?? 0,
        jitter: rawNetworkData.connection_quality?.jitter ?? 0,
        gateway_latency: rawNetworkData.connection_quality?.gateway_latency ?? 0,
        dns_latency: rawNetworkData.connection_quality?.dns_latency ?? 
                      rawNetworkData.dns_metrics?.query_time_ms ?? 0,
        internet_latency: rawNetworkData.connection_quality?.internet_latency ?? 
                           rawNetworkData.internet_metrics?.isp_latency ?? 0
      },
      protocol_stats: rawNetworkData.protocol_stats || {
        tcp: { active: 0, established: 0 },
        udp: { active: 0 },
        http: { connections: 0 },
        https: { connections: 0 },
        dns: { queries: 0 }
      },
      protocol_breakdown: rawNetworkData.protocol_breakdown || {
        web: 0,
        email: 0,
        streaming: 0,
        gaming: 0,
        file_transfer: 0,
        other: 0
      },
      top_bandwidth_processes: rawNetworkData.top_bandwidth_processes || 
                               (rawNetworkData as any).processes || [],

      dns_metrics: rawNetworkData.dns_metrics,
      internet_metrics: rawNetworkData.internet_metrics
    };
    
    return { networkData: processedData, error: null };
  } catch (err) {
    console.error('Error processing network data:', err);
    return { 
      networkData: null, 
      error: `Failed to process network data: ${err instanceof Error ? err.message : 'Unknown error'}` 
    };
  }
}

/**
 * Processes interface data which might be in different formats
 */
function processInterfacesData(interfaces: any): NetworkInterface[] {
  if (!interfaces) return [];
  
  if (Array.isArray(interfaces)) {
    return interfaces.map(iface => ({
      name: iface.name || 'Unknown',
      isup: iface.isup || false,
      bytes_sent: iface.bytes_sent || 0,
      bytes_recv: iface.bytes_recv || 0,
      address: iface.address,
      mac_address: iface.mac_address,
      speed: iface.speed,
      mtu: iface.mtu
    }));
  }
  
  if (typeof interfaces === 'object') {
    return Object.entries(interfaces).map(([name, details]) => ({
      name,
      isup: (details as any).isup || false,
      bytes_sent: (details as any).bytes_sent || 0,
      bytes_recv: (details as any).bytes_recv || 0,
      address: (details as any).address,
      mac_address: (details as any).mac_address,
      speed: (details as any).speed,
      mtu: (details as any).mtu
    }));
  }
  
  return [];
}

export default processNetworkData;