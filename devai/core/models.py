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

    source: str = Field(default="ai_planner", description="Producer of the plan payload")
    environment: str = Field(default="development", description="Target environment for execution")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp for the generated plan",
    )
    requires_manual_approval: bool = Field(
        default=False,
        description="Whether the full plan requires an explicit human approval before execution",
    )


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


class ResourceDefinition(BaseModel):
    """
    Represents a single infrastructure or application resource to be managed.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Unique logical name for this resource in the plan")
    type: str = Field(..., description="The type of the resource (e.g., 'docker_container', 's3_bucket')")
    action: ActionType = Field(default=ActionType.CREATE, description="The action to perform on this resource")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Configuration properties for the resource")
    depends_on: List[str] = Field(default_factory=list, description="List of resource names this resource depends on")
    rationale: str = Field(default="", description="Why this resource is required")
    risk: RiskLevel = Field(default=RiskLevel.LOW, description="Estimated change risk for this resource")
    requires_approval: bool = Field(
        default=False,
        description="Whether this single resource requires explicit approval",
    )

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


class DeploymentPlan(BaseModel):
    """
    The structured output expected from the AI Planner.
    This defines the declarative state of the desired infrastructure.
    """

    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="1.0", description="Schema version")
    description: str = Field(..., description="A natural language summary of what this plan does")
    resources: List[ResourceDefinition] = Field(..., description="The list of resources to manage")
    metadata: PlanMetadata = Field(default_factory=PlanMetadata, description="Execution metadata and approval hints")

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
                "Plan dependencies must reference existing resources: "
                + ", ".join(unknown_dependencies)
            )

        if any(resource.requires_approval for resource in self.resources):
            self.metadata.requires_manual_approval = True
        return self


class IntentCategory(str, Enum):
    DEPLOY = "DEPLOY"
    DESTROY = "DESTROY"
    STATUS = "STATUS"
    DRIFT_CHECK = "DRIFT_CHECK"
    UNKNOWN = "UNKNOWN"


class ParsedIntent(BaseModel):
    """
    Represents the parsed natural language intent of the user.
    """

    original_text: str
    category: IntentCategory
    confidence: float
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
