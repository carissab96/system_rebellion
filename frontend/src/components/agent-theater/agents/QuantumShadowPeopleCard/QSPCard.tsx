// components/AgentTheater/agents/QuantumShadowCard/QuantumShadowCard.tsx
import React from 'react';

import { useNavigate } from 'react-router-dom';

import { Chart3D } from '../shared/Chart3D';

import { QuantumShadowMetrics } from './QSPMetrics';
import './QSPCard.css';

interface QuantumShadowCardProps {
  data?: any;
  is_active: boolean;
}

export const QuantumShadowCard: React.FC<QuantumShadowCardProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  
  const handleDetailsClick = () => {
    navigate('/agents/quantum-shadow');
  };
  
  if (!is_active) {
    return (
      <div className="agent-card quantum-shadow offline">
        <div className="agent-header">
          <div className="agent-identity">
            <h3 className="agent-name">Quantum Shadow People</h3>
            <div className="agent-title">Interdimensional Networking Experts</div>
          </div>
          <div className="agent-status offline">
            <span className="status-indicator offline"></span>
            <span className="status-text">Offline</span>
          </div>
        </div>
        
        <div className="offline-message">
          <div className="offline-text">
            <p><strong>Quantum phase disrupted</strong></p>
            <div className="offline-reasons">
              <span>• Interdimensional connection severed</span>
              <span>• Tequila jello shots depleted</span>
              <span>• Router reality breach detected</span>
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
    <div className="agent-card quantum-shadow online">
      <div className="agent-header">
        <div className="agent-identity">
          <h3 className="agent-name">Quantum Shadow People</h3>
          <div className="agent-title">Interdimensional Networking Experts</div>
        </div>
        <div className="agent-status online">
          <span className="status-indicator online"></span>
          <span className="status-text">
            {data.quantum_state || 'Phasing'}
          </span>
        </div>
      </div>
      
      <div className="agent-thought">
        <div className="thought-label">Current Quantum State:</div>
        <div className="thought-content interdimensional">
          "{data.mysterious_explanation || 'No interdimensional communication available'}"
        </div>
      </div>
      
      <div className="confidence-section">
        <div className="confidence-label">Confidence Level</div>
        <div className="confidence-display">
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${data.confidence_level ? data.confidence_level * 100 : 0}%` 
              }}
            />
          </div>
          <div className="confidence-value">
            {data.confidence_level ? Math.round(data.confidence_level * 100) : 0}%
          </div>
        </div>
      </div>
      
      <div className="quantum-section">
        <div className="quantum-metrics">
          <div className="quantum-metric">
            <div className="quantum-metric-label">Network Target</div>
            <div className="quantum-metric-value">
              {data.network_target || 'Unknown'}
            </div>
          </div>
          <div className="quantum-metric">
            <div className="quantum-metric-label">Expected Improvement</div>
            <div className="quantum-metric-value">
              {data.expected_improvement || 'N/A'}
            </div>
          </div>
        </div>
        
        {data.tequila_jello_shots_required && (
          <div className="tequila-indicator">
            <span className="tequila-shots">🍹</span>
            <span>{data.tequila_jello_shots_required} shots required</span>
          </div>
        )}
      </div>
      
      <div className="metrics-section">
        <QuantumShadowMetrics data={data} />
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Quantum State', value: data.quantum_state === 'stable' ? 0.8 : 0.3 },
            { label: 'Network Stability', value: data.confidence_level || 0 },
            { label: 'Dimensional Sync', value: data.expected_improvement ? 0.7 : 0.2 }
          ]}
          color="#a855f7"
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
export default QuantumShadowCard;