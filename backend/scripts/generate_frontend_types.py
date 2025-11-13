#!/usr/bin/env python3
"""
Generate TypeScript types from Python dataclasses and Pydantic models.

This script parses Python source files to extract dataclass and Pydantic model
definitions and generates corresponding TypeScript interfaces.

Usage:
    python scripts/generate_frontend_types.py

Output:
    frontend/src/types/backend-generated.ts
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


class TypeScriptGenerator:
    """Generate TypeScript types from Python type annotations."""
    
    # Python to TypeScript type mapping
    TYPE_MAP = {
        'str': 'string',
        'int': 'number',
        'float': 'number',
        'bool': 'boolean',
        'datetime': 'string',  # ISO datetime string
        'date': 'string',
        'Any': 'any',
        'None': 'null',
        'dict': 'Record<string, any>',
        'list': 'any[]',
    }
    
    def __init__(self):
        self.imports: Set[str] = set()
        self.enums: Dict[str, List[str]] = {}
        self.interfaces: Dict[str, str] = {}
        
    def convert_type(self, type_annotation: str) -> str:
        """Convert Python type annotation to TypeScript type."""
        if not type_annotation:
            return 'any'
        
        # Handle Optional[T] -> T | null
        optional_match = re.match(r'Optional\[(.*)\]', type_annotation)
        if optional_match:
            inner_type = self.convert_type(optional_match.group(1))
            return f'{inner_type} | null'
        
        # Handle List[T] -> T[]
        list_match = re.match(r'List\[(.*)\]', type_annotation)
        if list_match:
            inner_type = self.convert_type(list_match.group(1))
            return f'{inner_type}[]'
        
        # Handle Dict[K, V] -> Record<K, V>
        dict_match = re.match(r'Dict\[(.*),\s*(.*)\]', type_annotation)
        if dict_match:
            key_type = self.convert_type(dict_match.group(1))
            value_type = self.convert_type(dict_match.group(2))
            return f'Record<{key_type}, {value_type}>'
        
        # Direct mapping
        return self.TYPE_MAP.get(type_annotation, type_annotation)
    
    def parse_dataclass(self, node: ast.ClassDef, source_file: str) -> Optional[str]:
        """Parse a Python dataclass and generate TypeScript interface."""
        # Check if it's a dataclass
        has_dataclass = any(
            isinstance(dec, ast.Name) and dec.id == 'dataclass'
            for dec in node.decorator_list
        )
        
        if not has_dataclass:
            return None
        
        fields: List[Tuple[str, str, Optional[str]]] = []
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                
                # Get type annotation
                type_str = ast.unparse(item.annotation) if item.annotation else 'any'
                ts_type = self.convert_type(type_str)
                
                # Get default value if present
                default = None
                if item.value:
                    if isinstance(item.value, ast.Constant):
                        default = repr(item.value.value)
                    elif isinstance(item.value, ast.Name) and item.value.id == 'None':
                        default = 'null'
                
                fields.append((field_name, ts_type, default))
        
        if not fields:
            return None
        
        # Generate TypeScript interface
        lines = [f'export interface {node.name} {{']
        
        for field_name, ts_type, default in fields:
            optional = '?' if default == 'null' else ''
            lines.append(f'  {field_name}{optional}: {ts_type};')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def parse_enum(self, node: ast.ClassDef) -> Optional[str]:
        """Parse a Python Enum and generate TypeScript enum or union type."""
        # Check if it's an Enum
        is_enum = any(
            isinstance(base, ast.Name) and 'Enum' in base.id
            for base in node.bases
        )
        
        if not is_enum:
            return None
        
        values: List[str] = []
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(item.value, ast.Constant):
                            values.append(f'"{item.value.value}"')
        
        if not values:
            return None
        
        # Generate TypeScript union type (more idiomatic than enum)
        return f'export type {node.name} = {" | ".join(values)};'
    
    def parse_file(self, file_path: Path) -> None:
        """Parse a Python file and extract dataclasses and enums."""
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Try parsing as dataclass
                    interface = self.parse_dataclass(node, str(file_path))
                    if interface:
                        self.interfaces[node.name] = interface
                        continue
                    
                    # Try parsing as enum
                    enum = self.parse_enum(node)
                    if enum:
                        self.interfaces[node.name] = enum
        
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
    
    def generate_output(self) -> str:
        """Generate the complete TypeScript output file."""
        lines = [
            '// ============================================================================',
            '// AUTO-GENERATED TYPESCRIPT TYPES FROM BACKEND',
            f'// Generated: {datetime.now().isoformat()}',
            '// DO NOT EDIT THIS FILE MANUALLY - Run scripts/generate_frontend_types.py',
            '// ============================================================================',
            '',
        ]
        
        # Add all interfaces and enums
        for name in sorted(self.interfaces.keys()):
            lines.append(self.interfaces[name])
            lines.append('')
        
        return '\n'.join(lines)


def find_python_files(base_dir: Path, patterns: List[str]) -> List[Path]:
    """Find Python files matching patterns."""
    files = []
    for pattern in patterns:
        files.extend(base_dir.glob(pattern))
    return files


def main():
    """Main entry point."""
    # Get project root
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    project_dir = backend_dir.parent
    frontend_dir = project_dir / 'frontend'
    
    print("🔍 Scanning backend for dataclasses and enums...")
    
    # Files to parse
    files_to_parse = [
        # Sir Hawkington
        backend_dir / 'app' / 'ai_agents' / 'sir_hawkington' / 'data_types.py',
        backend_dir / 'app' / 'ai_agents' / 'sir_hawkington' / 'decision_engine.py',
        backend_dir / 'app' / 'ai_agents' / 'sir_hawkington' / 'triage_engine.py',
        
        # Response models
        backend_dir / 'app' / 'schemas' / 'response_models.py',
        
        # Distributed agent types
        backend_dir / 'app' / 'ai_agents' / 'distributed' / 'communication_hub.py',
        backend_dir / 'app' / 'ai_agents' / 'distributed' / 'resource_monitor.py',
    ]
    
    # Also scan all agent directories for data types
    agents_dir = backend_dir / 'app' / 'ai_agents'
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('_'):
            data_types_file = agent_dir / 'data_types.py'
            if data_types_file.exists():
                files_to_parse.append(data_types_file)
    
    # Generate types
    generator = TypeScriptGenerator()
    
    for file_path in files_to_parse:
        if file_path.exists():
            print(f"  📄 Parsing {file_path.relative_to(backend_dir)}...")
            generator.parse_file(file_path)
    
    # Generate output
    print("\n✨ Generating TypeScript types...")
    output = generator.generate_output()
    
    # Write to frontend
    output_file = frontend_dir / 'src' / 'types' / 'backend-generated.ts'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"\n✅ Generated {len(generator.interfaces)} types")
    print(f"📝 Output: {output_file.relative_to(project_dir)}")
    print("\n🎉 Done! TypeScript types are now in sync with backend.")
    
    # Print summary
    print("\n📊 Generated types:")
    for name in sorted(generator.interfaces.keys()):
        print(f"  - {name}")


if __name__ == '__main__':
    main()
