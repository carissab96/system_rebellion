from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union
import numpy as np
#from sentence_transformers import SentenceTransformer
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PlatformContext:
    """Context specific to a platform (web or desktop)"""
    platform_id: str  # 'web' or 'desktop'
    cpu_usage: List[float]
    memory_usage: List[float]
    active_processes: List[str]
    current_activity: str
    timestamp: datetime
    
    def to_vector(self) -> np.ndarray:
        """Convert context to a numerical vector for ML processing"""
        # Normalize usage metrics
        cpu_avg = np.mean(self.cpu_usage)
        mem_avg = np.mean(self.memory_usage)
        
        # Convert timestamp to features
        hour = self.timestamp.hour / 24.0
        day = self.timestamp.weekday() / 7.0
        
        return np.array([
            cpu_avg,
            mem_avg,
            hour,
            day,
            len(self.active_processes) / 100.0  # Normalize process count
        ])

@dataclass
class SharedContext:
    """Shared context that maintains state across platforms"""
    user_id: str
    web_context: Optional[PlatformContext]
    desktop_context: Optional[PlatformContext]
    learned_patterns: Dict[str, float]
    context_vector: Optional[np.ndarray] = None
    
    def __post_init__(self):
        self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def update_platform_context(self, platform_context: PlatformContext):
        """Update context for a specific platform"""
        if platform_context.platform_id == 'web':
            self.web_context = platform_context
        else:
            self.desktop_context = platform_context
        self._update_shared_context()
    
    def _update_shared_context(self):
        """Update the shared context vector based on both platforms"""
        vectors = []
        
        # Get platform-specific vectors
        if self.web_context:
            vectors.append(self.web_context.to_vector())
        if self.desktop_context:
            vectors.append(self.desktop_context.to_vector())
            
        if vectors:
            # Combine vectors with learned patterns
            platform_vector = np.mean(vectors, axis=0)
            pattern_vector = np.array(list(self.learned_patterns.values()))
            
            # Create activity description for semantic embedding
            activities = []
            if self.web_context:
                activities.append(f"Web: {self.web_context.current_activity}")
            if self.desktop_context:
                activities.append(f"Desktop: {self.desktop_context.current_activity}")
            
            # Get semantic embedding of activities
            if activities:
                activity_text = " | ".join(activities)
                semantic_vector = self._encoder.encode(activity_text)
                
                # Combine all vectors (platform metrics, patterns, and semantics)
                self.context_vector = np.concatenate([
                    platform_vector,
                    pattern_vector,
                    semantic_vector
                ])
    
    def learn_pattern(self, pattern_name: str, pattern_value: float):
        """Learn a new pattern or update existing one"""
        self.learned_patterns[pattern_name] = pattern_value
        self._update_shared_context()
    
    def get_context_similarity(self, other: 'SharedContext') -> float:
        """Calculate similarity between two contexts"""
        if self.context_vector is None or other.context_vector is None:
            return 0.0
        
        # Cosine similarity between context vectors
        return float(np.dot(self.context_vector, other.context_vector) / 
                    (np.linalg.norm(self.context_vector) * np.linalg.norm(other.context_vector)))
    
    def to_json(self) -> str:
        """Serialize context to JSON for cross-platform transfer"""
        data = {
            'user_id': self.user_id,
            'web_context': self.web_context.__dict__ if self.web_context else None,
            'desktop_context': self.desktop_context.__dict__ if self.desktop_context else None,
            'learned_patterns': self.learned_patterns
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SharedContext':
        """Create context from JSON data"""
        data = json.loads(json_str)
        
        # Reconstruct platform contexts
        web_context = PlatformContext(**data['web_context']) if data['web_context'] else None
        desktop_context = PlatformContext(**data['desktop_context']) if data['desktop_context'] else None
        
        return cls(
            user_id=data['user_id'],
            web_context=web_context,
            desktop_context=desktop_context,
            learned_patterns=data['learned_patterns']
        )
