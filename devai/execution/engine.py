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
                    
        SYSTEM_PROMPT = """
    You are an AI DevOps Architect. 
    Your job is to generate a valid multi-service deployment plan in JSON format.
    
    ### Guidelines:
    - ONLY output valid JSON.
    - Resources must be deterministic.
    - Valid types: multi_service_deployment, vps_server.
    
    ### Multi-Service Schema Example:
    {
      "resources": [
        {
          "name": "project_name",
          "type": "multi_service_deployment",
          "action": "CREATE",
          "properties": {
            "server": "server_alias_or_default",
            "services": [
              {
                "name": "api",
                "image": "my-api:latest",
                "ports": ["8000:8000"],
                "env": ["DB_HOST=postgres"]
              },
              {
                "name": "postgres",
                "image": "postgres:latest",
                "env": ["POSTGRES_PASSWORD=secret"]
              }
            ],
            "env": {
               "GLOBAL_KEY": "val"
            }
          }
        }
      ]
    }

    Orchestration Rules:
    - For `vps_server`, include a `commands` list for bootstrap (apt install docker, ufw allow 80).
    - For `multi_service_deployment`, define each service and their dependencies.
    - Always prefer Docker-based deployments on VPS.

    Example VPS Output:
    {
      "name": "VPS Setup",
      "version": "1.0",
      "resources": [
        {
          "name": "web-host",
          "type": "vps_server",
          "action": "setup",
          "properties": {
            "host": "1.2.3.4",
            "username": "root",
            "commands": ["apt update", "apt install -y docker.io"]
          }
        }
      ]
    }
    """
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
