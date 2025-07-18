// components/AgentTheater/agents/QuantumShadowCard/QuantumShadowMetrics.tsx
import React from 'react';

interface QuantumShadowMetricsProps {
  data: any;
}

export const QuantumShadowMetrics: React.FC<QuantumShadowMetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No Quantum Shadow People data available</p>
        <p className="metrics-reason">Interdimensional connection severed</p>
      </div>
    );
  }

  return (
    <div className="qsp-metrics">
      <div className="qsp-metric">
        <div className="qsp-metric-label">Quantum State</div>
        <div className="qsp-metric-value">
          {data.quantum_state || 'Unknown'}
        </div>
      </div>
      
      <div className="qsp-metric">
        <div className="qsp-metric-label">Network Target</div>
        <div className="qsp-metric-value">
          {data.network_target || 'None'}
        </div>
      </div>
      
      <div className="qsp-metric">
        <div className="qsp-metric-label">Tequila Jello Shots</div>
        <div className="qsp-metric-value">
          {data.tequila_jello_shots_required !== undefined ? 
            data.tequila_jello_shots_required : 'N/A'}
        </div>
      </div>
      
      <div className="qsp-metric">
        <div className="qsp-metric-label">Expected Improvement</div>
        <div className="qsp-metric-value">
          {data.expected_improvement || 'Unknown'}
        </div>
      </div>
      
      <div className="qsp-metric">
        <div className="qsp-metric-label">Technical Details</div>
        <div className="qsp-metric-value">
          {data.technical_details ? 'Available' : 'None'}
        </div>
      </div>
      
      {data.quantum_icon && (
        <div className="qsp-metric">
          <div className="qsp-metric-label">Quantum Icon</div>
          <div className="qsp-metric-value">
            {data.quantum_icon}
          </div>
        </div>
      )}
      
      {data.status && (
        <div className="qsp-metric">
          <div className="qsp-metric-label">Status</div>
          <div className="qsp-metric-value">
            {data.status}
          </div>
        </div>
      )}
    </div>
  );
};