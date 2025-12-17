import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { selectRecentCommunications } from '../../store/slices/communicationSlice';
import { ArrowRight, GitBranch } from 'lucide-react';

/**
 * Agent Coordination Flow Visualizer - Real Decision Chains
 * 
 * CRITICAL RULE: All flows visualized from ACTUAL agent-to-agent messages.
 * NO fake data, NO simulated coordination, NO placeholder flows.
 * 
 * Data Sources:
 * - Real TRIAGE_ALERT messages from Hawkington
 * - Real COORDINATION_REQUEST messages from VIC-20
 * - Real agent_insight messages showing actions taken
 * - Real message chains showing decision → coordination → action flow
 */

interface CoordinationFlow {
  id: string;
  timestamp: string;
  chain: CoordinationStep[];
  status: 'active' | 'completed' | 'failed';
}

interface CoordinationStep {
  agent: string;
  action: string;
  timestamp: string;
  messageType: string;
  toAgent?: string;
}

const AGENT_COLORS: Record<string, string> = {
  sir_hawkington: '#e6ac00',
  vic20_sage: '#06b6d4',
  meth_snail: '#00d084',
  the_stick: '#f97316',
  hamsters: '#ff8c42',
  quantum_shadow_people: '#a855f7',
};

const AGENT_DISPLAY_NAMES: Record<string, string> = {
  sir_hawkington: 'Hawkington',
  vic20_sage: 'VIC-20',
  meth_snail: 'Terry',
  the_stick: 'Stick',
  hamsters: 'Hamsters',
  quantum_shadow_people: 'QSP',
};

