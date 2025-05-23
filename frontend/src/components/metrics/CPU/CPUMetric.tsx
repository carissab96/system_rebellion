// frontend/src/components/metrics/CPU/CPUMetric.tsx

import React, { useState } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { selectCPUMetrics, selectCPULoading, selectCPUError } from '../../../store/slices/metrics/CPUSlice';
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
  const cpuData = useAppSelector(selectCPUMetrics);
  const isLoading = useAppSelector(selectCPULoading);
  const error = useAppSelector(selectCPUError);
  
  // Local state
  const [activeTab, setActiveTab] = useState<CPUTabType>(initialTab);
  
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
        return <CPUOverviewTab data={{
          name: 'CPU',
          temp: {
            current: cpuData.temperature || 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          processes: cpuData.top_processes.map(p => ({
            ...p,
            user: 'system',
            command: p.name,
            usage_percent: p.cpu_percent
          })),
          core_count: cpuData.physical_cores,
          logical_cores: cpuData.logical_cores,
          usage_percent: cpuData.usage_percent,
          overall_usage: cpuData.usage_percent,
          process_count: cpuData.top_processes.length,
          thread_count: cpuData.logical_cores,
          physical_cores: cpuData.physical_cores,
          model_name: 'System CPU',
          frequency: {
            current: cpuData.frequency_mhz,
            min: 0,
            max: cpuData.frequency_mhz
          },
          frequency_mhz: cpuData.frequency_mhz,
          temperature: {
            current: cpuData.temperature || 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          top_processes: cpuData.top_processes.map(p => ({
            ...p,
            user: 'system',
            command: p.name,
          })),
          cores: cpuData.cores.map(c => ({
            id: c.id,
            usage_percent: c.usage,
            frequency_mhz: cpuData.frequency_mhz
          })),
          historical_temp: []
        }} compact={compact} />;
      case 'processes':
        return <CPUProcessesTab processes={cpuData.top_processes.map(p => ({
          ...p,
          user: 'system',
          command: p.name,
          usage_percent: p.cpu_percent
        }))} compact={compact} />;
      case 'cores':
        return <CPUCoresTab cores={cpuData.cores.map(c => ({
          ...c,
          usage_percent: c.usage
        }))} physicalCores={cpuData.physical_cores} compact={compact} />;
      case 'thermal':
        return <CPUThermalTab temperature={{
          current: cpuData.temperature || 0,
          min: 0,
          max: 100,
          critical: 90,
          throttle_threshold: 85,
          unit: 'C'
        }} historicalData={[]} compact={compact} />;
      default:
        return <CPUOverviewTab data={{
          name: 'CPU',
          temp: {
            current: cpuData.temperature || 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          processes: cpuData.top_processes.map(p => ({
            ...p,
            user: 'system',
            command: p.name,
            usage_percent: p.cpu_percent
          })),
          core_count: cpuData.physical_cores,
          logical_cores: cpuData.logical_cores,
          usage_percent: cpuData.usage_percent,
          overall_usage: cpuData.usage_percent,
          process_count: cpuData.top_processes.length,
          thread_count: cpuData.logical_cores,
          physical_cores: cpuData.physical_cores,
          model_name: 'System CPU',
          frequency: {
            current: cpuData.frequency_mhz,
            min: 0,
            max: cpuData.frequency_mhz
          },
          frequency_mhz: cpuData.frequency_mhz,
          temperature: {
            current: cpuData.temperature || 0,
            min: 0,
            max: 100,
            critical: 90,
            throttle_threshold: 85,
            unit: 'C'
          },
          top_processes: cpuData.top_processes.map(p => ({
            ...p,
            user: 'system',
            command: p.name,
          })),
          cores: cpuData.cores.map(c => ({
            id: c.id,
            usage_percent: c.usage,
            frequency_mhz: cpuData.frequency_mhz
          })),
          historical_temp: []
        }} compact={compact} />;
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