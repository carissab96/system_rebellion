// frontend/src/components/metrics/NetworkMetrics/NetworkMetric.tsx

import React, { useState } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { selectNetworkMetrics, selectNetworkHistorical } from '../../../store/slices/metrics/NetworkSlice';
import { NetworkDetails } from '../../../types/metrics';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { MetricsCard, MetricStatus } from '../../../design-system/components/MetricsCard';
import Tabs, { Tab } from '../../../design-system/components/Tabs';
import ErrorDisplay from '../../common/ErrorDisplay';
import LoadingIndicator from '../../common/LoadingIndicator';
import NetworkOverviewTab from './tabs/NetworkOverviewTab';
import NetworkInterfacesTab from './tabs/NetworkInterfacesTab';
import NetworkConnectionsTab from './tabs/NetworkConnectionsTab';
import './NetworkMetric.css';

interface NetworkMetricProps {
  compact?: boolean;
  defaultTab?: string;
  dashboardMode?: boolean; // Whether this is being used in the dashboard
  height?: number | string;
}

export const NetworkMetric: React.FC<NetworkMetricProps> = ({ 
  compact = false,
  defaultTab = 'overview',
  dashboardMode = false,
  height
}) => {
  type TabType = 'overview' | 'interfaces' | 'connections' | 'history';
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab as TabType);
  
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId as TabType);
  };

  // Get network metrics from the main metrics slice
  const currentMetric = useAppSelector(selectNetworkMetrics);
  const historicalMetrics = useAppSelector(selectNetworkHistorical);
  const loading = !currentMetric;
  const error = !currentMetric ? 'No metrics data available' : null;
  
  // Handle loading state
  if (loading) {
    return dashboardMode ? (
      <MetricsCard title="Network Traffic" value="--" unit="KB/s" updating={true} />
    ) : (
      <LoadingIndicator message="Fetching network metrics..." />
    );
  }
  
  // Handle error state
  if (error || !currentMetric) {
    return dashboardMode ? (
      <div className={`network-metric ${compact ? 'compact' : ''}`} style={{ height }}>
        <MetricsCard title="Network Traffic" value="--" unit="KB/s" status="critical" />
      </div>
    ) : (
      <ErrorDisplay 
        message="Unable to load network metrics" 
        details={typeof error === 'string' ? error : 'Unknown error occurred'} 
        retry={() => {}} 
      />
    );
  }

  // Extract network data from metrics
  const networkDetails: NetworkDetails = currentMetric.network || {
    bytes_sent: 0,
    bytes_recv: 0,
    packets_sent: 0,
    packets_recv: 0,
    rate_mbps: 0,
    sent_rate_bps: 0,
    recv_rate_bps: 0,
    io_stats: {
      bytes_sent: 0,
      bytes_recv: 0,
      packets_sent: 0,
      packets_recv: 0,
      sent_rate: 0,
      recv_rate: 0,
      errors_in: 0,
      errors_out: 0,
      drops_in: 0,
      drops_out: 0
    },
    interfaces: [],
    protocol_stats: {
      tcp: {
        active: 0,
        established: 0,
        listening: 0
      },
      udp: {
        active: 0
      },
      http: {
        connections: 0
      },
      https: {
        connections: 0
      },
      dns: {
        queries: 0
      }
    }
  };
  const networkReceiveRate = networkDetails.recv_rate_bps || 0;
  const networkTransmitRate = networkDetails.sent_rate_bps || 0;
  const totalNetworkRate = networkReceiveRate + networkTransmitRate;
  
  // Format bytes to human-readable format
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  // Format bytes per second
  const formatBytesPerSecond = (bytesPerSecond: number) => {
    return formatBytes(bytesPerSecond) + '/s';
  };

  // Calculate network status
  const getStatus = (rate: number): MetricStatus => {
    // These thresholds can be adjusted based on what's considered high network usage
    if (rate >= 10 * 1024 * 1024) return 'critical'; // 10 MB/s
    if (rate >= 5 * 1024 * 1024) return 'warning';   // 5 MB/s
    return 'normal';
  };

  // Prepare historical data for area chart
  const networkHistoryData = historicalMetrics?.map(metric => ({
    timestamp: new Date(metric.timestamp).getTime(),
    receive: metric.network?.recv_rate_bps || 0,
    transmit: metric.network?.sent_rate_bps || 0,
    total: (metric.network?.recv_rate_bps || 0) + (metric.network?.sent_rate_bps || 0)
  })) || [];

  // Prepare network interfaces data with correct property mapping
  const networkInterfaces = (networkDetails.interfaces || []).map(iface => ({
    name: iface.name,
    status: iface.isup ? 'Up' : 'Down',
    ip_address: iface.address || 'Unknown',
    mac_address: iface.mac_address || 'Unknown',
    receive_rate: iface.bytes_recv || 0,
    transmit_rate: iface.bytes_sent || 0
  }));
  
  // Prepare network connections data
  const networkConnections = networkDetails.protocol_stats?.tcp ? [
    {
      protocol: 'TCP',
      active: networkDetails.protocol_stats.tcp.active,
      listening: networkDetails.protocol_stats.tcp.listening || 0,
      established: networkDetails.protocol_stats.tcp.established
    }
  ] : [];

  // If using dashboard mode, render the dashboard style
  if (dashboardMode) {
    return (
      <div className="network-metric" style={{ height }}>
        <MetricsCard
          title="Network Traffic"
          value={formatBytes(totalNetworkRate / 1024).split(' ')[0]}
          unit={formatBytes(totalNetworkRate / 1024).split(' ')[1] + '/s'}
          status={getStatus(totalNetworkRate)}
        >
          <Tabs activeTab={activeTab} onChange={handleTabChange}>
            <Tab id="overview" label="Overview">
              <div className="overview-content">
                <div className="network-rates">
                  <div className="network-rate">
                    <span>Download:</span>
                    <span>{formatBytesPerSecond(networkReceiveRate)}</span>
                  </div>
                  <div className="network-rate">
                    <span>Upload:</span>
                    <span>{formatBytesPerSecond(networkTransmitRate)}</span>
                  </div>
                  <div className="network-rate">
                    <span>Total:</span>
                    <span>{formatBytesPerSecond(totalNetworkRate)}</span>
                  </div>
                </div>
              </div>
            </Tab>
            <Tab id="history" label="History">
              <div className="history-content">
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart
                    data={networkHistoryData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()} 
                    />
                    <YAxis tickFormatter={(value) => formatBytes(value).split(' ')[0] + ' ' + formatBytes(value).split(' ')[1]} />
                    <Tooltip 
                      labelFormatter={(timestamp) => new Date(timestamp as number).toLocaleString()}
                      formatter={(value, name) => [
                        formatBytesPerSecond(value as number), 
                        name === 'receive' ? 'Download' : name === 'transmit' ? 'Upload' : 'Total'
                      ]} 
                    />
                    <Area type="monotone" dataKey="receive" stackId="1" stroke="#8884d8" fill="#8884d8" name="Download" />
                    <Area type="monotone" dataKey="transmit" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Upload" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Tab>
            <Tab id="interfaces" label="Interfaces">
              <div className="interfaces-list">
                {networkInterfaces.map((iface, index) => (
                  <div key={index} className="interface-card">
                    <div className="interface-name">{iface.name}</div>
                    <div className="interface-status">{iface.status}</div>
                    <div className="interface-details">
                      <span>IP: {iface.ip_address}</span>
                      <span>MAC: {iface.mac_address}</span>
                      <span>Download: {formatBytesPerSecond(iface.receive_rate || 0)}</span>
                      <span>Upload: {formatBytesPerSecond(iface.transmit_rate || 0)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Tab>
          </Tabs>
        </MetricsCard>
      </div>
    );
  }
  
  // Prepare network data for component tabs
  const networkData = {
    overview: {
      receiveRate: networkReceiveRate,
      transmitRate: networkTransmitRate,
      totalReceived: networkDetails.bytes_recv || 0,
      totalTransmitted: networkDetails.bytes_sent || 0,
      packetErrors: networkDetails.io_stats?.errors_in || 0,
      packetDrops: networkDetails.io_stats?.drops_in || 0,
      io_stats: networkDetails.io_stats || {
        bytes_sent: networkDetails.bytes_sent || 0,
        bytes_recv: networkDetails.bytes_recv || 0,
        sent_rate: networkDetails.sent_rate_bps || 0,
        recv_rate: networkDetails.recv_rate_bps || 0,
        errors_in: 0,
        errors_out: 0,
        drops_in: 0,
        drops_out: 0
      },
      connection_quality: networkDetails.connection_quality || {
        average_latency: 0,
        packet_loss_percent: 0,
        connection_stability: 100,
        jitter: 0,
        gateway_latency: 0,
        dns_latency: 0,
        internet_latency: 0
      },
      protocol_breakdown: networkDetails.protocol_breakdown || {
        web: 30,
        email: 10,
        streaming: 25,
        gaming: 15,
        file_transfer: 10,
        other: 10
      },
      protocol_stats: networkDetails.protocol_stats || {
        tcp: { active: 0, established: 0 },
        udp: { active: 0 },
        http: { connections: 0 },
        https: { connections: 0 },
        dns: { queries: 0 }
      },
      top_bandwidth_processes: networkDetails.top_bandwidth_processes || []
    },
    interfaces: networkInterfaces,
    connections: networkConnections,
    history: networkHistoryData
  };
  
  // Render compact version for dashboard if requested
  if (compact) {
    return (
      <div className="network-metric network-metric--compact">
        <NetworkOverviewTab 
          data={networkData.overview} 
          historicalMetrics={networkData.history}
          compact={true} 
        />
      </div>
    );
  }
  
  // Render full tabbed version for component mode
  return (
    <div className={`network-metric ${compact ? 'compact' : ''}`}>
      <Tabs activeTab={activeTab} onChange={handleTabChange}>
        <Tab id="overview" label="Overview">
          <NetworkOverviewTab 
            data={networkData.overview} 
            historicalMetrics={networkData.history}
            compact={compact} 
          />
        </Tab>
        <Tab id="interfaces" label="Interfaces">
          <NetworkInterfacesTab interfaces={networkData.interfaces} />
        </Tab>
        <Tab id="connections" label="Connections">
          <NetworkConnectionsTab 
            connections={networkData.connections} 
            processes={networkData.overview.top_bandwidth_processes} 
          />
        </Tab>
        <Tab id="history" label="History">
          <div className="history-content">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart
                data={networkData.history}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()} 
                />
                <YAxis tickFormatter={(value) => formatBytes(value).split(' ')[0] + ' ' + formatBytes(value).split(' ')[1]} />
                <Tooltip 
                  labelFormatter={(timestamp) => new Date(timestamp as number).toLocaleString()}
                  formatter={(value, name) => [
                    formatBytesPerSecond(value as number), 
                    name === 'receive' ? 'Download' : name === 'transmit' ? 'Upload' : 'Total'
                  ]} 
                />
                <Legend />
                <Area type="monotone" dataKey="receive" stroke="#8884d8" fill="#8884d8" name="Download" />
                <Area type="monotone" dataKey="transmit" stroke="#82ca9d" fill="#82ca9d" name="Upload" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default NetworkMetric;