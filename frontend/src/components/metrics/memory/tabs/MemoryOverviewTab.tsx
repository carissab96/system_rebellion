import React from 'react';
import { ProcessedMemoryData } from '../types';
import { formatBytes } from '../utils/formatters';
import { ProgressBar } from '@/design-system/components/ProgressBar/ProgressBar';
import { Card } from '@/design-system/components/Card';
import { InfoTooltip } from '@/design-system/components/InfoTooltip/InfoTooltip';

interface MemoryOverviewTabProps {
  data: ProcessedMemoryData;
  compact?: boolean;
}

export const MemoryOverviewTab: React.FC<MemoryOverviewTabProps> = ({ data, compact = false }) => {
  const { overview } = data;
  
  // Determine severity levels for various indicators
  const getPhysicalMemorySeverity = () => {
    const percent = overview.physicalMemory.percentUsed;
    if (percent > 90) return 'critical';
    if (percent > 75) return 'warning';
    return 'normal';
  };
  
  const getSwapSeverity = () => {
    const percent = overview.swap.percentUsed;
    if (percent > 50) return 'warning';
    if (percent > 25) return 'caution';
    return 'normal';
  };
  
  const getPressureSeverityColor = () => {
    switch (overview.pressureLevel) {
      case 'high': return 'var(--color-danger)';
      case 'medium': return 'var(--color-warning)';
      case 'low': return 'var(--color-success)';
      default: return 'var(--color-text-secondary)';
    }
  };
  
  // Compact view for dashboard
  if (compact) {
    return (
      <Card className="memory-overview memory-overview--compact">
        <div className="memory-overview__header">
          <h3>Memory</h3>
          <span className="memory-pressure-indicator" style={{ color: getPressureSeverityColor() }}>
            {overview.pressureLevel.toUpperCase()}
          </span>
        </div>
        
        <ProgressBar 
          value={overview.physicalMemory.percentUsed} 
          severity={getPhysicalMemorySeverity()}
          label={`${formatBytes(overview.physicalMemory.used)} / ${formatBytes(overview.physicalMemory.total)}`}
        />
        
        {overview.swap.total > 0 && (
          <div className="memory-overview__swap-indicator">
            <small>Swap: {overview.swap.percentUsed.toFixed(1)}%</small>
          </div>
        )}
      </Card>
    );
  }
  
  // Full view
  return (
    <div className="memory-overview">
      <div className="memory-overview__header">
        <h2>Memory Overview</h2>
        <div className="memory-pressure-card">
          <span>Memory Pressure:</span>
          <span className="memory-pressure-value" style={{ color: getPressureSeverityColor() }}>
            {overview.pressureLevel.toUpperCase()}
            <InfoTooltip content="Memory pressure indicates how stressed your system's memory is. High pressure may lead to performance degradation." />
          </span>
        </div>
      </div>
      
      <div className="memory-overview__grid">
        {/* Physical Memory Section */}
        <Card className="memory-overview__physical">
          <h3>Physical Memory</h3>
          <ProgressBar 
            value={overview.physicalMemory.percentUsed} 
            severity={getPhysicalMemorySeverity()}
            label={`${overview.physicalMemory.percentUsed.toFixed(1)}%`}
          />
          
          <div className="memory-stats-grid">
            <div className="memory-stat">
              <span className="memory-stat-label">Total</span>
              <span className="memory-stat-value">{formatBytes(overview.physicalMemory.total)}</span>
            </div>
            <div className="memory-stat">
              <span className="memory-stat-label">Used</span>
              <span className="memory-stat-value">{formatBytes(overview.physicalMemory.used)}</span>
            </div>
            <div className="memory-stat">
              <span className="memory-stat-label">Free</span>
              <span className="memory-stat-value">{formatBytes(overview.physicalMemory.free)}</span>
            </div>
          </div>
        </Card>
        
        {/* Swap Memory Section */}
        <Card className="memory-overview__swap">
          <h3>Swap Memory</h3>
          {overview.swap.total === 0 ? (
            <div className="memory-overview__no-swap">
              <p>No swap memory configured on this system.</p>
            </div>
          ) : (
            <>
              <ProgressBar 
                value={overview.swap.percentUsed} 
                severity={getSwapSeverity()}
                label={`${overview.swap.percentUsed.toFixed(1)}%`}
              />
              
              <div className="memory-stats-grid">
                <div className="memory-stat">
                  <span className="memory-stat-label">Total</span>
                  <span className="memory-stat-value">{formatBytes(overview.swap.total)}</span>
                </div>
                <div className="memory-stat">
                  <span className="memory-stat-label">Used</span>
                  <span className="memory-stat-value">{formatBytes(overview.swap.used)}</span>
                </div>
                <div className="memory-stat">
                  <span className="memory-stat-label">Free</span>
                  <span className="memory-stat-value">{formatBytes(overview.swap.free)}</span>
                </div>
              </div>
              
              <div className="memory-stat memory-swap-rate">
                <span className="memory-stat-label">Page I/O</span>
                <div className="memory-stat-value">
                  <span className="page-in">
                    In: {overview.pressureIndicators.pageInRate.toFixed(1)}/s
                  </span>
                  <span className="page-out">
                    Out: {overview.pressureIndicators.pageOutRate.toFixed(1)}/s
                  </span>
                </div>
              </div>
            </>
          )}
        </Card>
        
        {/* Memory Type Breakdown */}
        <Card className="memory-overview__breakdown">
          <h3>Memory Type Breakdown</h3>
          <div className="memory-type-bars">
            <div className="memory-type-bar">
              <div className="memory-type-bar__label">
                <span>Active</span>
                <InfoTooltip content="Memory that has been used recently and is typically not reclaimed unless necessary" />
              </div>
              <ProgressBar 
                value={(overview.active / overview.physicalMemory.total) * 100} 
                color="var(--color-primary)"
                label={formatBytes(overview.active)}
              />
            </div>
            
            <div className="memory-type-bar">
              <div className="memory-type-bar__label">
                <span>Cached</span>
                <InfoTooltip content="Memory used for disk caching. Can be reclaimed when needed by applications" />
              </div>
              <ProgressBar 
                value={(overview.cached / overview.physicalMemory.total) * 100} 
                color="var(--color-info)"
                label={formatBytes(overview.cached)}
              />
            </div>
            
            <div className="memory-type-bar">
              <div className="memory-type-bar__label">
                <span>Buffers</span>
                <InfoTooltip content="Memory used for file system metadata and other kernel operations" />
              </div>
              <ProgressBar 
                value={(overview.buffers / overview.physicalMemory.total) * 100} 
                color="var(--color-accent)"
                label={formatBytes(overview.buffers)}
              />
            </div>
          </div>
        </Card>
        
        {/* Memory Pressure Details */}
        <Card className="memory-overview__pressure">
          <h3>Memory Pressure Indicators</h3>
          
          <div className="memory-pressure-indicators">
            <div className="pressure-indicator">
              <span className="pressure-indicator__label">
                Page-in Rate
                <InfoTooltip content="Rate at which data is being read from disk into memory. High rates indicate memory shortage." />
              </span>
              <span className="pressure-indicator__value">
                {overview.pressureIndicators.pageInRate.toFixed(2)}/s
                <TrendIndicator 
                  value={overview.pressureIndicators.pageInRate} 
                  threshold={10}
                  higherIsBad={true}
                />
              </span>
            </div>
            
            <div className="pressure-indicator">
              <span className="pressure-indicator__label">
                Page-out Rate
                <InfoTooltip content="Rate at which data is being written from memory to disk. High rates indicate memory pressure." />
              </span>
              <span className="pressure-indicator__value">
                {overview.pressureIndicators.pageOutRate.toFixed(2)}/s
                <TrendIndicator 
                  value={overview.pressureIndicators.pageOutRate} 
                  threshold={5}
                  higherIsBad={true}
                />
              </span>
            </div>
            
            <div className="pressure-indicator">
              <span className="pressure-indicator__label">
                Swap Usage Rate
                <InfoTooltip content="Rate at which swap memory usage is changing. Positive values indicate increasing memory pressure." />
              </span>
              <span className="pressure-indicator__value">
                {overview.pressureIndicators.swapUsageRate > 0 ? '+' : ''}
                {overview.pressureIndicators.swapUsageRate.toFixed(2)} MB/s
                <TrendIndicator 
                  value={overview.pressureIndicators.swapUsageRate} 
                  threshold={1}
                  higherIsBad={true}
                />
              </span>
            </div>
          </div>
          
          <div className="memory-pressure-advice">
            {overview.pressureLevel === 'high' && (
              <p className="memory-advice memory-advice--critical">
                <strong>Critical Memory Pressure:</strong> Your system is experiencing high memory demand. 
                Consider closing unused applications or increasing system memory.
              </p>
            )}
            
            {overview.pressureLevel === 'medium' && (
              <p className="memory-advice memory-advice--warning">
                <strong>Moderate Memory Pressure:</strong> Memory usage is elevated. 
                Monitor for performance impacts and consider optimizing memory-intensive applications.
              </p>
            )}
            
            {overview.pressureLevel === 'low' && (
              <p className="memory-advice memory-advice--good">
                <strong>Low Memory Pressure:</strong> Your system has sufficient memory resources.
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};