import React, { useState } from 'react';
import { ProcessedDiskData } from '../types';
import { formatBytes, formatNumber } from '../utils/formatters';
import { Card } from '@/design-system/components/Card';
import { LineChart } from '@/components/common/LineChart';
import { Badge } from '@/design-system/components/Badge';
import { ProgressBar } from '@/components/common/ProgressBar';
import { Table, TableColumn } from '@/components/common/Table';
import { InfoTooltip } from '@/components/common/InfoTooltip';

interface DiskPerformanceTabProps {
  data: ProcessedDiskData;
}

export const DiskPerformanceTab: React.FC<DiskPerformanceTabProps> = ({ data }) => {
  const [selectedProcess, setSelectedProcess] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState<'minute' | 'hour' | 'day'>('minute');
  
  const { performance } = data;
  
  // Process table columns
  const processColumns: TableColumn<ProcessedDiskData['performance']['topProcesses'][0]>[] = [
    {
      key: 'pid',
      header: 'PID',
      sortable: true,
      width: '10%'
    },
    {
      key: 'name',
      header: 'Process',
      sortable: true,
      width: '25%'
    },
    {
      key: 'readRate',
      header: 'Read',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.readRate) + '/s'
    },
    {
      key: 'writeRate',
      header: 'Write',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.writeRate) + '/s'
    },
    {
      key: 'totalRate',
      header: 'Total I/O',
      sortable: true,
      width: '15%',
      render: (process) => formatBytes(process.totalRate) + '/s'
    },
    {
      key: 'percentage',
      header: '% of I/O',
      sortable: true,
      width: '20%',
      render: (process) => (
        <ProgressBar 
          value={process.percentage} 
          severity={
            process.percentage > 80 ? 'warning' : 'normal'
          }
          label={`${process.percentage.toFixed(1)}%`}
        />
      )
    }
  ];
  
  // Helper function to get severity class for latency
  const getLatencySeverityClass = (latency: number): string => {
    if (latency > 20) return 'severity-critical';
    if (latency > 10) return 'severity-warning';
    return 'severity-normal';
  };
  
  // Helper function to get color for bottleneck severity
  const getBottleneckSeverityColor = (severity: 'low' | 'medium' | 'high' | null): string => {
    if (!severity) return 'var(--color-text-secondary)';
    
    switch (severity) {
      case 'high': return 'var(--color-danger)';
      case 'medium': return 'var(--color-warning)';
      case 'low': return 'var(--color-info)';
      default: return 'var(--color-text-secondary)';
    }
  };
  
  return (
    <div className="disk-performance">
      <div className="disk-performance__header">
        <h2>Disk I/O Performance</h2>
        <div className="disk-performance__summary">
          <div className="performance-metric">
            <span className="performance-metric__label">Read:</span>
            <span className="performance-metric__value">{formatBytes(performance.current.readSpeed)}/s</span>
          </div>
          <div className="performance-metric">
            <span className="performance-metric__label">Write:</span>
            <span className="performance-metric__value">{formatBytes(performance.current.writeSpeed)}/s</span>
          </div>
          <div className="performance-metric">
            <span className="performance-metric__label">Utilization:</span>
            <span className="performance-metric__value">{performance.current.utilization.toFixed(1)}%</span>
          </div>
        </div>
      </div>
      
      <div className="disk-performance__grid">
        <Card className="disk-performance__charts">
          <div className="chart-header">
            <h3>I/O Performance History</h3>
            <div className="chart-time-selector">
              <button 
                className={`chart-time-btn ${timeRange === 'minute' ? 'active' : ''}`}
                onClick={() => setTimeRange('minute')}
              >
                Minute
              </button>
              <button 
                className={`chart-time-btn ${timeRange === 'hour' ? 'active' : ''}`}
                onClick={() => setTimeRange('hour')}
              >
                Hour
              </button>
              <button 
                className={`chart-time-btn ${timeRange === 'day' ? 'active' : ''}`}
                onClick={() => setTimeRange('day')}
              >
                Day
              </button>
            </div>
          </div>
          
          <div className="performance-charts">
            <div className="performance-chart">
              <h4>Throughput (Bytes/s)</h4>
              <LineChart
                data={[
                  {
                    name: 'Read',
                    color: 'var(--color-primary)',
                    values: performance.historical.timestamps.map((ts, idx) => ({
                      x: ts,
                      y: performance.historical.readSpeed[idx] / (1024 * 1024) // Convert to MB/s
                    }))
                  },
                  {
                    name: 'Write',
                    color: 'var(--color-secondary)',
                    values: performance.historical.timestamps.map((ts, idx) => ({
                      x: ts,
                      y: performance.historical.writeSpeed[idx] / (1024 * 1024) // Convert to MB/s
                    }))
                  }
                ]}
                yAxisLabel="MB/s"
                height={200}
                showLegend={true}
              />
            </div>
            
            <div className="performance-chart">
              <h4>IOPS (Operations/s)</h4>
              <LineChart
                data={[
                  {
                    name: 'Read IOPS',
                    color: 'var(--color-info)',
                    values: performance.historical.timestamps.map((ts, idx) => ({
                      x: ts,
                      y: performance.historical.readIOPS[idx]
                    }))
                  },
                  {
                    name: 'Write IOPS',
                    color: 'var(--color-accent)',
                    values: performance.historical.timestamps.map((ts, idx) => ({
                      x: ts,
                      y: performance.historical.writeIOPS[idx]
                    }))
                  }
                ]}
                yAxisLabel="Operations/s"
                height={200}
                showLegend={true}
              />
            </div>
            
            <div className="performance-chart">
              <h4>Disk Utilization</h4>
              <LineChart
                data={[
                  {
                    name: 'Utilization',
                    color: 'var(--color-warning)',
                    values: performance.historical.timestamps.map((ts, idx) => ({
                      x: ts,
                      y: performance.historical.utilization[idx]
                    }))
                  }
                ]}
                yAxisLabel="%"
                height={150}
                yMax={100}
                thresholds={[
                  { value: 90, label: 'Critical', color: 'var(--color-danger)' },
                  { value: 70, label: 'Warning', color: 'var(--color-warning)' }
                ]}
              />
            </div>
          </div>
        </Card>
        
        <Card className="disk-performance__current">
          <h3>Current I/O Performance</h3>
          
          <div className="current-performance-metrics">
            <div className="current-performance-metric">
              <div className="metric-block">
                <h4>
                  Throughput
                  <InfoTooltip content="Amount of data read from or written to the disk per second" />
                </h4>
                <div className="metric-value-group">
                  <div className="metric-value">
                    <span className="metric-label">Read:</span>
                    <span className="metric-value">{formatBytes(performance.current.readSpeed)}/s</span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Write:</span>
                    <span className="metric-value">{formatBytes(performance.current.writeSpeed)}/s</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="current-performance-metric">
              <div className="metric-block">
                <h4>
                  IOPS
                  <InfoTooltip content="Input/Output Operations Per Second. Measures the number of read and write operations." />
                </h4>
                <div className="metric-value-group">
                  <div className="metric-value">
                    <span className="metric-label">Read:</span>
                    <span className="metric-value">{formatNumber(performance.current.readIOPS)}/s</span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Write:</span>
                    <span className="metric-value">{formatNumber(performance.current.writeIOPS)}/s</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="current-performance-metric">
              <div className="metric-block">
                <h4>
                  Latency
                  <InfoTooltip content="Time it takes to complete a disk I/O request. Lower is better." />
                </h4>
                <div className="metric-value-group">
                  <div className="metric-value">
                    <span className="metric-label">Read:</span>
                    <span className={`metric-value ${getLatencySeverityClass(performance.current.latency.read)}`}>
                      {performance.current.latency.read.toFixed(2)} ms
                    </span>
                  </div>
                  <div className="metric-value">
                    <span className="metric-label">Write:</span>
                    <span className={`metric-value ${getLatencySeverityClass(performance.current.latency.write)}`}>
                      {performance.current.latency.write.toFixed(2)} ms
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="current-performance-metric">
              <div className="metric-block">
                <h4>
                  Utilization
                  <InfoTooltip content="Percentage of time the disk is busy processing I/O requests." />
                </h4>
                <div className="metric-chart">
                  <ProgressBar 
                    value={performance.current.utilization} 
                    severity={
                      performance.current.utilization > 90 ? 'critical' :
                      performance.current.utilization > 70 ? 'warning' : 'normal'
                    }
                    label={`${performance.current.utilization.toFixed(1)}%`}
                  />
                </div>
              </div>
            </div>
          </div>
        </Card>
        
        <Card className="disk-performance__bottlenecks">
          <h3>I/O Bottleneck Analysis</h3>
          
          {performance.bottlenecks.detected ? (
            <div className="bottleneck-detected">
              <div className="bottleneck-header">
                <Badge 
                  type={
                    performance.bottlenecks.severity === 'high' ? 'danger' :
                    performance.bottlenecks.severity === 'medium' ? 'warning' : 'info'
                  }
                >
                  {performance.bottlenecks.severity ? performance.bottlenecks.severity.toUpperCase() : 'UNKNOWN'} BOTTLENECK
                </Badge>
                <h4>
                  {performance.bottlenecks.type === 'read' ? 'Read Bottleneck' :
                   performance.bottlenecks.type === 'write' ? 'Write Bottleneck' :
                   performance.bottlenecks.type === 'mixed' ? 'Read/Write Bottleneck' : 'I/O Bottleneck'}
                </h4>
              </div>
              
              <div className="bottleneck-details">
                <p className="bottleneck-cause">
                  <strong>Likely Cause:</strong> {performance.bottlenecks.cause || 'Unknown'}
                </p>
                
                {performance.bottlenecks.process && (
                  <div className="bottleneck-process">
                    <p>
                      <strong>Process Causing Bottleneck:</strong> {performance.bottlenecks.process.name} (PID: {performance.bottlenecks.process.pid})
                    </p>
                    <p>
                      I/O Rate: {formatBytes(performance.bottlenecks.process.ioRate)}/s
                    </p>
                  </div>
                )}
                
                <div className="bottleneck-recommendations">
                  <h5>Recommendations:</h5>
                  <ul className="recommendations-list">
                    {performance.bottlenecks.recommendations.map((rec, idx) => (
                      <li key={idx} className="recommendation-item">{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="no-bottleneck">
              <div className="no-bottleneck__icon">✓</div>
              <p className="no-bottleneck__message">No disk I/O bottlenecks detected.</p>
              <p className="no-bottleneck__details">
                Current disk I/O performance appears to be normal without any significant bottlenecks.
              </p>
            </div>
          )}
        </Card>
        
        <Card className="disk-performance__processes">
          <h3>Top I/O Processes</h3>
          
          <Table
            columns={processColumns}
            data={performance.topProcesses}
            onRowClick={(process) => setSelectedProcess(process.pid === selectedProcess ? null : process.pid)}
            highlightedRow={(row) => row.pid === selectedProcess}
            emptyMessage="No I/O process data available."
          />
          
          {selectedProcess && (
            <div className="selected-process-details">
              {(() => {
                const process = performance.topProcesses.find(p => p.pid === selectedProcess);
                if (!process) return null;
                
                return (
                  <div className="process-io-details">
                    <h4>{process.name} (PID: {process.pid})</h4>
                    <div className="process-io-stats">
                      <div className="io-stat">
                        <span className="io-stat__label">Read Rate:</span>
                        <span className="io-stat__value">{formatBytes(process.readRate)}/s</span>
                      </div>
                      <div className="io-stat">
                        <span className="io-stat__label">Write Rate:</span>
                        <span className="io-stat__value">{formatBytes(process.writeRate)}/s</span>
                      </div>
                      <div className="io-stat">
                        <span className="io-stat__label">Total I/O:</span>
                        <span className="io-stat__value">{formatBytes(process.totalRate)}/s</span>
                      </div>
                      <div className="io-stat">
                        <span className="io-stat__label">% of System I/O:</span>
                        <span className="io-stat__value">{process.percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                    
                    {performance.bottlenecks.process?.pid === process.pid && (
                      <div className="process-bottleneck-warning">
                        <Badge type="danger">BOTTLENECK</Badge>
                        <p>This process is identified as causing an I/O bottleneck.</p>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};