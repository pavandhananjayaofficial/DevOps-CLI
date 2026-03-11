from collections import deque
from typing import Deque, Optional

from devai.audit.audit_logger import AuditLogger
from devai.connectors.base import ConnectorBase
from devai.utils.core.exceptions import DevAIException, ExecutionError
from devai.utils.core.models import DeploymentPlan, ExecutedResource, ExecutionReport, ResourceDefinition
from devai.utils.core.server_manager import ServerManager
from devai.execution.approvals import ApprovalCallback, ApprovalGate
from devai.execution.registry import ExecutorRegistry
from devai.database.models import StateManager
from devai.plugins.registry import PluginRegistry
from devai.server.deployment_manager import DeploymentManager


class ExecutionEngine:
    """
    Takes a strictly validated DeploymentPlan and executes the state changes deterministically.
    """

    def __init__(self, registry: Optional[PluginRegistry] = None, audit_logger: Optional[AuditLogger] = None):
        self.registry = ExecutorRegistry(registry)
        self.audit_logger = audit_logger or AuditLogger()

    def register_connector(self, resource_type: str, connector: ConnectorBase):
        """Plugin entry point for new infrastructure providers."""
        self.registry.plugin_registry.connectors[resource_type] = connector

    def execute(
        self,
        plan: DeploymentPlan,
        approval_callback: ApprovalCallback | None = None,
    ) -> ExecutionReport:
        """
        Executes the plan by building a dependency graph and running tasks in order.
        """
        self.audit_logger.record(
            "plan_execution_started",
            description=plan.description,
            environment=plan.metadata.environment,
            resource_count=len(plan.resources),
        )
        approval_gate = ApprovalGate(approval_callback)
        approval_gate.require_plan_approval(plan)

        adj_list = {resource.name: resource.depends_on for resource in plan.resources}
        in_degree = {resource.name: 0 for resource in plan.resources}

        for name in adj_list:
            for dependency in adj_list[name]:
                if dependency in in_degree:
                    in_degree[name] += 1

        queue: Deque[str] = deque([name for name, degree in in_degree.items() if degree == 0])
        sorted_order: list[str] = []

        while queue:
            node = queue.popleft()
            sorted_order.append(node)

            for name, dependencies in adj_list.items():
                if node in dependencies:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        if len(sorted_order) != len(plan.resources):
            raise ExecutionError("Circular dependency detected in the deployment plan DAG!")

        resource_map = {resource.name: resource for resource in plan.resources}
        report = ExecutionReport(plan_description=plan.description)
        for resource_name in sorted_order:
            resource = resource_map[resource_name]
            approval_gate.require_resource_approval(resource)
            report.executed_resources.append(self._execute_resource(resource))

        self.audit_logger.record(
            "plan_execution_completed",
            description=plan.description,
            executed_resources=[item.model_dump() for item in report.executed_resources],
        )
        return report

    def _execute_resource(self, resource: ResourceDefinition) -> ExecutedResource:
        """
        Routes the resource to the correct connector and handles orchestration logic.
        """
        self.audit_logger.record(
            "resource_execution_started",
            resource=resource.name,
            resource_type=resource.type,
            action=resource.action.value,
            risk=resource.risk.value,
        )

        if resource.type == "vps_server" and resource.action == ActionType.SETUP:
            ServerManager.setup_server(resource.name)
            result = ExecutedResource(
                name=resource.name,
                type=resource.type,
                action=resource.action,
                status="completed",
                detail="Server setup executed via ServerManager.",
            )
        elif resource.type == "multi_service_deployment":
            result = self._handle_orchestration(resource)
        else:
            connector = self.registry.get_connector(resource.type)
            if connector is None:
                raise ExecutionError(f"No executor registered for resource type '{resource.type}'.")

            if resource.action in {ActionType.CREATE, ActionType.UPDATE}:
                connector.apply(resource.name, resource.properties)
                StateManager.update_resource(resource.name, resource.type, resource.properties, "deployed")
                result = ExecutedResource(
                    name=resource.name,
                    type=resource.type,
                    action=resource.action,
                    status="completed",
                    detail="Connector apply completed.",
                )
            elif resource.action == ActionType.DELETE:
                connector.destroy(resource.name, resource.properties)
                StateManager.delete_resource(resource.name)
                result = ExecutedResource(
                    name=resource.name,
                    type=resource.type,
                    action=resource.action,
                    status="completed",
                    detail="Connector destroy completed.",
                )
            elif resource.action == ActionType.READ:
                connector.read_state(resource.name, resource.properties)
                result = ExecutedResource(
                    name=resource.name,
                    type=resource.type,
                    action=resource.action,
                    status="completed",
                    detail="Connector state read completed.",
                )
            else:
                raise ExecutionError(f"Unsupported action '{resource.action.value}' for resource '{resource.name}'.")

        self.audit_logger.record(
            "resource_execution_completed",
            resource=result.name,
            resource_type=result.type,
            action=result.action.value,
            status=result.status,
            detail=result.detail,
        )
        return result

    def _handle_orchestration(self, resource: ResourceDefinition) -> ExecutedResource:
        """
        High-level orchestration for multi-service deployments.
        """
        props = resource.properties
        target_server = props.get("server", "default")
        services = props.get("services", [])

        servers = ServerManager.list_servers()
        server = next((candidate for candidate in servers if candidate["name"] == target_server), None)
        if not server:
            raise DevAIException(f"Target server '{target_server}' not found.")

        manager = DeploymentManager(server["ip"], server["username"])
        try:
            manager.deploy_project(resource.name, services, env_vars=props.get("env", {}))
            StateManager.update_resource(resource.name, resource.type, props, "deployed")
            return ExecutedResource(
                name=resource.name,
                type=resource.type,
                action=resource.action,
                status="completed",
                detail=f"Deployed {len(services)} services to server '{target_server}'.",
            )
        finally:
            manager.close()
