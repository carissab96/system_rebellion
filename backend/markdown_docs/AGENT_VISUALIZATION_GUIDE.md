# Agent Visualization Guide: Using AST Introspection for UI

## Overview

This guide explains how to use AST (Abstract Syntax Tree) introspection to map backend agent functions, methods, and variables to the frontend UI, enabling real-time visualization of agent behavior.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AST Introspection Layer                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  resource_monitor_ast.py  →  Extracts metric functions       │
│  agent_introspection_ast.py → Extracts agent structure       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Generated Mappings                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend: metricKeys.ts, agentIntrospection.ts             │
│  Backend:  metric_keys.py, agent_introspection.py           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    UI Visualization                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  • Real-time method execution tracking                       │
│  • State variable monitoring                                 │
│  • Agent interaction visualization                           │
│  • Performance metrics display                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Tools

### 1. `resource_monitor_ast.py` - Metric Function Extraction

**Purpose:** Extracts metric collection functions from `resource_monitor.py`

**What it extracts:**
- Function names (e.g., `_get_cpu_usage`, `_get_memory_usage`)
- Metric keys (e.g., `cpu_usage`, `memory_usage`)
- Async/sync status
- TypeScript type mappings

**Generated files:**
- `frontend/src/types/metricKeys.ts` - TypeScript constants and types
- `backend/app/optimization/metric_keys.py` - Python constants

**Usage:**
```bash
python backend/resource_monitor_ast.py
```

### 2. `agent_introspection_ast.py` - Agent Structure Extraction

**Purpose:** Extracts complete agent class structures for UI visualization

**What it extracts:**
- **Agent classes** with base classes and docstrings
- **Methods** with:
  - Name, async status, parameters, return types
  - Category (core_processing, handler, getter, monitoring, etc.)
  - State changes (which `self.variable` assignments occur)
  - Method calls (which other methods are invoked)
  - Docstrings for documentation
- **State variables** with types and defaults

**Generated files:**
- `frontend/src/types/agentIntrospection.ts` - TypeScript interfaces and data
- `backend/app/ai_agents/agent_introspection.py` - Python helper functions
- `backend/agent_introspection_data.json` - Raw JSON data

**Usage:**
```bash
python backend/agent_introspection_ast.py
```

## UI Visualization Strategies

### Strategy 1: Real-Time Method Execution Tracking

**Concept:** Show which agent methods are currently executing

**Implementation:**
1. Backend emits events when methods start/end
2. Frontend uses introspection data to display method info
3. UI shows execution timeline with method categories

**Example:**
```typescript
import { getAgentMethods, AGENT_INTROSPECTION_DATA } from '@/types/agentIntrospection';

// Get all methods for an agent
const hawkMethods = getAgentMethods('sir_hawkington');

// Filter by category
const processingMethods = getAgentMethods('sir_hawkington', 'core_processing');

// Display in UI
function AgentMethodTracker({ agentName, activeMethod }) {
  const methods = getAgentMethods(agentName);
  const currentMethod = methods.find(m => m.name === activeMethod);
  
  return (
    <div>
      <h3>{agentName} - Executing: {currentMethod?.name}</h3>
      <p>Category: {currentMethod?.category}</p>
      <p>State Changes: {currentMethod?.stateChanges.join(', ')}</p>
      <p>Calls: {currentMethod?.methodCalls.map(c => c.method).join(', ')}</p>
    </div>
  );
}
```

### Strategy 2: State Variable Monitoring

**Concept:** Display agent state variables and their changes over time

**Implementation:**
1. Use introspection to know which state variables exist
2. Backend emits state changes via WebSocket
3. Frontend displays current values and history

**Example:**
```typescript
import { getAgentStateVariables } from '@/types/agentIntrospection';

function AgentStateMonitor({ agentName, currentState }) {
  const stateVars = getAgentStateVariables(agentName);
  
  return (
    <div className="state-monitor">
      {stateVars.map(stateVar => (
        <div key={stateVar.name}>
          <span>{stateVar.name}</span>
          <span className="type">{stateVar.type}</span>
          <span className="value">{currentState[stateVar.name]}</span>
        </div>
      ))}
    </div>
  );
}
```

### Strategy 3: Agent Theater Visualization

**Concept:** Visual representation of agents working together

**Implementation:**
1. Use method categories to determine agent activity type
2. Show agent "characters" performing actions
3. Animate based on method execution and state changes

**Example:**
```typescript
import { AGENT_INTROSPECTION_DATA } from '@/types/agentIntrospection';

function AgentTheater({ agentEvents }) {
  return (
    <div className="agent-theater">
      {Object.keys(AGENT_INTROSPECTION_DATA).map(agentName => {
        const currentEvent = agentEvents[agentName];
        const agentData = AGENT_INTROSPECTION_DATA[agentName][0];
        
        return (
          <AgentCharacter
            key={agentName}
            name={agentName}
            currentMethod={currentEvent?.method}
            methodCategory={currentEvent?.category}
            docstring={agentData?.docstring}
          />
        );
      })}
    </div>
  );
}
```

### Strategy 4: Method Call Flow Visualization

**Concept:** Show how agents call each other's methods

**Implementation:**
1. Use `methodCalls` data to build interaction graph
2. Display as flow diagram or network graph
3. Highlight active call chains in real-time

**Example:**
```typescript
import { getAgentMethods } from '@/types/agentIntrospection';

function buildInteractionGraph() {
  const graph = {};
  
  Object.keys(AGENT_INTROSPECTION_DATA).forEach(agentName => {
    const methods = getAgentMethods(agentName);
    
    methods.forEach(method => {
      method.methodCalls.forEach(call => {
        if (call.object && call.object !== 'self') {
          // This method calls another object's method
          graph[`${agentName}.${method.name}`] = 
            graph[`${agentName}.${method.name}`] || [];
          graph[`${agentName}.${method.name}`].push(
            `${call.object}.${call.method}`
          );
        }
      });
    });
  });
  
  return graph;
}
```

