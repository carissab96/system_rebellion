# AST Introspection System

## What We Built

A complete AST (Abstract Syntax Tree) introspection system that automatically maps backend Python code to frontend TypeScript, enabling real-time visualization of agent behavior in the UI.

## Files Created

### 1. Core Tools

#### `resource_monitor_ast.py`
Extracts metric collection functions from `resource_monitor.py`

**Extracts:**
- Metric function names and keys
- Async/sync status
- TypeScript type mappings

**Generates:**
- `frontend/src/types/metricKeys.ts` - TypeScript constants
- `backend/app/optimization/metric_keys.py` - Python constants

**Run:**
```bash
python backend/resource_monitor_ast.py
```

#### `agent_introspection_ast.py`
Extracts complete agent class structures

**Extracts:**
- Agent classes with base classes and docstrings
- Methods with parameters, return types, categories
- State variables with types
- Method calls and state changes
- Documentation strings

**Generates:**
- `frontend/src/types/agentIntrospection.ts` - TypeScript interfaces and data
- `backend/app/ai_agents/agent_introspection.py` - Python helpers
- `backend/agent_introspection_data.json` - Raw JSON

**Run:**
```bash
python backend/agent_introspection_ast.py
```

### 2. Documentation

#### `AGENT_VISUALIZATION_GUIDE.md`
Complete guide on how to use the introspection system for UI visualization

**Includes:**
- Architecture overview
- 5 visualization strategies with code examples
- WebSocket event structures
- Backend instrumentation patterns
- Complete React component examples

## Quick Start

### 1. Generate Mappings

```bash
# From backend directory
python resource_monitor_ast.py
python agent_introspection_ast.py
```

### 2. Use in Frontend

```typescript
// Import metric keys
import { METRIC_KEYS, METRIC_METADATA } from '@/types/metricKeys';

// Import agent introspection
import { 
  AGENT_INTROSPECTION_DATA, 
  getAgentMethods,
  getAgentStateVariables 
} from '@/types/agentIntrospection';

// Get all methods for an agent
const methods = getAgentMethods('sir_hawkington');

// Get methods by category
const coreProcessing = getAgentMethods('sir_hawkington', 'core_processing');

// Get state variables
const stateVars = getAgentStateVariables('sir_hawkington');

// Use metric keys
console.log(METRIC_KEYS.CPU_USAGE); // 'cpu_usage'
console.log(METRIC_METADATA.cpu_usage.type); // 'number'
```

### 3. Use in Backend

```python
# Import metric keys
from app.optimization.metric_keys import METRIC_KEYS, ALL_METRIC_KEYS

# Import agent introspection
from app.ai_agents.agent_introspection import (
    get_agent_methods,
    get_agent_state_variables
)

# Get methods
methods = get_agent_methods('sir_hawkington', category='core_processing')

# Get all metric keys
for key in ALL_METRIC_KEYS:
    print(f"Metric: {key}")
```

## Visualization Strategies

### 1. Real-Time Method Execution Tracking
Show which agent methods are currently executing with full metadata

### 2. State Variable Monitoring
Display agent state variables and track changes over time

### 3. Agent Theater Visualization
Visual representation of agents as characters performing actions

### 4. Method Call Flow Visualization
Show how agents interact and call each other's methods

### 5. Performance Metrics Dashboard
Correlate system metrics with agent method execution

## Method Categories

The introspection system automatically categorizes methods:

- **`core_processing`** - Main processing methods (process_metrics, analyze, etc.)
- **`getter`** - Methods that retrieve data (get_*, _get_*)
- **`setter`** - Methods that set data (set_*, _set_*)
- **`handler`** - Event/request handlers (handle_*)
- **`initialization`** - Setup methods (initialize, init, setup)
- **`monitoring`** - Health/status methods (health_check, get_status)
- **`private`** - Private methods (starting with _)
- **`public`** - Public methods
- **`dunder`** - Magic methods (__init__, __str__, etc.)

## Data Structure Examples

### Metric Keys Output

```typescript
export const METRIC_KEYS = {
  CPU_USAGE: 'cpu_usage',
  MEMORY_USAGE: 'memory_usage',
  DISK_USAGE: 'disk_usage',
  // ... more keys
} as const;

export const METRIC_METADATA = {
  'cpu_usage': {
    key: 'cpu_usage',
    functionName: '_get_cpu_usage',
    isAsync: true,
    type: 'number',
  },
  // ... more metadata
} as const;
```

