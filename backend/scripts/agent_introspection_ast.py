"""
Agent Introspection using AST
Extracts agent classes, methods, and state variables for UI visualization
"""

import ast
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class AgentIntrospector:
    """Extract agent structure information using AST parsing"""
    
    def __init__(self, agents_base_path: str):
        self.agents_base_path = Path(agents_base_path)
        self.agent_data = {}
        
    def extract_class_info(self, node: ast.ClassDef, file_path: str) -> Dict[str, Any]:
        """Extract information about a class (agent)"""
        
        # Extract base classes
        base_classes = [self._get_name(base) for base in node.bases]
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract methods
        methods = []
        state_variables = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                method_info = self._extract_method_info(item)
                methods.append(method_info)
            elif isinstance(item, ast.AnnAssign):
                # Class-level type annotations
                var_info = self._extract_variable_info(item)
                if var_info:
                    state_variables.append(var_info)
        
        return {
            "name": node.name,
            "file_path": str(file_path),
            "base_classes": base_classes,
            "docstring": docstring,
            "methods": methods,
            "state_variables": state_variables,
            "line_number": node.lineno,
        }
    
    def _extract_method_info(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
        """Extract information about a method"""
        
        # Get parameters
        params = []
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation) if arg.annotation else None
            }
            params.append(param_info)
        
        # Get return type
        return_type = self._get_annotation(node.returns) if node.returns else None
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Check for decorators
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        
        # Detect method category based on name patterns
        method_category = self._categorize_method(node.name)
        
        # Extract state changes (assignments to self.*)
        state_changes = self._extract_state_changes(node)
        
        # Extract method calls (to track agent interactions)
        method_calls = self._extract_method_calls(node)
        
        return {
            "name": node.name,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "is_abstract": "abstractmethod" in decorators,
            "is_private": node.name.startswith("_"),
            "parameters": params,
            "return_type": return_type,
            "docstring": docstring,
            "decorators": decorators,
            "category": method_category,
            "state_changes": state_changes,
            "method_calls": method_calls,
            "line_number": node.lineno,
        }
    
    def _extract_variable_info(self, node: ast.AnnAssign) -> Optional[Dict[str, Any]]:
        """Extract information about a variable assignment"""
        if isinstance(node.target, ast.Name):
            return {
                "name": node.target.id,
                "type": self._get_annotation(node.annotation),
                "has_default": node.value is not None,
            }
        elif isinstance(node.target, ast.Attribute):
            if isinstance(node.target.value, ast.Name) and node.target.value.id == "self":
                return {
                    "name": node.target.attr,
                    "type": self._get_annotation(node.annotation),
                    "has_default": node.value is not None,
                }
        return None
    
    def _extract_state_changes(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
        """Extract state variable assignments (self.variable = ...)"""
        state_changes = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            state_changes.add(target.attr)
            elif isinstance(child, ast.AugAssign):
                if isinstance(child.target, ast.Attribute):
                    if isinstance(child.target.value, ast.Name) and child.target.value.id == "self":
                        state_changes.add(child.target.attr)
        
        return sorted(list(state_changes))
    
    def _extract_method_calls(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Dict[str, str]]:
        """Extract method calls to track interactions"""
        method_calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    # self.method_name() or object.method_name()
                    obj_name = None
                    if isinstance(child.func.value, ast.Name):
                        obj_name = child.func.value.id
                    
                    method_calls.append({
                        "object": obj_name,
                        "method": child.func.attr,
                    })
                elif isinstance(child.func, ast.Name):
                    # Direct function call
                    method_calls.append({
                        "object": None,
                        "method": child.func.id,
                    })
        
        # Deduplicate while preserving order
        seen = set()
        unique_calls = []
        for call in method_calls:
            key = f"{call['object']}.{call['method']}"
            if key not in seen:
                seen.add(key)
                unique_calls.append(call)
        
        return unique_calls[:10]  # Limit to first 10 unique calls
    
    def _categorize_method(self, method_name: str) -> str:
        """Categorize methods based on naming patterns"""
        if method_name.startswith("__") and method_name.endswith("__"):
            return "dunder"
        elif method_name in ["process_metrics", "process", "analyze"]:
            return "core_processing"
        elif method_name.startswith("get_") or method_name.startswith("_get_"):
            return "getter"
        elif method_name.startswith("set_") or method_name.startswith("_set_"):
            return "setter"
        elif method_name.startswith("handle_"):
            return "handler"
        elif method_name in ["initialize", "init", "setup"]:
            return "initialization"
        elif "health" in method_name or "status" in method_name:
            return "monitoring"
        elif method_name.startswith("_"):
            return "private"
        else:
            return "public"
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from various node types"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> str:
        """Get type annotation as string"""
        if node is None:
            return "Any"
        try:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        except:
            return "Any"
    
    def analyze_agent_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single Python file for agent classes"""
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            
            tree = ast.parse(source)
            agents = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's an agent class (inherits from BaseAIAgent or has "Agent" in name)
                    base_names = [self._get_name(base) for base in node.bases]
                    is_agent = (
                        any("Agent" in base for base in base_names) or
                        "Agent" in node.name
                    )
                    
                    if is_agent:
                        agent_info = self.extract_class_info(node, file_path)
                        agents.append(agent_info)
            
            return agents
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return []
    
    def scan_agents_directory(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scan the agents directory for all agent files"""
        all_agents = {}
        
        # Find all Python files in agent directories
        for agent_dir in self.agents_base_path.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith("__"):
                agent_name = agent_dir.name
                all_agents[agent_name] = []
                
                # Scan Python files in this agent's directory
                for py_file in agent_dir.rglob("*.py"):
                    if py_file.name.startswith("__"):
                        continue
                    
                    agents = self.analyze_agent_file(py_file)
                    all_agents[agent_name].extend(agents)
        
        # Also check for agents in the base directory
        for py_file in self.agents_base_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            agents = self.analyze_agent_file(py_file)
            if agents:
                all_agents["_base"] = all_agents.get("_base", []) + agents
        
        return all_agents


def generate_typescript_agent_map(agents_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate TypeScript interface for agent structure"""
    lines = []
    lines.append("// Auto-generated agent introspection data")
    lines.append("// DO NOT EDIT MANUALLY - Run 'python backend/agent_introspection_ast.py' to regenerate")
    lines.append("")
    lines.append("export interface AgentMethod {")
    lines.append("  name: string;")
    lines.append("  isAsync: boolean;")
    lines.append("  isAbstract: boolean;")
    lines.append("  isPrivate: boolean;")
    lines.append("  category: string;")
    lines.append("  parameters: Array<{ name: string; annotation: string | null }>;")
    lines.append("  returnType: string | null;")
    lines.append("  docstring: string | null;")
    lines.append("  stateChanges: string[];")
    lines.append("  methodCalls: Array<{ object: string | null; method: string }>;")
    lines.append("}")
    lines.append("")
    lines.append("export interface AgentStateVariable {")
    lines.append("  name: string;")
    lines.append("  type: string;")
    lines.append("  hasDefault: boolean;")
    lines.append("}")
    lines.append("")
    lines.append("export interface AgentClass {")
    lines.append("  name: string;")
    lines.append("  filePath: string;")
    lines.append("  baseClasses: string[];")
    lines.append("  docstring: string | null;")
    lines.append("  methods: AgentMethod[];")
    lines.append("  stateVariables: AgentStateVariable[];")
    lines.append("  lineNumber: number;")
    lines.append("}")
    lines.append("")
    lines.append("export interface AgentDirectory {")
    lines.append("  [agentName: string]: AgentClass[];")
    lines.append("}")
    lines.append("")
    
    # Generate the actual data
    lines.append("export const AGENT_INTROSPECTION_DATA: AgentDirectory = ")
    lines.append(json.dumps(agents_data, indent=2))
    lines.append(";")
    lines.append("")
    
    # Generate helper functions
    lines.append("// Helper functions for agent introspection")
    lines.append("export function getAgentByName(agentName: string): AgentClass[] {")
    lines.append("  return AGENT_INTROSPECTION_DATA[agentName] || [];")
    lines.append("}")
    lines.append("")
    lines.append("export function getAllAgentNames(): string[] {")
    lines.append("  return Object.keys(AGENT_INTROSPECTION_DATA);")
    lines.append("}")
    lines.append("")
    lines.append("export function getAgentMethods(agentName: string, category?: string): AgentMethod[] {")
    lines.append("  const agents = getAgentByName(agentName);")
    lines.append("  const allMethods = agents.flatMap(agent => agent.methods);")
    lines.append("  if (category) {")
    lines.append("    return allMethods.filter(m => m.category === category);")
    lines.append("  }")
    lines.append("  return allMethods;")
    lines.append("}")
    lines.append("")
    lines.append("export function getAgentStateVariables(agentName: string): AgentStateVariable[] {")
    lines.append("  const agents = getAgentByName(agentName);")
    lines.append("  return agents.flatMap(agent => agent.stateVariables);")
    lines.append("}")
    lines.append("")
    
    return "\n".join(lines)


def generate_python_agent_map(agents_data: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate Python constants for agent structure"""
    lines = []
    lines.append("# Auto-generated agent introspection data")
    lines.append("# DO NOT EDIT MANUALLY - Run 'python backend/agent_introspection_ast.py' to regenerate")
    lines.append("")
    lines.append("from typing import Dict, List, Any")
    lines.append("")
    lines.append("AGENT_INTROSPECTION_DATA: Dict[str, List[Dict[str, Any]]] = \\")
    lines.append(json.dumps(agents_data, indent=4))
    lines.append("")
    lines.append("")
    lines.append("def get_agent_by_name(agent_name: str) -> List[Dict[str, Any]]:")
    lines.append('    """Get agent class information by agent name"""')
    lines.append("    return AGENT_INTROSPECTION_DATA.get(agent_name, [])")
    lines.append("")
    lines.append("")
    lines.append("def get_all_agent_names() -> List[str]:")
    lines.append('    """Get list of all agent names"""')
    lines.append("    return list(AGENT_INTROSPECTION_DATA.keys())")
    lines.append("")
    lines.append("")
    lines.append("def get_agent_methods(agent_name: str, category: str = None) -> List[Dict[str, Any]]:")
    lines.append('    """Get methods for an agent, optionally filtered by category"""')
    lines.append("    agents = get_agent_by_name(agent_name)")
    lines.append("    all_methods = []")
    lines.append("    for agent in agents:")
    lines.append("        all_methods.extend(agent.get('methods', []))")
    lines.append("    ")
    lines.append("    if category:")
    lines.append("        return [m for m in all_methods if m.get('category') == category]")
    lines.append("    return all_methods")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """Main execution"""
    backend_dir = Path(__file__).parent
    agents_path = backend_dir / "app" / "ai_agents"
    
    print("=" * 60)
    print("Agent Introspection Tool")
    print("=" * 60)
    print(f"Scanning: {agents_path}")
    print()
    
    # Create introspector
    introspector = AgentIntrospector(str(agents_path))
    
    # Scan all agents
    agents_data = introspector.scan_agents_directory()
    
    # Display summary
    print(f"Found {len(agents_data)} agent directories:")
    for agent_name, classes in agents_data.items():
        print(f"  📁 {agent_name}: {len(classes)} class(es)")
        for cls in classes:
            method_count = len(cls['methods'])
            state_count = len(cls['state_variables'])
            print(f"     └─ {cls['name']}: {method_count} methods, {state_count} state vars")
    
    # Generate TypeScript mapping
    print("\n" + "=" * 60)
    print("Generating mapping files...")
    print("=" * 60)
    
    ts_mapping = generate_typescript_agent_map(agents_data)
    py_mapping = generate_python_agent_map(agents_data)
    
    # Save TypeScript mapping
    frontend_output = backend_dir / "../frontend/src/types/agentIntrospection.ts"
    frontend_output.parent.mkdir(parents=True, exist_ok=True)
    with open(frontend_output, "w") as f:
        f.write(ts_mapping)
    print(f"✓ TypeScript mapping saved to: {frontend_output}")
    
    # Save Python mapping
    backend_output = backend_dir / "app/ai_agents/agent_introspection.py"
    with open(backend_output, "w") as f:
        f.write(py_mapping)
    print(f"✓ Python mapping saved to: {backend_output}")
    
    # Save JSON for debugging
    json_output = backend_dir / "agent_introspection_data.json"
    with open(json_output, "w") as f:
        json.dump(agents_data, f, indent=2)
    print(f"✓ JSON data saved to: {json_output}")
    
    print("\n" + "=" * 60)
    print("Usage Examples:")
    print("=" * 60)
    print("Frontend:")
    print("  import { AGENT_INTROSPECTION_DATA, getAgentMethods } from '@/types/agentIntrospection';")
    print("  const methods = getAgentMethods('sir_hawkington', 'core_processing');")
    print("")
    print("Backend:")
    print("  from app.ai_agents.agent_introspection import get_agent_methods")
    print("  methods = get_agent_methods('sir_hawkington', 'core_processing')")
    print("")
    print("This data can be used to:")
    print("  • Visualize agent method execution in real-time")
    print("  • Show state variable changes in the UI")
    print("  • Track agent interactions and method calls")
    print("  • Display agent capabilities and documentation")


if __name__ == "__main__":
    main()
