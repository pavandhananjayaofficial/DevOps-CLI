from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    RESTART = "RESTART"
    NONE = "NONE"

class PlanMetadata(BaseModel):
    environment: str = "development"
    generated_at: datetime = Field(default_factory=datetime.now)
    requires_manual_approval: bool = False

class ResourceDefinition(BaseModel):
    name: str
    type: str
    action: ActionType
    risk: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    properties: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        v = v.upper()
        if v not in ["CREATE", "UPDATE", "DELETE", "RESTART", "NONE"]:
            raise ValueError(f"Invalid action: {v}")
        return v

class DeploymentPlan(BaseModel):
    metadata: PlanMetadata = Field(default_factory=PlanMetadata)
    description: str
    resources: List[ResourceDefinition] = Field(default_factory=list)

class PolicyViolation(BaseModel):
    policy: str
    message: str
    severity: str  # error, warning
    requires_approval: bool = False

class PolicyDecision(BaseModel):
    violations: List[PolicyViolation] = Field(default_factory=list)
    warnings: List[PolicyViolation] = Field(default_factory=list)
    requires_manual_approval: bool = False

class ExecutedResource(BaseModel):
    name: str
    type: str
    action: str
    status: str  # success, failed, skipped
    detail: str = ""

class ExecutionReport(BaseModel):
    plan_id: Optional[str] = None
    executed_resources: List[ExecutedResource] = Field(default_factory=list)
    summary: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
