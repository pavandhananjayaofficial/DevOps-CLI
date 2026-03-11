from typing import List, Dict, Any
from devai.ai.providers.base import BaseAIProvider

class LlamaProvider(BaseAIProvider):
    """
    Placeholder/Mock for local llama.cpp / Ollama integration.
    """
    def __init__(self, config: Dict[str, Any]):
        self.model = config.get("model", "qwen-7b")
        self.endpoint = config.get("endpoint", "http://localhost:11434")

    def generate_response(self, prompt: str, system_prompt: str, history: List[dict] = []) -> str:
        # In a real app, this would use httpx to talk to Ollama or llama.cpp server
        return f"MOCK LOCAL RESPONSE ({self.model}): Plan for your request on {self.endpoint}."

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "llama", "model": self.model, "endpoint": self.endpoint}
