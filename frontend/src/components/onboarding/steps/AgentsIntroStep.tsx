// components/onboarding/steps/AgentsIntroStep.tsx
import React, { useState } from 'react';
import type { CSSProperties } from 'react';

import { motion, AnimatePresence } from 'framer-motion';

import { StepNavigation } from '../components/StepNavigation';
import type { StepProps } from '../OnboardingFlow';

import styles from './AgentsIntroStep.module.css';


// The full agent data with your excellent, thematic lore
const agents = [
  {
    id: 'hawkington',
    name: 'Sir Hawkington',
    role: 'Triage Commander',
    description: 'Aristocratic decision-maker who routes issues with monocle-yeeting precision',
    style: { color: '#e6ac00' },
    details: {
      personality: 'Aristocratic perfectionist with zero tolerance for bad data',
      responsibility: 'First responder who assesses severity and delegates to specialists',
      quirks: 'Yeets monocle when data quality is beneath standards',
      memory: 'Remembers every monocle yeet incident and data quality failure',
      interactions: 'Commands all other agents, especially during emergencies'
    }
  },
  {
    id: 'stick',
    name: 'The Stick',
    role: 'Compliance Monitor',
    description: 'Anxiety-driven hypervigilance catches what others miss',
    style: { color: '#f97316' },
    details: {
      personality: 'OCD + ADHD + PTSD + Eidetic Memory = Perfect paranoid monitor',
      responsibility: 'Learns user patterns and enforces compliance thresholds',
      quirks: 'Consumes paper bags when anxious, especially around Bob',
      memory: 'Eidetic - remembers EVERYTHING that ever happened',
      interactions: 'Panics when Hamsters nearby, understands their squeaks through shared anxiety'
    }
  },
  {
    id: 'hamsters',
    name: 'The Hamsters',
    role: 'Infrastructure Team',
    description: 'Steve, Bob, and Carl fix everything with beer and duct tape',
    style: { color: '#ff8c42' },
    details: {
      personality: 'Steve (careful), Bob (chaos), Carl (duct tape mathematician)',
      responsibility: '3AM emergency infrastructure fixes, disk cleanup, defragmentation',
      quirks: 'Peak performance at 3-4 beers, communicate in squeaks',
      memory: 'Collective telepathic memory, ancient beer-stained wisdom',
      interactions: 'Bob causes Stick anxiety, telepathic understanding with QSP'
    }
  },
  {
    id: 'snail',
    name: 'Meth Snail',
    role: 'Speed Optimizer',
    description: 'Caffeinated gastropod who makes everything faster',
    style: { color: '#00d084' },
    details: {
      personality: 'Hyperactive optimization and energy-drink addict leaving trails of improvements',
      responsibility: 'CPU optimization, process prioritization, speed enhancements',
      quirks: 'Leaves glowing optimization trails, shell spins indicate excitement',
      memory: 'Remembers every optimization and its cascading effects',
      interactions: 'Too caffeinated to understand Hamster squeaks, respects Hawkington'
    }
  },
  {
    id: 'qsp',
    name: 'Quantum Shadow People',
    role: 'Network Specialists',
    description: 'Interdimensional travelers who phase through dimensions to fix network issues',
    style: { color: '#a855f7' },
    details: {
      personality: 'Mysterious entities who have existed across dimensions for eons',
      responsibility: 'Network optimization, security, packet recovery from the void',
      quirks: 'Fix routers by phasing them upside down through tequila jello shots',
      memory: 'Remember network patterns across dimensional boundaries',
      interactions: 'Telepathic bond with each other and the Hamsters, incomprehensible to most humans'
    }
  },
  {
    id: 'vic20',
    name: 'VIC-20',
    role: 'Ancient Wisdom',
    description: 'Mediates conflicts and provides historical wisdom from 1982-2025',
    style: { color: '#06b6d4' },
    details: {
      personality: 'Ancient sage who has seen every pattern since 1982 and might have attempted to start geonuclear war',
      responsibility: 'Pattern recognition, conflict mediation, auto-tuning recommendations',
      quirks: 'Speaks in historical computing references, always relevant',
      memory: '40+ years of patterns, every mistake and solution ever made',
      interactions: 'Mediates between agents, determines auto-tuning recommendations,translates Hamster squeaks to others, provides historical wisdom'
    }
  }
];

