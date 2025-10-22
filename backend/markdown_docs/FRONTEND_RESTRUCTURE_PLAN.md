# Frontend Restructure Implementation Plan
## Comprehensive Agent Field Mapping + Design System Integration

**Date**: October 13, 2025  
**Objective**: Restructure entire frontend to match backend field mappings and integrate design system  
**Estimated Time**: 3-4 days (systematic implementation)

---

## 📋 OVERVIEW

### What We're Fixing:
1. ❌ **Agent data structures don't match backend field mappings**
2. ❌ **Design system exists but not integrated**
3. ❌ **Fake/placeholder data throughout**
4. ❌ **Inconsistent styling (mix of CSS files, inline styles)**
5. ❌ **WebSocket data handling doesn't match new dual-write structure**

### What We're Building:
1. ✅ **Type-safe agent interfaces matching backend field mappings**
2. ✅ **Design system integrated via inline styles + CSS modules**
3. ✅ **Real data only - no fake fallbacks**
4. ✅ **Consistent visual identity across all pages**
5. ✅ **WebSocket handlers for dual-write data structure**

---

## 🎯 PHASE 1: TYPE SYSTEM & DATA STRUCTURES (Day 1)

### 1.1 Create Agent Type Definitions

**File**: `/frontend/src/types/agents.ts` (NEW)

