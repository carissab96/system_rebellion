import { RawMemoryMetrics, ProcessedMemoryData, MemoryProcess } from '../tabs/types';
import { detectMemoryLeaks } from './memoryLeakDetector';
import { generateOptimizationRecommendations } from './optimizationEngine';

/**
 * Processes raw memory metrics into structured data for components
 */
export const processMemoryData = (
  rawData: RawMemoryMetrics
): ProcessedMemoryData => {
  // Calculate overview metrics
  const overview = processOverviewMetrics(rawData);
  
  // Process memory consumption trends
  const processes = processProcessMetrics(rawData);
  
  // Memory allocation analysis
  const allocation = processAllocationMetrics(rawData);
  
  return {
    overview,
    processes,
    allocation
  };
};

/**
 * Process overview-related metrics
 */
const processOverviewMetrics = (rawData: RawMemoryMetrics) => {
  return {
    physicalMemory: {
      total: rawData.total,
      used: rawData.used,
      free: rawData.free,
      percentUsed: (rawData.used / rawData.total) * 100
    },
    swap: {
      total: rawData.swap.total,
      used: rawData.swap.used,
      free: rawData.swap.free,
      percentUsed: rawData.swap.total > 0 
        ? (rawData.swap.used / rawData.swap.total) * 100 
        : 0
    },
    cached: rawData.cached,
    active: rawData.active,
    buffers: rawData.buffers,
    pressureLevel: rawData.pressureLevel,
    pressureIndicators: {
      pageInRate: calculatePageRate(rawData.history),
      pageOutRate: calculatePageRate(rawData.history),
      swapUsageRate: calculateSwapUsageRate(rawData.history)
    }
  };
};

/**
 * Process process-related metrics including leak detection
 */
const processProcessMetrics = (rawData: RawMemoryMetrics) => {
  // Calculate growth trends for processes
  const growthTrends = calculateProcessGrowthTrends(rawData.processes, rawData.history);
  
  // Detect potential memory leaks
  const potentialLeaks = detectMemoryLeaks(rawData.processes, rawData.history);
  
  return {
    topConsumers: sortProcessesByMemory(rawData.processes),
    growthTrends,
    potentialLeaks
  };
};

/**
 * Process allocation-related metrics
 */
const processAllocationMetrics = (rawData: RawMemoryMetrics) => {
  return {
    byType: calculateMemoryByType(rawData.allocations),
    fragmentation: {
      index: rawData.fragmentation.index,
      largestBlock: rawData.fragmentation.largestBlock,
      freeChunks: rawData.fragmentation.freeChunks,
      rating: rateFragmentation(rawData.fragmentation.index)
    },
    optimizationRecommendations: generateOptimizationRecommendations(rawData)
  };
};

/**
 * Calculate the rate of page operations based on history
 */
const calculatePageRate = (
 
  history: RawMemoryMetrics['history']
): number => {
  if (history.length < 2) return 0;
  
  // Get page operations from the last two history points if available
  // Assuming these are cumulative counts since system boot
  const currentTime = Date.now();
  const recentHistory = history
    .filter(h => currentTime - h.timestamp < 60000) // Last minute
    .sort((a, b) => b.timestamp - a.timestamp); // Most recent first
  
  if (recentHistory.length < 2) return 0;
  
  // Calculate the rate of operations per second
  const latestPoint = recentHistory[0];
  const earlierPoint = recentHistory[recentHistory.length - 1];
  
  const timeDiffSeconds = (latestPoint.timestamp - earlierPoint.timestamp) / 1000;
  if (timeDiffSeconds <= 0) return 0;
  
  // Since we don't have page operations in history directly in this model,
  // we'll estimate based on memory usage changes
  // In a real implementation, we'd store pageIn/pageOut in history
  const memoryDiff = Math.abs(latestPoint.used - earlierPoint.used);
  const estimatedPageOps = memoryDiff / 4096; // Assuming 4KB page size
  
  return estimatedPageOps / timeDiffSeconds;
};

/**
 * Calculate the rate of swap usage change
 */
