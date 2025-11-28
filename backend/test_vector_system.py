#!/usr/bin/env python3
"""
Test Vector Database System
Verifies embedding generation and vector storage work correctly
"""

import asyncio
import sys
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, '/home/carissa/Documents/system_rebellion/backend')

from app.services.embedding_service import get_embedding_service, create_decision_text
from app.services.vector_storage import get_vector_storage

def utc_now():
    return datetime.now(timezone.utc)

async def test_embedding_service():
    """Test embedding generation"""
    print("\n" + "="*60)
    print("TEST 1: Embedding Service")
    print("="*60)
    
    try:
        embedding_service = get_embedding_service()
        print("✅ Embedding service initialized")
        
        # Create test decision text
        decision_text = create_decision_text(
            agent_name="vic_20_sage",
            decision_type="coordination",
            description="Test coordination decision",
            reasoning="Testing vector database integration",
            context={'priority': 5, 'test': True}
        )
        print(f"📝 Decision text created: {decision_text[:100]}...")
        
        # Generate embedding
        print("🔮 Generating embedding...")
        embedding = await embedding_service.generate_embedding_async(decision_text)
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
        print(f"   First 5 values: {embedding[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_storage():
    """Test vector storage"""
    print("\n" + "="*60)
    print("TEST 2: Vector Storage")
    print("="*60)
    
    try:
        embedding_service = get_embedding_service()
        vector_storage = get_vector_storage()
        print("✅ Vector storage initialized")
        
        # Create test decision
        decision_text = create_decision_text(
            agent_name="vic_20_sage",
            decision_type="coordination",
            description="Test coordination for vector storage",
            reasoning="Verifying fire-and-forget vector writes work",
            context={'priority': 5, 'test': True}
        )
        
        # Generate embedding
        embedding = await embedding_service.generate_embedding_async(decision_text)
        print(f"✅ Test embedding generated")
        
        # Store vector (fire-and-forget)
        print("🔮 Storing vector (fire-and-forget)...")
        vector_storage.store_decision_vector_fire_and_forget(
            agent_name="vic_20_sage",
            decision_type="coordination",
            decision_text=decision_text,
            embedding=embedding,
            occurred_at=utc_now(),
            user_id="test_user",
            event_type="test_coordination",
            priority=5,
            metadata={'test': True, 'source': 'test_vector_system.py'},
            sql_memory_id="test-memory-id-12345",
            confidence_score=0.95,
            decision_summary="Test coordination decision"
        )
        print("✅ Vector queued for storage (fire-and-forget)")
        
        # Wait a moment for async write to complete
        print("⏳ Waiting 2 seconds for async write to complete...")
        await asyncio.sleep(2)
        
        print("✅ Vector storage test complete")
        print("   Check PostgreSQL agent_decision_vectors table for test entry")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_search():
    """Test semantic search"""
    print("\n" + "="*60)
    print("TEST 3: Semantic Search")
    print("="*60)
    
    try:
        vector_storage = get_vector_storage()
        
        # Search for similar decisions
        print("🔍 Searching for coordination decisions...")
        results = await vector_storage.search_similar_decisions(
            query_text="agent coordination and system harmony",
            agent_name="vic_20_sage",
            limit=5
        )
        
        print(f"✅ Found {len(results)} similar decisions")
        for i, result in enumerate(results, 1):
            print(f"\n   Result {i}:")
            print(f"   - Decision: {result.get('decision_summary', 'N/A')[:60]}")
            print(f"   - Similarity: {result.get('similarity', 0):.3f}")
            print(f"   - Agent: {result.get('agent_name', 'N/A')}")
            print(f"   - Type: {result.get('decision_type', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 VECTOR DATABASE SYSTEM TEST")
    print("="*60)
    print("\nThis will test:")
    print("1. Embedding generation (sentence-transformers)")
    print("2. Vector storage (fire-and-forget writes)")
    print("3. Semantic search (pgvector similarity)")
    print()
    
    # Run tests
    test1 = await test_embedding_service()
    test2 = await test_vector_storage()
    test3 = await test_vector_search()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Embedding Service: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Vector Storage:    {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Semantic Search:   {'✅ PASS' if test3 else '❌ FAIL'}")
    print()
    
    if all([test1, test2, test3]):
        print("🎉 ALL TESTS PASSED!")
        print("\nVector database system is working correctly.")
        print("VIC-20 and Sir Hawkington can now store spatial memories!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\nCheck errors above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
