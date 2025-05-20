// frontend/src/components/metrics/CPU/tabs/CPUOverviewTab.tsx (continued)

import React from 'react';
import { CPUData } from './types';
import { formatTemperature, getTemperatureClass } from '../Utils/temperatureUtils';
import './CPUTabs.css';

interface CPUOverviewTabProps {
  data: CPUData;
  compact?: boolean;
}

const CPUOverviewTab: React.FC<CPUOverviewTabProps> = ({ data, compact = false }) => {
  return (
    <div className="cpu-overview-tab">
      <div className="cpu-usage-container">
        <div className="cpu-usage-gauge">
          {/* Background arc */}
          <svg viewBox="0 0 200 100" className="gauge">
            {/* Background arc */}
            <path 
              d="M20,90 A 60,60 0 0,1 180,90" 
              className="gauge-background" 
            />
            
            {/* Usage arc */}
            <path 
              d={`M20,90 A 60,60 0 ${data.overall_usage > 50 ? 1 : 0},1 ${20 + 160 * (data.overall_usage / 100)},${90 - Math.sin(Math.PI * data.overall_usage / 100) * 60}`} 
              className={`gauge-value ${
                data.overall_usage > 90 ? 'critical' :
                data.overall_usage > 70 ? 'high' :
                data.overall_usage > 40 ? 'medium' : 'low'
              }`} 
            />
            
            {/* Usage percentage text */}
            <text x="100" y="85" className="gauge-percentage">
              {data.overall_usage.toFixed(1)}%
            </text>
            
            <text x="100" y="15" className="gauge-label">CPU Usage</text>
          </svg>
        </div>
        
        <div className="cpu-info-panel">
          <div className="info-row">
            <div className="info-label">Model:</div>
            <div className="info-value">{data.model_name}</div>
          </div>
          <div className="info-row">
            <div className="info-label">Cores:</div>
            <div className="info-value"></div>
          </div>
          <div className="info-row">
            <div className="info-label">Frequency:</div>
            <div className="info-value">{(data.frequency_mhz / 1000).toFixed(2)} GHz</div>
          </div>
          <div className="info-row">
            <div className="info-label">Processes:</div>
            <div className="info-value">{data.process_count}</div>
          </div>
          <div className="info-row">
            <div className="info-label">Threads:</div>
            <div className="info-value">{data.thread_count}</div>
          </div>
          {data.temperature && (
            <div className="info-row">
              <div className="info-label">Temperature:</div>
              <div className={`info-value ${getTemperatureClass(
                data.temperature.current,
                data.temperature.throttle_threshold,
                data.temperature.critical
              )}`}>
                {formatTemperature(data.temperature.current, data.temperature.unit)}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Top Processes Overview */}
      <div className="cpu-section">
        <div className="cpu-section-title">Top CPU Processes</div>
        
        {data.top_processes && data.top_processes.length > 0 ? (
          <div className="top-processes-overview">
            {data.top_processes.slice(0, 5).map((process, index) => (
              <div key={process.pid} className="top-process-item">
                <div className="process-rank">{index + 1}</div>
                <div className="process-details">
                  <div className="process-name">{process.name}</div>
                  <div className="process-info">
                    <span className="process-pid">PID: {process.pid}</span>
                    <span className="process-user">{process.user}</span>
                  </div>
                </div>
                <div className="process-usage">
                  <div className="usage-bar-container">
                    <div 
                      className="usage-bar-fill" 
                      style={{ width: `${Math.min(process.cpu_percent, 100)}%` }}
                    />
                    <span className="usage-text">{process.cpu_percent.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data-message">No process data available</div>
        )}
        
        <div className="view-all-link">
          <button onClick={() => {/* Navigate to processes tab */}}>View All Processes</button>
        </div>
      </div>
      
      {/* Temperature Overview */}
      {data.temperature && (
        <div className="cpu-section">
          <div className="cpu-section-title">Temperature Status</div>
          
          <div className="temperature-overview">
            <div className="current-temperature">
              <div className={`temp-value ${getTemperatureClass(
                data.temperature.current,
                data.temperature.throttle_threshold,
                data.temperature.critical
              )}`}>
                {formatTemperature(data.temperature.current, data.temperature.unit)}
              </div>
              
              <div className="temp-scale">
                <div className="temp-scale-min">
                  {formatTemperature(data.temperature.min, data.temperature.unit)}
                </div>
                <div className="temp-scale-bar">
                  <div className="temp-scale-normal"></div>
                  <div className="temp-scale-warning"></div>
                  <div className="temp-scale-critical"></div>
                  <div 
                    className="temp-scale-marker"
                    style={{
                      left: `${Math.min(100, Math.max(0, (
                        (data.temperature.current - data.temperature.min) / 
                        (data.temperature.max - data.temperature.min)
                      ) * 100))}%`
                    }}
                  ></div>
                </div>
                <div className="temp-scale-max">
                  {formatTemperature(data.temperature.max, data.temperature.unit)}
                </div>
              </div>
            </div>
            
            {data.temperature.current >= data.temperature.throttle_threshold * 0.8 && (
              <div className={`temp-alert ${data.temperature.current >= data.temperature.critical ? 
                'critical' : data.temperature.current >= data.temperature.throttle_threshold ? 
                'warning' : 'notice'}`}>
                <div className="alert-icon">⚠️</div>
                <div className="alert-message">
                  {data.temperature.current >= data.temperature.critical ? 
                    'CRITICAL: CPU temperature exceeds critical threshold!' : 
                    data.temperature.current >= data.temperature.throttle_threshold ? 
                    'WARNING: CPU temperature has reached throttling threshold.' : 
                    'NOTICE: CPU temperature is elevated.'}
                </div>
              </div>
            )}
            
            <div className="view-thermal-link">
              <button onClick={() => {/* Navigate to thermal tab */}}>View Detailed Thermal Analysis</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Core Balance Indicator */}
      {data.cores && data.cores.length > 0 && (
        <div className="cpu-section">
          <div className="cpu-section-title">Core Balance</div>
          
          <div className="core-balance-overview">
            <div className="core-usage-bars">
              {data.cores.slice(0, compact ? 4 : 8).map(core => (
                <div key={core.id} className="core-mini-bar">
                  <div className="core-mini-label">Core {core.id}</div>
                  <div className="core-mini-bar-container">
                    <div 
                      className={`core-mini-bar-fill ${
                        core.usage_percent > 90 ? 'critical' :
                        core.usage_percent > 70 ? 'high' :
                        core.usage_percent > 40 ? 'medium' : 'low'
                      }`}
                      style={{ height: `${core.usage_percent}%` }}
                    ></div>
                  </div>
                  <div className="core-mini-value">{core.usage_percent.toFixed(0)}%</div>
                </div>
              ))}
              
              {data.cores.length > (compact ? 4 : 8) && (
                <div className="core-mini-more">+{data.cores.length - (compact ? 4 : 8)} more</div>
              )}
            </div>
            
            <div className="core-balance-analysis">
              {(() => {
                // Calculate imbalance
                const usages = data.cores.map(c => c.usage_percent);
                const maxUsage = Math.max(...usages);
                const minUsage = Math.min(...usages);
                const imbalance = maxUsage - minUsage;
                
                if (imbalance > 30) {
                  return (
                    <div className="imbalance-warning">
                      <span className="warning-icon">⚠️</span>
                      <span className="warning-text">
                        Significant core imbalance detected ({imbalance.toFixed(0)}% difference)
                      </span>
                      <button className="view-cores-button">View Core Details</button>
                    </div>
                  );
                }
                
                return (
                  <div className="balance-status">
                    <span className="status-icon">✓</span>
                    <span className="status-text">
                      Core workload is relatively balanced ({imbalance.toFixed(0)}% max difference)
                    </span>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CPUOverviewTab;