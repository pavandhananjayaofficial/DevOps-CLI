from typing import Dict, Any, List, Optional
from devai.execution.ssh_executor import SSHExecutor
from devai.utils.core.exceptions import DevAIException

class VPSConnector:
    """
    Refined SSH connector for managing remote VPS servers.
    Implements higher-level orchestration tasks.
    """
    
    def __init__(self, host: str, username: str, password: Optional[str] = None):
        self.executor = SSHExecutor(host, username, password)

    def setup_server(self):
        """Runs the automatic server setup sequence."""
        commands = [
            "apt-get update",
            "apt-get install -y docker.io docker-compose-plugin",
            "systemctl enable --now docker",
            "ufw allow 22/tcp",
            "ufw allow 80/tcp",
            "ufw allow 443/tcp",
            "ufw --force enable",
            "mkdir -p /opt/devai/apps"
        ]
        for cmd in commands:
            self.executor.execute(cmd)

    def create_project_dir(self, project_name: str):
        """Creates the standardized project structure on the remote host."""
        path = f"/opt/devai/apps/{project_name}"
        self.executor.execute(f"mkdir -p {path}/logs")
        print(f"Created project directory: {path}")

    def deploy_files(self, project_name: str, files: Dict[str, str]):
        """Transfers local files (like docker-compose.yml) to the project dir."""
        remote_base = f"/opt/devai/apps/{project_name}"
        for filename, content in files.items():
            # In a real app, write to a temp file first
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
                tf.write(content)
                temp_name = tf.name
            
            try:
                self.executor.upload_file(temp_name, f"{remote_base}/{filename}")
            finally:
                os.unlink(temp_name)

    def run_commands(self, commands: List[str]):
        """Runs a batch of commands."""
        for cmd in commands:
            self.executor.execute(cmd)

    def close(self):
        self.executor.close()
