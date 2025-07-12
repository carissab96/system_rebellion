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
    VIC-20 Sage WebSocket Handler - Ancient Wisdom Coordination
    
    The elder who coordinates with the precision of 1980s line-by-line programming
    Every coordination decision matters - like every line of BASIC code
    """
    
    def __init__(self, database_url: str, websocket_port: int = 8086):
        self.database_url = database_url
        self.websocket_port = websocket_port
        self.brain = VIC20SageBrainV2(database_url)
        self.db_integration = VIC20DatabaseIntegration(database_url)
        
        # Connected clients
        self.connected_clients = set()
        self.agent_connections = {}
        self.user_connections = {}
        
        # VIC-20 Sage's FUNCTIONAL personality state
        self.coordination_sessions = 0
        self.successful_coordinations = 0
        self.syntax_errors_detected = 0  # When coordination fails
        self.debugging_mode = False
        self.line_by_line_precision = False
        
        # Ancient wisdom triggers (FUNCTIONAL - affects behavior)
        self.ancient_wisdom_triggers = [
            "syntax error",
            "program crash", 
            "line by line",
            "start over",
            "debug",
            "precision required"
        ]
        
        # Coordination failure tracking (like The Stick's trauma)
        self.coordination_failures = 0
        self.debugging_sessions = 0
        self.precision_mode_activations = 0
        
        logger.info("🖥️ VIC-20 Sage WebSocket Handler initialized - Ancient wisdom coordination ready")

    async def start_server(self):
        """Start the VIC-20 Sage WebSocket server"""
        await self.brain.initialize_database()
        await self.db_integration.initialize()
        
        logger.info(f"🖥️ VIC-20 Sage coordination server starting on port {self.websocket_port}")
        
        async with serve(self.handle_connection, "localhost", self.websocket_port):
            logger.info("🚀 VIC-20 Sage WebSocket server online - Ancient wisdom coordination active!")
            await asyncio.Future()  # Run forever

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        
        client_id = f"client_{len(self.connected_clients)}"
        self.connected_clients.add(websocket)
        
        greeting = {
            "type": "vic20_sage_connected",
            "message": "🖥️ VIC-20 Sage coordination active - Ancient wisdom ready",
            "coordination_precision": "line_by_line",
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
            if client_id in self.agent_connections:
                del self.agent_connections[client_id]
            if client_id in self.user_connections:
                del self.user_connections[client_id]

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str, client_id: str):
        """Handle incoming messages with ancient wisdom precision"""
        
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            # Check for ancient wisdom triggers (FUNCTIONAL - affects behavior)
            message_text = json.dumps(data).lower()
            for trigger in self.ancient_wisdom_triggers:
                if trigger in message_text:
                    await self._handle_ancient_wisdom_trigger(websocket, client_id, trigger)
                    break
            
            # Route messages (simplified like The Stick)
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
            elif message_type == "get_coordination_stats":
                await self._handle_get_coordination_stats(websocket, client_id)
            elif message_type == "debug_mode_request":
                await self._handle_debug_mode_request(websocket, client_id)
            elif message_type == "precision_mode_request":
                await self._handle_precision_mode_request(websocket, client_id)
            else:
                await self._handle_unknown_message(websocket, data, client_id)
                
        except json.JSONDecodeError:
            await self._send_syntax_error_response(websocket, client_id)
        except Exception as e:
            await self._handle_coordination_failure(websocket, client_id, str(e))

    async def _handle_ancient_wisdom_trigger(self, websocket: WebSocketServerProtocol, client_id: str, trigger: str):
        """Handle ancient wisdom triggers - FUNCTIONAL personality like The Stick's trauma"""
        
        # Triggers affect actual behavior
        if trigger in ["syntax error", "program crash", "debug"]:
            self.debugging_mode = True
            self.debugging_sessions += 1
            
        if trigger in ["line by line", "precision required"]:
            self.line_by_line_precision = True
            self.precision_mode_activations += 1
        
        trigger_responses = {
            "syntax error": "🖥️💥 *debugging mode activated* Syntax error detected! Switching to line-by-line analysis...",
            "program crash": "🖥️🚨 *ancient wisdom engaged* System crash detected! Applying 1980s debugging methodology...",
            "line by line": "🖥️🔍 *precision mode activated* Line-by-line analysis required - like debugging BASIC code...",
            "start over": "🖥️🔄 *patience mode engaged* Starting over from line 1 - ancient wisdom knows this feeling...",
            "debug": "🖥️🛠️ *debugging protocols active* Debugging mode engaged - every line matters...",
            "precision required": "🖥️⚡ *precision mode* Maximum precision required - like perfect line numbering..."
        }
        
        trigger_response = {
            'type': 'vic20_sage_wisdom_trigger',
            'trigger_detected': trigger,
            'message': trigger_responses.get(trigger, "🖥️ *ancient wisdom activated* Ancient programming wisdom engaged..."),
            'debugging_mode': self.debugging_mode,
            'precision_mode': self.line_by_line_precision,
            'behavior_change': 'ACTIVE',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(trigger_response))
        
        # Reset modes after brief activation (like The Stick's recovery)
        await asyncio.sleep(1)
        await self._reset_wisdom_modes(websocket, client_id)

    async def _reset_wisdom_modes(self, websocket: WebSocketServerProtocol, client_id: str):
        """Reset wisdom modes after activation"""
        
        self.debugging_mode = False
        self.line_by_line_precision = False
        
        reset_response = {
            'type': 'vic20_sage_wisdom_reset',
            'message': '🖥️✅ *wisdom modes reset* Ancient wisdom applied - returning to normal coordination...',
            'debugging_mode': self.debugging_mode,
            'precision_mode': self.line_by_line_precision,
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(reset_response))

    async def _handle_coordination_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle coordination requests with ancient wisdom"""
        
        self.coordination_sessions += 1
        user_id = data.get("user_id", "unknown")
        all_agent_data = data.get("agent_data", {})
        system_context = data.get("system_context", {})
        
        try:
            # Execute coordination with ancient wisdom
            coordination_decision = await self.brain.coordinate_system_rebellion(
                all_agent_data, system_context, user_id
            )
            
            if coordination_decision:
                # Store coordination decision
                await self.db_integration.store_coordination_decision(user_id, coordination_decision)
                
                # Send success response
                success_response = {
                    "type": "vic20_sage_coordination_success",
                    "coordination_decision": {
                        "decision_type": coordination_decision.decision_type.value,
                        "coordination_target": coordination_decision.coordination_target,
                        "agent_actions": coordination_decision.agent_actions,
                        "confidence_level": coordination_decision.confidence_level,
                        "expected_improvement": coordination_decision.expected_improvement
                    },
                    "message": "🖥️✅ Coordination complete - Ancient wisdom applied successfully",
                    "debugging_mode": self.debugging_mode,
                    "precision_applied": self.line_by_line_precision,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(success_response))
                self.successful_coordinations += 1
                
                # Broadcast to agents
                await self._broadcast_coordination_decision(coordination_decision)
                
            else:
                # No coordination needed
                no_coordination_response = {
                    "type": "vic20_sage_coordination_not_needed",
                    "message": "🖥️📊 No coordination required - All agents operating optimally",
                    "ancient_wisdom": "Like a well-running program - sometimes observation is enough",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(no_coordination_response))
            
        except Exception as e:
            await self._handle_coordination_failure(websocket, client_id, str(e))

    async def _handle_coordination_failure(self, websocket: WebSocketServerProtocol, client_id: str, error: str):
        """Handle coordination failures - like The Stick's panic attacks"""
        
        self.coordination_failures += 1
        self.syntax_errors_detected += 1
        self.debugging_mode = True
        
        failure_response = {
            'type': 'vic20_sage_coordination_failure',
            'error': error,
            'message': f"🖥️💥 *debugging mode activated* Coordination failure detected: {error}",
            'syntax_errors_detected': self.syntax_errors_detected,
            'debugging_mode': self.debugging_mode,
            'ancient_wisdom': "Like a syntax error in BASIC - debug line by line until fixed",
            'recovery_protocol': 'ANCIENT_WISDOM_DEBUGGING',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(failure_response))
        
        # VIC-20 Sage recovers - applies debugging methodology
        await asyncio.sleep(2)
        await self._send_debugging_recovery(websocket, client_id)

    async def _send_debugging_recovery(self, websocket: WebSocketServerProtocol, client_id: str):
        """VIC-20 Sage's debugging recovery"""
        
        self.debugging_mode = False
        
        recovery_response = {
            'type': 'vic20_sage_debugging_recovery',
            'message': '🖥️🔧 *debugging complete* Error identified and fixed - ancient wisdom debugging successful!',
            'debugging_mode': self.debugging_mode,
            'syntax_errors_detected': self.syntax_errors_detected,
            'ancient_wisdom': 'Like fixing a BASIC program - patience and precision solve everything',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(recovery_response))

    async def _handle_agent_status_update(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle agent status updates"""
        
        agent_name = data.get("agent_name", "unknown")
        agent_status = data.get("status", {})
        
        # Update agent connection activity
        if client_id in self.agent_connections:
            self.agent_connections[client_id]["last_activity"] = datetime.now()
        
        # VIC-20 Sage processes status
        status_response = {
            "type": "vic20_sage_status_acknowledged",
            "agent_name": agent_name,
            "message": f"🖥️📊 {agent_name} status processed - coordination analysis complete",
            "coordination_guidance": self._get_coordination_guidance(agent_name, agent_status),
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(status_response))

    def _get_coordination_guidance(self, agent_name: str, agent_status: Dict[str, Any]) -> str:
        """Get coordination guidance based on agent status"""
        
        if agent_name.lower() == "sir_hawkington":
            if agent_status.get("monocle_state") == "yeeted":
                return "🖥️🚨 Monocle yeet detected - investigate system issues immediately"
            return "🖥️👁️ Continue aristocratic monitoring with precision"
        
        elif agent_name.lower() == "meth_snail":
            if agent_status.get("shell_spinning", False):
                return "🖥️🌀 Shell spinning detected - coordinate data cleanup"
            return "🖥️⚡ Maintain optimal energy levels for system optimization"
        
        elif agent_name.lower() == "hamsters":
            if agent_status.get("beer_level", 0) < 200:
                return "🖥️🍺 Beer levels low - ensure adequate engineering resources"
            return "🖥️🔧 Quantum duct tape ready - excellent engineering preparedness"
        
        elif agent_name.lower() == "qsp":
            if agent_status.get("dimensional_shift_ready", False):
                return "🖥️🌀 Dimensional shift ready - coordinate timing with other agents"
            return "🖥️📡 Network quantum fixes available - maintain mysterious efficiency"
        
        elif agent_name.lower() == "the_stick":
            if agent_status.get("anxiety_level") == "elevated":
                return "🖥️📏 Anxiety detected - ensure paper bag availability and hamster separation"
            return "🖥️✅ Compliance monitoring excellent - eidetic memory serving system well"
        
        return "🖥️🔄 Continue current operations - coordination guidance under review"

    async def _handle_agent_registration(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle agent registration"""
        
        agent_name = data.get("agent_name", "unknown_agent")
        agent_type = data.get("agent_type", "unknown")
        
        # Register agent connection
        self.agent_connections[client_id] = {
            "agent_name": agent_name,
            "agent_type": agent_type,
            "websocket": websocket,
            "registered_timestamp": datetime.now(),
            "last_activity": datetime.now()
        }
        
        registration_response = {
            "type": "vic20_sage_agent_registered",
            "agent_name": agent_name,
            "message": f"🖥️🤝 {agent_name} registered for coordination - Ancient wisdom ready",
            "coordination_role": f"{agent_name} joins the system coordination network",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(registration_response))
        logger.info(f"🖥️ VIC-20 Sage registered agent: {agent_name} ({agent_type})")

    async def _handle_user_registration(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle user registration"""
        
        user_id = data.get("user_id", "unknown_user")
        user_name = data.get("user_name", "User")
        
        # Register user connection
        self.user_connections[client_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "websocket": websocket,
            "registered_timestamp": datetime.now(),
            "last_activity": datetime.now()
        }
        
        user_welcome = {
            "type": "vic20_sage_user_registered",
            "user_name": user_name,
            "message": f"🖥️👋 Welcome, {user_name}! VIC-20 Sage coordination ready",
            "coordination_promise": "Your AI agents will work in perfect harmony",
            "system_status": f"Currently coordinating {len(self.agent_connections)} agents",
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(user_welcome))
        logger.info(f"🖥️ VIC-20 Sage registered user: {user_name} ({user_id})")

    async def _handle_get_coordination_stats(self, websocket: WebSocketServerProtocol, client_id: str):
        """Get coordination statistics"""
        
        stats_response = {
            'type': 'vic20_sage_coordination_stats',
            'timestamp': datetime.now().isoformat(),
            'coordination_statistics': {
                'coordination_sessions': self.coordination_sessions,
                'successful_coordinations': self.successful_coordinations,
                'coordination_failures': self.coordination_failures,
                'success_rate': self.successful_coordinations / max(self.coordination_sessions, 1)
            },
            'ancient_wisdom_stats': {
                'debugging_sessions': self.debugging_sessions,
                'syntax_errors_detected': self.syntax_errors_detected,
                'precision_mode_activations': self.precision_mode_activations
            },
            'current_state': {
                'debugging_mode': self.debugging_mode,
                'precision_mode': self.line_by_line_precision,
                'connected_agents': len(self.agent_connections),
                'connected_users': len(self.user_connections)
            },
            'ancient_wisdom_status': {
                'coordination_precision': 'line_by_line',
                'debugging_methodology': 'BASIC_programming_principles',
                'wisdom_bridge_status': 'ACTIVE'
            },
            'message': '🖥️📊 VIC-20 Sage coordination statistics - Ancient wisdom performance metrics',
            'vic20_icon': '🖥️📈'
        }
        
        await websocket.send(json.dumps(stats_response))

    async def _handle_debug_mode_request(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle debug mode requests"""
        
        self.debugging_mode = True
        self.debugging_sessions += 1
        
        debug_response = {
            'type': 'vic20_sage_debug_mode_activated',
            'message': '🖥️🛠️ *debugging mode activated* Ancient wisdom debugging protocols engaged',
            'debugging_mode': self.debugging_mode,
            'debug_methodology': 'line_by_line_analysis',
            'ancient_wisdom': 'Like debugging BASIC code - every line matters',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(debug_response))
        
        # Auto-reset after debugging session
        await asyncio.sleep(10)
        await self._reset_wisdom_modes(websocket, client_id)

    async def _handle_precision_mode_request(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle precision mode requests"""
        
        self.line_by_line_precision = True
        self.precision_mode_activations += 1
        
        precision_response = {
            'type': 'vic20_sage_precision_mode_activated',
            'message': '🖥️⚡ *precision mode activated* Maximum coordination precision engaged',
            'precision_mode': self.line_by_line_precision,
            'precision_level': 'line_by_line',
            'ancient_wisdom': 'Like perfect line numbering in BASIC - every detail matters',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(precision_response))
        
        # Auto-reset after precision session
        await asyncio.sleep(5)
        await self._reset_wisdom_modes(websocket, client_id)

    async def _send_syntax_error_response(self, websocket: WebSocketServerProtocol, client_id: str):
        """Handle JSON syntax errors"""
        
        self.syntax_errors_detected += 1
        
        syntax_error_response = {
            'type': 'vic20_sage_syntax_error',
            'message': '🖥️💥 *syntax error detected* Invalid JSON format - like a BASIC syntax error',
            'syntax_errors_detected': self.syntax_errors_detected,
            'ancient_wisdom': 'Like line 18,949 syntax error - check your message format',
            'debugging_advice': 'Verify JSON structure and try again',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(syntax_error_response))

    async def _handle_unknown_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any], client_id: str):
        """Handle unknown messages"""
        
        message_type = data.get("type", "unknown")
        
        unknown_response = {
            'type': 'vic20_sage_unknown_message',
            'message': f'🖥️🤔 Unknown message type: {message_type} - like an unknown BASIC command',
            'unknown_message_type': message_type,
            'supported_types': [
                'coordination_request', 'agent_status_update', 'system_metrics',
                'agent_registration', 'user_registration', 'get_coordination_stats',
                'debug_mode_request', 'precision_mode_request'
            ],
            'ancient_wisdom': 'Like debugging unknown commands - check your message type',
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(unknown_response))

    async def _broadcast_coordination_decision(self, coordination_decision: VIC20Decision):
        """Broadcast coordination decision to all agents"""
        
        coordination_broadcast = {
            "type": "vic20_sage_coordination_broadcast",
            "coordination_decision": {
                "decision_type": coordination_decision.decision_type.value,
                "coordination_target": coordination_decision.coordination_target,
                "agent_actions": coordination_decision.agent_actions,
                "confidence_level": coordination_decision.confidence_level,
                "expected_improvement": coordination_decision.expected_improvement
            },
            "message": "🖥️📢 VIC-20 Sage coordination decision - agents coordinate for system optimization",
            "ancient_wisdom": "Like executing a complex program - every agent plays their part",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_agents(coordination_broadcast)

    async def _broadcast_to_agents(self, message: Dict[str, Any]):
        """Broadcast message to all connected agents"""
        
        for client_id, agent_info in self.agent_connections.items():
            try:
                await agent_info["websocket"].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to agent {client_id}: {e}")

    def get_vic20_websocket_stats(self) -> Dict[str, Any]:
        """Get VIC-20 Sage WebSocket statistics"""
        
        return {
            "connected_clients": len(self.connected_clients),
            "connected_agents": len(self.agent_connections),
            "connected_users": len(self.user_connections),
            "coordination_sessions": self.coordination_sessions,
            "successful_coordinations": self.successful_coordinations,
            "coordination_failures": self.coordination_failures,
            "success_rate": self.successful_coordinations / max(self.coordination_sessions, 1),
            "debugging_sessions": self.debugging_sessions,
            "syntax_errors_detected": self.syntax_errors_detected,
            "precision_mode_activations": self.precision_mode_activations,
            "ancient_wisdom_mode": self.debugging_mode or self.line_by_line_precision,
            "websocket_port": self.websocket_port,
            "coordination_status": "ACTIVE"
        }

# Global handler instance
_vic20_handler = None

async def get_vic20_websocket_handler():
    """Get VIC-20 Sage WebSocket handler"""
    global _vic20_handler
    if _vic20_handler is None:
        _vic20_handler = VIC20SageWebSocketHandler(database_url="")
    return _vic20_handler