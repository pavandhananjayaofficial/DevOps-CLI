import importlib
import importlib.metadata
from typing import Dict, Any, List, Optional

class PluginManager:
    """
    Handles dynamic discovery and loading of external DevAI plugins.
    Uses entry_points for extensibility.
    """

    def __init__(self, group_name: str = "devai.plugins"):
        self.group_name = group_name
        self.loaded_plugins: Dict[str, Any] = {}

    def discover_plugins(self) -> List[str]:
        """Discovers available plugins using entry_points."""
        try:
            eps = importlib.metadata.entry_points()
            if hasattr(eps, 'select'):
                plugins = eps.select(group=self.group_name)
            else:
                plugins = eps.get(self.group_name, [])
            return [p.name for p in plugins]
        except Exception:
            return []

    def load_plugin(self, name: str) -> Optional[Any]:
        """Loads a specific plugin by name."""
        try:
            eps = importlib.metadata.entry_points()
            if hasattr(eps, 'select'):
                p = eps.select(group=self.group_name, name=name)
                plugin_entry = next(iter(p), None)
            else:
                plugin_entry = next((p for p in eps.get(self.group_name, []) if p.name == name), None)
            
            if plugin_entry:
                loaded = plugin_entry.load()
                self.loaded_plugins[name] = loaded
                return loaded
        except Exception as e:
            print(f"[Plugin] ❌ Failed to load plugin {name}: {e}")
        return None