### Strategy 5: Performance Metrics Dashboard

**Concept:** Display metrics alongside agent method execution

**Implementation:**
1. Use `METRIC_KEYS` to know available metrics
2. Use `METRIC_METADATA` to get type information
3. Correlate metric changes with agent method execution

**Example:**
```typescript
import { METRIC_KEYS, METRIC_METADATA } from '@/types/metricKeys';
import { getAgentMethods } from '@/types/agentIntrospection';

function MetricsAgentCorrelation({ metrics, agentActivity }) {
  return (
    <div className="correlation-view">
      <div className="metrics-panel">
        {Object.values(METRIC_KEYS).map(key => (
          <MetricCard
            key={key}
            metricKey={key}
            value={metrics[key]}
            metadata={METRIC_METADATA[key]}
          />
        ))}
      </div>
      
      <div className="agent-panel">
        {agentActivity.map(activity => {
          const method = getAgentMethods(activity.agentName)
            .find(m => m.name === activity.methodName);
          
          return (
            <AgentActivityCard
              key={activity.id}
              agent={activity.agentName}
              method={method}
              timestamp={activity.timestamp}
            />
          );
        })}
      </div>
    </div>
  );
}
```

## Backend Event Emission

To make this work, the backend needs to emit events when agents execute methods:

```python
from app.ai_agents.agent_introspection import get_agent_methods

class InstrumentedAgent(BaseAIAgent):
    async def process_metrics(self, metrics, user_context=None):
        # Emit method start event
        await self.emit_event({
            'type': 'method_start',
            'agent_name': self.agent_name,
            'method_name': 'process_metrics',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        try:
            result = await self._actual_process_metrics(metrics, user_context)
            
            # Emit method end event
            await self.emit_event({
                'type': 'method_end',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'timestamp': datetime.utcnow().isoformat(),
                'success': True
            })
            
            return result
        except Exception as e:
            await self.emit_event({
                'type': 'method_error',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            raise
```

## WebSocket Event Structure

```typescript
interface AgentMethodEvent {
  type: 'method_start' | 'method_end' | 'method_error';
  agent_name: string;
  method_name: string;
  timestamp: string;
  state_changes?: Record<string, any>;
  method_calls?: string[];
  success?: boolean;
  error?: string;
}

interface AgentStateChangeEvent {
  type: 'state_change';
  agent_name: string;
  variable_name: string;
  old_value: any;
  new_value: any;
  timestamp: string;
}
```

## Regenerating Mappings

Whenever you modify agent code or add new metrics:

```bash
# Regenerate metric mappings
python backend/resource_monitor_ast.py

# Regenerate agent introspection
python backend/agent_introspection_ast.py
```

Add this to your development workflow or CI/CD pipeline.

## Benefits

1. **Type Safety**: Frontend knows exact structure of agents and metrics
2. **Auto-Documentation**: Docstrings and type info available in UI
3. **Real-Time Debugging**: See exactly what agents are doing
4. **Performance Analysis**: Correlate agent activity with system metrics
5. **User Engagement**: Visual representation makes AI agents tangible
6. **Development Speed**: No manual mapping between backend and frontend

## Future Enhancements

1. **Decorator-based instrumentation**: Automatically emit events for all methods
2. **Performance profiling**: Track execution time per method
3. **Call stack visualization**: Show nested method calls
4. **State history**: Track state variable changes over time
5. **Agent collaboration patterns**: Detect and visualize common interaction patterns
6. **Predictive UI**: Use method categories to predict what agent will do next
7. **Interactive debugging**: Trigger specific agent methods from UI

## Example: Complete Agent Theater Component

```typescript
import { 
  AGENT_INTROSPECTION_DATA, 
  getAgentMethods, 
  getAllAgentNames 
} from '@/types/agentIntrospection';
import { METRIC_KEYS } from '@/types/metricKeys';

export function AgentTheater() {
  const [agentEvents, setAgentEvents] = useState({});
  const [metrics, setMetrics] = useState({});
  
  useEffect(() => {
    // Subscribe to WebSocket events
    const ws = new WebSocket('ws://localhost:8000/ws/agent-events');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'method_start' || data.type === 'method_end') {
        setAgentEvents(prev => ({
          ...prev,
          [data.agent_name]: {
            method: data.method_name,
            timestamp: data.timestamp,
            // Enrich with introspection data
            methodInfo: getAgentMethods(data.agent_name)
              .find(m => m.name === data.method_name)
          }
        }));
      }
      
      if (data.type === 'metrics_update') {
        setMetrics(data.metrics);
      }
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="agent-theater">
      <div className="agents-stage">
        {getAllAgentNames().map(agentName => (
          <AgentCharacter
            key={agentName}
            name={agentName}
            currentActivity={agentEvents[agentName]}
            agentData={AGENT_INTROSPECTION_DATA[agentName]}
          />
        ))}
      </div>
      
      <div className="metrics-sidebar">
        {Object.entries(METRIC_KEYS).map(([key, value]) => (
          <MetricDisplay
            key={value}
            metricKey={value}
            value={metrics[value]}
          />
        ))}
      </div>
    </div>
  );
}
```

## Conclusion

This AST-based introspection system creates a bridge between your backend agent code and frontend UI, enabling rich, real-time visualization of agent behavior without manual mapping or hardcoded references. The system is type-safe, self-documenting, and automatically updates when you modify your agent code.
