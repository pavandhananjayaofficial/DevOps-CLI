from __future__ import annotations

from typing import Optional

from devai.connectors.base import ConnectorBase
from devai.plugins.registry import PluginRegistry


class ExecutorRegistry:
    """
    Thin wrapper around the plugin registry so the execution layer only talks to
    a single typed abstraction.
    """

    def __init__(self, plugin_registry: Optional[PluginRegistry] = None):
        self.plugin_registry = plugin_registry or PluginRegistry()
        if not self.plugin_registry.connectors:
            self.plugin_registry.load_plugins()

    def get_connector(self, resource_type: str) -> Optional[ConnectorBase]:
        return self.plugin_registry.get_connector(resource_type)
