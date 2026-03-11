from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"

class ResourceDefinition(BaseModel):
    """
    Represents a single infrastructure or application resource to be managed.
    """
    name: str = Field(..., description="Unique logical name for this resource in the plan")
    type: str = Field(..., description="The type of the resource (e.g., 'docker_container', 's3_bucket')")
    action: ActionType = Field(default=ActionType.CREATE, description="The action to perform on this resource")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Configuration properties for the resource")
    depends_on: List[str] = Field(default_factory=list, description="List of resource names this resource depends on")

class DeploymentPlan(BaseModel):
    """
    The structured output expected from the AI Planner.
    This defines the declarative state of the desired infrastructure.
    """
    version: str = Field(default="1.0", description="Schema version")
    description: str = Field(..., description="A natural language summary of what this plan does")
    resources: List[ResourceDefinition] = Field(..., description="The list of resources to manage")

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
