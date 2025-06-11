#!/usr/bin/env python3
"""
Component Field Analyzer - Case-Insensitive Version
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict

class ComponentFieldAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_root = self.project_root / "frontend"
        self.results = defaultdict(lambda: {
            "main_component": {},
            "subcomponents": {},
            "all_fields": set()
        })
    
    def find_metric_components(self):
        """Find all metric components with case-insensitive search"""
        metrics_base = self.frontend_root / "src" / "components" / "metrics"
        
        # Map of canonical names to actual directory names
        component_dirs = {}
        
        if metrics_base.exists():
            for item in metrics_base.iterdir():
                if item.is_dir():
                    # Normalize to lowercase for comparison
                    normalized = item.name.lower()
                    if normalized in ['cpu', 'memory', 'disk', 'network']:
                        # Map to canonical name
                        if normalized == 'cpu':
                            component_dirs['CPU'] = item
                        elif normalized == 'memory':
                            component_dirs['Memory'] = item
                        elif normalized == 'disk':
                            component_dirs['Disk'] = item
                        elif normalized == 'network':
                            component_dirs['Network'] = item
        
        return component_dirs
    
    def analyze_component_file(self, filepath: Path) -> Dict:
        """Analyze a single component file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return {"fields_accessed": set()}
        
        fields = set()
        
        # All the patterns to find field access
        patterns = [
            # Direct access: currentMetric.cpu_usage
            r'currentMetric\.(\w+)',
            # Array access: currentMetric['cpu_usage']
            r'currentMetric$$[\'"]([\w_]+)[\'"]$$',
            # Destructuring: const { cpu_usage } = currentMetric
            r'const\s*{\s*([^}]+)\s*}\s*=\s*currentMetric',
            # Optional chaining: currentMetric?.cpu_usage
            r'currentMetric\?\.(\w+)',
            # Nested access: currentMetric.cpu?.cores
            r'currentMetric\.(\w+)\??\.',
            # From metrics object
            r'metrics\.(\w+)',
            # From data object
            r'data\.(\w+)',
            # From state
            r'state\.current\.(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if isinstance(matches[0], tuple) if matches else False:
                # Handle destructuring pattern
                for match in matches:
                    fields.update([f.strip() for f in match[0].split(',')])
            else:
                fields.update(matches)
        
        # Also look for specific CPU-related fields
        cpu_specific = re.findall(r'(cpu_\w+)', content, re.IGNORECASE)
        fields.update(cpu_specific)
        
        return {"fields_accessed": fields}
    
    def analyze_all_components(self):
        """Analyze all metric components"""
        component_dirs = self.find_metric_components()
        
        print(f"\n📁 Found component directories:")
        for name, path in component_dirs.items():
            print(f"   - {name}: {path.name}")
        
        for metric_type, component_dir in component_dirs.items():
            print(f"\n🔍 Analyzing {metric_type} components...")
            
            # Main component file (handle various naming patterns)
            possible_names = [
                f"{metric_type}Metric.tsx",
                f"{metric_type.lower()}Metric.tsx",
                f"{metric_type.lower()}_metric.tsx",
                f"{metric_type}Metrics.tsx"
            ]
            
            main_found = False
            for name in possible_names:
                main_file = component_dir / name
                if main_file.exists():
                    print(f"   ✓ Found main component: {name}")
                    analysis = self.analyze_component_file(main_file)
                    self.results[metric_type]["main_component"] = analysis
                    self.results[metric_type]["all_fields"].update(analysis["fields_accessed"])
                    main_found = True
                    break
            
            if not main_found:
                print(f"   ✗ No main component file found")
            
            # Check for Tabs or tabs directory
            tabs_dirs = ['Tabs', 'tabs']
            tabs_found = False
            
            for tabs_name in tabs_dirs:
                tabs_dir = component_dir / tabs_name
                if tabs_dir.exists():
                    print(f"   ✓ Found {tabs_name} directory")
                    tabs_found = True
                    
                    for tab_file in tabs_dir.glob("*.tsx"):
                        if not tab_file.name.startswith("types"):
                            analysis = self.analyze_component_file(tab_file)
                            self.results[metric_type]["subcomponents"][tab_file.stem] = analysis
                            self.results[metric_type]["all_fields"].update(analysis["fields_accessed"])
                            print(f"     - {tab_file.name}: {len(analysis['fields_accessed'])} fields")
                    break
            
            if not tabs_found:
                print(f"   ✗ No tabs directory found")
    
    def generate_transformer_code(self, metric_type: str, fields: set) -> str:
        """Generate the transformer code for WebSocket"""
        code = f'''
    # Transform {metric_type} metrics
    if "{metric_type.lower()}" in metrics:
        {metric_type.lower()}_data = metrics["{metric_type.lower()}"]
        
        # Component expects these exact fields'''
        
        for field in sorted(fields):
            if field and not field.startswith('_'):  # Skip private fields
                # Generate fallback chain
                base_name = field.replace(f'{metric_type.lower()}_', '')
                code += f'''
        transformed["{field}"] = (
            {metric_type.lower()}_data.get("{field}") or
            {metric_type.lower()}_data.get("{base_name}") or
            {metric_type.lower()}_data.get("{field.replace('_', '')}", 0)
        )'''
        
        return code
    
    def generate_report(self):
        """Generate the final report"""
        self.analyze_all_components()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "transformer_code": {}
        }
        
        print("\n" + "="*60)
        print("📊 FINAL FIELD ANALYSIS REPORT")
        print("="*60)
        
        for metric_type, data in self.results.items():
            if data["all_fields"]:
                fields = sorted(data["all_fields"])
                
                print(f"\n🎯 {metric_type} Component Expects:")
                print(f"   Total unique fields: {len(fields)}")
                print("   Fields:")
                for field in fields[:15]:  # Show first 15
                    print(f"     - {field}")
                if len(fields) > 15:
                    print(f"     ... and {len(fields) - 15} more")
                
                report["summary"][metric_type] = {
                    "total_fields": len(fields),
                    "fields": fields,
                    "main_component_fields": sorted(data["main_component"].get("fields_accessed", [])),
                    "subcomponent_count": len(data["subcomponents"])
                }
                
                # Generate transformer code
                transformer = self.generate_transformer_code(metric_type, fields)
                report["transformer_code"][metric_type] = transformer
        
        # Save report
        with open("component_expectations.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate transformer file
        with open("websocket_transformer_fix.py", "w") as f:
            f.write("# Add this to your transform_metrics_for_frontend function:\n\n")
            for metric_type, code in report["transformer_code"].items():
                f.write(code)
                f.write("\n\n")
        
        print("\n✅ Reports generated:")
        print("   - component_expectations.json")
        print("   - websocket_transformer_fix.py")
        
        return report

if __name__ == "__main__":
    analyzer = ComponentFieldAnalyzer(".")
    analyzer.generate_report()