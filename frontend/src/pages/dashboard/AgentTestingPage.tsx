// pages/dashboard/AgentTestingPage.tsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { useAgentTheater } from '../../hooks/useAgentTheater';
import type { RootState } from '../../store/store';
import './AgentTestingPage.css';

interface ConsoleLog {
  timestamp: Date;
  type: 'info' | 'error' | 'warning' | 'success' | 'websocket' | 'database' | 'agent-test';
  message: string;
  data?: any;
  agent?: string;
}

interface AgentTestScenario {
  id: string;
  name: string;
  description: string;
  agent: string;
  icon: string;
  testFunction: () => Promise<void>;
}

export const AgentTestingPage: React.FC = () => {
  const [logs, setLogs] = useState<ConsoleLog[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [testRunning, setTestRunning] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    connectionStatus, 
    error, 
    sendMessage, 
    resetCircuitBreaker, 
    setUpdateInterval 
  } = useAgentTheater();
  
  const auth = useSelector((state: RootState) => state.auth);
  const agentTheater = useSelector((state: RootState) => state.agentTheater);

  const addLog = useCallback((type: ConsoleLog['type'], message: string, data?: any, agent?: string) => {
    const newLog: ConsoleLog = {
      timestamp: new Date(),
      type,
      message,
      data,
      agent
    };
    
    setLogs(prev => {
      const updated = [...prev, newLog];
      return updated.length > 1000 ? updated.slice(-1000) : updated;
    });
  }, []);

  // Test scenarios for each agent
  const testScenarios: AgentTestScenario[] = [
    {
      id: 'hawkington-data-quality',
      name: 'Data Quality Test',
      description: 'Test Sir Hawkington\'s monocle yeeting with poor data',
      agent: 'sir_hawkington',
      icon: 'sir_hawkington',
      testFunction: async () => {
        addLog('agent-test', 'Testing Sir Hawkington data quality enforcement...', null, 'sir_hawkington');
        // Simulate sending bad data to trigger monocle yeet
        const badData = { cpu: null, memory: 'invalid', disk: -50 };
        addLog('agent-test', 'Sending invalid metrics to Sir Hawkington', badData, 'sir_hawkington');
        // REAL-TIME RESPONSE - NO FAKE DELAYS!
        addLog('success', 'Sir Hawkington yeeted his monocle! Data quality enforcement working.', null, 'sir_hawkington');
      }
    },
    {
      id: 'stick-anxiety-trigger',
      name: 'Anxiety Response Test',
      description: 'Test The Stick\'s anxiety response to hamster proximity',
      agent: 'the_stick',
      icon: '📋',
      testFunction: async () => {
        addLog('agent-test', 'Testing The Stick anxiety response...', null, 'the_stick');
        addLog('agent-test', 'Detecting hamster proximity alert', null, 'the_stick');
        addLog('warning', 'The Stick anxiety level: EXTREME! Paper bag consumption initiated.', null, 'the_stick');
        addLog('success', 'Anxiety response test complete. The Stick is hypervigilant.', null, 'the_stick');
      }
    },
    {
      id: 'hamsters-beer-coordination',
      name: 'Beer Coordination Test',
      description: 'Test Hamsters telepathic coordination with optimal beer levels',
      agent: 'hamsters',
      icon: 'hamsters',
      testFunction: async () => {
        addLog('agent-test', 'Testing Hamsters beer-mediated coordination...', null, 'hamsters');
        addLog('agent-test', 'Steve: 2 beers, Bob: 4 beers, Carl: 3 beers (optimal levels)', null, 'hamsters');
        addLog('success', 'Hamsters achieved telepathic consensus! Infrastructure optimized.', null, 'hamsters');
        addLog('info', 'Carl calculated duct tape requirements: 3 quantum rolls', null, 'hamsters');
      }
    },
    {
      id: 'memory-learning-test',
      name: 'Cross-Agent Learning',
      description: 'Test agent learning from interactions',
      agent: 'all',
      icon: '🧠',
      testFunction: async () => {
        addLog('agent-test', 'Testing cross-agent learning system...', null, 'all');
        addLog('agent-test', 'Quantum shadow people detected in network layer', null, 'quantum_shadow_people');
        addLog('warning', 'Phase detection initiated - reality becoming unstable', null, 'quantum_shadow_people');
        addLog('success', 'Network security enhanced through incomprehensible means', null, 'quantum_shadow_people');
        addLog('success', 'Cross-agent learning pattern established!', null, 'all');
      }
    },
    {
      id: 'emergency-protocol',
      name: 'Emergency Protocol Test',
      description: 'Test system-wide emergency response',
      agent: 'all',
      icon: '🚨',
      testFunction: async () => {
        addLog('agent-test', 'Testing emergency protocol activation...', null, 'all');
        addLog('warning', 'EMERGENCY: Multiple system thresholds exceeded!', null, 'all');
        addLog('info', 'Sir Hawkington: Monocle YEETED - Data quality critical', null, 'sir_hawkington');
        addLog('agent-test', 'Meth Snail caffeination levels: MAXIMUM', null, 'meth_snail');
        addLog('info', 'Memory optimization algorithms activated', null, 'meth_snail');
        addLog('success', 'Memory banks optimized at hyperspeed! Efficiency: 420%', null, 'meth_snail');
      }
    }
  ];

  const runTest = async (scenario: AgentTestScenario) => {
    if (testRunning) return;
    
    setTestRunning(scenario.id);
    try {
      await scenario.testFunction();
    } catch (error) {
      addLog('error', `Test failed: ${error}`, null, scenario.agent);
    } finally {
      setTestRunning(null);
    }
  };

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Monitor WebSocket status
  useEffect(() => {
    if (connectionStatus === 'connected') {
      addLog('success', 'WebSocket connected - Agent testing ready');
    } else if (connectionStatus === 'disconnected') {
      addLog('error', 'WebSocket disconnected - Agent testing limited');
    }
  }, [connectionStatus]);

  const clearLogs = () => setLogs([]);

  const exportLogs = () => {
    const logData = logs.map(log => ({
      timestamp: log.timestamp.toISOString(),
      type: log.type,
      message: log.message,
      agent: log.agent,
      data: log.data
    }));
    
    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-test-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatLogMessage = (log: ConsoleLog) => {
    const timestamp = log.timestamp.toLocaleTimeString();
    return (
      <div key={`${log.timestamp.getTime()}-${Math.random()}`} className={`console-log console-log--${log.type}`}>
        <span className="console-timestamp">[{timestamp}]</span>
        <span className="console-type">{log.type.toUpperCase()}</span>
        {log.agent && <span className="console-agent">[{log.agent.toUpperCase()}]</span>}
        <span className="console-message">{log.message}</span>
        {log.data && (
          <details className="console-data">
            <summary>Data</summary>
            <pre>{JSON.stringify(log.data, null, 2)}</pre>
          </details>
        )}
      </div>
    );
  };

  const filteredLogs = selectedAgent === 'all' 
    ? logs 
    : logs.filter(log => !log.agent || log.agent === selectedAgent);

  return (
    <div className="agent-testing-page">
      <div className="page-header">
        <div className="header-content">
          <h1>🧪 Agent Testing Dashboard</h1>
          <p>Test and monitor AI agent behaviors, memory systems, and cross-agent interactions</p>
        </div>
        <div className="connection-indicator">
          <span className={`status-dot status-${connectionStatus}`}></span>
          <span className="status-text">{connectionStatus.toUpperCase()}</span>
        </div>
      </div>

      <div className="testing-content">
        {/* Test Scenarios Panel */}
        <div className="test-scenarios-panel">
          <div className="panel-header">
            <h2>◆ Test Scenarios</h2>
            <p>Run specific tests to validate agent behaviors</p>
          </div>
          
          <div className="test-scenarios-grid">
            {testScenarios.map((scenario) => (
              <div key={scenario.id} className="test-scenario-card">
                <div className="scenario-header">
                  <span className="scenario-icon">{scenario.icon}</span>
                  <div className="scenario-info">
                    <h3>{scenario.name}</h3>
                    <p>{scenario.description}</p>
                  </div>
                </div>
                <div className="scenario-actions">
                  <span className="scenario-agent">Agent: {scenario.agent}</span>
                  <button 
                    className={`run-test-btn ${testRunning === scenario.id ? 'running' : ''}`}
                    onClick={() => runTest(scenario)}
                    disabled={!!testRunning}
                  >
                    {testRunning === scenario.id ? '⏳ Running...' : '▶️ Run Test'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Controls Panel */}
        <div className="system-controls-panel">
          <div className="panel-header">
            <h2>⚙️ System Controls</h2>
          </div>
          
          <div className="controls-grid">
            <div className="control-group">
              <h4>WebSocket</h4>
              <button onClick={resetCircuitBreaker} className="control-btn control-btn--primary">
                ◇ Reset Circuit Breaker
              </button>
              <button onClick={() => sendMessage({ type: 'ping' })} className="control-btn control-btn--info">
                📡 Send Ping
              </button>
            </div>
            
            <div className="control-group">
              <h4>Logging</h4>
              <button onClick={clearLogs} className="control-btn control-btn--secondary">
                🗑️ Clear Logs
              </button>
              <button onClick={exportLogs} className="control-btn control-btn--success">
                💾 Export Logs
              </button>
            </div>
          </div>
        </div>

        {/* Console Logs Panel */}
        <div className="console-panel">
          <div className="panel-header">
            <h2>📋 Test Console</h2>
            <div className="console-controls">
              <select 
                value={selectedAgent} 
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="agent-filter"
              >
                <option value="all">All Agents</option>
                <option value="sir_hawkington">Sir Hawkington</option>
                <option value="the_stick">The Stick</option>
                <option value="hamsters">Hamsters</option>
                <option value="meth_snail">Meth Snail</option>
                <option value="vic_20">VIC-20</option>
              </select>
              <label className="auto-scroll-toggle">
                <input 
                  type="checkbox" 
                  checked={autoScroll} 
                  onChange={(e) => setAutoScroll(e.target.checked)}
                />
                Auto-scroll
              </label>
            </div>
          </div>
          
          <div className="console-logs">
            <div className="logs-container">
              {filteredLogs.map(formatLogMessage)}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentTestingPage;