const calculateSwapUsageRate = (
  history: RawMemoryMetrics['history']
): number => {
  if (history.length < 2) return 0;
  
  // Get the most recent history entries within the last minute
  const currentTime = Date.now();
  const recentHistory = history
    .filter(h => currentTime - h.timestamp < 60000)
    .sort((a, b) => b.timestamp - a.timestamp);
  
  if (recentHistory.length < 2) return 0;
  
  // Calculate the rate of swap usage change in MB/s
  // In a real implementation, we'd have swap usage in history
  const latestPoint = recentHistory[0];
  const earlierPoint = recentHistory[recentHistory.length - 1];
  
  const timeDiffSeconds = (latestPoint.timestamp - earlierPoint.timestamp) / 1000;
  if (timeDiffSeconds <= 0) return 0;
  
  // Since we don't have swap in history directly in this model,
  // we'll return a placeholder. In a real implementation:
  // const swapDiffMB = (latestPoint.swap.used - earlierPoint.swap.used) / (1024 * 1024);
  // return swapDiffMB / timeDiffSeconds;
  
  return 0; // Placeholder
};

/**
 * Sort processes by memory usage (RSS)
 */
const sortProcessesByMemory = (
  processes: MemoryProcess[]
): MemoryProcess[] => {
  return [...processes].sort((a, b) => b.rss - a.rss);
};

/**
 * Calculate growth trends for processes based on historical data
 */
const calculateProcessGrowthTrends = (
  processes: MemoryProcess[],
  history: RawMemoryMetrics['history']
): ProcessedMemoryData['processes']['growthTrends'] => {
  const result: ProcessedMemoryData['processes']['growthTrends'] = [];
  
  // Process each active process
  processes.forEach(process => {
    // Get history points for this process
    const processHistory = history
      .map(point => {
        const processPoint = point.processes.find(p => p.pid === process.pid);
        if (!processPoint) return null;
        
        return {
          timestamp: point.timestamp,
          bytes: processPoint.rss
        };
      })
      .filter((point): point is { timestamp: number; bytes: number } => point !== null);
    
    // Need at least 3 points for a meaningful trend
    if (processHistory.length < 3) return;
    
    // Calculate linear regression for trendline
    const trendline = calculateLinearRegression(processHistory);
    
    result.push({
      pid: process.pid,
      name: process.name,
      dataPoints: processHistory,
      trendline
    });
  });
  
  return result;
};

/**
 * Calculate a linear regression (trendline) from time series data
 */
const calculateLinearRegression = (
  points: { timestamp: number; bytes: number }[]
): { slope: number; intercept: number } => {
  // Convert timestamps to relative time in minutes for better numerical stability
  const baseTime = points[0].timestamp;
  const timePoints = points.map(p => (p.timestamp - baseTime) / 60000); // minutes
  const bytePoints = points.map(p => p.bytes);
  
  const n = points.length;
  
  // Calculate means
  const meanX = timePoints.reduce((sum, x) => sum + x, 0) / n;
  const meanY = bytePoints.reduce((sum, y) => sum + y, 0) / n;
  
  // Calculate slope and intercept
  let numerator = 0;
  let denominator = 0;
  
  for (let i = 0; i < n; i++) {
    numerator += (timePoints[i] - meanX) * (bytePoints[i] - meanY);
    denominator += Math.pow(timePoints[i] - meanX, 2);
  }
  
  // Avoid division by zero
  const slope = denominator !== 0 ? numerator / denominator : 0;
  const intercept = meanY - slope * meanX;
  
  return { slope, intercept };
};

/**
 * Calculate memory usage by application type
 */
const calculateMemoryByType = (
  allocations: RawMemoryMetrics['allocations']
) => {
  const total = allocations.reduce((sum, item) => sum + item.bytes, 0);
  
  return allocations.map(item => ({
    type: item.type,
    bytes: item.bytes,
    percentage: (item.bytes / total) * 100
  }));
};

/**
 * Rate memory fragmentation based on fragmentation index
 */
const rateFragmentation = (
  index: number
): 'good' | 'moderate' | 'poor' => {
  if (index < 30) return 'good';
  if (index < 70) return 'moderate';
  return 'poor';
};