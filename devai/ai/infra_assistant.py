from typing import Dict, Any, List, Optional
from devai.ai.planner import AIPlanner

class AIInfraAssistant:
    """
    Acts as a full AI Infrastructure Assistant.
    Provides architecture advice, detects misconfigurations, and recommends scaling.
    """

    def __init__(self):
        self.planner = AIPlanner()

    def suggest_architecture(self, requirement: str) -> str:
        """Suggests a best-practice architecture for a given requirement."""
        prompt = f"""
        As a senior Infrastructure Architect, suggest a modern, scalable, and secure architecture for:
        {requirement}
        
        Focus on:
        1. Component selection (Database, Cache, API).
        2. High availability and scaling.
        3. Security best practices.
        
        Provide a detailed technical blueprint.
        """
        try:
            res = self.planner.provider.generate_response(
                prompt=prompt,
                system_prompt="You are a senior AI Infrastructure Assistant.",
                history=[]
            )
            return res.strip()
        except Exception as e:
            return f"Failed to get architecture suggestion: {e}"

    def audit_misconfiguration(self, project_summary: str) -> str:
        """Audits a project for potential misconfigurations or security risks."""
        prompt = f"""
        Analyze the following project summary for misconfigurations, security risks, or anti-patterns:
        {project_summary}
        """
        # (AI loop here)
        return "No major misconfigurations detected (Mock)."
