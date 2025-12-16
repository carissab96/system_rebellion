// components/distributed/DistributedAgentDashboard.tsx
// THE AGENT THEATER - Watch distributed agents work in real-time
// Data flows: WebSocket → Redux → useDistributedAgents → this component
//
// Design: Uses rebellion design system + CSS modules (no inline styles except design tokens)

import React, { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { useDistributedAgents, type DistributedAgent } from '../../hooks/useDistributedAgents';
import { selectRecentCommunications, MESSAGE_TYPE_COLORS } from '../../store/slices/communicationSlice';
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
  quantum_shadow_people: { icon: qspIcon, displayName: 'QSP', styleClass: 'quantumShadowPeople' },
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
  const recentCommunications = useSelector(selectRecentCommunications);
  const [activityLog, setActivityLog] = useState<ActivityLog[]>([]);

  // Convert real-time communications to activity log format
  useEffect(() => {
    if (recentCommunications.length === 0) return;
    
    // Take last 20 communications and convert to activity log
    const newActivities: ActivityLog[] = recentCommunications.slice(0, 20).map(comm => {
      const color = MESSAGE_TYPE_COLORS[comm.message_type] || MESSAGE_TYPE_COLORS.default;
      
      // Extract readable action text from summary
      let action = '';
      if (typeof comm.summary === 'string') {
        action = comm.summary;
      } else if (comm.summary && typeof comm.summary === 'object') {
        // If summary is an object, try to extract meaningful text
        const summaryObj = comm.summary as any;
        action = summaryObj.message || summaryObj.action || summaryObj.content || JSON.stringify(comm.summary);
      } else {
        action = `${comm.message_type} → ${comm.to_agent}`;
      }
      
      // Truncate long messages
      if (action.length > 100) {
        action = action.substring(0, 97) + '...';
      }
      
      return {
        id: comm.id,
        agent: comm.from_agent,
        action,
        timestamp: new Date(comm.timestamp),
        color,
      };
    });
    
    setActivityLog(newActivities);
  }, [recentCommunications]);

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

      {/* Agent-Specific Personality Stats */}
      <AgentPersonalityStats agent={agent} />
    </div>
  );
};

// =============================================================================
// AGENT PERSONALITY STATS COMPONENT
// =============================================================================

interface AgentPersonalityStatsProps {
  agent: DistributedAgent;
}

const AgentPersonalityStats: React.FC<AgentPersonalityStatsProps> = ({ agent }) => {
  const renderStats = () => {
    switch (agent.agent_name) {
      case 'sir_hawkington':
        return (
          <>
            {agent.monocle_yeet_count !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Monocle Yeets:</span>
                <span className={styles.personalityValue}>{agent.monocle_yeet_count}</span>
              </div>
            )}
            {agent.monocle_state && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Monocle State:</span>
                <span className={styles.personalityValue}>{agent.monocle_state}</span>
              </div>
            )}
          </>
        );

      case 'meth_snail':
        return (
          <>
            {agent.shell_spin_count !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Shell Spins:</span>
                <span className={styles.personalityValue}>{agent.shell_spin_count}</span>
              </div>
            )}
            {agent.energy_drinks_consumed !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Energy Drinks:</span>
                <span className={styles.personalityValue}>{agent.energy_drinks_consumed}</span>
              </div>
            )}
            {agent.current_jitter_level && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Jitter Level:</span>
                <span className={styles.personalityValue}>{agent.current_jitter_level}</span>
              </div>
            )}
          </>
        );

      case 'hamsters':
        return (
          <>
            {agent.bob_wild_ideas !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Bob's Wild Ideas:</span>
                <span className={styles.personalityValue}>{agent.bob_wild_ideas}</span>
              </div>
            )}
            {agent.bob_hold_my_beer_count !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Hold My Beer:</span>
                <span className={styles.personalityValue}>{agent.bob_hold_my_beer_count}</span>
              </div>
            )}
            {agent.collective_beer_level && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Beer Level:</span>
                <span className={styles.personalityValue}>{agent.collective_beer_level}</span>
              </div>
            )}
            {agent.duct_tape_inventory && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Duct Tape:</span>
                <span className={styles.personalityValue}>
                  {typeof agent.duct_tape_inventory === 'object' 
                    ? Object.values(agent.duct_tape_inventory).reduce((a: any, b: any) => (a || 0) + (b || 0), 0)
                    : agent.duct_tape_inventory}
                </span>
              </div>
            )}
          </>
        );

      case 'the_stick':
        return (
          <>
            {agent.paper_bag_inventory !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Paper Bags Left:</span>
                <span className={styles.personalityValue}>{agent.paper_bag_inventory}</span>
              </div>
            )}
            {agent.paper_bags_consumed !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Bags Consumed:</span>
                <span className={styles.personalityValue}>{agent.paper_bags_consumed}</span>
              </div>
            )}
          </>
        );

      case 'quantum_shadow_people':
        return (
          <>
            {agent.tequila_jello_shots !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Tequila Shots:</span>
                <span className={styles.personalityValue}>{agent.tequila_jello_shots}</span>
              </div>
            )}
            {agent.paranoia_level && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Paranoia:</span>
                <span className={styles.personalityValue}>{agent.paranoia_level}</span>
              </div>
            )}
            {agent.threats_detected !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Threats Found:</span>
                <span className={styles.personalityValue}>{agent.threats_detected}</span>
              </div>
            )}
            {agent.false_alarms !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>False Alarms:</span>
                <span className={styles.personalityValue}>{agent.false_alarms}</span>
              </div>
            )}
          </>
        );

      case 'vic_20_sage':
        return (
          <>
            {agent.totalAnalyses !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Analyses:</span>
                <span className={styles.personalityValue}>{agent.totalAnalyses}</span>
              </div>
            )}
            {agent.decisionsMade !== undefined && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Decisions:</span>
                <span className={styles.personalityValue}>{agent.decisionsMade}</span>
              </div>
            )}
            {agent.wisdomLevel && (
              <div className={styles.personalityStat}>
                <span className={styles.personalityLabel}>Wisdom:</span>
                <span className={styles.personalityValue}>{agent.wisdomLevel}</span>
              </div>
            )}
          </>
        );

      default:
        return null;
    }
  };

  const stats = renderStats();
  if (!stats) return null;

  return (
    <div className={styles.personalitySection}>
      <div className={styles.personalityTitle}>Personality Stats</div>
      {stats}
    </div>
  );
};
