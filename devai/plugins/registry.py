import importlib.metadata
import logging
from typing import Dict, Type, Any, Optional
from devai.connectors.base import ConnectorBase

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Handles dynamic loading of DevAI plugins using Python entry points.
    """
    
    def __init__(self):
        self.connectors: Dict[str, ConnectorBase] = {}
        
    def load_plugins(self):
        """
        Discovers and loads plugins registered under 'devai.connectors' entry point.
        """
        # Load built-in connectors first
        from devai.connectors.docker import DockerConnector
        from devai.connectors.ssh import SSHConnector
        from devai.connectors.cloud_connector import CloudConnector
        self.connectors["docker_container"] = DockerConnector()
        self.connectors["ssh_server"] = SSHConnector()
        self.connectors["cloud_server"] = CloudConnector("mock")
        
        # Load external plugins
        eps = importlib.metadata.entry_points()
        if hasattr(eps, 'select'): # Python 3.10+
            connectors = eps.select(group='devai.connectors')
        else:
            connectors = eps.get('devai.connectors', [])
            
        for entry_point in connectors:
            try:
                connector_class = entry_point.load()
                if issubclass(connector_class, ConnectorBase):
                    name = entry_point.name
                    self.connectors[name] = connector_class()
                    logger.info(f"Loaded connector plugin: {name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {entry_point.name}: {e}")

    def get_connector(self, resource_type: str) -> Optional[ConnectorBase]:
        return self.connectors.get(resource_type)
