import React from 'react';
import './MetricsCard.css';
import { Card } from '../Card';
import { Badge } from '../Badge';
// Using tokens for consistent styling
import { colors, effects } from '../../tokens';

export type MetricStatus = 'normal' | 'warning' | 'critical' | 'optimized';
export type MetricTrend = 'up' | 'down' | 'stable';

export interface MetricsCardProps {
  /** Title of the metric */
  title: string;
  /** Current value of the metric */
  value: string | number;
  /** Unit of measurement (e.g., %, MB, ms) */
  unit?: string;
  /** Previous value for comparison */
  previousValue?: string | number;
  /** Percentage change from previous value */
  changePercentage?: number;
  /** Status of the metric */
  status?: MetricStatus;
  /** Trend direction of the metric */
  trend?: MetricTrend;
  /** Whether the metric card is updating/loading */
  updating?: boolean;
  /** Timestamp of the last update */
  lastUpdated?: string;
  /** Whether to show the sparkline chart */
  showSparkline?: boolean;
  /** Data points for the sparkline chart */
  sparklineData?: number[];
  /** Icon to display */
  icon?: React.ReactNode;
  /** Additional CSS class names */
  className?: string;
  /** Additional props */
  [x: string]: any;
}

/**
 * MetricsCard component for System Rebellion UI
 * 
 * A specialized card component for displaying system metrics with cyberpunk styling.
 * Includes status indicators, trend visualization, and optional sparkline.
 */
export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  unit = '',
  previousValue,
  changePercentage,
  status = 'normal',
  trend = 'stable',
  updating = false,
  lastUpdated,
  showSparkline = false,
  sparklineData = [],
  icon,
  className = '',
  ...props
}) => {
  // Get status badge variant based on status
  const getStatusVariant = () => {
    switch (status) {
      case 'normal':
        return 'info';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'danger';
      case 'optimized':
        return 'success';
      default:
        return 'info';
    }
  };

  // Get trend icon based on trend
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'stable':
        return '→';
      default:
        return '→';
    }
  };

  // Get trend class based on trend and context
  const getTrendClass = () => {
    // For some metrics, up is good (e.g., available memory)
    // For others, down is good (e.g., CPU usage)
    // This is a simplified example
    if (trend === 'stable') return 'sr-metrics-trend-stable';
    
    if (status === 'critical') {
      return 'sr-metrics-trend-negative';
    } else if (status === 'optimized') {
      return 'sr-metrics-trend-positive';
    } else {
      return trend === 'up' ? 'sr-metrics-trend-up' : 'sr-metrics-trend-down';
    }
  };

  // Build the class names
  const metricsClasses = [
    'sr-metrics-card',
    `sr-metrics-status-${status}`,
    updating ? 'sr-metrics-updating' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <Card 
      variant="default" 
      elevation="low" 
      glass
      className={metricsClasses}
      {...props}
    >
      <div className="sr-metrics-header">
        <div className="sr-metrics-title">
          {icon && <span className="sr-metrics-icon">{icon}</span>}
          <span>{title}</span>
        </div>
        <Badge 
          variant={getStatusVariant()} 
          size="sm" 
          rounded 
          glow={status === 'critical'}
          pulse={status === 'critical'}
        >
          {status}
        </Badge>
      </div>
      
      <div className="sr-metrics-value-container">
        <div className="sr-metrics-value">
          {value}
          {unit && <span className="sr-metrics-unit">{unit}</span>}
        </div>
        
        {(previousValue !== undefined || changePercentage !== undefined) && (
          <div className={`sr-metrics-trend ${getTrendClass()}`}>
            <span className="sr-metrics-trend-icon">{getTrendIcon()}</span>
            {changePercentage !== undefined && (
              <span className="sr-metrics-change-percentage">
                {Math.abs(changePercentage)}%
              </span>
            )}
          </div>
        )}
      </div>
      
      {showSparkline && sparklineData.length > 0 && (
        <div className="sr-metrics-sparkline">
          {/* Simple representation of sparkline */}
          <div className="sr-metrics-sparkline-visual">
            {sparklineData.map((point, index) => (
              <div 
                key={index} 
                className="sr-metrics-sparkline-point" 
                style={{ height: `${point}%` }}
              />
            ))}
          </div>
        </div>
      )}
      
      {lastUpdated && (
        <div className="sr-metrics-last-updated">
          Updated: {lastUpdated}
        </div>
      )}
    </Card>
  );
};

export default MetricsCard;
