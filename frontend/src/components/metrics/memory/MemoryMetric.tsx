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
import { MemoryMetricProps, RawMemoryMetrics } from './types';

export const MemoryMetric: React.FC<MemoryMetricProps> = ({ 
  compact = false,
  defaultTab = 'overview' 
}) => {
  type TabType = 'overview' | 'processes' | 'allocation';
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab as TabType);
  // Use the latest SystemMetric for memory data
  const currentMetric = useSelector((state: RootState) => state.metrics.current);
  const loading = useSelector((state: RootState) => state.metrics.loading);
  const error = useSelector((state: RootState) => state.metrics.error);

  // Extract memory metrics from SystemMetric type
  // Map SystemMetric to RawMemoryMetrics shape expected by processMemoryData
  const memoryMetrics: RawMemoryMetrics | null = currentMetric
    ? {
        total: currentMetric.memory_total,
        used: currentMetric.memory_usage,
        free: currentMetric.memory_free,
        cached: currentMetric.memory_cache,
        active: currentMetric.memory_buffer ?? 0, // fallback if not present
        buffers: currentMetric.memory_buffer ?? 0,
        swap: {
          total: currentMetric.memory_swap_total,
          used: currentMetric.memory_swap_used,
          free: currentMetric.memory_swap_free,
        },
        pageIn: 0, // Not available from SystemMetric, fallback to 0
        pageOut: 0, // Not available from SystemMetric, fallback to 0
        pressureLevel: 'low', // Default/fallback, adjust if available
        allocations: [], // Fill with real data if available
        fragmentation: {
          index: 0,
          largestBlock: 0,
          freeChunks: 0,
        },
        history: [], // Fill with real data if available
        processes: [], // Fill with real data if available
      }
    : null;
  
  // Handle loading state
  if (loading) {
    return <LoadingIndicator message="Fetching memory metrics..." />;
  }
  
  // Handle error state
  if (error || !memoryMetrics) {
    return <ErrorDisplay 
      message="Unable to load memory metrics" 
      details={typeof error === 'string' ? error : undefined}
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
      <Tabs activeTab={activeTab} onChange={(tabId: string) => setActiveTab(tabId as TabType)}>
        <Tab id="overview" label="Overview">
          <TabPanel id="overview" active={activeTab === 'overview'}>
            <MemoryOverviewTab data={processedData} />
          </TabPanel>
        </Tab>
        <Tab id="processes" label="Processes">
          <TabPanel id="processes" active={activeTab === 'processes'}>
            <MemoryProcessesTab data={processedData} />
          </TabPanel>
        </Tab>
        <Tab id="allocation" label="Allocation">
          <TabPanel id="allocation" active={activeTab === 'allocation'}>
            <MemoryAllocationTab data={processedData} />
          </TabPanel>
        </Tab>
      </Tabs>
    </div>
  );
};