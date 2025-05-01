import React, { useEffect, useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../../store/store';
import {
  fetchCurrentMetrics,
  fetchRecommendations,
  fetchPatterns,
  fetchTuningHistory,
  applyRecommendation,
  applyOptimizationProfile,
  setActiveProfile
} from '../../../store/slices/autoTunerSlice';
import { AppDispatch } from '../../../store/store';
import { OptimizationProfile } from '../../../types/metrics';
import { ParameterDescription, AutoTunerHelp } from './parameter_descriptions';
import SystemLogsViewer from '../../dashboard/SystemLogs/SystemLogsViewer';
import './auto_tuner.css';

// Current Metrics Component
const CurrentMetricsPanel: React.FC = () => {
  const metrics = useSelector((state: RootState) => state.autoTuner.currentMetrics);
  const status = useSelector((state: RootState) => state.autoTuner.status);
  const [isUpdating, setIsUpdating] = useState(false);
  const prevMetricsRef = useRef(metrics);

  // Detect when metrics change to trigger smooth update animation
  useEffect(() => {
    if (metrics && prevMetricsRef.current && JSON.stringify(metrics) !== JSON.stringify(prevMetricsRef.current)) {
      setIsUpdating(true);
      const timer = setTimeout(() => setIsUpdating(false), 1000);
      return () => clearTimeout(timer);
    }
    prevMetricsRef.current = metrics;
  }, [metrics]);

  if (status === 'loading' && !metrics) {
    return <div className="metrics-panel loading">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="metrics-panel empty">No metrics available</div>;
  }

  return (
    <div className={`metrics-panel ${isUpdating ? 'data-updating' : ''}`}>
      <h2>Current System Metrics</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>CPU Usage</h3>
          <div className="metric-value" key={`cpu-${metrics.cpu_usage}`}>{metrics.cpu_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.cpu_usage}%`, backgroundColor: metrics.cpu_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
          <div className="help-text">
            <small title="The percentage of CPU usage">CPU usage is the percentage of CPU resources being used.</small>
          </div>
        </div>
        <div className="metric-card">
          <h3>Memory Usage</h3>
          <div className="metric-value" key={`memory-${metrics.memory_usage}`}>{metrics.memory_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.memory_usage}%`, backgroundColor: metrics.memory_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
          <div className="help-text">
            <small title="The percentage of memory usage">Memory usage is the percentage of memory resources being used.</small>
          </div>
        </div>
        <div className="metric-card">
          <h3>Disk Usage</h3>
          <div className="metric-value" key={`disk-${metrics.disk_usage}`}>{metrics.disk_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.disk_usage}%`, backgroundColor: metrics.disk_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
          <div className="help-text">
            <small title="The percentage of disk usage">Disk usage is the percentage of disk resources being used.</small>
          </div>
        </div>
        <div className="metric-card">
          <h3>Network Usage</h3>
          <div className="metric-value" key={`network-${metrics.network_usage || 0}`}>{metrics.network_usage ? `${metrics.network_usage.toFixed(2)} MB/s` : 'N/A'}</div>
          {metrics.network_usage && (
            <div className="metric-gauge">
              <div 
                className="metric-fill" 
                style={{ width: `${Math.min(metrics.network_usage * 10, 100)}%`, backgroundColor: '#1890ff' }}
              ></div>
            </div>
          )}
          <div className="help-text">
            <small title="The amount of network usage in MB/s">Network usage is the amount of network resources being used.</small>
          </div>
        </div>
      </div>
      <div className="metric-timestamp">
        Last updated: {new Date(metrics.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

// Recommendations Panel
const RecommendationsPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { recommendations, status, error } = useSelector((state: RootState) => state.autoTuner);
  const [selectedParameter, setSelectedParameter] = useState<string | null>(null);

  const handleApplyRecommendation = (recommendationId: number) => {
    dispatch(applyRecommendation(recommendationId));
  };

  const toggleParameterDescription = (parameter: string) => {
    if (selectedParameter === parameter) {
      setSelectedParameter(null);
    } else {
      setSelectedParameter(parameter);
    }
  };

  return (
    <div className="panel recommendations-panel">
      <h3>Tuning Recommendations</h3>
      <div className="help-text">
        <small>Click on any parameter name to see detailed information about what it means.</small>
      </div>
      {status === 'loading' && <p>Loading recommendations...</p>}
      {error && <p className="error">Error: {error}</p>}
      {recommendations.length === 0 ? (
        <p>No recommendations available at this time.</p>
      ) : (
        <ul className="recommendations-list">
          {recommendations.map((recommendation, index) => (
            <li key={index} className="recommendation-item">
              <div className="recommendation-header">
                <span 
                  className="parameter clickable" 
                  onClick={() => toggleParameterDescription(recommendation.parameter)}
                  title="Click for more information"
                >
                  {recommendation.parameter}
                </span>
                <div className="scores">
                  <span className="impact-score" title="How significant this change will be (0.0-1.0)">
                    Impact: {recommendation.impact_score.toFixed(2)}
                  </span>
                  <span className="confidence" title="How certain the system is about this recommendation">
                    Confidence: {(recommendation.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              {selectedParameter === recommendation.parameter && (
                <div className="parameter-info">
                  <ParameterDescription parameter={recommendation.parameter} />
                </div>
              )}
              
              <div className="recommendation-details">
                <div className="values">
                  <span className="current-value" title="The current setting on your system">Current: {recommendation.current_value}</span>
                  <span className="recommended-value" title="The recommended optimal setting">Recommended: {recommendation.recommended_value}</span>
                </div>
                <p className="reason">{recommendation.reason}</p>
                <button 
                  className="apply-button" 
                  onClick={() => handleApplyRecommendation(index)}
                  title="Apply this recommendation to your system"
                >
                  Apply
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

// Patterns Component
const PatternsPanel: React.FC = () => {
  const patterns = useSelector((state: RootState) => state.autoTuner.patterns);
  const status = useSelector((state: RootState) => state.autoTuner.status);

  if (status === 'loading') {
    return <div className="patterns-panel loading">Loading patterns...</div>;
  }

  if (!patterns || patterns.length === 0) {
    return <div className="patterns-panel empty">No patterns detected</div>;
  }

  return (
    <div className="patterns-panel">
      <h2>Detected System Patterns</h2>
      <div className="patterns-list">
        {patterns.map((pattern, index) => (
          <div key={index} className="pattern-card">
            <div className="pattern-header">
              <h3>{pattern.type}</h3>
              <div className="pattern-confidence">
                Confidence: {(pattern.confidence * 100).toFixed(0)}%
              </div>
            </div>
            <div className="pattern-details">
              <div className="pattern-description">{pattern.pattern}</div>
              <div className="pattern-info">
                {Object.entries(pattern.details).map(([key, value]) => (
                  <div key={key} className="pattern-detail-item">
                    <span className="detail-key">{key}:</span> {JSON.stringify(value)}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Tuning History Component
const TuningHistoryPanel: React.FC = () => {
  const tuningHistory = useSelector((state: RootState) => state.autoTuner.tuningHistory);
  const status = useSelector((state: RootState) => state.autoTuner.status);

  if (status === 'loading') {
    return <div className="history-panel loading">Loading tuning history...</div>;
  }

  if (!tuningHistory || tuningHistory.length === 0) {
    return <div className="history-panel empty">No tuning history available</div>;
  }

  return (
    <div className="history-panel">
      <h2>Optimization History</h2>
      <div className="history-list">
        {tuningHistory.map((result, index) => (
          <div key={index} className={`history-card ${result.success ? 'success' : 'failure'}`}>
            <div className="history-header">
              <h3>{result.parameter}</h3>
              <div className="history-status">
                {result.success ? '✓ Success' : '✗ Failed'}
              </div>
            </div>
            {result.metrics_before && result.metrics_after && (
              <div className="history-metrics">
                <div className="metrics-before">
                  <h4>Before</h4>
                  <pre>{JSON.stringify(result.metrics_before, null, 2)}</pre>
                </div>
                <div className="metrics-after">
                  <h4>After</h4>
                  <pre>{JSON.stringify(result.metrics_after, null, 2)}</pre>
                </div>
              </div>
            )}
            {result.error && (
              <div className="history-error">
                Error: {result.error}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Profiles Component
const ProfilesPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const activeProfile = useSelector((state: RootState) => state.autoTuner.activeProfile);
  const [profiles, setProfiles] = useState<OptimizationProfile[]>([]);
  
  // In a real implementation, we would fetch profiles from the API
  useEffect(() => {
    // This is a placeholder. In a real app, you'd fetch from the API
    const dummyProfiles: OptimizationProfile[] = [
      {
        id: '1',
        name: 'Performance Mode',
        description: 'Optimize for maximum performance',
        thresholds: { cpu: 90, memory: 90, disk: 90, network: 90 },
        actions: ['increase_cpu_priority', 'optimize_memory']
      },
      {
        id: '2',
        name: 'Power Saving Mode',
        description: 'Optimize for battery life',
        thresholds: { cpu: 60, memory: 70, disk: 80, network: 50 },
        actions: ['reduce_cpu_usage', 'limit_background_processes']
      },
      {
        id: '3',
        name: 'Balanced Mode',
        description: 'Balance between performance and power saving',
        thresholds: { cpu: 75, memory: 80, disk: 85, network: 70 },
        actions: ['moderate_cpu_usage', 'optimize_memory']
      }
    ];
    setProfiles(dummyProfiles);
  }, []);

  const handleApplyProfile = (profileId: string) => {
    // Find the profile to set as active
    const profileToApply = profiles.find(p => p.id === profileId);
    if (profileToApply) {
      // Set the profile as active in the Redux store
      dispatch(setActiveProfile(profileToApply));
      // Apply the profile settings
      dispatch(applyOptimizationProfile(profileId));
    }
  };

  return (
    <div className="profiles-panel">
      <h2>Optimization Profiles</h2>
      <div className="profiles-list">
        {profiles.map((profile) => (
          <div key={profile.id} className={`profile-card ${activeProfile?.id === profile.id ? 'active' : ''}`}>
            <div className="profile-header">
              <h3>{profile.name}</h3>
              {activeProfile?.id === profile.id && (
                <div className="active-badge">Active</div>
              )}
            </div>
            <div className="profile-description">{profile.description}</div>
            <div className="profile-thresholds">
              <h4>Thresholds</h4>
              <div className="thresholds-grid">
                <div>CPU: {profile.thresholds.cpu}%</div>
                <div>Memory: {profile.thresholds.memory}%</div>
                <div>Disk: {profile.thresholds.disk}%</div>
                <div>Network: {profile.thresholds.network}%</div>
              </div>
            </div>
            <div className="profile-actions">
              <button 
                className="apply-button" 
                onClick={() => handleApplyProfile(profile.id)}
                disabled={activeProfile?.id === profile.id}
              >
                {activeProfile?.id === profile.id ? 'Applied' : 'Apply'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// System Logs Panel Component
const SystemLogsPanel: React.FC = () => {
  return (
    <div className="system-logs-panel">
      <SystemLogsViewer 
        title="System Activity Logs" 
        maxHeight={400} 
        autoRefresh={true}
        refreshInterval={10000}
      />
    </div>
  );
};

// Main Auto-Tuner Component
export const AutoTuner: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { lastUpdated } = useSelector((state: RootState) => state.autoTuner);
  const [showHelp, setShowHelp] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const lastUpdatedRef = useRef(lastUpdated);
  
  // Detect when data updates to trigger animation
  useEffect(() => {
    if (lastUpdated && lastUpdatedRef.current !== lastUpdated) {
      setIsUpdating(true);
      const timer = setTimeout(() => setIsUpdating(false), 1000);
      return () => clearTimeout(timer);
    }
    lastUpdatedRef.current = lastUpdated;
  }, [lastUpdated]);

  useEffect(() => {
    // Fetch initial data
    dispatch(fetchCurrentMetrics());
    dispatch(fetchRecommendations());
    dispatch(fetchPatterns());
    dispatch(fetchTuningHistory());

    // Set up polling for metrics and recommendations
    const pollingInterval = setInterval(() => {
      dispatch(fetchCurrentMetrics());
      dispatch(fetchRecommendations());
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(pollingInterval);
  }, [dispatch]);

  return (
    <div className={`auto-tuner-container ${isUpdating ? 'data-updating' : ''}`}>
      <div className="auto-tuner-header">
        <h2>System Auto-Tuner</h2>
        <button 
          className="help-button" 
          onClick={() => setShowHelp(!showHelp)}
          title="Learn about auto-tuner values"
        >
          {showHelp ? 'Hide Help' : 'What do these values mean?'}
        </button>
        {lastUpdated && (
          <div className="last-updated">
            Last updated: {new Date(lastUpdated).toLocaleTimeString()}
          </div>
        )}
      </div>
      
      {showHelp && (
        <div className="help-panel">
          <AutoTunerHelp />
        </div>
      )}
      
      <div className="auto-tuner-panels">
        <div className="panel-row">
          <CurrentMetricsPanel />
          <RecommendationsPanel />
        </div>
        <div className="panel-row">
          <PatternsPanel />
          <TuningHistoryPanel />
        </div>
        <div className="panel-row">
          <ProfilesPanel />
        </div>
        <div className="panel-row">
          <SystemLogsPanel />
        </div>
      </div>
    </div>
  );
};