import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import Tabs, { Tab } from '@/design-system/components/Tabs';
import ErrorDisplay from '@/components/common/ErrorDisplay';
import LoadingIndicator from '@/components/common/LoadingIndicator';
import DiskPartitionsTab from './tabs/DiskPartitionsTab';
import { DiskDirectoryTab } from './tabs/DiskDirectoryTab';
import { DiskPerformanceTab } from './tabs/DiskPerformanceTab';
import { processDiskData } from './utils/diskDataProcessor';
import { DiskMetricProps, RawDiskMetrics } from './tabs/types';

export const DiskMetric: React.FC<DiskMetricProps> = ({ 
  compact = false,
  defaultTab = 'partitions' 
}) => {
  type TabType = 'partitions' | 'directory' | 'performance';
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab as TabType);
  
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId as TabType);
  };
  // Get disk metrics from the current system metrics
  const diskMetrics = useSelector((state: RootState) => state.metrics.current?.disk_usage);
  const loading = useSelector((state: RootState) => state.metrics.loading);
  const error = useSelector((state: RootState) => state.metrics.error);
  
  // Handle loading state
  if (loading) {
    return <LoadingIndicator message="Fetching disk metrics..." />;
  }
  
  // Handle error state
  if (error || !diskMetrics) {
    return <ErrorDisplay 
      message="Unable to load disk metrics" 
      details={typeof error === 'string' ? error : 'Unknown error occurred'} 
      retry={() => {
        // Dispatch refresh action here if needed
        // dispatch(fetchMetrics());
      }} 
    />;
  }

  // Convert number to RawDiskMetrics structure if needed
  const rawDiskMetrics: RawDiskMetrics = typeof diskMetrics === 'number' ? {
    partitions: [],
    physicalDisks: [],
    directories: [],
    performance: {
      current: {
        readSpeed: 0,
        writeSpeed: 0,
        readIOPS: 0,
        writeIOPS: 0,
        utilization: 0,
        queueDepth: 0,
        latency: {
          read: 0,
          write: 0
        }
      },
      bottlenecks: {
        detected: false,
        type: null,
        severity: null,
        cause: null,
        recommendations: []
      },
      topProcesses: []
    },
    history: []
  } : diskMetrics;

  // Process disk data once for all tabs
  const processedData = processDiskData(rawDiskMetrics);
  
  // Render compact version for dashboard if requested
  if (compact) {
    return (
      <div className="disk-metric disk-metric--compact">
        <DiskPartitionsTab data={processedData} compact={true} />
      </div>
    );
  }
  
  // Render full tabbed version
  return (
    <div className={`disk-metric ${compact ? 'compact' : ''}`}>
      <Tabs activeTab={activeTab} onChange={handleTabChange}>
        <Tab id="partitions" label="Partitions">
          <DiskPartitionsTab data={processedData} compact={compact} />
        </Tab>
        <Tab id="directory" label="Directory Usage">
          <DiskDirectoryTab data={processedData} />
        </Tab>
        <Tab id="performance" label="Performance">
          <DiskPerformanceTab data={processedData} />
        </Tab>
      </Tabs>
    </div>
  );
};