### Agent Introspection Output

```typescript
export interface AgentMethod {
  name: string;
  isAsync: boolean;
  isAbstract: boolean;
  isPrivate: boolean;
  category: string;
  parameters: Array<{ name: string; annotation: string | null }>;
  returnType: string | null;
  docstring: string | null;
  stateChanges: string[];  // Which self.* variables are modified
  methodCalls: Array<{ object: string | null; method: string }>;
}

export interface AgentClass {
  name: string;
  filePath: string;
  baseClasses: string[];
  docstring: string | null;
  methods: AgentMethod[];
  stateVariables: AgentStateVariable[];
  lineNumber: number;
}
```

## Example: Agent Theater Component

```typescript
import { getAgentMethods, getAllAgentNames } from '@/types/agentIntrospection';

export function AgentTheater() {
  const [agentEvents, setAgentEvents] = useState({});
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/agent-events');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'method_start') {
        setAgentEvents(prev => ({
          ...prev,
          [data.agent_name]: {
            method: data.method_name,
            methodInfo: getAgentMethods(data.agent_name)
              .find(m => m.name === data.method_name)
          }
        }));
      }
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="agent-theater">
      {getAllAgentNames().map(agentName => (
        <AgentCharacter
          key={agentName}
          name={agentName}
          currentActivity={agentEvents[agentName]}
        />
      ))}
    </div>
  );
}
```

## Backend Event Emission

To enable real-time visualization, emit events when methods execute:

```python
class InstrumentedAgent(BaseAIAgent):
    async def process_metrics(self, metrics, user_context=None):
        # Emit start event
        await self.emit_event({
            'type': 'method_start',
            'agent_name': self.agent_name,
            'method_name': 'process_metrics',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        try:
            result = await self._actual_process_metrics(metrics, user_context)
            
            # Emit end event with state changes
            await self.emit_event({
                'type': 'method_end',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'state_changes': self._get_state_snapshot(),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return result
        except Exception as e:
            await self.emit_event({
                'type': 'method_error',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'error': str(e)
            })
            raise
```

## Benefits

✅ **Type Safety** - Frontend knows exact structure of agents and metrics
✅ **Auto-Documentation** - Docstrings and type info available in UI
✅ **Real-Time Debugging** - See exactly what agents are doing
✅ **Performance Analysis** - Correlate agent activity with system metrics
✅ **User Engagement** - Visual representation makes AI agents tangible
✅ **Development Speed** - No manual mapping between backend and frontend
✅ **Maintainability** - Changes to backend automatically reflected in frontend types

## Workflow Integration

Add to your development workflow:

```bash
# Add to package.json scripts
"scripts": {
  "generate:mappings": "python backend/resource_monitor_ast.py && python backend/agent_introspection_ast.py",
  "dev": "npm run generate:mappings && vite"
}
```

Or add to pre-commit hooks:

```bash
#!/bin/bash
# .git/hooks/pre-commit

cd backend
python resource_monitor_ast.py
python agent_introspection_ast.py

# Add generated files to commit
git add ../frontend/src/types/metricKeys.ts
git add ../frontend/src/types/agentIntrospection.ts
git add app/optimization/metric_keys.py
git add app/ai_agents/agent_introspection.py
```

## Next Steps

1. **Instrument your agents** - Add event emission to agent methods
2. **Create WebSocket endpoint** - Stream agent events to frontend
3. **Build UI components** - Use the introspection data to create visualizations
4. **Add state tracking** - Emit state changes when variables are modified
5. **Performance profiling** - Track execution time per method
6. **Interactive debugging** - Trigger agent methods from UI

## Troubleshooting

### No agents found
- Check that agent classes inherit from `BaseAIAgent` or have "Agent" in the class name
- Verify the agents directory path is correct

### Missing methods
- Ensure methods are defined at class level (not nested)
- Check for syntax errors in the source file

### Type mismatches
- Update `METRIC_TYPE_MAPPING` in `resource_monitor_ast.py` for new metric types
- Regenerate mappings after changes

## Summary

This AST introspection system creates a powerful bridge between your Python backend and TypeScript frontend, enabling:

- **Automatic code mapping** without manual maintenance
- **Type-safe** references to backend structures
- **Real-time visualization** of agent behavior
- **Self-documenting** UI with docstrings and type info
- **Performance monitoring** correlated with agent activity

The system is designed to be **zero-maintenance** - just run the scripts when you modify your code, and the mappings automatically update.
