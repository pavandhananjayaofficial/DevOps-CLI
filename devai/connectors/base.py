from typing import Dict, Any
from devai.utils.core.models import ActionType

class ConnectorBase:
    """
    Abstract base interface for all Infrastructure Connectors.
    Each connector (e.g., Docker, AWS, Terraform) must implement this.
    """
    
    def apply(self, resource_name: str, properties: Dict[str, Any]):
        """Executes a CREATE or UPDATE action deterministically."""
        raise NotImplementedError("Connectors must implement apply()")

    def destroy(self, resource_name: str, properties: Dict[str, Any]):
        """Executes a DELETE action deterministically."""
        raise NotImplementedError("Connectors must implement destroy()")

    def read_state(self, resource_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Reads the current real-world state to calculate drift."""
        raise NotImplementedError("Connectors must implement read_state()")
