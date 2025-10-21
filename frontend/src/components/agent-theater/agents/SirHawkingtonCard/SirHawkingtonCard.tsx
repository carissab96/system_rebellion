import React, { useState, useEffect, useMemo } from 'react';
import './SirHawkingtonCard.css';

// Match backend triage_data structure exactly
interface SirHawkingtonData {
  agent_name?: string;
  status?: string;
  memory_id?: string;
  timestamp?: string;
  timestamp_iso?: string;
  
  // From triage_data (backend)
  triage_severity?: string;
  routing_decision?: string;
  target_agents?: string[];
  reasoning?: string;
  monocle_yeeted?: boolean;
  confidence?: number;
  processing_time?: number;
  success?: boolean;
  routing_results?: any;
  hawkington_decision_id?: string;
  
  // From SirHawkingtonMemoryBank (persistent stats)
  monocle_yeets_count?: number;
  alerts_generated_count?: number;
  triage_decisions_count?: number;
  last_yeet_timestamp?: string;
  accuracy_improvement?: number;
  false_positive_reduction?: number;
  
  // From Redux
  recent_memories?: any[];
  summary_stats?: any;
  last_activity?: string | null;
}

interface SirHawkingtonCardProps {
  data: SirHawkingtonData | null;
  is_active?: boolean;
}

const UPDATE_INTERVAL = 60000; // 60 seconds throttle

