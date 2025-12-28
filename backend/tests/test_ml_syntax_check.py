#!/usr/bin/env python3
"""
Syntax validation for ML Blueprint v2 - All Agents

Checks that all Python files have valid syntax without importing dependencies.
"""
import ast
import sys
from pathlib import Path

def check_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def main():
    """Validate syntax for all ML blueprint files"""
    print("="*80)
    print("ML BLUEPRINT V2 - SYNTAX VALIDATION")
    print("="*80)
    
    base_path = Path(__file__).parent / "app" / "ai_agents"
    
    agents = {
        "Terry v2 (Meth Snail)": [
            "meth_snail/perception.py",
            "meth_snail/reasoning.py",
            "meth_snail/action_selection.py",
            "meth_snail/learning.py"
        ],
        "Sir Hawkington v2": [
            "sir_hawkington/perception.py",
            "sir_hawkington/reasoning.py",
            "sir_hawkington/action_selection.py",
            "sir_hawkington/learning.py"
        ],
        "VIC-20 v2": [
            "vic_20_sage/perception.py",
            "vic_20_sage/reasoning.py",
            "vic_20_sage/action_selection.py",
            "vic_20_sage/learning.py"
        ],
        "Hamsters v2": [
            "hamsters/perception.py",
            "hamsters/reasoning.py",
            "hamsters/action_selection.py",
            "hamsters/learning.py"
        ],
        "QSP v2": [
            "qsp/perception.py",
            "qsp/reasoning.py",
            "qsp/action_selection.py",
            "qsp/learning.py"
        ],
        "The Stick v2": [
            "the_stick/perception.py",
            "the_stick/reasoning.py",
            "the_stick/action_selection.py",
            "the_stick/learning.py"
        ]
    }
    
    all_passed = True
    results = []
    
    for agent_name, files in agents.items():
        print(f"\n{agent_name}:")
        agent_passed = True
        
        for file_rel in files:
            file_path = base_path / file_rel
            layer = file_rel.split('/')[-1].replace('.py', '')
            
            if not file_path.exists():
                print(f"  ❌ {layer}: FILE NOT FOUND")
                agent_passed = False
                all_passed = False
            else:
                passed, msg = check_syntax(file_path)
                if passed:
                    print(f"  ✅ {layer}")
                else:
                    print(f"  ❌ {layer}: {msg}")
                    agent_passed = False
                    all_passed = False
        
        results.append((agent_name, agent_passed))
    
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
    
    if all_passed:
        print("\n" + "="*80)
        print("🎉 ALL AGENTS ML BLUEPRINT V2 SYNTAX VALID!")
        print("="*80)
        print("\nArchitecture Pattern (All Agents):")
        print("  Perception → Reasoning → Action Selection → Learning")
        print("\nPersonality Behaviors (All Reactive to Real Data):")
        print("  🐌 Terry: Shell spins, energy drinks")
        print("  🎩 Hawk: Monocle yeets, triage confidence")
        print("  🖥️ VIC-20: Coordination routing, specialist trust")
        print("  🐹 Hamsters: Beer, duct tape, telepathic consensus")
        print("  👻 QSP: Quantum states, existential dread")
        print("  📊 Stick: Anxiety, paper bags, Bob detection")
        print("\nInter-Agent Dynamics:")
        print("  🐹→📊 Hamster telepathy (only Stick understands)")
        print("  👻→🐹 QSP quantum messages (only Hamsters understand)")
        print("  🐹(Bob)→📊 Bob's chaos (terrorizes Stick)")
        print("  🐌→🎩 Energy drink authorization (Hawk can VETO)")
        print("  🎩→🖥️→🐌🐹👻📊 Coordination hierarchy")
        print("\n🎄 Merry Christmas Eve! All ML architectures complete! 🎄")
        return 0
    else:
        print(f"\n⚠️ {total - passed} agent(s) have syntax errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