// The pattern rendering function, now part of this component
const renderAgentPattern = (agentId: string) => {
  // ... (The exact switch/case code for patterns you provided)
  // I will include it here for completeness
    switch (agentId) {
      case 'hawkington': return (<div className="agent-pattern hawkington-pattern"><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /></div>);
      case 'stick': return (<div className="agent-pattern stick-pattern"><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /></div>);
      case 'hamsters': return (<div className="agent-pattern hamsters-pattern"><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /></div>);
      case 'snail': return (<div className="agent-pattern snail-pattern"><svg viewBox="0 0 80 80"><path className="snail-spiral" d="M40,40 Q50,30 40,20 T20,20 Q10,30 10,40 T20,60 Q30,70 40,70 T60,60 Q70,50 70,40 T60,20"/></svg></div>);
      case 'qsp': return (<div className="agent-pattern qsp-pattern"><div className="pattern-element" /><div className="pattern-element" /></div>);
      case 'vic20': return (<div className="agent-pattern vic20-pattern"><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /><div className="pattern-element" /></div>);
      default: return null;
    }
};

export const AgentsIntroStep: React.FC<StepProps> = ({ onNext, onBack }) => {
  // State for the interactive cards, from your final version
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);
  const [lockedAgents, setLockedAgents] = useState<Set<string>>(new Set());

  // Handlers from your final version
  const handleCardClick = (agentId: string) => {
    setLockedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) newSet.delete(agentId);
      else newSet.add(agentId);
      return newSet;
    });
  };

  const handleMouseEnter = (agentId: string) => setHoveredAgent(agentId);
  const handleMouseLeave = () => setHoveredAgent(null);
  const isExpanded = (agentId: string) => lockedAgents.has(agentId) || hoveredAgent === agentId;

  return (
    <div className={styles.agentsIntroStep}>
      <div className={styles.agentsShowcase}>
        {agents.map((agent) => {
          const expanded = isExpanded(agent.id);
          const locked = lockedAgents.has(agent.id);
          
          return (
            <motion.div
              key={agent.id}
              className={`${styles.agentShowcaseCard} ${expanded ? styles.expanded : ''} ${locked ? styles.locked : ''}`}
              onClick={() => handleCardClick(agent.id)}
              onMouseEnter={() => handleMouseEnter(agent.id)}
              onMouseLeave={handleMouseLeave}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                ...({ '--agent-color': agent.style.color } as CSSProperties),
                borderColor: expanded ? agent.style.color : 'transparent'
              }}            >
              <div className={styles.agentIdentity}>
                <div className={styles.agentPatternContainer}>
                  {renderAgentPattern(agent.id)}
                </div>
                <div className={styles.agentBasicInfo}>
                  <h3 className={styles.agentName}>{agent.name}</h3>
                  <p className={styles.agentRole}>{agent.role}</p>
                </div>
                {locked && <div className={styles.lockIndicator}><div className={styles.lockIcon} /></div>}
              </div>
              
              <p className={styles.agentDescription}>{agent.description}</p>
              
              <AnimatePresence>
                {expanded && (
                  <motion.div 
                    className={styles.agentDetails}
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* Re-creating the details from your code */}
                    <div className={styles.detailItem}><span className={styles.detailLabel}>Personality</span><span className={styles.detailContent}>{agent.details.personality}</span></div>
                    <div className={styles.detailItem}><span className={styles.detailLabel}>Responsibility</span><span className={styles.detailContent}>{agent.details.responsibility}</span></div>
                    <div className={styles.detailItem}><span className={styles.detailLabel}>Quirks</span><span className={styles.detailContent}>{agent.details.quirks}</span></div>
                    <div className={styles.detailItem}><span className={styles.detailLabel}>Memory</span><span className={styles.detailContent}>{agent.details.memory}</span></div>
                    <div className={styles.detailItem}><span className={styles.detailLabel}>Interactions</span><span className={styles.detailContent}>{agent.details.interactions}</span></div>
                  </motion.div>
                )}
              </AnimatePresence>
              
              <div className={styles.cardFooter}>
                <span className={styles.interactionHint}>
                  {locked ? 'Click to collapse' : expanded ? 'Click to lock open' : 'Hover to preview • Click to lock'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className={styles.agentsFooter}>
        <p className={styles.agentsNote}>
          Hover over each agent to preview their details. Click to keep a card expanded while exploring others.
          These aren't chatbots - they're specialized decision engines with persistent memory and complex inter-agent relationships.
        </p>
      </div>
      
      {/* INTEGRATION: Using our consistent StepNavigation component */}
      <StepNavigation 
        onNext={onNext} 
        onBack={onBack} 
        nextLabel="Configure Agents" 
      />
    </div>
  );
};