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

# Core agent names and their roles
CORE_AGENTS = {
    'sir_hawkington': 'Triage and monitoring',
    'meth_snail': 'Performance optimization',
    'hamsters': 'Infrastructure management',
    'quantum_shadow_people': 'Security and anomalies',
    'vic20': 'Coordination and wisdom',
    'the_stick': 'Memory and safety'
}

class AgentModelAnalyzer:
    """Analyzes agent models and their memory coverage."""
    
    def __init__(self):
        self.agent_models = {}
        self.memory_bank_schema = {}
    
    def analyze(self):
        """Run the full analysis."""
        print("Analyzing agent models and memory banks...")
        self._load_agent_models()
        self._analyze_memory_banks()
        self._generate_coverage_report()
        print("Analysis complete. Check 'memory_coverage_report.md' for results.")
    
    def _load_agent_models(self):
        """Load and analyze all agent models."""
        agent_files = {
            'sir_hawkington': 'sir_hawkington_model.py',
            'meth_snail': 'meth_snail_model.py',
            'hamsters': 'hamsters_model.py',
            'quantum_shadow_people': 'qsp_models.py',
            'vic20': 'vic20_sage_model.py',
            'the_stick': 'the_stick_model.py'
        }
        
        for agent, filename in agent_files.items():
            model_file = MODELS_DIR / filename
            if not model_file.exists():
                print(f"Warning: No model file found for agent {agent} at {model_file}")
                continue
            
            print(f"Analyzing {model_file.name}...")
            self.agent_models[agent] = self._extract_model_concepts(model_file)
    
    def _infer_table_purpose(self, table_name: str, columns: set) -> str:
        """Infer the purpose of a table based on its name and columns."""
        name_lower = table_name.lower()
        cols_lower = [c.lower() for c in columns]
        
        # Check for common patterns
        if any(x in name_lower for x in ['log', 'history', 'record']):
            return "Appears to be an activity log or history table"
            
        if any(x in name_lower for x in ['config', 'setting', 'profile']):
            return "Appears to be a configuration or settings table"
            
        if any(x in name_lower for x in ['stats', 'metric', 'measure']):
            return "Appears to store metrics or statistics"
            
        # Check column patterns
        if any('timestamp' in c or 'created_at' in c for c in cols_lower):
            if any('status' in c or 'state' in c for c in cols_lower):
                return "Likely a status tracking table with timestamps"
            return "Contains timestamped records"
            
        if any('user_id' in c or 'agent_id' in c for c in cols_lower):
            return "Contains user or agent-specific data"
            
        return "Purpose not immediately clear from name and columns"
        
    def _extract_model_concepts(self, model_path: Path) -> Dict[str, Any]:
        """Extract concepts and data structures from an agent model."""
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        concepts = {
            'tables': set(),
            'columns': defaultdict(set),
            'relationships': [],
            'methods': set(),
            'method_details': {},
            'table_descriptions': {}
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
                        
                        # Find methods and their docstrings
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'docstring': ast.get_docstring(item) or "No docstring",
                                'args': [arg.arg for arg in item.args.args if arg.arg != 'self'],
                                'decorators': [d.id for d in item.decorator_list if hasattr(d, 'id')]
                            }
                            concepts['methods'].add(item.name)
                            concepts['method_details'] = concepts.get('method_details', {})
                            concepts['method_details'][item.name] = method_info
            
            return concepts
            
        except Exception as e:
            print(f"Error analyzing {model_path}: {e}")
            return concepts
    
    def _find_semantic_matches(self, table_name: str, table_columns: set) -> List[Dict[str, Any]]:
        """Find semantically similar tables in memory banks.
        
        Args:
            table_name: Name of the table to find matches for
            table_columns: Set of column names in the table
            
        Returns:
            List of potential matches with their similarity scores
        """
        # First check for agent-specific memory banks
        agent_mapping = {
            'hawkington': 'sir_hawkington_memory_bank',
            'meth_snail': 'meth_snail_memory_bank',
            'hamsters': 'hamsters_memory_bank',
            'qsp': 'quantum_shadow_people_memory_bank',
            'vic20': 'vic20_memory_bank'
        }
        
        # Check if this is an agent-specific table
        for agent_prefix, mem_bank in agent_mapping.items():
            if table_name.startswith(agent_prefix):
                # This is an agent-specific table, map to their memory bank
                return [{
                    'table': mem_bank,
                    'common_terms': agent_prefix,
                    'column_overlap': '100%',
                    'score': '100%',
                    'mapping_type': 'agent_memory_bank'
                }]
        
        # Convert to lowercase and split into words
        def get_keywords(name):
            # Remove common suffixes/prefixes and split into words
            name = name.lower()
            for suffix in ['_table', '_model', '_log', '_stats', '_metrics', '_memory_bank']:
                if name.endswith(suffix):
                    name = name[:-len(suffix)]
            return set(word for word in name.split('_') if word and len(word) > 2)
            
        table_keywords = get_keywords(table_name)
        matches = []
        
        # Also check for column name patterns that might indicate purpose
        purpose_indicators = {
            'user': any('user' in col.lower() for col in table_columns),
            'time': any('time' in col.lower() or 'date' in col.lower() or 'timestamp' in col.lower() for col in table_columns),
            'status': any('status' in col.lower() or 'state' in col.lower() for col in table_columns),
            'metric': any(col.lower() in ['count', 'total', 'score', 'value', 'amount', 'quantity'] for col in table_columns),
            'log': any('log' in col.lower() or 'history' in col.lower() for col in table_columns)
        }
        
        for mem_table_name, mem_table in self.memory_bank_schema.items():
            # Central memory bank can contain any type of data
            if mem_table_name == 'central_memory_bank':
                matches.append({
                    'table': mem_table_name,
                    'common_terms': 'central',
                    'column_overlap': '50%',
                    'score': '80%',
                    'mapping_type': 'central_memory_bank'
                })
                continue
                
            # Skip system tables not meant for direct agent data
            if mem_table_name in ['agent_learning_interactions', 
                                'user_learning_patterns', 
                                'memory_bank_metadata']:
                continue
                
            mem_keywords = get_keywords(mem_table_name)
            
            # Check for direct word matches
            common_terms = table_keywords.intersection(mem_keywords)
            if not common_terms:
                continue
                
            # Calculate column overlap
            mem_columns = set(mem_table['columns'].keys())
            column_overlap = len(table_columns.intersection(mem_columns)) / max(1, len(table_columns))
            
            # Check purpose indicators
            purpose_score = 0
            mem_columns_lower = [c.lower() for c in mem_columns]
            for purpose, has_purpose in purpose_indicators.items():
                if has_purpose and any(purpose in c for c in mem_columns_lower):
                    purpose_score += 0.2
            
            # Calculate overall score (weighted average)
            keyword_score = len(common_terms) / max(len(table_keywords), len(mem_keywords))
            score = (keyword_score * 0.6) + (column_overlap * 0.3) + (purpose_score * 0.1)
            
            if score > 0.3:  # Only include reasonably good matches
                # Check if this is a log/audit table
                is_log_table = any(x in table_name.lower() for x in ['log', 'history', 'audit'])
                
                matches.append({
                    'table': mem_table_name,
                    'common_terms': ', '.join(common_terms),
                    'column_overlap': f"{int(column_overlap * 100)}%",
                    'score': f"{int(score * 100)}%",
                    'mapping_type': 'semantic_match',
                    'is_log_table': is_log_table
                })
        
        # Sort by score (highest first)
        return sorted(matches, key=lambda x: float(x['score'].rstrip('%')), reverse=True)
    
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
            'docstring': ast.get_docstring(node) or "No docstring",
            'columns': {},
            'relationships': []
        }
        
        # Find table name and columns
        for item in node.body:
            # Skip non-relevant nodes early
            if not isinstance(item, (ast.Assign, ast.AnnAssign)):
                continue
                
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
                col_type = "Unknown"
                
                # Try to extract column type
                if isinstance(item.annotation, ast.Name):
                    col_type = item.annotation.id
                elif (isinstance(item.annotation, ast.Subscript) and 
                      isinstance(item.annotation.value, ast.Name)):
                    col_type = item.annotation.value.id
                    if hasattr(item.annotation, 'slice') and hasattr(item.annotation.slice, 'value'):
                        col_type += f"[{item.annotation.slice.value.id}]"
                
                # Get column attributes
                col_attrs = {}
                if hasattr(item, 'value'):
                    if isinstance(item.value, ast.Call):
                        for kw in item.value.keywords:
                            if isinstance(kw.value, (ast.Name, ast.Constant)):
                                col_attrs[kw.arg] = getattr(kw.value, 'id', getattr(kw.value, 'value', str(kw.value)))
                
                table_info['columns'][col_name] = {
                    'type': col_type,
                    'attrs': col_attrs,
                    'docstring': ast.get_docstring(item) or ""
                }
                
                # Check for relationships
                if (isinstance(item.annotation, ast.Call) and
                    isinstance(item.annotation.func, ast.Name) and
                    item.annotation.func.id in ['relationship']):
                    rel_info = {
                        'column': col_name,
                        'type': 'relationship',
                        'target': None,
                        'backref': None
                    }
                    # Extract relationship details
                    for kw in item.annotation.keywords:
                        if kw.arg == 'backref':
                            rel_info['backref'] = kw.value.value if isinstance(kw.value, ast.Str) else str(kw.value)
                        elif kw.arg == 'foreign_keys':
                            # Handle foreign key references
                            if isinstance(kw.value, ast.List) and kw.value.elts:
                                rel_info['target'] = kw.value.elts[0].value if hasattr(kw.value.elts[0], 'value') else str(kw.value.elts[0])
                    
                    table_info['relationships'].append(rel_info)
        
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
            if table_info['docstring']:
                report += f"*{table_info['docstring']}*\n\n"
            
            if table_info['columns']:
                report += "#### Columns\n"
                report += "| Column | Type | Attributes | Description |\n"
                report += "|--------|------|------------|-------------|\n"
                for col_name, col_info in sorted(table_info['columns'].items()):
                    attrs = ", ".join([f"{k}={v}" for k, v in col_info['attrs'].items()])
                    report += f"| `{col_name}` | {col_info['type']} | {attrs} | {col_info['docstring']} |\n"
                report += "\n"
            
            if table_info['relationships']:
                report += "#### Relationships\n"
                for rel in table_info['relationships']:
                    target = rel.get('target', 'Unknown')
                    backref = f", backref='{rel['backref']}'" if rel.get('backref') else ""
                    report += f"- `{rel['column']}` → `{target}`{backref}\n"
                report += "\n"
        
        # Agent model coverage
        report += "## Agent Model Coverage\n\n"
        for agent, concepts in self.agent_models.items():
            report += f"### {agent.replace('_', ' ').title()}\n"
            report += f"**Tables:** {', '.join(concepts['tables'])}\n\n"
            
            # Check coverage for each table
            for table in concepts['tables']:
                report += f"#### Table: {table}\n"
                
                # Get table columns for semantic matching
                table_columns = set(concepts['columns'].get(table, []))
                
                # Check for exact match first
                if table in self.memory_bank_schema:
                    # Check for missing columns
                    missing_cols = []
                    for col in table_columns:
                        if col not in self.memory_bank_schema[table]['columns']:
                            missing_cols.append(col)
                    if missing_cols:
                        report += f"⚠️ Found with missing columns: {', '.join(missing_cols)}\n"
                    else:
                        report += "✅ Exact match found in memory banks\n"
                else:
                    # Look for semantic matches
                    semantic_matches = self._find_semantic_matches(table, table_columns)
                    if semantic_matches:
                        # Group by match type first
                        matches_by_type = {}
                        for match in semantic_matches:
                            match_type = match.get('mapping_type', 'semantic')
                            if match_type not in matches_by_type:
                                matches_by_type[match_type] = []
                            matches_by_type[match_type].append(match)
                        
                        report += "🔍 Possible mappings to memory banks:\n"
                        
                        # 1. Show direct agent memory bank mappings first
                        if 'agent_memory_bank' in matches_by_type:
                            for match in matches_by_type['agent_memory_bank']:
                                report += (f"  - 🎯 **Direct mapping to {match['table']}**\n"
                                          f"    - This table's data should be stored in the agent's memory bank\n"
                                          f"    - Consider migrating data to {match['table']}\n")
                        
                        # 2. Show central memory bank mappings
                        if 'central_memory_bank' in matches_by_type:
                            for match in matches_by_type['central_memory_bank']:
                                report += (f"  - 🌐 **Suitable for Central Memory Bank**\n"
                                          f"    - This appears to be shared learning data\n"
                                          f"    - Consider migrating to {match['table']}\n")
                        
                        # 3. Show other semantic matches
                        if 'semantic_match' in matches_by_type:
                            # Group by memory bank for better organization
                            matches_by_bank = {}
                            for match in matches_by_type['semantic_match']:
                                bank_name = match['table'].split('_memory_bank')[0] if '_memory_bank' in match['table'] else 'Other'
                                if bank_name not in matches_by_bank:
                                    matches_by_bank[bank_name] = []
                                matches_by_bank[bank_name].append(match)
                            
                            for bank_name, matches in matches_by_bank.items():
                                report += f"  - 🔍 **Possible {bank_name.title()} Memory Bank Matches**:\n"
                                for match in matches[:3]:  # Top 3 matches per bank
                                    report += (f"    - `{match['table']}` "
                                              f"(Score: {match['score']}, "
                                              f"Common terms: {match['common_terms']})\n")
                        
                        # 4. Special handling for log/audit tables
                        if any(m.get('is_log_table', False) for m in semantic_matches):
                            report += ("\n  📝 **Note**: This appears to be a log or audit table. "
                                      "Consider if this data needs to be in the memory system or "
                                      "if it should remain in the application database.\n")
                    else:
                        report += "❌ No clear match found in memory banks\n"
                        # Check if this appears to be a new concept
                        report += "\n**Analysis of missing table:**\n"
                        report += f"- **Purpose**: {self._infer_table_purpose(table, table_columns)}\n"
                        report += "\n**Suggested actions**:\n"
                        if 'log' in table.lower() or 'history' in table.lower():
                            report += "- Consider adding to the appropriate agent's memory bank as a log table\n"
                        if 'config' in table.lower() or 'profile' in table.lower():
                            report += "- Consider adding to the appropriate agent's memory bank as a configuration table\n"
                        report += "- Review if this table's data should be part of the central memory bank\n"
                        
                report += "\n"
            
            # Report key methods and their purposes
            if 'method_details' in concepts and concepts['method_details']:
                report += "#### Key Methods and Concepts\n"
                # Group methods by category based on name patterns
                categories = {
                    'Data Processing': [],
                    'Decision Making': [],
                    'Memory Operations': [],
                    'Monitoring': [],
                    'Utility': []
                }
                
                # Categorize methods
                for method_name, details in concepts['method_details'].items():
                    method_desc = f"**{method_name}**"
                    if details['args']:
                        method_desc += f"({', '.join(details['args'])})"
                    if details['docstring']:
                        first_line = details['docstring'].split('\n')[0]
                        method_desc += ": " + first_line
                    
                    # Simple categorization based on method name patterns
                    if any(term in method_name.lower() for term in ['process', 'transform', 'parse']):
                        categories['Data Processing'].append(method_desc)
                    elif any(term in method_name.lower() for term in ['decide', 'evaluate', 'judge', 'triage']):
                        categories['Decision Making'].append(method_desc)
                    elif any(term in method_name.lower() for term in ['save', 'load', 'recall', 'remember']):
                        categories['Memory Operations'].append(method_desc)
                    elif any(term in method_name.lower() for term in ['monitor', 'check', 'inspect', 'scan']):
                        categories['Monitoring'].append(method_desc)
                    else:
                        categories['Utility'].append(method_desc)
                
                # Add categorized methods to report
                for category, methods in categories.items():
                    if methods:
                        report += f"- **{category}**\n"
                        for method in sorted(methods):
                            report += f"  - {method}\n"
                report += "\n"
        
        # Save the report
        with open('memory_coverage_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

if __name__ == "__main__":
    analyzer = AgentModelAnalyzer()
    analyzer.analyze()
