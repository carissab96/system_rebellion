import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Crown, Cpu, Zap, HardDrive, Wifi, Ruler, Settings } from 'lucide-react';
import type { RootState } from '../../store/store';
import { WebSocketService } from '../../services/websocket';

// Backend WebSocket message types (source of truth)
interface AgentMessage {
  type: 'agent_message';
  data: {
    message_id: string;
    message_type: string;
    priority: number;
    from_agent: string;
    timestamp: string;
    payload: {
      severity?: string;
      routing?: string;
      reasoning?: string;
      metrics_summary?: any;
    };
    redis_channel: string;
  };
}

interface ResourceAlert {
  type: 'resource_alert';
  data: {
    from_agent: string;
    timestamp: string;
    payload: {
      type: string;
      metrics: any;
    };
    redis_channel: string;
  };
}

interface LogEntry {
  timestamp: string;
  level: string;
  category: string;
  message: string;
}

interface AgentState {
  agent_name: string;
  icon: React.ComponentType<any>;
  color: string;
  displayName: string;
  is_active: boolean;
  logs: {
    redis: LogEntry[];
    postgres: LogEntry[];
    vector: LogEntry[];
    system: LogEntry[];
  };
}

const AGENT_CONFIG = {
  sir_hawkington: { icon: Crown, color: '#e6ac00', displayName: 'Sir Hawkington' },
  vic_20_sage: { icon: Cpu, color: '#06b6d4', displayName: 'VIC-20 Sage' },
  meth_snail: { icon: Zap, color: '#00d084', displayName: 'Terry (Meth Snail)' },
  hamsters: { icon: HardDrive, color: '#ff8c42', displayName: 'The Hamsters' },
  quantum_shadow_people: { icon: Wifi, color: '#a855f7', displayName: 'Quantum Shadow People' },
  the_stick: { icon: Ruler, color: '#f97316', displayName: 'The Stick' },
  system: { icon: Settings, color: '#64748b', displayName: 'System' },
};

export function AgentMonitorDashboard() {
  const [agents, setAgents] = useState<Map<string, AgentState>>(new Map());
  const metrics = useSelector((state: RootState) => state.metrics);
  const wsConnected = metrics.connectionStatus === 'connected';

  useEffect(() => {
    // Initialize agent states
    const initialAgents = new Map<string, AgentState>();
    Object.entries(AGENT_CONFIG).forEach(([name, config]) => {
      initialAgents.set(name, {
        agent_name: name,
        icon: config.icon,
        color: config.color,
        displayName: config.displayName,
        is_active: false,
        logs: {
          redis: [],
          postgres: [],
          vector: [],
          system: [],
        },
      });
    });
    setAgents(initialAgents);
  }, []);

  // Listen for agent messages from WebSocket
  useEffect(() => {
    const handleAgentMessage = (msg: AgentMessage | ResourceAlert) => {
      if (msg.type === 'agent_message') {
        const agentName = msg.data?.from_agent;
        if (!agentName) return;
        
        const reasoning = msg.data?.payload?.reasoning || msg.data?.message_type || 'Agent message';
        const severity = msg.data?.payload?.severity || 'info';
        
        setAgents(prev => {
          const updated = new Map(prev);
          const agent = updated.get(agentName);
          
          if (agent) {
            const logEntry: LogEntry = {
              timestamp: msg.data.timestamp,
              level: severity === 'high' || severity === 'emergency' ? 'error' : 
                     severity === 'medium' ? 'warning' : 'info',
              category: 'system',
              message: reasoning,
            };
            
            const systemLogs = [...agent.logs.system, logEntry].slice(-5);
            
            updated.set(agentName, {
              ...agent,
              is_active: true,
              logs: {
                ...agent.logs,
                system: systemLogs,
              },
            });
          }
          
          return updated;
        });
      } else if (msg.type === 'resource_alert') {
        const agentName = msg.data?.from_agent;
        const metrics = msg.data?.payload?.metrics;
        
        // Skip if no agent name or metrics
        if (!agentName) return;
        
        setAgents(prev => {
          const updated = new Map(prev);
          const agent = updated.get(agentName);
          
          if (agent) {
            // Build message with safe property access
            const cpuPct = metrics?.cpu_percent ?? metrics?.cpu ?? 'N/A';
            const memPct = metrics?.memory_percent ?? metrics?.memory ?? 'N/A';
            const diskPct = metrics?.disk_percent ?? metrics?.disk ?? 'N/A';
            
            const logEntry: LogEntry = {
              timestamp: msg.data.timestamp,
              level: 'info',
              category: 'system',
              message: metrics 
                ? `CPU: ${cpuPct}% | Memory: ${memPct}% | Disk: ${diskPct}%`
                : 'Resource alert received (no metrics)',
            };
            
            const systemLogs = [...agent.logs.system, logEntry].slice(-5);
            
            updated.set(agentName, {
              ...agent,
              is_active: true,
              logs: {
                ...agent.logs,
                system: systemLogs,
              },
            });
          }
          
          return updated;
        });
      }
    };

    // Subscribe to WebSocket messages
    const wsService = WebSocketService.getInstance(
      import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    );
    
    wsService.subscribe(handleAgentMessage);
    console.log('✅ AgentMonitor: Subscribed to WebSocket messages');
    
    return () => {
      wsService.unsubscribe(handleAgentMessage);
      console.log('❌ AgentMonitor: Unsubscribed from WebSocket messages');
    };
  }, []);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'info': return 'text-cyan-400';
      case 'debug': return 'text-gray-400';
      default: return 'text-slate-300';
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'bg-green-500' : 'bg-gray-500';
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
              Agent Monitor
            </h2>
            <p className="text-slate-400 text-sm">Real-time backend event streaming</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              <span className="text-sm text-slate-300">{wsConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            <span className="text-sm text-slate-400">
              {Array.from(agents.values()).filter(a => a.is_active).length} / {agents.size} active
            </span>
          </div>
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from(agents.values()).map(agent => {
          const Icon = agent.icon;
          
          return (
            <div 
              key={agent.agent_name} 
              className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700/50 overflow-hidden hover:border-cyan-500/50 transition-colors"
            >
              {/* Agent Header */}
              <div className="bg-slate-900/50 p-4 border-b border-slate-700/50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <Icon size={24} style={{ color: agent.color }} />
                    <h3 className="font-bold text-slate-100">{agent.displayName}</h3>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.is_active)}`} />
                </div>
              </div>

              {/* Event Categories */}
              <div className="p-4 space-y-3">
                <LogSection title="Redis" logs={agent.logs.redis} getLevelColor={getLevelColor} />
                <LogSection title="PostgreSQL" logs={agent.logs.postgres} getLevelColor={getLevelColor} />
                <LogSection title="Vector" logs={agent.logs.vector} getLevelColor={getLevelColor} />
                <LogSection title="System" logs={agent.logs.system} getLevelColor={getLevelColor} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function LogSection({ 
  title, 
  logs, 
  getLevelColor 
}: { 
  title: string; 
  logs: LogEntry[]; 
  getLevelColor: (level: string) => string;
}) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-400 mb-1">{title}</h4>
      <div className="bg-slate-900/80 rounded p-2 h-20 overflow-y-auto text-xs space-y-1 font-mono">
        {logs.length === 0 ? (
          <div className="text-slate-600 italic">No events</div>
        ) : (
          logs.slice(-5).map((log, idx) => (
            <div key={idx} className={`${getLevelColor(log.level)} truncate`} title={log.message}>
              {new Date(log.timestamp).toLocaleTimeString()}: {log.message}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
