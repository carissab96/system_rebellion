// frontend/src/components/metrics/memory/MemoryMetric.tsx

import React, { useState } from 'react';
import { useAppSelector } from '../../../store/hooks';
import { selectCurrentMetrics, selectHistoricalMetrics } from '../../../store/slices/metricsSlice';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { MetricsCard, MetricStatus } from '../../../design-system/components/MetricsCard';
import Tabs, { Tab } from '../../../design-system/components/Tabs';
import ErrorDisplay from '../../../components/common/ErrorDisplay';
import LoadingIndicator from '../../../components/common/LoadingIndicator';
import { MemoryAllocationTab } from './tabs/MemoryAllocationTab';
import { MemoryProcessesTab } from './tabs/MemoryProcessesTab';
import { MemoryOverviewTab } from './tabs/MemoryOverviewTab';
import { ProcessedMemoryData, MemoryProcess } from './tabs/types';
import './MemoryMetric.css';

interface MemoryMetricProps {
  compact?: boolean;
  defaultTab?: string;
  dashboardMode?: boolean; // Whether this is being used in the dashboard
  height?: number | string;
}

export const MemoryMetric: React.FC<MemoryMetricProps> = ({ 
  compact = false,
  defaultTab = 'usage',
  dashboardMode = false,
  height
}) => {
  type TabType = 'overview' | 'processes' | 'allocation';
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab as TabType);
  
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId as TabType);
  };

  // Get memory metrics from the main metrics slice
  const currentMetric = useAppSelector(selectCurrentMetrics);
  const historicalMetrics = useAppSelector(selectHistoricalMetrics);
  const loading = !currentMetric;
  const error = !currentMetric ? 'No metrics data available' : null;
  
  // Handle loading state
  if (loading) {
    return dashboardMode ? (
      <MetricsCard title="Memory Usage" value="--" unit="%" updating={true} />
    ) : (
      <LoadingIndicator message="Fetching memory metrics..." />
    );
  }
  
  // Handle error state
  if (error || !currentMetric?.memory_percent) {
    return dashboardMode ? (
      <div className={`memory-metric ${compact ? 'compact' : ''}`} style={{ height }}>
        <MetricsCard title="Memory Usage" value="--" unit="%" status="critical" />
      </div>
    ) : (
      <ErrorDisplay 
        message="Unable to load memory metrics" 
        details={typeof error === 'string' ? error : 'Unknown error occurred'} 
        retry={() => {}} 
      />
    );
  }

  // Extract memory data from metrics
  const memoryUsage = currentMetric.memory_percent || 0;
  
  const totalMemory = currentMetric.memory_total || 0;
  
  const usedMemory = (memoryUsage / 100) * totalMemory;
  
  const freeMemory = totalMemory - usedMemory;

  // Process raw metrics into the format expected by tab components
  const processedData: ProcessedMemoryData = {
    overview: {
      physicalMemory: {
        total: totalMemory,
        used: usedMemory,
        free: freeMemory,
        percentUsed: memoryUsage
      },
      swap: {
        total: currentMetric.memory_swap_total || totalMemory,
        used: currentMetric.memory_swap_used ? (currentMetric.memory_swap_percent / 100) * (currentMetric.memory_swap_total || totalMemory) : 0,
        free: currentMetric.memory_swap_free || (totalMemory - ((currentMetric.memory_swap_percent || 0) / 100) * totalMemory),
        percentUsed: currentMetric.memory_swap_percent || 0
      },
      cached: currentMetric.memory_cache || 0,
      active: currentMetric.memory_available || 0, // Using memory_available as a substitute for active memory
      buffers: currentMetric.memory_buffer || 0,
      pressureLevel: 'low', // Default to low if not available
      pressureIndicators: {
        pageInRate: 0, // These would come from metrics in a real implementation
        pageOutRate: 0,
        swapUsageRate: currentMetric.memory_swap_percent || 0
      }
    },
    processes: {
      topConsumers: (currentMetric.additional?.top_memory_processes || []).map((proc: any) => ({
        pid: proc.pid || 0,
        name: proc.name || 'Unknown',
        command: proc.command || '',
        rss: proc.memory_usage || 0,
        vms: 0, // Default value
        shared: 0, // Default value
        percentMemory: proc.memory_percent || 0
      })) as MemoryProcess[],
      growthTrends: [],
      potentialLeaks: []
    },
    allocation: {
      byType: [
        {
          type: 'Used',
          bytes: usedMemory,
          percentage: memoryUsage
        },
        {
          type: 'Free',
          bytes: freeMemory,
          percentage: 100 - memoryUsage
        }
      ],
      fragmentation: {
        index: 0, // These would come from metrics in a real implementation
        largestBlock: 0,
        freeChunks: 0,
        rating: 'good'
      },
      optimizationRecommendations: []
    }
  };

  // Format bytes to human-readable format
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  // Prepare historical data for area chart
  const memoryHistoryData = historicalMetrics.map(metric => ({
    timestamp: new Date(metric.timestamp).getTime(),
    usage: metric.memory_percent
  }));

  // Calculate memory status
  const getStatus = (usage: number): MetricStatus => {
    if (usage >= 90) return 'critical';
    if (usage >= 70) return 'warning';
    return 'normal';
  };

  // Colors for pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  // Prepare memory data for charts
  const memoryPieData = [
    { name: 'Used', value: usedMemory },
    { name: 'Free', value: freeMemory },
    { name: 'Cached', value: currentMetric.memory_cache || 0 },
    { name: 'Buffers', value: currentMetric.memory_buffer || 0 }
  ];
  
  // If using dashboard mode, render the dashboard style
  if (dashboardMode) {
    return (
      <div className="memory-metric" style={{ height }}>
        <MetricsCard
          title="Memory Usage"
          value={`${memoryUsage.toFixed(1)}`}
          unit="%"
          status={getStatus(memoryUsage)}
        >
          <Tabs activeTab={activeTab} onChange={handleTabChange}>
            <Tab id="overview" label="Overview">
              <div className="overview-content">
                <div className="memory-chart">
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={memoryPieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {memoryPieData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatBytes(value as number)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="memory-details">
                  <div className="memory-detail">
                    <span>Total:</span>
                    <span>{formatBytes(totalMemory)}</span>
                  </div>
                  <div className="memory-detail">
                    <span>Used:</span>
                    <span>{formatBytes(usedMemory)}</span>
                  </div>
                  <div className="memory-detail">
                    <span>Free:</span>
                    <span>{formatBytes(freeMemory)}</span>
                  </div>
                </div>
              </div>
            </Tab>
            <Tab id="history" label="History">
              <div className="history-content">
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart
                    data={memoryHistoryData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()} 
                    />
                    <YAxis domain={[0, 100]} />
                    <Tooltip 
                      labelFormatter={(timestamp) => new Date(timestamp as number).toLocaleString()}
                      formatter={(value) => [`${value}%`, 'Memory Usage']} 
                    />
                    <Area type="monotone" dataKey="usage" stroke="#8884d8" fill="#8884d8" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Tab>
          </Tabs>
        </MetricsCard>
      </div>
    );
  }
  
  // Render compact version for dashboard if requested
  if (compact) {
    return (
      <div className="memory-metric memory-metric--compact">
        <MemoryOverviewTab 
          data={processedData}
          compact={true} 
        />
      </div>
    );
  }
  
  // We already have processedData defined above, no need to redefine it
  
  // Render full tabbed version for component mode
  return (
    <div className={`memory-metric ${compact ? 'compact' : ''}`}>
      <Tabs activeTab={activeTab} onChange={handleTabChange}>
        <Tab id="overview" label="Overview">
          <MemoryOverviewTab 
            data={processedData}
            compact={compact} 
          />
        </Tab>
        <Tab id="processes" label="Processes">
          <MemoryProcessesTab data={processedData} />
        </Tab>
        <Tab id="allocation" label="Allocation">
          <MemoryAllocationTab 
            data={processedData}
          />
        </Tab>
      </Tabs>
    </div>
  );
};

export default MemoryMetric;