# test_ml.py
from sentence_transformers import SentenceTransformer
import torch
from core.ml.pattern_recognition.pattern_analyzer import PatternAnalyzer
from core.ml.pattern_recognition.pattern_matcher import PatternMatcher
from core.ml.pattern_recognition.pattern_validator import PatternValidator
from core.models import SystemMetrics

def main():
    print("=== Sir Hawkington's Distinguished ML Tests ===")
    
    # Test 1: GPU Check
    print("\nChecking GPU availability...")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    
    # Test 2: Transformer Test
    print("\nTesting Sentence Transformers...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    optimization_contexts = [
        "My system is running slowly",
        "CPU usage is very high",
        "Need to improve performance",
        "Memory usage is at 90%",
        "System needs optimization",
        # Control sentence
        "I'm making a sandwich"
    ]
    
    print("\nAnalyzing contextual relationships...")
    embeddings = model.encode(optimization_contexts)
    from sklearn.metrics.pairwise import cosine_similarity
    
    sim_matrix = cosine_similarity(embeddings)
    
    print("\nSimilarity Analysis:")
    for i, context in enumerate(optimization_contexts):
        print(f"\nContext: {context}")
        # Find most similar (excluding self)
        similarities = [(j, sim) for j, sim in enumerate(sim_matrix[i]) if j != i]
        most_similar = max(similarities, key=lambda x: x[1])
        print(f"Most similar: {optimization_contexts[most_similar[0]]} ({most_similar[1]:.4f})")
    
    print("\n🧐 Sir Hawkington's Distinguished ML Tests 🧐")

def test_similarity():
    print("\nTesting contextual understanding...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    sentences = [
        "The system needs optimization",
        "This computer requires performance tuning",
        "I like chocolate cake"
    ]
    
    embeddings = model.encode(sentences)
    from sklearn.metrics.pairwise import cosine_similarity
    
    sim_matrix = cosine_similarity(embeddings)
    print("\nSimilarity Matrix:")
    for i, sent in enumerate(sentences):
        print(f"\nSentence {i+1}: {sent}")
        for j, sim in enumerate(sim_matrix[i]):
            print(f"Similarity to sentence {j+1}: {sim:.4f}")

    embeddings = model.encode(sentences)
    print(f"Embeddings generated successfully!")
    print(f"Embeddings shape: {embeddings.shape}")

if __name__ == "__main__":
    main()
