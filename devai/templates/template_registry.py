import json
from typing import Dict, Any, List, Optional

class TemplateRegistry:
    """
    Registry of reusable infrastructure and application templates.
    """

    def __init__(self):
        self.templates = {
            "fastapi-basic": {
                "description": "FastAPI application with basic Docker configuration",
                "services": ["api"],
                "plan_hint": "Generate a single FastAPI docker container with port 8000"
            },
            "microservice-stack": {
                "description": "Standard Microservice architecture: API + Postgres + Redis",
                "services": ["api", "db", "cache"],
                "plan_hint": "Generate a 3-tier stack: FastAPI API, PostgreSQL 15, and Redis 7"
            }
        }

    def list_templates(self) -> List[Dict[str, str]]:
        return [{"id": k, "description": v["description"]} for k, v in self.templates.items()]

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return self.templates.get(template_id)
