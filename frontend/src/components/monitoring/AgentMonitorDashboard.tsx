import { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store/store';

interface AgentEvent {
  timestamp: string;
  agent: string;
  category: 'redis' | 'postgres' | 'vector' | 'system';
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}

interface AgentStatus {
  name: string;
  emoji: string;
  status: 'active' | 'idle' | 'error';
  uptime: string;
  events: {
    redis: AgentEvent[];
    postgres: AgentEvent[];
    vector: AgentEvent[];
    system: AgentEvent[];
  };
}

const AGENTS = [
  { name: 'sir_hawkington', emoji: '🧐', displayName: 'Sir Hawkington' },
  { name: 'vic_20_sage', emoji: '🖥️', displayName: 'VIC-20 Sage' },
  { name: 'meth_snail', emoji: '🐌', displayName: 'Terry (Meth Snail)' },
  { name: 'hamsters', emoji: '🐹', displayName: 'The Hamsters' },
  { name: 'quantum_shadow_people', emoji: '👻', displayName: 'Quantum Shadow People' },
  { name: 'the_stick', emoji: '📏', displayName: 'The Stick' },
  { name: 'system', emoji: '⚙️', displayName: 'System' },
];

export function AgentMonitorDashboard() {
  const [agents, setAgents] = useState<Map<string, AgentStatus>>(new Map());
  const startTimeRef = useRef<Date>(new Date());
  const messageQueueRef = useRef<any[]>([]);
  
  // Use existing WebSocket connection from Redux
  const metrics = useSelector((state: RootState) => state.metrics);
  const connected = metrics.connectionStatus === 'connected';

  useEffect(() => {
    // Initialize agent states
    const initialAgents = new Map<string, AgentStatus>();
    AGENTS.forEach(agent => {
      initialAgents.set(agent.name, {
        name: agent.name,
        emoji: agent.emoji,
        status: 'idle',
        uptime: '0s',
        events: {
          redis: [],
          postgres: [],
          vector: [],
          system: [],
        },
      });
    });
    setAgents(initialAgents);
    startTimeRef.current = new Date();
  }, []);

  // Process metrics data from Redux
  useEffect(() => {
    if (metrics.data?.agents) {
      // Update agent status from backend data
      setAgents(prev => {
        const updated = new Map(prev);
        
        metrics.data.agents.forEach((agentData: any) => {
          const agentName = agentData.agent_name;
          const existing = updated.get(agentName);
          
          if (existing) {
            // Add message stats as events
            if (agentData.distributed?.messages_sent > 0) {
              const event: AgentEvent = {
                timestamp: new Date().toISOString(),
                agent: agentName,
                category: 'redis',
                message: `Sent ${agentData.distributed.messages_sent} messages`,
                level: 'info'
              };
              const redisEvents = [...existing.events.redis, event].slice(-5);
              updated.set(agentName, {
                ...existing,
                status: agentData.is_active ? 'active' : 'idle',
                events: { ...existing.events, redis: redisEvents }
              });
            }
            
            // Add decision stats
            if (agentData.total_decisions > 0) {
              const event: AgentEvent = {
                timestamp: new Date().toISOString(),
                agent: agentName,
                category: 'system',
                message: `Total decisions: ${agentData.total_decisions}`,
                level: 'success'
              };
              const systemEvents = [...existing.events.system, event].slice(-5);
              updated.set(agentName, {
                ...existing,
                events: { ...existing.events, system: systemEvents }
              });
            }
          }
        });
        
        return updated;
      });
    }
    
    // Process recent insights
    if (metrics.data?.recent_insights) {
      metrics.data.recent_insights.forEach((insight: any) => {
        handleAgentEvent({
          type: 'agent_insight',
          from_agent: insight.from_agent,
          ...insight
        });
      });
    }
  }, [metrics.data]);

  // Listen to real-time WebSocket messages
  useEffect(() => {

    // Update uptime every second
    const uptimeInterval = setInterval(() => {
      setAgents(prev => {
        const updated = new Map(prev);
        const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        const uptimeStr = hours > 0 
          ? `${hours}h ${minutes}m`
          : minutes > 0
          ? `${minutes}m ${seconds}s`
          : `${seconds}s`;
        
        updated.forEach((agent, key) => {
          updated.set(key, { ...agent, uptime: uptimeStr });
        });
        return updated;
      });
    }, 1000);

    return () => {
      clearInterval(uptimeInterval);
    };
  }, [metrics]);

  const handleAgentEvent = (data: any) => {
    // Skip heartbeat and connection messages
    if (data.type === 'heartbeat' || data.type === 'connected' || data.type === 'pong' || data.type === 'connection_established' || data.type === 'system_info' || data.type === 'agent_roster' || data.type === 'persist_result' || data.type === 'system_update') {
      return;
    }

    // Handle agent_log messages (backend logs)
    if (data.type === 'agent_log') {
      const agentName = data.agent_name;
      const message = data.message;
      const category = data.category as 'redis' | 'postgres' | 'vector' | 'system';
      const level = data.level as 'info' | 'warning' | 'error' | 'success';
      
      const event: AgentEvent = {
        timestamp: data.timestamp,
        agent: agentName,
        category,
        message,
        level
      };
      
      setAgents(prev => {
        const updated = new Map(prev);
        const agent = updated.get(agentName);
        if (agent) {
          const categoryEvents = [...agent.events[category], event].slice(-10);
          updated.set(agentName, {
            ...agent,
            status: 'active',
            events: {
              ...agent.events,
              [category]: categoryEvents,
            },
          });
        }
        return updated;
      });
      return;
    }

    // Parse the event and categorize it
    let agentName = data.agent_name || data.from_agent || data.agent || 'system';
    
    // Normalize agent names
    if (agentName === 'vic20_sage' || agentName === 'vic_20') agentName = 'vic_20_sage';
    if (agentName === 'sir_hawkington' || agentName === 'hawkington') agentName = 'sir_hawkington';
    
    const message = data.message || data.reasoning || data.action || data.event_type || data.type || JSON.stringify(data);
    
    // Determine category based on message type and content
    let category: 'redis' | 'postgres' | 'vector' | 'system' = 'system';
    if (data.type === 'agent_message' || data.type === 'agent_insight') {
      category = 'redis';
    } else if (data.type === 'resource_alert') {
      category = 'system';
    } else if (message.includes('Redis') || message.includes('pub/sub') || message.includes('broadcast')) {
      category = 'redis';
    } else if (message.includes('PostgreSQL') || message.includes('database') || message.includes('wrote')) {
      category = 'postgres';
    } else if (message.includes('vector') || message.includes('embedding')) {
      category = 'vector';
    }

    // Determine level
    let level: 'info' | 'warning' | 'error' | 'success' = 'info';
    if (message.includes('✅') || message.includes('success')) {
      level = 'success';
    } else if (message.includes('⚠️') || message.includes('warning')) {
      level = 'warning';
    } else if (message.includes('💥') || message.includes('error') || message.includes('failed')) {
      level = 'error';
    }

    const event: AgentEvent = {
      timestamp: new Date().toISOString(),
      agent: agentName,
      category,
      message,
      level,
    };

    setAgents(prev => {
      const updated = new Map(prev);
      const agent = updated.get(agentName);
      if (agent) {
        const categoryEvents = [...agent.events[category], event].slice(-10); // Keep last 10
        updated.set(agentName, {
          ...agent,
          status: 'active',
          events: {
            ...agent.events,
            [category]: categoryEvents,
          },
        });
      }
      return updated;
    });
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
              🎯 Agent Monitor
            </h2>
            <p className="text-slate-400 text-sm">Real-time backend event streaming</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              <span className="text-sm text-slate-300">{connected ? 'Connected' : 'Disconnected'}</span>
            </div>
            <span className="text-sm text-slate-400">
              {Array.from(agents.values()).filter(a => a.status === 'active').length} / {agents.size} active
            </span>
          </div>
        </div>
      </div>

      {/* Agent Cards Grid - 2 rows of 3-4 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {AGENTS.map(agentConfig => {
          const agent = agents.get(agentConfig.name);
          if (!agent) return null;

          return (
            <div key={agent.name} className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700/50 overflow-hidden hover:border-cyan-500/50 transition-colors">
              {/* Agent Header */}
              <div className="bg-slate-900/50 p-4 border-b border-slate-700/50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{agent.emoji}</span>
                    <h3 className="font-bold text-slate-100">{agentConfig.displayName}</h3>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                </div>
                <div className="text-xs text-slate-400">
                  Uptime: {agent.uptime}
                </div>
              </div>

              {/* Event Categories */}
              <div className="p-4 space-y-3">
                <EventSection title="🔴 Redis" events={agent.events.redis} getLevelColor={getLevelColor} />
                <EventSection title="💾 PostgreSQL" events={agent.events.postgres} getLevelColor={getLevelColor} />
                <EventSection title="🔮 Vector" events={agent.events.vector} getLevelColor={getLevelColor} />
                <EventSection title="📊 System" events={agent.events.system} getLevelColor={getLevelColor} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function EventSection({ 
  title, 
  events, 
  getLevelColor 
}: { 
  title: string; 
  events: AgentEvent[]; 
  getLevelColor: (level: string) => string;
}) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-400 mb-1">{title}</h4>
      <div className="bg-slate-900/80 rounded p-2 h-20 overflow-y-auto text-xs space-y-1 font-mono">
        {events.length === 0 ? (
          <div className="text-slate-600 italic">No events</div>
        ) : (
          events.slice(-5).map((event, idx) => (
            <div key={idx} className={`${getLevelColor(event.level)} truncate`}>
              {new Date(event.timestamp).toLocaleTimeString()}: {event.message}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
