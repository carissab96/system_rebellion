#!/usr/bin/env python3
"""
Terry's Action Executor - Actually Doing The Thing

Routes selected actions to their actual implementations in SystemActions.
No more hardcoded cache clears - Terry can now execute ANY action he selects.

🐌💨 "I can do MORE than just cache clears! Watch this!"
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger('TerryActionExecutor')


class TerryActionExecutor:
    """
    Execute actions selected by Terry's ML brain.
    
    Routes action names to their actual SystemActions implementations.
    """
    
    def __init__(self):
        """Initialize action executor"""
        self.logger = logger
        self.logger.info("🐌⚙️ Terry's action executor initialized - ready to execute!")
    
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the selected action with given parameters.
        
        Args:
            action: Action name (e.g., 'emergency_cache_clear', 'optimize_memory_allocation')
            parameters: Action-specific parameters
            
        Returns:
            Execution result with success status and metrics
        """
        self.logger.info(f"🐌⚡ Executing action: {action}")
        
        # Import SystemActions here to avoid circular imports
        from app.ai_agents.distributed.system_actions import SystemActions, RecommendationEngine
        
        try:
            # === RAM/CPU ACTIONS (Terry's specialty) ===
            
            if action == 'emergency_cache_clear':
                result = await SystemActions.emergency_cache_clear(
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'clear_cache':
                # Non-emergency cache clear (gentler approach)
                result = await SystemActions.clear_cache(
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'adjust_process_priority':
                result = await RecommendationEngine.adjust_process_priority(
                    process_name=parameters.get('process_name'),
                    pid=parameters.get('pid'),
                    nice_value=parameters.get('nice_value', 10),
                    agent_name='meth_snail'
                )
            
            elif action == 'restart_service':
                result = await RecommendationEngine.restart_service(
                    service_name=parameters.get('service_name', 'redis'),
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'throttle_cpu_intensive_tasks':
                result = await SystemActions.throttle_cpu_intensive_tasks(
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'kill_memory_hog':
                # Kill the top memory-consuming process
                result = await SystemActions.kill_process(
                    process_name=parameters.get('process_name'),
                    pid=parameters.get('pid'),
                    signal='SIGTERM',  # Graceful shutdown first
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'optimize_memory_allocation':
                # Trigger Python garbage collection and memory optimization
                result = await SystemActions.optimize_memory(
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'reduce_memory_footprint':
                # Reduce memory usage by clearing caches and optimizing
                result = await SystemActions.reduce_memory_footprint(
                    agent_name='meth_snail',
                    verify=True
                )
            
            elif action == 'monitor':
                # Do nothing, just observe (useful for learning)
                self.logger.info("🐌👁️ Monitoring situation without intervention")
                result = {
                    'action': 'monitor',
                    'success': True,
                    'message': 'Monitoring without intervention',
                    'intervention': False
                }
            
            elif action == 'escalate':
                # Escalate to VIC-20 for coordination
                self.logger.info("🐌📢 Escalating to VIC-20 - Terry needs help!")
                result = {
                    'action': 'escalate',
                    'success': True,
                    'message': 'Escalated to VIC-20 for coordination',
                    'escalated': True
                }
            
            else:
                # Unknown action - FAIL instead of fallback
                # Terry needs to learn what works, not have a safety net
                self.logger.error(f"🐌❌ Unknown action: {action} - NO FALLBACK, Terry must learn!")
                result = {
                    'action': action,
                    'success': False,
                    'error': f'Unknown action: {action}. Terry does not know how to execute this.',
                    'learning_opportunity': True
                }
            
            # Add execution metadata
            result['executed_action'] = action
            result['executed_at'] = datetime.now(timezone.utc).isoformat()
            
            if result.get('success'):
                self.logger.info(f"🐌✅ Action {action} executed successfully!")
            else:
                self.logger.warning(f"🐌⚠️ Action {action} failed: {result.get('error', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"🐌💥 Action execution failed: {e}", exc_info=True)
            return {
                'action': action,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_available_actions(self) -> list:
        """
        Get list of actions Terry can execute.
        
        Terry specializes in CPU and Memory optimization.
        Disk actions → Hamsters
        Network actions → QSP
        
        Returns:
            List of action names Terry can execute
        """
        return [
            # Memory actions
            'emergency_cache_clear',       # Aggressive memory clear
            'clear_cache',                 # Gentle cache clear
            'kill_memory_hog',             # Kill memory-consuming process
            'optimize_memory_allocation',  # Python GC + optimization
            'reduce_memory_footprint',     # Comprehensive memory reduction
            
            # CPU actions
            'adjust_process_priority',     # Nice CPU hogs
            'throttle_cpu_intensive_tasks', # Throttle CPU usage
            
            # Recovery actions
            'restart_service',             # Service restart
            
            # Learning actions
            'monitor',                     # Observe without intervention
            'escalate',                    # Ask for help
        ]
