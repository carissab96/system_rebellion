import React from 'react';
import type { AgentDisplayData } from '../../store/slices/agentsSlice';
import styles from '../../styles/modules/AgentCard.module.css';

interface AgentCardProps {
  agent: AgentDisplayData;
  agentType: 'hawkington' | 'stick' | 'snail' | 'hamsters' | 'qsp' | 'vic20';
  onClick?: () => void;
}

const AGENT_COLORS = {
  hawkington: '#e6ac00',
  stick: '#f97316',
  snail: '#00d084',
  hamsters: '#ff8c42',
  qsp: '#a855f7',
  vic20: '#06b6d4'
};

const AGENT_DISPLAY_NAMES = {
  hawkington: 'Sir Hawkington',
  stick: 'The Stick',
  snail: 'Meth Snail',
  hamsters: 'The Hamsters',
  qsp: 'Quantum Shadow People',
  vic20: 'VIC-20 Sage'
};

export const AgentCard: React.FC<AgentCardProps> = ({ agent, agentType, onClick }) => {
  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div 
      className={`${styles.agentCard} ${styles[agentType]}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className={styles.agentHeader}>
        <h3 
          className={styles.agentName}
          style={{ color: AGENT_COLORS[agentType] }}
        >
          {AGENT_DISPLAY_NAMES[agentType]}
        </h3>
        <span className={`${styles.agentStatus} ${styles[agent.status]}`}>
          {agent.status}
        </span>
      </div>

      <div className={styles.agentMetrics}>
        <div className={styles.metricItem}>
          <span className={styles.metricLabel}>Total Events</span>
          <span className={styles.metricValue}>
            {agent.summary_stats.total_events}
          </span>
        </div>
        
        <div className={styles.metricItem}>
          <span className={styles.metricLabel}>Last 24h</span>
          <span className={styles.metricValue}>
            {agent.summary_stats.recent_events_24h}
          </span>
        </div>
        
        {agent.summary_stats.avg_confidence !== undefined && (
          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Confidence</span>
            <span 
              className={styles.metricValue}
              style={{ 
                color: agent.summary_stats.avg_confidence > 0.8 
                  ? 'var(--success)' 
                  : agent.summary_stats.avg_confidence > 0.5 
                    ? 'var(--warning)' 
                    : 'var(--error)' 
              }}
            >
              {(agent.summary_stats.avg_confidence * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {agent.last_activity && (
        <div className={styles.lastActivity}>
          Last activity: {formatTimestamp(agent.last_activity)}
        </div>
      )}
    </div>
  );
};
