import type { WebSocketMessage } from '../components/agent-theater/agents/shared/types'

/**
 * Creates a coordination message between agents
 */
export const createCoordinationMessage = ({
  fromAgentId,
  toAgentIds,
  action,
  payload = {},
  correlationId,
}: {
  fromAgentId: string;
  toAgentIds: string | string[];
  action: string;
  payload?: Record<string, unknown>;
  correlationId?: string;
}): WebSocketMessage => {
  const recipients = Array.isArray(toAgentIds) ? toAgentIds : [toAgentIds];
  
  return {
    type: 'coordination',
    agentId: fromAgentId,
    agentType: 'hawkington', // Default to Hawkington as coordinator
    timestamp: new Date().toISOString(),
    source: 'frontend',
    correlationId: correlationId || `coord-${Date.now()}`,
    payload: {
      action,
      recipients,
      ...payload,
    },
  };
};

/**
 * Handles coordination messages from the WebSocket
 */
export const handleCoordinationMessage = (
  message: WebSocketMessage,
  handlers: Record<string, (payload: any) => void>
): boolean => {
  if (message.type !== 'coordination') return false;
  
  const { action, ...payload } = message.payload as { action: string };
  const handler = handlers[action];
  
  if (handler) {
    handler(payload);
    return true;
  }
  
  return false;
};

/**
 * Creates a message for the triage engine
 */
export const createTriageMessage = ({
  agentId,
  agentType,
  priority,
  metrics,
  context = {},
}: {
  agentId: string;
  agentType: string;
  priority: number;
  metrics: Record<string, unknown>;
  context?: Record<string, unknown>;
}): WebSocketMessage => ({
  type: 'triage',
  agentId,
  agentType,
  timestamp: new Date().toISOString(),
  source: 'frontend',
  payload: {
    priority,
    metrics,
    context,
  },
});

/**
 * Creates a message for the eidetic memory system
 */
export const createEideticMemoryMessage = ({
  agentId,
  eventType,
  data,
  timestamp = new Date().toISOString(),
}: {
  agentId: string;
  eventType: string;
  data: Record<string, unknown>;
  timestamp?: string;
}): WebSocketMessage => ({
  type: 'eidetic_memory',
  agentId,
  agentType: 'stick',
  timestamp,
  source: 'frontend',
  payload: {
    eventType,
    data,
  },
});

/**
 * Creates a message for VIC-20 agent coordination
 */
export const createVIC20CoordinationMessage = ({
  fromAgentId,
  toAgentId,
  command,
  parameters = {},
}: {
  fromAgentId: string;
  toAgentId: string;
  command: string;
  parameters?: Record<string, unknown>;
}): WebSocketMessage => ({
  type: 'vic20_coordination',
  agentId: fromAgentId,
  agentType: 'vic20',
  timestamp: new Date().toISOString(),
  source: 'frontend',
  payload: {
    command,
    targetAgent: toAgentId,
    parameters,
  },
});
