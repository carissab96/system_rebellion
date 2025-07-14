export interface MemoryMetricProps {
    compact?: boolean;
    defaultTab?: 'overview' | 'processes' | 'allocation';
  }
  
  // Raw memory data from Redux store
  export interface RawMemoryMetrics {
    total: number;           // Total physical memory in bytes
    used: number;            // Used physical memory in bytes
    free: number;            // Free physical memory in bytes
    cached: number;          // Cached memory in bytes
    active: number;          // Active memory in bytes
    buffers: number;         // Memory in buffers in bytes
    swap: {
      total: number;         // Total swap in bytes
      used: number;          // Used swap in bytes
      free: number;          // Free swap in bytes
    };
    pressureLevel: 'low' | 'medium' | 'high'; // Memory pressure indicator
    pageIn: number;          // Page-in operations count
    pageOut: number;         // Page-out operations count
    processes: MemoryProcess[];  // Memory consumption by process
    allocations: {
      type: string;          // Application type (system, user, service)
      bytes: number;         // Memory allocated in bytes
    }[];
    fragmentation: {         // Memory fragmentation metrics
      index: number;         // Fragmentation index (0-100)
      largestBlock: number;  // Largest available block in bytes
      freeChunks: number;    // Number of free memory chunks
    };
    // Historical data for trend analysis
    history: {
      timestamp: number;
      used: number;
      processes: { pid: number; rss: number }[];
    }[];
  }
  
  // Process memory consumption
  export interface MemoryProcess {
    pid: number;             // Process ID
    name: string;            // Process name
    command: string;         // Full command
    rss: number;             // Resident Set Size in bytes
    vms: number;             // Virtual Memory Size in bytes
    shared: number;          // Shared memory in bytes
    percentMemory: number;   // Percentage of total memory
    growthRate?: number;     // Memory growth rate (bytes/minute)
    leakProbability?: number; // Probability this process has a memory leak (0-1)
  }
  
  // Processed data structure for components
  export interface ProcessedMemoryData {
    overview: {
      physicalMemory: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
      };
      swap: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
      };
      cached: number;
      active: number;
      buffers: number;
      pressureLevel: 'low' | 'medium' | 'high';
      pressureIndicators: {
        pageInRate: number;
        pageOutRate: number;
        swapUsageRate: number;
      };
    };
    processes: {
      topConsumers: MemoryProcess[];
      growthTrends: {
        pid: number;
        name: string;
        dataPoints: { timestamp: number; bytes: number }[];
        trendline: { slope: number; intercept: number };
      }[];
      potentialLeaks: {
        pid: number;
        name: string;
        growthRate: number;
        leakProbability: number;
        evidencePoints: string[];
      }[];
    };
    allocation: {
      byType: {
        type: string;
        bytes: number;
        percentage: number;
      }[];
      fragmentation: {
        index: number;
        largestBlock: number;
        freeChunks: number;
        rating: 'good' | 'moderate' | 'poor';
      };
      optimizationRecommendations: {
        id: string;
        title: string;
        description: string;
        impact: 'high' | 'medium' | 'low';
        actionable: boolean;
        action?: string;
      }[];
    };
  }