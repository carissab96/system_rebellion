#!/usr/bin/env python3
"""
Fix WebSocket router import issues
"""

import os

def fix_websocket_router_imports():
    """Fix missing imports in WebSocket router"""
    file_path = "app/ai_agents/master_websocket_router_v2.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove the problematic import
    imports_to_remove = [
        "from .sir_hawkington.decision_engine import analyze_for_websocket",
        ", analyze_for_websocket",
        "analyze_for_websocket,",
        "analyze_for_websocket"
    ]
    
    original_content = content
    
    for import_line in imports_to_remove:
        content = content.replace(import_line, "")
    
    # Clean up any resulting empty import lines
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip empty import lines
        if line.strip() in ["from", "import", "from import"]:
            continue
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ Fixed WebSocket router imports")
        return True
    else:
        print("✅ No import issues found")
        return True

def main():
    print("🧐 FIXING WEBSOCKET ROUTER IMPORTS")
    print("="*50)
    
    if fix_websocket_router_imports():
        print("✅ WebSocket router imports fixed")
    
    print("\n🎯 Next steps:")
    print("1. Run the debug script to find 'self' issues")
    print("2. Fix any indentation or method definition issues")
    print("3. Re-run tests")

if __name__ == "__main__":
    main()