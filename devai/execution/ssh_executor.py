from typing import List, Optional
import paramiko
from devai.utils.core.exceptions import DevAIException

class SSHExecutor:
    """
    Handles low-level SSH command execution and file transfers.
    Provides a reusable interface for remote operations.
    """
    
    def __init__(self, host: str, username: str, password: Optional[str] = None, key_path: Optional[str] = None):
        self.host = host
        self.username = username
        self.password = password
        self.key_path = key_path
        self._client = None
        self._sftp = None

    def _get_client(self):
        if self._client is None:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # prioritize key_path if provided
            self._client.connect(hostname=self.host, username=self.username, password=self.password, key_filename=self.key_path)
        return self._client

    def execute(self, command: str) -> str:
        """Executes a single command and returns stdout."""
        client = self._get_client()
        print(f"[SSH] Executing: {command}")
        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code != 0:
            err = stderr.read().decode().strip()
            raise DevAIException(f"Command '{command}' failed with exit code {exit_code}: {err}")
            
        return stdout.read().decode().strip()

    def upload_file(self, local_path: str, remote_path: str):
        """Uploads a file via SFTP."""
        client = self._get_client()
        if self._sftp is None:
            self._sftp = client.open_sftp()
        print(f"[SFTP] Uploading {local_path} -> {remote_path}")
        self._sftp.put(local_path, remote_path)

    def close(self):
        if self._sftp:
            self._sftp.close()
        if self._client:
            self._client.close()
