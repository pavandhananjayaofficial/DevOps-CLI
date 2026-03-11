from typing import List, Dict, Any, Optional
from devai.memory.state_manager import StateManager
from devai.connectors.vps_connector import VPSConnector
from devai.core.exceptions import DevAIException

class ServerManager:
    """
    Business logic for managing remote VPS servers.
    Handles registration, removal, and health checks.
    """
    
    @staticmethod
    def add_server(name: str, ip: str, username: str):
        # 1. Check if name already exists
        existing = StateManager.get_servers()
        if any(s['name'] == name for s in existing):
            raise DevAIException(f"Server with name '{name}' already exists.")
            
        # 2. Add to database
        StateManager.add_server(name, ip, username, status="pending")
        print(f"Server '{name}' ({ip}) added. Run 'devai server setup {name}' to configure it.")

    @staticmethod
    def list_servers() -> List[Dict[str, Any]]:
        return StateManager.get_servers()

    @staticmethod
    def remove_server(name: str):
        StateManager.remove_server(name)
        print(f"Server '{name}' removed from registry.")

    @staticmethod
    def setup_server(name: str):
        # 1. Get server info
        servers = StateManager.get_servers()
        server = next((s for s in servers if s['name'] == name), None)
        if not server:
            raise DevAIException(f"Server '{name}' not found.")
            
        print(f"🚀 Starting automatic setup for {name} ({server['ip']})...")
        
        # 2. Connect and setup
        # In a real app, we'd get the password/key from the Vault
        connector = VPSConnector(server['ip'], server['username'])
        try:
            connector.setup_server()
            StateManager.update_server_status(name, "ready")
            print(f"✅ Server '{name}' is now ready!")
        finally:
            connector.close()
