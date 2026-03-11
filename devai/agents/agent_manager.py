from typing import Dict, Any, List, Optional
from devai.ai.planner import AIPlanner

class AgentManager:
    """
    Orchestrates specialized AI agents to handle complex DevOps tasks.
    """

    def __init__(self):
        self.planner = AIPlanner()
        self.agents = {
            "infra": "InfrastructureAgent",
            "deploy": "DeploymentAgent",
            "monitor": "MonitoringAgent",
            "security": "SecurityAgent"
        }

    def run_task(self, task_description: str) -> str:
        """Analyzes a task and delegates to appropriate agents."""
        print(f"[AgentManager] 🤖 Analyzing complex task: '{task_description}'")
        
        # In a real agentic system, this would be a multi-turn reasoning loop
        prompt = f"""
        You are an Agent Orchestrator. Break down this DevOps task into steps for sub-agents:
        Task: {task_description}
        
        Agents Available:
        - InfrastructureAgent: Provisioning, cluster management.
        - DeploymentAgent: Rolling updates, CI/CD, rollbacks.
        - MonitoringAgent: Analysis of logs and metrics.
        - SecurityAgent: Policy enforcement, vulnerability checks.
        
        Output a multi-agent plan.
        """
        try:
            res = self.planner.provider.generate_response(
                prompt=prompt,
                system_prompt="You are a senior DevOps Agent Manager.",
                history=[]
            )
            return res.strip()
        except Exception as e:
            return f"Agent orchestration failed: {e}"

    def get_agent_status(self) -> Dict[str, str]:
        return {k: "Active" for k in self.agents.keys()}
