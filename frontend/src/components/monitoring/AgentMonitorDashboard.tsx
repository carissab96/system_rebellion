import { useState, useEffect, useRef } from 'react';

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
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const startTimeRef = useRef<Date>(new Date());

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

    // Connect to WebSocket
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No auth token found');
      return;
    }

    // Use environment variable for WebSocket URL
    const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/agent-events?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ Connected to agent events WebSocket');
      setConnected(true);
      startTimeRef.current = new Date();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleAgentEvent(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = () => {
      console.log('❌ Disconnected from agent events WebSocket');
      setConnected(false);
    };

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
      ws.close();
    };
  }, []);

  const handleAgentEvent = (data: any) => {
    // Parse the event and categorize it
    const agentName = data.agent_name || data.from_agent || 'system';
    const message = data.message || data.event_type || JSON.stringify(data);
    
    // Determine category based on message content
    let category: 'redis' | 'postgres' | 'vector' | 'system' = 'system';
    if (message.includes('Redis') || message.includes('pub/sub') || message.includes('broadcast')) {
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

      {/* Agent Cards Grid */}
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
