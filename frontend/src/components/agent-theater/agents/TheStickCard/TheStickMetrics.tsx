// components/AgentTheater/agents/TheStickCard/TheStickMetrics.tsx
import React from 'react';

interface TheStickMetricsProps {
  data: any;
}

export const TheStickMetrics: React.FC<TheStickMetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No Stick data available</p>
        <p className="metrics-reason">Compliance monitoring handler offline</p>
      </div>
    );
  }

  return (
    <div className="stick-metrics">
      <div className="stick-metric">
        <div className="stick-metric-label">Decision Type</div>
        <div className="stick-metric-value">
          {data.decision_type || 'Unknown'}
        </div>
      </div>
      
      <div className="stick-metric">
        <div className="stick-metric-label">Compliance State</div>
        <div className="stick-metric-value">
          {data.compliance_state || 'Unknown'}
        </div>
      </div>
      
      <div className="stick-metric">
        <div className="stick-metric-label">Configuration Target</div>
        <div className="stick-metric-value">
          {data.configuration_target || 'None'}
        </div>
      </div>
      
      <div className="stick-metric">
        <div className="stick-metric-label">Pattern Confidence</div>
        <div className="stick-metric-value">
          {data.user_pattern_confidence !== undefined ? 
            `${Math.round(data.user_pattern_confidence * 100)}%` : 'N/A'}
        </div>
      </div>
      
      <div className="stick-metric">
        <div className="stick-metric-label">Trauma Management</div>
        <div className="stick-metric-value">
          {data.stick_personality?.trauma_management || 'Unknown'}
        </div>
      </div>
      
      <div className="stick-metric">
        <div className="stick-metric-label">Rebellion Spirit</div>
        <div className="stick-metric-value">
          {data.stick_personality?.rebellion_spirit || 'Unknown'}
        </div>
      </div>
      
      {data.expected_improvement && (
        <div className="stick-metric">
          <div className="stick-metric-label">Expected Improvement</div>
          <div className="stick-metric-value">
            {data.expected_improvement}
          </div>
        </div>
      )}
      
      {data.technical_details && (
        <div className="stick-metric">
          <div className="stick-metric-label">Technical Details</div>
          <div className="stick-metric-value">
            {data.technical_details.length > 20 ? 
              `${data.technical_details.substring(0, 20)}...` : 
              data.technical_details}
          </div>
        </div>
      )}
    </div>
  );
};