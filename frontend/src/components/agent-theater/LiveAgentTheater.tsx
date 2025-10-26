// components/agent-theater/LiveAgentTheater.tsx
import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { LiveAgentCard } from './LiveAgentCard';
import styles from './LiveAgentTheater.module.css';

// Agent personality data from onboarding
const AGENT_PERSONALITIES = [
  {
    id: 'sir_hawkington',
    name: 'Sir Hawkington',
    role: 'Triage Commander',
    description: 'Aristocratic decision-maker who routes issues with monocle-yeeting precision',
    color: '#e6ac00',
    personality: 'Aristocratic perfectionist with zero tolerance for bad data',
    responsibility: 'First responder who assesses severity and delegates to specialists',
    quirks: 'Yeets monocle when data quality is beneath standards',
    memory: 'Remembers every monocle yeet incident and data quality failure',
    interactions: 'Commands all other agents, especially during emergencies'
  },
  {
    id: 'the_stick',
    name: 'The Stick',
    role: 'Compliance Monitor',
    description: 'Anxiety-driven hypervigilance catches what others miss',
    color: '#f97316',
    personality: 'OCD + ADHD + PTSD + Eidetic Memory = Perfect paranoid monitor',
    responsibility: 'Learns user patterns and enforces compliance thresholds',
    quirks: 'Consumes paper bags when anxious, especially around Bob',
    memory: 'Eidetic - remembers EVERYTHING that ever happened',
    interactions: 'Panics when Hamsters nearby, understands their squeaks through shared anxiety'
  },
  {
    id: 'hamsters',
    name: 'The Hamsters',
    role: 'Infrastructure Team',
    description: 'Steve, Bob, and Carl fix everything with beer and duct tape',
    color: '#ff8c42',
    personality: 'Steve (careful), Bob (chaos), Carl (duct tape mathematician)',
    responsibility: '3AM emergency infrastructure fixes, disk cleanup, defragmentation',
    quirks: 'Peak performance at 3-4 beers, communicate in squeaks',
    memory: 'Collective telepathic memory, ancient beer-stained wisdom',
    interactions: 'Bob causes Stick anxiety, telepathic understanding with QSP'
  },
  {
    id: 'meth_snail',
    name: 'Meth Snail',
    role: 'Speed Optimizer',
    description: 'Caffeinated gastropod who makes everything faster',
    color: '#00d084',
    personality: 'Hyperactive optimization and energy-drink addict leaving trails of improvements',
    responsibility: 'CPU optimization, process prioritization, speed enhancements',
    quirks: 'Leaves glowing optimization trails, shell spins indicate excitement',
    memory: 'Remembers every optimization and its cascading effects',
    interactions: 'Too caffeinated to understand Hamster squeaks, respects Hawkington'
  },
  {
    id: 'quantum_shadow_people',
    name: 'Quantum Shadow People',
    role: 'Network Specialists',
    description: 'Interdimensional travelers who phase through dimensions to fix network issues',
    color: '#a855f7',
    personality: 'Mysterious entities who have existed across dimensions for eons',
    responsibility: 'Network optimization, security, packet recovery from the void',
    quirks: 'Fix routers by phasing them upside down through tequila jello shots',
    memory: 'Remember network patterns across dimensional boundaries',
    interactions: 'Telepathic bond with each other and the Hamsters, incomprehensible to most humans'
  },
  {
    id: 'vic20_sage',
    name: 'VIC-20',
    role: 'Ancient Wisdom',
    description: 'Mediates conflicts and provides historical wisdom from 1982-2025',
    color: '#06b6d4',
    personality: 'Ancient sage who has seen every pattern since 1982 and might have attempted to start geonuclear war',
    responsibility: 'Pattern recognition, conflict mediation, auto-tuning recommendations',
    quirks: 'Speaks in historical computing references, always relevant',
    memory: '40+ years of patterns, every mistake and solution ever made',
    interactions: 'Mediates between agents, determines auto-tuning recommendations, translates Hamster squeaks to others, provides historical wisdom'
  }
];

const setsEqual = <T,>(a: Set<T>, b: Set<T>): boolean => {
  if (a.size !== b.size) {
    return false;
  }
  for (const value of a) {
    if (!b.has(value)) {
      return false;
    }
  }
  return true;
};


interface AgentData {
  [agentId: string]: any;
}

interface LiveAgentTheaterProps {
  agentData: AgentData;
  onAgentClick?: (agentId: string) => void;
}

export const LiveAgentTheater: React.FC<LiveAgentTheaterProps> = ({
  agentData,
  onAgentClick
}) => {
  const [activeAgents, setActiveAgents] = useState<Set<string>>(new Set());
  const [activityPulses, setActivityPulses] = useState<Set<string>>(new Set());
  const previousDataRef = useRef<AgentData>({});

  // Detect active agents and activity changes
  useEffect(() => {
    const newActiveAgents = new Set<string>();
    const newPulses = new Set<string>();

    Object.entries(agentData).forEach(([agentId, data]) => {
      if (data && data.status === 'active') {
        newActiveAgents.add(agentId);

        // Check if data changed (activity pulse)
        const prevData = previousDataRef.current[agentId];
        if (prevData && JSON.stringify(prevData) !== JSON.stringify(data)) {
          newPulses.add(agentId);
          // Clear pulse after animation
          setTimeout(() => {
            setActivityPulses(prev => {
              const next = new Set(prev);
              next.delete(agentId);
              return next;
            });
          }, 1000);
        }
      }
    });

    if (!setsEqual(activeAgents, newActiveAgents)) {
      setActiveAgents(newActiveAgents);
    }

    if (!setsEqual(activityPulses, newPulses)) {
      setActivityPulses(newPulses);
    }

    previousDataRef.current = agentData;
  }, [agentData, activeAgents, activityPulses]);

  return (
    <div className={styles.theaterContainer}>
      {/* Theater Header */}
      <motion.header 
        className={styles.theaterHeader}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className={styles.headerContent}>
          <h1 className={styles.theaterTitle}>
            🎭 Agent Theater 
            <span style={{ 
              marginLeft: '12px', 
              fontSize: '0.6em', 
              color: '#00d084',
              fontWeight: 'bold',
              textTransform: 'uppercase',
              letterSpacing: '0.1em'
            }}>
              NEW
            </span>
          </h1>
          <p className={styles.theaterSubtitle}>
            Live AI Agent Activity • Updates every 60 seconds
          </p>
        </div>
        <div className={styles.activityIndicator}>
          <div className={styles.activityDot} />
          <span className={styles.activityText}>
            {activeAgents.size} {activeAgents.size === 1 ? 'Agent' : 'Agents'} Active
          </span>
        </div>
      </motion.header>

      {/* Agent Cards Grid */}
      <motion.div 
        className={styles.agentGrid}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {AGENT_PERSONALITIES.map((personality, index) => (
          <motion.div
            key={personality.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <LiveAgentCard
              personality={personality}
              data={agentData[personality.id] || null}
              isActive={activeAgents.has(personality.id)}
              activityPulse={activityPulses.has(personality.id)}
              onCardClick={() => onAgentClick?.(personality.id)}
            />
          </motion.div>
        ))}
      </motion.div>

      {/* Theater Footer */}
      <motion.footer 
        className={styles.theaterFooter}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <div className={styles.footerContent}>
          <span className={styles.footerText}>
            System Rebellion • Hawkington Technologies
          </span>
          <span className={styles.footerHint}>
            Click any agent card to view detailed information
          </span>
        </div>
      </motion.footer>
    </div>
  );
};
