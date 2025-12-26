#!/usr/bin/env python3
"""
Hamsters' Action Executor - Steve, Bob, and Carl Actually Doing The Thing

Routes selected actions to their actual implementations in SystemActions.
No more hardcoded defrag - the Hamsters can now execute ANY action they select.

🐹🐹🐹 "We can do MORE than just defrag! *cracks beer* Watch this!"
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger('HamstersActionExecutor')


class HamstersActionExecutor:
    """
    Execute actions selected by the Hamsters' ML brain.
    
    Routes action names to their actual SystemActions implementations.
    """
    
    def __init__(self):
        """Initialize action executor"""
        self.logger = logger
        self.logger.info("🐹⚙️ Hamsters' action executor initialized - ready to execute!")
    
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the selected action with given parameters.
        
        Args:
            action: Action name (e.g., 'cleanup', 'defrag', 'rotate_logs')
            parameters: Action-specific parameters
            
        Returns:
            Execution result with success status and metrics
        """
        self.logger.info(f"🐹⚡ Executing action: {action}")
        
        # Import SystemActions here to avoid circular imports
        from app.ai_agents.distributed.system_actions import SystemActions, RecommendationEngine
        
        try:
            # Route to correct SystemActions method
            if action == 'cleanup':
                # Basic cleanup WITHOUT defrag (faster, less invasive)
                result = await SystemActions.emergency_disk_cleanup(
                    include_defrag=False
                )
            
            elif action == 'cleanup_with_defrag':
                # Full cleanup WITH defrag (slower, more thorough)
                result = await SystemActions.emergency_disk_cleanup(
                    include_defrag=True
                )
            
            elif action == 'rotate_logs':
                result = await RecommendationEngine.rotate_logs(
                    log_directory=parameters.get('log_directory', '/var/log'),
                    max_age_days=parameters.get('max_age_days', 7),
                    agent_name='hamsters'
                )
            
            elif action == 'defrag_only':
                # Just defrag, no cleanup
                # Note: This is actually cleanup with defrag, but we could add a defrag-only option
                result = await SystemActions.emergency_disk_cleanup(
                    include_defrag=True
                )
            
            else:
                # Unknown action - fall back to basic cleanup
                self.logger.warning(f"🐹⚠️ Unknown action {action} - falling back to basic cleanup")
                result = await SystemActions.emergency_disk_cleanup(
                    include_defrag=False
                )
            
            # Add execution metadata
            result['executed_action'] = action
            result['executed_at'] = datetime.now(timezone.utc).isoformat()
            
            if result.get('success'):
                self.logger.info(f"🐹✅ Action {action} executed successfully!")
            else:
                self.logger.warning(f"🐹⚠️ Action {action} failed: {result.get('error', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"🐹💥 Action execution failed: {e}", exc_info=True)
            return {
                'action': action,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_available_actions(self) -> list:
        """
        Get list of actions Hamsters can execute.
        
        Hamsters specialize in Disk/Storage management.
        
        Returns:
            List of action names Hamsters can execute
        """
        return [
            'cleanup',              # Basic cleanup (no defrag)
            'cleanup_with_defrag',  # Full cleanup + defrag
            'rotate_logs',          # Log rotation
            'defrag_only'           # Just defrag (when fragmentation is high)
        ]
