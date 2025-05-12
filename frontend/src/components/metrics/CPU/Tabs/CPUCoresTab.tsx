// frontend/src/components/metrics/CPU/tabs/CPUCoresTab.tsx

import React, { useMemo } from 'react';
import { CPUCore } from '../types';
import './CPUTabs.css';

interface CPUCoresTabProps {
  cores: CPUCore[];
  physicalCores: number;
  compact?: boolean;
}

const CPUCoresTab: React.FC<CPUCoresTabProps> = ({ 
  cores, 
  physicalCores,
  compact = false 
}) => {
  // Calculate statistics and detect imbalances
  const stats = useMemo(() => {
    if (!cores || cores.length === 0) return null;
    
    // Calculate average usage across all cores
    const avgUsage = cores.reduce((sum, core) => sum + core.usage_percent, 0) / cores.length;
    
    // Find most and least loaded cores
    const mostLoaded = [...cores].sort((a, b) => b.usage_percent - a.usage_percent)[0];
    const leastLoaded = [...cores].sort((a, b) => a.usage_percent - b.usage_percent)[0];
    
    // Calculate imbalance as the difference between most and least loaded cores
    const imbalancePercent = mostLoaded.usage_percent - leastLoaded.usage_percent;
    
    // Determine if there's a significant imbalance (more than 30% difference)
    const hasImbalance = imbalancePercent > 30;
    
    // Calculate standard deviation to quantify overall balance
    const variance = cores.reduce((sum, core) => {
      const diff = core.usage_percent - avgUsage;
      return sum + (diff * diff);
    }, 0) / cores.length;
    const stdDev = Math.sqrt(variance);
    
    // Group cores by physical core (assuming logical cores are sequential pairs)
    const physicalCoreGroups: { [key: number]: CPUCore[] } = {};
    cores.forEach(core => {
      const physicalId = Math.floor(core.id / 2);
      if (!physicalCoreGroups[physicalId]) {
        physicalCoreGroups[physicalId] = [];
      }
      physicalCoreGroups[physicalId].push(core);
    });
    
    return {
      avgUsage,
      mostLoaded,
      leastLoaded,
      imbalancePercent,
      hasImbalance,
      stdDev,
      physicalCoreGroups
    };
  }, [cores]);
  
  // If no core data available
  if (!cores || cores.length === 0 || !stats) {
    return (
      <div className="cpu-section">
        <div className="cpu-section-title">CPU Cores</div>
        <div className="no-data-message">No core-specific data available</div>
      </div>
    );
  }

  // Get class for usage level
  const getUsageClass = (usage: number) => {
    if (usage > 90) return 'critical';
    if (usage > 70) return 'high';
    if (usage > 40) return 'medium';
    return 'low';
  };
  
  // Get class for imbalance
  const getImbalanceClass = (imbalance: number) => {
    if (imbalance > 50) return 'critical';
    if (imbalance > 30) return 'significant';
    if (imbalance > 15) return 'moderate';
    return 'balanced';
  };

  return (
    <div className="cpu-cores-tab">
      <div className="cpu-section">
        <div className="cpu-section-title">Core Usage Overview</div>
        <div className="cpu-stats-summary">
          <div className="stat-card">
            <div className="stat-title">Average Load</div>
            <div className={`stat-value ${getUsageClass(stats.avgUsage)}`}>
              {stats.avgUsage.toFixed(1)}%
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Core Imbalance</div>
            <div className={`stat-value ${getImbalanceClass(stats.imbalancePercent)}`}>
              {stats.imbalancePercent.toFixed(1)}%
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Most Loaded Core</div>
            <div className={`stat-value ${getUsageClass(stats.mostLoaded.usage_percent)}`}>
              Core {stats.mostLoaded.id}: {stats.mostLoaded.usage_percent.toFixed(1)}%
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-title">Most Idle Core</div>
            <div className={`stat-value ${getUsageClass(stats.leastLoaded.usage_percent)}`}>
              Core {stats.leastLoaded.id}: {stats.leastLoaded.usage_percent.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
      
      <div className="cpu-section">
        <div className="cpu-section-title">Per-Core Metrics</div>
        <div className="cores-grid">
          {cores.map(core => {
            const threadData = core.threads || [];
            const hasThreadData = threadData.length > 0;
            const coreClass = getUsageClass(core.usage_percent);
            
            return (
              <div key={core.id} className={`core-card ${coreClass}`}>
                <div className="core-header">
                  <div className="core-id">Core {core.id}</div>
                  <div className="core-usage">{core.usage_percent.toFixed(1)}%</div>
                </div>
                
                <div className="core-usage-bar">
                  <div 
                    className={`usage-bar-fill ${coreClass}`}
                    style={{ width: `${core.usage_percent}%` }}
                  ></div>
                </div>
                
                {core.frequency_mhz && (
                  <div className="core-frequency">
                    {(core.frequency_mhz / 1000).toFixed(2)} GHz
                  </div>
                )}
                
                {hasThreadData && (
                  <div className="core-threads">
                    {threadData.map(thread => (
                      <div key={thread.id} className="thread-item">
                        <div className="thread-info">
                          <span className="thread-id">Thread {thread.id}</span>
                          {thread.process_name && (
                            <span className="thread-process">{thread.process_name}</span>
                          )}
                        </div>
                        <div className="thread-usage-bar">
                          <div 
                            className={`usage-bar-fill ${getUsageClass(thread.usage_percent)}`}
                            style={{ width: `${thread.usage_percent}%` }}
                          ></div>
                          <span className="thread-usage-text">
                            {thread.usage_percent.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {stats.hasImbalance && (
        <div className="cpu-section">
          <div className="cpu-section-title">Workload Imbalance Detected</div>
          <div className="imbalance-analysis">
            <div className="imbalance-description">
              <p>
                <strong>Significant core imbalance detected ({stats.imbalancePercent.toFixed(1)}% difference)</strong>
              </p>
              <p>
                Some CPU cores are significantly more loaded than others, which may indicate:
              </p>
              <ul>
                <li>Single-threaded applications consuming one core</li>
                <li>Inefficient thread scheduling</li>
                <li>Background processes concentrated on specific cores</li>
              </ul>
            </div>
            
            <div className="optimization-recommendations">
              <h4>Recommended Actions:</h4>
              <div className="recommendations-list">
                <div className="recommendation-item">
                  <div className="recommendation-title">Use Thread Affinity</div>
                  <div className="recommendation-description">
                    Set thread affinity for high-CPU processes to distribute load more evenly across cores.
                  </div>
                  <button className="recommendation-action">Configure in Auto-Tuner</button>
                </div>
                
                <div className="recommendation-item">
                  <div className="recommendation-title">Process Priority Adjustment</div>
                  <div className="recommendation-description">
                    Adjust process priorities to ensure background tasks don't monopolize specific cores.
                  </div>
                  <button className="recommendation-action">View Processes</button>
                </div>
                
                <div className="recommendation-item">
                  <div className="recommendation-title">Application Thread Settings</div>
                  <div className="recommendation-description">
                    For applications with adjustable thread settings, ensure they're configured to use multiple cores effectively.
                  </div>
                  <button className="recommendation-action">Application Settings</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="cpu-section">
        <div className="cpu-section-title">Physical vs Logical Cores</div>
        <div className="physical-cores-grid">
          {Object.entries(stats.physicalCoreGroups).map(([physicalId, logicalCores]) => (
            <div key={physicalId} className="physical-core-card">
              <div className="physical-core-header">
                <div className="physical-core-id">Physical Core {physicalId}</div>
                <div className="logical-cores-count">
                  {logicalCores.length} Logical {logicalCores.length === 1 ? 'Core' : 'Cores'}
                </div>
              </div>
              
              <div className="logical-cores">
                {logicalCores.map(core => (
                  <div key={core.id} className="logical-core">
                    <div className="logical-core-header">
                      <span className="logical-core-id">Logical Core {core.id}</span>
                      <span className={`logical-core-usage ${getUsageClass(core.usage_percent)}`}>
                        {core.usage_percent.toFixed(1)}%
                      </span>
                    </div>
                    <div className="logical-core-bar">
                      <div 
                        className={`usage-bar-fill ${getUsageClass(core.usage_percent)}`}
                        style={{ width: `${core.usage_percent}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="physical-core-stats">
                <div className="physical-core-usage">
                  <div className="stat-label">Average Usage:</div>
                  <div className="stat-value">
                    {(logicalCores.reduce((sum, core) => sum + core.usage_percent, 0) / logicalCores.length).toFixed(1)}%
                  </div>
                </div>
                
                <div className="physical-core-balance">
                  <div className="stat-label">Core Balance:</div>
                  <div className="stat-value">
                    {logicalCores.length > 1 ? 
                      Math.abs(logicalCores[0].usage_percent - logicalCores[1].usage_percent).toFixed(1) + '% diff' : 
                      'N/A'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="cpu-section">
        <div className="cpu-section-title">Thread Distribution Analysis</div>
        <div className="thread-distribution">
          <div className="thread-distribution-chart">
            {/* Placeholder for a more advanced visualization - could be replaced with a proper chart */}
            <div className="thread-heatmap">
              {cores.map(core => (
                <div 
                  key={core.id}
                  className={`heatmap-cell ${getUsageClass(core.usage_percent)}`}
                  style={{ 
                    height: '30px', 
                    width: `${100 / cores.length}%`,
                    opacity: 0.3 + (core.usage_percent / 100) * 0.7 
                  }}
                  title={`Core ${core.id}: ${core.usage_percent.toFixed(1)}%`}
                />
              ))}
            </div>
          </div>
          
          <div className="thread-distribution-stats">
            <div className="distribution-stat">
              <div className="stat-label">Distribution Balance:</div>
              <div className={`stat-value ${stats.stdDev > 20 ? 'warning' : 'good'}`}>
                {stats.stdDev < 10 ? 'Excellent' : 
                  stats.stdDev < 20 ? 'Good' : 
                  stats.stdDev < 30 ? 'Fair' : 'Poor'} 
                (σ = {stats.stdDev.toFixed(1)})
              </div>
            </div>
            
            <div className="distribution-stat">
              <div className="stat-label">Threads per Core:</div>
              <div className="stat-value">
                {(cores.reduce((sum, core) => sum + (core.threads?.length || 0), 0) / cores.length).toFixed(1)} avg
              </div>
            </div>
          </div>
          
          <div className="thread-distribution-recommendations">
            <h4>Optimization Strategies:</h4>
            <ul className="strategy-list">
              <li>
                <strong>Process Affinity:</strong> Assign CPU-intensive processes to specific cores to balance load
              </li>
              <li>
                <strong>Background Process Management:</strong> Limit the CPU usage of background processes
              </li>
              <li>
                <strong>Thread Throttling:</strong> For applications with many threads, consider limiting thread count
              </li>
              <li>
                <strong>NUMA Optimization:</strong> For multi-socket systems, ensure processes run on the appropriate node
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CPUCoresTab;