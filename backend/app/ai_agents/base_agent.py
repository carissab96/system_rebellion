"""
Base Agent Interface

All AI agents inherit from this base class to ensure consistent behavior
and integration patterns. This is the contract that all agents must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

class BaseAIAgent(ABC):
    """
    Abstract base class for all AI agents in the System Rebellion.
    
    This ensures all agents have consistent interfaces and behavior patterns.
    """
    
    def __init__(self, agent_name: str, version: str = "1.0"):
        self.agent_name = agent_name
        self.version = version
        self.is_active = True
        self.logger = logging.getLogger(f"Agent.{agent_name}")
        self.initialization_time = datetime.now()
        self.processing_count = 0
        self.error_count = 0
        
        self.logger.info(f"🤖 {agent_name} agent initialized (v{version})")
    
    @abstractmethod
    async def process_metrics(self, metrics: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process system metrics and return enhanced metrics with agent analysis.
        
        Args:
            metrics: Raw system metrics from the monitoring system
            user_context: Optional user context for personalized analysis
            
        Returns:
            Enhanced metrics dictionary with agent's analysis added
            
        Raises:
            Exception: If processing fails critically
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
    
    def activate(self):
        """Activate this agent for processing"""
        self.is_active = True
        self.logger.info(f"🤖 {self.agent_name} activated")
    
    def deactivate(self):
        """Deactivate this agent (it will passthrough without processing)"""
        self.is_active = False
        self.logger.info(f"🤖 {self.agent_name} deactivated")
    
    def increment_processing_count(self):
        """Track processing statistics"""
        self.processing_count += 1
    
    def increment_error_count(self):
        """Track error statistics"""
        self.error_count += 1
    
    def get_base_status(self) -> Dict[str, Any]:
        """Get base status information common to all agents"""
        uptime = datetime.now() - self.initialization_time
        
        return {
            'agent_name': self.agent_name,
            'version': self.version,
            'is_active': self.is_active,
            'uptime_seconds': uptime.total_seconds(),
            'processing_count': self.processing_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.processing_count, 1),
            'initialized_at': self.initialization_time.isoformat()
        }