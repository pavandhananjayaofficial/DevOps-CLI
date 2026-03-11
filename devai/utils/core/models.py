from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    DEPLOY = "DEPLOY"
    DESTROY = "DESTROY"
    STATUS = "STATUS"
    DRIFT_CHECK = "DRIFT_CHECK"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PlanMetadata(BaseModel):
    author: str = "DevAI"
    created_at: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    estimated_cost: Optional[float] = None

class ResourceDefinition(BaseModel):
    name: str
    type: str  # e.g., "docker_container", "vps_server"
    action: ActionType
    properties: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)

class DeploymentPlan(BaseModel):
    project_name: str
    metadata: PlanMetadata
    resources: List[ResourceDefinition]
    summary: str

class PolicyViolation(BaseModel):
    resource_name: str
    policy_id: str
    message: str
    severity: str = "error"

class PolicyDecision(BaseModel):
    allowed: bool
    violations: List[PolicyViolation] = Field(default_factory=list)
    reason: Optional[str] = None

class ExecutedResource(BaseModel):
    name: str
    status: str
    output: str
    duration_ms: int

class ExecutionReport(BaseModel):
    success: bool
    executed_resources: List[ExecutedResource]
    summary: str


class ExecutionPreviewItem(BaseModel):
    order: int
    action_id: str
    summary: str
    risk: RiskLevel
    requires_approval: bool


class ExecutionPreview(BaseModel):
    plan_description: str
    environment: str
    requires_manual_approval: bool
    actions: List[ExecutionPreviewItem]
