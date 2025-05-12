import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from 'src/store';
import { TabPanel, Tabs, Tab } from 'src/components/common/Tabs';
import { ErrorDisplay } from 'src/components/common/ErrorDisplay';
import { LoadingIndicator } from 'src/components/common/LoadingIndicator';
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
    <div className="memory-metric">
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="overview" label="Overview" />
        <Tab value="processes" label="Processes" />
        <Tab value="allocation" label="Allocation" />
      </Tabs>
      
      <TabPanel value={activeTab} activeValue="overview">
        <MemoryOverviewTab data={processedData} />
      </TabPanel>
      
      <TabPanel value={activeTab} activeValue="processes">
        <MemoryProcessesTab data={processedData} />
      </TabPanel>
      
      <TabPanel value={activeTab} activeValue="allocation">
        <MemoryAllocationTab data={processedData} />
      </TabPanel>
    </div>
  );
};