```typescript
// ============================================================================
// AGENT TYPE DEFINITIONS - MATCHING BACKEND FIELD MAPPINGS
// ============================================================================

// Base agent interface
export interface BaseAgentMemory {
  memory_id: string;
  user_id: string;
  timestamp: string; // ISO datetime
  shared_with_central: boolean;
  central_memory_id: string;
}

// ============================================================================
// SIR HAWKINGTON - Quality Analysis & Triage
// ============================================================================
export interface SirHawkingtonMemory extends BaseAgentMemory {
  memory_category: 'quality_analysis' | 'quality_alert' | 'critical_analysis' | 'triage' | 'monocle_yeet';
  
  // Structured JSON fields
  data_quality_pattern: {
    cpu_valid?: boolean;
    memory_valid?: boolean;
    disk_valid?: boolean;
    analysis_depth?: string;
    monocle_yeeted?: boolean;
    metrics_complete?: boolean;
    triage_confidence?: number;
    missing_metrics?: string[];
    invalid_metrics?: string[];
    yeet_reason?: string;
    data_quality_failure?: boolean;
  } | null;
  
  triage_decision_context: {
    decision_type?: string;
    system_impact?: string;
    confidence?: number;
    stress_score?: number;
    severity?: string;
    routing?: string;
    target_agents?: string[];
    reasoning?: string;
    processing_time?: number;
    attempted_analysis?: boolean;
    data_validation_failed?: boolean;
    yeet_intensity?: string;
    requires_data_quality_review?: boolean;
  } | null;
  
  quality_threshold_adjustment: {
    thresholds_applied?: {
      concern?: number;
      alert?: number;
      critical?: number;
    };
    decision_alignment?: string;
    severity_thresholds?: {
      normal?: number;
      medium?: number;
      emergency?: number;
    };
    applied_severity?: string;
    minimum_required_metrics?: string[];
    metrics_present?: {
      cpu?: boolean;
      memory?: boolean;
      disk?: boolean;
    };
  } | null;
  
  // Numeric metrics (REAL or null)
  accuracy_improvement: number | null;
  false_positive_reduction: number | null;
}

// ============================================================================
// THE STICK - Compliance & Anxiety Management
// ============================================================================
export interface TheStickMemory extends BaseAgentMemory {
  // Structured JSON fields
  anxiety_pattern: {
    anxiety_impact?: number;
    paper_bags_triggered?: number;
    severity_level?: string;
    anxiety_multiplier?: number;
    panic_level?: string;
    paper_bags_consumed?: number;
    bob_involved?: boolean;
  } | null;
  
  compliance_tracking: {
    violation_type?: string;
    measured_value?: number;
    threshold_value?: number;
    anxiety_adjusted_threshold?: number;
    severity?: string;
    resolved?: boolean;
    paper_bags_triggered?: number;
  } | null;
  
  compliance_violations: {
    violation_type?: string;
    recommendation?: string;
    resolved?: boolean;
    timestamp?: string;
  } | null;
  
  hamster_behavior_log: {
    active_hamsters?: string[];
    locations?: Record<string, string>;
    infrastructure_risk?: string;
    stick_response?: string;
  } | null;
  
  paper_bag_moments: {
    consumed?: number;
    panic_level?: string;
    timestamp?: string;
  } | null;
  
  // Numeric metrics (REAL or null)
  anxiety_level: number | null;
  compliance_score: number | null;
  hyperventilation_count: number | null;
  bob_proximity_alerts: number | null;
}

// ============================================================================
// METH SNAIL - Optimization & Performance
// ============================================================================
export interface MethSnailMemory extends BaseAgentMemory {
  // Structured JSON fields
  optimization_pattern: {
    priority?: string;
    actions?: Array<Record<string, any>>;
    urgency?: string;
    analysis_depth?: string;
    estimated_impact?: Record<string, number>;
  } | null;
  
  shell_spin_correlation: {
    missing_metrics?: string[];
    invalid_metrics?: string[];
    reason?: string;
    data_quality_score?: number;
  } | null;
  
  jitter_threshold_learning: {
    current_jitter_level?: number;
    threshold_adjustment?: number;
    learning_rate?: number;
  } | null;
  
  // Numeric metrics (REAL or null)
  caffeine_level_context: number | null;
  performance_improvement: number | null;
  confidence_level: number | null;
}

// ============================================================================
// HAMSTERS - Infrastructure Engineering
// ============================================================================
export interface HamstersMemory extends BaseAgentMemory {
  contributing_hamster: 'steve' | 'bob' | 'carl' | 'collective';
  problem_type: string;
  
  // Structured JSON fields
  infrastructure_pattern: {
    intervention_type?: string;
    status?: string;
    tools_used?: string[];
  } | null;
  
  duct_tape_solution: {
    duct_tape_used?: Array<{
      grade?: string;
      amount_strips?: number;
      purpose?: string;
      applied_by?: string;
      effectiveness?: number;
    }>;
  } | null;
  
  beer_consumption_correlation: {
    beer_consumed?: number;
    intervention_success?: boolean;
  } | null;
  
  steve_contribution: {
    action?: string;
  } | null;
  
  bob_contribution: {
    action?: string;
  } | null;
  
  carl_contribution: {
    action?: string;
  } | null;
  
  stick_anxiety_trigger: {
    caused_anxiety?: boolean;
    anxiety_level?: number;
  } | null;
  
  // Numeric metrics (REAL or null)
  solution_effectiveness: number | null;
}

// ============================================================================
// QUANTUM SHADOW PEOPLE - Network Optimization
// ============================================================================
export interface QuantumShadowPeopleMemory extends BaseAgentMemory {
  // Structured JSON fields
  phase_pattern: {
    quantum_state?: string;
    network_target?: string;
    phase_shift_applied?: boolean;
  } | null;
  
  quantum_signature: {
    decision_type?: string;
    optimization_parameters?: Record<string, any>;
    mysterious_explanation?: string;
  } | null;
  
  dimensional_correlation: Record<string, any> | null;
  
  threat_pattern_recognition: Record<string, any> | null;
  
  network_anomaly_signatures: Record<string, any> | null;
  
  tequila_jello_correlation: {
    shots_required?: number;
    effectiveness_multiplier?: number;
    dimension_accessed?: string;
  } | null;
  
  // Numeric metrics (REAL or null)
  phase_shift_effectiveness: number | null;
  comprehensibility_score: number | null;
  quantum_confidence: number | null;
}

// ============================================================================
// VIC-20 SAGE - Coordination & Mediation
// ============================================================================
export interface VIC20Memory extends BaseAgentMemory {
  // Structured JSON fields
  coordination_pattern: {
    coordination_type?: string;
    agents_involved?: string[];
    strategy_applied?: string;
  } | null;
  
  mediation_insight: {
    conflict_detected?: boolean;
    mediation_required?: boolean;
    resolution_method?: string;
    success?: boolean;
  } | null;
  
  ancient_wisdom_application: {
    wisdom_applied?: string;
    relevance?: string;
    effectiveness?: number;
  } | null;
  
  conflict_resolution_method: Record<string, any> | null;
  
  agent_personality_patterns: Record<string, any> | null;
  
  successful_mediation_strategies: Record<string, any> | null;
  
  retro_computing_insight: Record<string, any> | null;
  
  // Numeric metrics (REAL or null)
  agent_harmony_score: number | null;
  coordination_efficiency: number | null;
  simplicity_effectiveness: number | null;
}

// ============================================================================
// WEBSOCKET MESSAGE TYPES
// ============================================================================
export interface AgentMemoryUpdate {
  type: 'agent_memory_update';
  agent_name: 'sir_hawkington' | 'the_stick' | 'meth_snail' | 'hamsters' | 'quantum_shadow_people' | 'vic20_sage';
  memory: SirHawkingtonMemory | TheStickMemory | MethSnailMemory | HamstersMemory | QuantumShadowPeopleMemory | VIC20Memory;
}

export interface MetricsUpdate {
  type: 'metrics_update';
  timestamp: string;
  data: {
    cpu_usage?: number;
    memory_usage?: number;
    disk_usage?: number;
    network_data?: {
      bytes_sent?: number;
      bytes_recv?: number;
    };
    process_count?: number;
  };
}

export interface TriageResult {
  type: 'triage_result';
  disposition: string;
  routed_by: string;
  agent_dispatch: string[];
  triage_decision: Record<string, any>;
}

// ============================================================================
// UI DISPLAY TYPES (Derived from memory data)
// ============================================================================
export interface AgentDisplayData {
  agent_name: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  last_activity: string | null;
  recent_memories: any[]; // Array of agent-specific memory types
  summary_stats: {
    total_events: number;
    recent_events_24h: number;
    avg_confidence?: number;
    effectiveness_score?: number;
  };
}
```

