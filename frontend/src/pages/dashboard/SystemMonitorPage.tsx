// pages/dashboard/SystemMonitorPage.tsx
import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/store';
import './SystemMonitorPage.css';

export const SystemMonitorPage: React.FC = () => {
  const metrics = useSelector((state: RootState) => state.metrics);
  const cpu = useSelector((state: RootState) => state.cpu);
  const memory = useSelector((state: RootState) => state.memory);
  const disk = useSelector((state: RootState) => state.disk);
  const network = useSelector((state: RootState) => state.network);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatRate = (bytesPerSecond: number) => {
    return formatBytes(bytesPerSecond) + '/s';
  };

  return (
    <div className="system-monitor-page">
      <div className="page-header">
        <div className="header-content">
          <h1>◆ System Monitor</h1>
          <p>Real-time system metrics and performance monitoring</p>
        </div>
        <div className="connection-status">
          <span className={`status-dot status-${metrics.status}`}></span>
          <span className="status-text">{metrics.status?.toUpperCase()}</span>
        </div>
      </div>

      <div className="monitor-content">
        {/* CPU Metrics */}
        <div className="metric-panel">
          <div className="panel-header">
            <h2>◆ CPU Usage</h2>
            <span className="metric-value">{cpu.current?.percent?.toFixed(1) || '0.0'}%</span>
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill cpu-fill"
              style={{ width: `${cpu.current?.percent || 0}%` }}
            ></div>
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span>Load Average:</span>
              <span>{cpu.current?.load_avg?.map(l => l.toFixed(2)).join(', ') || 'N/A'}</span>
            </div>
            <div className="detail-item">
              <span>Process Count:</span>
              <span>{cpu.current?.process_count || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Memory Metrics */}
        <div className="metric-panel">
          <div className="panel-header">
            <h2>🧠 Memory Usage</h2>
            <span className="metric-value">{memory.current?.percent?.toFixed(1) || '0.0'}%</span>
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill memory-fill"
              style={{ width: `${memory.current?.percent || 0}%` }}
            ></div>
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span>Used:</span>
              <span>{formatBytes(memory.current?.used || 0)}</span>
            </div>
            <div className="detail-item">
              <span>Total:</span>
              <span>{formatBytes(memory.current?.total || 0)}</span>
            </div>
            <div className="detail-item">
              <span>Available:</span>
              <span>{formatBytes(memory.current?.available || 0)}</span>
            </div>
          </div>
        </div>

        {/* Disk Metrics */}
        <div className="metric-panel">
          <div className="panel-header">
            <h2>💾 Disk Usage</h2>
            <span className="metric-value">{disk.current?.percent?.toFixed(1) || '0.0'}%</span>
          </div>
          <div className="metric-bar">
            <div 
              className="metric-fill disk-fill"
              style={{ width: `${disk.current?.percent || 0}%` }}
            ></div>
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span>Used:</span>
              <span>{formatBytes(disk.current?.used || 0)}</span>
            </div>
            <div className="detail-item">
              <span>Free:</span>
              <span>{formatBytes(disk.current?.free || 0)}</span>
            </div>
            <div className="detail-item">
              <span>Total:</span>
              <span>{formatBytes(disk.current?.total || 0)}</span>
            </div>
          </div>
        </div>

        {/* Network Metrics */}
        <div className="metric-panel">
          <div className="panel-header">
            <h2>🌐 Network Activity</h2>
            <span className="metric-value">
              ↓{formatRate(network.current?.recv_rate || 0)} ↑{formatRate(network.current?.sent_rate || 0)}
            </span>
          </div>
          <div className="network-bars">
            <div className="network-bar">
              <span className="network-label">Download</span>
              <div className="metric-bar">
                <div 
                  className="metric-fill network-recv-fill"
                  style={{ width: `${Math.min((network.current?.recv_rate || 0) / 1000000 * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            <div className="network-bar">
              <span className="network-label">Upload</span>
              <div className="metric-bar">
                <div 
                  className="metric-fill network-sent-fill"
                  style={{ width: `${Math.min((network.current?.sent_rate || 0) / 1000000 * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
          <div className="metric-details">
            <div className="detail-item">
              <span>Total Received:</span>
              <span>{formatBytes(network.current?.bytes_recv || 0)}</span>
            </div>
            <div className="detail-item">
              <span>Total Sent:</span>
              <span>{formatBytes(network.current?.bytes_sent || 0)}</span>
            </div>
          </div>
        </div>

        {/* System Overview */}
        <div className="overview-panel">
          <div className="panel-header">
            <h2>◇ System Overview</h2>
          </div>
          <div className="overview-grid">
            <div className="overview-card">
              <div className="overview-icon">◆</div>
              <div className="overview-content">
                <h3>CPU Health</h3>
                <div className="overview-status">
                  {(cpu.current?.percent || 0) < 80 ? '✅ Good' : '⚠️ High'}
                </div>
              </div>
            </div>
            <div className="overview-card">
              <div className="overview-icon">🧠</div>
              <div className="overview-content">
                <h3>Memory Health</h3>
                <div className="overview-status">
                  {(memory.current?.percent || 0) < 85 ? '✅ Good' : '⚠️ High'}
                </div>
              </div>
            </div>
            <div className="overview-card">
              <div className="overview-icon">💾</div>
              <div className="overview-content">
                <h3>Disk Health</h3>
                <div className="overview-status">
                  {(disk.current?.percent || 0) < 90 ? '✅ Good' : '⚠️ High'}
                </div>
              </div>
            </div>
            <div className="overview-card">
              <div className="overview-icon">🌐</div>
              <div className="overview-content">
                <h3>Network Health</h3>
                <div className="overview-status">✅ Active</div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Status */}
        <div className="agent-status-panel">
          <div className="panel-header">
            <h2>◈ Agent Status</h2>
            <p>Current status of all AI agents</p>
          </div>
          <div className="agent-status-grid">
            <div className="agent-status-card">
              <div className="agent-icon">◆</div>
              <div className="agent-info">
                <h3>Sir Hawkington</h3>
                <div className="agent-status online">Online</div>
              </div>
            </div>
            <div className="agent-status-card">
              <div className="agent-icon">📋</div>
              <div className="agent-info">
                <h3>The Stick V3</h3>
                <div className="agent-status online">Hypervigilant</div>
              </div>
            </div>
            <div className="agent-status-card">
              <div className="agent-icon">◇</div>
              <div className="agent-info">
                <h3>Hamsters</h3>
                <div className="agent-status online">Beer Break</div>
              </div>
            </div>
            <div className="agent-status-card">
              <div className="agent-icon">◈</div>
              <div className="agent-info">
                <h3>Meth Snail</h3>
                <div className="agent-status online">Caffeinated</div>
              </div>
            </div>
            <div className="agent-status-card">
              <div className="agent-icon">👥</div>
              <div className="agent-info">
                <h3>Quantum Shadow</h3>
                <div className="agent-status online">Phased</div>
              </div>
            </div>
            <div className="agent-status-card">
              <div className="agent-icon">◉</div>
              <div className="agent-info">
                <h3>VIC-20 Sage</h3>
                <div className="agent-status online">Ancient Wisdom</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitorPage;
