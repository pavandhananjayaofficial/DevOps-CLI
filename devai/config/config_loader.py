import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """
    Manages DevAI configuration stored in ~/.devai/config.yaml
    """
    CONFIG_DIR = Path.home() / ".devai"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    DEFAULT_CONFIG = {
        "models": {
            "openai": {
                "type": "api",
                "provider": "openai",
                "model": "gpt-4o"
            },
            "anthropic": {
                "type": "api",
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20240620"
            },
            "qwen_local": {
                "type": "local",
                "runtime": "llama_cpp",
                "model_path": ""
            }
        },
        "active_model": "openai",
        "web": {
            "port": 3000,
            "host": "localhost"
        }
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # Deep merge or simple update
                        self._merge_configs(self.config, user_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
        else:
            self.save_config()

    def _merge_configs(self, base: dict, override: dict):
        for key, value in override.items():
            if isinstance(value, dict) and key in base:
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def save_config(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            yaml.safe_dump(self.config, f)

    def get_active_model_config(self) -> Dict[str, Any]:
        active = self.config.get("active_model")
        return self.config.get("models", {}).get(active, {})

    def set_active_model(self, model_name: str):
        if model_name in self.config.get("models", {}):
            self.config["active_model"] = model_name
            self.save_config()
        else:
            raise ValueError(f"Model '{model_name}' not found in configuration.")

    def add_model(self, name: str, config: Dict[str, Any]):
        self.config.setdefault("models", {})[name] = config
        self.save_config()
