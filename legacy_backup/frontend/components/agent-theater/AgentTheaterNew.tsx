import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/store';
import { useWebSocketConnection } from '../../hooks/useWebSocketConnection';
import { selectAllAgentDisplayData } from '../../store/slices/agentsSlice';
import { AgentCard } from '../agents/AgentCard';
import styles from './AgentTheater.module.css';

const AGENT_TYPE_MAP: Record<string, 'hawkington' | 'stick' | 'snail' | 'hamsters' | 'qsp' | 'vic20'> = {
  'sir_hawkington': 'hawkington',
  'the_stick': 'stick',
  'meth_snail': 'snail',
  'hamsters': 'hamsters',
  'quantum_shadow_people': 'qsp',
  'vic20_sage': 'vic20'
};

export const AgentTheater: React.FC = () => {
  const { isConnected, connectionStatus } = useWebSocketConnection();
  const agentDisplayData = useSelector(selectAllAgentDisplayData);
  const metrics = useSelector((state: RootState) => state.metrics);
  const auth = useSelector((state: RootState) => state.auth);
  
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const activeCount = agentDisplayData.length;
  const totalCount = 6;

  return (
    <div className={styles.agentTheater}>
      {/* Navigation */}
      <nav className={styles.theaterNav}>
        <div className={styles.navLeft}>
          <button 
            onClick={() => window.location.href = '/'} 
            className={styles.logoButton}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--rebellion-text-bright)',
              fontSize: '1.25rem',
              fontWeight: 700,
              cursor: 'pointer',
              padding: 'var(--space-sm) var(--space-md)',
              borderRadius: 'var(--radius-sm)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--rebellion-surface)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'none';
            }}
          >
            ◆ System Rebellion
          </button>
        </div>
        <div className={styles.navRight}>
          <div style={{ position: 'relative' }}>
            <button 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              style={{
                background: 'var(--rebellion-surface)',
                border: '1px solid var(--rebellion-border)',
                color: 'var(--rebellion-text-bright)',
                padding: 'var(--space-sm) var(--space-md)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: 600
              }}
            >
              {auth.user?.first_name || 'User'}
            </button>
            {showProfileMenu && (
              <div style={{
                position: 'absolute',
                top: 'calc(100% + var(--space-xs))',
                right: 0,
                background: 'var(--rebellion-surface)',
                border: '1px solid var(--rebellion-border)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-sm)',
                minWidth: '150px',
                boxShadow: 'var(--shadow-rebellion)',
                zIndex: 1000
              }}>
                <button style={{
                  width: '100%',
                  background: 'none',
                  border: 'none',
                  color: 'var(--rebellion-text)',
                  padding: 'var(--space-sm)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.875rem'
                }}>Settings</button>
                <button style={{
                  width: '100%',
                  background: 'none',
                  border: 'none',
                  color: 'var(--rebellion-text)',
                  padding: 'var(--space-sm)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.875rem'
                }}>Profile</button>
                <div style={{
                  height: '1px',
                  background: 'var(--rebellion-border)',
                  margin: 'var(--space-xs) 0'
                }}></div>
                <button 
                  onClick={() => {
                    // Logout logic
                  }}
                  style={{
                    width: '100%',
                    background: 'none',
                    border: 'none',
                    color: 'var(--error)',
                    padding: 'var(--space-sm)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.875rem'
                  }}
                >Logout</button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Header */}
      <div className={styles.theaterHeader}>
        <div>
          <h1 style={{
            fontSize: '3rem',
            fontWeight: 800,
            margin: 0,
            marginBottom: 'var(--space-xs)',
            background: 'linear-gradient(135deg, var(--rebellion-text-bright), var(--vic20-cyan), var(--hawkington-gold))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Agent Theater
          </h1>
          <p style={{
            fontSize: '1.125rem',
            color: 'var(--rebellion-text-dim)',
            margin: 0
          }}>
            Watch your AI agents work in real-time
          </p>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-lg)'
        }}>
          {/* Connection Status */}
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
              {connectionStatus}
            </span>
          </div>

          {/* Agent Count */}
          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: 'var(--space-xs)',
            padding: 'var(--space-sm) var(--space-md)',
            background: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid var(--vic20-cyan)',
            borderRadius: 'var(--radius-sm)'
          }}>
            <span style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--vic20-cyan)',
              fontFamily: 'var(--font-mono)'
            }}>
              {activeCount}
            </span>
            <span style={{
              fontSize: '1rem',
              color: 'var(--rebellion-text-dim)'
            }}>
              /{totalCount}
            </span>
            <span style={{
              fontSize: '0.875rem',
              color: 'var(--rebellion-text)',
              fontWeight: 600,
              marginLeft: 'var(--space-xs)'
            }}>
              Active
            </span>
          </div>
        </div>
      </div>

      {/* System Metrics Quick View */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-md)',
        marginBottom: 'var(--space-2xl)'
      }}>
        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase', marginBottom: 'var(--space-xs)' }}>CPU</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--rebellion-text-bright)', fontFamily: 'var(--font-mono)' }}>
              {(metrics.cpu?.usage_percent || metrics.cpu_usage || 0).toFixed(1)}%
            </div>
          </div>
          <div style={{ fontSize: '2rem' }}>⚡</div>
        </div>

        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase', marginBottom: 'var(--space-xs)' }}>Memory</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--rebellion-text-bright)', fontFamily: 'var(--font-mono)' }}>
              {(metrics.memory?.percent || metrics.memory_usage || 0).toFixed(1)}%
            </div>
          </div>
          <div style={{ fontSize: '2rem' }}>🧠</div>
        </div>

        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase', marginBottom: 'var(--space-xs)' }}>Disk</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--rebellion-text-bright)', fontFamily: 'var(--font-mono)' }}>
              {(metrics.disk?.percent || metrics.disk_usage || 0).toFixed(1)}%
            </div>
          </div>
          <div style={{ fontSize: '2rem' }}>💾</div>
        </div>

        <div style={{
          background: 'var(--rebellion-surface)',
          border: '1px solid var(--rebellion-border)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--rebellion-text-dim)', textTransform: 'uppercase', marginBottom: 'var(--space-xs)' }}>Network</div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--rebellion-text-bright)', fontFamily: 'var(--font-mono)' }}>
              ↓ {((metrics.network_recv_rate || 0) / 1024).toFixed(0)} KB/s
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--rebellion-text-dim)', fontFamily: 'var(--font-mono)' }}>
              ↑ {((metrics.network_sent_rate || 0) / 1024).toFixed(0)} KB/s
            </div>
          </div>
          <div style={{ fontSize: '2rem' }}>🌐</div>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: 'var(--space-xl)',
        marginBottom: 'var(--space-2xl)'
      }}>
        {agentDisplayData.length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            background: 'var(--rebellion-surface)',
            border: '1px solid var(--rebellion-border)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-2xl)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)' }}>🎭</div>
            <h3 style={{ color: 'var(--rebellion-text-bright)', marginBottom: 'var(--space-sm)' }}>
              Agents Warming Up...
            </h3>
            <p style={{ color: 'var(--rebellion-text-dim)' }}>
              Your AI agents will appear here once they start processing system metrics.
            </p>
          </div>
        ) : (
          agentDisplayData.map((agent) => (
            <AgentCard
              key={agent.agent_name}
              agent={agent}
              agentType={AGENT_TYPE_MAP[agent.agent_name]}
            />
          ))
        )}
      </div>

      {/* Missing Agents Indicator */}
      {activeCount < totalCount && activeCount > 0 && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid var(--warning)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-lg)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-sm)' }}>⏳</div>
          <p style={{ color: 'var(--warning)', margin: 0, fontWeight: 600 }}>
            {totalCount - activeCount} agent{totalCount - activeCount !== 1 ? 's' : ''} waiting for activity
          </p>
        </div>
      )}
    </div>
  );
};

export default AgentTheater;
