// components/AgentTheater/agents/SirHawkingtonCard/SirHawkingtonCard.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { SirHawkingtonMetrics } from './SirHawkingtonMetrics';
import { Chart3D } from '../shared/Chart3D';
import './SirHawkingtonCard.css';

interface SirHawkingtonCardProps {
  data?: any;
  isActive: boolean;
}

export const SirHawkingtonCard: React.FC<SirHawkingtonCardProps> = ({ data, isActive }) => {
  const navigate = useNavigate();
  
  const handleDetailsClick = () => {
    navigate('/agents/sir-hawkington');
  };
  
  if (!isActive) {
    return (
      <div className="agent-card sir-hawkington offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">Sir Hawkington Von Monitorious III</h3>
            <div className="agent-title">Systems Watchman</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>No data received</strong></p>
            <div className="offline-reasons">
              <span>• WebSocket handler not running</span>
              <span>• Decision engine offline</span>
              <span>• Database connection issues</span>
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
    <div className="agent-card sir-hawkington online">
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">Sir Hawkington Von Monitorious III</h3>
          <div className="agent-title">Systems Watchman</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online"></span>
          <span className="status-text">
            {data.monocle_state === 'yeeted' ? 'Monocle Yeeted' : 'Monitoring'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Current Analysis:</div>
        <div className="thought-content aristocratic">
          "{data.message || 'No current analysis available'}"
        </div>
      </div>
      
      <div className="confidence-section">
        <div className="confidence-label">Confidence Level</div>
        <div className="confidence-display">
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${data.confidence ? data.confidence * 100 : 0}%` 
              }}
            />
          </div>
          <div className="confidence-value">
            {data.confidence ? Math.round(data.confidence * 100) : 0}%
          </div>
        </div>
      </div>
      
      <div className="metrics-section">
        <SirHawkingtonMetrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Data Quality', value: data.data_quality_score || 0 },
            { label: 'Stress Level', value: data.stress_score || 0 },
            { label: 'Confidence', value: data.confidence || 0 }
          ]}
          color="#c9b037"
          height={120}
        />
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
export default SirHawkingtonCard;
