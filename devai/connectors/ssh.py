import paramiko
from typing import Dict, Any, Optional
from devai.connectors.base import ConnectorBase

class SSHConnector(ConnectorBase):
    """
    Connector for executing commands on a remote VPS via SSH.
    """
    
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _connect(self, properties: Dict[str, Any]):
        host = properties.get("host")
        port = properties.get("port", 22)
        username = properties.get("username")
        password = properties.get("password")
        key_filename = properties.get("key_filename")

        if not host or not username:
            raise ValueError("SSH Connector requires 'host' and 'username'.")

        self.client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            key_filename=key_filename
        )

    def apply(self, resource_name: str, properties: Dict[str, Any]):
        """
        Executes deployment commands on the remote host.
        """
        print(f"[SSH Connector] 🚀 Connecting to {properties.get('host')} for resource '{resource_name}'...")
        self._connect(properties)
        
        commands = properties.get("commands", [])
        if not commands:
            # Fallback or default behavior (e.g., standard deployment)
            print(f"[SSH Connector] No specific commands provided for {resource_name}. Using default setup.")
            commands = ["echo 'Setting up project...'"]

        for cmd in commands:
            print(f"[SSH Connector] ⚡ Executing: {cmd}")
            stdin, stdout, stderr = self.client.exec_command(cmd)
            # We could stream output here in the future
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"[SSH Connector] ❌ Command failed with exit code {exit_status}")
                print(stderr.read().decode())
            else:
                print(f"[SSH Connector] ✅ Success")

        self.client.close()

    def destroy(self, resource_name: str, properties: Dict[str, Any]):
        """
        Cleans up resources on the remote host.
        """
        print(f"[SSH Connector] 🧨 Cleaning up resource '{resource_name}' on {properties.get('host')}...")
        self._connect(properties)
        
        cleanup_commands = properties.get("cleanup_commands", [])
        for cmd in cleanup_commands:
            print(f"[SSH Connector] ⚡ Executing: {cmd}")
            self.client.exec_command(cmd)

        self.client.close()

    def read_state(self, resource_name: str) -> Dict[str, Any]:
        # Implementation for reading remote state (e.g., checking if process is running)
        return {"status": "unknown"}
