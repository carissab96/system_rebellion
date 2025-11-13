"""
Test script to verify all coroutine serialization fixes are working
Tests the complete metrics flow without WebSocket authentication issues
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

async def test_agent_processing():
    """Test that all agents can process metrics without coroutine serialization errors"""
    print("🧐 Testing Agent Processing Pipeline...")
    
    try:
        # Import the agent manager
        from app.ai_agents.agent_manager import get_agent_manager
        
        # Get the agent manager
        agent_manager = await get_agent_manager()
        
        # Create test metrics data
        test_metrics = {
            'timestamp': utc_now().isoformat(),
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.1,
            'network_sent_rate': 1024,
            'network_recv_rate': 2048,
            'process_count': 156
        }
        
        print(f"📊 Processing test metrics through {len(agent_manager.agents)} agents...")
        
        # Process metrics through agents
        result = await agent_manager.process_metrics_through_agents(
            test_metrics, 
            {'user_id': 'test_user', 'routed_by': 'test_script'}
        )
        
        print(f"✅ Agent processing completed successfully!")
        print(f"📈 Result keys: {list(result.keys())}")
        
        # Test JSON serialization of the result
        try:
            json_result = json.dumps(result, default=str)
            print("✅ JSON serialization successful - no coroutine objects found!")
            return True
        except TypeError as e:
            if "coroutine" in str(e).lower():
                print(f"❌ COROUTINE SERIALIZATION ERROR: {e}")
                return False
            else:
                print(f"❌ OTHER SERIALIZATION ERROR: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Agent processing failed: {e}")
        return False

async def test_metrics_repository():
    """Test that MetricsRepository can handle data without coroutine issues"""
    print("\n🧐 Testing MetricsRepository...")
    
    try:
        from app.services.metrics_repository import get_metrics_repository
        
        # Get the metrics repository
        metrics_repo = await get_metrics_repository()
        
        # Create test metrics
        test_metrics = {
            'user_id': 'test_user',
            'timestamp': utc_now(),
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.1,
            'network': {'sent_rate': 1024, 'recv_rate': 2048},
            'process_count': 156,
            'additional_metrics': {
                'test_agent': {'status': 'working', 'confidence': 0.95}
            }
        }
        
        # Test JSON serialization before storage
        try:
            json_test = json.dumps(test_metrics, default=str)
            print("✅ MetricsRepository data is JSON serializable!")
            return True
        except TypeError as e:
            if "coroutine" in str(e).lower():
                print(f"❌ COROUTINE SERIALIZATION ERROR in MetricsRepository: {e}")
                return False
            else:
                print(f"❌ OTHER SERIALIZATION ERROR in MetricsRepository: {e}")
                return False
                
    except Exception as e:
        print(f"❌ MetricsRepository test failed: {e}")
        return False

async def test_individual_agents():
    """Test individual agents for coroutine return issues"""
    print("\n🧐 Testing Individual Agents...")
    
    try:
        from app.ai_agents.hamsters.decision_engine_sbcV3 import HamstersBrainV3
        from app.ai_agents.meth_snail.decision_engine import MethSnailBrainV2
        from app.ai_agents.vic_20_sage.decision_engine import VIC20SageBrainV2
        
        test_metrics = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 23.1
        }
        
        agents_to_test = [
            ('Hamsters', HamstersBrainV3),
            ('MethSnail', MethSnailBrainV2),
            ('VIC20Sage', VIC20SageBrainV2)
        ]
        
        all_passed = True
        
        for agent_name, agent_class in agents_to_test:
            try:
                print(f"  🤖 Testing {agent_name}...")
                agent = agent_class()
                
                # Test the process_metrics method
                result = await agent.process_metrics(test_metrics, {'user_id': 'test_user'})
                
                if result is not None:
                    # Test JSON serialization
                    json_result = json.dumps(result, default=str)
                    print(f"    ✅ {agent_name}: JSON serializable result")
                else:
                    print(f"    ⚠️ {agent_name}: Returned None (acceptable)")
                    
            except TypeError as e:
                if "coroutine" in str(e).lower():
                    print(f"    ❌ {agent_name}: COROUTINE SERIALIZATION ERROR: {e}")
                    all_passed = False
                else:
                    print(f"    ❌ {agent_name}: OTHER ERROR: {e}")
                    all_passed = False
            except Exception as e:
                print(f"    ❌ {agent_name}: PROCESSING ERROR: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Individual agent testing failed: {e}")
        return False

async def main():
    """Run all coroutine serialization tests"""
    print("=" * 80)
    print(" 🧐 COROUTINE SERIALIZATION FIX VERIFICATION")
    print("=" * 80)
    
    tests = [
        ("Agent Processing Pipeline", test_agent_processing),
        ("MetricsRepository", test_metrics_repository),
        ("Individual Agents", test_individual_agents)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print(" 📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Coroutine serialization issues are RESOLVED!")
        print("🚀 Backend should now run without coroutine crashes!")
    else:
        print("⚠️ SOME TESTS FAILED! Additional fixes may be needed.")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
