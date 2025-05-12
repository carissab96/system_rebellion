import { RawDiskMetrics, ProcessedDiskData } from '../types';
import { analyzeSmartData } from './smartDataAnalyzer';
import { generateCleanupRecommendations } from './diskCleanupEngine';
import { detectIOBottlenecks } from './iobottleneckDetector';

/**
 * Processes raw disk metrics into structured data for components
 */
export const processDiskData = (
  rawData: RawDiskMetrics
): ProcessedDiskData => {
  // Process partition data
  const partitions = processPartitionsData(rawData);
  
  // Process physical disk data
  const physicalDisks = processPhysicalDisksData(rawData);
  
  // Process directory data
  const directories = processDirectoryData(rawData);
  
  // Process performance data
  const performance = processPerformanceData(rawData);
  
  return {
    partitions,
    physicalDisks,
    directories,
    performance
  };
};

/**
 * Process partition-related data
 */
const processPartitionsData = (rawData: RawDiskMetrics): ProcessedDiskData['partitions'] => {
  const partitionItems = rawData.partitions.map((partition: { mountPoint: any; device: any; fsType: any; total: any; used: any; available: any; percentUsed: any; health: { status: any; issues: any; }; inodes: { percentUsed: any; }; readOnly: any; physicalDiskId: any; }) => ({
    mountPoint: partition.mountPoint,
    device: partition.device,
    fsType: partition.fsType,
    total: partition.total,
    used: partition.used,
    available: partition.available,
    percentUsed: partition.percentUsed,
    health: {
      status: partition.health.status,
      issues: partition.health.issues
    },
    inodeUsage: partition.inodes.percentUsed,
    readOnly: partition.readOnly,
    physicalDiskId: partition.physicalDiskId
  }));
  
  // Calculate total and used disk space across all partitions
  const totalDiskSpace = partitionItems.reduce((total: any, partition: { total: any; }) => total + partition.total, 0);
  const usedDiskSpace = partitionItems.reduce((total: any, partition: { used: any; }) => total + partition.used, 0);
  
  // Determine overall health
  const healthStatuses = partitionItems.map((p: { health: { status: any; }; }) => p.health.status);
  const overallHealth = healthStatuses.includes('error') 
    ? 'error' 
    : healthStatuses.includes('warning')
      ? 'warning'
      : 'healthy';
  
  return {
    items: partitionItems,
    totalDiskSpace,
    usedDiskSpace,
    overallHealth
  };
};

/**
 * Process physical disk data including SMART analysis
 */
const processPhysicalDisksData = (rawData: RawDiskMetrics): ProcessedDiskData['physicalDisks'] => {
  // Process physical disk items with SMART analysis
  const diskItems = rawData.physicalDisks.map((disk: { smart: { status: any; lifeRemaining: any; }; id: any; model: any; type: any; size: any; temperature: any; partitions: any; }) => {
    // Analyze SMART data for health assessment
    const smartAnalysis = analyzeSmartData(disk.smart);
    
    return {
      id: disk.id,
      model: disk.model,
      type: disk.type,
      size: disk.size,
      temperature: disk.temperature,
      health: {
        status: disk.smart.status,
        lifeRemaining: disk.smart.lifeRemaining,
        issues: smartAnalysis.issues
      },
      partitions: disk.partitions
    };
  });
  
  // Extract critical issues across all disks
  const criticalIssues = diskItems.flatMap((disk: { health: { issues: any[]; }; id: any; }) => 
    disk.health.issues.map((issue: any) => ({
      diskId: disk.id,
      issue
    }))
  );
  
  // Determine overall health
  const healthStatuses = diskItems.map((d: { health: { status: any; }; }) => d.health.status);
  const overallHealth = healthStatuses.includes('failed') 
    ? 'critical' 
    : healthStatuses.includes('warning')
      ? 'warning'
      : 'good';
  
  return {
    items: diskItems,
    overallHealth,
    criticalIssues
  };
};

/**
 * Process directory data and generate cleanup recommendations
 */
