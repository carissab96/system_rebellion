// components/AgentTheater/agents/HamstersCard/HamstersMetrics.tsx
import React from 'react';

interface HamstersMetricsProps {
  data: any;
}

export const HamstersMetrics: React.FC<HamstersMetricsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="metrics-unavailable">
        <p className="metrics-error">No Hamsters data available</p>
        <p className="metrics-reason">Engineering team handler not streaming data</p>
      </div>
    );
  }

  return (
    <div className="hamsters-metrics">
      <div className="hamster-metric">
        <div className="hamster-metric-label">Wheel State</div>
        <div className="hamster-metric-value">
          {data.wheel_state || 'Unknown'}
        </div>
      </div>
      
      <div className="hamster-metric">
        <div className="hamster-metric-label">Wheel Spins</div>
        <div className="hamster-metric-value">
          {data.wheel_spin_count !== undefined ? data.wheel_spin_count : 'N/A'}
        </div>
      </div>
      
      <div className="hamster-metric">
        <div className="hamster-metric-label">Actions Count</div>
        <div className="hamster-metric-value">
          {data.actions_count !== undefined ? data.actions_count : 'N/A'}
        </div>
      </div>
      
      <div className="hamster-metric">
        <div className="hamster-metric-label">Redneck Ingenuity</div>
        <div className="hamster-metric-value">
          {data.redneck_ingenuity || 'Unknown'}
        </div>
      </div>
      
      <div className="hamster-metric">
        <div className="hamster-metric-label">Supply Closet</div>
        <div className="hamster-metric-value">
          {data.supply_closet_status || 'Unknown'}
        </div>
      </div>
      
      <div className="hamster-metric">
        <div className="hamster-metric-label">Data Quality</div>
        <div className="hamster-metric-value">
          {data.data_quality_score !== undefined ? 
            `${Math.round(data.data_quality_score * 100)}%` : 'N/A'}
        </div>
      </div>
      
      {data.estimated_impact && (
        <div className="hamster-metric">
          <div className="hamster-metric-label">Estimated Impact</div>
          <div className="hamster-metric-value">
            {data.estimated_impact}
          </div>
        </div>
      )}
      
      {data.analysis_depth && (
        <div className="hamster-metric">
          <div className="hamster-metric-label">Analysis Depth</div>
          <div className="hamster-metric-value">
            {data.analysis_depth}
          </div>
        </div>
      )}
    </div>
  );
};