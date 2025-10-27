// components/agent-theater/AgentIntelligenceOverlay.tsx
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './AgentIntelligenceOverlay.module.css';

export interface AgentDecision {
  trigger: string;
  analysis: string;
  action: string;
  confidence: number;
  impact: string;
  status: 'analyzing' | 'executing' | 'complete';
}

interface AgentIntelligenceOverlayProps {
  agentId: string;
  decision: AgentDecision | null;
  isVisible: boolean;
}

export const AgentIntelligenceOverlay: React.FC<AgentIntelligenceOverlayProps> = ({
  agentId,
  decision,
  isVisible
}) => {
  if (!decision || !isVisible) return null;

  const accentColors: Record<string, string> = {
    sir_hawkington: 'var(--hawkington-gold)',
    the_stick: 'var(--stick-coral)',
    hamsters: 'var(--hamster-amber)',
    meth_snail: 'var(--snail-electric)',
    quantum_shadow_people: 'var(--qsp-violet)',
    vic20_sage: 'var(--vic20-cyan)'
  };

  const accentColor = accentColors[agentId] || 'var(--rebellion-border)';

  const statusIcons: Record<AgentDecision['status'], string> = {
    analyzing: '🔍',
    executing: '⚡',
    complete: '✓'
  };

  const statusColors: Record<AgentDecision['status'], string> = {
    analyzing: 'var(--warning)',
    executing: 'var(--info)',
    complete: 'var(--success)'
  };

  return (
    <AnimatePresence>
      <motion.div
        className={styles.overlay}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        style={{
          // expose accent color to CSS module for dynamic theming
          '--overlay-accent': accentColor
        } as React.CSSProperties}
      >
        <div className={styles.decisionHeader}>
          <span 
            className={styles.statusIcon}
            style={{ color: statusColors[decision.status] }}
          >
            {statusIcons[decision.status]}
          </span>
          <span className={styles.statusText}>
            {decision.status.toUpperCase()}
          </span>
          <span className={styles.confidence}>
            {decision.confidence}% confidence
          </span>
        </div>

        <div className={styles.decisionContent}>
          <div className={styles.decisionRow}>
            <span className={styles.label}>Trigger:</span>
            <span className={styles.value}>{decision.trigger}</span>
          </div>
          
          <div className={styles.decisionRow}>
            <span className={styles.label}>Analysis:</span>
            <span className={styles.value}>{decision.analysis}</span>
          </div>
          
          <div className={styles.decisionRow}>
            <span className={styles.label}>Action:</span>
            <span className={styles.actionValue}>{decision.action}</span>
          </div>

          {decision.status === 'executing' && (
            <div className={styles.progressBar}>
              <motion.div
                className={styles.progressFill}
                initial={{ width: '0%' }}
                animate={{ width: '75%' }}
                transition={{ duration: 2, ease: 'easeOut' }}
              />
            </div>
          )}

          <div className={styles.impactRow}>
            <span className={styles.impactLabel}>Expected Impact:</span>
            <span className={styles.impactValue}>{decision.impact}</span>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};