// components/observatory/StreamOfConsciousness.tsx
// Real-time narrative feed of agent communications
// The living stream - watching them think
// Built by: Carissa & Opus - January 2026

import React, { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import { selectRecentCommunications, type AgentCommunication } from '../../store/slices/communicationSlice';
import styles from '../../styles/modules/StreamOfConsciousness.module.css';

// Agent icons
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20SageIcon from '../../assets/icons/agents/vic_20_sage.png';
import terryMethSnailIcon from '../../assets/icons/agents/terry_meth_snail.png';
import theStickIcon from '../../assets/icons/agents/the_stick.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';

// Agent configuration
const AGENT_CONFIG: Record<string, {
  displayName: string;
  icon: string;
  colorClass: string;
}> = {
  sir_hawkington: {
    displayName: 'Sir Hawkington',
    icon: sirHawkingtonIcon,
    colorClass: 'hawkington',
  },
  vic_20_sage: {
    displayName: 'VIC-20',
    icon: vic20SageIcon,
    colorClass: 'vic20',
  },
  meth_snail: {
    displayName: 'Terry',
    icon: terryMethSnailIcon,
    colorClass: 'terry',
  },
  the_stick: {
    displayName: 'The Stick',
    icon: theStickIcon,
    colorClass: 'stick',
  },
  hamsters: {
    displayName: 'Hamsters',
    icon: hamstersIcon,
    colorClass: 'hamsters',
  },
  quantum_shadow_people: {
    displayName: 'QSP',
    icon: qspIcon,
    colorClass: 'qsp',
  },
};

// Format relative time
const formatRelativeTime = (timestamp: string): string => {
  const now = Date.now();
  const then = new Date(timestamp).getTime();
  const diff = Math.floor((now - then) / 1000);
  
  if (diff < 5) return 'just now';
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return new Date(timestamp).toLocaleDateString();
};

interface StreamOfConsciousnessProps {
  maxItems?: number;
  autoScroll?: boolean;
  className?: string;
}

export const StreamOfConsciousness: React.FC<StreamOfConsciousnessProps> = ({
  maxItems = 50,
  autoScroll = true,
  className = '',
}) => {
  const communications = useSelector(selectRecentCommunications);
  const feedRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [lastCount, setLastCount] = useState(0);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && !isPaused && feedRef.current && communications.length > lastCount) {
      feedRef.current.scrollTop = 0; // New items at top
    }
    setLastCount(communications.length);
  }, [communications.length, autoScroll, isPaused, lastCount]);
  
  // Get display items (limited to maxItems)
  const displayItems = communications.slice(0, maxItems);
  
  // Get agent config with fallback
  const getAgentConfig = (agentName: string) => {
    return AGENT_CONFIG[agentName] || {
      displayName: agentName,
      icon: vic20SageIcon, // Default fallback
      colorClass: 'default',
    };
  };
  
  // Determine message type for styling
  const getMessageTypeClass = (comm: AgentCommunication): string => {
    const type = comm.message_type?.toUpperCase() || '';
    if (type.includes('TRIAGE') || type.includes('ALERT')) return 'triage';
    if (type.includes('LOG') || type.includes('DECISION')) return 'log';
    if (type.includes('COORDINATION') || type.includes('REQUEST')) return 'coordination';
    if (type.includes('ERROR')) return 'error';
    return 'insight';
  };

  return (
    <div className={`${styles.streamContainer} ${className}`}>
      {/* Header */}
      <div className={styles.streamHeader}>
        <div className={styles.streamTitle}>
          <span className={styles.titleText}>STREAM OF CONSCIOUSNESS</span>
          <span className={`${styles.liveIndicator} ${communications.length > 0 ? styles.active : ''}`}>
            ● LIVE
          </span>
        </div>
        <button 
          className={`${styles.pauseButton} ${isPaused ? styles.paused : ''}`}
          onClick={() => setIsPaused(!isPaused)}
          title={isPaused ? 'Resume auto-scroll' : 'Pause auto-scroll'}
        >
          {isPaused ? '▶' : '⏸'}
        </button>
      </div>
      
      {/* Feed */}
      <div 
        ref={feedRef}
        className={styles.streamFeed}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        {displayItems.length === 0 ? (
          <div className={styles.emptyState}>
            <span className={styles.emptyText}>Agents initializing...</span>
            <div className={styles.loadingPulse}></div>
          </div>
        ) : (
          displayItems.map((comm, index) => {
            const agentConfig = getAgentConfig(comm.from_agent);
            const typeClass = getMessageTypeClass(comm);
            
            return (
              <div 
                key={comm.id || index}
                className={`${styles.streamItem} ${styles[agentConfig.colorClass]} ${styles[typeClass]}`}
              >
                <div className={styles.itemHeader}>
                  <img 
                    src={agentConfig.icon} 
                    alt={agentConfig.displayName}
                    className={styles.agentIcon}
                  />
                  <span className={styles.agentName}>{agentConfig.displayName}</span>
                  {comm.to_agent && comm.to_agent !== 'broadcast' && (
                    <span className={styles.routingArrow}>
                      → {AGENT_CONFIG[comm.to_agent]?.displayName || comm.to_agent}
                    </span>
                  )}
                  <span className={styles.timestamp}>{formatRelativeTime(comm.timestamp)}</span>
                </div>
                <div className={styles.itemMessage}>
                  {comm.summary || comm.message_type || 'Activity'}
                </div>
                {comm.confidence !== undefined && (
                  <div className={styles.itemMeta}>
                    confidence: {(comm.confidence * 100).toFixed(0)}%
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
      
      {/* Footer with count */}
      <div className={styles.streamFooter}>
        <span className={styles.messageCount}>
          {communications.length} messages
        </span>
        {isPaused && (
          <span className={styles.pausedIndicator}>⏸ Paused</span>
        )}
      </div>
    </div>
  );
};

export default StreamOfConsciousness;