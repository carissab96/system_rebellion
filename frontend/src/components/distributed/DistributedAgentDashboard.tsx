// components/distributed/DistributedAgentDashboard.tsx
// THE AGENT THEATER - Watch distributed agents work in real-time
// Data flows: WebSocket → Redux → useDistributedAgents → this component
//
// Design: Uses rebellion design system + CSS modules (no inline styles except design tokens)

import React, { useState, useEffect, useRef } from 'react';
import { useDistributedAgents, type DistributedAgent } from '../../hooks/useDistributedAgents';
import { Radio, Activity, AlertTriangle } from 'lucide-react';
import styles from '../../styles/modules/AgentDashboard.module.css';

// Agent icons
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// Agent display configuration - maps backend agent_name to display info
// NO EMOJIS - use icons from assets
const AGENT_CONFIG: Record<string, { icon: string; displayName: string; styleClass: string }> = {
  sir_hawkington: { icon: sirHawkingtonIcon, displayName: 'Sir Hawkington', styleClass: 'sirHawkington' },
  vic_20_sage: { icon: vic20SageIcon, displayName: 'VIC-20 Sage', styleClass: 'vic20Sage' },
  meth_snail: { icon: terryMethSnailIcon, displayName: 'Terry', styleClass: 'methSnail' },
  the_stick: { icon: theStickIcon, displayName: 'The Stick', styleClass: 'theStick' },
  hamsters: { icon: hamstersIcon, displayName: 'The Hamsters', styleClass: 'hamsters' },
  quantum_shadow_people: { icon: qspIcon, displavasobrassilarj     mmmmmmmyName: 'QSP', styleClass: 'quantumShadowPeople' },
};

interface ActivityLog {
  id: string;
  agent: string;
  action: string;
  timestamp: Date;
  color: string;
}

