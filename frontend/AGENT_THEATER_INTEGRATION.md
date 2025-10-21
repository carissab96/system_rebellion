# Agent Theater Enhanced - Integration Guide

## What We Built

An enhanced Agent Theater that uses AST introspection data to visualize agent methods, state, and activity in real-time.

## Files Created

### Frontend Components

1. **`AgentMethodTracker.tsx`** - Displays agent methods with full introspection data
   - Shows active method execution
   - Categorizes methods (core_processing, handler, getter, etc.)
   - Displays parameters, return types, docstrings
   - Shows state changes and method calls

2. **`AgentTheaterEnhanced.tsx`** - Enhanced theater with introspection view
   - Toggle between Theater View and Introspection View
   - Agent selector panel with activity tracking
   - Method tracker panel showing real-time execution
   - Agent card preview

3. **CSS Files** - Styling for the enhanced components
   - `AgentMethodTracker.css`
   - `AgentTheaterEnhanced.css`

## How to Use

### Option 1: Replace Existing Agent Theater

Update your routing to use the enhanced version:

```typescript
// In your router file (e.g., App.tsx or routes.tsx)
import AgentTheaterEnhanced from './components/agent-theater/AgentTheaterEnhanced';

// Replace:
// <Route path="/agent-theater" element={<AgentTheater />} />

// With:
<Route path="/agent-theater" element={<AgentTheaterEnhanced />} />
```

### Option 2: Add as New Route

Keep both versions and add a new route:

```typescript
import AgentTheater from './components/agent-theater/AgentTheater';
import AgentTheaterEnhanced from './components/agent-theater/AgentTheaterEnhanced';

<Route path="/agent-theater" element={<AgentTheater />} />
<Route path="/agent-theater/enhanced" element={<AgentTheaterEnhanced />} />
```

## Features

### 🔍 Introspection View

- **Agent Selector Panel** (left)
  - Lists all available agents
  - Shows active status
  - Displays method count
  - Shows current activity

- **Method Tracker Panel** (center)
  - Full method introspection data
  - Active method highlighting
  - Method categories with icons
  - Parameters and return types
  - State changes tracking
  - Method call chains
  - Docstrings and documentation

- **Agent Card Preview** (right)
  - Shows the traditional agent card
  - Updates based on selected agent

### 🎭 Theater View

- Traditional grid view of all agent cards
- Quick toggle to switch views

## Real-Time Updates

The component is ready for real-time WebSocket integration:

```typescript
// In your WebSocket handler
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'agent_method_start') {
    // Update agent activity
    setAgentActivities(prev => ({
      ...prev,
      [data.agent_name]: {
        agentName: data.agent_name,
        methodName: data.method_name,
        timestamp: data.timestamp,
        category: data.category,
      }
    }));
  }
};
```

## Backend Integration

To emit real-time method execution events, instrument your agents:

```python
# In your agent base class or specific agents
class InstrumentedAgent(BaseAIAgent):
    async def process_metrics(self, metrics, user_context=None):
        # Emit method start
        await self.emit_event({
            'type': 'agent_method_start',
            'agent_name': self.agent_name,
            'method_name': 'process_metrics',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        try:
            result = await self._actual_process(metrics, user_context)
            
            # Emit method end
            await self.emit_event({
                'type': 'agent_method_end',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return result
        except Exception as e:
            await self.emit_event({
                'type': 'agent_method_error',
                'agent_name': self.agent_name,
                'method_name': 'process_metrics',
                'error': str(e)
            })
            raise
```

## Customization

### Show Specific Method Categories

```typescript
<AgentMethodTracker
  agentName="sir_hawkington"
  activeMethod={currentMethod}
  showCategories={['core_processing', 'handler']} // Only show these categories
/>
```

### Styling

All colors and styles are in the CSS files. Key variables:

```css
/* Method category colors */
--core-processing: #4CAF50;
--getter: #2196F3;
--setter: #FF9800;
--handler: #9C27B0;
--monitoring: #00BCD4;
```

## Current Limitations

1. **Simulated Activity** - Currently uses random method selection for demo
   - Replace with real WebSocket events in production

2. **Limited Agent Data** - Some agents may not have introspection data yet
   - Run `python backend/agent_introspection_ast.py` to regenerate

3. **No State Tracking** - State variable values not yet tracked
   - Add state emission to backend agents

## Next Steps

1. **Connect Real WebSocket Events**
   - Update `useAgentEventsConnection` to handle method events
   - Parse and dispatch to component state

2. **Add State Variable Tracking**
   - Emit state changes from backend
   - Display in UI with history

3. **Add Performance Metrics**
   - Track method execution time
   - Show performance graphs

4. **Interactive Features**
   - Click method to see full details
   - Filter by method category
   - Search methods

5. **Agent Interaction Graph**
   - Visualize method call chains
   - Show agent-to-agent communication

## Testing

1. Start your backend:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to `/agent-theater` (or `/agent-theater/enhanced`)

4. Toggle between views using the buttons in the nav bar

5. Select different agents to see their introspection data

## Troubleshooting

### "No introspection data available"

Run the introspection tool:
```bash
cd backend
python agent_introspection_ast.py
```

### Agent not showing methods

Check that the agent class:
- Inherits from `BaseAIAgent` or has "Agent" in the class name
- Has methods defined at class level
- Is in the correct directory structure

### Import errors

Ensure the generated TypeScript files exist:
- `frontend/src/types/metricKeys.ts`
- `frontend/src/types/agentIntrospection.ts`

Run both generation scripts if missing:
```bash
cd backend
python resource_monitor_ast.py
python agent_introspection_ast.py
```

## Summary

You now have a fully functional enhanced Agent Theater that:

✅ Uses AST introspection data to show agent structure
✅ Displays methods with full documentation
✅ Categorizes methods for easy navigation
✅ Shows active method execution (ready for real-time)
✅ Toggles between traditional and introspection views
✅ Is ready for WebSocket integration
✅ Provides a foundation for advanced visualizations

The system brings your agents to life by making their internal workings visible and understandable in the UI!
