// components/AgentTheater/agents/HamstersCard/HamstersCard.tsx
import React from 'react';

import { useNavigate } from 'react-router-dom';

import { Chart3D } from '../shared/Chart3D';

import { useHamstersMetrics } from './HamstersMetrics';
import './HamstersCard.css';

interface HamstersCardComponentProps {
  data?: any;
  is_active: boolean;
}

export const HamstersCard: React.FC<HamstersCardComponentProps> = ({ data, is_active }) => {
  const navigate = useNavigate();
  const metrics = useHamstersMetrics();
  
  // Use the metrics from the hook if available, otherwise use the passed-in data
  const cardData = metrics.raw || data;
  
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
            <span className={`supply-value ${cardData?.duct_tape_available ? 'available' : 'unavailable'}`}>
              {cardData?.duct_tape_available ? 'Available' : 'Unavailable'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="metrics-section">
        <div className="metrics-container">
          <div className="metric-item">
            <span className="metric-label">Status:</span>
            <span className={`status-indicator ${metrics.status}`}>
              {metrics.status.toUpperCase()}
            </span>
          </div>
          {metrics.throughput !== undefined && (
            <div className="metric-item">
              <span className="metric-label">Throughput:</span>
              <span className="metric-value">{metrics.throughput} ops/s</span>
            </div>
          )}
          {metrics.latencyMs !== undefined && (
            <div className="metric-item">
              <span className="metric-label">Latency:</span>
              <span className="metric-value">{metrics.latencyMs}ms</span>
            </div>
          )}
          {metrics.notes && (
            <div className="metric-notes">
              <span className="notes-label">Notes:</span>
              <span className="notes-text">{metrics.notes}</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="chart-section">
        <Chart3D
          data={[
            { label: 'Redneck Ingenuity', value: cardData?.redneck_ingenuity === 'MAXIMUM' ? 1 : 0 },
            { label: 'Rapid Response', value: cardData?.rapid_response_possible ? 1 : 0 },
            { label: 'Engineering Readiness', value: cardData?.confidence || 0 }
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
