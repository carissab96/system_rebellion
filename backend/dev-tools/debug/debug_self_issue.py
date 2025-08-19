#!/usr/bin/env python3
"""
Debug the 'self' is not defined issue
"""

import ast
import os

def find_self_issues(file_path):
    """Find potential 'self' issues in Python files"""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Look for 'self' usage outside method definitions
        if 'self' in line and line.strip():
            # Skip if it's in a method definition
            if 'def ' in line and 'self' in line:
                continue
            # Skip if it's in a comment
            if line.strip().startswith('#'):
                continue
            # Skip if it's in a string
            if line.count('"') >= 2 or line.count("'") >= 2:
                continue
            
            # Check if it's actually problematic
            stripped = line.strip()
            if (stripped.startswith('self.') or 
                'self.' in stripped or 
                'self,' in stripped or 
                stripped.endswith('self')):
                
                # Check if we're inside a class method
                method_indent = None
                for j in range(i-1, max(0, i-20), -1):
                    prev_line = lines[j-1].strip()
                    if prev_line.startswith('def ') and 'self' in prev_line:
                        method_indent = len(lines[j-1]) - len(lines[j-1].lstrip())
                        break
                    if prev_line.startswith('class '):
                        break
                
                current_indent = len(line) - len(line.lstrip())
                
                if method_indent is None or current_indent <= method_indent:
                    issues.append((i, line.strip()))
    
    return issues

def main():
    print("🧐 DEBUGGING 'self' ISSUES")
    print("="*50)
    
    files_to_check = [
        "app/ai_agents/agent_manager.py",
        "app/ai_agents/sir_hawkington/triage_engine.py",
        "app/ai_agents/sir_hawkington/decision_engine.py",
        "app/ai_agents/master_websocket_routes.py"
    ]
    
    for file_path in files_to_check:
        print(f"\n🔍 Checking {file_path}:")
        issues = find_self_issues(file_path)
        
        if issues:
            print(f"   ❌ Found {len(issues)} potential issues:")
            for line_num, line in issues:
                print(f"      Line {line_num}: {line}")
        else:
            print("   ✅ No obvious 'self' issues found")

if __name__ == "__main__":
    main()