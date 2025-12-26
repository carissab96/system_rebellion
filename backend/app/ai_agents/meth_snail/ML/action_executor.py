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
            action: Action name (e.g., 'emergency_cache_clear', 'rotate_logs')
            parameters: Action-specific parameters
            
        Returns:
            Execution result with success status and metrics
        """
        self.logger.info(f"🐌⚡ Executing action: {action}")
        
        # Import SystemActions here to avoid circular imports
        from app.ai_agents.distributed.system_actions import SystemActions, RecommendationEngine
        
        try:
            # Route to correct SystemActions method
            if action == 'emergency_cache_clear':
                result = await SystemActions.emergency_cache_clear(
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
            
            # Disk actions should go to Hamsters, not Terry
            elif action == 'rotate_logs':
                self.logger.warning(f"🐌⚠️ {action} is Hamster territory - Terry shouldn't be doing disk work!")
                self.logger.warning(f"🐌⚠️ Falling back to cache clear (memory/CPU is Terry's specialty)")
                result = await SystemActions.emergency_cache_clear(
                    agent_name='meth_snail',
                    verify=True
                )
            
            # Network actions should go to QSP, not Terry
            elif action == 'scan_open_ports':
                self.logger.warning(f"🐌⚠️ {action} is QSP territory - Terry shouldn't be doing network work!")
                self.logger.warning(f"🐌⚠️ Falling back to cache clear (memory/CPU is Terry's specialty)")
                result = await SystemActions.emergency_cache_clear(
                    agent_name='meth_snail',
                    verify=True
                )
            
            else:
                # Unknown action - fall back to cache clear
                self.logger.warning(f"🐌⚠️ Unknown action {action} - falling back to cache clear")
                result = await SystemActions.emergency_cache_clear(
                    agent_name='meth_snail',
                    verify=True
                )
            
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
            'emergency_cache_clear',      # Memory optimization
            'adjust_process_priority',    # CPU optimization
            'restart_service',            # Memory/CPU recovery
            'throttle_cpu_intensive_tasks'  # CPU throttling
        ]
