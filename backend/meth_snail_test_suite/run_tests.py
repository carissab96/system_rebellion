#!/usr/bin/env python3
"""
Standalone Meth Snail Test Runner 🐌⚡
Run from the meth_snail_test_suite directory!
"""
import subprocess
import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the test environment"""
    # Change to the test suite directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Add backend to Python path
    backend_dir = test_dir.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    print(f"🐌 Running from: {test_dir}")
    print(f"📁 Backend root: {backend_dir}")

def run_test_category(category, description):
    """Run a specific test category"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    if category == "unit":
        cmd = ["pytest", "tests/unit/", "-v"]
    elif category == "integration":
        cmd = ["pytest", "tests/integration/", "-v"]
    elif category == "performance":
        cmd = ["pytest", "tests/performance/", "-v", "-m", "performance"]
    elif category == "edge_cases":
        cmd = ["pytest", "tests/edge_cases/", "-v"]
    elif category == "all":
        cmd = ["pytest", "tests/", "-v"]
    elif category == "coverage":
        cmd = ["pytest", "tests/", "--cov=app.ai_agents.meth_snail", 
               "--cov=agent_memory_banks", "--cov-report=html:reports/coverage", 
               "--cov-report=term"]
    else:
        print(f"❌ Unknown category: {category}")
        return False
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    """Main test runner"""
    setup_environment()
    
    print("🐌⚡ METH SNAIL TEST SUITE")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1]
        descriptions = {
            "unit": "Unit Tests - Individual Component Testing",
            "integration": "Integration Tests - Full System Testing", 
            "performance": "Performance Tests - Load & Speed Testing",
            "edge_cases": "Edge Case Tests - Error Handling",
            "all": "All Tests - Complete Suite",
            "coverage": "Coverage Report - Full Analysis"
        }
        
        if category in descriptions:
            success = run_test_category(category, descriptions[category])
        else:
            print(f"Available categories: {', '.join(descriptions.keys())}")
            return 1
    else:
        # Run all categories
        categories = [
            ("unit", "Unit Tests"),
            ("integration", "Integration Tests"),
            ("performance", "Performance Tests"),
            ("edge_cases", "Edge Case Tests"),
            ("coverage", "Coverage Report")
        ]
        
        success = True
        for category, description in categories:
            if not run_test_category(category, description):
                success = False
                break
    
    if success:
        print("\n✅ All tests passed! Meth Snail is fully operational!")
        print("📊 Coverage report: reports/coverage/index.html")
        return 0
    else:
        print("\n❌ Some tests failed! Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())