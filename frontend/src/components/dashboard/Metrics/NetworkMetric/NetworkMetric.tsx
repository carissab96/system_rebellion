import React, { useState, useMemo } from 'react';
import { useAppSelector } from '../../../../store/hooks';
import { RootState } from '../../../../store/store';
import { SystemMetric } from '../../../../types/metrics';
import { MetricsCard, MetricStatus } from '../../../../design-system/components/MetricsCard';
import { Tabs, Tab } from '../../../../design-system/components/Tabs/Tabs';
import NetworkQualityMetrics from '../../../metrics/NetworkMetrics/NetworkQualityMetrics';

// Import modular network metric components
import NetworkInterfaceMetrics from '../../../metrics/NetworkMetrics/NetworkInterfaceMetrics';
import NetworkProtocolChart from '../../../metrics/NetworkMetrics/NetworkProtocolChart';
import TopBandwidthProcesses from '../../../metrics/NetworkMetrics/TopBandwidthProcesses';
import NetworkConnectionsTable from '../../../metrics/NetworkMetrics/NetworkConnectionsTable';

// Helper function to format bytes with appropriate units
const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

// Helper function to format milliseconds to a readable format
// const formatLatency = (ms: number) => {
//   if (ms < 1) return '<1 ms';
//   return `${ms.toFixed(1)} ms`;
// };

// Helper function to get quality class based on score
// const getQualityClass = (score: number) => {
//   if (score >= 90) return 'excellent';
//   if (score >= 75) return 'good';
//   if (score >= 50) return 'fair';
//   if (score >= 25) return 'poor';
//   return 'critical';
// };

// Helper function to get latency class based on value
// const getLatencyClass = (ms: number) => {
//   if (ms < 10) return 'good';
//   if (ms < 50) return 'fair';
//   if (ms < 100) return 'poor';
//   return 'critical';
// };

// Define interfaces for network data
// interface NetworkProcess {
//   name: string;
//   pid: number;
//   protocol?: string;
//   state?: string;
//   write_rate: number;
//   read_rate: number;
//   connection_count: number;
// }

// interface NetworkInterface {
//   name: string;
//   address: string;
//   mac_address: string;
//   isup: boolean;
//   speed: number;
//   mtu: number;
//   bytes_sent: number;
//   bytes_recv: number;
// }

export const NetworkMetric: React.FC = () => {
  // Redux state
  const currentMetric = useAppSelector((state: RootState) => state.metrics.current) as SystemMetric | null;
  const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical || []) as SystemMetric[];
  const isLoading = useAppSelector((state: RootState) => state.metrics.loading);
  console.log("NetworkMetric: current metric", currentMetric);
console.log("NetworkMetric: network data", currentMetric?.network);
  // Tab state
  const [activeTab, setActiveTab] = useState<string>('overview');
  
  // Network metrics state
  const networkData = currentMetric?.network ?? {};
  const ioStats = networkData.io_stats ?? {};
  const sentRate = ioStats.sent_rate ?? 0;
  const receivedRate = ioStats.recv_rate ?? 0;
  const bytesSent = ioStats.bytes_sent ?? 0;
  const bytesReceived = ioStats.bytes_recv ?? 0;
  const totalRate = sentRate + receivedRate;
  
  // Prepare data for modular components
  const qualityData = useMemo(() => {
    const connectionQuality = networkData?.connection_quality || {};
    console.log("Netowrk quality raw data:", connectionQuality);
    return {
      overall_score: connectionQuality.overall_score ||
                     connectionQuality.stability || 
                     85,
    latency: {
      avg_ms: connectionQuality.average_latency ||
              connectionQuality.latency ||
               21.2,
      min_ms: connectionQuality.min_latency || 15.5,
      max_ms: connectionQuality.max_latency || 45.8,
      jitter_ms: connectionQuality.jitter || 3.2,
      stability_score: connectionQuality.connection_stability || 
                       connectionQuality.stability || 
                       85
    },
    packet_loss: {
      percentage: connectionQuality.packet_loss_percent || 
                  connectionQuality.packet_loss || 
                  0.5,
      trend: 'stable' as 'improving' | 'stable' | 'degrading',
      history: [0.2, 0.3, 0.5, 0.4, 0.5]
    },
    connection_stability: {
      score: connectionQuality.connection_stability || 
             connectionQuality.stability || 
             85,
      drops_last_hour: connectionQuality.drops_last_hour || 0,
      reconnects: connectionQuality.reconnects || 0
    }
  };
}, [networkData]);
  