export function AgentCoordinationFlow() {
  const recentCommunications = useSelector(selectRecentCommunications);
  const [coordinationFlows, setCoordinationFlows] = useState<CoordinationFlow[]>([]);

  useEffect(() => {
    // Build coordination flows from REAL messages
    const flows: Map<string, CoordinationFlow> = new Map();
    
    // Process messages in reverse chronological order to build chains
    const messages = [...recentCommunications].slice(0, 50); // Last 50 real messages
    
    messages.forEach(msg => {
      const fromAgent = msg.from_agent;
      const toAgent = msg.to_agent;
      const timestamp = msg.timestamp || new Date().toISOString();
      const messageType = msg.message_type;
      
      // Cast to any to access dynamic backend fields (real data from WebSocket)
      const msgData = msg as any;
      
      // Detect coordination chains
      let flowId: string | null = null;
      let action = '';
      
      // Start of chain: Hawkington's triage alert
      if (messageType === 'TRIAGE_ALERT') {
        flowId = `triage-${timestamp}`;
        action = `Triage: ${msgData.context?.severity || 'alert'} → ${toAgent}`;
      }
      
      // Middle of chain: VIC-20's coordination request
      else if (messageType === 'COORDINATION_REQUEST') {
        // Try to link to existing triage flow
        const recentTriage = Array.from(flows.values()).find(
          f => f.chain[0]?.toAgent === fromAgent && 
               Date.parse(timestamp) - Date.parse(f.timestamp) < 10000 // Within 10 seconds
        );
        flowId = recentTriage?.id || `coord-${timestamp}`;
        action = `Coordinate: ${msgData.context?.action || 'request'} → ${toAgent}`;
      }
      
      // End of chain: Agent action execution
      else if (messageType === 'agent_insight') {
        const insightAction = msgData.action || '';
        
        // Link to existing coordination flow
        const recentCoord = Array.from(flows.values()).find(
          f => f.chain.some(step => step.toAgent === fromAgent) &&
               Date.parse(timestamp) - Date.parse(f.timestamp) < 30000 // Within 30 seconds
        );
        
        if (recentCoord && (
          insightAction.includes('cache_clear') ||
          insightAction.includes('paper_bag') ||
          insightAction.includes('coordinate')
        )) {
          flowId = recentCoord.id;
          
          if (insightAction === 'cache_clear_executed') {
            action = `Execute: Cache clear (${msgData.context?.followed_vic20 ? 'followed VIC-20' : 'override'})`;
          } else if (insightAction === 'cache_clear_success') {
            action = `Success: Freed ${msgData.context?.memory_freed_mb?.toFixed(1) || 0}MB`;
          } else if (insightAction === 'paper_bag_consumed') {
            action = `React: Paper bag consumed (${msgData.context?.reason})`;
          } else {
            action = `Action: ${insightAction}`;
          }
        }
      }
      
      // Add step to flow if we identified one
      if (flowId && action) {
        const step: CoordinationStep = {
          agent: fromAgent,
          action,
          timestamp,
          messageType,
          toAgent,
        };
        
        if (flows.has(flowId)) {
          const flow = flows.get(flowId)!;
          flow.chain.push(step);
          flow.status = messageType === 'agent_insight' && 
                       (msg.action === 'cache_clear_success' || msg.context?.success)
                       ? 'completed' : 'active';
        } else {
          flows.set(flowId, {
            id: flowId,
            timestamp,
            chain: [step],
            status: 'active',
          });
        }
      }
    });
    
    // Convert to array and sort by timestamp (newest first)
    const flowsArray = Array.from(flows.values())
      .sort((a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp))
      .slice(0, 10); // Show last 10 real coordination flows
    
    setCoordinationFlows(flowsArray);
  }, [recentCommunications]);

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffSecs = Math.floor(diffMs / 1000);
      
      if (diffSecs < 60) return `${diffSecs}s ago`;
      if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'failed': return 'text-red-400';
      case 'active': return 'text-yellow-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'active': return '⏳';
      default: return '•';
    }
  };

  return (
    <div className="w-full bg-slate-900/50 backdrop-blur-sm rounded-lg border border-slate-700/50 p-4">
      <div className="flex items-center gap-2 mb-4">
        <GitBranch className="w-5 h-5 text-purple-400" />
        <h3 className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
          Agent Coordination Flows
        </h3>
        <span className="text-xs text-slate-500 ml-auto">
          Real decision chains • {coordinationFlows.length} active
        </span>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {coordinationFlows.length === 0 ? (
          <div className="text-center text-slate-500 py-8">
            No coordination flows detected yet...
          </div>
        ) : (
          coordinationFlows.map(flow => (
            <div
              key={flow.id}
              className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50"
            >
              {/* Flow Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getStatusIcon(flow.status)}</span>
                  <span className={`text-sm font-semibold ${getStatusColor(flow.status)}`}>
                    {flow.status.toUpperCase()}
                  </span>
                </div>
                <span className="text-xs text-slate-500">
                  {formatTimestamp(flow.timestamp)}
                </span>
              </div>

              {/* Coordination Chain */}
              <div className="space-y-2">
                {flow.chain.map((step, idx) => {
                  const agentColor = AGENT_COLORS[step.agent] || '#64748b';
                  const agentName = AGENT_DISPLAY_NAMES[step.agent] || step.agent;
                  const isLast = idx === flow.chain.length - 1;

                  return (
                    <div key={`${step.timestamp}-${idx}`} className="relative">
                      {/* Step */}
                      <div className="flex items-start gap-3">
                        {/* Agent Badge */}
                        <div
                          className="flex-shrink-0 w-20 px-2 py-1 rounded text-xs font-semibold text-center"
                          style={{
                            backgroundColor: `${agentColor}20`,
                            color: agentColor,
                            border: `1px solid ${agentColor}40`,
                          }}
                        >
                          {agentName}
                        </div>

                        {/* Arrow */}
                        {!isLast && (
                          <ArrowRight
                            className="flex-shrink-0 mt-1"
                            style={{ color: agentColor, width: 16, height: 16 }}
                          />
                        )}

                        {/* Action */}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-300">{step.action}</p>
                          {step.toAgent && (
                            <p className="text-xs text-slate-500 mt-0.5">
                              → {AGENT_DISPLAY_NAMES[step.toAgent] || step.toAgent}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Connector Line */}
                      {!isLast && (
                        <div
                          className="absolute left-10 top-8 w-0.5 h-4"
                          style={{ backgroundColor: `${agentColor}40` }}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
