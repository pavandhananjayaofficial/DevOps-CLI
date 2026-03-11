from typing import Dict, Any, List, Optional
from devai.monitoring.system_monitor import SystemMonitor

class ScaleController:
    """
    Autonomous scaling logic based on system metrics.
    Triggers horizontal scaling when thresholds are crossed.
    """

    def __init__(self, cpu_threshold: float = 80.0, mem_threshold: float = 85.0):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold

    def evaluate_scaling(self, project_name: str, health_summary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Determines if a project needs scaling based on its health summary.
        Returns a scaling plan if needed.
        """
        # Parse CPU usage (e.g., "75.5")
        cpu_usage = float(health_summary.get("cpu_usage", "0").rstrip("%") or "0")
        
        if cpu_usage > self.cpu_threshold:
            print(f"[Autoscale] 📈 CPU {cpu_usage}% exceeds threshold {self.cpu_threshold}%. Recommending scale-up.")
            return {
                "action": "scale_up",
                "project": project_name,
                "reason": f"CPU usage at {cpu_usage}%"
            }
        
        # Add logic for scale-down if usage is very low (e.g. < 10%)
        if cpu_usage < 5.0:
            print(f"[Autoscale] 📉 CPU {cpu_usage}% is very low. Recommending scale-down for cost saving.")
            return {
                "action": "scale_down",
                "project": project_name,
                "reason": f"CPU usage low at {cpu_usage}%"
            }

        return None

    def generate_scaling_plan(self, scaling_decision: Dict[str, Any], current_replicas: int) -> Dict[str, Any]:
        """Calculates new replica count."""
        action = scaling_decision["action"]
        if action == "scale_up":
            new_count = current_replicas + 1
        elif action == "scale_down":
            new_count = max(1, current_replicas - 1)
        else:
            new_count = current_replicas

        return {
            "resource_type": "k8s_deployment",
            "name": scaling_decision["project"],
            "action": "update",
            "properties": {"replicas": new_count},
            "reason": scaling_decision["reason"]
        }
