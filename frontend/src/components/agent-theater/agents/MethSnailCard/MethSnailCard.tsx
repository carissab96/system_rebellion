// components/AgentTheater/agents/MethSnailCard/MethSnailCard.tsx
import React from 'react';

import { useNavigate } from 'react-router-dom';

import { Chart3D } from '../shared/Chart3D';

import { MethSnailMetrics } from './MethSnailMetrics';
import './MethSnailCard.css';

interface MethSnailCardProps {
  data?: any;
  is_active: boolean;
}

export const MethSnailCard: React.FC<MethSnailCardProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  
  const handleDetailsClick = () => {
    navigate('/agents/meth-snail');
  };
  
  if (!is_active) {
    return (
      <div className="agent-card meth-snail offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">Meth Snail</h3>
            <div className="agent-title">Optimization Specialist</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>No optimization data</strong></p>
            <div className="offline-reasons">
              <span>• Shell spinning handler offline</span>
              <span>• Optimization engine stopped</span>
              <span>• Caffeine levels depleted</span>
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
    <div className="agent-card meth-snail online">
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">Meth Snail</h3>
          <div className="agent-title">Optimization Specialist</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online spinning"></span>
          <span className="status-text">
            {data.shell_state === 'spinning' ? 'Optimizing' : 'Active'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Current Process:</div>
        <div className="thought-content caffeinated">
          "{data.message || 'No current optimization process'}"
        </div>
      </div>
      
      <div className="caffeine-section">
        <div className="caffeine-label">Caffeine Level</div>
        <div className="caffeine-display">
          <div className="caffeine-indicator">
            <div 
              className={`caffeine-level ${data.caffeine_level?.toLowerCase() || 'unknown'}`}
            >
              {data.caffeine_level || 'Unknown'}
            </div>
          </div>
        </div>
      </div>
      
      <div className="metrics-section">
        <MethSnailMetrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Shell Velocity', value: data.shell_spin_count ? data.shell_spin_count / 100 : 0 },
            { label: 'Optimization Rate', value: data.confidence || 0 },
            { label: 'Energy Level', value: data.energy_level === 'MAXIMUM' ? 1 : 0 }
          ]}
          color="#00ff88"
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
export default MethSnailCard;
