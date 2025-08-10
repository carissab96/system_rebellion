// pages/dashboard/MemoryBanksPage.tsx
import React, { useState } from 'react';
import { AgentPattern } from '../../components/onboarding/components/AgentPattern';
import { useAgentTheater } from '../../hooks/useAgentTheater';
import styles from './MemoryBanksPage.module.css';

interface MemoryEntry {
  id: string;
  timestamp: Date;
  agent: string;
  type: string;
  content: string;
  metadata?: any;
}

export const MemoryBanksPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string>('sir_hawkington');
  
  // REAL-TIME DATA ONLY - NO MOCK DATA TOLERATED!
  const { metricsData, connectionStatus } = useAgentTheater();

  // REAL-TIME MEMORY DATA EXTRACTION FROM WEBSOCKET STREAM
  const extractMemoryEntries = (agentKey: string): MemoryEntry[] => {
    const agentData = metricsData[agentKey as keyof typeof metricsData];
    if (!agentData) {
      return [];
    }
    
    const entries: MemoryEntry[] = [];
    
    // Extract real memory entries from agent data
    if (agentData.analysis) {
      entries.push({
        id: `${agentKey}-analysis-${Date.now()}`,
        timestamp: new Date(),
        agent: agentKey,
        type: 'analysis',
        content: agentData.analysis,
        metadata: agentData
      });
    }
    
    if (agentData.decision_type) {
      entries.push({
        id: `${agentKey}-decision-${Date.now()}`,
        timestamp: new Date(),
        agent: agentKey,
        type: 'decision',
        content: `Decision: ${agentData.decision_type}`,
        metadata: { decision_type: agentData.decision_type, ...agentData }
      });
    }
    
    if (agentData.recommendations) {
      entries.push({
        id: `${agentKey}-recommendations-${Date.now()}`,
        timestamp: new Date(),
        agent: agentKey,
        type: 'recommendations',
        content: Array.isArray(agentData.recommendations) 
          ? agentData.recommendations.join('; ') 
          : agentData.recommendations,
        metadata: agentData
      });
    }
    
    return entries;
  };

  const agentInfo = {
    the_stick: {
      name: 'The Stick V3',
      icon: 'the_stick',
      description: 'Anxiety-driven hypervigilant safety system with eidetic memory',
      color: '#ff6b6b'
    },
    sir_hawkington: {
      name: 'Sir Hawkington',
      icon: 'sir_hawkington',
      description: 'Aristocratic triage engine with data quality enforcement',
      color: '#4dabf7'
    },
    hamsters: {
      name: 'The Hamsters',
      icon: 'hamsters',
      description: 'Beer-drinking infrastructure chaos engineers',
      color: '#51cf66'
    },
    meth_snail: {
      name: 'Meth Snail',
      icon: 'meth_snail',
      description: 'Caffeinated memory optimization specialist',
      color: '#9775fa'
    },
    quantum_shadow_people: {
      name: 'Quantum Shadow People',
      icon: 'quantum_shadow_people',
      description: 'Incomprehensible network security via phase detection',
      color: '#495057'
    },
    vic_20: {
      name: 'VIC-20 Sage',
      icon: 'vic_20',
      description: 'Ancient wisdom for mediation and coordination',
      color: '#00ffff'
    }
  };

  // Extract memory entries directly from current data - no useEffect needed
  const currentMemoryEntries = React.useMemo(() => {
    // REAL-TIME DATA EXTRACTION - NO FAKE DELAYS!
    const realMemoryEntries = extractMemoryEntries(selectedAgent);
    
    // If no real data available, honestly report the failure
    if (realMemoryEntries.length === 0 && connectionStatus === 'connected') {
      return [{
        id: 'no-data-failure',
        timestamp: new Date(),
        agent: selectedAgent,
        type: 'system_status',
        content: `No real-time memory data available for ${selectedAgent}. Connection status: ${connectionStatus}`,
        metadata: { failure_reason: 'no_agent_data', connection_status: connectionStatus }
      }];
    }
    
    return realMemoryEntries;
  }, [selectedAgent, metricsData, connectionStatus]);

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
    <div className={styles.memoryBanksPage}>
      <div className="card">
        <header className="card-header">
          <div className="d-flex justify-between align-center">
            <div>
              <h1 className="card-title">◆ Agent Memory Banks</h1>
              <p className="card-subtitle">Real-time memory insights from your AI agent collective</p>
            </div>
            <div className="d-flex align-center gap-2">
              <span className={`status-indicator ${connectionStatus === 'connected' ? 'online' : 'offline'}`}>
                {connectionStatus === 'connected' ? '●' : '○'}
              </span>
              <span className="text-sm text-dim">{connectionStatus}</span>
            </div>
          </div>
        </header>
        <div className="card-body">
          <div className={styles.memoryContent}>
            {/* Agent Selection Panel */}
            <div className="card mb-4">
              <div className="card-header">
                <h2 className="card-title">Select Agent</h2>
                <p className="card-subtitle">Choose an agent to explore their memory patterns</p>
              </div>
              <div className="card-body">
                <div className={styles.agentGrid}>
                  {Object.entries(agentInfo).map(([agentId, info]) => (
                    <button
                      key={agentId}
                      className={`btn ${selectedAgent === agentId ? 'btn-primary' : 'btn-secondary'} ${styles.agentCard}`}
                      onClick={() => setSelectedAgent(agentId)}
                      style={{ '--agent-color': info.color } as React.CSSProperties}
                    >
                      <div className={styles.agentIcon}>
                        <AgentPattern agentId={info.icon} />
                      </div>
                      <div className={styles.agentInfo}>
                        <h3>{info.name}</h3>
                        <p className="text-sm text-dim">{info.description}</p>
                      </div>
                      <div className={styles.memoryCount}>
                        <span className="text-xs text-dim">{extractMemoryEntries(agentId).length} memories</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Memory Visualization Panel */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Memory Stream - {agentInfo[selectedAgent as keyof typeof agentInfo]?.name}</h2>
                <p className="card-subtitle">Live memory entries and cognitive patterns</p>
              </div>
              <div className="card-body">
              <div className="memory-entries">
                {currentMemoryEntries.length === 0 ? (
                  <div className="d-flex flex-col align-center justify-center py-8">
                    <p className="text-dim">No memory entries found for this agent</p>
                  </div>
                ) : (
                  currentMemoryEntries.map((entry) => (
                    <div key={entry.id} className={`card ${styles.memoryEntry}`}>
                      <div className="card-body">
                        <div className="d-flex gap-3">
                          <div className={styles.memoryTimestamp}>
                            <span className="text-xs text-dim">{formatTimestamp(entry.timestamp)}</span>
                          </div>
                          <div className="flex-1">
                            <div className="d-flex align-center gap-2 mb-2">
                              <span 
                                className={`badge ${styles.memoryType}`}
                                style={{ backgroundColor: getMemoryTypeColor(entry.type) }}
                              >
                                {entry.type}
                              </span>
                            </div>
                              <p className="text-sm">{entry.content}</p>
                              {entry.metadata && (
                                <details className={styles.memoryMetadata}>
                                  <summary className="text-xs text-dim cursor-pointer">View metadata</summary>
                                  <pre className="text-xs mt-2 p-2 bg-surface border rounded">
                                    {JSON.stringify(entry.metadata, null, 2)}
                                  </pre>
                                </details>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
            </div>
          </div>
          <div className="card mt-4">
            <div className="card-header">
              <h2 className="card-title">Memory Analytics</h2>
              <p className="card-subtitle">Cognitive insights and pattern analysis</p>
            </div>
            <div className="card-body">
              <div className={styles.analyticsGrid}>
                <div className="card">
                  <div className="card-body d-flex align-center gap-3">
                    <div className={styles.analyticsIcon}>◆</div>
                    <div>
                      <h3 className="text-sm font-medium">Total Memories</h3>
                      <div className="text-lg font-bold" style={{ color: 'var(--vic20-cyan)' }}>
                        {currentMemoryEntries.length}
                      </div>
                      <div className="text-xs text-dim">Active entries</div>
                    </div>
                  </div>
                </div>
                <div className="card">
                  <div className="card-body d-flex align-center gap-3">
                    <div className={styles.analyticsIcon}>◇</div>
                    <div>
                      <h3 className="text-sm font-medium">Memory Types</h3>
                      <div className="text-lg font-bold" style={{ color: 'var(--vic20-cyan)' }}>
                        {new Set(currentMemoryEntries.map((e: MemoryEntry) => e.type)).size}
                      </div>
                      <div className="text-xs text-dim">Unique patterns</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


export default MemoryBanksPage;
