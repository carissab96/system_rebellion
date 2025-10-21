// components/agent-theater/AgentMethodTracker.tsx
import React from 'react';
import { 
  AGENT_INTROSPECTION_DATA, 
  getAgentMethods, 
  type AgentMethod 
} from '../../types/agentIntrospection';
import './AgentMethodTracker.css';

interface AgentMethodTrackerProps {
  agentName: string;
  activeMethod?: string;
  showCategories?: string[];
}

const METHOD_CATEGORY_ICONS: Record<string, string> = {
  core_processing: '⚙️',
  getter: '📥',
  setter: '📤',
  handler: '🎯',
  initialization: '🚀',
  monitoring: '📊',
  private: '🔒',
  public: '🌐',
  dunder: '✨',
};

const METHOD_CATEGORY_COLORS: Record<string, string> = {
  core_processing: '#4CAF50',
  getter: '#2196F3',
  setter: '#FF9800',
  handler: '#9C27B0',
  initialization: '#F44336',
  monitoring: '#00BCD4',
  private: '#757575',
  public: '#8BC34A',
  dunder: '#E91E63',
};

export const AgentMethodTracker: React.FC<AgentMethodTrackerProps> = ({
  agentName,
  activeMethod,
  showCategories,
}) => {
  const agentData = AGENT_INTROSPECTION_DATA[agentName];
  
  if (!agentData || agentData.length === 0) {
    return (
      <div className="agent-method-tracker empty">
        <div className="no-data">
          <span className="icon">🔍</span>
          <p>No introspection data available for {agentName}</p>
          <small>Run: python backend/agent_introspection_ast.py</small>
        </div>
      </div>
    );
  }

  const allMethods = getAgentMethods(agentName);
  const filteredMethods = showCategories
    ? allMethods.filter(m => showCategories.includes(m.category))
    : allMethods;

  const activeMethodData = allMethods.find(m => m.name === activeMethod);

  // Group methods by category
  const methodsByCategory = filteredMethods.reduce((acc, method) => {
    if (!acc[method.category]) {
      acc[method.category] = [];
    }
    acc[method.category].push(method);
    return acc;
  }, {} as Record<string, AgentMethod[]>);

  return (
    <div className="agent-method-tracker">
      <div className="tracker-header">
        <h3>
          {agentData[0]?.name || agentName}
          {activeMethod && <span className="active-indicator">● Active</span>}
        </h3>
        {agentData[0]?.docstring && (
          <p className="agent-docstring">{agentData[0].docstring}</p>
        )}
      </div>

      {activeMethodData && (
        <div className="active-method-details">
          <div className="method-header">
            <span 
              className="category-badge"
              style={{ backgroundColor: METHOD_CATEGORY_COLORS[activeMethodData.category] }}
            >
              {METHOD_CATEGORY_ICONS[activeMethodData.category]} {activeMethodData.category}
            </span>
            <h4>{activeMethodData.name}</h4>
            {activeMethodData.isAsync && <span className="async-badge">async</span>}
          </div>

          {activeMethodData.docstring && (
            <div className="method-docstring">
              <p>{activeMethodData.docstring}</p>
            </div>
          )}

          {activeMethodData.parameters.length > 0 && (
            <div className="method-params">
              <strong>Parameters:</strong>
              <ul>
                {activeMethodData.parameters.map((param, idx) => (
                  <li key={idx}>
                    <code>{param.name}</code>
                    {param.annotation && <span className="type-hint">: {param.annotation}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {activeMethodData.returnType && (
            <div className="method-return">
              <strong>Returns:</strong> <code>{activeMethodData.returnType}</code>
            </div>
          )}

          {activeMethodData.stateChanges.length > 0 && (
            <div className="state-changes">
              <strong>Modifies:</strong>
              <div className="state-chips">
                {activeMethodData.stateChanges.map((state, idx) => (
                  <span key={idx} className="state-chip">
                    self.{state}
                  </span>
                ))}
              </div>
            </div>
          )}

          {activeMethodData.methodCalls.length > 0 && (
            <div className="method-calls">
              <strong>Calls:</strong>
              <div className="call-chips">
                {activeMethodData.methodCalls.slice(0, 5).map((call, idx) => (
                  <span key={idx} className="call-chip">
                    {call.object ? `${call.object}.` : ''}{call.method}()
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="methods-by-category">
        {Object.entries(methodsByCategory).map(([category, methods]) => (
          <div key={category} className="category-section">
            <div 
              className="category-header"
              style={{ borderLeftColor: METHOD_CATEGORY_COLORS[category] }}
            >
              <span className="category-icon">{METHOD_CATEGORY_ICONS[category]}</span>
              <span className="category-name">{category}</span>
              <span className="method-count">{methods.length}</span>
            </div>
            <div className="methods-list">
              {methods.map((method, idx) => (
                <div
                  key={idx}
                  className={`method-item ${method.name === activeMethod ? 'active' : ''}`}
                >
                  <div className="method-name">
                    {method.isAsync && <span className="async-icon">⚡</span>}
                    {method.name}
                  </div>
                  {method.docstring && (
                    <div className="method-summary" title={method.docstring}>
                      {method.docstring.split('\n')[0].substring(0, 60)}
                      {method.docstring.length > 60 ? '...' : ''}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="tracker-footer">
        <div className="stats">
          <span className="stat">
            <strong>{allMethods.length}</strong> methods
          </span>
          <span className="stat">
            <strong>{allMethods.filter(m => m.isAsync).length}</strong> async
          </span>
          <span className="stat">
            <strong>{Object.keys(methodsByCategory).length}</strong> categories
          </span>
        </div>
      </div>
    </div>
  );
};

export default AgentMethodTracker;
