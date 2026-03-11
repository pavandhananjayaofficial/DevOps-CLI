import json
from typing import List, Dict, Any
from devai.ai_providers.base import BaseAIProvider


class MockProvider(BaseAIProvider):
    def __init__(self, config: Dict[str, Any] = {}):
        self.model = config.get("model", "mock-model")

    def generate_response(self, prompt: str, system_prompt: str, history: List[dict] = []) -> str:
        return json.dumps(
            {
                "description": "Auto-generated plan",
                "version": "1.0",
                "metadata": {
                    "environment": "development",
                    "requires_manual_approval": False,
                },
                "resources": [
                    {
                        "name": "web-server",
                        "type": "docker_container",
                        "action": "create",
                        "risk": "low",
                        "properties": {
                            "image": "nginx:alpine",
                            "port": 80,
                        },
                        "depends_on": [],
                    }
                ],
            }
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "mock", "model": self.model}
