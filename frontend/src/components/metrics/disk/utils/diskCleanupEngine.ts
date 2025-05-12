import { DirectoryInfo } from '../types';

interface CleanupRecommendation {
  id: string;
  path: string;
  size: number;
  description: string;
  impact: 'high' | 'medium' | 'low';
  action: string;
}

/**
 * Generates cleanup recommendations based on directory analysis
 */
export const generateCleanupRecommendations = (
  directories: DirectoryInfo[]
): CleanupRecommendation[] => {
  const recommendations: CleanupRecommendation[] = [];
  
  // Find large cleanable directories
  const largeDirs = directories
    .filter(dir => dir.usage?.cleanable && dir.size > 100 * 1024 * 1024) // > 100MB
    .sort((a, b) => b.size - a.size);
  
  // Find old temp/cache directories
  const oldCacheDirs = directories
    .filter(dir => 
      dir.usage?.cleanable && 
      ['cache', 'temp'].includes(dir.usage.type) && 
      isOlderThan(dir.usage.lastAccessed, 30) // Not accessed in 30+ days
    )
    .sort((a, b) => b.size - a.size);
  
  // Generate recommendations for large cleanable directories
  largeDirs.slice(0, 5).forEach((dir, index) => {
    recommendations.push({
      id: `large-cleanable-${index}`,
      path: dir.path,
      size: dir.size,
      description: `Large ${dir.usage?.type} directory (${formatBytes(dir.size)}) that can be safely cleaned.`,
      impact: dir.size > 1024 * 1024 * 1024 ? 'high' : 'medium', // High impact if > 1GB
      action: 'Clean Directory'
    });
  });
  
  // Generate recommendations for old cache/temp directories
  oldCacheDirs.slice(0, 5).forEach((dir, index) => {
    const daysSinceAccess = daysSince(dir.usage?.lastAccessed || 0);
    recommendations.push({
      id: `old-cache-${index}`,
      path: dir.path,
      size: dir.size,
      description: `${formatBytes(dir.size)} ${dir.usage?.type} directory not accessed in ${daysSinceAccess} days.`,
      impact: dir.size > 500 * 1024 * 1024 ? 'medium' : 'low', // Medium impact if > 500MB
      action: 'Clean Directory'
    });
  });
  
  // Look for log directories that might need rotation
  const largeLogDirs = directories
    .filter(dir => 
      dir.path.includes('/log') || 
      dir.path.includes('/logs') || 
      (dir.usage?.type === 'system' && dir.path.toLowerCase().includes('log'))
    )
    .filter(dir => dir.size > 200 * 1024 * 1024) // > 200MB
    .sort((a, b) => b.size - a.size);
  
  largeLogDirs.slice(0, 3).forEach((dir, index) => {
    recommendations.push({
      id: `large-logs-${index}`,
      path: dir.path,
      size: dir.size,
      description: `Large log directory (${formatBytes(dir.size)}). Consider implementing log rotation.`,
      impact: dir.size > 1024 * 1024 * 1024 ? 'high' : 'medium',
      action: 'View Directory'
    });
  });
  
  // Check for duplicate/backup directories
  const potentialBackups = directories
    .filter(dir => 
      dir.path.includes('backup') || 
      dir.path.includes('old') || 
      dir.path.includes('.bak') ||
      dir.path.endsWith('_old')
    )
    .filter(dir => dir.size > 100 * 1024 * 1024) // > 100MB
    .sort((a, b) => b.size - a.size);
  
  potentialBackups.slice(0, 3).forEach((dir, index) => {
    recommendations.push({
      id: `backup-dir-${index}`,
      path: dir.path,
      size: dir.size,
      description: `Potential backup/old directory (${formatBytes(dir.size)}). Consider archiving or removing.`,
      impact: dir.size > 2 * 1024 * 1024 * 1024 ? 'high' : 'medium', // High impact if > 2GB
      action: 'View Directory'
    });
  });
  
  return recommendations;
};

/**
 * Check if a timestamp is older than a specified number of days
 */
const isOlderThan = (timestamp: number, days: number): boolean => {
  const ageInMs = Date.now() - timestamp;
  const daysInMs = days * 24 * 60 * 60 * 1000;
  return ageInMs > daysInMs;
};

/**
 * Calculate days since a timestamp
 */
const daysSince = (timestamp: number): number => {
  const ageInMs = Date.now() - timestamp;
  return Math.floor(ageInMs / (24 * 60 * 60 * 1000));
};

/**
 * Format bytes to human-readable string
 */
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default generateCleanupRecommendations;
