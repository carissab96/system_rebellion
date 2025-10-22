# AST Introspection - Quick Reference Card

## 🔧 Generate Mappings

```bash
cd backend
python resource_monitor_ast.py      # Extract metrics
python agent_introspection_ast.py   # Extract agents
```

## 📥 Import in Frontend

```typescript
// Metric keys
import { METRIC_KEYS, METRIC_METADATA } from '@/types/metricKeys';

// Agent introspection
import { 
  AGENT_INTROSPECTION_DATA,
  getAgentMethods,
  getAgentStateVariables,
  getAllAgentNames
} from '@/types/agentIntrospection';
```

## 📤 Import in Backend

```python
# Metric keys
from app.optimization.metric_keys import METRIC_KEYS, ALL_METRIC_KEYS

# Agent introspection
from app.ai_agents.agent_introspection import (
    get_agent_methods,
    get_agent_state_variables,
    get_all_agent_names
)
```

## 🎯 Common Usage

### Get Agent Methods

```typescript
// All methods
const methods = getAgentMethods('sir_hawkington');

// By category
const handlers = getAgentMethods('sir_hawkington', 'handler');
const processing = getAgentMethods('sir_hawkington', 'core_processing');
```

### Get Metric Keys

```typescript
// Access specific metric
const cpuKey = METRIC_KEYS.CPU_USAGE; // 'cpu_usage'

// Get metadata
const cpuMeta = METRIC_METADATA.cpu_usage;
console.log(cpuMeta.isAsync);      // true
console.log(cpuMeta.functionName); // '_get_cpu_usage'
```

### Check Agent Data

```typescript
// Get all agents
const agents = getAllAgentNames();

// Check if agent has data
const hasData = AGENT_INTROSPECTION_DATA['sir_hawkington']?.length > 0;

// Get agent class info
const agentClass = AGENT_INTROSPECTION_DATA['sir_hawkington'][0];
console.log(agentClass.methods.length);
console.log(agentClass.docstring);
```

## 🎭 Use Enhanced Theater

### Option 1: Replace Current Theater

```typescript
// In your router
import AgentTheaterEnhanced from './components/agent-theater/AgentTheaterEnhanced';

<Route path="/agent-theater" element={<AgentTheaterEnhanced />} />
```

### Option 2: Add New Route

```typescript
<Route path="/agent-theater/enhanced" element={<AgentTheaterEnhanced />} />
```

## 🔌 WebSocket Integration

### Frontend

```typescript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'agent_method_start') {
    setAgentActivities(prev => ({
      ...prev,
      [data.agent_name]: {
        agentName: data.agent_name,
        methodName: data.method_name,
        timestamp: data.timestamp,
      }
    }));
  }
};
```

### Backend

```python
await emit_event({
    'type': 'agent_method_start',
    'agent_name': self.agent_name,
    'method_name': 'process_metrics',
    'timestamp': datetime.utcnow().isoformat()
})
```

## 📊 Method Categories

| Category | Icon | Description |
|----------|------|-------------|
| `core_processing` | ⚙️ | Main processing methods |
| `getter` | 📥 | Data retrieval |
| `setter` | 📤 | Data modification |
| `handler` | 🎯 | Event handlers |
| `initialization` | 🚀 | Setup methods |
| `monitoring` | 📊 | Health/status |
| `private` | 🔒 | Private methods |
| `public` | 🌐 | Public methods |
| `dunder` | ✨ | Magic methods |

## 🎨 Customize Method Tracker

```typescript
<AgentMethodTracker
  agentName="sir_hawkington"
  activeMethod="process_metrics"
  showCategories={['core_processing', 'handler']}
/>
```

## 🐛 Troubleshooting

### No introspection data?
```bash
cd backend
python agent_introspection_ast.py
```

### Import errors?
Check files exist:
- `frontend/src/types/metricKeys.ts`
- `frontend/src/types/agentIntrospection.ts`

### Agent not showing?
Ensure agent class:
- Inherits from `BaseAIAgent` OR
- Has "Agent" in class name

## 📁 File Locations

### Generated Files
```
frontend/src/types/
  ├── metricKeys.ts
  └── agentIntrospection.ts

backend/app/
  ├── optimization/metric_keys.py
  └── ai_agents/agent_introspection.py
```

### Components
```
frontend/src/components/agent-theater/
  ├── AgentMethodTracker.tsx
  ├── AgentMethodTracker.css
  ├── AgentTheaterEnhanced.tsx
  └── AgentTheaterEnhanced.css
```

### Tools
```
backend/
  ├── resource_monitor_ast.py
  └── agent_introspection_ast.py
```

## 🔄 Workflow

1. **Modify agent code** → 2. **Run AST tools** → 3. **Mappings auto-update** → 4. **UI reflects changes**

## 💾 Add to Scripts

### package.json
```json
{
  "scripts": {
    "generate:mappings": "cd ../backend && python resource_monitor_ast.py && python agent_introspection_ast.py",
    "dev": "npm run generate:mappings && vite"
  }
}
```

### Pre-commit Hook
```bash
#!/bin/bash
cd backend
python resource_monitor_ast.py
python agent_introspection_ast.py
git add ../frontend/src/types/*.ts
git add app/optimization/metric_keys.py
git add app/ai_agents/agent_introspection.py
```

## 🎯 Quick Test

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Browser
http://localhost:5173/agent-theater
```

## 📚 Documentation

- **`INTROSPECTION_SUMMARY.md`** - Complete overview
- **`backend/AGENT_VISUALIZATION_GUIDE.md`** - 5 visualization strategies
- **`backend/AST_INTROSPECTION_README.md`** - Technical reference
- **`frontend/AGENT_THEATER_INTEGRATION.md`** - Integration guide

## ✨ That's It!

You now have everything you need to visualize your agents in real-time! 🎉
