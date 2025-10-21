#!/usr/bin/env python3
"""
Find Memory Operations

This script scans the codebase for memory-related operations that might need to be updated.
"""

import os
import re
from pathlib import Path
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Directories to scan
SCAN_DIRS = [
    'app/ai_agents',
    'app/services',
    'app/api',
    'app/core',
    'app/models'
]

# File patterns to include
INCLUDE_PATTERNS = ['*.py']

# Directories to exclude
EXCLUDE_DIRS = {
    '__pycache__',
    '.git',
    'venv',
    '.venv',
    'migrations',
    'tests',
    'test',
    'utils',
    'scripts'
}

# Memory-related patterns to search for
MEMORY_PATTERNS = [
    # Session operations
    r'session\s*\.\s*add\s*\(',
    r'session\s*\.\s*add_all\s*\(',
    r'session\s*\.\s*query\s*\(',
    r'session\s*\.\s*execute\s*\(',
    r'session\s*\.\s*commit\s*\(',
    r'session\s*\.\s*delete\s*\(',
    
    # Memory-related method calls
    r'store_memory\s*\(',
    r'retrieve_memory\s*\(',
    r'get_memory\s*\(',
    r'create_memory\s*\(',
    r'update_memory\s*\(',
    r'delete_memory\s*\(',
    
    # Common memory-related terms
    r'Memory\s*\('
]

def should_skip_directory(dirname: str) -> bool:
    """Check if a directory should be skipped."""
    return dirname in EXCLUDE_DIRS or dirname.startswith('.')

def scan_file(filepath: str) -> List[Dict]:
    """Scan a file for memory-related operations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip empty files
        if not content.strip():
            return []
        
        # Check if file contains any memory-related patterns
        matches = []
        for pattern in MEMORY_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content.count('\n', 0, match.start()) + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line = content[line_start:line_end].strip()
                
                matches.append({
                    'file': filepath,
                    'line': line_num,
                    'pattern': pattern,
                    'code': line
                })
        
        return matches
    
    except Exception as e:
        logger.warning(f"Error scanning {filepath}: {e}")
        return []

def main():
    """Main function to scan the codebase."""
    base_dir = Path(__file__).parent.parent
    results = []
    
    # Scan all specified directories
    for rel_dir in SCAN_DIRS:
        abs_dir = base_dir / rel_dir
        if not abs_dir.exists():
            logger.warning(f"Directory not found: {abs_dir}")
            continue
            
        logger.info(f"Scanning directory: {abs_dir}")
        
        for root, dirs, files in os.walk(abs_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not should_skip_directory(d)]
            
            # Scan Python files
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                filepath = os.path.join(root, file)
                matches = scan_file(filepath)
                
                if matches:
                    logger.info(f"Found {len(matches)} memory operations in {os.path.relpath(filepath, base_dir)}")
                    results.extend(matches)
    
    # Generate report
    if not results:
        logger.info("No memory operations found.")
        return
    
    report_path = base_dir / 'memory_operations_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Memory Operations Report\n\n")
        f.write(f"Found {len(results)} memory operations that may need migration.\n\n")
        
        # Group by file
        files = {}
        for result in results:
            if result['file'] not in files:
                files[result['file']] = []
            files[result['file']].append(result)
        
        # Write report by file
        for file_path, ops in files.items():
            rel_path = os.path.relpath(file_path, base_dir)
            f.write(f"\n## File: {rel_path}\n\n")
            
            for op in sorted(ops, key=lambda x: x['line']):
                f.write(f"Line {op['line']}: {op['pattern']}\n")
                f.write(f"  {op['code']}\n\n")
    
    logger.info(f"\nReport generated: {report_path}")
    logger.info(f"Total memory operations found: {len(results)}")

if __name__ == "__main__":
    main()
