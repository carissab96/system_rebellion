import { RawMemoryMetrics } from '../types';

export interface OptimizationRecommendation {
  id: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
  action?: string;
}

/**
 * Generates memory optimization recommendations based on current memory metrics
 */
export const generateOptimizationRecommendations = (
  metrics: RawMemoryMetrics
): OptimizationRecommendation[] => {
  const recommendations: OptimizationRecommendation[] = [];
  
  // Calculate some helper metrics
  const physicalMemoryUsagePercent = (metrics.used / metrics.total) * 100;
  const swapUsagePercent = metrics.swap.total > 0 
    ? (metrics.swap.used / metrics.swap.total) * 100 
    : 0;
  const isHighMemoryPressure = metrics.pressureLevel === 'high';
  const isModerateMemoryPressure = metrics.pressureLevel === 'medium';
  const isHighFragmentation = metrics.fragmentation.index > 70;
  const isModerateFragmentation = metrics.fragmentation.index > 40;
  
  // Get top memory consumers (top 3)
  const topMemoryConsumers = [...metrics.processes]
    .sort((a, b) => b.rss - a.rss)
    .slice(0, 3);
  
  // High memory usage recommendation
  if (physicalMemoryUsagePercent > 85) {
    recommendations.push({
      id: 'high-memory-usage',
      title: 'High Memory Usage Detected',
      description: 
        `Your system is using ${physicalMemoryUsagePercent.toFixed(1)}% of available physical memory. ` +
        `This may lead to performance degradation and increased swap usage. Consider closing unused applications ` +
        `or upgrading system memory.`,
      impact: 'high',
      actionable: true,
      action: 'View Top Memory Consumers'
    });
  }
  
  // High swap usage recommendation
  if (swapUsagePercent > 50) {
    recommendations.push({
      id: 'high-swap-usage',
      title: 'Excessive Swap Usage',
      description: 
        `Your system is using ${swapUsagePercent.toFixed(1)}% of available swap space. ` +
        `Heavy swap usage significantly slows down system performance as disk access is much slower than RAM. ` +
        `Consider closing memory-intensive applications or adding more physical memory.`,
      impact: 'high',
      actionable: false
    });
  }
  
  // Memory hogs recommendations
  const memoryHogThreshold = metrics.total * 0.2; // 20% of total memory
  const memoryHogs = topMemoryConsumers.filter(process => process.rss > memoryHogThreshold);
  
  if (memoryHogs.length > 0 && physicalMemoryUsagePercent > 75) {
    memoryHogs.forEach(process => {
      recommendations.push({
        id: `memory-hog-${process.pid}`,
        title: `High Memory Usage: ${process.name}`,
        description: 
          `Process "${process.name}" (PID: ${process.pid}) is using ${process.percentMemory.toFixed(1)}% of your system memory. ` +
          `Consider restarting this application or investigating why it requires so much memory.`,
        impact: 'medium',
        actionable: true,
        action: 'Restart Process'
      });
    });
  }
  
  // Memory fragmentation recommendations
  if (isHighFragmentation) {
    recommendations.push({
      id: 'high-fragmentation',
      title: 'Severe Memory Fragmentation',
      description: 
        `Your system memory is highly fragmented (${metrics.fragmentation.index}% fragmentation index). ` +
        `This can prevent allocation of large memory blocks and decrease performance. ` +
        `Restarting memory-intensive applications or the system itself can help defragment memory.`,
      impact: 'medium',
      actionable: false
    });
  } else if (isModerateFragmentation && isHighMemoryPressure) {
    recommendations.push({
      id: 'moderate-fragmentation',
      title: 'Memory Fragmentation Under Pressure',
      description: 
        `Your system has moderate memory fragmentation (${metrics.fragmentation.index}% index) combined with high memory pressure. ` +
        `This combination can significantly impact performance. Consider freeing memory by closing unused applications.`,
      impact: 'medium',
      actionable: false
    });
  }
  
  // Memory leak recommendations - build on the leak detector results
  // This would normally be more sophisticated, connecting to the leak detector
  const potentialLeakyProcesses = metrics.processes.filter(p => 
    p.growthRate !== undefined && p.growthRate > 0 && p.leakProbability !== undefined && p.leakProbability > 0.7
  );
  
  potentialLeakyProcesses.forEach(process => {
    recommendations.push({
      id: `memory-leak-${process.pid}`,
      title: `Potential Memory Leak: ${process.name}`,
      description: 
        `Process "${process.name}" (PID: ${process.pid}) shows a pattern consistent with a memory leak. ` +
        `Its memory usage is steadily growing without release. Consider restarting the application or ` +
        `reporting the issue to the application developer.`,
      impact: 'high',
      actionable: true,
      action: 'View Leak Analysis'
    });
  });
  
  // Cached memory recommendations
  const cachedMemoryPercent = (metrics.cached / metrics.total) * 100;
  if (cachedMemoryPercent > 60 && isHighMemoryPressure) {
    recommendations.push({
      id: 'high-cache-usage',
      title: 'Excessive Memory Caching',
      description: 
        `${cachedMemoryPercent.toFixed(1)}% of your memory is used for disk caching while the system is under memory pressure. ` +
        `While caching improves disk performance, it may be consuming memory needed by applications. ` +
        `Consider adjusting your system's cache pressure settings.`,
      impact: 'low',
      actionable: false
    });
  }
  
  // Page rate recommendations
  if (metrics.pageOut > 100 && isModerateMemoryPressure) {
    recommendations.push({
      id: 'high-page-rate',
      title: 'High Memory Paging Activity',
      description: 
        `Your system is experiencing high paging activity (${metrics.pageOut} page-outs). ` +
        `This indicates memory pressure forcing the system to move memory pages to disk, ` +
        `which can significantly slow down performance.`,
      impact: 'medium',
      actionable: false
    });
  }
  
  return recommendations;
};