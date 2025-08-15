#!/usr/bin/env python3
"""
Dependency checker script for System Rebellion project.
This script analyzes Python files to find imports and compares them with requirements.txt.
"""

import os
import re
import sys
from collections import defaultdict

def parse_requirements_file(file_path):
    """Parse requirements.txt file and return a set of package names."""
    requirements = set()
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Extract package name (remove version specifiers)
            match = re.match(r'^([a-zA-Z0-9_.-]+)', line)
            if match:
                package_name = match.group(1).lower()
                requirements.add(package_name)
    
    return requirements

def find_imports_in_file(file_path):
    """Extract import statements from a Python file."""
    imports = set()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        try:
            content = f.read()
            
            # Find all import statements
            import_lines = re.findall(r'^import\s+(.+?)(?:\s+as\s+.+)?$', content, re.MULTILINE)
            for line in import_lines:
                # Handle multiple imports on one line (import os, sys, re)
                for imp in line.split(','):
                    base_module = imp.strip().split('.')[0]
                    if base_module and not base_module.startswith('_'):
                        imports.add(base_module.lower())
            
            # Find all from ... import statements
            from_import_lines = re.findall(r'^from\s+([a-zA-Z0-9_.]+)\s+import', content, re.MULTILINE)
            for imp in from_import_lines:
                if imp.startswith('.'):  # Relative import
                    continue
                base_module = imp.split('.')[0]
                if base_module and not base_module.startswith('_') and base_module != 'app':
                    imports.add(base_module.lower())
                    
        except UnicodeDecodeError:
            print(f"Warning: Could not decode {file_path}")
    
    return imports

def find_all_python_files(directory, exclude_dirs=None):
    """Find all Python files in the directory and subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = ['venv', '__pycache__', '.git']
        
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def map_import_to_package(import_name):
    """Map import names to package names in requirements.txt."""
    # Common mappings where import name differs from package name
    mappings = {
        'yaml': 'pyyaml',
        'jose': 'python-jose',
        'dotenv': 'python-dotenv',
        'jwt': 'pyjwt',
        'psycopg2': 'psycopg2-binary',
        'sqlalchemy': 'sqlalchemy',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'starlette': 'starlette',
        'websockets': 'websockets',
        'aiosqlite': 'aiosqlite',
        'rich': 'rich',
        'passlib': 'passlib',
        'bcrypt': 'bcrypt',
        'email_validator': 'email-validator',
        'httpx': 'httpx',
        'pytest': 'pytest',
        'channels': 'channels',
        'redis': 'redis',
        'numpy': 'numpy',
        'psutil': 'psutil',
    }
    
    return mappings.get(import_name, import_name)

def main():
    """Main function to check dependencies."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(project_dir, 'requirements.txt')
    
    # Parse requirements.txt
    required_packages = parse_requirements_file(requirements_file)
    print(f"Found {len(required_packages)} packages in requirements.txt")
    
    # Find all Python files
    python_files = find_all_python_files(project_dir)
    print(f"Found {len(python_files)} Python files to analyze")
    
    # Extract imports from all Python files
    all_imports = set()
    file_imports = defaultdict(set)
    
    for py_file in python_files:
        imports = find_imports_in_file(py_file)
        all_imports.update(imports)
        file_imports[py_file] = imports
    
    # Map imports to package names
    mapped_imports = {map_import_to_package(imp) for imp in all_imports}
    
    # Find missing packages (used but not in requirements.txt)
    standard_libs = {
        'os', 'sys', 're', 'json', 'time', 'datetime', 'collections', 'random',
        'math', 'logging', 'io', 'functools', 'itertools', 'pathlib', 'typing',
        'uuid', 'enum', 'abc', 'copy', 'inspect', 'traceback', 'warnings',
        'contextlib', 'asyncio', 'socket', 'subprocess', 'shutil', 'platform',
        'getpass', 'secrets', 'statistics', 'ast'
    }
    
    third_party_imports = mapped_imports - standard_libs
    missing_packages = third_party_imports - required_packages
    unused_packages = required_packages - third_party_imports
    
    # Print results
    print("\n=== DEPENDENCY ANALYSIS RESULTS ===")
    
    if missing_packages:
        print("\n🚨 MISSING PACKAGES (imported but not in requirements.txt):")
        for pkg in sorted(missing_packages):
            print(f"  - {pkg}")
    else:
        print("\n✅ No missing packages detected.")
    
    if unused_packages:
        print("\n⚠️  POTENTIALLY UNUSED PACKAGES (in requirements.txt but not imported):")
        for pkg in sorted(unused_packages):
            print(f"  - {pkg}")
    else:
        print("\n✅ No unused packages detected.")
    
    print("\n=== SUMMARY ===")
    print(f"Total packages in requirements.txt: {len(required_packages)}")
    print(f"Total third-party packages imported: {len(third_party_imports)}")
    print(f"Missing packages: {len(missing_packages)}")
    print(f"Potentially unused packages: {len(unused_packages)}")
    
    # Provide recommendations
    if missing_packages or unused_packages:
        print("\n=== RECOMMENDATIONS ===")
        if missing_packages:
            print("Consider adding these missing packages to requirements.txt:")
            for pkg in sorted(missing_packages):
                print(f"  {pkg}")
        
        if unused_packages:
            print("\nNote: 'Unused' packages might still be needed if:")
            print("  - They're used through dynamic imports")
            print("  - They're dependencies of other packages")
            print("  - They provide CLI tools used in your workflow")
            print("  - They're used in tests or scripts not analyzed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
