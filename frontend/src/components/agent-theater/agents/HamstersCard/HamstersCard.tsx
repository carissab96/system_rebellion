// components/AgentTheater/agents/HamstersCard/HamstersCard.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { HamstersMetrics } from './HamstersMetrics';
import { Chart3D } from '../shared/Chart3D';
import './HamstersCard.css';

interface HamstersCardProps {
  data?: any;
  is_active: boolean;
}

export const HamstersCard: React.FC<HamstersCardProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  
  const handleDetailsClick = () => {
    navigate('/agents/hamsters');
  };
  
  if (!is_active) {
    return (
      <div className="agent-card hamsters offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">The Hamsters</h3>
            <div className="agent-title">Rapid Response Engineering</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>Engineering team unavailable</strong></p>
            <div className="offline-reasons">
              <span>• Wheel spinning handler offline</span>
              <span>• Beer supply depleted</span>
              <span>• Duct tape inventory empty</span>
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
    <div className="agent-card hamsters online">
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">The Hamsters</h3>
          <div className="agent-title">Rapid Response Engineering</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online engineering"></span>
          <span className="status-text">
            {data.rapid_response_possible ? 'Ready to Fix Shit' : 'Standby'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Current Situation:</div>
        <div className="thought-content redneck">
          "{data.message || 'No current engineering situation'}"
        </div>
      </div>
      
      <div className="supply-section">
        <div className="supply-grid">
          <div className="supply-item">
            <span className="supply-label">Beer:</span>
            <span className={`supply-value ${data.beer_level?.toLowerCase() || 'unknown'}`}>
              {data.beer_level || 'Unknown'}
            </span>
          </div>
          <div className="supply-item">
            <span className="supply-label">Duct Tape:</span>
            <span className={`supply-value ${data.duct_tape_available ? 'available' : 'unavailable'}`}>
              {data.duct_tape_available ? 'Available' : 'Unavailable'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="metrics-section">
        <HamstersMetrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Redneck Ingenuity', value: data.redneck_ingenuity === 'MAXIMUM' ? 1 : 0 },
            { label: 'Rapid Response', value: data.rapid_response_possible ? 1 : 0 },
            { label: 'Engineering Readiness', value: data.confidence || 0 }
          ]}
          color="#ff6b35"
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
export default HamstersCard;
