// frontend/src/components/metrics/CPU/utils/temperatureUtils.ts

/**
 * Formats a temperature value with the appropriate unit
 * @param value Temperature value
 * @param unit Temperature unit ('C' or 'F')
 * @returns Formatted temperature string
 */
export function formatTemperature(value: number, unit: 'C' | 'F' = 'C'): string {
    return `${value.toFixed(1)}°${unit}`;
  }
  
  /**
   * Get CSS class based on temperature in relation to thresholds
   * @param temp Current temperature
   * @param throttleThreshold Throttling threshold
   * @param criticalThreshold Critical threshold
   * @returns CSS class name
   */
  export function getTemperatureClass(
    temp: number, 
    throttleThreshold: number, 
    criticalThreshold: number
  ): string {
    if (temp >= criticalThreshold) return 'critical';
    if (temp >= throttleThreshold) return 'warning';
    if (temp >= throttleThreshold * 0.8) return 'elevated';
    return 'normal';
  }
  
  /**
   * Gets a description of the temperature status
   * @param temp Current temperature
   * @param throttleThreshold Throttling threshold
   * @param criticalThreshold Critical threshold
   * @returns Description string
   */
  export function getThresholdDescription(
    temp: number, 
    throttleThreshold: number, 
    criticalThreshold: number
  ): string {
    if (temp >= criticalThreshold) return 'CRITICAL - Immediate action required';
    if (temp >= throttleThreshold) return 'WARNING - Throttling likely';
    if (temp >= throttleThreshold * 0.8) return 'ELEVATED - Monitor closely';
    return 'NORMAL - Within safe operating range';
  }
  
  /**
   * Determines if a temperature alert should be shown
   * @param temp Current temperature
   * @param throttleThreshold Throttling threshold
   * @returns Boolean indicating if an alert should be shown
   */
  export function shouldShowTemperatureAlert(temp: number, throttleThreshold: number): boolean {
    return temp >= (throttleThreshold * 0.8);
  }
  
  /**
   * Gets alert level based on temperature
   * @param temp Current temperature
   * @param throttleThreshold Throttling threshold
   * @param criticalThreshold Critical threshold
   * @returns Alert level string
   */
  export function getTemperatureAlertLevel(
    temp: number, 
    throttleThreshold: number, 
    criticalThreshold: number
  ): 'none' | 'notice' | 'warning' | 'critical' {
    if (temp >= criticalThreshold) return 'critical';
    if (temp >= throttleThreshold) return 'warning';
    if (temp >= throttleThreshold * 0.8) return 'notice';
    return 'none';
  }