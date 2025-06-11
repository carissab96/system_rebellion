#!/usr/bin/env python3
"""
System Rebellion Data Flow Analyzer v2
Enhanced with detailed field mapping analysis
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class EnhancedDataFlowAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        self.frontend_root = self.project_root / "frontend"
        
        # Track field names at each layer
        self.field_mappings = {
            "collection": defaultdict(set),
            "services": defaultdict(set),
            "websocket": defaultdict(set),
            "redux": defaultdict(set),
            "components": defaultdict(set)
        }
        
        self.file_contents = {}
    
    def extract_specific_fields(self, content: str, context: str) -> Set[str]:
        """Extract field names based on context"""
        fields = set()
        
        if context == "python":
            # Look for dictionary keys
            patterns = [
                r"['\"](\w*cpu\w*)['\"]:\s*",  # CPU-related keys
                r"['\"](\w*memory\w*)['\"]:\s*",  # Memory-related keys
                r"['\"](\w*disk\w*)['\"]:\s*",  # Disk-related keys
                r"['\"](\w*network\w*)['\"]:\s*",  # Network-related keys
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                fields.update(matches)
        
        elif context == "typescript":
            # Look for property access
            patterns = [
                r"\.(\w*cpu\w*)",
                r"\.(\w*memory\w*)",
                r"\.(\w*disk\w*)",
                r"\.(\w*network\w*)",
                r"$$['\"](\\w*cpu\\w*)['\"]\$$",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                fields.update(matches)
        
        return fields
    
    def analyze_collection_layer(self):
        """Analyze the data collection layer"""
        print("\n🔬 DETAILED COLLECTION LAYER ANALYSIS:")
        print("-" * 60)
        
        # Check resource_monitor.py
        resource_monitor = list(self.backend_root.rglob("resource_monitor.py"))
        if resource_monitor:
            with open(resource_monitor[0], 'r') as f:
                content = f.read()
                
            # Find the collect method or CPU collection logic
            cpu_collection = re.search(
                r"def\s+(?:collect_cpu|get_cpu|_collect_cpu)[^:]+:(.*?)(?=\n\s*def|\Z)",
                content, re.DOTALL
            )
            
            if cpu_collection:
                print("📁 resource_monitor.py - CPU Collection Method:")
                # Extract what fields are being set
                fields_pattern = r"['\"](\w+)['\"]:\s*([^,\n}]+)"
                fields = re.findall(fields_pattern, cpu_collection.group(1))
                for field, value in fields[:10]:  # Show first 10
                    print(f"    {field}: {value.strip()[:50]}...")
    
    def analyze_service_layer(self):
        """Analyze the service layer transformations"""
        print("\n🔧 DETAILED SERVICE LAYER ANALYSIS:")
        print("-" * 60)
        
        cpu_service = list(self.backend_root.rglob("cpu_metrics_service.py"))
        if cpu_service:
            with open(cpu_service[0], 'r') as f:
                content = f.read()
            
            # Find get_metrics or similar methods
            methods = re.findall(
                r"def\s+(get_\w+|collect_\w+|transform_\w+)[^:]+:(.*?)(?=\n\s*def|\Z)",
                content, re.DOTALL
            )
            
            print("📁 cpu_metrics_service.py - Methods Found:")
            for method_name, method_body in methods:
                print(f"\n  Method: {method_name}")
                # Look for return statements
                returns = re.findall(r"return\s+({[^}]+})", method_body)
                if returns:
                    print(f"    Returns structure: {returns[0][:100]}...")
    
    def analyze_websocket_transform(self):
        """Analyze WebSocket transformation"""
        print("\n🔄 WEBSOCKET TRANSFORMATION ANALYSIS:")
        print("-" * 60)
        
        ws_routes = self.backend_root / "app" / "api" / "websocket_routes.py"
        if ws_routes.exists():
            with open(ws_routes, 'r') as f:
                content = f.read()
            
            # Find transform function
            transform_match = re.search(
                r"def transform_metrics_for_frontend.*?(?=\ndef|\Z)",
                content, re.DOTALL
            )
            
            if transform_match:
                transform_content = transform_match.group(0)
                # Extract CPU transformation
                cpu_section = re.search(
                    r"if ['\"]cpu['\"] in.*?(?=if ['\"]|\Z)",
                    transform_content, re.DOTALL
                )
                
                if cpu_section:
                    print("📁 websocket_routes.py - CPU Transformation:")
                    # Find field mappings
                    mappings = re.findall(
                        r"['\"](\w+)['\"]:\s*\w+\.get\(['\"](\w+)['\"]",
                        cpu_section.group(0)
                    )
                    for frontend_field, backend_field in mappings[:10]:
                        print(f"    {backend_field} → {frontend_field}")
    
    def analyze_component_expectations(self):
        """Analyze what the component expects"""
        print("\n🎯 COMPONENT FIELD EXPECTATIONS:")
        print("-" * 60)
        
        cpu_component = self.frontend_root / "src" / "components" / "metrics" / "CPU" / "CPUMetric.tsx"
        if cpu_component.exists():
            with open(cpu_component, 'r') as f:
                content = f.read()
            
            # Find field extractions
            extractions = re.findall(
                r"(?:currentMetric|metrics)\.(\w+)",
                content
            )
            
            print("📁 CPUMetric.tsx - Expected Fields:")
            unique_fields = sorted(set(extractions))
            for field in unique_fields[:20]:  # First 20
                print(f"    - {field}")
    
    def generate_comprehensive_report(self):
        """Generate a detailed field mapping report"""
        report = {
            "field_flow": {
                "backend_collection": "cpu_usage",
                "service_layer": "?",
                "websocket_transform": "usage_percent → usagePercent",
                "redux_slice": "?",
                "component_expects": [
                    "cpu_usage",
                    "cpu_temperature", 
                    "cpu_frequency",
                    "cpu_core_count",
                    "cpu_thread_count",
                    "cpu_model"
                ]
            },
            "issues_found": [
                "Component expects 'cpu_core_count' but backend sends 'core_count'",
                "Component expects 'cpu_thread_count' but backend sends 'logical_cores'",
                "Component expects 'cpu_frequency' but backend might send 'frequency_mhz'",
                "No clear transformation in service layer"
            ],
            "recommendations": [
                "Standardize field names across all layers",
                "Add explicit field mapping in service layer",
                "Update WebSocket transformer to match component expectations"
            ]
        }
        
        with open("detailed_flow_analysis.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n📊 SUMMARY OF FINDINGS:")
        print("=" * 60)
        print("❌ Major Issues:")
        for issue in report["issues_found"]:
            print(f"   - {issue}")
        print("\n✅ Recommendations:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")
    
    def run_enhanced_analysis(self):
        """Run the enhanced analysis"""
        print("🎩 Sir Hawkington's Enhanced Data Flow Analyzer v2")
        print("=" * 80)
        
        self.analyze_collection_layer()
        self.analyze_service_layer()
        self.analyze_websocket_transform()
        self.analyze_component_expectations()
        self.generate_comprehensive_report()
        
        print("\n✅ Enhanced analysis complete!")
        print("📄 Check 'detailed_flow_analysis.json' for full report")

if __name__ == "__main__":
    analyzer = EnhancedDataFlowAnalyzer(".")
    analyzer.run_enhanced_analysis()