export const DistributedAgentDashboard: React.FC = () => {
  const { agents, loading, error, connectionStatus, lastUpdate } = useDistributedAgents();
  const [activityLog, setActivityLog] = useState<ActivityLog[]>([]);
  const prevAgentStatesRef = useRef<Map<string, any>>(new Map());

  // Watch for agent activity changes and log them
  useEffect(() => {
    const prevStates = prevAgentStatesRef.current;
    
    agents.forEach(agent => {
      const prev = prevStates.get(agent.agent_name);
      const dist = agent.distributed;
      
      if (!prev) {
        // First time seeing this agent
        addActivity(agent.agent_name, 'Agent online');
        return;
      }

      // Detect new messages sent
      const currentMsgCount = dist?.total_messages_sent;
      const prevMsgCount = prev.messages_sent;
      if (currentMsgCount !== undefined && prevMsgCount !== undefined && currentMsgCount > prevMsgCount) {
        const count = currentMsgCount - prevMsgCount;
        addActivity(agent.agent_name, `Broadcast ${count} message${count > 1 ? 's' : ''}`);
      }

      // Detect new decisions
      const currentDecisions = agent.total_decisions;
      const prevDecisions = prev.decisions;
      if (currentDecisions !== undefined && prevDecisions !== undefined && currentDecisions > prevDecisions) {
        const count = currentDecisions - prevDecisions;
        addActivity(agent.agent_name, `Made ${count} decision${count > 1 ? 's' : ''}`);
      }

      // Detect health changes
      if (agent.health && prev.health && agent.health !== prev.health) {
        addActivity(agent.agent_name, `Health: ${prev.health} -> ${agent.health}`);
      }
      
      // Detect triage events (Sir Hawkington)
      if (agent.triage?.disposition && agent.triage.disposition !== prev.triageDisposition) {
        addActivity(agent.agent_name, `Triage: ${agent.triage.disposition}`);
      }
    });

    // Update previous states
    const newStates = new Map();
    agents.forEach(agent => {
      newStates.set(agent.agent_name, {
        messages_sent: agent.distributed?.total_messages_sent,
        decisions: agent.total_decisions,
        health: agent.health,
        triageDisposition: agent.triage?.disposition,
      });
    });
    prevAgentStatesRef.current = newStates;
  }, [agents]);

  const addActivity = (agentName: string, action: string) => {
    const newActivity: ActivityLog = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      agent: agentName,
      action,
      timestamp: new Date(),
      color: getAgentColor(agentName),
    };
    setActivityLog(prev => [newActivity, ...prev].slice(0, 50));
  };

  const getAgentColor = (agentName: string): string => {
    const colors: Record<string, string> = {
      sir_hawkington: 'var(--hawkington-gold)',
      vic_20_sage: 'var(--vic20-cyan)',
      meth_snail: 'var(--snail-electric)',
      the_stick: 'var(--stick-coral)',
      hamsters: 'var(--hamster-amber)',
      quantum_shadow_people: 'var(--qsp-violet)',
    };
    return colors[agentName] || 'var(--rebellion-text)';
  };

  const formatUptime = (seconds: number): string => {
    if (!seconds) return '0s';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      hour12: false 
    });
  };

  // Loading state
  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner} />
        <span>Raising the curtain...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={styles.emptyState}>
        <h3 style={{ color: 'var(--error)', marginBottom: 'var(--space-sm)' }}>
          Connection Error
        </h3>
        <p>{error}</p>
      </div>
    );
  }

  // Empty state - no fake messaging, just facts
  if (agents.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h3>No agents reporting</h3>
        <p>Waiting for agent data from WebSocket.</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>
          <Radio style={{ width: 24, height: 24, color: 'var(--vic20-cyan)' }} />
          Agent Theater
        </h2>
        <div className={styles.connectionStatus}>
          <span 
            className={`${styles.statusDot} ${
              connectionStatus === 'connected' ? styles.connected :
              connectionStatus === 'connecting' ? styles.connecting :
              styles.error
            }`} 
          />
          <span>{connectionStatus}</span>
          {lastUpdate && (
            <span style={{ marginLeft: 'var(--space-sm)' }}>
              • Last update: {formatTimestamp(lastUpdate)}
            </span>
          )}
        </div>
      </div>

      {/* Agent Grid */}
      <div className={styles.agentGrid}>
        {agents.map(agent => {
          // Only show agents we have config for - no fallbacks
          const config = AGENT_CONFIG[agent.agent_name];
          if (!config) {
            console.warn(`Unknown agent: ${agent.agent_name}`);
            return null;
          }
          
          return (
            <AgentCard 
              key={agent.agent_name} 
              agent={agent} 
              config={config}
              formatUptime={formatUptime}
            />
          );
        })}
      </div>

      {/* Activity Feed */}
      <div className={styles.activityFeed}>
        <h3 className={styles.feedTitle}>
          <Activity style={{ width: 20, height: 20, color: 'var(--snail-electric)' }} />
          Live Activity Feed
        </h3>
        
        {activityLog.length === 0 ? (
          <div style={{ color: 'var(--rebellion-text-dim)', textAlign: 'center', padding: 'var(--space-lg)' }}>
            No activity yet
          </div>
        ) : (
          activityLog.map(log => {
            const config = AGENT_CONFIG[log.agent];
            return (
              <div key={log.id} className={styles.feedItem}>
                <span className={styles.feedDot} style={{ backgroundColor: log.color }} />
                <div className={styles.feedContent}>
                  <span className={styles.feedAgent} style={{ color: log.color }}>
                    {config?.displayName || log.agent}
                  </span>
                  <div className={styles.feedAction}>{log.action}</div>
                  <div className={styles.feedTimestamp}>{formatTimestamp(log.timestamp)}</div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

// =============================================================================
// AGENT CARD COMPONENT
// =============================================================================

interface AgentCardProps {
  agent: DistributedAgent;
  config: { icon: string; displayName: string; styleClass: string };
  formatUptime: (seconds: number) => string;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, config, formatUptime }) => {
  const dist = agent.distributed;
  
  // Determine health badge style - no fallback, show actual state
  const getHealthClass = (health: string | undefined): string => {
    switch (health?.toLowerCase()) {
      case 'healthy': return styles.healthy;
      case 'degraded': return styles.degraded;
      case 'unhealthy':
      case 'critical': return styles.unhealthy;
      default: return '';
    }
  };

  return (
    <div className={`${styles.agentCard} ${styles[config.styleClass] || ''}`}>
      {/* Card Header */}
      <div className={styles.cardHeader}>
        <div className={styles.agentName}>
          <img 
            src={config.icon} 
            alt={config.displayName} 
            className={styles.agentIcon}
          />
          {config.displayName}
        </div>
        {agent.health && (
          <span className={`${styles.healthBadge} ${getHealthClass(agent.health)}`}>
            {agent.health}
          </span>
        )}
      </div>

      {/* Stats Grid - show real data only, no zeros as fallback */}
      <div className={styles.statsGrid}>
        {agent.total_decisions !== undefined && (
          <div className={styles.stat}>
            <div className={styles.statLabel}>Decisions</div>
            <div className={styles.statValue}>{agent.total_decisions}</div>
          </div>
        )}
        {agent.uptime_seconds !== undefined && (
          <div className={styles.stat}>
            <div className={styles.statLabel}>Uptime</div>
            <div className={styles.statValue}>{formatUptime(agent.uptime_seconds)}</div>
          </div>
        )}
        {dist?.total_messages_sent !== undefined && (
          <div className={styles.stat}>
            <div className={styles.statLabel}>Msgs Sent</div>
            <div className={styles.statValue}>{dist.total_messages_sent}</div>
          </div>
        )}
        {dist?.total_messages_received !== undefined && (
          <div className={styles.stat}>
            <div className={styles.statLabel}>Msgs Recv</div>
            <div className={styles.statValue}>{dist.total_messages_received}</div>
          </div>
        )}
      </div>

      {/* Latest Event - only if real data exists */}
      {agent.event_type && (
        <div className={styles.recentActivity}>
          <div className={styles.activityTitle}>Latest Event</div>
          <div className={styles.activityItem}>
            <span className={styles.activityType}>{agent.event_type}</span>
          </div>
        </div>
      )}

      {/* Triage Section (Sir Hawkington only) - only show real data */}
      {agent.triage?.disposition && agent.agent_name === 'sir_hawkington' && (
        <div className={styles.triageSection}>
          <div className={styles.triageTitle}>
            <AlertTriangle style={{ width: 14, height: 14 }} />
            Triage Status
          </div>
          <div className={styles.triageDisposition}>
            {agent.triage.disposition}
          </div>
          {agent.triage.confidence !== undefined && (
            <div className={styles.triageConfidence}>
              Confidence: {(agent.triage.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )}
    </div>
  );
};
