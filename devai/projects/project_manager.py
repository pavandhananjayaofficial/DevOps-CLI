from typing import Dict, Any, List, Optional
import os

class ProjectManager:
    """
    Organizes deployments and resources into logical projects.
    """

    def __init__(self):
        # Projects could be stored in the main SQLite DB
        pass

    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        print(f"[Project] 📂 Creating project '{name}'...")
        # Simulate DB insert
        return {"name": name, "description": description, "created_at": "now", "resources": []}

    def list_projects(self) -> List[Dict[str, Any]]:
        return [{"name": "default", "description": "System default project"}]

    def get_project_resources(self, project_name: str) -> List[Dict[str, Any]]:
        # Link to StateManager
        return []

class EnvManager:
    """
    Manages deployment environments (dev, staging, prod).
    Handles config isolation and synchronization.
    """

    def __init__(self):
        self.environments = ["development", "staging", "production"]
        self.active_env = "development"

    def switch_env(self, name: str):
        if name in self.environments:
            self.active_env = name
            print(f"[Env] 🌐 Switched to global environment: {name}")
        else:
            print(f"[Env] ❌ Unknown environment: {name}")

    def get_env_config(self, env_name: str) -> Dict[str, str]:
        """Returns environment-specific variables."""
        return {
            "development": {"DEBUG": "true", "DB_HOST": "localhost"},
            "staging": {"DEBUG": "true", "DB_HOST": "staging-db.internal"},
            "production": {"DEBUG": "false", "DB_HOST": "prod-db.cloud"}
        }.get(env_name, {})
