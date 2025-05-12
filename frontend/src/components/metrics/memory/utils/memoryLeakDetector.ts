import { MemoryProcess, RawMemoryMetrics } from '../types';

interface LeakDetectionResult {
  pid: number;
  name: string;
  growthRate: number;
  leakProbability: number;
  evidencePoints: string[];
}

/**
 * Detects potential memory leaks by analyzing process memory trends
 */
export const detectMemoryLeaks = (
  processes: MemoryProcess[],
  history: RawMemoryMetrics['history']
): LeakDetectionResult[] => {
  // We need sufficient history to detect leaks
  if (history.length < 3) {
    return [];
  }
  
  const leakCandidates: LeakDetectionResult[] = [];
  
  // Analyze each process with memory history
  processes.forEach(process => {
    // Skip processes without growth rate
    if (process.growthRate === undefined || process.growthRate <= 0) {
      return;
    }
    
    // Create history points for this process
    const processHistory = createProcessHistory(process.pid, history);
    
    // Skip processes with insufficient history
    if (processHistory.length < 3) {
      return;
    }
    
    // Calculate memory growth metrics
    const { 
      isConsistentGrowth, 
      growthRate, 
      growthVariance, 
      totalGrowthPercentage,
      hasPeriodicity,
      growthAfterGC
    } = analyzeMemoryGrowthPattern(processHistory);
    
    // Evidence collection for leak detection
    const evidencePoints: string[] = [];
    let leakProbability = 0;
    
    // Check for consistent memory growth
    if (isConsistentGrowth) {
      evidencePoints.push(
        `Consistent memory growth of ${formatBytes(growthRate)}/minute over ${processHistory.length} measurements.`
      );
      leakProbability += 0.3;
    }
    
    // Check growth percentage threshold
    if (totalGrowthPercentage > 20) {
      evidencePoints.push(
        `Significant growth of ${totalGrowthPercentage.toFixed(1)}% from initial measurement.`
      );
      leakProbability += 0.2;
    }
    
    // Low variance indicates consistent growth pattern
    if (growthVariance < 0.3 && isConsistentGrowth) {
      evidencePoints.push(
        `Consistent growth pattern with low variance (${growthVariance.toFixed(2)}), typical of memory leaks.`
      );
      leakProbability += 0.15;
    }
    
    // Check if growth continues after apparent GC events
    if (growthAfterGC) {
      evidencePoints.push(
        'Memory usage continues to grow even after garbage collection events.'
      );
      leakProbability += 0.25;
    }
    
    // Check if memory usage growth appears periodic
    if (hasPeriodicity) {
      evidencePoints.push(
        'Memory usage exhibits periodic patterns, suggesting normal application behavior rather than a leak.'
      );
      leakProbability -= 0.2;
    }
    
    // If we have evidence and probability is significant, add to candidates
    if (evidencePoints.length > 0 && leakProbability > 0.3) {
      // Cap probability at 0.95
      leakProbability = Math.min(leakProbability, 0.95);
      
      leakCandidates.push({
        pid: process.pid,
        name: process.name,
        growthRate: process.growthRate,
        leakProbability,
        evidencePoints
      });
    }
  });
  
  return leakCandidates;
};

/**
 * Creates a time series of memory usage for a specific process
 */
const createProcessHistory = (
  pid: number,
  history: RawMemoryMetrics['history']
): { timestamp: number; bytes: number }[] => {
  return history
    .map(point => {
      const processPoint = point.processes.find(p => p.pid === pid);
      if (!processPoint) return null;
      
      return {
        timestamp: point.timestamp,
        bytes: processPoint.rss
      };
    })
    .filter((point): point is { timestamp: number; bytes: number } => point !== null);
};

/**
 * Analyzes memory growth patterns to identify leak characteristics
 */
