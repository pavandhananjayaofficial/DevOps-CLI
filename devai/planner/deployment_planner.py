import json
from typing import Any, Dict, List, Optional
from devai.utils.core.exceptions import AIPlanningError
from devai.knowledge.history import HistoryManager
from devai.config.config_loader import ConfigManager
from devai.ai_providers.openai_provider import OpenAIProvider
from devai.ai_providers.anthropic_provider import AnthropicProvider
from devai.ai_providers.mock_provider import MockProvider
from devai.ai_providers.llama_provider import LlamaProvider


class AIPlanner:
    """
    Orchestrates AI providers based on the user's configuration.
    """

    SYSTEM_PROMPT = """
    You are an AI DevOps Architect.
    Your job is to generate a valid deployment plan in JSON format.

    ### Guidelines:
    - ONLY output valid JSON.
    - Resources must be deterministic and schema-compliant.
    - NEVER output shell commands, SSH commands, kubectl commands, Docker CLI commands, scripts, or bootstrap command arrays.
    - Treat the execution layer as the only system allowed to translate structured actions into real commands.
    - Valid types: docker_container, multi_service_deployment, vps_server, s3_bucket, ec2_instance, kubernetes_deployment.
    - Always prefer Docker-based deployments on VPS.
    - Use metadata.requires_manual_approval=true for production changes, deletions, setup actions, or high-risk changes.

    ### Schema Example:
    {
      "metadata": {
        "environment": "development",
        "requires_manual_approval": false
      },
      "description": "Deploy a FastAPI app as a Docker container",
      "resources": [
        {
          "name": "project_name",
          "type": "multi_service_deployment",
          "action": "CREATE",
          "risk": "medium",
          "properties": {
            "server": "server_alias",
            "services": [
              {"name": "api", "image": "api:latest"}
            ]
          }
        }
      ]
    }
    """

    def __init__(self, provider_name: Optional[str] = None):
        self.config_manager = ConfigManager()
        if not provider_name:
            provider_name = self.config_manager.config.get("active_model", "openai")

        self.provider_config = self.config_manager.config.get("models", {}).get(provider_name, {})
        self.provider = self._get_provider(self.provider_config)

    def _get_provider(self, config: Dict[str, Any]):
        provider_type = config.get("provider")
        if provider_type == "openai":
            return OpenAIProvider(config)
        if provider_type == "anthropic":
            return AnthropicProvider(config)
        if provider_type == "llama":
            return LlamaProvider(config)
        return MockProvider(config)

    def generate_plan(self, prompt: str, context: str = "") -> str:
        HistoryManager.add_message("user", prompt)
        history = HistoryManager.get_recent_history(limit=5)
        full_prompt = f"CONTEXT:\n{context}\n\nREQUEST: {prompt}" if context else prompt

        raw_output = self.provider.generate_response(
            prompt=full_prompt,
            system_prompt=self.SYSTEM_PROMPT,
            history=history,
        )

        HistoryManager.add_message("ai", raw_output)
        return raw_output.strip()

    def get_active_model_info(self):
        return self.provider.get_model_info()