### 1.2 Update Redux Slices

**File**: `/frontend/src/store/slices/agentsSlice.ts` (REWRITE)

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type {
  SirHawkingtonMemory,
  TheStickMemory,
  MethSnailMemory,
  HamstersMemory,
  QuantumShadowPeopleMemory,
  VIC20Memory,
  AgentDisplayData
} from '../../types/agents';

interface AgentsState {
  // Recent memories for each agent (last 10)
  sir_hawkington: {
    recent_memories: SirHawkingtonMemory[];
    display_data: AgentDisplayData | null;
  };
  the_stick: {
    recent_memories: TheStickMemory[];
    display_data: AgentDisplayData | null;
  };
  meth_snail: {
    recent_memories: MethSnailMemory[];
    display_data: AgentDisplayData | null;
  };
  hamsters: {
    recent_memories: HamstersMemory[];
    display_data: AgentDisplayData | null;
  };
  quantum_shadow_people: {
    recent_memories: QuantumShadowPeopleMemory[];
    display_data: AgentDisplayData | null;
  };
  vic20_sage: {
    recent_memories: VIC20Memory[];
    display_data: AgentDisplayData | null;
  };
  
  // Aggregate state
  last_update: string | null;
  active_agents: string[];
}

const initialState: AgentsState = {
  sir_hawkington: { recent_memories: [], display_data: null },
  the_stick: { recent_memories: [], display_data: null },
  meth_snail: { recent_memories: [], display_data: null },
  hamsters: { recent_memories: [], display_data: null },
  quantum_shadow_people: { recent_memories: [], display_data: null },
  vic20_sage: { recent_memories: [], display_data: null },
  last_update: null,
  active_agents: []
};

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    addAgentMemory: (state, action: PayloadAction<{
      agent_name: keyof Omit<AgentsState, 'last_update' | 'active_agents'>;
      memory: any; // Type varies by agent
    }>) => {
      const { agent_name, memory } = action.payload;
      const agent = state[agent_name];
      
      // Add to recent memories (keep last 10)
      agent.recent_memories = [memory, ...agent.recent_memories].slice(0, 10);
      
      // Update display data
      agent.display_data = {
        agent_name,
        status: 'active',
        last_activity: memory.timestamp,
        recent_memories: agent.recent_memories,
        summary_stats: {
          total_events: agent.recent_memories.length,
          recent_events_24h: agent.recent_memories.filter(m => {
            const memTime = new Date(m.timestamp).getTime();
            const dayAgo = Date.now() - 24 * 60 * 60 * 1000;
            return memTime > dayAgo;
          }).length,
        }
      };
      
      state.last_update = new Date().toISOString();
      
      // Update active agents list
      if (!state.active_agents.includes(agent_name)) {
        state.active_agents.push(agent_name);
      }
    },
    
    clearAgentMemories: (state, action: PayloadAction<string>) => {
      const agent_name = action.payload as keyof Omit<AgentsState, 'last_update' | 'active_agents'>;
      state[agent_name].recent_memories = [];
      state[agent_name].display_data = null;
    },
    
    resetAllAgents: (state) => {
      return initialState;
    }
  }
});

