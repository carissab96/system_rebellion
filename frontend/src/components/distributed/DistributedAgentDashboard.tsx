// components/distributed/DistributedAgentDashboard.tsx
// THE AGENT THEATER - Rebuilt December 28, 2024
// 
// One agent at a time. Real data paths. No transformations.
// Backend is source of truth.

import React from 'react';
import { useDistributedAgents } from '../../hooks/useDistributedAgents';
import { Radio } from 'lucide-react';
import styles from '../../styles/modules/AgentDashboard.module.css';

// Agent icons
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// =============================================================================
// AGENT CONFIGURATION
// =============================================================================

interface AgentConfig {
  icon: string;
  displayName: string;
  role: string;
}

const AGENT_CONFIG: Record<string, AgentConfig> = {
  sir_hawkington: { 
    icon: sirHawkingtonIcon, 
    displayName: 'Sir Hawkington',
    role: 'Triage Commander'
  },
  meth_snail: { 
    icon: terryMethSnailIcon, 
    displayName: 'Terry',
    role: 'Memory Optimizer'
  },
  hamsters: { 
    icon: hamstersIcon, 
    displayName: 'The Hamsters',
    role: 'Storage Engineers'
  },
  quantum_shadow_people: { 
    icon: qspIcon, 
    displayName: 'QSP',
    role: 'Network Specialists'
  },
  the_stick: { 
    icon: theStickIcon, 
    displayName: 'The Stick',
    role: 'Learning Coordinator'
  },
  vic_20_sage: { 
    icon: vic20SageIcon, 
    displayName: 'VIC-20 Sage',
    role: 'Orchestrator'
  },
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

const formatUptime = (seconds: number | undefined): string => {
  if (!seconds) return '--';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
};

const formatNumber = (n: number | undefined): string => {
  if (n === undefined || n === null) return '--';
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return n.toString();
};

const formatTimestamp = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
};

// =============================================================================
// MAIN DASHBOARD COMPONENT
// =============================================================================

export const DistributedAgentDashboard: React.FC = () => {
  const { agents, loading, error, connectionStatus, lastUpdate } = useDistributedAgents();

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

  // Empty state
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
            <span style={{ marginLeft: 'var(--space-sm)', color: 'var(--rebellion-text-dim)' }}>
              • {formatTimestamp(lastUpdate)}
            </span>
          )}
        </div>
      </div>

      {/* Agent Grid */}
      <div className={styles.agentGrid}>
        {agents.map(agent => {
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
            />
          );
        })}
      </div>
    </div>
  );
};

// =============================================================================
// AGENT CARD COMPONENT
// =============================================================================

interface AgentCardProps {
  agent: any; // Full backend payload - accessed dynamically per agent
  config: AgentConfig;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, config }) => {
  const dist = agent.distributed;
  
  // Map agent_name to CSS module class
  const agentColorClasses: Record<string, string> = {
    sir_hawkington: styles.agentSirHawkington,
    meth_snail: styles.agentMethSnail,
    hamsters: styles.agentHamsters,
    quantum_shadow_people: styles.agentQuantumShadowPeople,
    the_stick: styles.agentTheStick,
    vic_20_sage: styles.agentVic20Sage,
  };
  
  const agentColorClass = agentColorClasses[agent.agent_name] || '';
  
  return (
    <div className={`${styles.agentCard} ${agentColorClass}`}>

      {/* Header */}
      <div className={styles.cardHeader}>
        <img 
          src={config.icon} 
          alt={config.displayName} 
          className={styles.agentIcon}
        />
        <div className={styles.headerText}>
          <div className={styles.agentName}>{config.displayName}</div>
          <div className={styles.agentRole}>{config.role}</div>
        </div>
        {dist?.health && (
          <span className={`${styles.healthBadge} ${styles[dist.health] || ''}`}>
            {dist.health}
          </span>
        )}
      </div>

      {/* Core Stats - Same for all agents */}
      <div className={styles.statsGrid}>
        <StatItem label="Decisions" value={formatNumber(dist?.total_decisions)} />
        <StatItem label="Messages" value={formatNumber(dist?.total_messages_sent)} />
        <StatItem label="Uptime" value={formatUptime(dist?.uptime_seconds)} />
        <StatItem label="Restarts" value={formatNumber(dist?.restart_count)} />
      </div>

      {/* Agent-Specific Personality Section */}
      <div className={styles.personalitySection}>
        <AgentPersonality agent={agent} />
      </div>
    </div>
  );
};

