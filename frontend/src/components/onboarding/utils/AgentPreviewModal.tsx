// src/components/onboarding/utils/AgentPreviewModal.tsx
import { useState } from 'react';
import { AgentPattern } from '../components/AgentPattern';
import styles from './AgentPreviewModal.module.css';

interface AgentPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAgent: (agentId: string) => void;
  onSaveAndContinueLater: () => void;
  onStartOver: () => void;
}

interface Agent {
  id: string;
  name: string;
  title: string;
  personality: string;
  signature_color: string;
  demo_action: string;
  preview_description: string;
  what_they_do: string;
}

const PREVIEW_AGENTS: Agent[] = [
  {
    id: 'hawkington',
    name: 'Sir Hawkington',
    title: 'The Aristocratic Triage Master',
    personality: 'Refined, precise, occasionally dramatic',
    signature_color: 'var(--hawkington-gold)',
    demo_action: '*adjusts monocle with aristocratic precision*',
    preview_description: 'Experience the most sophisticated system analysis in the galaxy',
    what_they_do: 'Triages system issues with aristocratic precision, yeeting his monocle when data quality is beneath his standards'
  },
  {
    id: 'stick',
    name: 'The Stick V3',
    title: 'The Hypervigilant Safety Net',
    personality: 'Anxious, thorough, protective',
    signature_color: 'var(--stick-coral)',
    demo_action: '*nervously huffs paper bag*',
    preview_description: 'Never miss a potential system failure again',
    what_they_do: 'Monitors everything with eidetic memory, prevents disasters through controlled anxiety and paper bag breathing'
  },
  {
    id: 'vic20',
    name: 'VIC-20 Sage',
    title: 'The Ancient Mediator',
    personality: 'Wise, patient, nostalgic',
    signature_color: 'var(--vic20-cyan)',
    demo_action: '*hums ancient computing wisdom*',
    preview_description: 'Benefit from decades of computing wisdom',
    what_they_do: 'Provides sage guidance and mediates conflicts between agents with the wisdom of computing history'
  }
];

export default function AgentPreviewModal({ 
  isOpen, 
  onClose, 
  onSelectAgent,
  onSaveAndContinueLater,
  onStartOver 
}: AgentPreviewModalProps) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgent(agentId);
  };

  const handleStartPreview = () => {
    if (selectedAgent) {
      onSelectAgent(selectedAgent);
    }
  };

  return (
    <div className="modal-overlay" onMouseDown={onClose}>
      <div className={`modal-content ${styles.previewModal}`} onMouseDown={e => e.stopPropagation()}>
        <header className="card-header text-center" style={{ position: 'relative' }}>
          <button 
            onClick={onClose}
            className="btn btn-ghost btn-sm"
            style={{ 
              position: 'absolute', 
              right: '1rem', 
              top: '1rem',
              padding: '0.25rem',
              minHeight: 'auto',
              fontSize: '1.2rem',
              lineHeight: '1'
            }}
            title="Close modal"
          >
            ×
          </button>
          <h2 className="card-title vic20-text">Choose Your Guardian</h2>
          <p className="card-subtitle mt-1">Select one agent for your 30-day preview experience</p>
        </header>

        <div className="card-body">
          <div className={styles.previewIntro}>
            <div className="alert alert-info">
              <strong>Preview Mode:</strong> Experience one agent's full personality and capabilities for 30 days. 
              The other agents will work silently in the background, learning your system.
            </div>
          </div>

          {/* Agent Selection Cards */}
          <div className={styles.agentGrid}>
            {PREVIEW_AGENTS.map((agent) => (
              <div 
                key={agent.id}
                className={`${styles.agentCard} ${selectedAgent === agent.id ? styles.selected : ''}`}
                onClick={() => handleSelectAgent(agent.id)}
                style={{ '--agent-color': agent.signature_color } as React.CSSProperties}
              >
                <div className={styles.agentHeader}>
                  <h3 className={styles.agentName}>{agent.name}</h3>
                  <p className={styles.agentTitle}>{agent.title}</p>
                </div>

                <div className={styles.agentDemo}>
                  <div className={styles.demoAction}>
                  <div className={styles.agentPatternContainer}>
                    <AgentPattern agentId={agent.id} />
                  </div>
                  <div>{agent.demo_action}</div>
                </div>
                  <p className={styles.personality}>"{agent.personality}"</p>
                </div>

                <div className={styles.agentDescription}>
                  <p className={styles.previewDesc}>{agent.preview_description}</p>
                  <p className={styles.whatTheyDo}>{agent.what_they_do}</p>
                </div>

                <div className={styles.selectionIndicator}>
                  {selectedAgent === agent.id && (
                    <div className={styles.selectedBadge}>
                      ✓ Selected for Preview
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Preview Benefits */}
          <div className={styles.previewBenefits}>
            <h4>What You'll Experience:</h4>
            <ul>
              <li><strong>Full personality interactions</strong> - See your chosen agent's quirks in action</li>
              <li><strong>Real-time learning</strong> - Watch them adapt to your system and habits</li>
              <li><strong>Weekly insights</strong> - Discover what the hidden agents are doing behind the scenes</li>
              <li><strong>Proactive protection</strong> - Experience autonomous system optimization</li>
            </ul>
          </div>
        </div>

        <footer className="card-footer">
          <div className={styles.modalActions}>
            <div className={styles.primaryActions}>
              <button 
                className="btn btn-primary btn-lg"
                onClick={handleStartPreview}
                disabled={!selectedAgent}
              >
                {selectedAgent ? `Start 30-Day Preview with ${PREVIEW_AGENTS.find(a => a.id === selectedAgent)?.name}` : 'Select an Agent First'}
              </button>
            </div>

            <div className={styles.secondaryActions}>
              <button 
                className="btn btn-ghost"
                onClick={onSaveAndContinueLater}
              >
                Save & Continue Later
              </button>
              
              <button 
                className="btn btn-ghost"
                onClick={onStartOver}
              >
                Start Over
              </button>
              
              <button 
                className="btn btn-ghost"
                onClick={onClose}
              >
                Continue Setup
              </button>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
