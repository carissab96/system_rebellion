import ast
import os
from typing import Dict, List

# Define the type mapping for metrics to TypeScript types
METRIC_TYPE_MAPPING = {
    "cpu_usage": "number",
    "memory_usage": "number",
    "disk_usage": "number",
    "process_count": "number",
    "network": "NetworkMetrics",
    "io_stats": "IOStats",
    "additional": "Record<string, any>",
}


def extract_metric_functions(source_file_path: str) -> List[Dict[str, str]]:
    """
    Extract metric function information from the resource monitor source code.
    
    Args:
        source_file_path: Path to the resource_monitor.py file
        
    Returns:
        List of dictionaries containing function_name and metric_key
    """
    metric_functions = []
    
    try:
        with open(source_file_path, "r") as f:
            source_code = f.read()
            tree = ast.parse(source_code)
        
        # Walk through all nodes in the AST
        for node in ast.walk(tree):
            # Check for both async and regular function definitions
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                function_name = node.name
                
                # Extract metric key from function name
                if function_name.startswith("_get_"):
                    metric_key = function_name.replace("_get_", "", 1)
                elif function_name.startswith("get_"):
                    metric_key = function_name.replace("get_", "", 1)
                else:
                    # Skip functions that don't match the pattern
                    continue
                
                metric_functions.append({
                    "function_name": function_name,
                    "metric_key": metric_key,
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
                
    except FileNotFoundError:
        print(f"Error: File not found at {source_file_path}")
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
    
    return metric_functions


def generate_typescript_mapping(metric_functions: List[Dict[str, str]]) -> str:
    """
    Generate TypeScript mapping file with metric keys and types.
    
    Args:
        metric_functions: List of metric function information
        
    Returns:
        TypeScript mapping file content
    """
    lines = []
    lines.append("// Auto-generated from resource_monitor.py using resource_monitor_ast.py")
    lines.append("// DO NOT EDIT MANUALLY - Run 'python backend/resource_monitor_ast.py' to regenerate")
    lines.append("")
    lines.append("export const METRIC_KEYS = {")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        lines.append(f"  {metric_key.upper()}: '{metric_key}',")
    
    lines.append("} as const;")
    lines.append("")
    lines.append("export type MetricKey = typeof METRIC_KEYS[keyof typeof METRIC_KEYS];")
    lines.append("")
    lines.append("export interface MetricTypes {")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        ts_type = METRIC_TYPE_MAPPING.get(metric_key, "any")
        lines.append(f"  '{metric_key}': {ts_type};")
    
    lines.append("}")
    lines.append("")
    lines.append("export const METRIC_METADATA = {")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        function_name = func_info["function_name"]
        is_async = func_info["is_async"]
        ts_type = METRIC_TYPE_MAPPING.get(metric_key, "any")
        lines.append(f"  '{metric_key}': {{")
        lines.append(f"    key: '{metric_key}',")
        lines.append(f"    functionName: '{function_name}',")
        lines.append(f"    isAsync: {str(is_async).lower()},")
        lines.append(f"    type: '{ts_type}',")
        lines.append(f"  }},")
    
    lines.append("} as const;")
    lines.append("")
    
    return "\n".join(lines)


def generate_python_mapping(metric_functions: List[Dict[str, str]]) -> str:
    """
    Generate Python mapping file with metric keys.
    
    Args:
        metric_functions: List of metric function information
        
    Returns:
        Python mapping file content
    """
    lines = []
    lines.append("# Auto-generated from resource_monitor.py using resource_monitor_ast.py")
    lines.append("# DO NOT EDIT MANUALLY - Run 'python backend/resource_monitor_ast.py' to regenerate")
    lines.append("")
    lines.append("from typing import Literal")
    lines.append("")
    lines.append("# Metric key constants")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        lines.append(f"{metric_key.upper()} = '{metric_key}'")
    
    lines.append("")
    lines.append("# Type alias for all valid metric keys")
    metric_keys_str = ", ".join([f"'{func['metric_key']}'" for func in metric_functions])
    lines.append(f"MetricKey = Literal[{metric_keys_str}]")
    lines.append("")
    lines.append("# List of all metric keys")
    lines.append("ALL_METRIC_KEYS = [")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        lines.append(f"    '{metric_key}',")
    
    lines.append("]")
    lines.append("")
    lines.append("# Metadata about each metric")
    lines.append("METRIC_METADATA = {")
    
    for func_info in metric_functions:
        metric_key = func_info["metric_key"]
        function_name = func_info["function_name"]
        is_async = func_info["is_async"]
        lines.append(f"    '{metric_key}': {{")
        lines.append(f"        'key': '{metric_key}',")
        lines.append(f"        'function_name': '{function_name}',")
        lines.append(f"        'is_async': {is_async},")
        lines.append(f"    }},")
    
    lines.append("}")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main execution function"""
    # Path to the resource monitor file
    backend_dir = os.path.dirname(__file__)
    resource_monitor_path = os.path.join(
        backend_dir,
        "app/optimization/resource_monitor.py"
    )
    
    print(f"Analyzing: {resource_monitor_path}")
    print("-" * 60)
    
    # Extract metric functions
    metric_functions = extract_metric_functions(resource_monitor_path)
    
    # Display found functions
    print(f"\nFound {len(metric_functions)} metric functions:")
    for func_info in metric_functions:
        async_marker = "[ASYNC]" if func_info["is_async"] else "[SYNC]"
        print(f"  {async_marker} {func_info['function_name']} -> {func_info['metric_key']}")
    
    # Generate TypeScript mapping
    print("\n" + "=" * 60)
    print("Generating mapping files...")
    print("=" * 60)
    
    ts_mapping = generate_typescript_mapping(metric_functions)
    py_mapping = generate_python_mapping(metric_functions)
    
    # Save TypeScript mapping to frontend
    frontend_output_path = os.path.join(
        backend_dir,
        "../frontend/src/types/metricKeys.ts"
    )
    os.makedirs(os.path.dirname(frontend_output_path), exist_ok=True)
    with open(frontend_output_path, "w") as f:
        f.write(ts_mapping)
    print(f"✓ TypeScript mapping saved to: {frontend_output_path}")
    
    # Save Python mapping to backend
    backend_output_path = os.path.join(
        backend_dir,
        "app/optimization/metric_keys.py"
    )
    os.makedirs(os.path.dirname(backend_output_path), exist_ok=True)
    with open(backend_output_path, "w") as f:
        f.write(py_mapping)
    print(f"✓ Python mapping saved to: {backend_output_path}")
    
    print("\n" + "=" * 60)
    print("Preview of TypeScript mapping:")
    print("=" * 60)
    print(ts_mapping[:500] + "...\n")
    
    print("\nDone! You can now import these mappings:")
    print("  Frontend: import { METRIC_KEYS, METRIC_METADATA } from '@/types/metricKeys';")
    print("  Backend:  from app.optimization.metric_keys import METRIC_KEYS, ALL_METRIC_KEYS")


if __name__ == "__main__":
    main()
