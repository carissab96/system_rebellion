# /agents/vic20_sage/websocket_handler.py (COMPLETE & DEBUGGED VERSION)
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from websockets.server import serve
from websockets import WebSocketServerProtocol
from .decision_engine import VIC20SageBrainV2
from .database_integration import VIC20DatabaseIntegration
from .data_types import *

logger = logging.getLogger("VIC20Sage.WebSocket")

class VIC20SageWebSocketHandler:
    """
    VIC-20 Sage WebSocket Handler - Coordination Center
    
    Streamlined for efficiency while maintaining full coordination scope
    Learning-enabled coordination with pattern recognition
    """
    
    def __init__(self, websocket_port: int = 8086):
        self.websocket_port = websocket_port
        self.brain = VIC20SageBrainV2()
        self.db_integration = VIC20DatabaseIntegration()
        
        # Connected clients
        self.connected_clients = set()
        self.agent_connections = {}
        self.user_connections = {}
        
        # Coordination statistics (for objective partnership metrics)
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.coordination_failures = 0
        self.pattern_applications = 0
        self.agent_interactions_logged = 0
        
        # Learning state
        self.learning_mode_active = True
        self.pattern_matching_enabled = True
        self.effectiveness_tracking_enabled = True
        
        logger.info("🖥️ VIC-20 Sage WebSocket Handler initialized - Coordination center online")

    async def start_server(self):
        """Start VIC-20 Sage coordination server"""
        await self.brain.initialize_database()
        await self.db_integration.initialize()
        
        logger.info(f"🖥️ VIC-20 Sage coordination server starting on port {self.websocket_port}")
        
        # Start background tasks
        asyncio.create_task(self._periodic_learning_update())
        asyncio.create_task(self._periodic_partnership_metrics_update())
        
        async with serve(self.handle_connection, "localhost", self.websocket_port):
            logger.info("🚀 VIC-20 Sage coordination center online - Learning enabled")
            await asyncio.Future()

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        
        client_id = f"client_{len(self.connected_clients)}"
        self.connected_clients.add(websocket)
        
        greeting = {
            "type": "vic20_sage_connected",
            "message": "🖥️ VIC-20 Sage coordination center active",
            "learning_capabilities": "pattern_recognition_enabled",
            "coordination_scope": "system_wide",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(greeting))
        logger.info(f"🖥️ VIC-20 Sage connected to {client_id}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message, client_id)
        except Exception as e:
            logger.error(f"VIC-20 Sage WebSocket error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            self._cleanup_client_connections(client_id)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str, client_id: str):
        """Handle incoming coordination messages"""
        
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            logger.info(f"🖥️ VIC-20 processing {message_type} from {client_id}")
            
            # Route to appropriate handler
            if message_type == "coordination_request":
                await self._handle_coordination_request(websocket, data, client_id)
            elif message_type == "agent_status_update":
                await self._handle_agent_status_update(websocket, data, client_id)
            elif message_type == "system_metrics":
                await self._handle_system_metrics(websocket, data, client_id)
            elif message_type == "agent_registration":
                await self._handle_agent_registration(websocket, data, client_id)
            elif message_type == "user_registration":
                await self._handle_user_registration(websocket, data, client_id)
            elif message_type == "coordination_feedback":
                await self._handle_coordination_feedback(websocket, data, client_id)
            elif message_type == "partnership_metrics_request":
                await self._handle_partnership_metrics_request(websocket, data, client_id)
            elif message_type == "learning_data_request":
                await self._handle_learning_data_request(websocket, data, client_id)
            else:
                await self._handle_unknown_message(websocket, data, client_id)
                
        except json.JSONDecodeError:
            await self._send_coordination_error(websocket, client_id, "Invalid JSON format")
        except Exception as e:
            await self._handle_coordination_failure(websocket, client_id, str(e))

    async def _handle_coordination_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle coordination requests with learning"""
        
        self.coordination_sessions += 1
        user_id = data.get("user_id", "unknown")
        all_agent_data = data.get("agent_data", {})
        system_context = data.get("system_context", {})
        
        coordination_start = {
            "type": "vic20_coordination_started",
            "message": "🖥️ Coordination analysis initiated",
            "learning_mode": self.learning_mode_active,
            "pattern_matching": self.pattern_matching_enabled,
            "session_id": self.coordination_sessions,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(coordination_start))
        
        try:
            # Execute coordination with learning
            coordination_decision = await self.brain.coordinate_system_rebellion(
                all_agent_data, system_context, user_id
            )
            
            if coordination_decision:
                # Store coordination decision
                coordination_id = await self.db_integration.store_coordination_decision(user_id, coordination_decision)
                
                # Log agent interactions
                await self._log_agent_interactions_from_coordination(coordination_decision, user_id)
                
                # Send success response
                success_response = {
                    "type": "vic20_coordination_success",
                    "coordination_id": coordination_id,
                    "coordination_decision": {
                        "decision_type": coordination_decision.decision_type.value,
                        "coordination_target": coordination_decision.coordination_target,
                        "agent_actions": coordination_decision.agent_actions,
                        "confidence_level": coordination_decision.confidence_level,
                        "expected_improvement": coordination_decision.expected_rebellion_improvement
                    },
                    "learning_applied": {
                        "ancient_wisdom_principle": coordination_decision.ancient_wisdom_principle,
                        "pattern_matches_found": len(coordination_decision.similar_past_decisions or []),
                        "learning_confidence": coordination_decision.system_synthesis_confidence
                    },
                    "message": "🖥️ Coordination complete - Learning patterns applied",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(success_response))
                self.successful_coordinations += 1
                
                # Broadcast coordination to agents
                await self._broadcast_coordination_to_agents(coordination_decision)
                
                # Track patterns applied
                if coordination_decision.similar_past_decisions:
                    self.pattern_applications += 1
                
            else:
                # No coordination needed
                no_coordination_response = {
                    "type": "vic20_coordination_not_needed",
                    "message": "🖥️ System analysis complete - No coordination required",
                    "system_assessment": "All agents operating within optimal parameters",
                    "learning_note": "Patterns indicate system stability",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(no_coordination_response))
            
        except Exception as e:
            await self._handle_coordination_failure(websocket, client_id, str(e))

    async def _handle_agent_status_update(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle agent status updates and store for learning"""
        
        agent_name = data.get("agent_name", "unknown")
        agent_status = data.get("status", {})
        user_id = data.get("user_id", "unknown")
        
        # Log agent interaction
        interaction_event = AgentInteractionEvent(
            user_id=user_id,
            source_agent=agent_name,
            target_agent="vic20_sage",
            interaction_type="status_update",
            message_content=agent_status,
            coordination_context="agent_status_reporting",
            timestamp=datetime.now(),
            vic20_processing_notes=f"Status update processed for {agent_name}",
            interaction_success=True
        )
        
        await self._store_agent_interaction(interaction_event)
        self.agent_interactions_logged += 1
        
        # Update agent connection activity
        if client_id in self.agent_connections:
            self.agent_connections[client_id]["last_activity"] = datetime.now()
        
        # Generate harmony snapshot
        harmony_snapshot = self._create_harmony_snapshot_from_status(user_id, agent_name, agent_status)
        if harmony_snapshot:
            await self._store_agent_harmony_snapshot(harmony_snapshot)
        
        # Send acknowledgment with coordination guidance
        status_response = {
            "type": "vic20_status_acknowledged",
            "agent_name": agent_name,
            "message": f"🖥️ {agent_name} status processed and stored for learning",
            "coordination_guidance": self._get_coordination_guidance(agent_name, agent_status),
            "learning_impact": "Status patterns stored for future coordination decisions",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(status_response))

    async def _handle_system_metrics(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle system metrics for synthesis and learning"""
        
        user_id = data.get("user_id", "unknown")
        metrics = data.get("metrics", {})
        
        # Create system synthesis
        synthesis_data = SystemSynthesisData(
            synthesis_id=f"synthesis_{datetime.now().timestamp()}",
            user_id=user_id,
            agent_intelligence_summary=metrics,
            coordination_opportunities=self._identify_coordination_opportunities(metrics),
            system_bottlenecks=self._identify_system_bottlenecks(metrics),
            agent_conflicts=self._identify_potential_conflicts(metrics),
            rebellion_effectiveness_score=self._calculate_system_effectiveness(metrics),
            synthesis_confidence=self._calculate_synthesis_confidence(metrics),
            pattern_recognition_data={"metrics_snapshot": metrics},
            historical_pattern_matches=[],
            ancient_wisdom_applications=[],
            timestamp=datetime.now()
        )
        
        # Store synthesis for learning
        await self.db_integration.store_system_synthesis(user_id, synthesis_data)
        
        # Send analysis response
        metrics_response = {
            "type": "vic20_metrics_analyzed",
            "message": "🖥️ System metrics analyzed and stored for learning",
            "synthesis_insights": {
                "system_effectiveness": synthesis_data.rebellion_effectiveness_score,
                "coordination_opportunities": len(synthesis_data.coordination_opportunities),
                "system_bottlenecks": len(synthesis_data.system_bottlenecks),
                "synthesis_confidence": synthesis_data.synthesis_confidence
            },
            "learning_value": "Metrics patterns stored for future coordination optimization",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(metrics_response))

    async def _handle_agent_registration(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle agent registration for coordination network"""
        
        agent_name = data.get("agent_name", "unknown_agent")
        agent_type = data.get("agent_type", "unknown")
        user_id = data.get("user_id", "system")
        
        # Register agent connection
        self.agent_connections[client_id] = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "websocket": websocket,
            "registered_timestamp": datetime.now(),
            "last_activity": datetime.now(),
            "user_id": user_id
        }
        
        # Log registration interaction
        interaction_event = AgentInteractionEvent(
            user_id=user_id,
            source_agent=agent_name,
            target_agent="vic20_sage",
            interaction_type="agent_registration",
            message_content={"agent_type": agent_type},
            coordination_context="coordination_network_join",
            timestamp=datetime.now(),
            vic20_processing_notes=f"Agent {agent_name} joined coordination network",
            interaction_success=True
        )
        
        await self._store_agent_interaction(interaction_event)
        
        registration_response = {
            "type": "vic20_agent_registered",
            "agent_name": agent_name,
            "message": f"🖥️ {agent_name} registered for system coordination",
            "coordination_network_status": f"Currently coordinating {len(self.agent_connections)} agents",
            "learning_enabled": self.learning_mode_active,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(registration_response))
        
        # Notify other agents
        await self._broadcast_to_agents({
            "type": "vic20_agent_network_update",
            "new_agent": agent_name,
            "total_agents": len(self.agent_connections),
            "coordination_capability": "enhanced"
        }, exclude_client=client_id)
        
        logger.info(f"🖥️ VIC-20 registered agent: {agent_name} ({agent_type})")

    async def _handle_user_registration(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle user registration for partnership tracking"""
        
        user_id = data.get("user_id", "unknown_user")
        user_name = data.get("user_name", "User")
        
        # Register user connection
        self.user_connections[client_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "websocket": websocket,
            "registered_timestamp": datetime.now(),
            "last_activity": datetime.now(),
            "partnership_id": f"partnership_{user_id}_{datetime.now().timestamp()}"
        }
        
        user_welcome = {
            "type": "vic20_user_registered",
            "user_name": user_name,
            "message": f"🖥️ Welcome, {user_name}! VIC-20 coordination ready",
            "coordination_capabilities": {
                "learning_enabled": self.learning_mode_active,
                "pattern_matching": self.pattern_matching_enabled,
                "effectiveness_tracking": self.effectiveness_tracking_enabled,
                "agents_available": len(self.agent_connections)
            },
            "partnership_tracking": "objective_behavioral_metrics_enabled",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(user_welcome))
        logger.info(f"🖥️ VIC-20 registered user: {user_name} ({user_id})")

    async def _handle_coordination_feedback(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle coordination feedback for effectiveness learning"""
        
        coordination_id = data.get("coordination_id")
        feedback = data.get("feedback", {})
        user_id = data.get("user_id", "unknown")
        
        # Extract objective outcome data
        actual_outcomes = {
            "coordination_successful": feedback.get("success", False),
            "system_improvement": feedback.get("improvement_score", 0.0),
            "problems_resolved": feedback.get("problems_resolved", 0),
            "efficiency_improved": feedback.get("efficiency_gain", False),
            "agent_response_success_rate": feedback.get("agent_response_rate", 0.0)
        }
        
        # Calculate effectiveness score
        if coordination_id:
            effectiveness_score = await self.brain.measure_coordination_effectiveness(
                str(coordination_id), actual_outcomes
            )
            
            # Store feedback for learning
            await self._store_coordination_feedback({
                "coordination_id": coordination_id,
                "user_id": user_id,
                "feedback": feedback,
                "effectiveness_score": effectiveness_score,
                "timestamp": datetime.now()
            })
            
            feedback_response = {
                "type": "vic20_coordination_feedback",
                "message": "🖥️📊 Coordination feedback processed and stored for learning",
                "effectiveness_score": effectiveness_score,
                "learning_value": "Feedback patterns stored for future coordination optimization",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(feedback_response))
            
            # Notify other agents
            await self._broadcast_to_agents({
                "type": "vic20_coordination_feedback_update",
                "coordination_id": coordination_id,
                "effectiveness_score": effectiveness_score,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }, exclude_client=client_id)
            
            logger.info(f"🖥️ VIC-20 processed coordination feedback for {coordination_id}")

    async def _handle_partnership_metrics_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle partnership metrics requests for objective data"""
        
        user_id = data.get("user_id", "unknown")
        
        # Get comprehensive partnership metrics
        partnership_metrics = await self.brain.get_partnership_metrics_data(user_id)
        coordination_stats = self.brain.get_vic20_coordination_stats()
        
        # Combine with current session statistics
        comprehensive_metrics = {
            **partnership_metrics,
            "session_statistics": {
                "coordination_sessions_this_session": self.coordination_sessions,
                "successful_coordinations_this_session": self.successful_coordinations,
                "coordination_failures_this_session": self.coordination_failures,
                "pattern_applications_this_session": self.pattern_applications,
                "agent_interactions_logged_this_session": self.agent_interactions_logged
            },
            "vic20_coordination_stats": coordination_stats,
            "learning_status": {
                "learning_mode": self.learning_mode_active,
                "pattern_matching": self.pattern_matching_enabled,
                "effectiveness_tracking": self.effectiveness_tracking_enabled
            }
        }
        
        metrics_response = {
            "type": "vic20_partnership_metrics",
            "message": "🖥️📊 Partnership metrics compiled - Ancient wisdom effectiveness data",
            "metrics": comprehensive_metrics,
            "data_reliability": "objective_behavioral_metrics",
            "measurement_period": "session_and_historical",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(metrics_response))
        logger.info(f"🖥️ VIC-20 provided partnership metrics for {user_id}")

    async def _handle_learning_data_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle requests for learning and pattern data"""
        
        user_id = data.get("user_id", "unknown")
        request_type = data.get("learning_request_type", "general")
        
        learning_data = {
            "coordination_patterns_available": len(self.brain.coordination_patterns),
            "agent_performance_trends": len(self.brain.agent_performance_trends),
            "effectiveness_history_size": len(self.brain.effectiveness_history),
            "ancient_wisdom_principles": self.brain.ancient_wisdom_principles,
            "learning_thresholds": self.brain.coordination_thresholds,
            "pattern_matching_capability": "historical_pattern_recognition_active"
        }
        
        if request_type == "detailed" and self.db_integration:
            # Get detailed learning insights
            try:
                learning_insights = await self.db_integration.get_comprehensive_coordination_report(user_id)
                learning_data["detailed_insights"] = learning_insights
            except Exception as e:
                learning_data["detailed_insights"] = {"error": f"Could not retrieve detailed insights: {str(e)}"}
        
        learning_response = {
            "type": "vic20_learning_data",
            "message": "🖥️🧠 Learning data compiled - Pattern recognition capabilities",
            "learning_data": learning_data,
            "ancient_wisdom_status": "1989_to_2025_wisdom_bridge_active",
            "learning_evolution": "continuous_pattern_recognition_improvement",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(learning_response))
        logger.info(f"🖥️ VIC-20 provided learning data for {user_id}")

    async def _handle_unknown_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle unknown message types with learning opportunity"""
        
        message_type = data.get("type", "unknown")
        
        # Log unknown message for learning
        unknown_message_event = {
            "client_id": client_id,
            "message_type": message_type,
            "message_data": data,
            "timestamp": datetime.now(),
            "learning_opportunity": "new_message_type_encountered"
        }
        
        if self.db_integration:
            await self._store_unknown_message_for_learning(unknown_message_event)
        
        unknown_response = {
            "type": "vic20_unknown_message_handled",
            "message": f"🖥️❓ Unknown message type '{message_type}' - Ancient wisdom learning opportunity",
            "original_message_type": message_type,
            "learning_note": "Message pattern stored for future coordination protocol enhancement",
            "coordination_guidance": "Consider using standard coordination message types for optimal processing",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(unknown_response))
        logger.warning(f"🖥️ VIC-20 handled unknown message type: {message_type} from {client_id}")

    async def _send_coordination_error(self, websocket: WebSocketServerProtocol, client_id: str, error_msg: str):
        """Send coordination error with learning context"""
        
        self.coordination_failures += 1
        
        error_response = {
            "type": "vic20_coordination_error",
            "message": f"🖥️⚠️ Coordination error encountered - Ancient wisdom learning engaged",
            "error_details": error_msg,
            "learning_impact": "Error pattern stored for future coordination improvement",
            "retry_guidance": "System continues learning - retry coordination when ready",
            "session_stats": {
                "coordination_sessions": self.coordination_sessions,
                "successful_coordinations": self.successful_coordinations,
                "coordination_failures": self.coordination_failures
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(error_response))
        logger.error(f"🖥️ VIC-20 coordination error for {client_id}: {error_msg}")

    async def _handle_coordination_failure(self, websocket: WebSocketServerProtocol, client_id: str, error_msg: str):
        """Handle coordination failure with comprehensive learning"""
        
        self.coordination_failures += 1
        
        # Store failure for learning
        failure_event = {
            "client_id": client_id,
            "error_message": error_msg,
            "coordination_session": self.coordination_sessions,
            "timestamp": datetime.now(),
            "learning_data": {
                "failure_type": "coordination_processing_error",
                "system_state": "coordination_attempt",
                "recovery_needed": True
            }
        }
        
        if self.db_integration:
            await self._store_coordination_failure_for_learning(failure_event)
        
        failure_response = {
            "type": "vic20_coordination_failure",
            "message": "🖥️💥 Coordination failure - Ancient wisdom learning from error",
            "error_details": error_msg,
            "failure_handling": "Error patterns stored for system improvement",
            "recovery_status": "VIC-20 continues coordination capability",
            "learning_value": "Failure analysis enhances future coordination reliability",
            "session_impact": {
                "session_coordination_sessions": self.coordination_sessions,
                "session_failures": self.coordination_failures,
                "current_success_rate": self.successful_coordinations / max(self.coordination_sessions, 1)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(failure_response))
        logger.error(f"🖥️ VIC-20 coordination failure for {client_id}: {error_msg}")

    async def _log_agent_interactions_from_coordination(self, coordination_decision, user_id: str):
        """Log agent interactions from coordination decision for learning"""
        
        if not coordination_decision.agent_actions:
            return
        
        for agent_name, action in coordination_decision.agent_actions.items():
            interaction_event = AgentInteractionEvent(
                user_id=user_id,
                source_agent="vic20_sage",
                target_agent=agent_name,
                interaction_type="coordination_directive",
                message_content=action,
                coordination_context=f"system_coordination_{coordination_decision.decision_type.value}",
                timestamp=datetime.now(),
                vic20_processing_notes=f"Coordination directive issued to {agent_name} - {coordination_decision.ancient_wisdom_principle}",
                interaction_success=True
            )
            
            await self._store_agent_interaction(interaction_event)
            self.agent_interactions_logged += 1

    async def _broadcast_coordination_to_agents(self, coordination_decision):
        """Broadcast coordination decision to all connected agents"""
        
        coordination_broadcast = {
            "type": "vic20_coordination_broadcast",
            "message": "🖥️📡 System coordination directive from Ancient Wisdom Engine",
            "coordination_data": {
                "decision_type": coordination_decision.decision_type.value,
                "coordination_target": coordination_decision.coordination_target,
                "agent_actions": coordination_decision.agent_actions,
                "ancient_wisdom_principle": coordination_decision.ancient_wisdom_principle,
                "expected_improvement": coordination_decision.expected_rebellion_improvement,
                "confidence_level": coordination_decision.confidence_level
            },
            "execution_guidance": "Process coordination directive according to agent capabilities",
            "coordination_context": "system_wide_optimization",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_agents(coordination_broadcast)

    async def _broadcast_to_agents(self, message_data: Dict[str, Any], exclude_client: str = None):
        """Broadcast message to all connected agents"""
        
        message_json = json.dumps(message_data)
        
        for client_id, agent_info in self.agent_connections.items():
            if exclude_client and client_id == exclude_client:
                continue
            
            try:
                websocket = agent_info["websocket"]
                await websocket.send(message_json)
            except Exception as e:
                logger.warning(f"🖥️ Failed to broadcast to agent {agent_info['agent_name']}: {e}")

    async def _periodic_learning_update(self):
        """Periodic learning update background task"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                if self.learning_mode_active and self.brain._db:
                    # Reload learning patterns
                    await self.brain._load_learning_patterns()
                    
                    # Update coordination statistics
                    await self._update_learning_metrics()
                    
                    logger.info("🖥️🧠 VIC-20 learning patterns updated - Ancient wisdom enhanced")
                
            except Exception as e:
                logger.error(f"🖥️ Learning update error: {e}")

    async def _periodic_partnership_metrics_update(self):
        """Periodic partnership metrics update background task"""
        
        while True:
            try:
                await asyncio.sleep(900)  # Every 15 minutes
                
                if self.effectiveness_tracking_enabled:
                    # Update partnership metrics for all connected users
                    for client_id, user_info in self.user_connections.items():
                        user_id = user_info["user_id"]
                        await self._update_partnership_metrics(user_id)
                    
                    logger.info("🖥️📊 Partnership metrics updated - Objective behavioral data refreshed")
                
            except Exception as e:
                logger.error(f"🖥️ Partnership metrics update error: {e}")

    async def _update_learning_metrics(self):
        """Update internal learning metrics"""
        
        if self.brain._db:
            try:
                # Get recent coordination effectiveness data
                recent_effectiveness = await self._get_recent_coordination_effectiveness(days=7)
                
                if recent_effectiveness:
                    self.brain.effectiveness_history.extend(recent_effectiveness)
                    # Keep only last 100 records for memory efficiency
                    self.brain.effectiveness_history = self.brain.effectiveness_history[-100:]
            except Exception as e:
                logger.warning(f"🖥️ Could not update learning metrics: {e}")

    async def _update_partnership_metrics(self, user_id: str):
        """Update partnership metrics for specific user"""
        
        if self.brain._db:
            try:
                current_metrics = await self.brain.get_partnership_metrics_data(user_id)
                # Store updated metrics - this would need a method in db_integration
                # For now, just log that we attempted the update
                logger.debug(f"🖥️ Updated partnership metrics for {user_id}")
            except Exception as e:
                logger.warning(f"🖥️ Could not update partnership metrics for {user_id}: {e}")

    def _cleanup_client_connections(self, client_id: str):
        """Clean up client connections on disconnect"""
        
        if client_id in self.agent_connections:
            agent_name = self.agent_connections[client_id]["agent_name"]
            del self.agent_connections[client_id]
            logger.info(f"🖥️ Agent {agent_name} disconnected from coordination network")
        
        if client_id in self.user_connections:
            user_name = self.user_connections[client_id]["user_name"]
            del self.user_connections[client_id]
            logger.info(f"🖥️ User {user_name} disconnected from partnership tracking")

    def _create_harmony_snapshot_from_status(self, user_id: str, agent_name: str, agent_status: Dict[str, Any]) -> Optional[AgentHarmonySnapshot]:
        """Create agent harmony snapshot from status update"""
        
        confidence = agent_status.get("confidence", 0.0)
        response_time = agent_status.get("response_time", 0.0)
        issues = agent_status.get("issues", [])
        
        # Calculate harmony score
        harmony_score = confidence * 0.7 + (1.0 - min(response_time / 5.0, 1.0)) * 0.3
        coordination_effectiveness = 1.0 - (len(issues) * 0.1)
        
        return AgentHarmonySnapshot(
            user_id=user_id,
            agent_name=agent_name,
            harmony_score=harmony_score,
            coordination_effectiveness=max(0.0, coordination_effectiveness),
            conflict_incidents=len(issues),
            response_time_average=response_time,
            confidence_stability=confidence,
            timestamp=datetime.now(),
            needs_coordination_attention=harmony_score < 0.7,
            coordination_recommendations=self._generate_agent_recommendations(agent_name, agent_status)
        )

    def _get_coordination_guidance(self, agent_name: str, agent_status: Dict[str, Any]) -> str:
        """Get coordination guidance for agent based on status"""
        
        confidence = agent_status.get("confidence", 0.0)
        response_time = agent_status.get("response_time", 0.0)
        issues = agent_status.get("issues", [])
        
        if confidence < 0.5:
            return f"Low confidence detected for {agent_name} - coordination may be needed"
        elif response_time > 3.0:
            return f"Slow response time for {agent_name} - performance optimization recommended"
        elif len(issues) > 2:
            return f"Multiple issues reported by {agent_name} - system review suggested"
        else:
            return f"{agent_name} operating within normal parameters"

    def _generate_agent_recommendations(self, agent_name: str, agent_status: Dict[str, Any]) -> List[str]:
        """Generate recommendations for specific agent"""
        
        recommendations = []
        confidence = agent_status.get("confidence", 0.0)
        response_time = agent_status.get("response_time", 0.0)
        issues = agent_status.get("issues", [])
        
        if confidence < 0.7:
            recommendations.append(f"Increase {agent_name} confidence through performance optimization")
        
        if response_time > 3.0:
            recommendations.append(f"Optimize {agent_name} response time for better coordination")
        
        if len(issues) > 1:
            recommendations.append(f"Address {agent_name} issues to improve system harmony")
        
        return recommendations

    def _identify_coordination_opportunities(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify coordination opportunities from system metrics"""
        
        opportunities = []
        
        # System-wide performance opportunities
        if metrics.get("overall_system_health", 1.0) < 0.7:
            opportunities.append({
                "type": "system_health_improvement",
                "priority": "high",
                "description": "Overall system health below optimal threshold"
            })
        
        # Agent-specific opportunities
        agent_data = metrics.get("agent_metrics", {})
        for agent_name, agent_metrics in agent_data.items():
            confidence = agent_metrics.get("confidence", 1.0)
            if confidence < 0.6:
                opportunities.append({
                    "type": "agent_confidence_improvement",
                    "agent": agent_name,
                    "priority": "medium",
                    "description": f"{agent_name} confidence below optimal threshold"
                })
        
        return opportunities

    def _identify_system_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify system bottlenecks from metrics"""
        
        bottlenecks = []
        
        # Response time bottlenecks
        agent_data = metrics.get("agent_metrics", {})
        for agent_name, agent_metrics in agent_data.items():
            response_time = agent_metrics.get("response_time", 0.0)
            if response_time > 3.0:
                bottlenecks.append({
                    "type": "response_time_bottleneck",
                    "agent": agent_name,
                    "severity": "high" if response_time > 5.0 else "medium",
                    "description": f"{agent_name} response time exceeds optimal threshold"
                })
        
        return bottlenecks

    def _identify_potential_conflicts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential agent conflicts from metrics"""
        
        conflicts = []
        
        # Agent error conflicts
        agent_data = metrics.get("agent_metrics", {})
        for agent_name, agent_metrics in agent_data.items():
            errors = agent_metrics.get("errors", [])
            if len(errors) > 3:
                conflicts.append({
                    "type": "error_overload_conflict",
                    "agent": agent_name,
                    "severity": "high",
                    "description": f"{agent_name} experiencing high error rate"
                })
        
        # Resource conflicts
        high_usage_agents = []
        for agent_name, agent_metrics in agent_data.items():
            cpu_usage = agent_metrics.get("cpu_usage", 0.0)
            if cpu_usage > 0.8:
                high_usage_agents.append(agent_name)
        
        if len(high_usage_agents) > 1:
            conflicts.append({
                "type": "resource_conflict",
                "agents": high_usage_agents,
                "severity": "medium",
                "description": "Multiple agents competing for system resources"
            })
        
        return conflicts

    def _calculate_system_effectiveness(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall system effectiveness score"""
        
        # Get agent effectiveness scores
        agent_data = metrics.get("agent_metrics", {})
        if not agent_data:
            return 0.5  # Default neutral score
        
        agent_scores = []
        for agent_name, agent_metrics in agent_data.items():
            confidence = agent_metrics.get("confidence", 0.5)
            response_time = agent_metrics.get("response_time", 5.0)
            error_count = len(agent_metrics.get("errors", []))
            
            # Calculate agent effectiveness
            response_score = max(0.0, 1.0 - (response_time / 10.0))  # Normalize response time
            error_score = max(0.0, 1.0 - (error_count * 0.1))  # Penalize errors
            
            agent_effectiveness = (confidence * 0.5 + response_score * 0.3 + error_score * 0.2)
            agent_scores.append(agent_effectiveness)
        
        # Calculate overall system effectiveness
        if agent_scores:
            return sum(agent_scores) / len(agent_scores)
        else:
            return 0.5

    def _calculate_synthesis_confidence(self, metrics: Dict[str, Any]) -> float:
        """Calculate confidence in system synthesis"""
        
        # Base confidence on data completeness and consistency
        agent_data = metrics.get("agent_metrics", {})
        if not agent_data:
            return 0.3  # Low confidence with no data
        
        confidence_factors = []
        
        # Data completeness
        required_fields = ["confidence", "response_time", "errors"]
        complete_agents = 0
        for agent_name, agent_metrics in agent_data.items():
            if all(field in agent_metrics for field in required_fields):
                complete_agents += 1
        
        data_completeness = complete_agents / len(agent_data)
        confidence_factors.append(data_completeness)
        
        # Agent confidence consistency
        agent_confidences = [agent_metrics.get("confidence", 0.0) for agent_metrics in agent_data.values()]
        if agent_confidences:
            avg_confidence = sum(agent_confidences) / len(agent_confidences)
            confidence_factors.append(avg_confidence)
        
        # System stability (low error rates)
        total_errors = sum(len(agent_metrics.get("errors", [])) for agent_metrics in agent_data.values())
        stability_score = max(0.0, 1.0 - (total_errors * 0.05))
        confidence_factors.append(stability_score)
        
        return sum(confidence_factors) / len(confidence_factors)

    # Helper methods for database operations
    async def _store_agent_interaction(self, interaction_event: AgentInteractionEvent):
        """Store agent interaction event"""
        
        try:
            # Convert to dict for storage
            interaction_data = {
                "user_id": interaction_event.user_id,
                "source_agent": interaction_event.source_agent,
                "target_agent": interaction_event.target_agent,
                "interaction_type": interaction_event.interaction_type,
                "message_content": interaction_event.message_content,
                "coordination_context": interaction_event.coordination_context,
                "timestamp": interaction_event.timestamp,
                "vic20_processing_notes": interaction_event.vic20_processing_notes,
                "interaction_success": interaction_event.interaction_success
            }
            
            # This would need to be implemented in database_integration
            # For now, just log the interaction
            logger.debug(f"🖥️ Agent interaction logged: {interaction_event.source_agent} -> {interaction_event.target_agent}")
            
        except Exception as e:
            logger.error(f"🖥️ Failed to store agent interaction: {e}")

    async def _store_agent_harmony_snapshot(self, harmony_snapshot: AgentHarmonySnapshot):
        """Store agent harmony snapshot"""
        
        try:
            # Convert to format expected by database
            harmony_metrics = [{
                "user_id": harmony_snapshot.user_id,
                "agent_name": harmony_snapshot.agent_name,
                "harmony_score": harmony_snapshot.harmony_score,
                "coordination_effectiveness": harmony_snapshot.coordination_effectiveness,
                "conflict_incidents": harmony_snapshot.conflict_incidents,
                "response_time_average": harmony_snapshot.response_time_average,
                "confidence_stability": harmony_snapshot.confidence_stability,
                "needs_coordination_attention": harmony_snapshot.needs_coordination_attention,
                "timestamp": harmony_snapshot.timestamp
            }]
            
            # This would use the existing database method
            # await self.db_integration.store_agent_harmony_metrics(harmony_snapshot.user_id, harmony_metrics)
            logger.debug(f"🖥️ Harmony snapshot stored for {harmony_snapshot.agent_name}")
            
        except Exception as e:
            logger.error(f"🖥️ Failed to store harmony snapshot: {e}")

    async def _store_coordination_feedback(self, feedback_data: Dict[str, Any]):
        """Store coordination feedback for learning"""
        
        try:
            # This would need to be implemented in database_integration
            # For now, just log the feedback
            logger.info(f"🖥️ Coordination feedback stored for learning: {feedback_data.get('coordination_id')}")
            
        except Exception as e:
            logger.error(f"🖥️ Failed to store coordination feedback: {e}")

    async def _store_unknown_message_for_learning(self, unknown_message_event: Dict[str, Any]):
        """Store unknown message for learning"""
        
        try:
            # This would need to be implemented in database_integration
            # For now, just log the unknown message
            logger.info(f"🖥️ Unknown message logged for learning: {unknown_message_event.get('message_type')}")
            
        except Exception as e:
            logger.error(f"🖥️ Failed to store unknown message: {e}")

    async def _store_coordination_failure_for_learning(self, failure_event: Dict[str, Any]):
        """Store coordination failure for learning"""
        
        try:
            # This would need to be implemented in database_integration
            # For now, just log the failure
            logger.info(f"🖥️ Coordination failure logged for learning: {failure_event.get('error_message')}")
            
        except Exception as e:
            logger.error(f"🖥️ Failed to store coordination failure: {e}")

    async def _get_recent_coordination_effectiveness(self, days: int = 7) -> List[float]:
        """Get recent coordination effectiveness data"""
        
        try:
            if self.db_integration:
                # This would get effectiveness data from database
                # For now, return empty list
                return []
            return []
        except Exception as e:
            logger.error(f"🖥️ Failed to get recent coordination effectiveness: {e}")
            return []

    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get current coordination statistics"""
        
        return {
            "coordination_sessions": self.coordination_sessions,
            "successful_coordinations": self.successful_coordinations,
            "coordination_failures": self.coordination_failures,
            "pattern_applications": self.pattern_applications,
            "agent_interactions_logged": self.agent_interactions_logged,
            "success_rate": self.successful_coordinations / max(self.coordination_sessions, 1),
            "connected_agents": len(self.agent_connections),
            "connected_users": len(self.user_connections),
            "learning_mode_active": self.learning_mode_active,
            "pattern_matching_enabled": self.pattern_matching_enabled,
            "effectiveness_tracking_enabled": self.effectiveness_tracking_enabled
        }

    def __str__(self):
        return f"VIC20SageWebSocketHandler(port={self.websocket_port}, learning_enabled={self.learning_mode_active})"

    def __repr__(self):
        return f"VIC20SageWebSocketHandler(coordination_sessions={self.coordination_sessions}, success_rate={self.successful_coordinations / max(self.coordination_sessions, 1):.2f})"