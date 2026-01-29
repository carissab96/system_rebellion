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
            action: Action name (e.g., 'cleanup', 'fstrim', 'rotate_logs')
            parameters: Action-specific parameters
            
        Returns:
            Execution result with success status and metrics
        """
        self.logger.info(f"🐹⚡ Executing action: {action}")
        
        # Import SystemActions here to avoid circular imports
        from app.ai_agents.distributed.system_actions import SystemActions, RecommendationEngine
        
        try:
            # === DISK/STORAGE ACTIONS (Hamsters' specialty) ===
            
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
            
            elif action == 'fstrim':
                # TRIM unused blocks (SSD optimization)
                result = await SystemActions.fstrim_disks(
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'defrag_only':
                # Just defrag, no cleanup
                result = await SystemActions.defrag_filesystem(
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'rotate_logs':
                result = await RecommendationEngine.rotate_logs(
                    log_directory=parameters.get('log_directory', '/var/log'),
                    max_age_days=parameters.get('max_age_days', 7),
                    agent_name='hamsters'
                )
            
            elif action == 'compress_logs':
                # Compress old logs to save space
                result = await SystemActions.compress_old_logs(
                    log_directory=parameters.get('log_directory', '/var/log'),
                    age_days=parameters.get('age_days', 7),
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'archive_old_files':
                # Archive old files to free up space
                result = await SystemActions.archive_old_files(
                    directory=parameters.get('directory', '/var/log'),
                    age_days=parameters.get('age_days', 30),
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'clear_temp_files':
                # Clear temporary files
                result = await SystemActions.clear_temp_files(
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'clear_package_cache':
                # Clear package manager cache (apt/yum)
                result = await SystemActions.clear_package_cache(
                    agent_name='hamsters',
                    verify=True
                )
            
            elif action == 'monitor':
                # Do nothing, just observe (useful for learning)
                self.logger.info("🐹👁️ Monitoring situation without intervention")
                result = {
                    'action': 'monitor',
                    'success': True,
                    'message': 'Monitoring without intervention',
                    'intervention': False
                }
            
            elif action == 'escalate':
                # Escalate to VIC-20 for coordination
                self.logger.info("🐹📢 Escalating to VIC-20 - Hamsters need help!")
                result = {
                    'action': 'escalate',
                    'success': True,
                    'message': 'Escalated to VIC-20 for coordination',
                    'escalated': True
                }
            
            else:
                # Unknown action - FAIL instead of fallback
                # Hamsters need to learn what works, not have a safety net
                self.logger.error(f"🐹❌ Unknown action: {action} - NO FALLBACK, Hamsters must learn!")
                result = {
                    'action': action,
                    'success': False,
                    'error': f'Unknown action: {action}. Hamsters do not know how to execute this.',
                    'learning_opportunity': True
                }
            
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
            # Cleanup actions
            'cleanup',                # Basic cleanup (no defrag)
            'cleanup_with_defrag',    # Full cleanup + defrag
            'clear_temp_files',       # Clear /tmp and temp directories
            'clear_package_cache',    # Clear apt/yum cache
            
            # Log management
            'rotate_logs',            # Log rotation
            'compress_logs',          # Compress old logs
            'archive_old_files',      # Archive old files
            
            # Disk optimization
            'fstrim',                 # TRIM unused blocks (SSD)
            'defrag_only',            # Defragment filesystem
            
            # Learning actions
            'monitor',                # Observe without intervention
            'escalate',               # Ask for help
        ]