export const { addAgentMemory, clearAgentMemories, resetAllAgents } = agentsSlice.actions;
export default agentsSlice.reducer;
```

---

## 🎨 PHASE 2: DESIGN SYSTEM INTEGRATION (Day 1-2)

### 2.1 Create CSS Module Templates

**File**: `/frontend/src/styles/modules/AgentCard.module.css` (NEW)

```css
/* Agent Card Component Styles */
.agentCard {
  background: var(--rebellion-surface);
  border: 1px solid var(--rebellion-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-rebellion);
}

.agentCard.hawkington {
  border-left: 4px solid var(--hawkington-gold);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(230, 172, 0, 0.05));
}

.agentCard.stick {
  border-left: 4px solid var(--stick-coral);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(249, 115, 22, 0.05));
}

.agentCard.snail {
  border-left: 4px solid var(--snail-electric);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(0, 208, 132, 0.05));
}

.agentCard.hamsters {
  border-left: 4px solid var(--hamster-amber);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(255, 140, 66, 0.05));
}

.agentCard.qsp {
  border-left: 4px solid var(--qsp-violet);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(168, 85, 247, 0.05));
}

.agentCard.vic20 {
  border-left: 4px solid var(--vic20-cyan);
  background: linear-gradient(135deg, var(--rebellion-surface), rgba(6, 182, 212, 0.05));
}

.agentHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.agentName {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--rebellion-text-bright);
  margin: 0;
}

.agentStatus {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
}

.agentStatus.active {
  background: rgba(34, 197, 94, 0.15);
  color: var(--success);
  border: 1px solid var(--success);
}

.agentStatus.idle {
  background: rgba(156, 163, 175, 0.15);
  color: var(--rebellion-text-dim);
  border: 1px solid var(--rebellion-border);
}

.agentMetrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-md);
  margin-top: var(--space-md);
}

