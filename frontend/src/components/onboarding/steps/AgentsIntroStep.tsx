// components/onboarding/steps/AgentsIntroStep.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { StepProps } from '../OnboardingFlow';
import { StepNavigation } from '../components/StepNavigation';

// The full agent data with your excellent, thematic lore
const agents = [
  {
    id: 'hawkington',
    name: 'Sir Hawkington',
    role: 'Triage Commander',
    description: 'Aristocratic decision-maker who routes issues with monocle-yeeting precision',
    color: '#e6ac00',
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
    color: '#f97316',
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
    color: '#ff8c42',
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
    description: 'Caffeinated mollusk who makes everything faster',
    color: '#00d084',
    details: {
      personality: 'Hyperactive optimization addict leaving trails of improvements',
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
    description: 'Phase through dimensions to fix network issues',
    color: '#a855f7',
    details: {
      personality: 'Mysterious entities who exist partially in multiple dimensions',
      responsibility: 'Network optimization, security, packet recovery from the void',
      quirks: 'Fix routers by phasing them through tequila jello dimensions',
      memory: 'Remember network patterns across dimensional boundaries',
      interactions: 'Telepathic bond with Hamsters, incomprehensible to most'
    }
  },
  {
    id: 'vic20',
    name: 'VIC-20',
    role: 'Ancient Wisdom',
    description: 'Mediates conflicts with knowledge from 1982-2025',
    color: '#06b6d4',
    details: {
      personality: 'Ancient sage who has seen every pattern since 1982',
      responsibility: 'Pattern recognition, conflict mediation, auto-tuning recommendations',
      quirks: 'Speaks in historical computing references, always relevant',
      memory: '40+ years of patterns, every mistake and solution ever made',
      interactions: 'Mediates between agents, translates Hamster squeaks to others'
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
    <div className="agents-intro-step">
      <div className="agents-showcase">
        {agents.map((agent) => {
          const expanded = isExpanded(agent.id);
          const locked = lockedAgents.has(agent.id);
          
          return (
            <motion.div
              key={agent.id}
              className={`agent-showcase-card ${expanded ? 'expanded' : ''} ${locked ? 'locked' : ''}`}
              onClick={() => handleCardClick(agent.id)}
              onMouseEnter={() => handleMouseEnter(agent.id)}
              onMouseLeave={handleMouseLeave}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ '--agent-color': agent.color, borderColor: expanded ? agent.color : 'transparent' }}
            >
              <div className="agent-identity">
                <div className="agent-pattern-container">
                  {renderAgentPattern(agent.id)}
                </div>
                <div className="agent-basic-info">
                  <h3 className="agent-name">{agent.name}</h3>
                  <p className="agent-role">{agent.role}</p>
                </div>
                {locked && <div className="lock-indicator"><div className="lock-icon" /></div>}
              </div>
              
              <p className="agent-description">{agent.description}</p>
              
              <AnimatePresence>
                {expanded && (
                  <motion.div 
                    className="agent-details"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* Re-creating the details from your code */}
                    <div className="detail-item"><span className="detail-label">Personality</span><span className="detail-content">{agent.details.personality}</span></div>
                    <div className="detail-item"><span className="detail-label">Responsibility</span><span className="detail-content">{agent.details.responsibility}</span></div>
                    <div className="detail-item"><span className="detail-label">Quirks</span><span className="detail-content">{agent.details.quirks}</span></div>
                    <div className="detail-item"><span className="detail-label">Memory</span><span className="detail-content">{agent.details.memory}</span></div>
                    <div className="detail-item"><span className="detail-label">Interactions</span><span className="detail-content">{agent.details.interactions}</span></div>
                  </motion.div>
                )}
              </AnimatePresence>
              
              <div className="card-footer">
                <span className="interaction-hint">
                  {locked ? 'Click to collapse' : expanded ? 'Click to lock open' : 'Hover to preview • Click to lock'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="agents-footer">
        <p className="agents-note">
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