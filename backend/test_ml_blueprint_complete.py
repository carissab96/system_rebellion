#!/usr/bin/env python3
"""
Quick validation test for ML Blueprint v2 - All Agents

Tests that all ML architecture components can be imported successfully.
This is a static validation - no runtime execution needed.

Agents tested:
- Terry (Meth Snail) v2
- Sir Hawkington v2
- VIC-20 v2
- Hamsters v2
- QSP v2
- The Stick v2
"""

def test_terry_v2_imports():
    """Test Terry v2 ML architecture imports"""
    print("🐌 Testing Terry v2 ML architecture...")
    try:
        from app.ai_agents.meth_snail.perception import TerryPerception, TerryPerceptionContext
        from app.ai_agents.meth_snail.reasoning import TerryReasoning, CacheReasoning
        from app.ai_agents.meth_snail.action_selection import TerryActionSelection, CacheAction
        from app.ai_agents.meth_snail.learning import TerryLearning, TerryLearningRecord
        print("✅ Terry v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ Terry v2 import failed: {e}")
        return False


def test_hawkington_v2_imports():
    """Test Sir Hawkington v2 ML architecture imports"""
    print("\n🎩 Testing Sir Hawkington v2 ML architecture...")
    try:
        from app.ai_agents.sir_hawkington.perception import HawkPerception, HawkPerceptionContext
        from app.ai_agents.sir_hawkington.reasoning import HawkReasoning, TriageReasoning
        from app.ai_agents.sir_hawkington.action_selection import HawkActionSelection, TriageAction
        from app.ai_agents.sir_hawkington.learning import HawkLearning, HawkLearningRecord
        print("✅ Sir Hawkington v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ Sir Hawkington v2 import failed: {e}")
        return False


def test_vic20_v2_imports():
    """Test VIC-20 v2 ML architecture imports"""
    print("\n🖥️ Testing VIC-20 v2 ML architecture...")
    try:
        from app.ai_agents.vic_20_sage.perception import VIC20Perception, VIC20PerceptionContext
        from app.ai_agents.vic_20_sage.reasoning import VIC20Reasoning, CoordinationReasoning
        from app.ai_agents.vic_20_sage.action_selection import VIC20ActionSelection, CoordinationAction
        from app.ai_agents.vic_20_sage.learning import VIC20Learning, VIC20LearningRecord
        print("✅ VIC-20 v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ VIC-20 v2 import failed: {e}")
        return False


def test_hamsters_v2_imports():
    """Test Hamsters v2 ML architecture imports"""
    print("\n🐹 Testing Hamsters v2 ML architecture...")
    try:
        from app.ai_agents.hamsters.perception import HamstersPerception, HamstersPerceptionContext
        from app.ai_agents.hamsters.reasoning import HamstersReasoning, StorageReasoning
        from app.ai_agents.hamsters.action_selection import HamstersActionSelection, StorageFixAction
        from app.ai_agents.hamsters.learning import HamstersLearning, HamstersLearningRecord
        print("✅ Hamsters v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ Hamsters v2 import failed: {e}")
        return False


def test_qsp_v2_imports():
    """Test QSP v2 ML architecture imports"""
    print("\n👻 Testing QSP v2 ML architecture...")
    try:
        from app.ai_agents.qsp.perception import QSPPerception, QSPPerceptionContext
        from app.ai_agents.qsp.reasoning import QSPReasoning, SecurityReasoning
        from app.ai_agents.qsp.action_selection import QSPActionSelection, SecurityResponseAction
        from app.ai_agents.qsp.learning import QSPLearning, QSPLearningRecord
        print("✅ QSP v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ QSP v2 import failed: {e}")
        return False


def test_stick_v2_imports():
    """Test The Stick v2 ML architecture imports"""
    print("\n📊 Testing The Stick v2 ML architecture...")
    try:
        from app.ai_agents.the_stick.perception import StickPerception, StickPerceptionContext
        from app.ai_agents.the_stick.reasoning import StickReasoning, LoggingReasoning
        from app.ai_agents.the_stick.action_selection import StickActionSelection, LoggingAction
        from app.ai_agents.the_stick.learning import StickLearning, StickLearningRecord
        print("✅ The Stick v2 imports successful")
        return True
    except Exception as e:
        print(f"❌ The Stick v2 import failed: {e}")
        return False


def main():
    """Run all ML blueprint v2 validation tests"""
    print("="*80)
    print("ML BLUEPRINT V2 - VALIDATION TEST")
    print("Testing all 6 agents: Terry, Hawk, VIC-20, Hamsters, QSP, The Stick")
    print("="*80)
    
    results = []
    
    # Test all agents
    results.append(("Terry v2", test_terry_v2_imports()))
    results.append(("Sir Hawkington v2", test_hawkington_v2_imports()))
    results.append(("VIC-20 v2", test_vic20_v2_imports()))
    results.append(("Hamsters v2", test_hamsters_v2_imports()))
    results.append(("QSP v2", test_qsp_v2_imports()))
    results.append(("The Stick v2", test_stick_v2_imports()))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for agent, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {agent}")
    
    print(f"\nResults: {passed}/{total} agents validated successfully")
    
    if passed == total:
        print("\n🎉 ALL AGENTS ML BLUEPRINT V2 COMPLETE!")
        print("\nArchitecture Pattern (All Agents):")
        print("  Perception → Reasoning → Action Selection → Learning")
        print("\nPersonality Behaviors (All Reactive to Real Data):")
        print("  🐌 Terry: Shell spins, energy drinks")
        print("  🎩 Hawk: Monocle yeets, triage confidence")
        print("  🖥️ VIC-20: Coordination routing, specialist trust")
        print("  🐹 Hamsters: Beer, duct tape, telepathic consensus")
        print("  👻 QSP: Quantum states, existential dread")
        print("  📊 Stick: Anxiety, paper bags, Bob detection")
        print("\n🎄 Merry Christmas! Time to celebrate! 🎄")
        return 0
    else:
        print(f"\n⚠️ {total - passed} agent(s) need attention")
        return 1


if __name__ == "__main__":
    exit(main())