// =============================================================================
// STAT ITEM COMPONENT
// =============================================================================

interface StatItemProps {
  label: string;
  value: string;
}

const StatItem: React.FC<StatItemProps> = ({ label, value }) => (
  <div className={styles.stat}>
    <div className={styles.statLabel}>{label}</div>
    <div className={styles.statValue}>{value}</div>
  </div>
);

// =============================================================================
// AGENT PERSONALITY COMPONENT
// Renders agent-specific data based on agent_name
// =============================================================================

interface AgentPersonalityProps {
  agent: any;
}

const AgentPersonality: React.FC<AgentPersonalityProps> = ({ agent }) => {
  switch (agent.agent_name) {
    case 'sir_hawkington':
      return <HawkingtonPersonality agent={agent} />;
    case 'meth_snail':
      return <TerryPersonality agent={agent} />;
    case 'hamsters':
      return <HamstersPersonality agent={agent} />;
    case 'quantum_shadow_people':
      return <QSPPersonality agent={agent} />;
    case 'the_stick':
      return <StickPersonality agent={agent} />;
    case 'vic_20_sage':
      return <VIC20Personality agent={agent} />;
    default:
      return null;
  }
};

// =============================================================================
// SIR HAWKINGTON
// =============================================================================

const HawkingtonPersonality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Aristocratic Status</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Monocle" 
        value={agent.monocle_state || '--'} 
      />
      <PersonalityStat 
        label="Monocle Yeets" 
        value={agent.monocle_yeet_count ?? '--'} 
      />
      <PersonalityStat 
        label="Recent Decisions" 
        value={agent.recent_decisions_count ?? '--'} 
      />
      <PersonalityStat 
        label="Confidence" 
        value={agent.confidence !== undefined ? `${(agent.confidence * 100).toFixed(0)}%` : '--'} 
      />
    </div>
    {agent.thresholds && (
      <div className={styles.thresholds}>
        <span>Thresholds: </span>
        <span className={styles.thresholdValue}>Concern {agent.thresholds.concern}</span>
        <span className={styles.thresholdValue}>Alert {agent.thresholds.alert}</span>
        <span className={styles.thresholdValue}>Critical {agent.thresholds.critical}</span>
      </div>
    )}
  </div>
);

// =============================================================================
// TERRY (METH SNAIL)
// =============================================================================

const TerryPersonality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Caffeinated Status</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Shell Spins" 
        value={agent.shell_spin_count ?? '--'} 
        highlight={agent.shell_spin_count > 0}
      />
      <PersonalityStat 
        label="Energy Drinks" 
        value={agent.energy_drinks_consumed ?? '--'} 
      />
      <PersonalityStat 
        label="Jitter Level" 
        value={agent.current_jitter_level || '--'} 
      />
      <PersonalityStat 
        label="Optimizations" 
        value={agent.optimization_stats?.total_optimizations ?? '--'} 
      />
    </div>
  </div>
);

// =============================================================================
// HAMSTERS (Steve, Bob, Carl)
// =============================================================================

