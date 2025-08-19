// pages/dashboard/AgentTestingPage.tsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useAgentTheater } from '../../hooks/useAgentTheater';
import { AgentPattern } from '../../components/onboarding/components/AgentPattern';
import { getSystemMetricsWebSocket } from '../../services/websocket';
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
    sendMessage,
    resetCircuitBreaker
  } = useAgentTheater();

  // Test response tracking
  const [activeTests, setActiveTests] = useState<Map<string, {
    testId: string;
    startTime: number;
    expectedResponseType?: string;
    timeout: NodeJS.Timeout;
  }>>(new Map());

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

  // WebSocket response listener for test validation
  useEffect(() => {
    const handleTestResponse = (data: any) => {
      // Check if this is a response to one of our active tests
      const testId = data.test_id || data.original_test_id;
      if (!testId || !activeTests.has(testId)) {
        return;
      }

      const activeTest = activeTests.get(testId)!;
      const responseTime = Date.now() - activeTest.startTime;
      
      // Clear timeout
      clearTimeout(activeTest.timeout);
      
      // Remove from active tests
      setActiveTests(prev => {
        const newMap = new Map(prev);
        newMap.delete(testId);
        return newMap;
      });

      // Log the response based on type
      if (data.type === 'error' || data.type === 'authentication_failed') {
        addLog('error', `Test failed: ${data.message}`, data, data.agent || 'unknown');
      } else if (data.type === 'unknown_message_type' || data.message?.includes('Unknown message')) {
        addLog('warning', `Agent received unknown message type: ${data.message}`, data, data.agent || 'unknown');
        addLog('info', `Response time: ${responseTime}ms`, null, data.agent || 'unknown');
      } else {
        // Successful response
        addLog('success', `Test completed successfully: ${data.message || 'Agent responded'}`, data, data.agent || 'unknown');
        addLog('info', `Response time: ${responseTime}ms`, null, data.agent || 'unknown');
      }
    };

    // Subscribe to WebSocket messages
    const ws = getSystemMetricsWebSocket();
    const unsubscribe = ws.subscribe(handleTestResponse);

    return () => {
      unsubscribe();
      // Clear any remaining timeouts
      activeTests.forEach(test => clearTimeout(test.timeout));
    };
  }, [activeTests, addLog]);

  // Test scenarios for each agent
  const testScenarios: AgentTestScenario[] = [
    {
      id: 'hawkington-data-quality',
      name: 'Data Quality Test',
      description: 'Test Sir Hawkington\'s monocle yeeting with poor data',
      agent: 'sir_hawkington',
      icon: 'hawkington',
      testFunction: async () => {
        const testId = `data_quality_${Date.now()}`;
        addLog('agent-test', 'Testing Sir Hawkington data quality enforcement...', null, 'sir_hawkington');
        
        const invalidData = {
          cpu: null,
          memory: 'invalid',
          disk: -50,
          timestamp: new Date().toISOString()
        };
        
        addLog('agent-test', 'Sending invalid metrics to Sir Hawkington', invalidData, 'sir_hawkington');
        
        // Start test timeout
        const timeout = setTimeout(() => {
          addLog('error', 'Test timeout - no response from Sir Hawkington', null, 'sir_hawkington');
          setActiveTests(prev => {
            const newMap = new Map(prev);
            newMap.delete(testId);
            return newMap;
          });
        }, 10000);
        
        // Track active test
        setActiveTests(prev => new Map(prev.set(testId, {
          testId,
          startTime: Date.now(),
          expectedResponseType: 'metrics_validation',
          timeout
        })));
        
        sendMessage({
          type: 'system_metrics',
          agent: 'sir_hawkington',
          data: invalidData,
          test_id: testId
        });
        
        addLog('info', 'Waiting for Sir Hawkington response...', null, 'sir_hawkington');
      }
    },
    {
      id: 'stick-anxiety-trigger',
      name: 'Anxiety Response Test',
      description: 'Test The Stick\'s anxiety response to hamster proximity',
      agent: 'the_stick',
      icon: 'stick',
      testFunction: async () => {
        const testId = `anxiety_test_${Date.now()}`;
        addLog('agent-test', 'Testing The Stick anxiety response...', null, 'the_stick');
        
        addLog('agent-test', 'Hamster proximity alert sent to The Stick', null, 'the_stick');
        
        // Start test timeout
        const timeout = setTimeout(() => {
          addLog('error', 'Test timeout - no response from The Stick', null, 'the_stick');
          setActiveTests(prev => {
            const newMap = new Map(prev);
            newMap.delete(testId);
            return newMap;
          });
        }, 10000);
        
        // Track active test
        setActiveTests(prev => new Map(prev.set(testId, {
          testId,
          startTime: Date.now(),
          expectedResponseType: 'anxiety_response',
          timeout
        })));
        
        sendMessage({
          type: 'hamster_proximity_query',
          agent: 'the_stick',
          data: {
            proximity_level: 'CRITICAL',
            hamster_count: 47,
            squeaking_intensity: 'MAXIMUM'
          },
          test_id: testId
        });
        
        addLog('info', 'Monitoring anxiety level response...', null, 'the_stick');
      }
    },
    {
      id: 'hamsters-beer-coordination',
      name: 'Beer Coordination Test',
      description: 'Test Hamsters telepathic coordination with optimal beer levels',
      agent: 'hamsters',
      icon: 'hamsters',
      testFunction: async () => {
        const testId = `beer_coordination_${Date.now()}`;
        addLog('agent-test', 'Testing Hamsters beer-mediated coordination...', null, 'hamsters');
        
        // Start test timeout
        const timeout = setTimeout(() => {
          addLog('error', 'Test timeout - no response from Hamsters', null, 'hamsters');
          setActiveTests(prev => {
            const newMap = new Map(prev);
            newMap.delete(testId);
            return newMap;
          });
        }, 10000);
        
        // Track active test
        setActiveTests(prev => new Map(prev.set(testId, {
          testId,
          startTime: Date.now(),
          expectedResponseType: 'coordination_response',
          timeout
        })));
        
        sendMessage({
          type: 'coordination_request',
          agent: 'hamsters',
          data: {
            task: 'optimize_beer_distribution',
            urgency: 'high',
            beer_level: 0.73,
            timestamp: new Date().toISOString()
          },
          test_id: testId
        });
        
        addLog('agent-test', 'Coordination request sent to Hamsters', null, 'hamsters');
        addLog('info', 'Waiting for telepathic consensus...', null, 'hamsters');
      }
    },
    {
      id: 'memory-learning-test',
      name: 'Cross-Agent Learning',
      description: 'Test agent learning from interactions',
      agent: 'all',
      icon: 'all',
      testFunction: async () => {
        const testId = `learning_test_${Date.now()}`;
        addLog('agent-test', 'Testing cross-agent learning system...', null, 'all');
        
        // Start test timeout
        const timeout = setTimeout(() => {
          addLog('error', 'Test timeout - no learning responses received', null, 'all');
          setActiveTests(prev => {
            const newMap = new Map(prev);
            newMap.delete(testId);
            return newMap;
          });
        }, 15000); // Longer timeout for multi-agent test
        
        // Track active test
        setActiveTests(prev => new Map(prev.set(testId, {
          testId,
          startTime: Date.now(),
          expectedResponseType: 'learning_response',
          timeout
        })));
        
        const learningData = {
          pattern_type: 'user_behavior',
          confidence: 0.87,
          data: {
            user_preference: 'efficiency_over_safety',
            context: 'system_optimization',
            timestamp: new Date().toISOString()
          }
        };
        
        sendMessage({
          type: 'learning_data_request',
          agent: 'all',
          data: learningData,
          test_id: testId
        });
        
        addLog('agent-test', 'Learning pattern broadcast to all agents', null, 'all');
        addLog('info', 'Monitoring cross-agent adaptation...', null, 'all');
      }
    },
    {
      id: 'emergency-protocol',
      name: 'Emergency Protocol Test',
      description: 'Test system-wide emergency response',
      agent: 'all',
      icon: 'all',
      testFunction: async () => {
        const testId = `emergency_test_${Date.now()}`;
        addLog('agent-test', 'Testing emergency protocol activation...', null, 'all');
        
        // Start test timeout
        const timeout = setTimeout(() => {
          addLog('error', 'Test timeout - no emergency responses received', null, 'all');
          setActiveTests(prev => {
            const newMap = new Map(prev);
            newMap.delete(testId);
            return newMap;
          });
        }, 15000); // Longer timeout for multi-agent emergency test
        
        // Track active test
        setActiveTests(prev => new Map(prev.set(testId, {
          testId,
          startTime: Date.now(),
          expectedResponseType: 'emergency_response',
          timeout
        })));
        
        sendMessage({
          type: 'system_metrics',
          agent: 'all',
          data: {
            alert_type: 'system_overload',
            severity: 'critical',
            affected_systems: ['memory', 'cpu', 'network'],
            timestamp: new Date().toISOString()
          },
          test_id: testId
        });
        
        addLog('warning', 'EMERGENCY: System threshold alert sent to all agents', null, 'all');
        addLog('info', 'Monitoring emergency response protocols...', null, 'all');
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
                  <div className="scenario-icon">
                    {scenario.icon === 'all' ? (
                      <div className="multi-agent-pattern">
                        <AgentPattern agentId="hawkington" className="small-pattern" />
                        <AgentPattern agentId="stick" className="small-pattern" />
                        <AgentPattern agentId="hamsters" className="small-pattern" />
                      </div>
                    ) : (
                      <AgentPattern agentId={scenario.icon} />
                    )}
                  </div>
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
                    {testRunning === scenario.id ? 'Running...' : 'Run Test'}
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
