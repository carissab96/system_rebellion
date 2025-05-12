/**
 * Formats byte values to human-readable strings with appropriate units
 */
export const formatBytes = (bytes: number, decimals = 2): string => {
    if (bytes === 0) return '0 Bytes';
    if (!bytes || isNaN(bytes)) return 'N/A';
    
    const isNegative = bytes < 0;
    bytes = Math.abs(bytes);
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    const formattedValue = parseFloat((bytes / Math.pow(k, i)).toFixed(decimals));
    return `${isNegative ? '-' : ''}${formattedValue} ${sizes[i]}`;
  };
  
  /**
   * Formats memory pressure level to a user-friendly string
   */
  export const formatMemoryPressure = (level: 'low' | 'medium' | 'high'): string => {
    switch (level) {
      case 'low': return 'Low (Normal)';
      case 'medium': return 'Medium (Elevated)';
      case 'high': return 'High (Critical)';
      default: return 'Unknown';
    }
  };
  
  /**
   * Formats a memory fragmentation index into a human-readable status
   */
  export const formatFragmentationStatus = (index: number): string => {
    if (index < 30) return 'Good';
    if (index < 70) return 'Moderate';
    return 'Poor';
  };
  
  /**
   * Formats a timestamp into a readable time string
   */
  export const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  /**
   * Formats a memory growth rate to readable string with appropriate sign
   */
  export const formatGrowthRate = (bytesPerMinute: number): string => {
    if (bytesPerMinute === 0) return '0 (Stable)';
    
    const sign = bytesPerMinute > 0 ? '+' : '';
    return `${sign}${formatBytes(bytesPerMinute)}/min`;
  };
  
  /**
   * Formats a percentage value with appropriate sign for growth
   */
  export const formatPercentage = (value: number, showSign = false): string => {
    const formattedValue = Math.abs(value).toFixed(1);
    
    if (showSign && value !== 0) {
      const sign = value > 0 ? '+' : '-';
      return `${sign}${formattedValue}%`;
    }
    
    return `${formattedValue}%`;
  };
  
  /**
   * Formats a leak probability into a human-readable string
   */
  export const formatLeakProbability = (probability: number): string => {
    const percentage = (probability * 100).toFixed(0);
    
    if (probability > 0.7) return `${percentage}% (High)`;
    if (probability > 0.4) return `${percentage}% (Medium)`;
    return `${percentage}% (Low)`;
  };
  
  /**
   * Returns CSS color class based on severity level
   */
  export const getSeverityColorClass = (
    value: number, 
    thresholds: { warning: number; critical: number }
  ): string => {
    if (value >= thresholds.critical) return 'color-critical';
    if (value >= thresholds.warning) return 'color-warning';
    return 'color-normal';
  };