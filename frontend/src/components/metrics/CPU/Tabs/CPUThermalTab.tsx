import React, { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
} from 'recharts';
import { CPUTemperature } from '../types';
import { formatTemperature, getTemperatureClass, getThresholdDescription } from '@/components/metrics/CPU/Utils/temperatureUtils';


interface CPUThermalTabProps {
  temperature: CPUTemperature;
  historicalData?: {
    timestamp: string;
    temperature: number;
    usage_percent: number;
  }[];
  compact?: boolean;
}

const CPUThermalTab: React.FC<CPUThermalTabProps> = ({ 
  temperature, 
  historicalData = []}) => {
  // Remove unused compact prop warning
  // Calculate threshold percentages for the gauge
  const thresholds = useMemo(() => {
    const range = temperature.max - temperature.min;
    return {
      throttle: ((temperature.throttle_threshold - temperature.min) / range) * 100,
      critical: ((temperature.critical - temperature.min) / range) * 100,
      current: ((temperature.current - temperature.min) / range) * 100
    };
  }, [temperature]);
  
  // Get temperature status class and description
  const tempClass = getTemperatureClass(temperature.current, temperature.throttle_threshold, temperature.critical);
  const tempDescription = getThresholdDescription(temperature.current, temperature.throttle_threshold, temperature.critical);

  return (
    <div className="cpu-thermal-tab">
      <div className="cpu-section">
        <div className="cpu-section-title">CPU Temperature</div>
        
        <div className="temperature-gauge-container">
          <div className="temperature-value">
            <span className={`temperature-number ${tempClass}`}>
              {formatTemperature(temperature.current, temperature.unit)}
            </span>
            <span className="temperature-status">{tempDescription}</span>
          </div>
          
          <div className="temperature-gauge">
            <div className="temperature-scale">
              <div className="temperature-zone normal" style={{ width: `${thresholds.throttle}%` }}></div>
              <div className="temperature-zone warning" style={{ width: `${thresholds.critical - thresholds.throttle}%` }}></div>
              <div className="temperature-zone critical" style={{ width: `${100 - thresholds.critical}%` }}></div>
              
              {/* Temperature marker */}
              <div 
                className="temperature-marker" 
                style={{ left: `${thresholds.current}%` }}
              ></div>
            </div>
            
            <div className="temperature-labels">
              <span className="min-temp">{formatTemperature(temperature.min, temperature.unit)}</span>
              <span className="throttle-temp">
                {formatTemperature(temperature.throttle_threshold, temperature.unit)}
                <span className="threshold-label">Throttle</span>
              </span>
              <span className="critical-temp">
                {formatTemperature(temperature.critical, temperature.unit)}
                <span className="threshold-label">Critical</span>
              </span>
              <span className="max-temp">{formatTemperature(temperature.max, temperature.unit)}</span>
            </div>
          </div>
        </div>
        
        <div className="temperature-recommendations">
          {temperature.current >= temperature.critical && (
            <div className="temperature-alert critical">
              <span className="alert-icon">⚠️</span>
              <span className="alert-message">
                Critical temperature detected! The system may shut down to prevent damage.
                Immediately check cooling systems and reduce system load.
              </span>
            </div>
          )}
          
          {temperature.current >= temperature.throttle_threshold && temperature.current < temperature.critical && (
            <div className="temperature-alert warning">
              <span className="alert-icon">⚠️</span>
              <span className="alert-message">
                CPU is running hot! Performance throttling may occur.
                Check that cooling fans are working and system vents are clear.
              </span>
            </div>
          )}
          
          {temperature.current >= (temperature.throttle_threshold * 0.8) && temperature.current < temperature.throttle_threshold && (
            <div className="temperature-alert notice">
              <span className="alert-icon">ℹ️</span>
              <span className="alert-message">
                CPU temperature is elevated but within acceptable limits.
                Consider monitoring and improving system cooling for optimal performance.
              </span>
            </div>
          )}
        </div>
      </div>
      
      {historicalData && historicalData.length > 0 ? (
        <div className="cpu-section">
          <div className="cpu-section-title">Temperature & Usage Correlation</div>
          
          <div className="temperature-chart">
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(time) => new Date(time).toLocaleTimeString()}
                  stroke="rgba(255, 255, 255, 0.7)"
                />
                <YAxis 
                  yAxisId="temp"
                  orientation="left" 
                  domain={[temperature.min, temperature.max]}
                  tickFormatter={(value) => `${value}°${temperature.unit}`}
                  stroke="rgba(255, 255, 255, 0.7)"
                />
                <YAxis 
                  yAxisId="usage"
                  orientation="right" 
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                  stroke="rgba(255, 255, 255, 0.7)"
                />
                <Tooltip 
                  formatter={(value, name) => {
                    if (name === 'temperature') return [`${value}°${temperature.unit}`, 'Temperature'];
                    if (name === 'usage_percent') return [`${value}%`, 'CPU Usage'];
                    return [value, name];
                  }}
                  labelFormatter={(label) => new Date(label).toLocaleString()}
                  contentStyle={{ background: 'rgba(0, 0, 0, 0.8)', border: 'none', borderRadius: '8px' }}
                  itemStyle={{ color: 'white' }}
                  labelStyle={{ color: 'white' }}
                />
                <Legend />
                
                {/* Draw threshold lines */}
                <Line 
                  type="monotone" 
                  dataKey={() => temperature.throttle_threshold}
                  stroke="#FF9F1C" 
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  yAxisId="temp"
                  name="Throttle Threshold"
                  dot={false}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey={() => temperature.critical}
                  stroke="#FF5252" 
                  strokeDasharray="5 5"
                  strokeWidth={1}
                  yAxisId="temp"
                  name="Critical Threshold"
                  dot={false}
                  isAnimationActive={false}
                />
                
                {/* Temperature and usage lines */}
                <Line 
                  type="monotone" 
                  dataKey="temperature"
                  stroke="#FF5252" 
                  strokeWidth={2}
                  yAxisId="temp"
                  name="Temperature"
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  isAnimationActive={true}
                />
                <Area
                  type="monotone"
                  dataKey="usage_percent"
                  fill="rgba(0, 245, 212, 0.2)"
                  stroke="#00F5D4"
                  yAxisId="usage"
                  name="CPU Usage %"
                  isAnimationActive={true}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          
          <div className="correlation-analysis">
            <h4>Analysis</h4>
            {analyzeTemperatureUsageCorrelation(historicalData, temperature)}
          </div>
        </div>
      ) : (
        <div className="cpu-section">
          <div className="cpu-section-title">Temperature & Usage Correlation</div>
          <div className="no-data-message">
            No historical temperature data available. 
            Temperature tracking will begin collecting data for future analysis.
          </div>
        </div>
      )}
      
      <div className="cpu-section">
        <div className="cpu-section-title">Thermal Management Tips</div>
        <div className="management-tips">
          <div className="tip">
            <div className="tip-title">Check Physical Cooling</div>
            <div className="tip-description">
              Ensure all fans are working, air vents are clear of dust, and thermal paste is properly applied.
            </div>
          </div>
          
          <div className="tip">
            <div className="tip-title">Manage Workloads</div>
            <div className="tip-description">
              Distribute CPU-intensive tasks over time rather than running them simultaneously.
            </div>
          </div>
          
          <div className="tip">
            <div className="tip-title">Consider Undervolting</div>
            <div className="tip-description">
              If supported, undervolting can reduce heat generation while maintaining performance.
            </div>
          </div>
          
          <div className="tip">
            <div className="tip-title">Ambient Temperature</div>
            <div className="tip-description">
              Keep your system in a cool, well-ventilated area. Ambient temperature directly affects CPU temps.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Analyzes temperature and usage data to provide insights
 */
function analyzeTemperatureUsageCorrelation(
  historicalData: { timestamp: string; temperature: number; usage_percent: number; }[],
  temperature: CPUTemperature
): React.ReactNode {
  if (!historicalData || historicalData.length < 5) {
    return <p>Not enough data to analyze patterns yet. Continue collecting data for insights.</p>;
  }
  
  // Find peaks and analyze correlation
  const peaks = findTemperaturePeaks(historicalData);
  const correlation = calculateUsageTempCorrelation(historicalData);
  
  // Check for throttling episodes
  const throttlingPoints = historicalData.filter(d => d.temperature >= temperature.throttle_threshold);
  
  let insights = [];
  
  // Correlation insights
  if (correlation > 0.7) {
    insights.push(
      <p key="high-corr">
        <strong>Strong correlation detected:</strong> CPU temperature closely follows usage patterns. 
        This is expected behavior, but high correlation may indicate limited thermal headroom.
      </p>
    );
  } else if (correlation > 0.4) {
    insights.push(
      <p key="med-corr">
        <strong>Moderate correlation detected:</strong> CPU temperature generally follows usage, 
        with some thermal buffering. Your cooling solution appears to be working.
      </p>
    );
  } else {
    insights.push(
      <p key="low-corr">
        <strong>Low correlation detected:</strong> Temperature doesn't follow usage patterns closely. 
        This could indicate external factors like changing ambient temperature or potential cooling issues.
      </p>
    );
  }
  
  // Peak insights
  if (peaks.length > 0) {
    insights.push(
      <p key="peaks">
        <strong>Temperature spikes detected:</strong> {peaks.length} significant temperature 
        {peaks.length === 1 ? ' spike' : ' spikes'} observed. 
        {peaks.some(p => p.temp >= temperature.throttle_threshold) ? 
          ' Some spikes approached or exceeded throttling threshold.' : 
          ' Temperature remained below throttling threshold.'}
      </p>
    );
  }
  
  // Throttling insights
  if (throttlingPoints.length > 0) {
    const percentTime = (throttlingPoints.length / historicalData.length) * 100;
    insights.push(
      <p key="throttle" className="warning-text">
        <strong>Throttling risk detected:</strong> CPU reached throttling temperatures during 
        approximately {percentTime.toFixed(1)}% of the monitored period. Performance may be affected.
      </p>
    );
  }
  
  return <>{insights}</>;
}

/**
 * Find significant temperature peaks in historical data
 */
function findTemperaturePeaks(data: { temperature: number }[]): { index: number; temp: number }[] {
  if (data.length < 5) return [];
  
  const peaks: { index: number; temp: number }[] = [];
  const threshold = 5; // Minimum difference to consider a peak
  
  for (let i = 2; i < data.length - 2; i++) {
    const current = data[i].temperature;
    const prev2 = data[i-2].temperature;
    const prev1 = data[i-1].temperature;
    const next1 = data[i+1].temperature;
    const next2 = data[i+2].temperature;
    
    if (current > prev1 && current > prev2 && current > next1 && current > next2 && 
        current - Math.min(prev2, prev1, next1, next2) > threshold) {
      peaks.push({ index: i, temp: current });
    }
  }
  
  return peaks;
}

/**
 * Calculate a simple correlation coefficient between usage and temperature
 */
function calculateUsageTempCorrelation(data: { temperature: number; usage_percent: number }[]): number {
  if (data.length < 5) return 0;
  
  const n = data.length;
  
  // Calculate means
  const tempMean = data.reduce((sum, d) => sum + d.temperature, 0) / n;
  const usageMean = data.reduce((sum, d) => sum + d.usage_percent, 0) / n;
  
  // Calculate covariance and variances
  let covariance = 0;
  let tempVariance = 0;
  let usageVariance = 0;
  
  for (const d of data) {
    const tempDiff = d.temperature - tempMean;
    const usageDiff = d.usage_percent - usageMean;
    
    covariance += tempDiff * usageDiff;
    tempVariance += tempDiff * tempDiff;
    usageVariance += usageDiff * usageDiff;
  }
  
  // Calculate correlation coefficient
  return covariance / (Math.sqrt(tempVariance) * Math.sqrt(usageVariance));
}

export default CPUThermalTab;