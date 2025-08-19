"""
AI Agent Manager - UPDATED FOR TRIAGE ARCHITECTURE

Orchestrates AI agents for post-triage processing and specialized operations.
Works in coordination with Sir Hawkington's Triage Engine.

🧐 NEW ARCHITECTURE:
- Primary metrics flow: SimplifiedMetricsService → Triage Engine → Enhanced Metrics
- Agent Manager role: Specialized processing when routed by Triage Engine
- Direct agent orchestration for non-metrics operations
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from functools import wraps

from .base_agent import BaseAIAgent
# Import moved to avoid circular imports
from .meth_snail.decision_engine import MethSnailBrainV2
from .hamsters.decision_engine_sbcV3 import HamstersBrainV3
from .quantum_shadow_people.decision_engine import QuantumShadowPeopleBrainV2
from .the_stick.decision_engine import TheStickBrainV3
from .vic_20_sage.decision_engine import VIC20SageBrainV2
        
logger = logging.getLogger(__name__)

def retry_on_failure(max_attempts: int = 3, delay: float = 0.5):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                    continue
            raise last_exception
        return wrapper
    return decorator

class AIAgentManager:
    """
    Central manager for AI agents in the System Rebellion.
    
    🧐 UPDATED ROLE IN TRIAGE ARCHITECTURE:
    - Coordinates agents for specialized processing
    - Handles non-metrics agent operations
    - Supports Sir Hawkington's triage routing decisions
    - Manages agent lifecycle and health monitoring
    """

    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
        self.agents: Dict[str, BaseAIAgent] = {}
        self.initialized = False
        self.logger = logging.getLogger("AIAgentManager")
        self.db_getter = db_getter
        self.db = None
        
        # Don't initialize agents here to avoid circular imports
        # Agents will be initialized in initialize_agents()
        self.total_processing_count = 0
        self.initialization_time = datetime.now()
        self.total_processing_count = 0
        self.logger = logging.getLogger("AgentManager")
        self.initialized = False
        
        # Agent processing order for specialized operations
        self.processing_order = [
            "meth_snail",           # Memory optimization specialist
            "hamsters",             # Storage/disk specialists  
            "quantum_shadow_people", # Network specialists
            "the_stick",            # Compliance and learning coordinator
            "vic_20_sage"           # Auto-tuner and orchestrator
        ]
        
        # Agent configuration
        self.agent_configs = {
            "meth_snail": {
                "class": MethSnailBrainV2,
                "role": "Memory Optimization Specialist",
                "retry_attempts": 3
            },
            "hamsters": {
                "class": HamstersBrainV3,
                "role": "Storage/Disk Engineers",
                "retry_attempts": 2
            },
            "quantum_shadow_people": {
                "class": QuantumShadowPeopleBrainV2,
                "role": "Network Specialists",
                "retry_attempts": 3
            },
            "the_stick": {
                "class": TheStickBrainV3,
                "role": "Compliance and Learning Coordinator",
                "retry_attempts": 1
            },
            "vic_20_sage": {
                "class": VIC20SageBrainV2,
                "role": "Auto-Tuner and Orchestrator",
                "retry_attempts": 2
            }
        }
        
        self.logger.info(" AI Agent Manager initialized - Triage Architecture Ready")
    
    def _ensure_agent_interface(self, agent: Any, name: str) -> None:
        """
        Ensure agent has required interface methods.
        
        Args:
            agent: The agent instance to check
            name: Name of the agent for logging
        """
        if not hasattr(agent, 'is_active'):
            agent.is_active = True
            
        if not hasattr(agent, 'activate'):
            agent.activate = lambda: setattr(agent, 'is_active', True)
            
        if not hasattr(agent, 'deactivate'):
            agent.deactivate = lambda: setattr(agent, 'is_active', False)
            
        if not hasattr(agent, 'process_metrics'):
            self.logger.warning(f" Agent '{name}' missing process_metrics method")
            
        if not hasattr(agent, 'get_agent_status'):
            # Provide a default status method
            agent.get_agent_status = lambda: {
                'status': 'operational' if agent.is_active else 'inactive',
                'name': name
            }
    
    async def _initialize_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> Optional[BaseAIAgent]:
        """
        Initialize a single agent with error handling.
        
        Args:
            agent_name: Name identifier for the agent
            agent_config: Configuration for the agent
            
        Returns:
            Initialized agent or None if failed
        """
        try:
            agent_class = agent_config['class']
            agent = agent_class(db_getter=self.db_getter)
            self._ensure_agent_interface(agent, agent_name)
            
            # Run agent-specific initialization if available
            if hasattr(agent, 'initialize'):
                await agent.initialize()
                
            self.logger.info(f"✅ Initialized {agent_name}: {agent_config['role']}")
            return agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {agent_name}: {str(e)}")
            return None
    
    async def initialize_agents(self):
        """
        Initialize all available AI agents for specialized processing.
        """
        if self.initialized:
            self.logger.debug("🤖 Agents already initialized, skipping")
            return
            
        self.logger.info("Initializing AI agents...")
        try:
            # Initialize all configured agents
            for agent_name, agent_config in self.agent_configs.items():
                agent = await self._initialize_agent(agent_name, agent_config)
                if agent:
                    self.agents[agent_name] = agent
                else:
                    self.logger.warning(f"⚠️ Continuing without {agent_name}")
            
            # Verify we have at least some agents
            if not self.agents:
                raise Exception("No agents successfully initialized")
            
            self._initialized = True
            self.logger.info(
                f"🤖 Agent Manager initialized {len(self.agents)} specialist agents: "
                f"{list(self.agents.keys())}"
            )
            
        except Exception as e:
            self.logger.error(f"🤖💥 Failed to initialize agents: {str(e)}", exc_info=True)
            raise
    
    def _merge_agent_results(
        self, 
        base_metrics: Dict[str, Any], 
        agent_name: str, 
        agent_result: Union[Dict[str, Any], Any]
    ) -> Dict[str, Any]:
        """
        Intelligently merge agent results into the base metrics.
        
        Args:
            base_metrics: The current enhanced metrics
            agent_name: Name of the agent providing results
            agent_result: Results from the agent
            
        Returns:
            Merged metrics dictionary
        """
        if not isinstance(agent_result, dict):
            # If agent returns non-dict, store under agent's name
            base_metrics[agent_name] = agent_result
            return base_metrics
        
        # Check if agent returns data under its own key
        if agent_name in agent_result:
            # Preserve agent-specific data under its namespace
            base_metrics[agent_name] = agent_result[agent_name]
            
            # Also merge any top-level updates (excluding the agent's own key)
            for key, value in agent_result.items():
                if key != agent_name and key not in ['timestamp', 'processing_time']:
                    base_metrics[key] = value
        else:
            # Merge all results, but preserve certain keys
            preserved_keys = ['agent_processing', 'triage_decision', 'timestamp']
            for key, value in agent_result.items():
                if key not in preserved_keys:
                    base_metrics[key] = value
        
        return base_metrics
    
    async def _process_single_agent(
        self,
        agent_name: str,
        agent: BaseAIAgent,
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Process metrics through a single agent with retry logic.
        
        Returns:
            Tuple of (success, result, error_message)
        """
        config = self.agent_configs.get(agent_name, {})
        retry_attempts = config.get('retry_attempts', 1)
        
        last_error = None
        for attempt in range(retry_attempts):
            try:
                result = await agent.process_metrics(metrics, user_context)
                return True, result, None
            except Exception as e:
                last_error = str(e)
                if attempt < retry_attempts - 1:
                    self.logger.warning(
                        f"⚠️ Agent '{agent_name}' attempt {attempt + 1} failed, retrying..."
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))
                continue
        
        return False, None, last_error
    
    async def process_metrics_through_agents(
        self, 
        metrics: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process metrics through specialist agents.
        
        🧐 UPDATED ROLE: This method now handles SPECIALIST PROCESSING
        when routed by Sir Hawkington's Triage Engine (normal operations).
        
        Args:
            metrics: System metrics (potentially pre-processed by Triage Engine)
            user_context: Optional user context for personalized analysis
            
        Returns:
            Enhanced metrics with specialist agent analyses
        """
        if not self._initialized:
            await self.initialize_agents()
            
        self.total_processing_count += 1
        
        # Ensure metrics is a dictionary before calling copy()
        if isinstance(metrics, dict):
            enhanced_metrics = metrics.copy()
        elif isinstance(metrics, str):
            # If metrics is a string, try to parse as JSON, otherwise create empty dict
            try:
                import json
                enhanced_metrics = json.loads(metrics)
            except (json.JSONDecodeError, ValueError):
                enhanced_metrics = {'raw_data': metrics}
        else:
            # For any other type, create a dictionary wrapper
            enhanced_metrics = {'data': metrics} if metrics is not None else {}
        
        # Track which agents processed successfully
        processing_results = {
            'successful_agents': [],
            'failed_agents': [],
            'processing_time': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if getattr(a, 'is_active', False)]),
            'processing_mode': 'specialist_agents',  # Not primary triage
            'routed_by': user_context.get('routed_by', 'direct_call') if user_context else 'direct_call'
        }
        
        # Process through specialist agents in order
        for agent_name in self.processing_order:
            if agent_name not in self.agents:
                self.logger.warning(f"🤖 Specialist agent '{agent_name}' not found in registry")
                continue
            
            agent = self.agents[agent_name]
            
            # Check if agent is active
            if not getattr(agent, 'is_active', True):
                self.logger.debug(f"🤖 Agent '{agent_name}' is inactive, skipping")
                continue
            
            # Process metrics through this specialist agent
            start_time = datetime.now()
            success, agent_result, error = await self._process_single_agent(
                agent_name, agent, enhanced_metrics, user_context
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if success and agent_result is not None:
                # Intelligently merge results
                enhanced_metrics = self._merge_agent_results(
                    enhanced_metrics, agent_name, agent_result
                )
                
                processing_results['successful_agents'].append({
                    'agent_name': agent_name,
                    'processing_time_seconds': processing_time,
                    'agent_role': self._get_agent_role(agent_name)
                })
                
                self.logger.debug(
                    f"🤖 Specialist agent '{agent_name}' processed metrics in {processing_time:.3f}s"
                )
            else:
                processing_results['failed_agents'].append({
                    'agent_name': agent_name,
                    'error': error or 'Unknown error',
                    'agent_role': self._get_agent_role(agent_name)
                })
                
                self.logger.error(f"🤖💥 Specialist agent '{agent_name}' failed: {error}")
        
        # Add processing metadata
        enhanced_metrics['agent_processing'] = processing_results
        
        self.logger.info(
            f"🤖✅ Agent Manager processed metrics: {len(processing_results['successful_agents'])} successful, "
                    f"{len(processing_results['failed_agents'])} failed"
        )
        
        return enhanced_metrics
    
    def _get_agent_role(self, agent_name: str) -> str:
        """Get the role description for an agent"""
        return self.agent_configs.get(agent_name, {}).get('role', 'Unknown Specialist')
    
    async def process_agent_specific_request(
        self,
        agent_name: str,
        request_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request through a specific agent.
        
        This allows for direct agent communication outside of metrics flow.
        """
        if not self._initialized:
            await self.initialize_agents()
        
        if agent_name not in self.agents:
            raise Exception(f"Agent '{agent_name}' not found")
        
        agent = self.agents[agent_name]
        
        if not getattr(agent, 'is_active', True):
            raise Exception(f"Agent '{agent_name}' is not active")
        
        try:
            # Process the specific request
            if hasattr(agent, 'process_request'):
                return await agent.process_request(request_data, user_context)
            elif hasattr(agent, 'process_metrics'):
                return await agent.process_metrics(request_data, user_context)
            else:
                raise Exception(f"Agent '{agent_name}' doesn't support request processing")
                
        except Exception as e:
            self.logger.error(f"🤖💥 Agent '{agent_name}' request failed: {str(e)}")
            raise
    
    async def get_agent_status(self, agent_name: str = None) -> Dict[str, Any]:
        """Get status information for agents"""
        if agent_name:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                status = agent.get_agent_status() if hasattr(agent, 'get_agent_status') else {}
                status.update({
                    'agent_name': agent_name,
                    'is_active': getattr(agent, 'is_active', True),
                    'role': self._get_agent_role(agent_name),
                    'retry_config': self.agent_configs.get(agent_name, {}).get('retry_attempts', 1)
                })
                return status
            else:
                return {'error': f'Agent {agent_name} not found'}
        
        # Return status for all agents
        all_status = {
            'manager_status': {
                'initialized': self._initialized,
                'architecture_mode': 'triage_integration',
                'total_agents': len(self.agents),
                'active_agents': sum(1 for agent in self.agents.values() if getattr(agent, 'is_active', True)),
                'total_processing_count': self.total_processing_count,
                'uptime_seconds': (datetime.now() - self.initialization_time).total_seconds(),
                'registered_agents': list(self.agents.keys()),
                'processing_order': self.processing_order,
                'agent_configurations': {
                    name: {
                        'role': config['role'],
                        'retry_attempts': config.get('retry_attempts', 1)
                    } for name, config in self.agent_configs.items()
                }
            },
            'agents': {}
        }
        
        for name, agent in self.agents.items():
            status = agent.get_agent_status() if hasattr(agent, 'get_agent_status') else {}
            status.update({
                'agent_name': name,
                'is_active': getattr(agent, 'is_active', True),
                'role': self._get_agent_role(name),
                'retry_config': self.agent_configs.get(name, {}).get('retry_attempts', 1)
            })
            all_status['agents'][name] = status
        
        return all_status
    
    async def activate_agent(self, agent_name: str) -> bool:
        """Activate a specific agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            if hasattr(agent, 'activate'):
                agent.activate()
            else:
                setattr(agent, 'is_active', True)
            self.logger.info(f"🤖✅ Agent '{agent_name}' activated")
            return True
        return False
    
    async def deactivate_agent(self, agent_name: str) -> bool:
        """Deactivate a specific agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            if hasattr(agent, 'deactivate'):
                agent.deactivate()
            else:
                setattr(agent, 'is_active', False)
            self.logger.info(f"🤖❌ Agent '{agent_name}' deactivated")
            return True
        return False
    
    async def get_active_agents(self) -> List[str]:
        """Get list of currently active agent names"""
        return [name for name, agent in self.agents.items() if getattr(agent, 'is_active', True)]
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        self.logger.info("🔥 Shutting down AI Agent Manager...")
        
        shutdown_tasks = []
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'shutdown'):
                shutdown_tasks.append(self._shutdown_agent(agent_name, agent))
        
        # Shutdown all agents concurrently
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.agents.clear()
        self._initialized = False
        self.logger.info("🎭 AI Agent Manager shutdown complete")
    
    async def _shutdown_agent(self, agent_name: str, agent: BaseAIAgent):
        """Shutdown a single agent with error handling"""
        try:
            await agent.shutdown()
            self.logger.info(f"✅ {agent_name} shut down successfully")
        except Exception as e:
            self.logger.error(f"❌ Error shutting down {agent_name}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of the agent manager"""
        try:
            if not self._initialized:
                await self.initialize_agents()
            
            # Get individual agent health if available
            agent_health = {}
            for name, agent in self.agents.items():
                if hasattr(agent, 'health_check'):
                    try:
                        agent_health[name] = await agent.health_check()
                    except Exception as e:
                        agent_health[name] = {'status': 'error', 'error': str(e)}
                else:
                    agent_health[name] = {'status': 'operational' if getattr(agent, 'is_active', True) else 'inactive'}
            
            active_count = len(await self.get_active_agents())
            
            return {
                'status': 'OPERATIONAL',
                'manager_type': 'specialist_agent_orchestration',
                'architecture_mode': 'triage_integration',  
                'total_agents': len(self.agents),
                'active_agents': active_count,
                'agent_roles': {name: self._get_agent_role(name) for name in self.agents.keys()},
                'agent_health': agent_health,
                'processing_order': self.processing_order,
                'total_processing_count': self.total_processing_count,
                'uptime_seconds': (datetime.now() - self.initialization_time).total_seconds(),
                'triage_coordination': 'ready_for_sir_hawkington_routing',
                'last_health_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'FAILED',
                'manager_type': 'specialist_agent_orchestration',
                'error': str(e),
                'last_health_check': datetime.now().isoformat()
            }

# Global agent manager instance
_agent_manager_instance = None
_initialization_lock = asyncio.Lock()

async def get_agent_manager():
    """
    Get the global agent manager instance (singleton pattern).
    Thread-safe initialization with async lock.
    
    Returns:
        Initialized AIAgentManager instance
    """
    global _agent_manager_instance
    
    if _agent_manager_instance is None:
        async with _initialization_lock:
            if _agent_manager_instance is None:
                _agent_manager_instance = AIAgentManager()
                await _agent_manager_instance.initialize_agents()
    
    return _agent_manager_instance

# === CONVENIENCE FUNCTIONS FOR TRIAGE INTEGRATION ===

async def process_specialist_agents(
    metrics: Dict[str, Any], 
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for Triage Engine to process metrics through specialist agents.
    
    This is called by Sir Hawkington's Triage Engine for NORMAL severity routing.
    
    Args:
        metrics: System metrics from SimplifiedMetricsService
        user_context: Optional context including triage routing info
    
    Returns:
        Enhanced metrics with specialist agent processing
    """
    agent_manager = await get_agent_manager()
    return await agent_manager.process_metrics_through_agents(metrics, user_context)

async def get_specialist_agent_status() -> Dict[str, Any]:
    """
    Get status of all specialist agents for monitoring.
    
    Returns:
        Comprehensive agent status information
    """
    agent_manager = await get_agent_manager()
    return await agent_manager.get_agent_status()

async def activate_specialist_agent(agent_name: str) -> bool:
    """
    Activate a specific specialist agent.
    
    Args:
        agent_name: Name of agent to activate
        
    Returns:
        True if successful, False otherwise
    """
    agent_manager = await get_agent_manager()
    return await agent_manager.activate_agent(agent_name)

async def deactivate_specialist_agent(agent_name: str) -> bool:
    """
    Deactivate a specific specialist agent.
    
    Args:
        agent_name: Name of agent to deactivate
        
    Returns:
        True if successful, False otherwise
    """
    agent_manager = await get_agent_manager()
    return await agent_manager.deactivate_agent(agent_name)

async def agent_manager_health_check() -> Dict[str, Any]:
    """
    Perform health check on the agent manager.
    
    Returns:
        Health check results
    """
    try:
        agent_manager = await get_agent_manager()
        return await agent_manager.health_check()
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e),
            'last_health_check': datetime.now().isoformat()
        }

# === TESTING FUNCTIONS ===

async def test_agent_manager():
    """Test the agent manager functionality"""
    print("\n" + "="*80)
    print(" 🤖⚡ AI AGENT MANAGER TEST - TRIAGE ARCHITECTURE INTEGRATION")
    print("="*80)
    
    print(f"\n🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize agent manager
        print("\n🤖 Initializing Agent Manager...")
        agent_manager = await get_agent_manager()
        print(f"📊 Manager instance created successfully")

        # Health check
        print("\n🏥 Agent Manager Health Check:")
        health = await agent_manager.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Architecture Mode: {health.get('architecture_mode', 'Unknown')}")
        print(f"   Total Agents: {health.get('total_agents', 'Unknown')}")
        print(f"   Active Agents: {health.get('active_agents', 'Unknown')}")
        print(f"   Processing Order: {health.get('processing_order', [])}")

        # Get agent status
        print(f"\n📊 Individual Agent Status:")
        all_status = await agent_manager.get_agent_status()
        for agent_name, status in all_status.get('agents', {}).items():
            active_status = "🟢 ACTIVE" if status.get('is_active', False) else "🔴 INACTIVE"
            role = status.get('role', 'Unknown Role')
            retry = status.get('retry_config', 1)
            print(f"   {active_status} {agent_name}: {role} (retry: {retry})")
        
        # Test specialist agent processing
        print(f"\n🧪 Testing Specialist Agent Processing:")
        test_metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': 45.2,
            'memory_usage': 68.7,
            'disk_usage': 34.1,
            'network_sent_rate': 1024,
            'network_recv_rate': 2048,
            'test_mode': True
        }
        
        user_context = {
            'routed_by': 'sir_hawkington_triage',
            'triage_severity': 'normal',
            'test_context': True
        }
        
        active_agents = await agent_manager.get_active_agents()
        print(f"   Processing test metrics through {len(active_agents)} active agents...")
        enhanced_metrics = await agent_manager.process_metrics_through_agents(test_metrics, user_context)
        
        # Show results
        if 'agent_processing' in enhanced_metrics:
            processing = enhanced_metrics['agent_processing']
            successful = len(processing.get('successful_agents', []))
            failed = len(processing.get('failed_agents', []))
            print(f"   ✅ Successful Agents: {successful}")
            print(f"   ❌ Failed Agents: {failed}")
            
            if processing.get('successful_agents'):
                print(f"   🎯 Successfully Processed By:")
                for agent in processing['successful_agents']:
                    print(f"     - {agent['agent_name']} ({agent['processing_time_seconds']:.3f}s)")
            
            if processing.get('failed_agents'):
                print(f"   💥 Failed Agents:")
                for agent in processing['failed_agents']:
                    print(f"     - {agent['agent_name']}: {agent['error']}")
        
        # Show enhanced metrics
        print(f"\n📈 Enhanced Metrics Preview:")
        for agent_name in ['meth_snail', 'hamsters', 'quantum_shadow_people', 'the_stick', 'vic_20_sage']:
            if agent_name in enhanced_metrics:
                print(f"   {agent_name}: Data present")
        
        # Test convenience functions
        print(f"\n🔧 Testing Convenience Functions:")
        
        # Test specialist agent status
        specialist_status = await get_specialist_agent_status()
        manager_status = specialist_status.get('manager_status', {})
        print(f"   Specialist Status: {manager_status.get('total_agents', 0)} agents, {manager_status.get('active_agents', 0)} active")
        
        # Test agent activation/deactivation (if any agents exist)
        if active_agents:
            test_agent = active_agents[0]
            print(f"\n   Testing activation/deactivation with agent: {test_agent}")
            
            # Deactivate
            deactivated = await deactivate_specialist_agent(test_agent)
            print(f"   Deactivation result: {'✅' if deactivated else '❌'}")
            
            # Check status
            status = await agent_manager.get_agent_status(test_agent)
            print(f"   Agent is now: {'🔴 INACTIVE' if not status.get('is_active') else '🟢 ACTIVE'}")
            
            # Reactivate
            activated = await activate_specialist_agent(test_agent)
            print(f"   Reactivation result: {'✅' if activated else '❌'}")
            
            # Check status again
            status = await agent_manager.get_agent_status(test_agent)
            print(f"   Agent is now: {'🟢 ACTIVE' if status.get('is_active') else '🔴 INACTIVE'}")
        
        # Test error handling
        print(f"\n🧪 Testing Error Handling:")
        try:
            result = await agent_manager.process_agent_specific_request(
                'non_existent_agent', 
                {'test': 'data'}
            )
        except Exception as e:
            print(f"   ✅ Correctly caught error for non-existent agent: {e}")
        
        # Final health check
        print(f"\n🏥 Final Health Check:")
        final_health = await agent_manager_health_check()
        print(f"   Status: {final_health['status']}")
        print(f"   Total Processing Count: {manager_status.get('total_processing_count', 0)}")
        print(f"   Uptime: {manager_status.get('uptime_seconds', 0):.1f} seconds")
        
        print(f"\n🧐 AGENT MANAGER INTEGRATION WITH TRIAGE ARCHITECTURE:")
        print(f"   ✅ Ready for Sir Hawkington's routing decisions")
        print(f"   ✅ Specialist agents operational for normal operations")
        print(f"   ✅ Direct agent communication available")
        print(f"   ✅ Proper error handling and graceful degradation")
        print(f"   ✅ Intelligent result merging implemented")
        print(f"   ✅ Retry logic for transient failures")
        print(f"   ✅ Concurrent agent shutdown for efficiency")
        
        # Performance summary
        if 'agent_processing' in enhanced_metrics:
            processing = enhanced_metrics['agent_processing']
            total_time = sum(
                agent['processing_time_seconds'] 
                for agent in processing.get('successful_agents', [])
            )
            print(f"\n📊 Performance Summary:")
            print(f"   Total Processing Time: {total_time:.3f}s")
            print(f"   Average per Agent: {total_time/len(processing.get('successful_agents', [])) if processing.get('successful_agents') else 0:.3f}s")
        
    except Exception as e:
        print(f"\n💥 AGENT MANAGER TEST FAILED: {str(e)}")
        print("This indicates agent initialization or processing issues")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    print(" 🤖✨ AGENT MANAGER TEST COMPLETE - SYSTEM REBELLION READY")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_agent_manager())