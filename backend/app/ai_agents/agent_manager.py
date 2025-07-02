"""
AI Agent Manager

Orchestrates all AI agents and manages their integration with the WebSocket service.
This is the single point of contact for all agent operations.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAIAgent
from .sir_hawkington.hawks_websocket_integration import create_sir_hawkington_handler

logger = logging.getLogger(__name__)

class AIAgentManager:
    """
    Central manager for all AI agents in the System Rebellion.
    
    Handles agent lifecycle, coordination, and provides a unified interface
    for the WebSocket service to interact with all agents.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAIAgent] = {}
        self.initialization_time = datetime.now()
        self.total_processing_count = 0
        self.logger = logging.getLogger("AgentManager")
        
        # Agent processing order (some agents may depend on others)
        self.processing_order = [
            "sir_hawkington",
            # Future agents will be added here
            # "the_stick",
            # "meth_snail", 
            # "hamsters",
            # "vic_20"
        ]
        
        self.logger.info("🤖 AI Agent Manager initialized")
    
    async def initialize_agents(self):
        """
        Initialize all available AI agents.
        
        This method discovers and initializes all agent handlers.
        """
        try:
            # Initialize Sir Hawkington
            sir_hawkington = await create_sir_hawkington_handler()
            self.agents["sir_hawkington"] = sir_hawkington
            
            # Future agent initialization will go here
            # self.agents["the_stick"] = await create_the_stick_handler()
            # self.agents["meth_snail"] = await create_meth_snail_handler()
            # etc.
            
            self.logger.info(f"🤖 Agent Manager initialized {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}", exc_info=True)
            raise
    
    async def process_metrics_through_agents(self, metrics: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process metrics through all active agents in the proper order.
        
        Args:
            metrics: Raw system metrics
            user_context: Optional user context for personalized analysis
            
        Returns:
            Enhanced metrics with all agent analyses
        """
        self.total_processing_count += 1
        enhanced_metrics = metrics.copy()
        
        # Track which agents processed successfully
        processing_results = {
            'successful_agents': [],
            'failed_agents': [],
            'processing_time': datetime.now().isoformat()
        }
        
        # Process through agents in order
        for agent_name in self.processing_order:
            if agent_name not in self.agents:
                self.logger.warning(f"🤖 Agent '{agent_name}' not found in agent registry")
                continue
            
            agent = self.agents[agent_name]
            
            if not agent.is_active:
                self.logger.debug(f"🤖 Agent '{agent_name}' is inactive, skipping")
                continue
            
            try:
                # Process metrics through this agent
                start_time = datetime.now()
                enhanced_metrics = await agent.process_metrics(enhanced_metrics, user_context)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                processing_results['successful_agents'].append({
                    'agent_name': agent_name,
                    'processing_time_seconds': processing_time
                })
                
                self.logger.debug(f"🤖 Agent '{agent_name}' processed metrics successfully in {processing_time:.3f}s")
                
            except Exception as e:
                processing_results['failed_agents'].append({
                    'agent_name': agent_name,
                    'error': str(e)
                })
                
                self.logger.error(f"🤖 Agent '{agent_name}' failed to process metrics: {str(e)}")
                # Continue processing with other agents - don't let one failure break everything
        
        # Add processing metadata
        enhanced_metrics['agent_processing'] = processing_results
        
        return enhanced_metrics
    
    def get_agent_status(self, agent_name: str = None) -> Dict[str, Any]:
        """
        Get status information for a specific agent or all agents.
        
        Args:
            agent_name: Specific agent name, or None for all agents
            
        Returns:
            Agent status information
        """
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name].get_agent_status()
            else:
                return {'error': f'Agent {agent_name} not found'}
        
        # Return status for all agents
        all_status = {
            'manager_status': {
                'total_agents': len(self.agents),
                'active_agents': sum(1 for agent in self.agents.values() if agent.is_active),
                'total_processing_count': self.total_processing_count,
                'uptime_seconds': (datetime.now() - self.initialization_time).total_seconds(),
                'registered_agents': list(self.agents.keys())
            },
            'agents': {}
        }
        
        for name, agent in self.agents.items():
            all_status['agents'][name] = agent.get_agent_status()
        
        return all_status
    
    def activate_agent(self, agent_name: str) -> bool:
        """Activate a specific agent"""
        if agent_name in self.agents:
            self.agents[agent_name].activate()
            self.logger.info(f"🤖 Agent '{agent_name}' activated")
            return True
        return False
    
    def deactivate_agent(self, agent_name: str) -> bool:
        """Deactivate a specific agent"""
        if agent_name in self.agents:
            self.agents[agent_name].deactivate()
            self.logger.info(f"🤖 Agent '{agent_name}' deactivated")
            return True
        return False
    
    def get_active_agents(self) -> List[str]:
        """Get list of currently active agent names"""
        return [name for name, agent in self.agents.items() if agent.is_active]

# Global agent manager instance
_agent_manager: Optional[AIAgentManager] = None

async def get_agent_manager() -> AIAgentManager:
    """
    Get the global agent manager instance (singleton pattern).
    
    Returns:
        Initialized AIAgentManager instance
    """
    global _agent_manager
    
    if _agent_manager is None:
        _agent_manager = AIAgentManager()
        await _agent_manager.initialize_agents()
    
    return _agent_manager