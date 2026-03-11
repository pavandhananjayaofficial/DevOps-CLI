import unittest

from devai.core.exceptions import ApprovalRequiredError, ValidationError
from devai.core.models import ActionType, DeploymentPlan, ResourceDefinition, RiskLevel
from devai.execution.engine import ExecutionEngine
from devai.memory.database import init_db
from devai.plugins.registry import PluginRegistry
from devai.policy.policy_engine import PolicyEngine
from devai.validation.validator import SchemaValidator


class DummyConnector:
    def __init__(self):
        self.applied = []
        self.destroyed = []

    def apply(self, resource_name, properties):
        self.applied.append((resource_name, properties))

    def destroy(self, resource_name, properties):
        self.destroyed.append((resource_name, properties))

    def read_state(self, resource_name, properties):
        return {"name": resource_name, "properties": properties}


class SafetyPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_validator_rejects_direct_command_fields(self):
        validator = SchemaValidator()
        raw_plan = {
            "description": "Unsafe plan",
            "resources": [
                {
                    "name": "bad-container",
                    "type": "docker_container",
                    "action": "CREATE",
                    "properties": {
                        "image": "nginx:alpine",
                        "command": "docker run nginx",
                    },
                }
            ],
        }

        with self.assertRaises(ValidationError):
            validator.validate_plan(raw_plan)

    def test_policy_engine_requires_approval_for_production_delete(self):
        plan = DeploymentPlan(
            description="Delete API",
            metadata={"environment": "production"},
            resources=[
                ResourceDefinition(
                    name="api",
                    type="docker_container",
                    action=ActionType.DELETE,
                    properties={"image": "api:v1"},
                    risk=RiskLevel.HIGH,
                )
            ],
        )

        decision = PolicyEngine().evaluate(plan, "production")

        self.assertTrue(decision.requires_manual_approval)
        self.assertTrue(any(item.policy == "production_change_control" for item in decision.violations))

    def test_plan_converts_resources_into_typed_actions(self):
        plan = DeploymentPlan(
            description="Deploy app",
            resources=[
                ResourceDefinition(
                    name="api",
                    type="docker_container",
                    action=ActionType.CREATE,
                    properties={"image": "api:v2"},
                ),
                ResourceDefinition(
                    name="platform",
                    type="multi_service_deployment",
                    action=ActionType.UPDATE,
                    properties={
                        "server": "staging",
                        "services": [
                            {"name": "api", "image": "api:v2"},
                            {"name": "worker", "image": "worker:v2"},
                        ],
                    },
                    depends_on=["api"],
                    risk=RiskLevel.MEDIUM,
                ),
            ],
        )

        actions = plan.to_actions()

        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].resource_name, "api")
        self.assertIn("Docker container", actions[0].summary)
        self.assertIn("multi-service deployment", actions[1].summary)

    def test_execution_engine_blocks_high_risk_plan_without_approval(self):
        registry = PluginRegistry()
        connector = DummyConnector()
        registry.connectors["docker_container"] = connector

        plan = DeploymentPlan(
            description="High risk deploy",
            resources=[
                ResourceDefinition(
                    name="api",
                    type="docker_container",
                    action=ActionType.CREATE,
                    properties={"image": "api:v2"},
                    risk=RiskLevel.HIGH,
                )
            ],
        )

        engine = ExecutionEngine(registry=registry)
        with self.assertRaises(ApprovalRequiredError):
            engine.execute(plan)

    def test_execution_engine_preview_respects_dependency_order(self):
        registry = PluginRegistry()
        connector = DummyConnector()
        registry.connectors["docker_container"] = connector

        plan = DeploymentPlan(
            description="Preview deploy",
            resources=[
                ResourceDefinition(
                    name="db",
                    type="docker_container",
                    action=ActionType.CREATE,
                    properties={"image": "postgres:15"},
                ),
                ResourceDefinition(
                    name="api",
                    type="docker_container",
                    action=ActionType.CREATE,
                    properties={"image": "api:v2"},
                    depends_on=["db"],
                ),
            ],
        )

        engine = ExecutionEngine(registry=registry)
        preview = engine.preview(plan)

        self.assertEqual(preview.actions[0].action_id, "db:create")
        self.assertEqual(preview.actions[1].action_id, "api:create")

    def test_execution_engine_runs_with_explicit_approval(self):
        registry = PluginRegistry()
        connector = DummyConnector()
        registry.connectors["docker_container"] = connector

        plan = DeploymentPlan(
            description="Approved deploy",
            resources=[
                ResourceDefinition(
                    name="api",
                    type="docker_container",
                    action=ActionType.CREATE,
                    properties={"image": "api:v2"},
                )
            ],
        )

        engine = ExecutionEngine(registry=registry)
        report = engine.execute(plan, approval_callback=lambda _: True)

        self.assertEqual(len(report.executed_resources), 1)
        self.assertEqual(connector.applied[0][0], "api")


if __name__ == "__main__":
    unittest.main()
