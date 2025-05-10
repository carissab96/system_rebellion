import React from 'react';
import './NetworkMetrics.css';


export interface QualityData {
  overall_score?: number;
  latency?: {
    avg_ms?: number;
    min_ms?: number;
    max_ms?: number;
    jitter_ms?: number;
    stability_score?: number;
  };
  packet_loss?: {
    percentage?: number;
    trend?: 'improving' | 'stable' | 'degrading';
    history?: number[];
  };
  connection_stability?: {
    score?: number;
    drops_last_hour?: number;
    reconnects?: number;
  };
}

export interface DNSMetrics {
  query_time_ms?: number;
  success_rate?: number;
  cache_hit_ratio?: number;
  last_failures?: number;
}

export interface InternetMetrics {
  gateway_latency_ms?: number;
  internet_latency_ms?: number;
  hop_count?: number;
  isp_performance_score?: number;
}

// Define the props type for the component
export interface NetworkQualityMetricsProps {
  qualityData: QualityData;
  dnsMetrics: DNSMetrics;
  internetMetrics: InternetMetrics;
}

const NetworkQualityMetrics: React.FC<NetworkQualityMetricsProps> = ({
  qualityData,
  dnsMetrics,
  internetMetrics
}) => {
  // Calculate quality score class
  const getQualityScoreClass = (score?: number): string => {
    if (!score && score !== 0) return 'unknown';
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 50) return 'fair';
    if (score >= 25) return 'poor';
    return 'critical';
  };
  
  // Get quality score label
  const getQualityScoreLabel = (score?: number): string => {
    if (!score && score !== 0) return 'Unknown';
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 50) return 'Fair';
    if (score >= 25) return 'Poor';
    return 'Critical';
  };
  
  // Get trend icon
  const getTrendIcon = (trend?: string): string => {
    if (!trend) return '➖';
    if (trend === 'improving') return '📈';
    if (trend === 'degrading') return '📉';
    return '➖';
  };
  
  // Calculate gauge percentage for visualization
  const calculateGaugePercentage = (score?: number): number => {
    if (!score && score !== 0) return 0;
    return Math.min(Math.max(score, 0), 100);
  };
  
  // Render gauge with cyberpunk style
  const renderGauge = (score?: number, label: string = 'Score') => {
    const percentage = calculateGaugePercentage(score);
    const scoreClass = getQualityScoreClass(score);
    
    return (
      <div className="quality-gauge">
        <div className="gauge-label">{label}</div>
        <div className="gauge-container">
          <div 
            className={`gauge-fill ${scoreClass}`} 
            style={{ width: `${percentage}%` }}
          />
          <div className="gauge-markers">
            <div className="gauge-marker" style={{ left: '25%' }}>25</div>
            <div className="gauge-marker" style={{ left: '50%' }}>50</div>
            <div className="gauge-marker" style={{ left: '75%' }}>75</div>
          </div>
        </div>
        <div className="gauge-value">
          {score !== undefined ? score : 'N/A'}
          <span className="gauge-label">{getQualityScoreLabel(score)}</span>
        </div>
      </div>
    );
  };
  
  // Render connection quality section
  const renderConnectionQuality = () => (
    <div className="quality-section">
      <h4>Connection Quality</h4>
      
      <div className="quality-overall-score">
        {renderGauge(qualityData.overall_score, 'Overall Quality')}
      </div>
      
      <div className="quality-details-grid">
        <div className="quality-detail-card">
          <div className="detail-header">Latency</div>
          <div className="detail-value">{qualityData.latency?.avg_ms || 'N/A'} ms</div>
          <div className="detail-subvalues">
            <div className="detail-subvalue">
              <span className="subvalue-label">Min:</span>
              <span className="subvalue-data">{qualityData.latency?.min_ms || 'N/A'} ms</span>
            </div>
            <div className="detail-subvalue">
              <span className="subvalue-label">Max:</span>
              <span className="subvalue-data">{qualityData.latency?.max_ms || 'N/A'} ms</span>
            </div>
            <div className="detail-subvalue">
              <span className="subvalue-label">Jitter:</span>
              <span className="subvalue-data">{qualityData.latency?.jitter_ms || 'N/A'} ms</span>
            </div>
          </div>
          {renderGauge(qualityData.latency?.stability_score, 'Stability')}
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">Packet Loss</div>
          <div className="detail-value">
            {qualityData.packet_loss?.percentage !== undefined 
              ? `${qualityData.packet_loss.percentage.toFixed(2)}%` 
              : 'N/A'}
            <span className="trend-icon">{getTrendIcon(qualityData.packet_loss?.trend)}</span>
          </div>
          <div className="detail-chart">
            {qualityData.packet_loss?.history && qualityData.packet_loss.history.length > 0 ? (
              <div className="mini-chart">
                {qualityData.packet_loss.history.map((value, index) => (
                  <div 
                    key={index} 
                    className="chart-bar" 
                    style={{ 
                      height: `${Math.min(value * 5, 100)}%`,
                      backgroundColor: value > 5 ? 'var(--danger)' : 'var(--success)'
                    }} 
                  />
                ))}
              </div>
            ) : (
              <div className="no-chart-data">No historical data</div>
            )}
          </div>
          <div className="detail-note">
            {qualityData.packet_loss?.percentage !== undefined && qualityData.packet_loss.percentage > 2 ? (
              <span className="note-warning">
                The Meth Snail is concerned about your packet loss levels.
              </span>
            ) : (
              <span>Packet loss within acceptable parameters.</span>
            )}
          </div>
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">Connection Stability</div>
          <div className="detail-value">
            {qualityData.connection_stability?.score !== undefined 
              ? qualityData.connection_stability.score 
              : 'N/A'}
          </div>
          <div className="detail-subvalues">
            <div className="detail-subvalue">
              <span className="subvalue-label">Drops (1h):</span>
              <span className="subvalue-data">{qualityData.connection_stability?.drops_last_hour || 'N/A'}</span>
            </div>
            <div className="detail-subvalue">
              <span className="subvalue-label">Reconnects:</span>
              <span className="subvalue-data">{qualityData.connection_stability?.reconnects || 'N/A'}</span>
            </div>
          </div>
          <div className="detail-note">
            {qualityData.connection_stability?.drops_last_hour !== undefined && 
             qualityData.connection_stability.drops_last_hour > 0 ? (
              <span className="note-warning">
                Sir Hawkington suggests checking your aristocratic cable connections.
              </span>
            ) : (
              <span>Connection stability is aristocratically approved.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  
  // Render DNS metrics section
  const renderDNSMetrics = () => (
    <div className="quality-section">
      <h4>DNS Performance</h4>
      
      <div className="quality-details-grid dns-grid">
        <div className="quality-detail-card">
          <div className="detail-header">Query Time</div>
          <div className="detail-value">{dnsMetrics.query_time_ms || 'N/A'} ms</div>
          <div className="detail-note">
            {dnsMetrics.query_time_ms !== undefined && dnsMetrics.query_time_ms > 100 ? (
              <span className="note-warning">
                DNS queries are slower than optimal. The Hamsters recommend checking your DNS configuration.
              </span>
            ) : (
              <span>DNS query time is within acceptable parameters.</span>
            )}
          </div>
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">Success Rate</div>
          <div className="detail-value">
            {dnsMetrics.success_rate !== undefined 
              ? `${(dnsMetrics.success_rate * 100).toFixed(1)}%` 
              : 'N/A'}
          </div>
          <div className="detail-subvalues">
            <div className="detail-subvalue">
              <span className="subvalue-label">Recent Failures:</span>
              <span className="subvalue-data">{dnsMetrics.last_failures || 'N/A'}</span>
            </div>
          </div>
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">Cache Hit Ratio</div>
          <div className="detail-value">
            {dnsMetrics.cache_hit_ratio !== undefined 
              ? `${(dnsMetrics.cache_hit_ratio * 100).toFixed(1)}%` 
              : 'N/A'}
          </div>
          <div className="detail-note">
            {dnsMetrics.cache_hit_ratio !== undefined && dnsMetrics.cache_hit_ratio < 0.5 ? (
              <span className="note-warning">
                Low DNS cache hit ratio. The Stick suggests reviewing your DNS caching policy.
              </span>
            ) : (
              <span>DNS caching is functioning efficiently.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  
  // Render internet metrics section
  const renderInternetMetrics = () => (
    <div className="quality-section">
      <h4>Internet Connectivity</h4>
      
      <div className="quality-details-grid internet-grid">
        <div className="quality-detail-card">
          <div className="detail-header">Gateway Latency</div>
          <div className="detail-value">{internetMetrics.gateway_latency_ms || 'N/A'} ms</div>
          <div className="detail-note">
            {internetMetrics.gateway_latency_ms !== undefined && internetMetrics.gateway_latency_ms > 5 ? (
              <span className="note-warning">
                Local network latency is higher than optimal. The quantum shadow people suggest checking your router.
              </span>
            ) : (
              <span>Local network latency is excellent.</span>
            )}
          </div>
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">Internet Latency</div>
          <div className="detail-value">{internetMetrics.internet_latency_ms || 'N/A'} ms</div>
          <div className="detail-subvalues">
            <div className="detail-subvalue">
              <span className="subvalue-label">Hop Count:</span>
              <span className="subvalue-data">{internetMetrics.hop_count || 'N/A'}</span>
            </div>
          </div>
        </div>
        
        <div className="quality-detail-card">
          <div className="detail-header">ISP Performance</div>
          <div className="detail-value">
            {internetMetrics.isp_performance_score !== undefined 
              ? internetMetrics.isp_performance_score 
              : 'N/A'}
          </div>
          <div className="detail-note">
            {internetMetrics.isp_performance_score !== undefined && internetMetrics.isp_performance_score < 50 ? (
              <span className="note-warning">
                Your ISP performance is suboptimal. The Meth Snail suggests cosmic intervention.
              </span>
            ) : (
              <span>ISP performance is within acceptable parameters.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  
  return (
    <div className="network-quality-metrics">
      {renderConnectionQuality()}
      {renderDNSMetrics()}
      {renderInternetMetrics()}
      
      <div className="quality-footer">
        <div className="quality-note">
          <div className="note-icon">🧠</div>
          <div className="note-text">
            <p>
              <strong>The Meth Snail's Cosmic Wisdom:</strong> {" "}
              {qualityData.overall_score && qualityData.overall_score < 50 ? (
                "Your network connection appears to be suffering from quantum interference. Have you tried turning it off and on again while wearing a tinfoil hat?"
              ) : (
                "Your network connection is performing admirably. The cosmic energies are aligned in your favor."
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NetworkQualityMetrics;
