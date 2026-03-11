import json
from typing import Optional, List, Dict, Any
from devai.core.models import DeploymentPlan
from devai.core.exceptions import AIPlanningError
from devai.memory.history import HistoryManager
from devai.core.config import ConfigManager
from devai.ai.providers.openai_provider import OpenAIProvider
from devai.ai.providers.anthropic_provider import AnthropicProvider
from devai.ai.providers.mock_provider import MockProvider

class AIPlanner:
    """
    Orchestrates AI providers based on the user's configuration.
    """
    
    SYSTEM_PROMPT = """
    You are an AI DevOps Architect. 
    Your job is to generate a valid infrastructure deployment plan in JSON format.
    Rules:
    - ONLY output valid JSON.
    - Resources must be deterministic.
    - Valid types: docker_container, s3_bucket, ec2_instance, kubernetes_deployment.
    - Valid actions: create, update, delete.
    Example output format:
    {
      "name": "Project Name",
      "version": "1.0",
      "resources": [
        {
          "name": "srv",
          "type": "docker_container",
          "action": "create",
          "properties": {"image": "nginx"},
          "depends_on": []
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
        else:
            return MockProvider(config)

    def generate_plan(self, prompt: str) -> str:
        """
        Takes the user intent and asks the AI to generate a JSON plan.
        """
        # Save user message
        HistoryManager.add_message("user", prompt)
        
        # Get context
        history = HistoryManager.get_recent_history(limit=5)
        
        raw_output = self.provider.generate_response(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            history=history
        )
            
        # Save AI response
        HistoryManager.add_message("ai", raw_output)
            
        # Clean up potential markdown formatting
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3]
        elif raw_output.startswith("```"):
            raw_output = raw_output[3:-3]
            
        return raw_output.strip()

    def get_active_model_info(self):
        return self.provider.get_model_info()
