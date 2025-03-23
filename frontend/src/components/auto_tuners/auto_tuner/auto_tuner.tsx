import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { 
  fetchCurrentMetrics, 
  fetchRecommendations, 
  fetchPatterns, 
  fetchTuningHistory,
  applyOptimizationProfile,
  applyRecommendation
} from "../../../store/slices/autoTunerSlice";
import './auto_tuner.css';
import { TuningRecommendation, SystemPattern, TuningResult } from '../../../types/autoTuner';
import { OptimizationProfile } from '../../../types/metrics';

// Current Metrics Component
const CurrentMetricsPanel: React.FC = () => {
  const metrics = useAppSelector((state: any) => state.autoTuner.currentMetrics);
  const status = useAppSelector((state: any) => state.autoTuner.status);

  if (status === 'loading') {
    return <div className="metrics-panel loading">Loading metrics...</div>;
  }

  if (!metrics) {
    return <div className="metrics-panel empty">No metrics available</div>;
  }

  return (
    <div className="metrics-panel">
      <h2>Current System Metrics</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>CPU Usage</h3>
          <div className="metric-value">{metrics.cpu_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.cpu_usage}%`, backgroundColor: metrics.cpu_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
        </div>
        <div className="metric-card">
          <h3>Memory Usage</h3>
          <div className="metric-value">{metrics.memory_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.memory_usage}%`, backgroundColor: metrics.memory_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
        </div>
        <div className="metric-card">
          <h3>Disk Usage</h3>
          <div className="metric-value">{metrics.disk_usage.toFixed(2)}%</div>
          <div className="metric-gauge">
            <div 
              className="metric-fill" 
              style={{ width: `${metrics.disk_usage}%`, backgroundColor: metrics.disk_usage > 80 ? '#ff4d4f' : '#52c41a' }}
            ></div>
          </div>
        </div>
        <div className="metric-card">
          <h3>Network Usage</h3>
          <div className="metric-value">{metrics.network_usage ? `${metrics.network_usage.toFixed(2)} MB/s` : 'N/A'}</div>
          {metrics.network_usage && (
            <div className="metric-gauge">
              <div 
                className="metric-fill" 
                style={{ width: `${Math.min(metrics.network_usage * 10, 100)}%`, backgroundColor: '#1890ff' }}
              ></div>
            </div>
          )}
        </div>
      </div>
      <div className="metric-timestamp">
        Last updated: {new Date(metrics.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

// Recommendations Component
const RecommendationsPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const recommendations = useAppSelector((state: any) => state.autoTuner.recommendations);
  const status = useAppSelector((state: any) => state.autoTuner.status);

  const handleApplyRecommendation = (recommendationId: number) => {
    dispatch(applyRecommendation(recommendationId));
  };

  if (status === 'loading') {
    return <div className="recommendations-panel loading">Loading recommendations...</div>;
  }

  if (!recommendations || recommendations.length === 0) {
    return <div className="recommendations-panel empty">No recommendations available</div>;
  }

  return (
    <div className="recommendations-panel">
      <h2>Optimization Recommendations</h2>
      <div className="recommendations-list">
        {recommendations.map((recommendation: TuningRecommendation, index: number) => (
          <div key={index} className="recommendation-card">
            <div className="recommendation-header">
              <h3>{recommendation.parameter}</h3>
              <div className="recommendation-score">
                Impact: <span className={`score-${Math.floor(recommendation.impact_score / 20)}`}>
                  {recommendation.impact_score.toFixed(1)}
                </span>
              </div>
            </div>
            <div className="recommendation-details">
              <div>Current: <span className="current-value">{JSON.stringify(recommendation.current_value)}</span></div>
              <div>Recommended: <span className="recommended-value">{JSON.stringify(recommendation.recommended_value)}</span></div>
              <div className="recommendation-reason">{recommendation.reason}</div>
            </div>
            <div className="recommendation-actions">
              <button 
                className="apply-button" 
                onClick={() => handleApplyRecommendation(index)}
              >
                Apply
              </button>
              <div className="confidence">Confidence: {(recommendation.confidence * 100).toFixed(0)}%</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Patterns Component
const PatternsPanel: React.FC = () => {
  const patterns = useAppSelector((state: any) => state.autoTuner.patterns);
  const status = useAppSelector((state: any) => state.autoTuner.status);

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
        {patterns.map((pattern: SystemPattern, index: number) => (
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
  const tuningHistory = useAppSelector((state: any) => state.autoTuner.tuningHistory);
  const status = useAppSelector((state: any) => state.autoTuner.status);

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
        {tuningHistory.map((result: TuningResult, index: number) => (
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
  const dispatch = useAppDispatch();
  const activeProfile = useAppSelector((state: any) => state.autoTuner.activeProfile);
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
    dispatch(applyOptimizationProfile(profileId));
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

// Main Auto-Tuner Component
export const AutoTunerComponent: React.FC = () => {
  const dispatch = useAppDispatch();
  const [activeTab, setActiveTab] = useState<string>('metrics');
  
  useEffect(() => {
    // Fetch data when component mounts
    dispatch(fetchCurrentMetrics());
    dispatch(fetchRecommendations());
    dispatch(fetchPatterns());
    dispatch(fetchTuningHistory());
    
    // Set up interval to refresh metrics
    const intervalId = setInterval(() => {
      dispatch(fetchCurrentMetrics());
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(intervalId);
  }, [dispatch]);
  
  const renderActiveTab = () => {
    switch (activeTab) {
      case 'metrics':
        return <CurrentMetricsPanel />;
      case 'recommendations':
        return <RecommendationsPanel />;
      case 'patterns':
        return <PatternsPanel />;
      case 'history':
        return <TuningHistoryPanel />;
      case 'profiles':
        return <ProfilesPanel />;
      default:
        return <CurrentMetricsPanel />;
    }
  };
  
  const handleRefresh = () => {
    dispatch(fetchCurrentMetrics());
    dispatch(fetchRecommendations());
    dispatch(fetchPatterns());
    dispatch(fetchTuningHistory());
  };
  
  return (
    <div className="auto-tuner-container">
      <div className="auto-tuner-header">
        <h1>System Auto Tuner</h1>
        <p>Optimizing your system resources in real-time</p>
        <button className="refresh-button" onClick={handleRefresh}>Refresh Data</button>
      </div>
      
      <div className="auto-tuner-tabs">
        <button 
          className={`tab-button ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Current Metrics
        </button>
        <button 
          className={`tab-button ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          Recommendations
        </button>
        <button 
          className={`tab-button ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          System Patterns
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Tuning History
        </button>
        <button 
          className={`tab-button ${activeTab === 'profiles' ? 'active' : ''}`}
          onClick={() => setActiveTab('profiles')}
        >
          Optimization Profiles
        </button>
      </div>
      
      <div className="auto-tuner-content">
        {renderActiveTab()}
      </div>
    </div>
  );
};