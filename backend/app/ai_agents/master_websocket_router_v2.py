"""
Master WebSocket Router V2
Coordinates all individual agent WebSocket handlers with perfect separation
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

# Import all individual handlers
from .sir_hawkington.hawks_websocket_integration import get_hawkington_websocket_handler
from .meth_snail.methys_websocket_integration import get_meth_snail_websocket_handler
from .hamsters.hamsters_websocket_integration import get_hamsters_websocket_handler
# from .stick.stick_websocket_integration import get_stick_websocket_handler
# from .vic20_sage.vic_20_websocket_integration import get_vic20_websocket_handler
# from .quantum_shadow_people.qsp_websocket_integration import get_qsp_websocket_handler

logger = logging.getLogger("SystemRebellion.WebSocketRouter")

class SystemRebellionWebSocketRouter:
    """
    Master router for all System Rebellion agent WebSocket handlers
    
    Maintains perfect separation while coordinating all agents
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SystemRebellion.WebSocketRouter")
        self.total_processing_count = 0
        self.agent_handlers = {}
        
        self.logger.info("🚀 System Rebellion WebSocket Router V2 initialized - PERFECT SEPARATION ACHIEVED")
    
    async def process_metrics_all_agents(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through all agents with perfect separation
        
        Each agent handler is completely isolated - one fails, others continue
        """
        self.total_processing_count += 1
        
        # Get all handlers
        handlers = {
            'sir_hawkington': await get_hawkington_websocket_handler(),
            'meth_snail': await get_meth_snail_websocket_handler(),
            'hamsters': await get_hamsters_websocket_handler(),
            'stick': await get_stick_websocket_handler(),
            'vic20_sage': await get_vic20_websocket_handler(),
            'quantum_shadow_people': await get_qsp_websocket_handler()
        }
        
        # Process through all agents in parallel with isolation
        results = await asyncio.gather(
            handlers['sir_hawkington'].process_metrics(metrics_data, user_id),
            handlers['meth_snail'].process_metrics(metrics_data, user_id),
            handlers['hamsters'].process_metrics(metrics_data, user_id),
            handlers['stick'].process_metrics(metrics_data, user_id),
            handlers['vic20_sage'].process_metrics(metrics_data, user_id),
            handlers['quantum_shadow_people'].process_metrics(metrics_data, user_id),
            return_exceptions=True
        )
        
        # Combine results with error isolation
        combined_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'processing_id': self.total_processing_count,
            'agents': {},
            'errors': [],
            'successful_agents': [],
            'failed_agents': []
        }
        
        agent_names = ['sir_hawkington', 'meth_snail', 'hamsters', 'stick', 'vic20_sage', 'quantum_shadow_people']
        
        for i, result in enumerate(results):
            agent_name = agent_names[i]
            
            if isinstance(result, Exception):
                # Agent handler failed completely
                combined_results['errors'].append({
                    'agent': agent_name,
                    'error': str(result)
                })
                combined_results['failed_agents'].append(agent_name)
            else:
                # Agent handler succeeded
                combined_results['agents'][agent_name] = result
                combined_results['successful_agents'].append(agent_name)
        
        combined_results['total_agents'] = len(agent_names)
        combined_results['successful_count'] = len(combined_results['successful_agents'])
        combined_results['failed_count'] = len(combined_results['failed_agents'])
        
        return combined_results
    
    async def get_all_agent_stats(self) -> Dict[str, Any]:
        """Get statistics from all agent handlers"""
        handlers = {
            'sir_hawkington': await get_hawkington_websocket_handler(),
            'meth_snail': await get_meth_snail_websocket_handler(),
            'hamsters': await get_hamsters_websocket_handler(),
            'stick': await get_stick_websocket_handler(),
            'vic20_sage': await get_vic20_websocket_handler(),
            'quantum_shadow_people': await get_qsp_websocket_handler()
        }
        
        all_stats = {}
        
        for agent_name, handler in handlers.items():
            try:
                all_stats[agent_name] = handler.get_handler_stats()
            except Exception as e:
                all_stats[agent_name] = {
                    'error': str(e),
                    'status': 'ERROR'
                }
        
        return all_stats

# Global router instance
_websocket_router = None

async def get_websocket_router():
    global _websocket_router
    if _websocket_router is None:
        _websocket_router = SystemRebellionWebSocketRouter()
    return _websocket_router

async def process_all_agents_websocket(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Main entry point for WebSocket processing"""
    router = await get_websocket_router()
    return await router.process_metrics_all_agents(metrics_data, user_id)