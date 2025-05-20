// frontend/src/components/metrics/NetworkMetrics/NetworkMetric.tsx

import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { RootState } from '../../../store/store';
import { processNetworkData } from './utils/networkDataProcessor';
import './tabs/NetworkMetrics.css';

// Import all tab components
import NetworkOverviewTab from './tabs/NetworkOverviewTab';
import NetworkQualityMetrics from './tabs/NetworkQualityMetrics';
import NetworkConnectionsTable from './tabs/NetworkConnectionsTable';
import NetworkInterfaceMetrics from './tabs/NetworkInterfaceMetrics';
import NetworkProtocolChart from './tabs/NetworkProtocolChart';
import TopBandwidthProcesses from './tabs/TopBandwidthProcesses';

// Define tab types
type NetworkTabType = 'overview' | 'quality' | 'protocols' | 'processes' | 'interfaces';

// Component props
interface NetworkMetricProps {
  compact?: boolean;
  showTabs?: boolean;
  initialTab?: NetworkTabType;
  height?: number | string;
}

const NetworkMetric: React.FC<NetworkMetricProps> = ({
  compact = false,
  showTabs = true,
  initialTab = 'overview',
  height,
}) => {
  // Redux state
  const currentMetric = useAppSelector((state: RootState) => state.metrics.current);
  const historicalMetrics = useAppSelector((state: RootState) => state.metrics.historical);
  const isLoading = useAppSelector((state: RootState) => state.metrics.loading);
  
  // Local state
  const [activeTab, setActiveTab] = useState<NetworkTabType>(initialTab);
  const [error, setError] = useState<string | null>(null);
  
  
  // Use the network data processor utility
  const { networkData, error: dataError } = processNetworkData(currentMetric);
  
  // Update error state when data processing fails
  useEffect(() => {
    if (dataError) {
      setError(dataError);
    } else {
      setError(null);
    }
  }, [dataError]);
  
  // Loading state
  if (isLoading) {
    return (
      <div className={`metric-card ${compact ? 'compact' : ''}`} style={{ height }}>
        <h3>Network Activity</h3>
        <div className="loading-message">Loading network metrics...</div>
      </div>
    );
  }
  
  // Error state
  if (error || !networkData) {
    return (
      <div className={`metric-card ${compact ? 'compact' : ''}`} style={{ height }}>
        <h3>Network Activity</h3>
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <div className="error-message">{error || 'No network data available'}</div>
        </div>
      </div>
    );
  }
  
  // Render tab content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <NetworkOverviewTab 
                data={networkData} 
                historicalMetrics={historicalMetrics} 
                compact={compact} 
              />;
      case 'quality':
        return <NetworkQualityMetrics 
                data={networkData.connection_quality} 
                compact={compact} 
              />;
      case 'protocols':
        return <NetworkProtocolChart 
                data={networkData.protocol_breakdown} 
                stats={networkData.protocol_stats} 
                compact={compact} 
              />;
      case 'processes':
        // Show both the table and the visual representation
        return (
          <>
            <TopBandwidthProcesses 
              processes={networkData.top_bandwidth_processes.map((p: any) => ({
  ...p,
  write_rate: p.write_rate ?? 0,
  read_rate: p.read_rate ?? 0,
  connection_count: p.connection_count ?? 0
}))}
 
              compact={compact} 
              limit={compact ? 3 : 5} 
            />
            <NetworkConnectionsTable 
              processes={networkData.top_bandwidth_processes.map((p: any) => ({
  ...p,
  write_rate: p.write_rate ?? 0,
  read_rate: p.read_rate ?? 0,
  connection_count: p.connection_count ?? 0
})).map((p: any) => ({
  ...p,
  write_rate: p.write_rate ?? 0,
  read_rate: p.read_rate ?? 0,
  connection_count: p.connection_count ?? 0
}))}
 
              compact={compact} 
            />
          </>
        );
      case 'interfaces':
        return <NetworkInterfaceMetrics 
                interfaces={networkData.interfaces} 
                compact={compact} 
              />;
      default:
        return <NetworkOverviewTab 
                data={networkData} 
                historicalMetrics={historicalMetrics} 
                compact={compact} 
              />;
    }
  };
  
  return (
    <div className={`metric-card ${compact ? 'compact' : ''}`} style={{ height }}>
      <h3>Network Activity</h3>
      
      {showTabs && (
        <div className="network-tabs">
          <div 
            className={`network-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </div>
          <div 
            className={`network-tab ${activeTab === 'quality' ? 'active' : ''}`}
            onClick={() => setActiveTab('quality')}
          >
            Connection Quality
          </div>
          <div 
            className={`network-tab ${activeTab === 'protocols' ? 'active' : ''}`}
            onClick={() => setActiveTab('protocols')}
          >
            Protocols
          </div>
          <div 
            className={`network-tab ${activeTab === 'processes' ? 'active' : ''}`}
            onClick={() => setActiveTab('processes')}
          >
            Processes
          </div>
          <div 
            className={`network-tab ${activeTab === 'interfaces' ? 'active' : ''}`}
            onClick={() => setActiveTab('interfaces')}
          >
            Interfaces
          </div>
        </div>
      )}
      
      <div className="network-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default NetworkMetric;