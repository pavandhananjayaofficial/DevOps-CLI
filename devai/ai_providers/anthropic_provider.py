import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from anthropic.types import TextBlock
from devai.ai_providers.base import BaseAIProvider
from devai.utils.core.exceptions import AIPlanningError

class AnthropicProvider(BaseAIProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model = config.get("model", "claude-3-5-sonnet-20240620")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise AIPlanningError("ANTHROPIC_API_KEY not found in environment.")
        self.client = Anthropic(api_key=api_key)

    def generate_response(self, prompt: str, system_prompt: str, history: List[dict] = []) -> str:
        messages = []
        for h in history:
            messages.append(h)
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                temperature=0.0
            )
            
            full_text = ""
            for block in response.content:
                if isinstance(block, TextBlock):
                    full_text += block.text
            return full_text
        except Exception as e:
            raise AIPlanningError(f"Anthropic Error: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "anthropic", "model": self.model}