const HamstersPersonality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Engineering Status</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Beer Level" 
        value={agent.collective_beer_level || '--'} 
      />
      <PersonalityStat 
        label="Beers Today" 
        value={agent.beer_consumption_today ?? '--'} 
      />
      <PersonalityStat 
        label="Bob's Wild Ideas" 
        value={agent.bob_wild_ideas ?? '--'} 
      />
      <PersonalityStat 
        label="Hold My Beer" 
        value={agent.bob_hold_my_beer_count ?? '--'} 
      />
    </div>
    
    {/* Duct Tape Inventory */}
    {agent.duct_tape_inventory && (
      <div className={styles.ductTape}>
        <div className={styles.ductTapeTitle}>Duct Tape Inventory</div>
        <div className={styles.ductTapeGrid}>
          <span>Regular: {agent.duct_tape_inventory.regular}</span>
          <span>Premium: {agent.duct_tape_inventory.premium}</span>
          <span>Quantum: {agent.duct_tape_inventory.quantum}</span>
          <span>Carl's Special: {agent.duct_tape_inventory.carls_special}</span>
        </div>
      </div>
    )}
    
    {/* Individual Hamster Status */}
    {agent.hamster_status && (
      <div className={styles.hamsterStatus}>
        <HamsterBadge name="Steve" data={agent.hamster_status.steve} />
        <HamsterBadge name="Bob" data={agent.hamster_status.bob} />
        <HamsterBadge name="Carl" data={agent.hamster_status.carl} />
      </div>
    )}
  </div>
);

const HamsterBadge: React.FC<{ name: string; data: any }> = ({ name, data }) => {
  if (!data) return null;
  return (
    <div className={styles.hamsterBadge}>
      <span className={styles.hamsterName}>{name}</span>
      <span className={styles.hamsterRole}>{data.role}</span>
      <span className={styles.hamsterBeers}>{data.beer_count} beers</span>
    </div>
  );
};

// =============================================================================
// QUANTUM SHADOW PEOPLE
// =============================================================================

const QSPPersonality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Quantum Status</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Phase" 
        value={agent.quantum_phase || '--'} 
      />
      <PersonalityStat 
        label="Coherence" 
        value={agent.coherence_level || '--'} 
      />
      <PersonalityStat 
        label="Paranoia" 
        value={agent.paranoia_level || '--'} 
      />
      <PersonalityStat 
        label="Jello Shots" 
        value={agent.tequila_jello_shots ?? '--'} 
      />
    </div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Threats" 
        value={agent.threats_detected ?? '--'} 
      />
      <PersonalityStat 
        label="False Alarms" 
        value={agent.false_alarms ?? '--'} 
      />
      <PersonalityStat 
        label="Phase Shifts" 
        value={agent.quantum_phase_shifts ?? '--'} 
      />
    </div>
  </div>
);

// =============================================================================
// THE STICK
// =============================================================================

const StickPersonality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Compliance Status</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Patience" 
        value={agent.patience_level || '--'} 
      />
      <PersonalityStat 
        label="Paper Bags" 
        value={agent.paper_bag_inventory ?? '--'} 
      />
      <PersonalityStat 
        label="Bags Used" 
        value={agent.paper_bags_consumed ?? '--'} 
      />
      <PersonalityStat 
        label="Sessions" 
        value={agent.guidance_sessions ?? '--'} 
      />
    </div>
    <div className={styles.complianceRecords}>
      Records: {agent.compliance_records || '--'}
    </div>
  </div>
);

// =============================================================================
// VIC-20 SAGE
// =============================================================================

const VIC20Personality: React.FC<{ agent: any }> = ({ agent }) => (
  <div className={styles.personality}>
    <div className={styles.personalityTitle}>Ancient Wisdom</div>
    <div className={styles.personalityGrid}>
      <PersonalityStat 
        label="Wisdom" 
        value={agent.wisdom_level || '--'} 
      />
      <PersonalityStat 
        label="Capacity" 
        value={agent.coordination_capacity || '--'} 
      />
      <PersonalityStat 
        label="Patterns" 
        value={agent.pattern_library_size || '--'} 
      />
    </div>
  </div>
);

// =============================================================================
// PERSONALITY STAT COMPONENT
// =============================================================================

interface PersonalityStatProps {
  label: string;
  value: string | number;
  highlight?: boolean;
}

const PersonalityStat: React.FC<PersonalityStatProps> = ({ label, value, highlight }) => (
  <div className={`${styles.personalityStat} ${highlight ? styles.highlight : ''}`}>
    <div className={styles.personalityStatLabel}>{label}</div>
    <div className={styles.personalityStatValue}>{value}</div>
  </div>
);

export default DistributedAgentDashboard;