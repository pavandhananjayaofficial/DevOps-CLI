from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers (OpenAI, Anthropic, Local).
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str, history: List[dict] = []) -> str:
        """
        Generates a text response from the model.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns metadata about the model.
        """
        pass
