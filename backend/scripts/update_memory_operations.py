#!/usr/bin/env python3
"""
Memory Operations Updater

This script helps migrate direct database operations to use the new MemoryService.
It scans the codebase for database operations and suggests replacements.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memory_operations_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Common patterns to identify memory-related operations
MEMORY_PATTERNS = {
    'session.add': r'session\.add\(([^)]+)\)',
    'session.add_all': r'session\.add_all\(([^)]+)\)',
    'session.query': r'session\.query\(([^)]+)\)',
    'session.execute': r'session\.execute\(([^)]+)\)',
    'select': r'select\(([^)]+)\)',
    'insert': r'insert\(([^)]+)\)',
    'update': r'update\(([^)]+)\)',
    'delete': r'delete\(([^)]+)\)',
}

# Models and patterns that indicate memory operations
MEMORY_RELATED_PATTERNS = [
    # Model classes
    'Memory', 'AgentMemory', 'UserMemory', 'SystemMemory', 'EventMemory',
    'VIC20CoordinationLog', 'VIC20SystemSynthesis', 'VIC20AgentHarmony',
    'VIC20PartnershipMetrics', 'VIC20DecisionOrchestration', 'StickMemory',
    'StickAnxietyLog', 'StickEncounter', 'StickPaperBagUsage', 'StickMemoryEntry',
    'MemoryBank', 'MemoryStore', 'MemoryRecord',
    
    # Common method names
    'store_memory', 'retrieve_memory', 'create_memory', 'get_memory',
    'update_memory', 'delete_memory', 'save_memory', 'load_memory',
    'remember', 'recall', 'persist', 'store', 'retrieve',
    
    # Common variable names
    'memory_', '_memory', 'mem_', '_mem', 'memories', 'cache', 'storage'
]

class MemoryOperationAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze memory-related operations."""
    
    def __init__(self):
        self.memory_operations = []
        self.imports = {}
        self.current_file = ""
        self.current_class = None
    
    def visit_Import(self, node):
        for name in node.names:
            self.imports[name.name] = name.asname or name.name.split('.')[-1]
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for name in node.names:
            full_name = f"{node.module}.{name.name}" if node.module else name.name
            self.imports[name.name] = name.asname or name.name
        self.generic_visit(node)
    
    def visit_Call(self, node):
        try:
            # Get the full line of code
            with open(self.current_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                line = lines[node.lineno - 1].strip()
            
            # Check for session operations
            if (isinstance(node.func, ast.Attribute) and 
                isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'session' and 
                node.func.attr in ['add', 'add_all', 'query', 'execute', 'commit', 'delete']):
                
                # Check if this is a memory-related operation
                if any(pattern.lower() in line.lower() for pattern in MEMORY_RELATED_PATTERNS):
                    self.memory_operations.append({
                        'file': self.current_file,
                        'line': node.lineno,
                        'col': node.col_offset,
                        'operation': f'session.{node.func.attr}',
                        'code': line,
                        'context': {
                            'class': self.current_class,
                            'imports': dict(self.imports)
                        }
                    })
            
            # Check for direct model instantiation or method calls
            elif isinstance(node.func, (ast.Name, ast.Attribute)):
                func_name = ''
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"
                
                if any(pattern.lower() in func_name.lower() for pattern in MEMORY_RELATED_PATTERNS):
                    self.memory_operations.append({
                        'file': self.current_file,
                        'line': node.lineno,
                        'col': node.col_offset,
                        'operation': func_name,
                        'code': line,
                        'context': {
                            'class': self.current_class,
                            'imports': dict(self.imports)
                        }
                    })
                    
        except Exception as e:
            logger.warning(f"Error processing {self.current_file}:{node.lineno}: {e}")
            
        self.generic_visit(node)
        
        self.generic_visit(node)

def scan_directory(directory: str) -> List[Dict]:
    """Scan a directory for Python files and analyze them for memory operations."""
    directory = Path(directory)
    analyzer = MemoryOperationAnalyzer()
    
    # Skip these directories
    skip_dirs = {'__pycache__', '.git', 'venv', '.venv', 'migrations', 'tests'}
    
    for root, dirs, files in os.walk(directory):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            analyzer.current_file = file_path
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip empty or very small files
                if len(content.strip()) < 10:
                    continue
                
                # Quick check before parsing
                if not any(pattern.lower() in content.lower() for pattern in MEMORY_RELATED_PATTERNS):
                    continue
                
                # Parse the file
                tree = ast.parse(content, filename=file_path)
                analyzer.visit(tree)
                
            except Exception as e:
                logger.warning(f"Error parsing {file_path}: {e}")
    
    return analyzer.memory_operations

def generate_migration_report(operations: List[Dict]) -> str:
    """Generate a report of memory operations that need to be migrated."""
    if not operations:
        return "No memory operations found that need migration."
    
    report = ["# Memory Operations Migration Report\n"]
    
    # Group by file
    files = {}
    for op in operations:
        if op['file'] not in files:
            files[op['file']] = []
        files[op['file']].append(op)
    
    # Generate report by file
    for file_path, ops in files.items():
        report.append(f"## File: {file_path}\n")
        
        for op in ops:
            # Suggest replacement based on operation type
            replacement = ""
            if op['operation'] in ['session.add', 'session.add_all']:
                replacement = f"# TODO: Replace with MemoryService.store_memory()\n"
                replacement += f"# Example: \n"
                replacement += f"# from app.services.memory import MemoryService\n"
                replacement += f"# memory_service = MemoryService()\n"
                replacement += f"# await memory_service.store_memory(\n"
                replacement += f"#     agent_name='agent_name',\n"
                replacement += f"#     event_type='event_type',\n"
                replacement += f"#     user_id='user_id',\n"
                replacement += f"#     content={{'data': 'your_data'}}\n"
                replacement += f"# )"
                
            elif op['operation'] in ['session.query', 'session.execute']:
                replacement = f"# TODO: Replace with MemoryService.retrieve_memory()\n"
                replacement += f"# Example: \n"
                replacement += f"# from app.services.memory import MemoryService\n"
                replacement += f"# memory_service = MemoryService()\n"
                replacement += f"# memories = await memory_service.retrieve_memory(\n"
                replacement += f"#     agent_name='agent_name',\n"
                replacement += f"#     event_type='event_type',\n"
                replacement += f"#     user_id='user_id'\n"
                replacement += f"# )"
            
            report.append(f"### Line {op['line']}: {op['operation']} ({op['model']})\n")
            report.append(f"```python\n{op['code']}\n```\n")
            report.append(f"**Suggested replacement:**\n")
            report.append(f"```python\n{replacement}\n```\n")
            report.append("---\n")
    
    return "\n".join(report)

def main():
    """Main function to run the memory operations scanner."""
    # Scan the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    operations = scan_directory(backend_dir)
    
    # Generate and save the report
    report = generate_migration_report(operations)
    report_path = os.path.join(os.path.dirname(__file__), 'memory_migration_report.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Memory operations scan complete. Report saved to: {report_path}")
    logger.info(f"Found {len(operations)} memory operations that may need migration.")

if __name__ == "__main__":
    main()
