#!/usr/bin/env python3
"""
Agent Model Analysis Script

This script analyzes and compares agent-related models to ensure agent_memory_banks.py
properly covers all necessary functionality from other agent models.
"""
import os
import re
import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Define the project root and models directory
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "app" / "models"

# Files to analyze (excluding the ones you mentioned)
EXCLUDED_FILES = {
    'alerts.py', 'metrics_aggregation.py', 'metrics.py', 
    'system.py', 'tuning_history.py', 'user.py', '__init__.py',
    'agent_memory.legacy.py'  # Excluding legacy files
}

class ModelAnalyzer(ast.NodeVisitor):
    """AST visitor to extract table and column information from SQLAlchemy models."""
    
    def __init__(self):
        self.tables = {}
        self.current_class = None
        
    def visit_ClassDef(self, node):
        # Check if this is a SQLAlchemy model (has __tablename__ or inherits from Base)
        is_model = any(
            isinstance(base, ast.Name) and base.id == 'Base' 
            for base in node.bases
        )
        
        if not is_model:
            return
            
        self.current_class = node.name
        self.tables[self.current_class] = {
            'name': None,
            'columns': {},
            'relationships': []
        }
        
        # Process class body
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                self.visit_AnnAssign(item)
            elif isinstance(item, ast.Assign):
                self.visit_Assign(item)
                
        self.current_class = None
        
    def visit_Assign(self, node):
        # Look for __tablename__ assignments
        if (isinstance(node.targets[0], ast.Name) and 
            node.targets[0].id == '__tablename__' and 
            isinstance(node.value, ast.Str)):
            if self.current_class in self.tables:
                self.tables[self.current_class]['name'] = node.value.s
    
    def visit_AnnAssign(self, node):
        if not self.current_class or not node.target or not hasattr(node.target, 'id'):
            return
            
        column_name = node.target.id
        
        # Skip non-column attributes
        if not (isinstance(node.annotation, ast.Call) and 
               isinstance(node.annotation.func, ast.Name) and 
               node.annotation.func.id == 'Column'):
            return
            
        # Extract column type and arguments
        column_type = 'Unknown'
        args = []
        
        for kw in node.annotation.keywords:
            if kw.arg == 'type_':
                if isinstance(kw.value, ast.Name):
                    column_type = kw.value.id
            elif kw.arg == 'type':
                if isinstance(kw.value, ast.Name):
                    column_type = kw.value.id
            
        self.tables[self.current_class]['columns'][column_name] = {
            'type': column_type,
            'nullable': True  # Default, can be updated by visiting more nodes
        }

def analyze_file(file_path: Path) -> Dict:
    """Analyze a single Python file and extract model information."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        analyzer = ModelAnalyzer()
        analyzer.visit(tree)
        return analyzer.tables
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {}

def compare_models():
    """Compare agent_memory_banks.py with other agent-related models."""
    all_models = {}
    
    # First, collect all model information
    for model_file in MODELS_DIR.glob("*.py"):
        if model_file.name in EXCLUDED_FILES:
            continue
            
        models = analyze_file(model_file)
        if models:
            all_models[model_file.name] = models
    
    # Separate agent_memory_banks from other models
    memory_banks = all_models.pop('agent_memory_banks.py', {})
    agent_models = all_models
    
    # Compare tables and columns
    report = {
        'memory_bank_tables': set(),
        'agent_tables': set(),
        'missing_tables': set(),
        'missing_columns': defaultdict(dict),
        'coverage': 0.0
    }
    
    # Collect all table names
    for model_name, models_dict in agent_models.items():
        for class_name, table_info in models_dict.items():
            if isinstance(table_info, dict) and 'name' in table_info and table_info['name']:
                report['agent_tables'].add(table_info['name'])
    
    for model_name, models_dict in memory_banks.items():
        for class_name, table_info in models_dict.items():
            if isinstance(table_info, dict) and 'name' in table_info and table_info['name']:
                report['memory_bank_tables'].add(table_info['name'])
    
    # Find missing tables
    report['missing_tables'] = report['agent_tables'] - report['memory_bank_tables']
    
    # Calculate coverage
    if report['agent_tables']:
        report['coverage'] = (
            (len(report['memory_bank_tables']) - len(report['missing_tables'])) / 
            len(report['agent_tables']) * 100
        )
    
    # Generate a markdown report
    with open('agent_model_analysis.md', 'w', encoding='utf-8') as f:
        f.write("# Agent Model Analysis Report\n\n")
        f.write("## Coverage Summary\n")
        f.write(f"- **Total Agent Tables:** {len(report['agent_tables'])}\n")
        f.write(f"- **Tables in Memory Banks:** {len(report['memory_bank_tables'])}\n")
        f.write(f"- **Missing Tables:** {len(report['missing_tables'])}\n")
        f.write(f"- **Coverage:** {report['coverage']:.2f}%\n\n")
        
        if report['missing_tables']:
            f.write("## Missing Tables\n")
            for table in sorted(report['missing_tables']):
                f.write(f"- {table}\n")
            f.write("\n")
        
        f.write("## Detailed Table Comparison\n")
        for model_file, models_dict in agent_models.items():
            for class_name, table_info in models_dict.items():
                if not isinstance(table_info, dict) or not table_info.get('name'):
                    continue
                    
                f.write(f"### Table: {table_info['name']} (from {model_file})\n")
                f.write("| Column | Type | In Memory Banks |\n")
                f.write("|--------|------|------------------|\n")
                
                for col_name, col_info in table_info.get('columns', {}).items():
                    in_memory = False
                    for mb_models in memory_banks.values():
                        for mb_class, mb_table in mb_models.items():
                            if (isinstance(mb_table, dict) and 
                                'columns' in mb_table and 
                                col_name in mb_table['columns']):
                                in_memory = True
                                break
                        if in_memory:
                            break
                    
                    f.write(f"| `{col_name}` | {col_info.get('type', 'Unknown')} | {'✅' if in_memory else '❌'} |\n")
                
                f.write("\n")
    
    print(f"Analysis complete. Report saved to 'agent_model_analysis.md'")

if __name__ == "__main__":
    compare_models()
