from typing import List, Dict, Set, Optional, Deque
from collections import deque
from devai.core.models import DeploymentPlan, ActionType, ResourceDefinition
from devai.core.exceptions import ExecutionError
from devai.connectors.base import ConnectorBase
from devai.plugins.registry import PluginRegistry
from devai.memory.state_manager import StateManager
from devai.core.models import ActionType

class ExecutionEngine:
    """
    Takes a STRICTLY VALIDATED DeploymentPlan and executes the state changes deterministically.
    """
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()
        if not registry:
            self.registry.load_plugins()
        
    def register_connector(self, resource_type: str, connector: ConnectorBase):
        """Plugin entry point for new infrastructure providers."""
        self.registry.connectors[resource_type] = connector

    def _build_dag(self, resources: List[ResourceDefinition]) -> List[ResourceDefinition]:
        """
        Performs a topological sort securely resolving the Directed Acyclic Graph.
        """
        # Map resource names to their definitions
        resource_map = {r.name: r for r in resources}
        
        # Build adjacency list
        in_degree: Dict[str, int] = {r.name: 0 for r in resources}
        adj_list: Dict[str, List[str]] = {r.name: [] for r in resources}
        
        for r in resources:
            for dep in r.depends_on:
                if dep not in resource_map:
                    raise ExecutionError(f"Resource '{r.name}' depends on '{dep}', but '{dep}' is missing from the plan.")
                adj_list[dep].append(r.name)
                in_degree[r.name] += 1
                
        # Queue for nodes with no incoming dependencies
        queue: Deque[str] = deque([name for name in in_degree if in_degree[name] == 0])
        sorted_order: List[ResourceDefinition] = []
        
        while queue:
            current = queue.popleft()
            sorted_order.append(resource_map[current])
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(sorted_order) != len(resources):
            raise ExecutionError("Circular dependency detected in the deployment plan DAG!")
            
        return sorted_order

    def execute(self, plan: DeploymentPlan):
        """Executes the plan deterministically according to the Dependency DAG."""
        print(f"Executing Plan: {plan.description} (Version: {plan.version})")
        print("Dependency DAG Resolved Successfully.\n")
        
        try:
            sorted_resources = self._build_dag(plan.resources)
        except Exception as e:
            raise ExecutionError(f"Failed to resolve execution DAG: {str(e)}")
            
        for resource in sorted_resources:
            connector = self.registry.get_connector(resource.type)
            if not connector:
                print(f"Warning: No connector registered for type '{resource.type}'. Skipping {resource.name}.")
                continue
                
            if resource.action == ActionType.CREATE or resource.action == ActionType.UPDATE:
                connector.apply(resource.name, resource.properties)
                StateManager.update_resource(resource.name, resource.type, resource.properties, "deployed")
            elif resource.action == ActionType.DELETE:
                connector.destroy(resource.name, resource.properties)
                StateManager.delete_resource(resource.name)
            else:
                print(f"Action '{resource.action}' for resource '{resource.name}' is unsupported.")
