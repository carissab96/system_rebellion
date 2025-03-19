from typing import Dict, Optional
from datetime import datetime
import logging
from .context_model import SharedContext, PlatformContext
#from .views import ContextManagerView

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages context synchronization between platforms"""
    
    def __init__(self):
        self._contexts: Dict[str, SharedContext] = {}  # user_id -> SharedContext
        
    def get_user_context(self, user_id: str) -> Optional[SharedContext]:
        """Get context for a specific user"""
        return self._contexts.get(user_id)
    
    def update_context(self, user_id: str, platform_id: str, context_data: dict) -> SharedContext:
        """Update context for a specific user and platform"""
        # Create platform-specific context
        platform_context = PlatformContext(
            platform_id=platform_id,
            cpu_usage=context_data.get('cpu_usage', []),
            memory_usage=context_data.get('memory_usage', []),
            active_processes=context_data.get('active_processes', []),
            current_activity=context_data.get('current_activity', ''),
            timestamp=datetime.now()
        )
        
        # Get or create shared context
        shared_context = self._contexts.get(user_id)
        if not shared_context:
            shared_context = SharedContext(
                user_id=user_id,
                web_context=None,
                desktop_context=None,
                learned_patterns={}
            )
            self._contexts[user_id] = shared_context
        
        # Update platform-specific context
        shared_context.update_platform_context(platform_context)
        
        return shared_context
    
    def sync_contexts(self, source_user_id: str, target_user_id: str) -> float:
        """Synchronize contexts between two user sessions and return similarity"""
        source_context = self._contexts.get(source_user_id)
        target_context = self._contexts.get(target_user_id)
        
        if not source_context or not target_context:
            return 0.0
            
        similarity = source_context.get_context_similarity(target_context)
        
        # If contexts are similar enough, share learned patterns
        if similarity > 0.8:  # Threshold for pattern sharing
            for pattern, value in source_context.learned_patterns.items():
                if pattern not in target_context.learned_patterns:
                    target_context.learn_pattern(pattern, value)
        
        return similarity
    
    def export_context(self, user_id: str) -> Optional[str]:
        """Export context as JSON for cross-platform transfer"""
        context = self._contexts.get(user_id)
        if context:
            return context.to_json()
        return None
    
    def import_context(self, user_id: str, context_json: str) -> SharedContext:
        """Import context from JSON data"""
        context = SharedContext.from_json(context_json)
        self._contexts[user_id] = context
        return context

