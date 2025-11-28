#!/usr/bin/env python3
"""
Test sentence-transformers embedding generation
Quick validation that the model works and measures performance
"""

import time
from sentence_transformers import SentenceTransformer

def test_embeddings():
    print("🧪 Testing sentence-transformers embedding generation...")
    print()
    
    # Load model
    print("📥 Loading model: all-MiniLM-L6-v2")
    start = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    load_time = time.time() - start
    print(f"✅ Model loaded in {load_time:.2f}s")
    print()
    
    # Test sentences (simulating agent decisions)
    test_sentences = [
        "Decision Type: coordination | Agent: vic_20_sage | Description: Coordinating multi-agent response to system stress | Reasoning: Multiple agents reporting high load, need orchestrated response",
        "Decision Type: triage | Agent: sir_hawkington | Description: Emergency escalation to VIC-20 | Reasoning: System metrics critical, monocle yeeted, immediate coordination required",
        "Decision Type: optimization | Agent: meth_snail | Description: Shell-spinning optimization applied | Reasoning: Detected performance bottleneck, applied caffeinated solution",
        "Decision Type: infrastructure | Agent: hamsters | Description: Duct tape solution deployed | Reasoning: Bob detected, anxiety spike, emergency fix required",
        "Decision Type: security | Agent: quantum_shadow_people | Description: Phase-shift security pattern detected | Reasoning: Anomalous network activity, quantum analysis required"
    ]
    
    # Generate embeddings
    print("🔮 Generating embeddings...")
    start = time.time()
    embeddings = model.encode(test_sentences)
    total_time = time.time() - start
    avg_time = total_time / len(test_sentences)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"⏱️  Total time: {total_time*1000:.2f}ms")
    print(f"⏱️  Average per embedding: {avg_time*1000:.2f}ms")
    print(f"📊 Embedding dimensions: {embeddings[0].shape[0]}")
    print()
    
    # Test similarity
    print("🔍 Testing semantic similarity...")
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Compare coordination decisions (should be similar)
    sim_1_2 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    print(f"Coordination vs Triage (related): {sim_1_2:.4f}")
    
    # Compare unrelated decisions (should be less similar)
    sim_1_3 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
    print(f"Coordination vs Optimization (unrelated): {sim_1_3:.4f}")
    
    # Compare very different decisions
    sim_1_4 = cosine_similarity([embeddings[0]], [embeddings[3]])[0][0]
    print(f"Coordination vs Infrastructure (different): {sim_1_4:.4f}")
    
    print()
    print("✅ Embedding generation working!")
    print()
    print("📈 Performance Summary:")
    print(f"   - Model load: {load_time:.2f}s (one-time cost)")
    print(f"   - Per embedding: {avg_time*1000:.2f}ms")
    print(f"   - Dimensions: {embeddings[0].shape[0]}")
    print(f"   - Target: <10ms per embedding ✅" if avg_time*1000 < 10 else f"   - Target: <10ms per embedding ⚠️  (got {avg_time*1000:.2f}ms)")
    print()
    
    return True

if __name__ == "__main__":
    try:
        test_embeddings()
        print("🎉 All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
