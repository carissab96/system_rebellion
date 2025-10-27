// components/agent-theater/LiveAgentCard.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MetricsChart } from './MetricsChart';
import { AgentIntelligenceOverlay } from './AgentItelligenceOverlay';
import type { AgentDecision } from './AgentItelligenceOverlay';
import styles from './LiveAgentCard.module.css';

interface AgentPersonality {
  id: string;
  name: string;
  role: string;
  description: string;
  color: string;
  personality: string;
  responsibility: string;
  quirks: string;
  memory: string;
  interactions: string;
}

interface AgentData {
  status?: string;
  memory_id?: string;
  timestamp?: string;
  [key: string]: any; // Memory bank fields vary by agent
  intelligence?: {
    decision?: AgentDecision | null;
  };
}

interface LiveAgentCardProps {
  personality: AgentPersonality;
  data: AgentData | null;
  isActive: boolean;
  activityPulse: boolean;
  onCardClick?: () => void;
}

export const LiveAgentCard: React.FC<LiveAgentCardProps> = ({
  personality,
  data,
  isActive,
  activityPulse,
  onCardClick
}) => {
  const [expanded, setExpanded] = useState(false);

  // Extract key metrics based on agent type and their domain
  const getAgentMetrics = () => {
    if (!data) return null;

    switch (personality.id) {
      case 'sir_hawkington':
        // CPU + Quality Control + Triage
        const monocleYeets = data.monocle_yeets_count || data.monocle_yeet_count || 0;
        const triageCount = data.triage_decisions_count || data.triage_decision_count || 0;
        const confidence = data.confidence || data.avg_confidence || 0;
        
        return {
          'CPU Usage': data.cpu_usage || 0,
          'Monocle Yeets': monocleYeets,
          'Triage Decisions': triageCount,
          'Confidence': Math.round(confidence * 100)
        };
        
      case 'the_stick':
        // HYPERVIGILANT - monitors EVERYTHING with anxiety
        return {
          'Anxiety Level': data.anxiety_level || 'CALM',
          'Paper Bags': data.paper_bags_remaining || data.paper_bags_consumed || 100,
          'Hamster Proximity': data.hamster_proximity ? 'DETECTED!' : 'Safe',
          'Patterns Logged': data.patterns_detected || 0
        };
        
      case 'hamsters':
        // Infrastructure: Disk, I/O, processes
        return {
          'Disk Usage': data.disk_usage || 0,
          'Steve': data.steve_status || 'Idle',
          'Bob': data.bob_status || 'Idle',
          'Carl': data.carl_status || 'Idle',
          'Beer Level': data.beer_level || 0
        };
        
      case 'meth_snail':
        // RAM/Memory optimization
        return {
          'Memory Usage': data.memory_usage || 0,
          'Shell Spin Rate': data.shell_spin_rate || 0,
          'Optimizations': data.optimizations_count || 0,
          'Energy Drinks': data.energy_drinks_consumed || 0
        };
        
      case 'quantum_shadow_people':
        // Network specialists - FULL network analysis
        const sentRate = data.network_sent_rate || 0;
        const recvRate = data.network_recv_rate || 0;
        const connStats = data.connection_stats || {};
        const protoStats = data.protocol_stats || {};
        
        return {
          'Sent (KB/s)': Math.round(sentRate / 1024),
          'Recv (KB/s)': Math.round(recvRate / 1024),
          'Total Connections': data.connection_count || 0,
          'Established': connStats.ESTABLISHED || 0,
          'TCP': (protoStats.tcp || 0) + (protoStats.tcp6 || 0),
          'UDP': (protoStats.udp || 0) + (protoStats.udp6 || 0)
        };
        
      case 'vic20_sage':
        // Mediator, historian, auto-tuner
        return {
          'Wisdom Dispensed': data.wisdom_count || 0,
          'Conflicts Mediated': data.conflicts_mediated || 0,
          'Patterns (40yr)': data.patterns_recognized || 0,
          'Auto-tune Suggestions': data.autotuning_suggestions || 0
        };
        
      default:
        return null;
    }
  };

  const metrics = getAgentMetrics();
  // Agent is active if it has data OR if it's monitoring its domain (always show as active)
  const hasData = data && (data.status === 'active' || metrics !== null);

  return (
    <motion.div
      className={`${styles.agentCard} ${isActive ? styles.active : ''} ${expanded ? styles.expanded : ''}`}
      onClick={() => {
        setExpanded(!expanded);
        onCardClick?.();
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{
        opacity: 1,
        y: 0,
        scale: isActive ? 1.05 : 1,
        z: isActive ? 10 : 0
      }}
      transition={{ duration: 0.3 }}
      style={{
        '--agent-color': personality.color,
        borderColor: isActive ? personality.color : 'var(--rebellion-border)'
      } as React.CSSProperties}
    >
      {/* Activity Pulse Indicator */}
      {activityPulse && (
        <motion.div
          className={styles.activityPulse}
          initial={{ scale: 1, opacity: 1 }}
          animate={{ scale: 2, opacity: 0 }}
          transition={{ duration: 1 }}
          style={{ backgroundColor: personality.color }}
        />
      )}

      {/* Agent Header */}
      <div className={styles.agentHeader}>
        <div className={styles.agentIdentity}>
          <div 
            className={styles.agentAvatar}
            style={{ 
              backgroundColor: `${personality.color}20`,
              borderColor: personality.color 
            }}
          >
            <span className={styles.agentInitial}>
              {personality.name.charAt(0)}
            </span>
          </div>
          <div className={styles.agentInfo}>
            <h3 className={styles.agentName}>{personality.name}</h3>
            <p className={styles.agentRole}>{personality.role}</p>
          </div>
        </div>
        
        {/* Status Indicator */}
        <div className={styles.statusIndicator}>
          <div 
            className={`${styles.statusDot} ${hasData ? styles.statusActive : styles.statusIdle}`}
            style={{ backgroundColor: hasData ? personality.color : 'var(--rebellion-text-dim)' }}
          />
          <span className={styles.statusText}>
            {hasData ? 'Active' : 'Idle'}
          </span>
        </div>
      </div>

      {/* Agent Description */}
      <p className={styles.agentDescription}>{personality.description}</p>

      {/* Personality Quirk */}
      <div className={styles.quirkBadge}>
        <span className={styles.quirkLabel}>Quirk:</span>
        <span className={styles.quirkText}>{personality.quirks}</span>
      </div>

      {/* Metrics Visualization - Only show chart for numeric metrics */}
      {metrics && hasData && (
        <>
          <MetricsChart metrics={metrics} color={personality.color} />
        </>
      )}

      {/* Agent Intelligence Overlay */}
      {data?.intelligence?.decision && (
        <div className={styles.intelligenceSection}>
          <AgentIntelligenceOverlay
            agentId={personality.id}
            decision={data.intelligence.decision}
            isVisible={expanded || isActive}
          />
        </div>
      )}

      {/* Expanded Details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            className={styles.expandedDetails}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className={styles.detailSection}>
              <h4 className={styles.detailTitle}>Personality</h4>
              <p className={styles.detailText}>{personality.personality}</p>
            </div>
            <div className={styles.detailSection}>
              <h4 className={styles.detailTitle}>Responsibility</h4>
              <p className={styles.detailText}>{personality.responsibility}</p>
            </div>
            <div className={styles.detailSection}>
              <h4 className={styles.detailTitle}>Memory</h4>
              <p className={styles.detailText}>{personality.memory}</p>
            </div>
            <div className={styles.detailSection}>
              <h4 className={styles.detailTitle}>Interactions</h4>
              <p className={styles.detailText}>{personality.interactions}</p>
            </div>
            {data && data.timestamp && (
              <div className={styles.detailSection}>
                <h4 className={styles.detailTitle}>Last Update</h4>
                <p className={styles.detailText}>
                  {new Date(data.timestamp).toLocaleString()}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Interaction Hint */}
      <div className={styles.cardFooter}>
        <span className={styles.interactionHint}>
          {expanded ? 'Click to collapse' : 'Click to expand details'}
        </span>
      </div>
    </motion.div>
  );
};
