from typing import List, Dict, Set, Optional, Deque
from collections import deque
from devai.memory.state_manager import StateManager
from devai.core.models import DeploymentPlan, ResourceDefinition, ActionType
from devai.core.exceptions import ExecutionError, DevAIException
from devai.connectors.base import ConnectorBase
from devai.plugins.registry import PluginRegistry
from devai.connectors.vps_connector import VPSConnector
from devai.server.deployment_manager import DeploymentManager
from devai.core.server_manager import ServerManager

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

    def execute(self, plan: DeploymentPlan):
        """
        Executes the plan by building a dependency graph and running tasks in order.
        """
        print(f"🚀 Executing Deployment Plan: {plan.description}")
        
        # 1. Dependency Resolution (DAG)
        adj_list = {r.name: r.depends_on for r in plan.resources}
        in_degree = {r.name: 0 for r in plan.resources}
        
        for name in adj_list:
            for dep in adj_list[name]:
                if dep in in_degree:
                    in_degree[name] += 1
        
        # 2. Kahn's Algorithm for Topological Sort
        queue: Deque[str] = deque([r for r, d in in_degree.items() if d == 0])
        sorted_order = []
        
        while queue:
            node = queue.popleft()
            sorted_order.append(node)
            
            for name, deps in adj_list.items():
                if node in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
                        
        if len(sorted_order) != len(plan.resources):
            raise ExecutionError("Circular dependency detected in the deployment plan DAG!")
            
        # 3. Execution Loop
        resource_map = {r.name: r for r in plan.resources}
        for res_name in sorted_order:
            resource = resource_map[res_name]
            self._execute_resource(resource)

    def _execute_resource(self, resource: ResourceDefinition):
        """
        Routes the resource to the correct connector and handles orchestration logic.
        """
        print(f"[Engine] Processing {resource.type}: {resource.name}")
        
        if resource.type == "vps_server" and resource.action == "setup":
            ServerManager.setup_server(resource.name)
        elif resource.type == "multi_service_deployment":
            self._handle_orchestration(resource)
        else:
            # Legacy/Basic connectors
            connector = self.registry.get_connector(resource.type)
            if connector:
                if resource.action == "create":
                    connector.apply(resource.name, resource.properties)
                elif resource.action == "delete":
                    connector.destroy(resource.name, resource.properties)
                StateManager.update_resource(resource.name, resource.type, resource.properties, "deployed")

    def _handle_orchestration(self, resource: ResourceDefinition):
        """
        High-level orchestration for multi-service deployments.
        """
        props = resource.properties
        target_server = props.get("server", "default")
        services = props.get("services", [])
        
        # Get server details
        servers = ServerManager.list_servers()
        server = next((s for s in servers if s['name'] == target_server), None)
        if not server:
            raise DevAIException(f"Target server '{target_server}' not found.")
            
        # Deploy via Manager
        mgr = DeploymentManager(server['ip'], server['username'])
        try:
            mgr.deploy_project(resource.name, services, env_vars=props.get("env", {}))
            StateManager.update_resource(resource.name, "multi_service", props, "deployed")
        finally:
            mgr.close()
