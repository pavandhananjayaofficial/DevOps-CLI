import json
from typing import Optional, List, Dict, Any
from devai.core.models import DeploymentPlan
from devai.core.exceptions import AIPlanningError
from devai.memory.history import HistoryManager
from devai.core.config import ConfigManager
from devai.ai.providers.openai_provider import OpenAIProvider
from devai.ai.providers.anthropic_provider import AnthropicProvider
from devai.ai.providers.mock_provider import MockProvider
from devai.ai.providers.llama_provider import LlamaProvider

class AIPlanner:
    """
    Orchestrates AI providers based on the user's configuration.
    """
    
    SYSTEM_PROMPT = """
    You are an AI DevOps Architect. 
    Your job is to generate a valid multi-service deployment plan in JSON format.
    
    ### Guidelines:
    - ONLY output valid JSON.
    - Resources must be deterministic.
    - Valid types: multi_service_deployment, vps_server.
    - Orchestration Rules:
        - For vps_server, include a 'commands' list for bootstrap.
        - Always prefer Docker-based deployments on VPS.
    
    ### Schema Example:
    {
      "resources": [
        {
          "name": "project_name",
          "type": "multi_service_deployment",
          "action": "CREATE",
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
        elif provider_type == "anthropic":
            return AnthropicProvider(config)
        elif provider_type == "llama":
            return LlamaProvider(config)
        else:
            return MockProvider(config)

    def generate_plan(self, prompt: str, context: str = "") -> str:
        # Save user message
        HistoryManager.add_message("user", prompt)
        history = HistoryManager.get_recent_history(limit=5)
        full_prompt = f"CONTEXT:\n{context}\n\nREQUEST: {prompt}" if context else prompt
        
        raw_output = self.provider.generate_response(
            prompt=full_prompt,
            system_prompt=self.SYSTEM_PROMPT,
            history=history
        )
            
        HistoryManager.add_message("ai", raw_output)
        return raw_output.strip()

    def get_active_model_info(self):
        return self.provider.get_model_info()