const processDirectoryData = (rawData: RawDiskMetrics): ProcessedDiskData['directories'] => {
  // Sort directories by size to get largest ones
  const sortedDirs = [...rawData.directories]
    .sort((a, b) => b.size - a.size);
  
  // Extract largest directories
  const largestDirs = sortedDirs.slice(0, 10).map(dir => ({
    path: dir.path,
    size: dir.size,
    fileCount: dir.fileCount,
    lastModified: dir.lastModified,
    type: dir.usage?.type || 'other',
    cleanable: dir.usage?.cleanable || false
  }));
  
  // Create treemap data structure
  const treemapData = createDirectoryTreemap(rawData.directories);
  
  // Generate cleanup recommendations
  const cleanupRecommendations = generateCleanupRecommendations(rawData.directories);
  
  // Calculate total analyzed size
  const totalAnalyzedSize = rawData.directories.reduce((total: any, dir: { size: any; }) => total + dir.size, 0);
  
  return {
    largest: largestDirs,
    treemapData,
    cleanupRecommendations,
    totalAnalyzedSize
  };
};

/**
 * Create hierarchical treemap data structure from directory information
 */
const createDirectoryTreemap = (directories: RawDiskMetrics['directories']) => {
  // Find root directory
  const rootDirectory = directories.find((dir: { path: string; }) => 
    !directories.some((parent: { path: string; }) => dir.path.startsWith(parent.path + '/') && parent.path !== dir.path)
  );
  
  if (!rootDirectory) {
    return { name: 'No data', path: '', value: 0 };
  }
  
  // Recursively build treemap structure
  return buildTreemapNode(rootDirectory, directories);
};

/**
 * Build a single node for the treemap
 */
const buildTreemapNode = (
  directory: RawDiskMetrics['directories'][0],
  allDirectories: RawDiskMetrics['directories']
) => {
  // Find direct children
  const children = allDirectories.filter((dir: { path: { startsWith: (arg0: string) => any; split: (arg0: string) => { (): any; new(): any; length: any; }; }; }) => 
    dir.path.startsWith(directory.path + '/') &&
    dir.path.split('/').length === directory.path.split('/').length + 1
  );
  
  // Create node
  const node: any = {
    name: directory.path.split('/').pop() || directory.path,
    path: directory.path,
    value: directory.size
  };
  
  // Add children if they exist
  if (children.length > 0) {
    node.children = children.map((child: any) => buildTreemapNode(child, allDirectories));
  }
  
  return node;
};

/**
 * Process I/O performance data
 */
const processPerformanceData = (rawData: RawDiskMetrics): ProcessedDiskData['performance'] => {
  // Get current performance metrics
  const current = {
    readSpeed: rawData.performance.current.readSpeed,
    writeSpeed: rawData.performance.current.writeSpeed,
    readIOPS: rawData.performance.current.readIOPS,
    writeIOPS: rawData.performance.current.writeIOPS,
    utilization: rawData.performance.current.utilization,
    latency: {
      read: rawData.performance.current.latency.read,
      write: rawData.performance.current.latency.write
    }
  };
  
  // Process historical data
  const historical = processHistoricalData(rawData.history);
  
  // Process top I/O processes
  const topProcesses = rawData.performance.topProcesses.map((process: { pid: any; name: any; readRate: any; writeRate: any; totalRate: number; }) => ({
    pid: process.pid,
    name: process.name,
    readRate: process.readRate,
    writeRate: process.writeRate,
    totalRate: process.totalRate,
    percentage: (process.totalRate / 
      rawData.performance.topProcesses.reduce((sum: any, p: { totalRate: any; }) => sum + p.totalRate, 0)) * 100
  }));
  
  // Detect I/O bottlenecks
  const bottlenecks = detectIOBottlenecks(rawData.performance, rawData.history);
  
  return {
    current,
    historical,
    topProcesses,
    bottlenecks
  };
};

/**
 * Process historical I/O data into a format suitable for charts
 */
const processHistoricalData = (history: RawDiskMetrics['history']) => {
  // Extract timestamp and metric arrays for charting
  const timestamps = history.map((point: { timestamp: any; }) => point.timestamp);
  const readSpeed = history.map((point: { readSpeed: any; }) => point.readSpeed);
  const writeSpeed = history.map((point: { writeSpeed: any; }) => point.writeSpeed);
  const readIOPS = history.map((point: { readIOPS: any; }) => point.readIOPS);
  const writeIOPS = history.map((point: { writeIOPS: any; }) => point.writeIOPS);
  const utilization = history.map((point: { utilization: any; }) => point.utilization);
  
  return {
    timestamps,
    readSpeed,
    writeSpeed,
    readIOPS,
    writeIOPS,
    utilization
  };
};

export default processDiskData;