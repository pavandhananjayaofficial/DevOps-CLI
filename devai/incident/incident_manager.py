from typing import Dict, Any, List, Optional
from devai.monitoring.system_monitor import SystemMonitor
from devai.logs.log_collector import LogCollector
from devai.ai.error_analyzer import AIErrorAnalyzer

class IncidentManager:
    """
    Manages autonomous incident detection and self-healing.
    Orchestrates monitoring, log analysis, and recovery actions.
    """

    def __init__(self, monitor: SystemMonitor, collector: LogCollector):
        self.monitor = monitor
        self.collector = collector
        self.analyzer = AIErrorAnalyzer()

    def detect_incident(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Probes project health to detect incidents."""
        # Scenario 1: Containers are down
        containers = self.monitor.get_container_status(project_name)
        if "Exit" in containers or "Down" in containers:
            return {
                "type": "container_failure",
                "project": project_name,
                "details": containers
            }
        
        # Scenario 2: Error spikes in logs (simplified)
        logs = self.collector.fetch_logs(project_name, tail=100)
        errors = self.collector.analyze_errors(logs)
        if len(errors) > 5:
            return {
                "type": "log_error_spike",
                "project": project_name,
                "details": f"Found {len(errors)} error lines in recent logs."
            }

        return None

    def resolve_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Runs AI analysis and returns a recovery plan."""
        project = incident["project"]
        print(f"[Self-Heal] 🚨 Incident detected: {incident['type']} on {project}. Analyzing...")
        
        logs = self.collector.fetch_logs(project, tail=200)
        errors = self.collector.analyze_errors(logs)
        suggestion = self.analyzer.analyze_and_suggest(project, errors)
        
        print(f"[Self-Heal] 🤖 AI Suggestion: {suggestion[:100]}...")
        
        # Automatic recovery strategy
        if incident["type"] == "container_failure":
            return {
                "resource_type": "docker_container",
                "name": project,
                "action": "restart",
                "properties": {"reason": "Autonomous self-healing: Container was found down."}
            }
        
        return {
            "resource_type": "deployment_fix",
            "name": project,
            "action": "notify",
            "properties": {"suggestion": suggestion}
        }
