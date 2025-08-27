#!/usr/bin/env python3
"""
Agent Memory Coverage Analyzer

This script analyzes the coverage of agent memory banks compared to individual agent models.
It identifies what's properly captured in memory and what might be missing.
"""
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import json
from collections import defaultdict

# Define paths
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "app" / "models"

# Core agent names
CORE_AGENTS = {
    'sir_hawkington': 'Triage and monitoring',
    'meth_snail': 'Performance optimization',
    'hamsters': 'Infrastructure management',
    'quantum_shadow_people': 'Security and anomalies',
    'vic20': 'Coordination and wisdom',
    'the_stick': 'Memory and safety'
}

# Concept categories to track
CONCEPT_CATEGORIES = [
    'triage_decisions',
    'optimizations',
    'infrastructure',
    'security',
    'coordination',
    'learning_patterns',
    'user_interactions',
    'system_metrics',
    'anomalies',
    'safety_features'
]

class AgentModelAnalyzer:
    """Analyzes agent models and their memory coverage."""
    
    def __init__(self):
        self.agent_models = {}
        self.memory_bank_schema = {}
        self.concept_coverage = {
            agent: {category: {
                'concepts': set(),
                'in_memory': set(),
                'not_in_memory': set()
            } for category in CONCEPT_CATEGORIES}
            for agent in CORE_AGENTS
        }
    
    def analyze(self):
        """Run the full analysis."""
        print("Analyzing agent models and memory banks...")
        self._load_agent_models()
        self._analyze_memory_banks()
        self._generate_coverage_report()
        print("Analysis complete. Check 'memory_coverage_report.md' for results.")
    
    def _load_agent_models(self):
        """Load and analyze all agent models."""
        for agent in CORE_AGENTS:
            model_file = MODELS_DIR / f"{agent}_model.py"
            if not model_file.exists():
                print(f"Warning: No model file found for agent {agent}")
                continue
            
            print(f"Analyzing {model_file.name}...")
            self.agent_models[agent] = self._extract_model_concepts(model_file)
    
    def _extract_model_concepts(self, model_path: Path) -> Dict[str, Any]:
        """Extract concepts and data structures from an agent model."""
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        concepts = {
            'tables': set(),
            'columns': defaultdict(set),
            'relationships': [],
            'methods': set()
        }
        
        try:
            tree = ast.parse(content)
            
            # Find all classes and their attributes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    table_name = None
                    for item in node.body:
                        # Find table name
                        if (isinstance(item, ast.Assign) and 
                            len(item.targets) == 1 and 
                            isinstance(item.targets[0], ast.Name) and 
                            item.targets[0].id == '__tablename__' and
                            isinstance(item.value, ast.Str)):
                            table_name = item.value.s
                            concepts['tables'].add(table_name)
                        
                        # Find columns
                        if (isinstance(item, ast.AnnAssign) and 
                            isinstance(item.target, ast.Name)):
                            col_name = item.target.id
                            concepts['columns'][table_name].add(col_name)
                            
                            # Check for relationships
                            if (isinstance(item.annotation, ast.Call) and
                                isinstance(item.annotation.func, ast.Name) and
                                item.annotation.func.id in ['relationship']):
                                concepts['relationships'].append({
                                    'table': table_name,
                                    'column': col_name,
                                    'type': 'relationship'
                                })
                        
                        # Find methods
                        if isinstance(item, ast.FunctionDef):
                            concepts['methods'].add(item.name)
            
            return concepts
            
        except Exception as e:
            print(f"Error analyzing {model_path}: {e}")
            return concepts
    
    def _analyze_memory_banks(self):
        """Analyze the memory bank structure."""
        memory_bank_file = MODELS_DIR / "agent_memory_banks.py"
        if not memory_bank_file.exists():
            print("Error: agent_memory_banks.py not found")
            return
        
        print(f"Analyzing {memory_bank_file.name}...")
        with open(memory_bank_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and hasattr(node, 'bases'):
                    # Check if this is a SQLAlchemy model
                    if any(isinstance(base, ast.Name) and base.id == 'Base' 
                          for base in node.bases):
                        self._process_memory_class(node)
        except Exception as e:
            print(f"Error parsing memory bank: {e}")
    
    def _process_memory_class(self, node: ast.ClassDef):
        """Process a memory bank class definition."""
        table_info = {
            'name': None,
            'columns': set(),
            'relationships': []
        }
        
        # Find table name and columns
        for item in node.body:
            # Table name
            if (isinstance(item, ast.Assign) and 
                len(item.targets) == 1 and 
                isinstance(item.targets[0], ast.Name) and 
                item.targets[0].id == '__tablename__' and
                isinstance(item.value, ast.Str)):
                table_info['name'] = item.value.s
            
            # Columns
            if (isinstance(item, ast.AnnAssign) and 
                isinstance(item.target, ast.Name)):
                col_name = item.target.id
                table_info['columns'].add(col_name)
                
                # Check for relationships
                if (isinstance(item.annotation, ast.Call) and
                    isinstance(item.annotation.func, ast.Name) and
                    item.annotation.func.id in ['relationship']):
                    table_info['relationships'].append({
                        'column': col_name,
                        'type': 'relationship'
                    })
        
        if table_info['name']:
            self.memory_bank_schema[table_info['name']] = table_info
    
    def _generate_coverage_report(self):
        """Generate a markdown report of the analysis."""
        report = "# Agent Memory Coverage Analysis\n\n"
        
        # Summary of findings
        report += "## Summary\n\n"
        report += "This report analyzes the coverage of agent memories in the memory bank system.\n\n"
        
        # Memory bank schema
        report += "## Memory Bank Schema\n\n"
        for table_name, table_info in self.memory_bank_schema.items():
            report += f"### {table_name}\n"
            report += f"**Columns:** {', '.join(sorted(table_info['columns']))}\n\n"
            if table_info['relationships']:
                rels = [f"{r['column']} ({r['type']})" 
                       for r in table_info['relationships']]
                report += f"**Relationships:** {', '.join(rels)}\n\n"
        
        # Agent model coverage
        report += "## Agent Model Coverage\n\n"
        for agent, concepts in self.agent_models.items():
            report += f"### {agent.replace('_', ' ').title()}\n"
            report += f"**Tables:** {', '.join(concepts['tables'])}\n\n"
            
            # Check coverage for each table
            for table in concepts['tables']:
                report += f"#### Table: {table}\n"
                if table in self.memory_bank_schema:
                    report += "✅ Found in memory banks\n"
                    # Check column coverage
                    missing_cols = []
                    for col in concepts['columns'].get(table, []):
                        if col not in self.memory_bank_schema[table]['columns']:
                            missing_cols.append(col)
                    if missing_cols:
                        report += f"❌ Missing columns: {', '.join(missing_cols)}\n"
                else:
                    report += "❌ Not found in memory banks\n"
                report += "\n"
            
            # Check methods for important concepts
            report += "#### Key Methods/Concepts\n"
            for method in sorted(concepts['methods']):
                # This is a simplified check - in a real analysis, you'd want to 
                # look at the method implementation for important concepts
                report += f"- {method}\n"
            report += "\n"
        
        # Save the report
        with open('memory_coverage_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

if __name__ == "__main__":
    analyzer = AgentModelAnalyzer()
    analyzer.analyze()