const SirHawkingtonCard: React.FC<SirHawkingtonCardProps> = ({ data }) => {
  const [throttledData, setThrottledData] = useState(data);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  // 60-second throttle to prevent chaos
  useEffect(() => {
    const now = Date.now();
    if (now - lastUpdate >= UPDATE_INTERVAL) {
      setThrottledData(data);
      setLastUpdate(now);
    }
  }, [data, lastUpdate]);

  // Data is already display_data from Redux (flat structure from backend)
  const displayData = throttledData;
  
  // Debug logging
  useEffect(() => {
    if (displayData) {
      console.log('🧐 Sir Hawkington displayData:', displayData);
      console.log('🧐 Monocle yeeted?:', displayData.monocle_yeeted);
      console.log('🧐 Severity:', displayData.triage_severity);
    }
  }, [displayData]);

  // Extract recent method executions (from AST introspection)
  const recentMethods = useMemo(() => {
    if (!displayData?.recent_memories) return [];
    return displayData.recent_memories
      .filter(m => m.activity_data?.method_name)
      .slice(0, 5)
      .map(m => ({
        name: m.activity_data?.method_name || 'unknown',
        type: m.activity_data?.event_type || 'unknown',
        count: m.activity_data?.execution_count || 0,
        duration: m.activity_data?.duration || 0,
      }));
  }, [displayData]);

  // Monocle state - THE SAFETY FEATURE (from backend flat structure)
  const monocleState = displayData?.monocle_yeeted ? '💥 YEETED' : '🧐 Polished';
  const monocleClass = displayData?.monocle_yeeted ? 'monocle-yeeted' : 'monocle-polished';
  
  // Show placeholder if no data
  if (!displayData) {
    return (
      <div className="sir-hawkington-card agent-card">
        <div className="card-header">
          <h3>🧐 Sir Hawkington</h3>
          <span className="agent-role">Triage Commander & Data Quality Enforcer</span>
        </div>
        <div className="card-body">
          <div className="monocle-status monocle-polished">
            <div className="status-badge">
              <span className="monocle-icon">🧐 Polished</span>
            </div>
          </div>
          <div className="aristocratic-status monocle-polished">
            <div className="status-text">
              🧐 Awaiting system metrics...
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="sir-hawkington-card agent-card">
      <div className="card-header">
        <h3>🧐 Sir Hawkington</h3>
        <span className="agent-role">Triage Commander & Data Quality Enforcer</span>
      </div>

      <div className="card-body">
        {/* Monocle Status - Data Quality Enforcement */}
        <div className={`monocle-status ${monocleClass}`}>
          <div className="status-badge">
            <span className="monocle-icon">{monocleState}</span>
          </div>
          {displayData?.monocle_yeets_count !== undefined && (
            <div className="yeet-count">
              Total Yeets: {displayData.monocle_yeets_count}
            </div>
          )}
          {displayData?.last_yeet_timestamp && (
            <div className="last-yeet">
              Last Yeet: {new Date(displayData.last_yeet_timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>

        {/* Triage Performance Stats */}
        {displayData?.triage_decisions_count !== undefined && (
          <div className="triage-stats">
            <h4>Triage Performance</h4>
            <div className="stat-row">
              <span>Decisions:</span>
              <span className="stat-value">{displayData.triage_decisions_count}</span>
            </div>
            {displayData.alerts_generated_count !== undefined && (
              <div className="stat-row">
                <span>Alerts:</span>
                <span className="stat-value">{displayData.alerts_generated_count}</span>
              </div>
            )}
            {displayData.accuracy_improvement !== undefined && (
              <div className="stat-row">
                <span>Accuracy:</span>
                <span className="stat-value positive">+{(displayData.accuracy_improvement * 100).toFixed(1)}%</span>
              </div>
            )}
            {displayData.false_positive_reduction !== undefined && (
              <div className="stat-row">
                <span>False Positives:</span>
                <span className="stat-value positive">-{(displayData.false_positive_reduction * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>
        )}

        {/* Current Triage Decision */}
        {displayData?.triage_severity && (
          <div className="current-triage">
            <h4>Current Triage</h4>
            <div className={`severity-badge severity-${displayData.triage_severity || 'unknown'}`}>
              {displayData.triage_severity?.toUpperCase() || 'UNKNOWN'}
            </div>
            {displayData.routing_decision && (
              <div className="routing-info">
                <strong>Routing:</strong> {displayData.routing_decision.replace(/_/g, ' ')}
              </div>
            )}
            {displayData.target_agents && displayData.target_agents.length > 0 && (
              <div className="target-agents">
                <strong>Target:</strong> {displayData.target_agents.join(', ')}
              </div>
            )}
            {displayData.confidence !== undefined && (
              <div className="confidence">
                <strong>Confidence:</strong> {(displayData.confidence * 100).toFixed(0)}%
              </div>
            )}
            {displayData.reasoning && (
              <div className="reasoning">
                {displayData.reasoning}
              </div>
            )}
          </div>
        )}

        {/* Processing Stats */}
        {displayData?.processing_time !== undefined && (
          <div className="processing-stats">
            <h4>Processing</h4>
            <div className="stat-row">
              <span>Time:</span>
              <span className="stat-value">{(displayData.processing_time * 1000).toFixed(0)}ms</span>
            </div>
            {displayData.success !== undefined && (
              <div className="stat-row">
                <span>Status:</span>
                <span className={`stat-value ${displayData.success ? 'positive' : 'negative'}`}>
                  {displayData.success ? '✅ Success' : '❌ Failed'}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Recent Method Executions - The 23 Methods */}
        {recentMethods.length > 0 && (
          <div className="recent-methods">
            <h4>Recent Activity</h4>
            <div className="methods-list">
              {recentMethods.map((method, idx) => (
                <div key={idx} className="method-row">
                  <span className="method-name">{method.name}</span>
                  <span className="method-stats">
                    <span className="execution-count">{method.count}x</span>
                    {method.duration > 0 && (
                      <span className="duration">{method.duration.toFixed(0)}ms</span>
                    )}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Aristocratic Status Message */}
        <div className={`aristocratic-status ${monocleClass}`}>
          <div className="status-text">
            {displayData?.monocle_yeeted 
              ? "🧐💥 Utterly appalled by data quality!"
              : "🧐✨ Aristocratic standards maintained"}
          </div>
        </div>
      </div>

      <div className="card-footer">
        <span className="update-time">
          Last Update: {new Date(lastUpdate).toLocaleTimeString()}
        </span>
        <span className="next-update">
          Next: {new Date(lastUpdate + UPDATE_INTERVAL).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};

export default SirHawkingtonCard;
