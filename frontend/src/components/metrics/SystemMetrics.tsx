import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { initializeWebSocket } from '../../store/slices/metricsSlice';

// Dashboard metric components (summary views)
import CPUMetric from '../dashboard/Metrics/CPUMetrics/CPUMetric';
import MemoryMetric from '../dashboard/Metrics/MemoryMetric/MemoryMetric';
import DiskMetric from '../dashboard/Metrics/DiskMetric/DiskMetric';
import { NetworkMetric } from '../dashboard/Metrics/NetworkMetric/NetworkMetric';
import { SystemStatus } from '../dashboard/Dashboard/SystemStatus/SystemStatus';

// Detailed network metrics components
import NetworkConnectionsTable from './NetworkMetrics/NetworkConnectionsTable';
import NetworkProtocolChart from './NetworkMetrics/NetworkProtocolChart';
import NetworkInterfaceMetrics from './NetworkMetrics/NetworkInterfaceMetrics';
import NetworkQualityMetrics from './NetworkMetrics/NetworkQualityMetrics';
import TopBandwidthProcesses from './NetworkMetrics/TopBandwidthProcesses';

// UI Components
import { Button } from '../../design-system/components/Button/Button';
import { Card } from '../../design-system/components/Card';

// Character icons
import { SirHawkington, MethSnail, Hamster, TheStick, QuantumShadowPerson } from '../common/CharacterIcons';

// Styles
import './SystemMetrics.css';

// Define a simple Tabs component until we create a proper one
interface TabProps {
  id: string;
  label: string;
  children: React.ReactNode;
}

const Tab: React.FC<TabProps> = ({ children }) => {
  return <div className="tab-content">{children}</div>;
};

interface TabsProps {
  activeTab: string;
  onChange: (tabId: string) => void;
  children: React.ReactElement<TabProps>[];
}

const Tabs: React.FC<TabsProps> = ({ activeTab, onChange, children }) => {
  return (
    <div className="tabs-container">
      <div className="tabs-header">
        {React.Children.map(children, (child) => (
          <div 
            className={`tab-button ${activeTab === child.props.id ? 'active' : ''}`}
            onClick={() => onChange(child.props.id)}
          >
            {child.props.label}
          </div>
        ))}
      </div>
      <div className="tabs-content">
        {React.Children.map(children, (child) => (
          activeTab === child.props.id ? child : null
        ))}
      </div>
    </div>
  );
};

/**
 * SystemMetrics Component
 * 
 * Displays detailed system metrics with tabbed navigation for different metric types.
 * Sir Hawkington oversees this distinguished metrics observatory with aristocratic splendor.
 */
