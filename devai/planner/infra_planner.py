from typing import Dict, Any, List, Optional
from devai.ai.planner import AIPlanner

class InfraAnalyzer:
    """
    AI-powered infrastructure analyzer.
    Examines metrics and logs to detect bottlenecks and suggest optimizations.
    """

    def __init__(self):
        self.planner = AIPlanner()

    def analyze_infrastructure(self, health_data: Dict[str, Any], historical_patterns: Optional[str] = None) -> str:
        """
        Runs an AI analysis on the current infrastructure state.
        """
        metrics_summary = f"""
        Project: {health_data.get('project', 'unknown')}
        CPU Usage: {health_data.get('cpu_usage', 'N/A')}
        Memory Usage: {health_data.get('memory_usage', 'N/A')}
        Disk Usage: {health_data.get('disk_usage', 'N/A')}
        Containers:
        {health_data.get('containers', 'N/A')}
        """
        
        prompt = f"""
        As a senior Infrastructure Architect, analyze the following system state and suggest optimizations:
        
        ---
        {metrics_summary}
        ---
        
        {f"Historical context:\n{historical_patterns}" if historical_patterns else ""}
        
        Focus on:
        1. Scaling recommendations (Horizontal vs Vertical).
        2. Cost optimization.
        3. Potential reliability risks.
        
        Response format: plain text with bullet points.
        """

        try:
            raw = self.planner.provider.generate_response(
                prompt=prompt,
                system_prompt="You are an expert Cloud Infrastructure Architect. Provide deep analysis and optimization suggestions.",
                history=[]
            )
            return raw.strip()
        except Exception as e:
            return f"Infrastructure analysis failed: {e}\n\nMetrics Summary:\n{metrics_summary}"

    def detect_bottleneck(self, metrics: Dict[str, Any]) -> Optional[str]:
        """Simple heuristic for immediate bottleneck detection."""
        cpu = float(metrics.get("cpu_usage", "0").rstrip("%") or "0")
        mem = float(metrics.get("memory_usage", "0").split("/")[0].replace("Gi","").replace("Mi","") or "0")
        
        if cpu > 90.0:
            return "CPU_SATURATION"
        if "95%" in metrics.get("disk_usage", ""):
            return "DISK_FULL"
        
        return None
