//Main Component
// frontend/src/components/metrics/CPU/CPUMetric.tsx

import React, { useState } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { RootState } from '../../../store/store';
import { processCPUData } from './Utils/cpuDataProcessor';
import CPUOverviewTab from './Tabs/CPUOverviewTab';
import CPUProcessesTab from './Tabs/CPUProcessesTab';
import CPUCoresTab from './Tabs/CPUCoresTab';
import CPUThermalTab from './Tabs/CPUThermalTab';
import './CPUMetric.css';

type CPUTabType = 'overview' | 'processes' | 'cores' | 'thermal';

interface CPUMetricProps {
  compact?: boolean;
  showTabs?: boolean;
  initialTab?: CPUTabType;
  height?: number | string;
}

const CPUMetric: React.FC<CPUMetricProps> = ({
  compact = false,
  showTabs = true,
  initialTab = 'overview',
  height,
}) => {
  // Redux state
  const currentMetric = useAppSelector((state: RootState) => state.metrics.current);
  const isLoading = useAppSelector((state: RootState) => state.metrics.loading);
  
  // Local state
  const [activeTab, setActiveTab] = useState<CPUTabType>(initialTab);
  const [error, setError] = useState<string | null>(null);
  
  // Process CPU data
  const { cpuData, error: dataError } = processCPUData(currentMetric);
  
  // Handle errors
  React.useEffect(() => {
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
        <h3>CPU Activity</h3>
        <div className="loading-message">Loading CPU metrics...</div>
      </div>
    );
  }
  
  // Error state
  if (error || !cpuData) {
    return (
      <div className={`metric-card ${compact ? 'compact' : ''}`} style={{ height }}>
        <h3>CPU Activity</h3>
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <div className="error-message">{error || 'No CPU data available'}</div>
        </div>
      </div>
    );
  }
  
  // Render tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <CPUOverviewTab data={cpuData} compact={compact} />;
      case 'processes':
        return <CPUProcessesTab processes={cpuData.top_processes} compact={compact} />;
      case 'cores':
        return <CPUCoresTab cores={cpuData.cores} physicalCores={cpuData.physical_cores} compact={compact} />;
      case 'thermal':
        return <CPUThermalTab temperature={cpuData.temperature} historicalData={cpuData.historical_temp} compact={compact} />;
      default:
        return <CPUOverviewTab data={cpuData} compact={compact} />;
    }
  };

  return (
    <div className={`metric-card ${compact ? 'compact' : ''}`} style={{ height }}>
      <h3>CPU Activity</h3>
      
      {showTabs && (
        <div className="cpu-tabs">
          <div 
            className={`cpu-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </div>
          <div 
            className={`cpu-tab ${activeTab === 'processes' ? 'active' : ''}`}
            onClick={() => setActiveTab('processes')}
          >
            Processes
          </div>
          <div 
            className={`cpu-tab ${activeTab === 'cores' ? 'active' : ''}`}
            onClick={() => setActiveTab('cores')}
          >
            Cores
          </div>
          <div 
            className={`cpu-tab ${activeTab === 'thermal' ? 'active' : ''}`}
            onClick={() => setActiveTab('thermal')}
          >
            Thermal
          </div>
        </div>
      )}
      
      <div className="cpu-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default CPUMetric;