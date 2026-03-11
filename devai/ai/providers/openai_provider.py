import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from devai.ai.providers.base import BaseAIProvider
from devai.core.exceptions import AIPlanningError

class OpenAIProvider(BaseAIProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model = config.get("model", "gpt-4o")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise AIPlanningError("OPENAI_API_KEY not found in environment.")
        self.client = OpenAI(api_key=api_key)

    def generate_response(self, prompt: str, system_prompt: str, history: List[dict] = []) -> str:
        messages: List[Any] = [{"role": "system", "content": system_prompt}]
        for h in history:
            messages.append(h)
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            raise AIPlanningError(f"OpenAI Error: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "openai", "model": self.model}
