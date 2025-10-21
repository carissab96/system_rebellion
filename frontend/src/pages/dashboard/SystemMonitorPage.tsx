import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/store';
import { AgentCard } from '../../components/agents/AgentCard';
import { useWebSocketConnection } from '../../hooks/useWebSocketConnection';
import { selectAllAgentDisplayData } from '../../store/slices/agentsSlice';
import styles from './SystemMonitorPage.module.css';

const AGENT_TYPE_MAP: Record<string, 'hawkington' | 'stick' | 'snail' | 'hamsters' | 'qsp' | 'vic20'> = {
  'sir_hawkington': 'hawkington',
  'the_stick': 'stick',
  'meth_snail': 'snail',
  'hamsters': 'hamsters',
  'quantum_shadow_people': 'qsp',
  'vic20_sage': 'vic20'
};

export const SystemMonitorPage: React.FC = () => {
  // Only metrics WebSocket connection (insights and events are in Agent Theater)
  const { isConnected: metricsConnected } = useWebSocketConnection();
  
  const metrics = useSelector((state: RootState) => state.metrics);
  const agentDisplayData = useSelector(selectAllAgentDisplayData);
  
  // For backward compatibility
  const isConnected = metricsConnected;
  const insightsConnected = false; // Not used here
  const eventsConnected = false; // Not used here
  
  // Metrics are direct properties, not nested in system_info
  const cpu = metrics.cpu;
  const memory = metrics.memory;
  const disk = metrics.disk;
  const network = metrics.network;

  const formatBytes = (bytes: number) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatRate = (bytesPerSecond: number) => {
    return formatBytes(bytesPerSecond) + '/s';
  };

  const getStatusColor = (percent: number) => {
    if (percent >= 90) return 'var(--error)';
    if (percent >= 75) return 'var(--warning)';
    return 'var(--success)';
  };

  return (
    <div className={styles.systemMonitorPage}>
      {/* Header */}
      <div className="page-header" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-xl)',
        padding: 'var(--space-lg)',
        background: 'var(--rebellion-surface)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--rebellion-border)'
      }}>
        <div>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: 'var(--rebellion-text-bright)',
            margin: 0,
            marginBottom: 'var(--space-xs)'
          }}>
            ◆ System Monitor
          </h1>
          <p style={{
            color: 'var(--rebellion-text-dim)',
            margin: 0
          }}>
            Real-time system metrics and agent activity
          </p>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          padding: 'var(--space-sm) var(--space-md)',
          background: isConnected ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${isConnected ? 'var(--success)' : 'var(--error)'}`,
          borderRadius: 'var(--radius-sm)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isConnected ? 'var(--success)' : 'var(--error)',
            boxShadow: `0 0 8px ${isConnected ? 'var(--success)' : 'var(--error)'}`
          }}></span>
          <span style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: isConnected ? 'var(--success)' : 'var(--error)',
            textTransform: 'uppercase'
          }}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* WebSocket Connection Status for All 3 Endpoints */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 'var(--space-md)',
        marginBottom: 'var(--space-lg)'
      }}>
        {/* Metrics Endpoint */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: `1px solid ${metricsConnected ? 'var(--success)' : 'var(--error)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-md)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: metricsConnected ? 'var(--success)' : 'var(--error)',
            boxShadow: `0 0 8px ${metricsConnected ? 'var(--success)' : 'var(--error)'}`
          }}></span>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase' }}>
              Metrics
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: metricsConnected ? 'var(--success)' : 'var(--error)' }}>
              {metricsConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        {/* Agent Insights Endpoint */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: `1px solid ${insightsConnected ? 'var(--success)' : 'var(--error)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-md)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: insightsConnected ? 'var(--success)' : 'var(--error)',
            boxShadow: `0 0 8px ${insightsConnected ? 'var(--success)' : 'var(--error)'}`
          }}></span>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase' }}>
              Agent Insights
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: insightsConnected ? 'var(--success)' : 'var(--error)' }}>
              {insightsConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        {/* Agent Events Endpoint */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: `1px solid ${eventsConnected ? 'var(--success)' : 'var(--error)'}`,
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-md)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: eventsConnected ? 'var(--success)' : 'var(--error)',
            boxShadow: `0 0 8px ${eventsConnected ? 'var(--success)' : 'var(--error)'}`
          }}></span>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase' }}>
              Agent Events
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: eventsConnected ? 'var(--success)' : 'var(--error)' }}>
              {eventsConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </div>

      {/* System Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 'var(--space-lg)',
        marginBottom: 'var(--space-xl)'
      }}>
        {/* CPU */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <h3 style={{ margin: 0, color: 'var(--rebellion-text-bright)' }}>CPU Usage</h3>
            <span style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              fontFamily: 'var(--font-mono)',
              color: getStatusColor(cpu?.usage_percent || metrics.cpu_usage || 0)
            }}>
              {(cpu?.usage_percent || metrics.cpu_usage || 0).toFixed(1)}%
            </span>
          </div>
          <div style={{
            height: '8px',
            background: 'var(--rebellion-bg-dark)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${cpu?.usage_percent || metrics.cpu_usage || 0}%`,
              background: getStatusColor(cpu?.usage_percent || metrics.cpu_usage || 0),
              transition: 'width 0.3s ease'
            }}></div>
          </div>
          <div style={{ marginTop: 'var(--space-md)', fontSize: '0.875rem', color: 'var(--rebellion-text-dim)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
              <span>Processes:</span>
              <span>{metrics.process_count || 'N/A'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Cores:</span>
              <span>{cpu?.physical_cores || 'N/A'} physical / {cpu?.logical_cores || 'N/A'} logical</span>
            </div>
          </div>
        </div>

        {/* Memory */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <h3 style={{ margin: 0, color: 'var(--rebellion-text-bright)' }}>Memory Usage</h3>
            <span style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              fontFamily: 'var(--font-mono)',
              color: getStatusColor(memory?.percent || metrics.memory_usage || 0)
            }}>
              {(memory?.percent || metrics.memory_usage || 0).toFixed(1)}%
            </span>
          </div>
          <div style={{
            height: '8px',
            background: 'var(--rebellion-bg-dark)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${memory?.percent || metrics.memory_usage || 0}%`,
              background: getStatusColor(memory?.percent || metrics.memory_usage || 0),
              transition: 'width 0.3s ease'
            }}></div>
          </div>
          <div style={{ marginTop: 'var(--space-md)', fontSize: '0.875rem', color: 'var(--rebellion-text-dim)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
              <span>Used:</span>
              <span>{formatBytes(memory?.used || 0)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Total:</span>
              <span>{formatBytes(memory?.total || 0)}</span>
            </div>
          </div>
        </div>

        {/* Disk */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <h3 style={{ margin: 0, color: 'var(--rebellion-text-bright)' }}>Disk Usage</h3>
            <span style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              fontFamily: 'var(--font-mono)',
              color: getStatusColor(disk?.percent || metrics.disk_usage || 0)
            }}>
              {(disk?.percent || metrics.disk_usage || 0).toFixed(1)}%
            </span>
          </div>
          <div style={{
            height: '8px',
            background: 'var(--rebellion-bg-dark)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${disk?.percent || metrics.disk_usage || 0}%`,
              background: getStatusColor(disk?.percent || metrics.disk_usage || 0),
              transition: 'width 0.3s ease'
            }}></div>
          </div>
          <div style={{ marginTop: 'var(--space-md)', fontSize: '0.875rem', color: 'var(--rebellion-text-dim)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
              <span>Used:</span>
              <span>{formatBytes(disk?.used || 0)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Free:</span>
              <span>{formatBytes(disk?.free || 0)}</span>
            </div>
          </div>
        </div>

        {/* Network */}
        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-lg)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
            <h3 style={{ margin: 0, color: 'var(--rebellion-text-bright)' }}>Network Activity</h3>
            <span style={{
              fontSize: '1rem',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              color: 'var(--info)'
            }}>
              ↓ {formatRate(metrics.network_recv_rate || 0)} / ↑ {formatRate(metrics.network_sent_rate || 0)}
            </span>
          </div>
          <div style={{ marginTop: 'var(--space-md)', fontSize: '0.875rem', color: 'var(--rebellion-text-dim)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
              <span>Bytes Received:</span>
              <span>{formatBytes(network?.bytes_recv || 0)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
              <span>Bytes Sent:</span>
              <span>{formatBytes(network?.bytes_sent || 0)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Packets:</span>
              <span>↓ {network?.packets_recv?.toLocaleString() || '0'} / ↑ {network?.packets_sent?.toLocaleString() || '0'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Agents Section */}
      <div style={{ marginBottom: 'var(--space-lg)' }}>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: 600,
          color: 'var(--rebellion-text-bright)',
          marginBottom: 'var(--space-md)'
        }}>
          ◆ Active Agents ({agentDisplayData.length})
        </h2>
        
        {agentDisplayData.length === 0 ? (
          <div style={{
            background: 'var(--rebellion-surface)',
            border: '1px solid var(--rebellion-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-xl)',
            textAlign: 'center',
            color: 'var(--rebellion-text-dim)'
          }}>
            <p style={{ margin: 0, fontSize: '1.125rem' }}>
              No agent activity detected yet. Agents will appear here once they start processing system metrics.
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: 'var(--space-lg)'
          }}>
            {agentDisplayData.map((agent) => (
              <AgentCard
                key={agent.agent_name}
                agent={agent}
                agentType={AGENT_TYPE_MAP[agent.agent_name]}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
