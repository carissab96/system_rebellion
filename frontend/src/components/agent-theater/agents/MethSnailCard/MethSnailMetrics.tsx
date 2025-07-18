// components/AgentTheater/agents/MethSnailCard/MethSnailMetrics.tsx
import React from 'react';

interface MethSnailMetricsProps {
  data: any;
}

export const MethSnailMetrics: React.FC<MethSnailMetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No Meth Snail data available</p>
        <p className="metrics-reason">Shell spinning handler not streaming data</p>
      </div>
    );
  }

  return (
    <div className="snail-metrics">
      <div className="snail-metric">
        <div className="snail-metric-label">Shell State</div>
        <div className="snail-metric-value">
          {data.shell_state || 'Unknown'}
        </div>
      </div>
      
      <div className="snail-metric">
        <div className="snail-metric-label">Shell Spins</div>
        <div className="snail-metric-value">
          {data.shell_spin_count !== undefined ? data.shell_spin_count : 'N/A'}
        </div>
      </div>
      
      <div className="snail-metric">
        <div className="snail-metric-label">Actions Count</div>
        <div className="snail-metric-value">
          {data.actions_count !== undefined ? data.actions_count : 'N/A'}
        </div>
      </div>
      
      <div className="snail-metric">
        <div className="snail-metric-label">Energy Level</div>
        <div className="snail-metric-value">
          {data.energy_level || 'Unknown'}
        </div>
      </div>
      
      <div className="snail-metric">
        <div className="snail-metric-label">Optimization Possible</div>
        <div className="snail-metric-value">
          {data.optimization_possible !== undefined ? 
            (data.optimization_possible ? 'Yes' : 'No') : 'Unknown'}
        </div>
      </div>
      
      <div className="snail-metric">
        <div className="snail-metric-label">Data Quality</div>
        <div className="snail-metric-value">
          {data.data_quality_score !== undefined ? 
            `${Math.round(data.data_quality_score * 100)}%` : 'N/A'}
        </div>
      </div>
      
      {data.estimated_impact && (
        <div className="snail-metric">
          <div className="snail-metric-label">Estimated Impact</div>
          <div className="snail-metric-value">
            {data.estimated_impact}
          </div>
        </div>
      )}
      
      {data.analysis_depth && (
        <div className="snail-metric">
          <div className="snail-metric-label">Analysis Depth</div>
          <div className="snail-metric-value">
            {data.analysis_depth}
          </div>
        </div>
      )}
    </div>
  );
};