// frontend/src/components/metrics/NetworkMetrics/tabs/TopBandwidthProcesses.tsx

import React from 'react';
import { NetworkProcess } from './types';
import { formatBytes } from '../utils/formatters';
import './NetworkMetrics.css';

interface TopBandwidthProcessesProps {
  processes: NetworkProcess[];
  compact?: boolean;
  limit?: number;
}

const TopBandwidthProcesses: React.FC<TopBandwidthProcessesProps> = ({ 
  processes, 
  compact: _compact = false,
  limit = 5 
}) => {
  // Sort processes by total bandwidth (read + write)
  const sortedProcesses = [...processes].sort((a, b) => {
    const totalA = (a.read_rate || 0) + (a.write_rate || 0);
    const totalB = (b.read_rate || 0) + (b.write_rate || 0);
    return totalB - totalA; // Sort descending
  });
  
  // Limit to the top N processes if specified
  const topProcesses = limit ? sortedProcesses.slice(0, limit) : sortedProcesses;
  
  // If no process data available
  if (!topProcesses || topProcesses.length === 0) {
    return (
      <div className="network-section">
        <div className="network-section-title">Top Bandwidth Consumers</div>
        <div className="no-data-message">No process data available</div>
      </div>
    );
  }

  return (
    <div className="network-section">
      <div className="network-section-title">Top Bandwidth Consumers</div>
      <div className="bandwidth-processes">
        {topProcesses.map((process, index) => {
          const totalBandwidth = (process.read_rate || 0) + (process.write_rate || 0);
          const downloadPercent = totalBandwidth ? (process.read_rate || 0) / totalBandwidth * 100 : 0;
          const uploadPercent = totalBandwidth ? (process.write_rate || 0) / totalBandwidth * 100 : 0;
          
          return (
            <div key={index} className="bandwidth-process">
              <div className="process-header">
                <div className="process-name">{process.name}</div>
                <div className="process-pid">PID: {process.pid}</div>
                <div className="process-bandwidth">{formatBytes(totalBandwidth)}/s</div>
              </div>
              
              <div className="bandwidth-bars">
                <div className="bandwidth-bar-container">
                  <div className="bandwidth-label">
                    <span>Download</span>
                    <span>{formatBytes(process.read_rate || 0)}/s</span>
                  </div>
                  <div className="bandwidth-bar">
                    <div 
                      className="bandwidth-bar-fill download"
                      style={{ width: `${downloadPercent}%` }}
                    />
                  </div>
                </div>
                
                <div className="bandwidth-bar-container">
                  <div className="bandwidth-label">
                    <span>Upload</span>
                    <span>{formatBytes(process.write_rate || 0)}/s</span>
                  </div>
                  <div className="bandwidth-bar">
                    <div 
                      className="bandwidth-bar-fill upload"
                      style={{ width: `${uploadPercent}%` }}
                    />
                  </div>
                </div>
              </div>
              
              <div className="process-connections">
                Connections: {process.connection_count || 0}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TopBandwidthProcesses;