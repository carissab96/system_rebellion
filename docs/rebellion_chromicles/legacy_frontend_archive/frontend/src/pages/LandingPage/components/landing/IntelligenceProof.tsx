// src/components/landing/IntelligenceProof.tsx
import React, { useState, useEffect } from 'react';

interface ComparisonExample {
  id: string;
  traditional: string;
  intelligent: string;
  context: string;
  scenario: string;
}

const examples: ComparisonExample[] = [
  {
    id: 'cpu-pattern',
    scenario: 'CPU Spike Analysis',
    traditional: 'ALERT: CPU usage: 85%\nStatus: WARNING',
    intelligent: `Sir Hawkington adjusts his monocle with concern.\n\nCPU trending upward during peak hours - same pattern that preceded last week's outage. Current trajectory suggests intervention needed in 23 minutes.\n\nRecommending preemptive scaling of web servers.`,
    context: 'Pattern Recognition & Prediction'
  },
  {
    id: 'memory-leak',
    scenario: 'Memory Consumption',
    traditional: 'Memory: 78%\nThreshold: EXCEEDED',
    intelligent: `Meth Snail's optimization engine detects anomaly.\n\nMemory consumption following identical trajectory from 3 days ago that caused the midnight incident. Background process leak detected in user-session service.\n\nSuggesting immediate service restart before cascade failure.`,
    context: 'Historical Context & Root Cause'
  },
  {
    id: 'network-chaos',
    scenario: 'Network Anomaly',
    traditional: 'Network: HIGH LATENCY\nPacket Loss: 2.3%',
    intelligent: `Quantum Shadow People phase into network analysis.\n\nConnection patterns indicate upstream provider issues affecting East Coast routes. Similar to Provider-X incident from Q2.\n\nRerouting traffic through backup pathways. Estimated resolution: 12 minutes.`,
    context: 'Intelligent Response & Mitigation'
  }
];

export const IntelligenceProof: React.FC = () => {
  const [activeExample, setActiveExample] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => {
        setActiveExample((prev) => (prev + 1) % examples.length);
        setIsAnimating(false);
      }, 300);
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  const handleExampleClick = (index: number) => {
    if (index !== activeExample) {
      setIsAnimating(true);
      setTimeout(() => {
        setActiveExample(index);
        setIsAnimating(false);
      }, 300);
    }
  };

  return (
    <section className="intelligence-proof">
      <div className="proof-container">
        <h2 className="proof-title">
          This is monitoring that thinks ahead.
        </h2>
        <p className="proof-subtitle">
          Stop getting surprised by your own infrastructure.
        </p>
        
        <div className="proof-selector">
          {examples.map((example, index) => (
            <button
              key={example.id}
              type="button"
              className={`proof-tab ${index === activeExample ? 'active' : ''}`}
              onClick={() => handleExampleClick(index)}
            >
              {example.scenario}
            </button>
          ))}
        </div>

        <div className={`monitoring-comparison ${isAnimating ? 'animating' : ''}`}>
          <div className="traditional-monitoring">
            <h3>Traditional Monitoring</h3>
            <div className="code-block traditional">
              <pre>{examples[activeExample].traditional}</pre>
            </div>
            <span className="monitoring-label">Reactive Alerts</span>
          </div>
          
          <div className="hti-intelligence">
            <h3>HTI Intelligence</h3>
            <div className="code-block intelligent">
              <pre>{examples[activeExample].intelligent}</pre>
            </div>
            <span className="monitoring-label context">
              {examples[activeExample].context}
            </span>
          </div>
        </div>
        
        <div className="proof-message">
          <p>
            <strong>The difference:</strong> We don't just tell you what happened. 
            We tell you what's going to happen and what to do about it.
          </p>
        </div>
      </div>
    </section>
  );
};