const SystemMetrics: React.FC = () => {
  const dispatch = useAppDispatch();
  const error = useAppSelector((state) => state.metrics.error);
  const isLoading = useAppSelector((state) => state.metrics.loading);
  
  // Use any type for metrics until we update the metrics slice type definitions
  const metrics: any = useAppSelector((state) => state.metrics);
  const currentMetrics = metrics?.current || {};
  const networkMetrics = currentMetrics?.network || {};
  
  // Debug output to console
  useEffect(() => {
    console.log('Current metrics state:', metrics);
    console.log('Network metrics:', networkMetrics);
  }, [metrics, networkMetrics]);
  
  // Debug logs to see what data we're getting
  console.log('🎩 Sir Hawkington is inspecting the metrics state:', metrics);
  console.log('🌐 Network metrics:', networkMetrics);
  
  // Tab state
  const [activeTab, setActiveTab] = useState('overview');
  
  // Time range state
  const [timeRange, setTimeRange] = useState('1h');
  
  useEffect(() => {
    // Initialize WebSocket connection for metrics
    dispatch(initializeWebSocket());

    return () => {
      // No need to clean up as the websocket service handles this
    };
  }, [dispatch]);

  const handleRefresh = () => {
    // Force refresh metrics
    dispatch(initializeWebSocket());
  };

  const renderTimeRangeButtons = () => (
    <div className="time-range-controls">
      <Button 
        size="sm" 
        variant={timeRange === '1h' ? 'primary' : 'secondary'}
        onClick={() => setTimeRange('1h')}
      >
        1h
      </Button>
      <Button 
        size="sm" 
        variant={timeRange === '6h' ? 'primary' : 'secondary'}
        onClick={() => setTimeRange('6h')}
      >
        6h
      </Button>
      <Button 
        size="sm" 
        variant={timeRange === '24h' ? 'primary' : 'secondary'}
        onClick={() => setTimeRange('24h')}
      >
        24h
      </Button>
      <Button 
        size="sm" 
        variant={timeRange === '7d' ? 'primary' : 'secondary'}
        onClick={() => setTimeRange('7d')}
      >
        7d
      </Button>
    </div>
  );

  return (
    <div className="system-metrics-container">
      <header className="metrics-header">
        <div className="metrics-header-top">
          <h1>
            <SirHawkington className="large-icon" /> 
            System Metrics
          </h1>
          <div className="metrics-controls">
            {renderTimeRangeButtons()}
            <Button 
              variant="accent" 
              onClick={handleRefresh}
              disabled={isLoading}
            >
              {isLoading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>
        <SystemStatus loading={isLoading} error={error} />
        <div className="metrics-subtitle">
          <p>"Sir Hawkington's Distinguished Metrics Observatory"</p>
        </div>
      </header>
      
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab id="overview" label="Overview">
          <div className="metrics-content">
            <div className="metrics-grid">
              <CPUMetric />
              <MemoryMetric />
              <DiskMetric />
              <NetworkMetric />
            </div>
          </div>
        </Tab>
        
        <Tab id="network" label="Network Metrics">
          <div className="metrics-detailed-content">
            <div className="metrics-section-header">
              <h2>Network Metrics</h2>
              <p className="metrics-quote">
                <QuantumShadowPerson className="small-icon" />
                "The quantum shadow people suggested routing through /dev/null, but Sir Hawkington vetoed with extreme prejudice."
              </p>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel network-summary-panel">
                <h3>Network Summary</h3>
                <div className="network-summary-stats">
                  <div className="network-stat">
                    <span className="stat-label">Total Sent</span>
                    <span className="stat-value">{networkMetrics?.io_stats?.bytes_sent_formatted || '0 B'}</span>
                  </div>
                  <div className="network-stat">
                    <span className="stat-label">Total Received</span>
                    <span className="stat-value">{networkMetrics?.io_stats?.bytes_recv_formatted || '0 B'}</span>
                  </div>
                  <div className="network-stat">
                    <span className="stat-label">Current Rate</span>
                    <span className="stat-value">
                      {networkMetrics?.io_stats?.total_rate_formatted || '0 B/s'}
                    </span>
                  </div>
                  <div className="network-stat">
                    <span className="stat-label">Connection Quality</span>
                    <span className="stat-value">
                      {networkMetrics?.connection_quality?.overall_score || 'N/A'}
                    </span>
                  </div>
                </div>
              </Card>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>Active Connections</h3>
                <NetworkConnectionsTable connections={networkMetrics?.connections || []} />
              </Card>
            </div>
            
            <div className="metrics-panels network-charts-grid">
              <Card className="metrics-panel">
                <h3>Protocol Distribution</h3>
                <NetworkProtocolChart protocolData={networkMetrics?.protocol_breakdown || {}} />
              </Card>
              
              <Card className="metrics-panel">
                <h3>Top Bandwidth Processes</h3>
                <TopBandwidthProcesses processes={networkMetrics?.top_bandwidth_processes || []} />
              </Card>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>Network Interfaces</h3>
                <NetworkInterfaceMetrics 
                  interfaces={networkMetrics?.interfaces || []} 
                  interfaceStats={networkMetrics?.interface_stats || {}} 
                />
              </Card>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>Connection Quality</h3>
                <NetworkQualityMetrics 
                  qualityData={networkMetrics?.connection_quality || {}} 
                  dnsMetrics={networkMetrics?.dns_metrics || {}} 
                  internetMetrics={networkMetrics?.internet_metrics || {}} 
                />
              </Card>
            </div>
          </div>
        </Tab>
        
        <Tab id="cpu" label="CPU Metrics">
          <div className="metrics-detailed-content">
            <div className="metrics-section-header">
              <h2>CPU Metrics</h2>
              <p className="metrics-quote">
                <MethSnail className="small-icon" />
                "The Meth Snail suggests overclocking your CPU with cosmic energy, but Sir Hawkington recommends proper thermal management instead."
              </p>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>CPU Metrics Coming Soon</h3>
                <p>Detailed CPU metrics will be implemented in the next phase.</p>
                <p>The Meth Snail is currently working on this feature while consuming Red Bull #138.</p>
              </Card>
            </div>
          </div>
        </Tab>
        
        <Tab id="memory" label="Memory Metrics">
          <div className="metrics-detailed-content">
            <div className="metrics-section-header">
              <h2>Memory Metrics</h2>
              <p className="metrics-quote">
                <Hamster className="small-icon" />
                "The Hamsters have applied duct tape to your memory modules, resulting in 74% more aristocratic efficiency."
              </p>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>Memory Metrics Coming Soon</h3>
                <p>Detailed memory metrics will be implemented in the next phase.</p>
                <p>The Hamsters are currently applying duct tape to this feature.</p>
              </Card>
            </div>
          </div>
        </Tab>
        
        <Tab id="disk" label="Disk Metrics">
          <div className="metrics-detailed-content">
            <div className="metrics-section-header">
              <h2>Disk Metrics</h2>
              <p className="metrics-quote">
                <TheStick className="small-icon" />
                "The Stick insists on proper disk partitioning according to regulatory standards, but we've ignored that advice."
              </p>
            </div>
            
            <div className="metrics-panels">
              <Card className="metrics-panel">
                <h3>Disk Metrics Coming Soon</h3>
                <p>Detailed disk metrics will be implemented in the next phase.</p>
                <p>The Stick is currently having an anxiety attack about this feature.</p>
              </Card>
            </div>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default SystemMetrics;
