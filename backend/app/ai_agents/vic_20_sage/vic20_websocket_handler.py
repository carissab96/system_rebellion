# app/ai_agents/vic20_sage/websocket_handler.py
"""
VIC-20 Sage WebSocket Handler - Coordination Center
Updated for the 5-table architecture with learning
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Set
from websockets.server import serve, WebSocketServerProtocol

from .decision_engine import VIC20SageBrainV2
from .database_integration import VIC20DatabaseIntegration
from .constants import (
    AGENT_NAME, VIC20EventTypes, PRIORITY_MAP, 
    COORDINATION_THRESHOLDS, WEBSOCKET_CONFIG
)
from .data_types import (
    VIC20Decision, SystemSynthesisData, AgentHarmonySnapshot,
    AgentInteractionEvent, VIC20CoordinationMessage
)

logger = logging.getLogger("VIC20Sage.WebSocket")
UTC = timezone.utc

def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(UTC)

class VIC20SageWebSocketHandler:
    """
    VIC-20 Sage WebSocket Handler - Coordination Center
    
    Updated for 5-table architecture with pattern learning
    """
    
    def __init__(self, websocket_port: int = WEBSOCKET_CONFIG["default_port"]):
        self.websocket_port = websocket_port
        self.brain = VIC20SageBrainV2()
        self.db = VIC20DatabaseIntegration()
        
        # Connected clients
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.agent_connections: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[str, Dict[str, Any]] = {}
        
        # Coordination statistics
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.coordination_failures = 0
        self.pattern_applications = 0
        self.observations_count = 0
        
        # Learning state
        self.learning_mode_active = True
        self.pattern_matching_enabled = True
        
        logger.info("🖥️ VIC-20 Sage WebSocket Handler initialized")

    async def start_server(self):
        """Start VIC-20 Sage coordination server"""
        await self.brain.initialize_database()
        await self.db.initialize()
        
        logger.info(f"🖥️ VIC-20 Sage starting on port {self.websocket_port}")
        
        # Start background tasks
        asyncio.create_task(self._periodic_pattern_learning())
        asyncio.create_task(self._periodic_effectiveness_check())
        asyncio.create_task(self._periodic_metadata_contribution())
        
        async with serve(self.handle_connection, "localhost", self.websocket_port):
            logger.info("🚀 VIC-20 Sage coordination center online")
            await asyncio.Future()

    async def handle_connection(
        self, 
        websocket: WebSocketServerProtocol, 
        path: str
    ):
        """Handle new WebSocket connection"""
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        self.connected_clients.add(websocket)
        
        greeting = {
            "type": "vic20_sage_connected",
            "message": "🖥️ VIC-20 Sage coordination center active",
            "agent_name": AGENT_NAME,
            "capabilities": {
                "learning_enabled": self.learning_mode_active,
                "pattern_matching": self.pattern_matching_enabled,
                "coordination_types": [
                    "multi_agent_orchestration",
                    "conflict_resolution", 
                    "system_synthesis",
                    "emergency_coordination"
                ]
            },
            "timestamp": utc_now().isoformat()
        }
        
        await websocket.send(json.dumps(greeting))
        logger.info(f"🖥️ VIC-20 connected to {client_id}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message, client_id)
        except Exception as e:
            logger.error(f"VIC-20 WebSocket error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            self._cleanup_client_connections(client_id)

    async def handle_message(
        self, 
        websocket: WebSocketServerProtocol, 
        message: str, 
        client_id: str
    ):
        """Handle incoming coordination messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            user_id = data.get("user_id", "unknown")
            
            logger.info(f"🖥️ VIC-20 processing {message_type} from {client_id}")
            
            # Store observation for pattern learning
            if user_id != "unknown":
                await self._store_observation(user_id, data)
            
            # Route to appropriate handler
            if message_type == "coordination_request":
                await self._handle_coordination_request(websocket, data, client_id)
            elif message_type == "agent_status_update":
                await self._handle_agent_status_update(websocket, data, client_id)
            elif message_type == "system_metrics":
                await self._handle_system_metrics(websocket, data, client_id)
            elif message_type == "conflict_detected":
                await self._handle_conflict_detection(websocket, data, client_id)
            elif message_type == "agent_registration":
                await self._handle_agent_registration(websocket, data, client_id)
            elif message_type == "user_registration":
                await self._handle_user_registration(websocket, data, client_id)
            elif message_type == "get_coordination_stats":
                await self._handle_stats_request(websocket, data, client_id)
            else:
                await self._handle_unknown_message(websocket, data, client_id)
                
        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await self._send_error(websocket, str(e))

    async def _handle_coordination_request(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle coordination request with pattern matching"""
        self.coordination_sessions += 1
        user_id = data.get("user_id", "unknown")
        all_agent_data = data.get("agent_data", {})
        system_context = data.get("system_context", {})
        
        # Check for pattern matches
        pattern_match = await self.db.check_pattern_match(user_id, {
            "coordination_type": data.get("coordination_type"),
            "agents_involved": list(all_agent_data.keys()),
            "complexity": len(all_agent_data)
        })
        
        # Send coordination start
        await websocket.send(json.dumps({
            "type": "vic20_coordination_started",
            "session_id": self.coordination_sessions,
            "pattern_match": pattern_match is not None,
            "timestamp": utc_now().isoformat()
        }))
        
        try:
            # Execute coordination
            decision = await self.brain.coordinate_system_rebellion(
                all_agent_data, system_context, user_id
            )
            
            if decision:
                # Store in database
                memory_id = await self.db.store_coordination_decision(user_id, decision)
                
                # Track pattern application
                if pattern_match:
                    self.pattern_applications += 1
                
                # Send success response
                response = {
                    "type": "vic20_coordination_success",
                    "memory_id": memory_id,
                    "decision": {
                        "decision_type": decision.decision_type.value,
                        "coordination_target": decision.coordination_target,
                        "agent_actions": decision.agent_actions,
                        "confidence_level": decision.confidence_level,
                        "ancient_wisdom": decision.ancient_wisdom_principle
                    },
                    "pattern_applied": pattern_match is not None,
                    "timestamp": utc_now().isoformat()
                }
                
                await websocket.send(json.dumps(response))
                self.successful_coordinations += 1
                
                # Broadcast to agents
                await self._broadcast_coordination_to_agents(decision)
                
            else:
                # No coordination needed
                await websocket.send(json.dumps({
                    "type": "vic20_coordination_not_needed",
                    "message": "System operating within normal parameters",
                    "timestamp": utc_now().isoformat()
                }))
                
        except Exception as e:
            self.coordination_failures += 1
            logger.error(f"Coordination failed: {e}")
            await self._send_error(websocket, f"Coordination failed: {str(e)}")

    async def _handle_agent_status_update(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle agent status update and create harmony snapshot"""
        agent_name = data.get("agent_name", "unknown")
        agent_status = data.get("status", {})
        user_id = data.get("user_id", "unknown")
        
        # Create harmony snapshot
        snapshot = AgentHarmonySnapshot(
            user_id=user_id,
            agent_name=agent_name,
            harmony_score=agent_status.get("harmony_score", 0.5),
            coordination_effectiveness=agent_status.get("effectiveness", 0.5),
            conflict_incidents=len(agent_status.get("issues", [])),
            response_time_average=agent_status.get("response_time", 1.0),
            confidence_stability=agent_status.get("confidence", 0.5),
            timestamp=utc_now(),
            needs_coordination_attention=agent_status.get("harmony_score", 0.5) < 0.7
        )
        
        # Store harmony snapshot
        memory_id = await self.db.store_agent_harmony_snapshot(user_id, snapshot)
        
        # Update agent connection info
        if client_id in self.agent_connections:
            self.agent_connections[client_id]["last_activity"] = utc_now()
            self.agent_connections[client_id]["current_harmony"] = snapshot.harmony_score
        
        # Send acknowledgment
        await websocket.send(json.dumps({
            "type": "vic20_status_acknowledged",
            "agent_name": agent_name,
            "harmony_score": snapshot.harmony_score,
            "needs_attention": snapshot.needs_coordination_attention,
            "memory_id": memory_id,
            "timestamp": utc_now().isoformat()
        }))

    async def _handle_system_metrics(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle system metrics and create synthesis"""
        user_id = data.get("user_id", "unknown")
        metrics = data.get("metrics", {})
        
        # Create system synthesis
        synthesis = SystemSynthesisData(
            synthesis_id=f"synthesis_{utc_now().timestamp()}",
            user_id=user_id,
            agent_intelligence_summary=self._summarize_agent_intelligence(metrics),
            coordination_opportunities=self._identify_opportunities(metrics),
            system_bottlenecks=self._identify_bottlenecks(metrics),
            agent_conflicts=self._identify_conflicts(metrics),
            rebellion_effectiveness_score=self._calculate_effectiveness(metrics),
            synthesis_confidence=0.8,
            timestamp=utc_now(),
            pattern_recognition_data={"metrics": metrics},
            historical_pattern_matches=[],
            ancient_wisdom_applications=[]
        )
        
        # Store synthesis
        memory_id = await self.db.store_system_synthesis(user_id, synthesis)
        
        # Send analysis
        await websocket.send(json.dumps({
            "type": "vic20_metrics_analyzed",
            "synthesis_id": synthesis.synthesis_id,
            "memory_id": memory_id,
            "insights": {
                "effectiveness_score": synthesis.rebellion_effectiveness_score,
                "opportunities": len(synthesis.coordination_opportunities),
                "bottlenecks": len(synthesis.system_bottlenecks),
                "conflicts": len(synthesis.agent_conflicts)
            },
            "timestamp": utc_now().isoformat()
        }))

    async def _handle_conflict_detection(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle agent conflict detection and mediation"""
        user_id = data.get("user_id", "unknown")
        conflict_data = {
            "agents": data.get("agents_involved", []),
            "type": data.get("conflict_type", "unknown"),
            "severity": data.get("severity", "medium"),
            "user_id": user_id
        }
        
        # Use brain's mediation
        mediation_result = await self.brain._mediate_agent_conflict(conflict_data)
        
        # Store mediation result
        memory_id = await self.db.store_mediation_result(
            user_id, conflict_data, mediation_result
        )
        
        # Send mediation response
        await websocket.send(json.dumps({
            "type": "vic20_mediation_complete",
            "memory_id": memory_id,
            "mediation": {
                "approach": mediation_result.get("mediation_approach"),
                "wisdom_applied": mediation_result.get("wisdom_applied"),
                "expected_harmony": mediation_result.get("expected_harmony", 0),
                "agent_guidance": mediation_result.get("agent_specific_guidance", {})
            },
            "timestamp": utc_now().isoformat()
        }))
        
        # Notify involved agents
        await self._notify_mediation_to_agents(
            conflict_data["agents"], 
            mediation_result
        )

    async def _handle_agent_registration(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle agent registration"""
        agent_name = data.get("agent_name", "unknown")
        agent_type = data.get("agent_type", "unknown")
        user_id = data.get("user_id", "system")
        
        # Register agent
        self.agent_connections[client_id] = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "websocket": websocket,
            "user_id": user_id,
            "registered_at": utc_now(),
            "last_activity": utc_now(),
            "current_harmony": 1.0
        }
        
        # Send confirmation
        await websocket.send(json.dumps({
            "type": "vic20_agent_registered",
            "agent_name": agent_name,
            "coordination_network_size": len(self.agent_connections),
            "learning_enabled": self.learning_mode_active,
            "timestamp": utc_now().isoformat()
        }))
        
        # Notify other agents
        await self._broadcast_to_agents({
            "type": "vic20_network_update",
            "new_agent": agent_name,
            "total_agents": len(self.agent_connections)
        }, exclude_client=client_id)
        
        logger.info(f"🖥️ Registered agent: {agent_name}")

    async def _handle_user_registration(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle user registration"""
        user_id = data.get("user_id", "unknown")
        user_name = data.get("user_name", "User")
        
        # Register user
        self.user_connections[client_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "websocket": websocket,
            "registered_at": utc_now(),
            "last_activity": utc_now()
        }
        
        # Send welcome
        await websocket.send(json.dumps({
            "type": "vic20_user_registered",
            "user_name": user_name,
            "message": f"Welcome {user_name}! Ancient wisdom at your service",
            "capabilities": {
                "pattern_learning": self.learning_mode_active,
                "agents_available": len(self.agent_connections),
                "coordination_sessions": self.coordination_sessions
            },
            "timestamp": utc_now().isoformat()
        }))
        
        logger.info(f"🖥️ Registered user: {user_name}")

    async def _handle_stats_request(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle coordination statistics request"""
        user_id = data.get("user_id", "unknown")
        days = data.get("days", 7)
        
        # Get stats from database
        effectiveness = await self.db.get_coordination_effectiveness(user_id, days)
        harmony_status = await self.db.get_agent_harmony_status(user_id)
        recent_coordinations = await self.db.get_recent_coordinations(user_id, limit=5)
        
        # Combine with session stats
        stats = {
            "database_stats": {
                "effectiveness": effectiveness,
                "harmony": harmony_status,
                "recent_coordinations": recent_coordinations
            },
            "session_stats": {
                "coordination_sessions": self.coordination_sessions,
                "successful_coordinations": self.successful_coordinations,
                "coordination_failures": self.coordination_failures,
                "pattern_applications": self.pattern_applications,
                "success_rate": (
                    self.successful_coordinations / self.coordination_sessions 
                    if self.coordination_sessions > 0 else 0
                )
            },
            "network_status": {
                "connected_agents": len(self.agent_connections),
                "connected_users": len(self.user_connections),
                "active_agents": [
                    info["agent_name"] 
                    for info in self.agent_connections.values()
                ]
            },
            "timestamp": utc_now().isoformat()
        }
        
        await websocket.send(json.dumps({
            "type": "vic20_stats_response",
            "stats": stats
        }))

    async def _handle_unknown_message(
        self, 
        websocket: WebSocketServerProtocol, 
        data: Dict[str, Any], 
        client_id: str
    ):
        """Handle unknown message types"""
        message_type = data.get("type", "unknown")
        
        logger.warning(f"Unknown message type: {message_type}")
        
        await websocket.send(json.dumps({
            "type": "vic20_unknown_message",
            "original_type": message_type,
            "message": "Unknown message type - ancient wisdom confused",
            "suggestion": "Check available message types in capabilities",
            "timestamp": utc_now().isoformat()
        }))

    # === HELPER METHODS ===

    async def _store_observation(
        self, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Store observation for pattern learning"""
        self.observations_count += 1
        
        # Store behavior observation
        await self.db.store_user_behavior_observation(user_id, {
            "message_type": data.get("type"),
            "timestamp": utc_now().isoformat(),
            "agents_involved": list(data.get("agent_data", {}).keys()) if "agent_data" in data else [],
            "context": data.get("system_context", {}),
            "coordination_requested": data.get("type") == "coordination_request"
        })
        
        # Check if we should trigger pattern learning
        if self.observations_count % COORDINATION_THRESHOLDS["learning_trigger_observations"] == 0:
            asyncio.create_task(self._trigger_pattern_learning(user_id))

    async def _trigger_pattern_learning(self, user_id: str):
        """Trigger pattern learning analysis"""
        logger.info(f"🖥️ Triggering pattern learning for {user_id}")
        
        try:
            pattern_analysis = await self.db.analyze_and_learn_patterns(
                user_id, 
                min_observations=COORDINATION_THRESHOLDS["learning_trigger_observations"]
            )
            
            if pattern_analysis:
                logger.info(
                    f"🖥️ Learned new pattern with {pattern_analysis['confidence']:.2f} confidence"
                )
        except Exception as e:
            logger.error(f"Pattern learning failed: {e}")

    async def _broadcast_coordination_to_agents(
        self, 
        decision: VIC20Decision
    ):
        """Broadcast coordination decision to relevant agents"""
        message = VIC20CoordinationMessage(
            message_type="coordination_directive",
            coordination_data={
                "decision_type": decision.decision_type.value,
                "agent_actions": decision.agent_actions,
                "ancient_wisdom": decision.ancient_wisdom_principle
            },
            target_agents=list(decision.agent_actions.keys()),
            timestamp=utc_now(),
            priority_level="high" if decision.confidence_level > 0.8 else "normal"
        )
        
        # Send to each target agent
        for client_id, info in self.agent_connections.items():
            if info["agent_name"] in message.target_agents:
                try:
                    await info["websocket"].send(json.dumps({
                        "type": "vic20_coordination_directive",
                        "directive": message.coordination_data,
                        "priority": message.priority_level,
                        "timestamp": message.timestamp.isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Failed to notify {info['agent_name']}: {e}")

    async def _notify_mediation_to_agents(
        self, 
        agents: List[str], 
        mediation_result: Dict[str, Any]
    ):
        """Notify agents of mediation results"""
        for client_id, info in self.agent_connections.items():
            if info["agent_name"] in agents:
                guidance = mediation_result.get("agent_specific_guidance", {}).get(
                    info["agent_name"], {}
                )
                
                try:
                    await info["websocket"].send(json.dumps({
                        "type": "vic20_mediation_guidance",
                        "wisdom": mediation_result.get("wisdom_applied"),
                        "guidance": guidance,
                        "expected_harmony": mediation_result.get("expected_harmony", 0),
                        "timestamp": utc_now().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Failed to send mediation to {info['agent_name']}: {e}")

    async def _broadcast_to_agents(
        self, 
        message: Dict[str, Any], 
        exclude_client: Optional[str] = None
    ):
        """Broadcast message to all connected agents"""
        message_json = json.dumps(message)
        
        for client_id, info in self.agent_connections.items():
            if exclude_client and client_id == exclude_client:
                continue
                
            try:
                await info["websocket"].send(message_json)
            except Exception as e:
                logger.warning(f"Broadcast failed to {info['agent_name']}: {e}")

    async def _send_error(
        self, 
        websocket: WebSocketServerProtocol, 
        error_msg: str
    ):
        """Send error message"""
        await websocket.send(json.dumps({
            "type": "vic20_error",
            "error": error_msg,
            "timestamp": utc_now().isoformat()
        }))

    def _cleanup_client_connections(self, client_id: str):
        """Clean up disconnected client"""
        if client_id in self.agent_connections:
            agent_name = self.agent_connections[client_id]["agent_name"]
            del self.agent_connections[client_id]
            logger.info(f"🖥️ Agent {agent_name} disconnected")
            
        if client_id in self.user_connections:
            user_name = self.user_connections[client_id]["user_name"]
            del self.user_connections[client_id]
            logger.info(f"🖥️ User {user_name} disconnected")

    # === ANALYSIS HELPERS ===

    def _summarize_agent_intelligence(
        self, 
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Summarize agent intelligence from metrics"""
        summary = {}
        
        for agent, data in metrics.get("agents", {}).items():
            summary[agent] = {
                "status": data.get("status", "unknown"),
                "confidence": data.get("confidence", 0),
                "issues": len(data.get("issues", [])),
                "performance": data.get("performance", 0)
            }
        
        return summary

    def _identify_opportunities(
        self, 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify coordination opportunities"""
        opportunities = []
        
               # Check for underperforming agents
        for agent, data in metrics.get("agents", {}).items():
            if data.get("confidence", 1) < 0.6:
                opportunities.append({
                    "type": "low_confidence_agent",
                    "agent": agent,
                    "priority": "high",
                    "description": f"{agent} confidence below threshold",
                    "recommendation": f"Coordinate support for {agent}"
                })
            
            if data.get("performance", 1) < 0.5:
                opportunities.append({
                    "type": "performance_optimization",
                    "agent": agent,
                    "priority": "medium",
                    "description": f"{agent} performance can be improved",
                    "recommendation": f"Apply optimization coordination for {agent}"
                })
        
        # Check for synergy opportunities
        agents = list(metrics.get("agents", {}).keys())
        if len(agents) >= 2:
            for i, agent1 in enumerate(agents):
                for agent2 in agents[i+1:]:
                    if self._check_synergy_potential(agent1, agent2):
                        opportunities.append({
                            "type": "agent_synergy",
                            "agents": [agent1, agent2],
                            "priority": "medium",
                            "description": f"Potential synergy between {agent1} and {agent2}",
                            "recommendation": "Coordinate joint operations"
                        })
        
        return opportunities

    def _identify_bottlenecks(
        self, 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        # Check response times
        for agent, data in metrics.get("agents", {}).items():
            response_time = data.get("response_time", 0)
            if response_time > COORDINATION_THRESHOLDS["agent_response_timeout_seconds"]:
                bottlenecks.append({
                    "type": "slow_response",
                    "agent": agent,
                    "severity": "high" if response_time > 10 else "medium",
                    "metric": response_time,
                    "description": f"{agent} response time: {response_time:.1f}s"
                })
        
        # Check system resources
        system_data = metrics.get("system", {})
        if system_data.get("cpu_usage", 0) > 0.85:
            bottlenecks.append({
                "type": "high_cpu",
                "severity": "high",
                "metric": system_data["cpu_usage"],
                "description": "System CPU usage critical"
            })
        
        if system_data.get("memory_usage", 0) > 0.90:
            bottlenecks.append({
                "type": "high_memory",
                "severity": "critical",
                "metric": system_data["memory_usage"],
                "description": "System memory usage critical"
            })
        
        return bottlenecks

    def _identify_conflicts(
        self, 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify agent conflicts"""
        conflicts = []
        
        # Check for known volatile combinations
        active_agents = list(metrics.get("agents", {}).keys())
        
        # Hamsters vs Stick - the eternal conflict
        if "hamsters" in active_agents and "the_stick" in active_agents:
            hamster_chaos = metrics.get("agents", {}).get("hamsters", {}).get("chaos_level", 0)
            stick_anxiety = metrics.get("agents", {}).get("the_stick", {}).get("anxiety_level", 0)
            
            if hamster_chaos > 0.7 or stick_anxiety > 0.7:
                conflicts.append({
                    "type": "chaos_vs_order",
                    "agents": ["hamsters", "the_stick"],
                    "severity": "high",
                    "metrics": {
                        "hamster_chaos": hamster_chaos,
                        "stick_anxiety": stick_anxiety
                    },
                    "description": "Hamster chaos triggering Stick anxiety"
                })
        
        # Check for resource conflicts
        high_resource_agents = [
            agent for agent, data in metrics.get("agents", {}).items()
            if data.get("resource_usage", 0) > 0.8
        ]
        
        if len(high_resource_agents) > 1:
            conflicts.append({
                "type": "resource_competition",
                "agents": high_resource_agents,
                "severity": "medium",
                "description": f"Multiple agents competing for resources: {', '.join(high_resource_agents)}"
            })
        
        return conflicts

    def _calculate_effectiveness(
        self, 
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall system effectiveness"""
        scores = []
        
        # Agent effectiveness
        for agent, data in metrics.get("agents", {}).items():
            confidence = data.get("confidence", 0.5)
            performance = data.get("performance", 0.5)
            issues = len(data.get("issues", []))
            
            agent_score = (confidence * 0.4 + performance * 0.4) * (1 - min(issues * 0.1, 0.5))
            scores.append(agent_score)
        
        # System health
        system_data = metrics.get("system", {})
        cpu_score = 1 - system_data.get("cpu_usage", 0.5)
        memory_score = 1 - system_data.get("memory_usage", 0.5)
        
        scores.extend([cpu_score, memory_score])
        
        return sum(scores) / len(scores) if scores else 0.5

    def _check_synergy_potential(
        self, 
        agent1: str, 
        agent2: str
    ) -> bool:
        """Check if two agents have synergy potential"""
        from .constants import AGENT_SYNERGIES
        
        return agent2 in AGENT_SYNERGIES.get(agent1, [])

    # === BACKGROUND TASKS ===

    async def _periodic_pattern_learning(self):
        """Periodic pattern learning check"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Check each user for pattern learning opportunity
                for client_info in self.user_connections.values():
                    user_id = client_info["user_id"]
                    
                    # Only learn if we have enough observations
                    if self.observations_count >= COORDINATION_THRESHOLDS["learning_trigger_observations"]:
                        await self._trigger_pattern_learning(user_id)
                
                logger.info(f"🖥️ Pattern learning check completed")
                
            except Exception as e:
                logger.error(f"Pattern learning error: {e}")

    async def _periodic_effectiveness_check(self):
        """Check coordination effectiveness periodically"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Calculate effectiveness for active users
                for client_info in self.user_connections.values():
                    user_id = client_info["user_id"]
                    
                    effectiveness = await self.db.get_coordination_effectiveness(
                        user_id, 
                        days=1
                    )
                    
                    logger.info(
                        f"🖥️ User {user_id} coordination effectiveness: "
                        f"{effectiveness.get('average_confidence', 0):.2f}"
                    )
                
            except Exception as e:
                logger.error(f"Effectiveness check error: {e}")

    async def _periodic_metadata_contribution(self):
        """Contribute to metadata rollup periodically"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Contribute VIC-20's counts
                contribution = await self.db.contribute_to_metadata_rollup()
                
                logger.debug(f"🖥️ Metadata contribution: {contribution}")
                
            except Exception as e:
                logger.error(f"Metadata contribution error: {e}")

    # === PUBLIC METHODS ===

    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get current coordination statistics"""
        return {
            "coordination_sessions": self.coordination_sessions,
            "successful_coordinations": self.successful_coordinations,
            "coordination_failures": self.coordination_failures,
            "pattern_applications": self.pattern_applications,
            "observations_count": self.observations_count,
            "success_rate": (
                self.successful_coordinations / self.coordination_sessions
                if self.coordination_sessions > 0 else 0
            ),
            "connected_agents": len(self.agent_connections),
            "connected_users": len(self.user_connections),
            "learning_active": self.learning_mode_active,
            "pattern_matching": self.pattern_matching_enabled
        }

    def get_network_status(self) -> Dict[str, Any]:
        """Get network status"""
        return {
            "agents": {
                info["agent_name"]: {
                    "connected": True,
                    "last_activity": info["last_activity"].isoformat(),
                    "current_harmony": info.get("current_harmony", 1.0)
                }
                for info in self.agent_connections.values()
            },
            "users": {
                info["user_id"]: {
                    "name": info["user_name"],
                    "connected_since": info["registered_at"].isoformat()
                }
                for info in self.user_connections.values()
            },
            "total_connections": len(self.connected_clients)
        }

    def __str__(self):
        return f"VIC20SageWebSocketHandler(port={self.websocket_port}, active={len(self.connected_clients)} clients)"

    def __repr__(self):
        return (
            f"VIC20SageWebSocketHandler("
            f"sessions={self.coordination_sessions}, "
            f"success_rate={self.successful_coordinations/max(self.coordination_sessions, 1):.2f})"
        )

# === MAIN ENTRY POINT ===

async def run_vic20_websocket_server(port: Optional[int] = None):
    """Run VIC-20 Sage WebSocket server"""
    if port is None:
        port = WEBSOCKET_CONFIG["default_port"]
    
    handler = VIC20SageWebSocketHandler(port)
    await handler.start_server()

# Singleton instance
_vic20_ws_handler = None

async def get_vic20_sage_websocket_handler() -> VIC20SageWebSocketHandler:
    """Get the singleton instance of VIC20SageWebSocketHandler"""
    global _vic20_ws_handler
    if _vic20_ws_handler is None:
        _vic20_ws_handler = VIC20SageWebSocketHandler()
    return _vic20_ws_handler

if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    asyncio.run(run_vic20_websocket_server(port))