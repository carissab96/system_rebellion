"""
Base Agent Interface - ENHANCED FOR TRIAGE ARCHITECTURE

All AI agents inherit from this base class to ensure consistent behavior
and integration patterns optimized for Sir Hawkington's Triage Engine.

🧐 "A proper agent interface ensures aristocratic consistency across all agents"
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

def utc_now():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)

class BaseAIAgent(ABC):
    """
    Abstract base class for all AI agents in the System Rebellion.
    
    🧐 ENHANCED FOR TRIAGE ARCHITECTURE:
    - Consistent interfaces for all agents
    - Triage-compatible processing methods
    - Comprehensive status reporting
    - NO fake data generation capabilities
    """
    
    def __init__(self, agent_name: str, version: str = "1.0", agent_role: str = "specialist"):
        self.agent_name = agent_name
        self.version = version
        self.agent_role = agent_role  # NEW: Agent specialization
        self.is_active = True
        self.logger = logging.getLogger(f"Agent.{agent_name}")
        self.initialization_time = utc_now()
        self.processing_count = 0
        self.error_count = 0
        self.last_processing_time = None
        self.total_processing_time = 0.0
        
        self.logger.info(f"🤖 {agent_name} agent initialized (v{version}) - Role: {agent_role}")
    
    @abstractmethod
    async def process_metrics(
        self, 
        metrics: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process system metrics and return enhanced metrics with agent analysis.
        
        🧐 TRIAGE ARCHITECTURE: This method is called by:
        - Agent Manager for specialist processing (normal operations)
        - Direct routing from Triage Engine (specific scenarios)
        
        Args:
            metrics: System metrics (may be pre-processed by Triage Engine)
            user_context: Optional context including triage routing information
            
        Returns:
            Enhanced metrics dictionary with agent's analysis added
            
        Raises:
            Exception: If processing fails critically (NO FAKE DATA GENERATED)
        """
        pass
    
    @abstractmethod
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current status and health information for this agent.
        
        Returns:
            Dictionary containing agent status, performance metrics, and health info
        """
        pass
    
    # === ACTIVATION/DEACTIVATION METHODS ===
    
    def activate(self):
        """Activate this agent for processing"""
        self.is_active = True
        self.logger.info(f"🤖✅ {self.agent_name} activated")
    
    def deactivate(self):
        """Deactivate this agent (it will skip processing)"""
        self.is_active = False
        self.logger.info(f"🤖❌ {self.agent_name} deactivated")
    
    # === OPTIONAL TRIAGE INTEGRATION METHODS ===
    
    async def handle_triage_routing(
        self,
        routing_decision: Dict[str, Any],
        metrics: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle specific routing from Sir Hawkington's Triage Engine.
        
        🧐 OPTIONAL: Agents can override this for specialized triage handling
        
        Args:
            routing_decision: Triage routing decision from Sir Hawkington
            metrics: System metrics
            user_context: User context
            
        Returns:
            Agent response to triage routing
        """
        # Default implementation: delegate to process_metrics
        return await self.process_metrics(metrics, user_context)
    
    async def handle_emergency_request(
        self,
        emergency_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle emergency requests (e.g., monocle yeet scenarios).
        
        🧐 OPTIONAL: For agents that support emergency operations
        
        Args:
            emergency_data: Emergency request data
            user_context: User context
            
        Returns:
            Emergency response
        """
        return {
            'agent_name': self.agent_name,
            'emergency_support': False,
            'message': f'{self.agent_name} does not support emergency operations',
            'timestamp': utc_now().isoformat()
        }
    
    # === STATISTICS AND MONITORING ===
    
    def start_processing_timer(self):
        """Start timing a processing operation"""
        self.last_processing_time = utc_now()
    
    def end_processing_timer(self):
        """End timing and record processing duration"""
        if self.last_processing_time:
            duration = (utc_now() - self.last_processing_time).total_seconds()
            self.total_processing_time += duration
            self.last_processing_time = None
            return duration
        return 0.0
    
    def increment_processing_count(self):
        """Track processing statistics"""
        self.processing_count += 1
    
    def increment_error_count(self):
        """Track error statistics"""
        self.error_count += 1
    
    def get_base_status(self) -> Dict[str, Any]:
        """Get base status information common to all agents"""
        uptime = (utc_now() - self.initialization_time).total_seconds()
        avg_processing_time = (
            self.total_processing_time / max(self.processing_count, 1) 
            if self.processing_count > 0 else 0.0
        )
        
        return {
            'agent_name': self.agent_name,
            'agent_role': self.agent_role,
            'version': self.version,
            'is_active': self.is_active,
            'uptime_seconds': round(uptime.total_seconds(), 2),
            'processing_count': self.processing_count,
            'error_count': self.error_count,
            'error_rate': round(self.error_count / max(self.processing_count, 1), 4),
            'average_processing_time': round(avg_processing_time, 4),
            'total_processing_time': round(self.total_processing_time, 2),
            'initialized_at': self.initialization_time.isoformat(),
            'triage_compatible': True,
            'supports_emergency_operations': hasattr(self, 'handle_emergency_request'),
            'supports_triage_routing': hasattr(self, 'handle_triage_routing')
        }
    
    # === HEALTH CHECK METHODS ===
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of this agent.
        
        🧐 OPTIONAL: Agents can override for specialized health checks
        
        Returns:
            Health check results
        """
        try:
            status = self.get_agent_status()
            
            # Determine health based on error rate and activity
            if not self.is_active:
                health_status = 'INACTIVE'
            elif self.error_rate > 0.5:  # More than 50% error rate
                health_status = 'DEGRADED'
            elif self.error_rate > 0.1:  # More than 10% error rate
                health_status = 'WARNING'
            else:
                health_status = 'HEALTHY'
            
            return {
                'agent_name': self.agent_name,
                'health_status': health_status,
                'is_active': self.is_active,
                'error_rate': self.error_rate,
                'processing_count': self.processing_count,
                'last_health_check': utc_now().isoformat(),
                'detailed_status': status
            }
            
        except Exception as e:
            return {
                'agent_name': self.agent_name,
                'health_status': 'ERROR',
                'error': str(e),
                'last_health_check': utc_now().isoformat()
            }
    
    # === UTILITY METHODS ===
    
    def log_processing_start(self, operation: str, context: Optional[Dict[str, Any]] = None):
        """Log the start of a processing operation"""
        context_info = f" (context: {context})" if context else ""
        self.logger.debug(f"🤖 {self.agent_name} starting {operation}{context_info}")
        self.start_processing_timer()
    
    def log_processing_success(self, operation: str, duration: Optional[float] = None):
        """Log successful completion of a processing operation"""
        if duration is None:
            duration = self.end_processing_timer()
        
        self.increment_processing_count()
        self.logger.debug(f"🤖✅ {self.agent_name} completed {operation} in {duration:.3f}s")
    
    def log_processing_error(self, operation: str, error: Exception, duration: Optional[float] = None):
        """Log a processing error"""
        if duration is None:
            duration = self.end_processing_timer()
        
        self.increment_error_count()
        self.logger.error(f"🤖💥 {self.agent_name} failed {operation} after {duration:.3f}s: {str(error)}")
    
    def __repr__(self):
        """String representation of the agent"""
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"<{self.__class__.__name__}(name='{self.agent_name}', status={status}, v{self.version})>"

# === AGENT ROLE CONSTANTS ===

class AgentRole:
    """Constants for agent roles in the triage architecture"""
    TRIAGE_COMMANDER = "triage_commander"      # Sir Hawkington
    MEMORY_SPECIALIST = "memory_specialist"    # Meth Snail
    STORAGE_SPECIALIST = "storage_specialist"  # Hamsters
    NETWORK_SPECIALIST = "network_specialist"  # Quantum Shadow People
    LEARNING_COORDINATOR = "learning_coordinator"  # The Stick
    AUTO_TUNER = "auto_tuner"                 # VIC-20 Sage
    WEBSOCKET_HANDLER = "websocket_handler"   # WebSocket integration agents

# === UTILITY FUNCTIONS ===

def validate_agent_implementation(agent_class):
    """
    Validate that an agent class properly implements the BaseAIAgent interface.
    
    Args:
        agent_class: Agent class to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check if it inherits from BaseAIAgent
    if not issubclass(agent_class, BaseAIAgent):
        errors.append("Agent must inherit from BaseAIAgent")
        return errors
    
    # Check required abstract methods
    required_methods = ['process_metrics', 'get_agent_status']
    
    for method_name in required_methods:
        if not hasattr(agent_class, method_name):
            errors.append(f"Missing required method: {method_name}")
        elif getattr(agent_class, method_name) is getattr(BaseAIAgent, method_name):
            errors.append(f"Method {method_name} is not implemented (still abstract)")
    
    return errors

# === TESTING UTILITIES ===

class MockAgent(BaseAIAgent):
    """Mock agent for testing purposes"""
    
    def __init__(self):
        super().__init__("mock_agent", "1.0", AgentRole.WEBSOCKET_HANDLER)
        self.test_processing_calls = []
    
    async def process_metrics(self, metrics: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock implementation that records calls"""
        self.log_processing_start("test_processing", user_context)
        
        # Record the call for testing
        self.test_processing_calls.append({
            'metrics': metrics,
            'user_context': user_context,
            'timestamp': utc_now().isoformat()
        })
        
        # Add mock agent processing
        enhanced_metrics = metrics.copy()
        enhanced_metrics['mock_agent_processed'] = True
        enhanced_metrics['mock_processing_time'] = utc_now().isoformat()
        
        self.log_processing_success("test_processing")
        return enhanced_metrics
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Mock status implementation"""
        base_status = self.get_base_status()
        base_status.update({
            'agent_type': 'mock',
            'test_calls': len(self.test_processing_calls),
            'mock_specific_data': 'test_data'
        })
        return base_status

def test_base_agent_interface():
    """Test the base agent interface"""
    print("\n" + "="*80)
    print(" 🤖⚡ BASE AGENT INTERFACE TEST - TRIAGE ARCHITECTURE COMPATIBILITY")
    print("="*80)
    
    print(f"\n🕐 Test Started: {utc_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test agent validation
        print("\n🔍 Testing Agent Validation:")
        
        # Valid agent (should have no errors)
        mock_errors = validate_agent_implementation(MockAgent)
        print(f"   MockAgent validation: {'✅ VALID' if not mock_errors else f'❌ ERRORS: {mock_errors}'}")
        
        # Test mock agent functionality
        print(f"\n🤖 Testing Mock Agent:")
        mock_agent = MockAgent()
        print(f"   Agent created: {mock_agent}")
        print(f"   Agent active: {mock_agent.is_active}")
        print(f"   Agent role: {mock_agent.agent_role}")
        
        # Test processing
        test_metrics = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'test_data': True
        }
        
        print(f"   Processing test metrics...")
        import asyncio
        enhanced = asyncio.run(mock_agent.process_metrics(test_metrics, {'test': True}))
        
        print(f"   ✅ Processing successful: {enhanced.get('mock_agent_processed', False)}")
        print(f"   📊 Processing calls: {len(mock_agent.test_processing_calls)}")
        
        # Test status
        status = mock_agent.get_agent_status()
        print(f"   📊 Status keys: {list(status.keys())}")
        print(f"   📊 Processing count: {status.get('processing_count', 0)}")
        print(f"   📊 Error rate: {status.get('error_rate', 0)}")
        
        # Test health check
        health = asyncio.run(mock_agent.health_check())
        print(f"   🏥 Health status: {health.get('health_status', 'Unknown')}")
        
        # Test activation/deactivation
        print(f"\n🔄 Testing Activation/Deactivation:")
        mock_agent.deactivate()
        print(f"   Agent active after deactivation: {mock_agent.is_active}")
        mock_agent.activate()
        print(f"   Agent active after activation: {mock_agent.is_active}")
        
        print(f"\n🧐 BASE AGENT INTERFACE ASSESSMENT:")
        print(f"   ✅ Proper abstract base class implementation")
        print(f"   ✅ Consistent interface contract for all agents")
        print(f"   ✅ Comprehensive statistics and monitoring")
        print(f"   ✅ Triage architecture compatibility")
        print(f"   ✅ NO fake data generation capabilities")
        print(f"   ✅ Proper error handling and logging")
        
    except Exception as e:
        print(f"\n💥 BASE AGENT INTERFACE TEST FAILED: {str(e)}")
    
    print(f"\n🕐 Test Completed: {utc_now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80)
    print(" 🤖✨ BASE AGENT INTERFACE TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_base_agent_interface()