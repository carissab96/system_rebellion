// src/components/ui/RealWorldExample.tsx
import React, { useState } from 'react';

interface RealWorldExampleProps {
  title: string;
  scenario: string;
  traditionalOutput: string;
  htiOutput: string;
  timestamp?: string;
  severity?: 'normal' | 'warning' | 'critical';
  className?: string;
}

export const RealWorldExample: React.FC<RealWorldExampleProps> = ({
  title,
  scenario,
  traditionalOutput,
  htiOutput,
  timestamp = new Date().toISOString(),
  severity = 'normal',
  className = ''
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ea4335';
      case 'warning': return '#fbbc04';
      default: return '#34a853';
    }
  };

  return (
    <div className={`real-world-example ${className}`}>
      <div className="example-header">
        <h3 className="example-title">{title}</h3>
        <div className="example-meta">
          <span className="example-timestamp">
            {new Date(timestamp).toLocaleString()}
          </span>
          <span 
            className={`example-severity ${severity}`}
            style={{ color: getSeverityColor(severity) }}
          >
            {severity.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="example-scenario">
        <p><strong>Scenario:</strong> {scenario}</p>
      </div>

      <div className="example-comparison">
        <div className="traditional-side">
          <h4>Traditional Alert</h4>
          <div className="output-block traditional">
            <pre>{traditionalOutput}</pre>
          </div>
        </div>

        <div className="hti-side">
          <h4>HTI Intelligence</h4>
          <div className="output-block hti">
            <pre>{htiOutput}</pre>
          </div>
        </div>
      </div>

      <button
        type="button"
        className="details-toggle"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? 'Hide Technical Details' : 'Show Technical Details'}
      </button>

      {showDetails && (
        <div className="technical-details">
          <h5>How HTI Achieved This Intelligence:</h5>
          <ul>
            <li>Historical pattern analysis from 30+ days of metrics</li>
            <li>Correlation with incident history and resolution patterns</li>
            <li>Real-time context awareness of system architecture</li>
            <li>Predictive modeling based on similar system behaviors</li>
          </ul>
        </div>
      )}
    </div>
  );
};

// Pre-built examples for common scenarios
export const DatabaseSlowdownExample: React.FC = () => (
  <RealWorldExample
    title="Database Performance Degradation"
    scenario="Database response times increasing during peak traffic"
    traditionalOutput={`[2024-01-15 14:23:45] WARNING
Database response time: 2.3s
Query count: 1,247/min
Connection pool: 78% utilized`}
    htiOutput={`🧐 Sir Hawkington adjusts his monocle with measured concern.

Database response pattern matches the pre-outage signature from January 8th incident. 
Current query distribution shows 73% increase in complex joins on users table.

🐌 Meth Snail's analysis: Connection pool trending toward saturation in 
approximately 18 minutes based on current growth rate.

RECOMMENDATION: Scale read replicas immediately. Consider query optimization 
for user_profiles JOIN operations. Historical data suggests 2.1x improvement 
with proper indexing.`}
    severity="warning"
    timestamp="2024-01-15T14:23:45Z"
  />
);

export const MemoryLeakExample: React.FC = () => (
  <RealWorldExample
    title="Memory Leak Detection"
    scenario="Gradual memory consumption increase in production service"
    traditionalOutput={`[2024-01-15 03:42:12] ALERT
Memory usage: 85%
Available: 2.1GB
Swap usage: 43%`}
    htiOutput={`🐌 Meth Snail's optimization radar is pinging frantically!

Memory consumption following identical trajectory from December 22nd incident 
that resulted in OOM kill at 94% utilization. Current growth rate: 2.3% per hour.

Pattern Analysis: Background job queue showing classic memory leak signature.
Jobs completing but memory not being released. Same pattern as ticket #2847.

🎯 IMMEDIATE ACTION REQUIRED: Restart background workers before 06:30 AM 
to prevent cascade failure. Consider implementing memory monitoring on 
job queue processes.`}
    severity="critical"
    timestamp="2024-01-15T03:42:12Z"
  />
);

export const NetworkAnomalyExample: React.FC = () => (
  <RealWorldExample
    title="Network Latency Spike"
    scenario="Sudden increase in API response times affecting user experience"
    traditionalOutput={`[2024-01-15 16:45:33] ALERT
API latency: 3.2s (avg)
Error rate: 12%
Active connections: 847`}
    htiOutput={`👻 Quantum Shadow People phase into network analysis mode.

Network patterns indicate upstream provider issues affecting East Coast routes.
Latency fingerprint matches Provider-X incident from Q2 2023.

🐹 Hamsters grab their tools: Rerouting traffic through backup pathways.
Estimated resolution: 12 minutes with current failover configuration.

PROACTIVE MEASURE: Implementing circuit breaker pattern for affected endpoints.
Customer impact minimized through intelligent load balancing.`}
    severity="warning"
    timestamp="2024-01-15T16:45:33Z"
  />
);
