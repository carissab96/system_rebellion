import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import Tabs, { TabPanel, Tab } from '@/design-system/components/Tabs/Tabs';
import ErrorDisplay from '@/components/common/ErrorDisplay';
import LoadingIndicator from '@/components/common/LoadingIndicator';
import { MemoryOverviewTab } from './tabs/MemoryOverviewTab';
import { MemoryProcessesTab } from './tabs/MemoryProcessesTab';
import { MemoryAllocationTab } from './tabs/MemoryAllocationTab';
import { processMemoryData } from './utils/memoryDataProcessor';
import { MemoryMetricProps } from './types';

export const MemoryMetric: React.FC<MemoryMetricProps> = ({ 
  compact = false,
  defaultTab = 'overview' 
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const memoryMetrics = useSelector((state: RootState) => state.metrics.memory);
  const loading = useSelector((state: RootState) => state.metrics.loading.memory);
  const error = useSelector((state: RootState) => state.metrics.errors.memory);
  
  // Handle loading state
  if (loading) {
    return <LoadingIndicator message="Fetching memory metrics..." />;
  }
  
  // Handle error state
  if (error || !memoryMetrics) {
    return <ErrorDisplay 
      message="Unable to load memory metrics" 
      details={error?.message} 
      retry={() => {/* Dispatch refresh action */}} 
    />;
  }
  
  // Process memory data once for all tabs
  const processedData = processMemoryData(memoryMetrics);
  
  // Render compact version for dashboard if requested
  if (compact) {
    return (
      <div className="memory-metric memory-metric--compact">
        <MemoryOverviewTab data={processedData} compact={true} />
      </div>
    );
  }
  
  // Render full tabbed version
  return (
    <div className={`memory-metric ${compact ? 'compact' : ''}`}>
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab id="overview" label="Overview">
          <TabPanel active={activeTab === 'overview'}>
            <MemoryOverviewTab data={processedData} />
          </TabPanel>
        </Tab>
        <Tab id="processes" label="Processes">
          <TabPanel active={activeTab === 'processes'}>
            <MemoryProcessesTab data={processedData} />
          </TabPanel>
        </Tab>
        <Tab id="allocation" label="Allocation">
          <TabPanel active={activeTab === 'allocation'}>
            <MemoryAllocationTab data={processedData} />
          </TabPanel>
        </Tab>
      </Tabs>
    </div>
  );
};