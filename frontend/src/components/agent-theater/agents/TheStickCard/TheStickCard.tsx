// components/AgentTheater/agents/TheStickCard/TheStickCard.tsx
import React from 'react';

import { useNavigate } from 'react-router-dom';

import { Chart3D } from '../shared/Chart3D';

import { TheStickMetrics } from './TheStickMetrics';
import './TheStickCard.css';

interface TheStickCardProps {
  data?: any;
  is_active: boolean;
}

export const TheStickCard: React.FC<TheStickCardProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  
  const handleDetailsClick = () => {
    navigate('/agents/the-stick');
  };
  
  if (!is_active) {
    return (
      <div className="agent-card the-stick offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">The Stick</h3>
            <div className="agent-title">Compliance Expert (Trauma Survivor)</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>Compliance monitoring unavailable</strong></p>
            <div className="offline-reasons">
              <span>• Trauma-awareness protocols offline</span>
              <span>• Paper bag supply exhausted</span>
              <span>• Hyperventilation sensors disconnected</span>
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
    <div className="agent-card the-stick online">
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">The Stick</h3>
          <div className="agent-title">Compliance Expert (Trauma Survivor)</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online"></span>
          <span className="status-text">
            {data.stick_personality?.anxiety_level || 'Monitoring'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Current State:</div>
        <div className="thought-content trauma-aware">
          "{data.message || 'No current compliance analysis available'}"
        </div>
      </div>
      
      <div className="confidence-section">
        <div className="confidence-label">Confidence Level</div>
        <div className="confidence-display">
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${data.pattern_confidence ? data.pattern_confidence * 100 : 0}%` 
              }}
            />
          </div>
          <div className="confidence-value">
            {data.pattern_confidence ? Math.round(data.pattern_confidence * 100) : 0}%
          </div>
        </div>
      </div>
      
      <div className="anxiety-section">
        <div className="anxiety-level">
          <div className={`anxiety-indicator ${data.stick_personality?.anxiety_level?.toLowerCase() || 'unknown'}`}></div>
          <span>Anxiety: {data.stick_personality?.anxiety_level || 'Unknown'}</span>
        </div>
        
        <div className="paper-bag-status">
          <span>Paper Bag: </span>
          <span className={`${data.paper_bag_status?.toLowerCase().replace('_', '-') || 'unknown'}`}>
            {data.paper_bag_status || 'Unknown'}
          </span>
        </div>
        
        <div className="compliance-metrics">
          <div className="compliance-metric">
            <div className="compliance-metric-value">
              {data.stick_personality?.ocd_satisfaction || 'N/A'}
            </div>
            <div className="compliance-metric-label">OCD Status</div>
          </div>
          <div className="compliance-metric">
            <div className="compliance-metric-value">
              {data.proctologist_flashbacks ? 'Active' : 'Inactive'}
            </div>
            <div className="compliance-metric-label">Flashbacks</div>
          </div>
        </div>
      </div>
      
      <div className="metrics-section">
        <TheStickMetrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Compliance Level', value: data.pattern_confidence || 0 },
            { label: 'Anxiety Management', value: data.stick_personality?.anxiety_level === 'MANAGEABLE' ? 0.8 : 0.3 },
            { label: 'Trauma Recovery', value: data.stick_personality?.trauma_management === 'ACTIVE' ? 0.7 : 0.2 }
          ]}
          color="#f97316"
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
export default TheStickCard;