const analyzeMemoryGrowthPattern = (
  history: { timestamp: number; bytes: number }[]
) => {
  // Calculate time-normalized growth rates
  const growthRates: number[] = [];
  for (let i = 1; i < history.length; i++) {
    const timeDiffMinutes = (history[i].timestamp - history[i-1].timestamp) / 60000;
    if (timeDiffMinutes > 0) {
      const growthRate = (history[i].bytes - history[i-1].bytes) / timeDiffMinutes;
      growthRates.push(growthRate);
    }
  }
  
  // Skip if we don't have enough growth rate points
  if (growthRates.length < 2) {
    return {
      isConsistentGrowth: false,
      growthRate: 0,
      growthVariance: 0,
      totalGrowthPercentage: 0,
      hasPeriodicity: false,
      growthAfterGC: false
    };
  }
  
  // Calculate average growth rate
  const avgGrowthRate = growthRates.reduce((sum, rate) => sum + rate, 0) / growthRates.length;
  
  // Calculate variance (normalized)
  const growthVariance = calculateNormalizedVariance(growthRates);
  
  // Calculate total growth percentage
  const totalGrowthPercentage = history[0].bytes > 0 
    ? ((history[history.length - 1].bytes - history[0].bytes) / history[0].bytes) * 100
    : 0;
  
  // Check for consistent growth (majority of measurements show growth)
  const positiveGrowthCount = growthRates.filter(rate => rate > 0).length;
  const isConsistentGrowth = positiveGrowthCount / growthRates.length > 0.7 && avgGrowthRate > 0;
  
  // Check for periodicity in memory usage
  const hasPeriodicity = detectPeriodicity(history.map(h => h.bytes));
  
  // Detect garbage collection events and check if growth continues afterward
  const gcEvents = detectGarbageCollectionEvents(history);
  const growthAfterGC = gcEvents.length > 0 && 
    gcEvents.some(eventIndex => {
      // Check if there's consistent growth after a GC event
      if (eventIndex >= history.length - 2) return false;
      
      const postGCPoints = history.slice(eventIndex + 1);
      return isConsistentGrowthSequence(postGCPoints.map(p => p.bytes));
    });
  
  return {
    isConsistentGrowth,
    growthRate: avgGrowthRate,
    growthVariance,
    totalGrowthPercentage,
    hasPeriodicity,
    growthAfterGC
  };
};

/**
 * Calculate normalized variance (0-1 scale)
 */
const calculateNormalizedVariance = (values: number[]): number => {
  if (values.length <= 1) return 0;
  
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
  const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
  
  // Normalize variance to a 0-1 scale relative to the mean
  return mean !== 0 ? Math.min(1, variance / Math.pow(mean, 2)) : 0;
};

/**
 * Detects if a memory sequence follows a periodic pattern
 */
const detectPeriodicity = (memorySequence: number[]): boolean => {
  if (memorySequence.length < 6) return false;
  
  // Simplified periodicity detection using autocorrelation
  const diffs = [];
  for (let i = 1; i < memorySequence.length; i++) {
    diffs.push(memorySequence[i] - memorySequence[i-1]);
  }
  
  let signChanges = 0;
  for (let i = 1; i < diffs.length; i++) {
    if ((diffs[i] >= 0 && diffs[i-1] < 0) || (diffs[i] < 0 && diffs[i-1] >= 0)) {
      signChanges++;
    }
  }
  
  // If we see multiple sign changes, we likely have periodic behavior
  const changeRatio = signChanges / (diffs.length - 1);
  return changeRatio > 0.4;
};

/**
 * Detects potential garbage collection events
 * (significant sudden drops in memory usage)
 */
const detectGarbageCollectionEvents = (
  history: { timestamp: number; bytes: number }[]
): number[] => {
  const gcEventIndices: number[] = [];
  
  for (let i = 1; i < history.length; i++) {
    const currentMemory = history[i].bytes;
    const prevMemory = history[i-1].bytes;
    
    // If memory drops by more than 15%, it might be a GC event
    if (prevMemory > 0 && (prevMemory - currentMemory) / prevMemory > 0.15) {
      gcEventIndices.push(i);
    }
  }
  
  return gcEventIndices;
};

/**
 * Check if a sequence of memory values shows consistent growth
 */
const isConsistentGrowthSequence = (memorySequence: number[]): boolean => {
  if (memorySequence.length < 3) return false;
  
  let growingIntervals = 0;
  for (let i = 1; i < memorySequence.length; i++) {
    if (memorySequence[i] > memorySequence[i-1]) {
      growingIntervals++;
    }
  }
  
  return growingIntervals / (memorySequence.length - 1) > 0.7;
};

/**
 * Format bytes to a human-readable string
 * Used internally in this file (referencing formatters.ts would create circular dependency)
 */
const formatBytes = (bytes: number): string => {
  if (Math.abs(bytes) < 1024) return `${bytes.toFixed(0)} B`;
  
  const units = ['KB', 'MB', 'GB', 'TB'];
  let value = Math.abs(bytes);
  let unitIndex = -1;
  
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }
  
  const sign = bytes < 0 ? '-' : '';
  return `${sign}${value.toFixed(2)} ${units[unitIndex]}`;
};