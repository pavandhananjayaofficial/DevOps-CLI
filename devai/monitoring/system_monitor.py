from typing import Dict, Any, Optional, List
from devai.execution.ssh_executor import SSHExecutor


class SystemMonitor:
    """
    Polls remote servers via SSH to collect health and resource metrics.
    Reports container status, CPU, and memory usage.
    """

    def __init__(self, host: str, username: str, password: Optional[str] = None):
        self.executor = SSHExecutor(host, username, password)

    def get_container_status(self, project_name: str) -> str:
        """Returns docker compose ps output for a given project."""
        cmd = f"cd /opt/devai/apps/{project_name} && docker compose ps --format 'table {{{{.Name}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'"
        return self.executor.execute(cmd)

    def get_system_stats(self) -> Dict[str, str]:
        """Returns CPU, Memory, and Disk usage."""
        cpu = self.executor.execute("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        mem = self.executor.execute("free -h | awk '/^Mem:/ {print $3\"/\"$2}'")
        disk = self.executor.execute("df -h / | awk 'NR==2 {print $3\"/\"$2\" (\"$5\" used)\"}'")
        return {"cpu": cpu, "memory": mem, "disk": disk}

    def get_health_summary(self, project_name: str) -> Dict[str, Any]:
        """Combined health report for a project and its host."""
        containers = self.get_container_status(project_name)
        stats = self.get_system_stats()
        return {
            "project": project_name,
            "containers": containers,
            "cpu_usage": stats.get("cpu", "N/A"),
            "memory_usage": stats.get("memory", "N/A"),
            "disk_usage": stats.get("disk", "N/A")
        }

    def close(self):
        self.executor.close()
