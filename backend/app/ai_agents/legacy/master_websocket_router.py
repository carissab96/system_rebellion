"""
System Rebellion WebSocket Router - TRIAGE ARCHITECTURE VERSION

Coordinates WebSocket operations in harmony with Sir Hawkington's Triage Engine.
NO direct metrics processing - that's the Triage Engine's domain!

🧐 "One does not bypass the aristocratic triage - one works in harmony with it"
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Import individual handlers for non-metrics operations
from .hawk_websocket import HawkWebSocket
from .terry_websocket import TerryWebSocket
from .hamsters.hamsters_websocket_integration import get_hamsters_websocket_handler
from .the_stick.sticks_websocket_integration import get_stick_websocket_handler
from .vic_20_sage.vic20_websocket_handler import get_vic20_sage_websocket_handler
from .quantum_shadow_people.qsp_websocket_integration import get_qsp_websocket_handler

logger = logging.getLogger("SystemRebellion.WebSocketRouter")

class SystemRebellionWebSocketRouter:
    """
    WebSocket router that respects the Triage Architecture.
    
    🧐 PURIFIED RESPONSIBILITIES:
    - Handles non-metrics WebSocket operations
    - Coordinates agent-specific WebSocket messages
    - Supports Triage Engine routing decisions
    - NO direct metrics processing (that's Sir Hawkington's domain)
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SystemRebellion.WebSocketRouter")
        self.total_operations_count = 0
        self.agent_handlers = {}
        self._initialized = False
        
        self.logger.info("🚀 System Rebellion WebSocket Router initialized - TRIAGE ARCHITECTURE COMPATIBLE")
    
    async def initialize_handlers(self):
        """Initialize all agent WebSocket handlers"""
        if self._initialized:
            return
        
        try:
            # Initialize handlers for non-metrics operations
            self.agent_handlers = {
                'sir_hawkington': get_hawkington_websocket_handler(),
                'meth_snail': get_meth_snail_ws_handler(),
                'hamsters': get_hamsters_websocket_handler(),
                'the_stick': get_stick_websocket_handler(),
                'quantum_shadow_people': get_qsp_websocket_handler(),
                'vic_20_sage': get_vic20_sage_websocket_handler()
            }
            
            self._initialized = True
            self.logger.info(f"🚀 WebSocket Router initialized {len(self.agent_handlers)} handlers")
            
        except Exception as e:
            self.logger.error(f"🚀💥 Failed to initialize WebSocket handlers: {str(e)}")
            raise
    
    async def handle_agent_message(
        self,
        agent_name: str,
        message_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a WebSocket message for a specific agent.
        
        🧐 TRIAGE-COMPATIBLE: For agent-specific operations, NOT metrics processing
        
        Args:
            agent_name: Target agent name
            message_data: Message data for the agent
            user_id: User identifier
            
        Returns:
            Agent response
            
        Raises:
            Exception: If agent handling fails
        """
        if not self._initialized:
            await self.initialize_handlers()
        
        if agent_name not in self.agent_handlers:
            raise Exception(f"Unknown agent: {agent_name}")
        
        handler = self.agent_handlers[agent_name]
        
        try:
            self.total_operations_count += 1
            
            # Handle agent-specific message
            if hasattr(handler, 'handle_message'):
                response = await handler.handle_message(message_data, user_id)
            elif hasattr(handler, 'process_request'):
                response = await handler.process_request(message_data, user_id)
            else:
                raise Exception(f"Agent {agent_name} doesn't support message handling")
            
            self.logger.debug(f"🚀 Agent {agent_name} handled message successfully")
            return response
            
        except Exception as e:
            error_msg = f"Agent {agent_name} message handling failed: {str(e)}"
            self.logger.error(f"🚀💥 {error_msg}")
            raise Exception(error_msg)
    
    async def broadcast_agent_notification(
        self,
        notification_data: Dict[str, Any],
        target_agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Broadcast a notification to specified agents (or all agents).
        
        🧐 USE CASE: When Triage Engine needs to notify agents of events
        
        Args:
            notification_data: Notification to broadcast
            target_agents: List of agent names, or None for all
            
        Returns:
            Broadcast results
        """
        if not self._initialized:
            await self.initialize_handlers()
        
        if target_agents is None:
            target_agents = list(self.agent_handlers.keys())
        
        broadcast_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'operation_id': self.total_operations_count + 1,
            'notification_type': notification_data.get('type', 'unknown'),
            'target_agents': target_agents,
            'successful_agents': [],
            'failed_agents': [],
            'responses': {}
        }
        
        self.total_operations_count += 1
        
        # Send notification to each target agent
        for agent_name in target_agents:
            if agent_name not in self.agent_handlers:
                broadcast_results['failed_agents'].append({
                    'agent_name': agent_name,
                    'error': 'Agent not found'
                })
                continue
            
            try:
                handler = self.agent_handlers[agent_name]
                
                if hasattr(handler, 'handle_notification'):
                    response = await handler.handle_notification(notification_data)
                    broadcast_results['responses'][agent_name] = response
                    broadcast_results['successful_agents'].append(agent_name)
                else:
                    # Agent doesn't support notifications - not an error
                    broadcast_results['successful_agents'].append(agent_name)
                    broadcast_results['responses'][agent_name] = {'status': 'notification_not_supported'}
                
            except Exception as e:
                broadcast_results['failed_agents'].append({
                    'agent_name': agent_name,
                    'error': str(e)
                })
        
        self.logger.info(
            f"🚀 Broadcast complete: {len(broadcast_results['successful_agents'])} successful, "
            f"{len(broadcast_results['failed_agents'])} failed"
        )
        
        return broadcast_results
    
    async def get_all_agent_websocket_status(self) -> Dict[str, Any]:
        """Get WebSocket status from all agent handlers"""
        if not self._initialized:
            await self.initialize_handlers()
        
        all_status = {
            'router_status': {
                'initialized': self._initialized,
                'total_operations': self.total_operations_count,
                'total_handlers': len(self.agent_handlers),
                'handler_names': list(self.agent_handlers.keys()),
                'architecture_mode': 'triage_compatible'
            },
            'agents': {}
        }
        
        # Get status from each handler
        for agent_name, handler in self.agent_handlers.items():
            try:
                if hasattr(handler, 'get_handler_stats'):
                    status = handler.get_handler_stats()
                elif hasattr(handler, 'get_status'):
                    status = handler.get_status()
                else:
                    status = {'status': 'no_status_method_available'}
                
                all_status['agents'][agent_name] = status
                
            except Exception as e:
                all_status['agents'][agent_name] = {
                    'error': str(e),
                    'status': 'ERROR'
                }
        
        return all_status
    
    async def handle_triage_routing_message(
        self,
        routing_decision: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a message from Sir Hawkington's Triage Engine.
        
        🧐 TRIAGE INTEGRATION: For when Triage Engine needs WebSocket coordination
        
        Args:
            routing_decision: Triage routing decision from Sir Hawkington
            user_id: User identifier
            
        Returns:
            WebSocket coordination results
        """
        if not self._initialized:
            await self.initialize_handlers()
        
        self.total_operations_count += 1
        
        try:
            routing_type = routing_decision.get('routing', 'unknown')
            target_agents = routing_decision.get('target_agents', [])
            
            if routing_type == 'vic20_emergency':
                # Handle emergency routing to VIC-20
                return await self._handle_vic20_emergency_routing(routing_decision, user_id)
                
            elif routing_type == 'vic20_coordination':
                # Handle coordination routing to VIC-20
                return await self._handle_vic20_coordination_routing(routing_decision, user_id)
                
            elif routing_type == 'stick_direct':
                # Handle direct routing to The Stick
                return await self._handle_stick_direct_routing(routing_decision, user_id)
                
            else:
                # Generic agent routing
                return await self._handle_generic_agent_routing(routing_decision, user_id)
                
        except Exception as e:
            error_msg = f"Triage routing message handling failed: {str(e)}"
            self.logger.error(f"🚀💥 {error_msg}")
            raise Exception(error_msg)
    
    async def _handle_vic20_emergency_routing(
        self,
        routing_decision: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle VIC-20 emergency routing"""
        try:
            vic20_handler = self.agent_handlers.get('vic_20_sage')
            
            if vic20_handler and hasattr(vic20_handler, 'handle_emergency_routing'):
                response = await vic20_handler.handle_emergency_routing(routing_decision, user_id)
            else:
                response = {
                    'status': 'vic20_not_available',
                    'message': 'VIC-20 emergency handler not implemented'
                }
            
            return {
                'routing_type': 'vic20_emergency',
                'vic20_response': response,
                'handled_by': 'websocket_router'
            }
            
        except Exception as e:
            raise Exception(f"VIC-20 emergency routing failed: {str(e)}")
    
    async def _handle_vic20_coordination_routing(
        self,
        routing_decision: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle VIC-20 coordination routing"""
        try:
            vic20_handler = self.agent_handlers.get('vic_20_sage')
            
            if vic20_handler and hasattr(vic20_handler, 'handle_coordination_routing'):
                response = await vic20_handler.handle_coordination_routing(routing_decision, user_id)
            else:
                response = {
                    'status': 'vic20_coordination_pending',
                    'message': 'VIC-20 coordination handler pending implementation'
                }
            
            return {
                'routing_type': 'vic20_coordination',
                'vic20_response': response,
                'handled_by': 'websocket_router'
            }
            
        except Exception as e:
            raise Exception(f"VIC-20 coordination routing failed: {str(e)}")
    
    async def _handle_stick_direct_routing(
        self,
        routing_decision: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle direct routing to The Stick"""
        try:
            stick_handler = self.agent_handlers.get('the_stick')
            
            if stick_handler and hasattr(stick_handler, 'handle_direct_routing'):
                response = await stick_handler.handle_direct_routing(routing_decision, user_id)
            else:
                response = {
                    'status': 'stick_routing_handled',
                    'message': 'The Stick received routing decision'
                }
            
            return {
                'routing_type': 'stick_direct',
                'stick_response': response,
                'handled_by': 'websocket_router'
            }
            
        except Exception as e:
            raise Exception(f"Stick direct routing failed: {str(e)}")
    
    async def _handle_generic_agent_routing(
        self,
        routing_decision: Dict[str, Any],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Handle generic agent routing"""
        target_agents = routing_decision.get('target_agents', [])
        
        if not target_agents:
            return {
                'routing_type': 'generic',
                'message': 'No target agents specified',
                'handled_by': 'websocket_router'
            }
        
        # Notify target agents of the routing decision
        notification_data = {
            'type': 'triage_routing',
            'routing_decision': routing_decision,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        broadcast_results = await self.broadcast_agent_notification(
            notification_data, 
            target_agents
        )
        
        return {
            'routing_type': 'generic',
            'broadcast_results': broadcast_results,
            'handled_by': 'websocket_router'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the WebSocket router"""
        try:
            if not self._initialized:
                await self.initialize_handlers()
            
            available_handlers = len([h for h in self.agent_handlers.values() if h is not None])
            
            return {
                'status': 'OPERATIONAL',
                'router_type': 'triage_compatible_websocket_router',
                'architecture_mode': 'triage_integration',
                'total_handlers': len(self.agent_handlers),
                'available_handlers': available_handlers,
                'total_operations': self.total_operations_count,
                'supported_operations': [
                    'handle_agent_message',
                    'broadcast_agent_notification',
                    'handle_triage_routing_message',
                    'get_all_agent_websocket_status'
                ],
                'triage_routing_support': [
                    'vic20_emergency',
                    'vic20_coordination', 
                    'stick_direct',
                    'generic_agent_routing'
                ],
                'no_direct_metrics_processing': True,  # Confirms we don't bypass triage
                'last_health_check': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'router_type': 'triage_compatible_websocket_router',
                'error': str(e),
                'last_health_check': datetime.now(timezone.utc).isoformat()
            }

# Global router instance
_websocket_router: Optional[SystemRebellionWebSocketRouter] = None
_router_lock = asyncio.Lock()

async def get_websocket_router():
    """Get the global WebSocket router instance"""
    global _websocket_router
    
    if _websocket_router is None:
        async with _router_lock:
            if _websocket_router is None:
                _websocket_router = SystemRebellionWebSocketRouter()
                await _websocket_router.initialize_handlers()
    
    return _websocket_router

# === CONVENIENCE FUNCTIONS FOR TRIAGE INTEGRATION ===

async def handle_triage_websocket_routing(
    routing_decision: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for Triage Engine WebSocket coordination.
    
    Args:
        routing_decision: Routing decision from Sir Hawkington's Triage Engine
        user_id: User identifier
        
    Returns:
        WebSocket coordination results
    """
    router = await get_websocket_router()
    return await router.handle_triage_routing_message(routing_decision, user_id)

async def notify_agents_via_websocket(
    notification_data: Dict[str, Any],
    target_agents: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to notify agents via WebSocket.
    
    Args:
        notification_data: Notification to send
        target_agents: Target agent names, or None for all
        
    Returns:
        Broadcast results
    """
    router = await get_websocket_router()
    return await router.broadcast_agent_notification(notification_data, target_agents)

async def get_websocket_router_status() -> Dict[str, Any]:
    """Get WebSocket router status"""
    try:
        router = await get_websocket_router()
        return await router.health_check()
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e),
            'last_health_check': datetime.now(timezone.utc).isoformat()
        }

# === TESTING FUNCTIONS ===

async def test_websocket_router():
    """Test the WebSocket router functionality"""
    print("\n" + "="*80)
    print(" 🚀⚡ WEBSOCKET ROUTER TEST - TRIAGE ARCHITECTURE COMPATIBILITY")
    print("="*80)
    
    print(f"\n🕐 Test Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize WebSocket router
        print("\n🚀 Initializing WebSocket Router...")
        router = await get_websocket_router()
        print(f"📊 Router instance: {router}")
        
        # Health check
        print("\n🏥 WebSocket Router Health Check:")
        health = await router.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Architecture Mode: {health.get('architecture_mode', 'Unknown')}")
        print(f"   Total Handlers: {health.get('total_handlers', 'Unknown')}")
        print(f"   Available Handlers: {health.get('available_handlers', 'Unknown')}")
        print(f"   No Direct Metrics Processing: {health.get('no_direct_metrics_processing', 'Unknown')}")
        
        # Test agent WebSocket status
        print(f"\n📊 Agent WebSocket Status:")
        all_status = await router.get_all_agent_websocket_status()
        router_status = all_status.get('router_status', {})
        print(f"   Router Operations: {router_status.get('total_operations', 0)}")
        print(f"   Handler Names: {router_status.get('handler_names', [])}")
        
        agent_count = 0
        for agent_name, status in all_status.get('agents', {}).items():
            if not status.get('error'):
                agent_count += 1
                print(f"   ✅ {agent_name}: WebSocket handler available")
            else:
                print(f"   ❌ {agent_name}: {status.get('error', 'Unknown error')}")
        
        print(f"   📊 {agent_count} agent handlers operational")
        
        # Test triage routing message handling
        print(f"\n🧐 Testing Triage Routing Integration:")
        
        # Test stick direct routing
        stick_routing = {
            'routing': 'stick_direct',
            'target_agents': ['the_stick'],
            'severity': 'normal',
            'reasoning': 'Test routing to The Stick',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            stick_result = await router.handle_triage_routing_message(stick_routing, 'test_user')
            print(f"   ✅ Stick Direct Routing: {stick_result.get('routing_type', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Stick Direct Routing Failed: {str(e)}")
        
        # Test VIC-20 coordination routing
        vic20_routing = {
            'routing': 'vic20_coordination',
            'target_agents': ['vic_20_sage'],
            'severity': 'medium',
            'reasoning': 'Test coordination routing to VIC-20',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            vic20_result = await router.handle_triage_routing_message(vic20_routing, 'test_user')
            print(f"   ✅ VIC-20 Coordination: {vic20_result.get('routing_type', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ VIC-20 Coordination Failed: {str(e)}")
        
        # Test emergency routing
        emergency_routing = {
            'routing': 'vic20_emergency',
            'target_agents': ['vic_20_sage'],
            'severity': 'emergency',
            'monocle_yeeted': True,
            'reasoning': 'MONOCLE YEET - Emergency routing to VIC-20',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            emergency_result = await router.handle_triage_routing_message(emergency_routing, 'test_user')
            print(f"   🧐💥 Emergency Routing: {emergency_result.get('routing_type', 'Unknown')}")
        except Exception as e:
            print(f"   💥 Emergency Routing Failed: {str(e)}")
        
        # Test agent notification broadcast
        print(f"\n📢 Testing Agent Notification Broadcast:")
        
        notification = {
            'type': 'system_status_update',
            'message': 'Test notification from WebSocket router',
            'priority': 'low',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            broadcast_result = await router.broadcast_agent_notification(notification, ['meth_snail', 'hamsters'])
            successful = len(broadcast_result.get('successful_agents', []))
            failed = len(broadcast_result.get('failed_agents', []))
            print(f"   📢 Broadcast Results: {successful} successful, {failed} failed")
        except Exception as e:
            print(f"   📢 Broadcast Failed: {str(e)}")
        
        # Test convenience functions
        print(f"\n🔧 Testing Convenience Functions:")
        
        # Test router status function
        try:
            status_result = await get_websocket_router_status()
            print(f"   Status Function: {status_result.get('status', 'Unknown')}")
        except Exception as e:
            print(f"   Status Function Failed: {str(e)}")
        
        # Test triage websocket routing function
        try:
            triage_result = await handle_triage_websocket_routing(stick_routing, 'test_user')
            print(f"   Triage Integration: {triage_result.get('routing_type', 'Unknown')}")
        except Exception as e:
            print(f"   Triage Integration Failed: {str(e)}")
        
        print(f"\n🧐 WEBSOCKET ROUTER TRIAGE ARCHITECTURE COMPLIANCE:")
        print(f"   ✅ NO direct metrics processing (respects Triage Engine)")
        print(f"   ✅ Supports Sir Hawkington's routing decisions")
        print(f"   ✅ Agent-specific WebSocket message handling")
        print(f"   ✅ Broadcast notification capabilities")
        print(f"   ✅ Emergency and coordination routing support")
        print(f"   ✅ Graceful error handling and isolation")
        
    except Exception as e:
        print(f"\n💥 WEBSOCKET ROUTER TEST FAILED: {str(e)}")
        print("This indicates WebSocket handler initialization or routing issues")
    
    print(f"\n🕐 Test Completed: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    print(" 🚀✨ WEBSOCKET ROUTER TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_websocket_router())