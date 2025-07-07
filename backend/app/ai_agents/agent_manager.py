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
from .sir_hawkington.decision_engine import SirHawkingtonBrainV2
from .meth_snail.decision_engine import MethSnailBrainV2
from .hamsters.decision_engine import HamstersBrainV2
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
        self._initialized = False  # Track initialization state
        
        # Agent processing order (some agents may depend on others)
        self.processing_order = [
            "sir_hawkington",
            "meth_snail",  # Move this up - he's operational!
            # Future agents will be added here
            # "the_stick",
            "hamsters",
            # "quantum_shadows",
            # "the_sage"
        ]
        
        self.logger.info("🤖 AI Agent Manager initialized")
    
    async def initialize_agents(self):
        """
        Initialize all available AI agents.
        
        This method discovers and initializes all agent handlers.
        """
        if self._initialized:
            self.logger.debug("🤖 Agents already initialized, skipping")
            return
            
        try:
            # Initialize Sir Hawkington
            sir_hawkington = SirHawkingtonBrainV2()
            self.agents["sir_hawkington"] = sir_hawkington
            
            # Initialize Meth Snail (he's ready!)
            meth_snail = MethSnailBrainV2()
            self.agents["meth_snail"] = meth_snail

            # Initialize Hamsters
            hamsters = HamstersBrainV2()
            self.agents["hamsters"] = hamsters
            
            # Future agent initialization will go here
            # self.agents["the_stick"] = await create_the_stick_handler()

            # self.agents["quantum_shadows"] = await create_quantum_shadows_handler()
            # self.agents["the_sage"] = await create_the_sage_handler()
            
            self._initialized = True
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
        if not self._initialized:
            await self.initialize_agents()
            
        self.total_processing_count += 1
        enhanced_metrics = metrics.copy()
        
        # Track which agents processed successfully
        processing_results = {
            'successful_agents': [],
            'failed_agents': [],
            'processing_time': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if a.is_active])
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
                'initialized': self._initialized,
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
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        self.logger.info("🔥 Shutting down AI Agent Manager...")
        
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'shutdown'):
                    await agent.shutdown()
                self.logger.info(f"✅ {agent_name} shut down successfully")
            except Exception as e:
                self.logger.error(f"❌ Error shutting down {agent_name}: {e}")
        
        self.agents.clear()
        self._initialized = False
        self.logger.info("🎭 AI Agent Manager shutdown complete")

# Global agent manager instance
_agent_manager: Optional[AIAgentManager] = None
_initialization_lock = asyncio.Lock()

async def get_agent_manager() -> AIAgentManager:
    """
    Get the global agent manager instance (singleton pattern).
    Thread-safe initialization with async lock.
    
    Returns:
        Initialized AIAgentManager instance
    """
    global _agent_manager
    
    if _agent_manager is None:
        async with _initialization_lock:
            # Double-check pattern for thread safety
            if _agent_manager is None:
                _agent_manager = AIAgentManager()
                await _agent_manager.initialize_agents()
    
    return _agent_manager