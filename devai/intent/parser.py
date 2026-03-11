from enum import Enum
from pydantic import BaseModel, Field

from devai.core.models import ActionType


class IntentCategory(str, Enum):
    DEPLOY = "DEPLOY"
    DESTROY = "DESTROY"
    STATUS = "STATUS"
    DRIFT_CHECK = "DRIFT_CHECK"
    UNKNOWN = "UNKNOWN"


class ParsedIntent(BaseModel):
    original_text: str
    category: IntentCategory
    confidence: float = Field(default=0.5)


class IntentParser:
    def parse(self, text: str) -> ParsedIntent:
        normalized = text.lower()
        if any(word in normalized for word in ["deploy", "release", "ship"]):
            category = IntentCategory.DEPLOY
        elif any(word in normalized for word in ["delete", "destroy", "remove"]):
            category = IntentCategory.DESTROY
        elif any(word in normalized for word in ["status", "health", "logs"]):
            category = IntentCategory.STATUS
        elif "drift" in normalized:
            category = IntentCategory.DRIFT_CHECK
        else:
            category = IntentCategory.UNKNOWN
        return ParsedIntent(original_text=text, category=category, confidence=0.75)

