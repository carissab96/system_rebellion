// frontend/src/components/metrics/NetworkMetrics/utils/formatters.ts

/**
 * Formats bytes to a human-readable string with appropriate units
 * @param bytes The number of bytes to format
 * @param decimals The number of decimal places to include
 * @returns Formatted string (e.g., "1.5 MB")
 */
export function formatBytes(bytes: number, decimals = 2): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }
  
  /**
   * Formats milliseconds into a readable latency string
   * @param ms Latency in milliseconds
   * @returns Formatted string (e.g., "15.2 ms")
   */
  export function formatLatency(ms: number): string {
    if (ms < 1) return '<1 ms';
    
    if (ms >= 1000) {
      return (ms / 1000).toFixed(2) + ' s';
    }
    
    return ms.toFixed(1) + ' ms';
  }
  
  /**
   * Gets a quality class name based on a score (0-100)
   * @param score Quality score between 0 and 100
   * @returns CSS class name for styling
   */
  export function getQualityClass(score: number): string {
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 50) return 'fair';
    if (score >= 25) return 'poor';
    return 'critical';
  }
  
  /**
   * Gets a latency class name based on millisecond value
   * @param ms Latency in milliseconds
   * @returns CSS class name for styling
   */
  export function getLatencyClass(ms: number): string {
    if (ms < 10) return 'good';
    if (ms < 50) return 'fair';
    if (ms < 100) return 'poor';
    return 'critical';
  }
  
  /**
   * Formats a timestamp into a readable time string
   * @param timestamp The timestamp to format
   * @returns Formatted time string
   */
  export function formatTime(timestamp: string | number): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }
  
  /**
   * Formats a timestamp into a readable date and time string
   * @param timestamp The timestamp to format
   * @returns Formatted date and time string
   */
  export function formatDateTime(timestamp: string | number): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }
  
  /**
   * Formats a number as a percentage
   * @param value The value to format (0-100 or 0-1)
   * @param normalize Whether to multiply by 100 (if input is 0-1)
   * @returns Formatted percentage string
   */
  export function formatPercentage(value: number, normalize = false): string {
    if (normalize && value <= 1) {
      value = value * 100;
    }
    return value.toFixed(1) + '%';
  }
  
  /**
   * Creates a smooth transition string for a value that changed
   * @param oldValue The previous value
   * @param newValue The new value
   * @param formatter Function to format the value
   * @returns Formatted string with change indicator
   */
  export function formatWithChange(
    oldValue: number, 
    newValue: number, 
    formatter: (val: number) => string
  ): string {
    const change = newValue - oldValue;
    const changeSymbol = change > 0 ? '↑' : change < 0 ? '↓' : '';
    const changeClass = change > 0 ? 'increase' : change < 0 ? 'decrease' : '';
    
    return `${formatter(newValue)} <span class="${changeClass}">${changeSymbol}</span>`;
  }