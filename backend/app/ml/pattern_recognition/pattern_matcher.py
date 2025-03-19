from typing import Dict, List, Optional
import numpy as np
#from sentence_transformers import SentenceTransformer

class PatternMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pattern_embeddings = {}
        self.similarity_threshold = 0.8

    async def match_pattern(self, current_state: Dict) -> Optional[Dict]:
        """Match current state against known patterns"""
        current_embedding = self._generate_embedding(current_state)
        
        best_match = None
        highest_similarity = 0

        for pattern_id, pattern_data in self.pattern_embeddings.items():
            similarity = self._calculate_similarity(
                current_embedding, 
                pattern_data['embedding']
            )
            
            if similarity > highest_similarity and similarity > self.similarity_threshold:
                highest_similarity = similarity
                best_match = pattern_data['pattern']

        return best_match

    def _generate_embedding(self, state: Dict) -> np.ndarray:
        """Generate embedding for state"""
        state_str = self._state_to_string(state)
        return self.model.encode([state_str])[0]

    def _state_to_string(self, state: Dict) -> str:
        """Convert state to string representation"""
        return f"CPU:{state['cpu_usage']} MEM:{state['memory_usage']} DISK:{state['disk_usage']}"

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))