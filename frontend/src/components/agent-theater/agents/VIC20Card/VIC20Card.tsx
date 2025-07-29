// components/AgentTheater/agents/VIC20Card/VIC20Card.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VIC20Metrics } from './VIC20Metrics';
import { Chart3D } from '../shared/Chart3D';
import './VIC20Card.css';

interface VIC20CardProps {
  data?: any;
  is_active: boolean;
}

export const VIC20Card: React.FC<VIC20CardProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  const [warGamesMode, setWarGamesMode] = useState(false);
  
  const handleDetailsClick = () => {
    navigate('/agents/vic-20');
  };
  
  const triggerWarGamesMode = () => {
    setWarGamesMode(true);
    setTimeout(() => setWarGamesMode(false), 5000);
  };
  
  if (!is_active) {
    return (
      <div className="agent-card vic-20 offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">VIC-20 Sage</h3>
            <div className="agent-title">Ancient Wisdom Coordinator</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>Ancient wisdom bridge offline</strong></p>
            <div className="offline-reasons">
              <span>• Coordination center disconnected</span>
              <span>• Learning patterns unavailable</span>
              <span>• 1989-2025 wisdom bridge severed</span>
            </div>
          </div>
        </div>
        
        <div className="card-actions">
          <button 
            className="details-button disabled"
            disabled
          >
            Details Unavailable
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`agent-card vic-20 online ${warGamesMode ? 'war-games-mode' : ''}`}>
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">VIC-20 Sage</h3>
          <div className="agent-title">Ancient Wisdom Coordinator</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online"></span>
          <span className="status-text">
            {data.learning_mode_active ? 'Learning Active' : 'Coordinating'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Ancient Wisdom:</div>
        <div className="thought-content retro-wisdom">
          "{data.message || data.ancient_wisdom_principle || 'No coordination analysis available'}"
        </div>
      </div>
      
      <div className="confidence-section">
        <div className="confidence-label">Coordination Confidence</div>
        <div className="confidence-display">
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${data.coordination_confidence ? data.coordination_confidence * 100 : 0}%` 
              }}
            />
          </div>
          <div className="confidence-value">
            {data.coordination_confidence ? Math.round(data.coordination_confidence * 100) : 0}%
          </div>
        </div>
      </div>
      
      <div className="retro-terminal">
        <div className="coordination-stats">
          <div className="coordination-stat">
            <div className="coordination-stat-label">Sessions</div>
            <div className="coordination-stat-value">
              {data.coordination_sessions || 0}
            </div>
          </div>
          <div className="coordination-stat">
            <div className="coordination-stat-label">Success</div>
            <div className="coordination-stat-value">
              {data.successful_coordinations || 0}
            </div>
          </div>
          <div className="coordination-stat">
            <div className="coordination-stat-label">Patterns</div>
            <div className="coordination-stat-value">
              {data.pattern_applications || 0}
            </div>
          </div>
          <div className="coordination-stat">
            <div className="coordination-stat-label">Agents</div>
            <div className="coordination-stat-value">
              {data.connected_agents || 0}
            </div>
          </div>
        </div>
      </div>
      
      <div className="ancient-wisdom-section">
        <div className={`wisdom-indicator ${data.pattern_matching_enabled ? 'active' : ''}`}>
          <span className="indicator-label">Pattern Matching:</span>
          <span className="indicator-status">
            {data.pattern_matching_enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <div className={`wisdom-indicator ${data.effectiveness_tracking_enabled ? 'active' : ''}`}>
          <span className="indicator-label">Effectiveness Tracking:</span>
          <span className="indicator-status">
            {data.effectiveness_tracking_enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      </div>
        
      <div className="wisdom-bridge">
        <span className="bridge-text">Wisdom Bridge: 1989 → 2025</span>
        <span className="bridge-status">
          {data.ancient_wisdom_bridge || 'Active'}
        </span>
      </div>
      
      <div className="metrics-section">
        <VIC20Metrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Coordination Success', value: data.coordination_sessions ? (data.successful_coordinations || 0) / data.coordination_sessions : 0 },
            { label: 'Learning Capability', value: data.learning_mode_active ? 0.95 : 0.3 },
            { label: 'Pattern Recognition', value: data.pattern_matching_enabled ? 0.88 : 0.2 }
          ]}
          color="#06b6d4"
          height={120}
        />
      </div>
      
      <div className="war-games-section">
        <button 
          className="war-games-button"
          onClick={triggerWarGamesMode}
          disabled={warGamesMode}
        >
          {warGamesMode ? 'ANALYZING...' : 'PLAY GLOBAL THERMONUCLEAR WAR'}
        </button>
        {warGamesMode && (
          <div className="war-games-message">
            <span className="blinking-text">
              HOW ABOUT A NICE GAME OF CHESS INSTEAD?
            </span>
          </div>
        )}
      </div>
      
      <div className="card-actions">
        <button 
          className="details-button"
          onClick={handleDetailsClick}
        >
          View Details
        </button>
      </div>
    </div>
  );
};
export default VIC20Card;
