// components/onboarding/components/AgentCard.tsx
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AgentPattern } from './AgentPattern';

interface AgentDetails {
  personality: string;
  responsibility: string;
  quirks: string;
  memory: string;
  interactions: string;
}

interface AgentCardProps {
  id: string;
  name: string;
  role: string;
  description: string;
  color: string;
  details: AgentDetails;
  expanded: boolean;
  locked: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onClick: () => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  id,
  name,
  role,
  description,
  color,
  details,
  expanded,
  locked,
  onMouseEnter,
  onMouseLeave,
  onClick
}) => {
  return (
    <motion.div
      className={`agent-showcase-card ${expanded ? 'expanded' : ''} ${locked ? 'locked' : ''}`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        '--agent-color': color,
        borderColor: expanded ? color : 'transparent'
      } as React.CSSProperties}
    >
      <div className="agent-identity">
        <div className="agent-pattern-container">
          <AgentPattern agentId={id} />
        </div>
        <div className="agent-basic-info">
          <h3 className="agent-name">{name}</h3>
          <p className="agent-role">{role}</p>
        </div>
        {locked && (
          <div className="lock-indicator">
            <div className="lock-icon" />
          </div>
        )}
      </div>
      
      <p className="agent-description">{description}</p>
      
      <AnimatePresence>
        {expanded && (
          <motion.div 
            className="agent-details"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {Object.entries(details).map(([key, value]) => (
              <div key={key} className="detail-item">
                <span className="detail-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                <span className="detail-content">{value}</span>
              </div>
            ))}
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
};