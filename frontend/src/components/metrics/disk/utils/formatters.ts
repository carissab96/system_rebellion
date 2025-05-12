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
   * Formats large numbers with thousands separators
   */
  export const formatNumber = (num: number): string => {
    if (isNaN(num)) return 'N/A';
    return num.toLocaleString();
  };
  
  /**
   * Formats a percentage value with appropriate sign
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
   * Formats a timestamp to a readable date/time string
   */
  export const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  /**
   * Returns a readable string for a disk health status
   */
  export const formatDiskHealthStatus = (status: 'healthy' | 'warning' | 'error' | 'passed' | 'failed'): string => {
    switch(status) {
      case 'healthy':
      case 'passed':
        return 'Healthy';
      case 'warning':
        return 'Warning';
      case 'error':
      case 'failed':
        return 'Critical';
      default:
        return 'Unknown';
    }
  };
  
  /**
   * Returns a CSS class based on disk health status
   */
  export const getDiskHealthClass = (status: 'healthy' | 'warning' | 'error' | 'passed' | 'failed'): string => {
    switch(status) {
      case 'healthy':
      case 'passed':
        return 'health-good';
      case 'warning':
        return 'health-warning';
      case 'error':
      case 'failed':
        return 'health-critical';
      default:
        return '';
    }
  };