.metricItem {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.metricLabel {
  font-size: 0.875rem;
  color: var(--rebellion-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.metricValue {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--rebellion-text-bright);
}
```

### 2.2 Create Reusable Agent Components

**File**: `/frontend/src/components/agents/AgentCard.tsx` (NEW)

```typescript
import React from 'react';
import type { AgentDisplayData } from '../../types/agents';
import styles from '../../styles/modules/AgentCard.module.css';

interface AgentCardProps {
  agent: AgentDisplayData;
  agentType: 'hawkington' | 'stick' | 'snail' | 'hamsters' | 'qsp' | 'vic20';
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, agentType }) => {
  const agentColors = {
    hawkington: '#e6ac00',
    stick: '#f97316',
    snail: '#00d084',
    hamsters: '#ff8c42',
    qsp: '#a855f7',
    vic20: '#06b6d4'
  };

  return (
    <div className={`${styles.agentCard} ${styles[agentType]}`}>
      <div className={styles.agentHeader}>
        <h3 
          className={styles.agentName}
          style={{ color: agentColors[agentType] }}
        >
          {agent.agent_name.replace(/_/g, ' ').toUpperCase()}
        </h3>
        <span className={`${styles.agentStatus} ${styles[agent.status]}`}>
          {agent.status}
        </span>
      </div>

      <div className={styles.agentMetrics}>
        <div className={styles.metricItem}>
          <span className={styles.metricLabel}>Total Events</span>
          <span className={styles.metricValue}>
            {agent.summary_stats.total_events}
          </span>
        </div>
        
        <div className={styles.metricItem}>
          <span className={styles.metricLabel}>Last 24h</span>
          <span className={styles.metricValue}>
            {agent.summary_stats.recent_events_24h}
          </span>
        </div>
        
        {agent.summary_stats.avg_confidence !== undefined && (
          <div className={styles.metricItem}>
            <span className={styles.metricLabel}>Avg Confidence</span>
            <span className={styles.metricValue}>
              {(agent.summary_stats.avg_confidence * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {agent.last_activity && (
        <div style={{
          marginTop: 'var(--space-md)',
          paddingTop: 'var(--space-md)',
          borderTop: '1px solid var(--rebellion-border)',
          fontSize: '0.875rem',
          color: 'var(--rebellion-text-dim)'
        }}>
          Last activity: {new Date(agent.last_activity).toLocaleString()}
        </div>
      )}
    </div>
  );
};
```

---

## 🔌 PHASE 3: WEBSOCKET INTEGRATION (Day 2)

### 3.1 Update WebSocket Service

**File**: `/frontend/src/services/websocket.ts` (UPDATE)

```typescript
import { store } from '../store/store';
import { addAgentMemory } from '../store/slices/agentsSlice';
import { updateMetrics } from '../store/slices/metricsSlice';
import type { AgentMemoryUpdate, MetricsUpdate } from '../types/agents';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(token: string) {
    const wsUrl = `ws://localhost:8000/api/ws/system-metrics?token=${token}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.attemptReconnect(token);
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'agent_memory_update':
        this.handleAgentMemoryUpdate(message as AgentMemoryUpdate);
        break;
      
      case 'metrics_update':
        this.handleMetricsUpdate(message as MetricsUpdate);
        break;
      
      case 'triage_result':
        console.log('Triage result:', message);
        // Handle triage results
        break;
      
      case 'connection_established':
        console.log('Connection established:', message);
        break;
      
      case 'system_info':
        console.log('System info:', message);
        break;
      
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private handleAgentMemoryUpdate(message: AgentMemoryUpdate) {
    store.dispatch(addAgentMemory({
      agent_name: message.agent_name,
      memory: message.memory
    }));
  }

  private handleMetricsUpdate(message: MetricsUpdate) {
    store.dispatch(updateMetrics(message.data));
  }

  private attemptReconnect(token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;
      
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(token);
      }, delay);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const websocketService = new WebSocketService();
```

---

## 📄 PHASE 4: PAGE RESTRUCTURING (Day 2-3)

### 4.1 System Monitor Page (REWRITE)

**File**: `/frontend/src/pages/dashboard/SystemMonitorPage.tsx`

### 4.2 Agent Testing Page (REWRITE)

**File**: `/frontend/src/pages/dashboard/AgentTestingPage.tsx`

### 4.3 Memory Banks Page (REWRITE)

**File**: `/frontend/src/pages/dashboard/MemoryBanksPage.tsx`

### 4.4 Agent Theater (REWRITE)

**File**: `/frontend/src/components/agent-theater/AgentTheater.tsx`

---

## 🎭 PHASE 5: LANDING & ONBOARDING (Day 3-4)

### 5.1 Landing Page Integration

### 5.2 Onboarding Flow

### 5.3 Login/Signup Modals

### 5.4 Navigation & Profile

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Types & Data (Day 1)
- [ ] Create `/types/agents.ts` with all agent memory interfaces
- [ ] Update `agentsSlice.ts` with new structure
- [ ] Update `metricsSlice.ts` if needed
- [ ] Test Redux store with new types

### Phase 2: Design System (Day 1-2)
- [ ] Create CSS modules for agent cards
- [ ] Create CSS modules for metrics displays
- [ ] Create reusable `AgentCard` component
- [ ] Create reusable `MetricPanel` component
- [ ] Create reusable `AgentBadge` component
- [ ] Test design system components

### Phase 3: WebSocket (Day 2)
- [ ] Update WebSocket service with new message handlers
- [ ] Test agent memory updates
- [ ] Test metrics updates
- [ ] Test triage results
- [ ] Verify no fake data fallbacks

### Phase 4: Pages (Day 2-3)
- [ ] Rewrite SystemMonitorPage
- [ ] Rewrite AgentTestingPage
- [ ] Rewrite MemoryBanksPage
- [ ] Rewrite AgentTheater
- [ ] Test all pages with real data

### Phase 5: Landing & Auth (Day 3-4)
- [ ] Integrate design system into landing page
- [ ] Update onboarding flow
- [ ] Update login/signup modals
- [ ] Update navigation
- [ ] Update profile dropdown
- [ ] Remove all placeholder data

### Phase 6: Testing & Polish (Day 4)
- [ ] End-to-end testing
- [ ] Cross-browser testing
- [ ] Accessibility testing
- [ ] Performance testing
- [ ] Final design system audit

---

## 🚀 EXECUTION STRATEGY

### Workflow:
1. **Create new files first** (types, components)
2. **Update existing files** (slices, services)
3. **Rewrite pages one at a time**
4. **Test after each major change**
5. **Remove old code only after new code works**

### Testing Strategy:
- Test with real backend data
- Test with WebSocket disconnects
- Test with missing data (null values)
- Test with all 6 agents active
- Test with no agents active

### Rollback Plan:
- Keep old files as `.old` until verified
- Git commit after each phase
- Document breaking changes

---

## 📊 SUCCESS CRITERIA

✅ **All agent data matches backend field mappings**  
✅ **Design system integrated consistently**  
✅ **No fake/placeholder data anywhere**  
✅ **WebSocket handles all message types**  
✅ **All pages render correctly with real data**  
✅ **All pages render correctly with null data**  
✅ **Type safety throughout**  
✅ **Accessible and performant**

---

**Ready to begin implementation!** 🎯
