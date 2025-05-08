import React from 'react';
import './NetworkMetrics.css';

interface Process {
  pid: number;
  name: string;
  read_rate?: number;
  write_rate?: number;
  total_rate?: number;
  connection_count?: number;
  protocols?: {
    tcp?: number;
    udp?: number;
    unix?: number;
    [key: string]: number | undefined;
  };
}

interface TopBandwidthProcessesProps {
  processes: Process[];
}

const TopBandwidthProcesses: React.FC<TopBandwidthProcessesProps> = ({ processes }) => {
  // Format bytes to human-readable format
  const formatBytes = (bytes?: number): string => {
    if (!bytes && bytes !== 0) return 'N/A';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };
  
  // Format rate to human-readable format
  const formatRate = (bytesPerSec?: number): string => {
    if (!bytesPerSec && bytesPerSec !== 0) return 'N/A';
    
    return `${formatBytes(bytesPerSec)}/s`;
  };
  
  // Calculate percentage of total bandwidth
  const calculatePercentage = (process: Process): string => {
    if (!process.total_rate) return '0%';
    
    const totalBandwidth = processes.reduce((sum, p) => sum + (p.total_rate || 0), 0);
    if (totalBandwidth === 0) return '0%';
    
    return `${((process.total_rate / totalBandwidth) * 100).toFixed(1)}%`;
  };
  
  // Get process icon based on name
  const getProcessIcon = (processName: string): string => {
    const name = processName.toLowerCase();
    
    if (name.includes('chrome') || name.includes('chromium')) return '🌐';
    if (name.includes('firefox')) return '🦊';
    if (name.includes('edge')) return '🌀';
    if (name.includes('safari')) return '🧭';
    
    if (name.includes('discord')) return '💬';
    if (name.includes('slack')) return '💼';
    if (name.includes('teams')) return '👥';
    if (name.includes('zoom')) return '🎥';
    
    if (name.includes('spotify')) return '🎵';
    if (name.includes('netflix') || name.includes('video')) return '🎬';
    if (name.includes('download')) return '⬇️';
    if (name.includes('upload')) return '⬆️';
    
    if (name.includes('system') || name.includes('kernel')) return '⚙️';
    if (name.includes('python')) return '🐍';
    if (name.includes('node')) return '📦';
    if (name.includes('java')) return '☕';
    
    return '📊';
  };
  
  // Sort processes by total bandwidth usage
  const sortedProcesses = [...processes].sort((a, b) => 
    (b.total_rate || 0) - (a.total_rate || 0)
  );
  
  // Calculate total bandwidth
  const totalBandwidth = processes.reduce((sum, p) => sum + (p.total_rate || 0), 0);
  
  return (
    <div className="top-bandwidth-processes">
      <div className="bandwidth-summary">
        <div className="summary-item">
          <span className="summary-label">Total Bandwidth</span>
          <span className="summary-value">{formatRate(totalBandwidth)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Active Processes</span>
          <span className="summary-value">{processes.length}</span>
        </div>
      </div>
      
      {sortedProcesses.length > 0 ? (
        <div className="process-list">
          {sortedProcesses.map((process, index) => (
            <div key={`${process.pid}-${index}`} className="process-item">
              <div className="process-rank">{index + 1}</div>
              <div className="process-icon">{getProcessIcon(process.name)}</div>
              <div className="process-info">
                <div className="process-name">
                  {process.name}
                  <span className="process-pid">({process.pid})</span>
                </div>
                <div className="process-bandwidth-bar">
                  <div 
                    className="bandwidth-fill" 
                    style={{ 
                      width: `${Math.min(((process.total_rate || 0) / (sortedProcesses[0].total_rate || 1)) * 100, 100)}%` 
                    }}
                  />
                </div>
                <div className="process-details">
                  <span className="process-rate">{formatRate(process.total_rate)}</span>
                  <span className="process-percentage">{calculatePercentage(process)}</span>
                  {process.connection_count !== undefined && (
                    <span className="process-connections">{process.connection_count} conn</span>
                  )}
                </div>
                {process.protocols && (
                  <div className="process-protocols">
                    {Object.entries(process.protocols)
                      .filter(([_, count]) => count && count > 0)
                      .map(([protocol, count]) => (
                        <span key={protocol} className="protocol-tag">
                          {protocol.toUpperCase()}: {count}
                        </span>
                      ))
                    }
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-processes">
          <p>No active network processes detected.</p>
          <p>The Meth Snail suggests checking if your system is in a quantum state of network isolation.</p>
        </div>
      )}
      
      <div className="process-note">
        <div className="note-icon">🔍</div>
        <div className="note-text">
          {sortedProcesses.length > 0 && sortedProcesses[0].total_rate && sortedProcesses[0].total_rate > 1000000 ? (
            <span className="note-warning">
              Sir Hawkington has detected unusually high bandwidth usage from {sortedProcesses[0].name}. 
              Perhaps it's time for an aristocratic investigation?
            </span>
          ) : (
            <span>
              All processes are using bandwidth within reasonable parameters. 
              The Hamsters approve of your network usage patterns.
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopBandwidthProcesses;
