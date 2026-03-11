from __future__ import annotations

from devai.knowledge.state_manager import StateManager


class ServerManager:
    @staticmethod
    def add_server(name: str, ip: str, username: str, status: str = "ready"):
        StateManager.add_server(name, ip, username, status=status)

    @staticmethod
    def list_servers():
        return StateManager.get_servers()

    @staticmethod
    def remove_server(name: str):
        StateManager.remove_server(name)

    @staticmethod
    def setup_server(name: str):
        servers = StateManager.get_servers()
        server = next((item for item in servers if item["name"] == name), None)
        if server:
            StateManager.update_server_status(name, "ready")
        return {"name": name, "status": "ready"}
