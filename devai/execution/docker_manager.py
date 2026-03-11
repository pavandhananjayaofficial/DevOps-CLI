from typing import List, Optional
from devai.execution.ssh_executor import SSHExecutor

class DockerManager:
    """
    Handles remote Docker operations like viewing logs and restarting services.
    Uses SSHExecutor to run commands on the target VPS.
    """
    
    def __init__(self, host: str, username: str, password: Optional[str] = None):
        self.executor = SSHExecutor(host, username, password)

    def get_logs(self, project_name: str, service_name: Optional[str] = None, tail: int = 100) -> str:
        """Fetch logs for a specific project or service."""
        remote_path = f"/opt/devai/apps/{project_name}"
        cmd = f"cd {remote_path} && docker compose logs --tail={tail}"
        if service_name:
            cmd += f" {service_name}"
        return self.executor.execute(cmd)

    def get_status(self, project_name: str) -> str:
        """Check the status of a deployed project."""
        remote_path = f"/opt/devai/apps/{project_name}"
        cmd = f"cd {remote_path} && docker compose ps"
        return self.executor.execute(cmd)

    def restart_project(self, project_name: str, service_name: Optional[str] = None):
        """Restart a project or a specific service."""
        remote_path = f"/opt/devai/apps/{project_name}"
        cmd = f"cd {remote_path} && docker compose restart"
        if service_name:
            cmd += f" {service_name}"
        self.executor.execute(cmd)
        print(f"Restarted project/service in {project_name}")

    def stop_project(self, project_name: str):
        """Stop a project."""
        remote_path = f"/opt/devai/apps/{project_name}"
        cmd = f"cd {remote_path} && docker compose stop"
        self.executor.execute(cmd)
        print(f"Stopped project {project_name}")

    def close(self):
        self.executor.close()
