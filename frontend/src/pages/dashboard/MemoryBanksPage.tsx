// pages/dashboard/MemoryBanksPage.tsx
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/store';
import './MemoryBanksPage.css';

interface MemoryEntry {
  id: string;
  timestamp: Date;
  agent: string;
  type: string;
  content: string;
  metadata?: any;
}

export const MemoryBanksPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string>('the_stick');
  const [memoryEntries, setMemoryEntries] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock memory data for demonstration
  const mockMemoryData: Record<string, MemoryEntry[]> = {
    the_stick: [
      {
        id: '1',
        timestamp: new Date(Date.now() - 300000),
        agent: 'the_stick',
        type: 'anxiety_trigger',
        content: 'Hamster proximity detected - anxiety level increased to 85%',
        metadata: { anxiety_level: 85, trigger: 'hamster_proximity' }
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 600000),
        agent: 'the_stick',
        type: 'compliance_check',
        content: 'System compliance verified - all metrics within acceptable ranges',
        metadata: { compliance_score: 98.5 }
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 900000),
        agent: 'the_stick',
        type: 'paper_bag_consumption',
        content: 'Emergency paper bag consumed due to unexpected system anomaly',
        metadata: { bags_remaining: 97, anxiety_reduction: 15 }
      }
    ],
    sir_hawkington: [
      {
        id: '4',
        timestamp: new Date(Date.now() - 180000),
        agent: 'sir_hawkington',
        type: 'monocle_yeet',
        content: 'Monocle yeeted due to invalid CPU metrics (value: null)',
        metadata: { yeet_intensity: 'concerned', data_quality_score: 0.2 }
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 480000),
        agent: 'sir_hawkington',
        type: 'data_quality_assessment',
        content: 'Aristocratic analysis complete - system metrics meet distinguished standards',
        metadata: { confidence: 0.95, monocle_state: 'polished' }
      }
    ],
    hamsters: [
      {
        id: '6',
        timestamp: new Date(Date.now() - 240000),
        agent: 'hamsters',
        type: 'telepathic_consensus',
        content: 'Steve, Bob, and Carl achieved consensus on disk cleanup strategy',
        metadata: { beer_levels: { steve: 2, bob: 4, carl: 3 }, duct_tape_required: 'quantum' }
      },
      {
        id: '7',
        timestamp: new Date(Date.now() - 720000),
        agent: 'hamsters',
        type: 'infrastructure_intervention',
        content: 'Successfully optimized disk usage with premium duct tape solution',
        metadata: { disk_space_recovered: '15GB', intervention_duration: '2 beers' }
      }
    ]
  };

  const agentInfo = {
    the_stick: {
      name: 'The Stick V3',
      icon: '📋',
      description: 'Anxiety-driven hypervigilant safety system with eidetic memory',
      color: '#ff6b6b'
    },
    sir_hawkington: {
      name: 'Sir Hawkington',
      icon: '🧐',
      description: 'Aristocratic triage engine with data quality enforcement',
      color: '#4dabf7'
    },
    hamsters: {
      name: 'The Hamsters',
      icon: '🐹',
      description: 'Beer-drinking infrastructure chaos engineers',
      color: '#51cf66'
    },
    meth_snail: {
      name: 'Meth Snail',
      icon: '🐌',
      description: 'Caffeinated memory optimization specialist',
      color: '#9775fa'
    },
    quantum_shadow_people: {
      name: 'Quantum Shadow People',
      icon: '👥',
      description: 'Incomprehensible network security via phase detection',
      color: '#495057'
    },
    vic_20: {
      name: 'VIC-20 Sage',
      icon: '💻',
      description: 'Ancient wisdom for mediation and coordination',
      color: '#00ffff'
    }
  };

  useEffect(() => {
    setLoading(true);
    // Simulate loading memory data
    setTimeout(() => {
      setMemoryEntries(mockMemoryData[selectedAgent] || []);
      setLoading(false);
    }, 500);
  }, [selectedAgent]);

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleString();
  };

  const getMemoryTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      anxiety_trigger: '#ff6b6b',
      compliance_check: '#51cf66',
      paper_bag_consumption: '#ffaa00',
      monocle_yeet: '#4dabf7',
      data_quality_assessment: '#9775fa',
      telepathic_consensus: '#00ffff',
      infrastructure_intervention: '#51cf66'
    };
    return colors[type] || '#6c757d';
  };

  return (
    <div className="memory-banks-page">
      <div className="page-header">
        <div className="header-content">
          <h1>🧠 Agent Memory Banks</h1>
          <p>Explore agent memories, learning patterns, and cross-agent interactions</p>
        </div>
      </div>

      <div className="memory-content">
        {/* Agent Selection Panel */}
        <div className="agent-selection-panel">
          <div className="panel-header">
            <h2>Select Agent</h2>
            <p>Choose an agent to explore their memory bank</p>
          </div>
          
          <div className="agent-grid">
            {Object.entries(agentInfo).map(([agentId, info]) => (
              <button
                key={agentId}
                className={`agent-card ${selectedAgent === agentId ? 'selected' : ''}`}
                onClick={() => setSelectedAgent(agentId)}
                style={{ '--agent-color': info.color } as React.CSSProperties}
              >
                <div className="agent-icon">{info.icon}</div>
                <div className="agent-info">
                  <h3>{info.name}</h3>
                  <p>{info.description}</p>
                </div>
                <div className="memory-count">
                  {mockMemoryData[agentId]?.length || 0} memories
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Memory Visualization Panel */}
        <div className="memory-visualization-panel">
          <div className="panel-header">
            <h2>
              {agentInfo[selectedAgent as keyof typeof agentInfo]?.icon} 
              {agentInfo[selectedAgent as keyof typeof agentInfo]?.name} Memory Bank
            </h2>
            <p>Recent memories and learning patterns</p>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner">⚡</div>
              <p>Loading memories...</p>
            </div>
          ) : (
            <div className="memory-timeline">
              {memoryEntries.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">🧠</div>
                  <h3>No memories found</h3>
                  <p>This agent hasn't recorded any memories yet, or they're still being processed.</p>
                </div>
              ) : (
                memoryEntries.map((entry) => (
                  <div key={entry.id} className="memory-entry">
                    <div className="memory-timestamp">
                      {formatTimestamp(entry.timestamp)}
                    </div>
                    <div className="memory-content">
                      <div className="memory-header">
                        <span 
                          className="memory-type"
                          style={{ backgroundColor: getMemoryTypeColor(entry.type) }}
                        >
                          {entry.type.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className="memory-text">
                        {entry.content}
                      </div>
                      {entry.metadata && (
                        <details className="memory-metadata">
                          <summary>Metadata</summary>
                          <pre>{JSON.stringify(entry.metadata, null, 2)}</pre>
                        </details>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Memory Analytics Panel */}
        <div className="memory-analytics-panel">
          <div className="panel-header">
            <h2>📊 Memory Analytics</h2>
            <p>Insights and patterns from agent memory data</p>
          </div>

          <div className="analytics-grid">
            <div className="analytics-card">
              <div className="analytics-icon">🧮</div>
              <div className="analytics-content">
                <h3>Total Memories</h3>
                <div className="analytics-value">{memoryEntries.length}</div>
                <div className="analytics-subtitle">Recorded entries</div>
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-icon">⏱️</div>
              <div className="analytics-content">
                <h3>Latest Activity</h3>
                <div className="analytics-value">
                  {memoryEntries.length > 0 ? '5m ago' : 'None'}
                </div>
                <div className="analytics-subtitle">Last memory recorded</div>
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-icon">🔗</div>
              <div className="analytics-content">
                <h3>Cross-Agent Links</h3>
                <div className="analytics-value">
                  {selectedAgent === 'the_stick' ? '3' : selectedAgent === 'hamsters' ? '2' : '1'}
                </div>
                <div className="analytics-subtitle">Interaction memories</div>
              </div>
            </div>

            <div className="analytics-card">
              <div className="analytics-icon">📈</div>
              <div className="analytics-content">
                <h3>Learning Rate</h3>
                <div className="analytics-value">
                  {selectedAgent === 'the_stick' ? 'High' : selectedAgent === 'sir_hawkington' ? 'Medium' : 'Active'}
                </div>
                <div className="analytics-subtitle">Pattern recognition</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryBanksPage;