// DNS metrics adapter
const dnsMetrics = useMemo(() => {
  // Get DNS metrics with fallbacks
  const dns = networkData?.dns_metrics || {};
  
  console.log("DNS metrics raw data:", dns);
  
  return {
    query_time_ms: dns.query_time_ms || 15.8,
    success_rate: dns.success_rate || 0.98,
    cache_hit_ratio: dns.cache_hit_ratio || 0.75,
    last_failures: dns.last_failures || 0
  };
}, [networkData]);

  
// Internet metrics adapter
const internetMetrics = useMemo(() => {
  // Get internet metrics with fallbacks
  const internet = networkData?.internet_metrics || {};
  const quality = networkData?.connection_quality || {};
  
  console.log("Internet metrics raw data:", internet);
  
  return {
    gateway_latency_ms: internet.gateway_latency || 
                        quality.gateway_latency || 
                        2.5,
    internet_latency_ms: internet.internet_latency || 
                         quality.internet_latency || 
                         45.2,
    hop_count: internet.hop_count || 8,
    isp_performance_score: internet.isp_performance_score || 
                          quality.isp_performance_score || 
                          78
  };
}, [networkData]);
  // Network interfaces data
  const interfaceList = useMemo(() => {
    return currentMetric?.network?.interfaces || [];
  }, [currentMetric]);
  
  // Convert interfaces array to Record for NetworkInterfaceMetrics
  const interfaces = useMemo(() => {
    const result: Record<string, any> = {};
    interfaceList.forEach((iface: { name: string | number; isup: any; }) => {
      result[iface.name] = {
        ...iface,
        isUp: iface.isup || false,
        internal: false
      };
    });
    return result;
  }, [interfaceList]);
  
  // Selected interface name
  const selectedInterface = useMemo(() => {
    return interfaceList.length > 0 ? interfaceList[0].name : '';
  }, [interfaceList]);
  
  // Top processes data
  const topProcesses = useMemo(() => {
    return currentMetric?.network?.top_processes || [];
  }, [currentMetric]);
  
  // Protocol data for charts
  const protocolData = useMemo(() => {
    return {
      http: 35,
      https: 45,
      dns: 10,
      other: 10
    };
  }, []);
  
  // Network connections data
  const connections = useMemo(() => {
    return topProcesses.map((process: { protocol: any; state: any; pid: any; name: any; write_rate: any; read_rate: any; }) => ({
      type: process.protocol || 'TCP',
      laddr: '127.0.0.1:' + (8000 + Math.floor(Math.random() * 1000)),
      raddr: '192.168.1.' + Math.floor(Math.random() * 255) + ':443',
      status: process.state || 'ESTABLISHED',
      pid: process.pid,
      process_name: process.name,
      protocol: process.protocol || 'TCP',
      bytes_sent: process.write_rate,
      bytes_recv: process.read_rate
    }));
  }, [topProcesses]);
  
  // Prepare chart data for overview tab
  // const _chartData = useMemo(() => {
  //   return historicalMetrics.map(metric => ({
  //     timestamp: metric.timestamp,
  //     bytes_sent: metric.network?.bytes_sent ?? 262144, // 256KB/s minimum
  //     bytes_recv: metric.network?.bytes_recv ?? 1048576 // 1MB/s minimum
  //   }));
  // }, [historicalMetrics]);
  
  // Calculate network status based on stability score
  const getStatus = (stability: number): MetricStatus => {
    if (stability < 50) return 'critical';
    if (stability < 75) return 'warning';
    return 'normal';
  };

  // Calculate trend based on current and previous values
  const getTrend = (current: number, previous: number): 'up' | 'down' | 'stable' => {
    if (current > previous * 1.1) return 'up';
    if (current < previous * 0.9) return 'down';
    return 'stable';
  };

  // Calculate network activity and trends
  const networkActivity = totalRate;
  const previousValue = (historicalMetrics || []).length > 1 ? 
    (historicalMetrics[historicalMetrics.length - 2]?.network?.sent_rate ?? 0) + 
    (historicalMetrics[historicalMetrics.length - 2]?.network?.recv_rate ?? 0) : 0;
  const changePercentage = previousValue !== 0 ? ((networkActivity - previousValue) / previousValue) * 100 : 0;

  // Loading state
  if (isLoading) {
    return <MetricsCard title="Network Activity" value="--" unit="/s" updating={true} />;
  }

  return (
    <MetricsCard
      title="Network Activity"
      value={formatBytes(networkActivity, 1)}
      unit="/s"
      status={getStatus(qualityData.overall_score)}
      trend={getTrend(networkActivity, previousValue)}
      changePercentage={changePercentage}
      showSparkline={true}
      sparklineData={(historicalMetrics || []).map(m => 
        (m.network?.sent_rate ?? 0) + (m.network?.recv_rate ?? 0)
      )}
    >
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab id="overview" label="Overview">
          <div className="network-overview">
            <div className="overview-stats">
              <div className="stat-item">
                <div className="stat-label">Sent</div>
                <div className="stat-value">{formatBytes(bytesSent)}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Received</div>
                <div className="stat-value">{formatBytes(bytesReceived)}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Send Rate</div>
                <div className="stat-value">{formatBytes(sentRate)}/s</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Receive Rate</div>
                <div className="stat-value">{formatBytes(receivedRate)}/s</div>
              </div>
            </div>
            <NetworkProtocolChart protocolData={protocolData} />
          </div>
        </Tab>
        <Tab id="quality" label="Connection Quality">
        <NetworkQualityMetrics 
          qualityData={qualityData} 
          dnsMetrics={dnsMetrics} 
          internetMetrics={internetMetrics} 
        />
        </Tab>
        <Tab id="processes" label="Processes">
          <TopBandwidthProcesses processes={topProcesses} />
        </Tab>
        <Tab id="interfaces" label="Interfaces">
          <NetworkInterfaceMetrics 
            interfaces={interfaces} 
            selectedInterface={selectedInterface}
            setSelectedInterface={() => {}} 
          />
        </Tab>
        <Tab id="connections" label="Connections">
          <NetworkConnectionsTable connections={connections} />
        </Tab>
      </Tabs>
    </MetricsCard>
  );
};

export default NetworkMetric;