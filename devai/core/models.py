from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"
    SETUP = "SETUP"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlanMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(default="ai_planner")
    environment: str = Field(default="development")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    requires_manual_approval: bool = Field(default=False)


class PolicyViolation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy: str
    message: str
    severity: str = "error"
    requires_approval: bool = False


class PolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    environment: str
    violations: List[PolicyViolation] = Field(default_factory=list)
    warnings: List[PolicyViolation] = Field(default_factory=list)
    requires_manual_approval: bool = False


class ExecutedResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    action: ActionType
    status: str
    detail: str = ""


class ExecutionReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_description: str
    executed_resources: List[ExecutedResource] = Field(default_factory=list)


class PlannedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    resource_name: str
    resource_type: str
    operation: ActionType
    summary: str
    risk: RiskLevel
    requires_approval: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionPreviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order: int
    action_id: str
    summary: str
    risk: RiskLevel
    requires_approval: bool


class ExecutionPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_description: str
    environment: str
    requires_manual_approval: bool
    actions: List[ExecutionPreviewItem] = Field(default_factory=list)


class ResourceDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    action: ActionType = Field(default=ActionType.CREATE)
    properties: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    rationale: str = Field(default="")
    risk: RiskLevel = Field(default=RiskLevel.LOW)
    requires_approval: bool = Field(default=False)

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def set_default_approval_flags(self) -> "ResourceDefinition":
        if self.action in {ActionType.DELETE, ActionType.SETUP} or self.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            self.requires_approval = True
        return self

    def to_action(self) -> PlannedAction:
        if self.type == "docker_container":
            image = self.properties.get("image", "unknown-image")
            summary = f"{self.action.value.title()} Docker container '{self.name}' using image '{image}'."
        elif self.type == "multi_service_deployment":
            services = self.properties.get("services", [])
            server = self.properties.get("server", "default")
            summary = f"{self.action.value.title()} multi-service deployment '{self.name}' on server '{server}' with {len(services)} service(s)."
        elif self.type == "vps_server" and self.action == ActionType.SETUP:
            summary = f"Set up VPS server '{self.name}'."
        else:
            summary = f"{self.action.value.title()} resource '{self.name}' of type '{self.type}'."

        return PlannedAction(
            action_id=f"{self.name}:{self.action.value.lower()}",
            resource_name=self.name,
            resource_type=self.type,
            operation=self.action,
            summary=summary,
            risk=self.risk,
            requires_approval=self.requires_approval,
            metadata={
                "depends_on": self.depends_on,
                "properties": self.properties,
            },
        )


class DeploymentPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="1.0")
    description: str
    resources: List[ResourceDefinition]
    metadata: PlanMetadata = Field(default_factory=PlanMetadata)

    @model_validator(mode="before")
    @classmethod
    def map_legacy_fields(cls, value: Any) -> Any:
        if isinstance(value, dict) and "description" not in value and "name" in value:
            value = dict(value)
            value["description"] = value.pop("name")
        return value

    @model_validator(mode="after")
    def validate_graph(self) -> "DeploymentPlan":
        names = [resource.name for resource in self.resources]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError(f"Duplicate resource names are not allowed: {', '.join(sorted(duplicates))}")

        unknown_dependencies = sorted(
            {
                dependency
                for resource in self.resources
                for dependency in resource.depends_on
                if dependency not in names
            }
        )
        if unknown_dependencies:
            raise ValueError(
                "Plan dependencies must reference existing resources: " + ", ".join(unknown_dependencies)
            )

        if any(resource.requires_approval for resource in self.resources):
            self.metadata.requires_manual_approval = True
        return self

    def to_actions(self) -> List[PlannedAction]:
        return [resource.to_action() for resource in self.resources]

    def to_preview(self) -> ExecutionPreview:
        return ExecutionPreview(
            plan_description=self.description,
            environment=self.metadata.environment,
            requires_manual_approval=self.metadata.requires_manual_approval,
            actions=[
                ExecutionPreviewItem(
                    order=index,
                    action_id=action.action_id,
                    summary=action.summary,
                    risk=action.risk,
                    requires_approval=action.requires_approval,
                )
                for index, action in enumerate(self.to_actions(), start=1)
            ],
        )
