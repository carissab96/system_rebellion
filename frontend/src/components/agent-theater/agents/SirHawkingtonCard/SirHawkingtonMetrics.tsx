// components/AgentTheater/agents/SirHawkingtonCard/SirHawkingtonMetrics.tsx
import React from 'react';

interface SirHawkingtonMetricsProps {
  data: any;
}

export const SirHawkingtonMetrics: React.FC<SirHawkingtonMetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No Sir Hawkington data available</p>
        <p className="metrics-reason">WebSocket handler not streaming data</p>
      </div>
    );
  }

  return (
    <div className="hawkington-metrics">
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Monocle State</div>
        <div className="hawkington-metric-value">
          {data.monocle_state || 'Unknown'}
        </div>
      </div>
      
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Monocle Yeets</div>
        <div className="hawkington-metric-value">
          {data.monocle_yeet_count !== undefined ? data.monocle_yeet_count : 'N/A'}
        </div>
      </div>
      
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Data Quality</div>
        <div className="hawkington-metric-value">
          {data.data_quality_score !== undefined ? 
            `${Math.round(data.data_quality_score * 100)}%` : 'N/A'}
        </div>
      </div>
      
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Stress Level</div>
        <div className="hawkington-metric-value">
          {data.stress_score !== undefined ? 
            `${Math.round(data.stress_score * 100)}%` : 'N/A'}
        </div>
      </div>
      
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Urgency</div>
        <div className="hawkington-metric-value">
          {data.urgency || 'Unknown'}
        </div>
      </div>
      
      <div className="hawkington-metric">
        <div className="hawkington-metric-label">Aristocratic Seal</div>
        <div className="hawkington-metric-value">
          {data.aristocratic_seal !== undefined ? 
            (data.aristocratic_seal ? 'Authentic' : 'Compromised') : 'Unknown'}
        </div>
      </div>
      
      {data.analysis_depth && (
        <div className="hawkington-metric">
          <div className="hawkington-metric-label">Analysis Depth</div>
          <div className="hawkington-metric-value">
            {data.analysis_depth}
          </div>
        </div>
      )}
      
      {data.estimated_impact && (
        <div className="hawkington-metric">
          <div className="hawkington-metric-label">Estimated Impact</div>
          <div className="hawkington-metric-value">
            {data.estimated_impact}
          </div>
        </div>
      )}
    </div>
  );
};