from typing import Dict, Any, Optional
from devai.utils.core.exceptions import DevAIException


class AIErrorAnalyzer:
    """
    AI-powered error analysis for deployment failures.
    Extracts error lines from logs and asks the AI Planner for suggested fixes.
    
    Architecture rule: AI analyzes and suggests - never executes.
    """

    def analyze_and_suggest(self, project_name: str, error_lines: list, context: str = "") -> str:
        """
        Sends error lines to the AI provider and returns a fix suggestion.
        """
        from devai.planner.deployment_planner import AIPlanner

        if not error_lines:
            return "✅ No errors found in the provided logs."

        error_text = "\n".join(error_lines[:30])  # limit to 30 lines
        prompt = f"""
        The deployment of project '{project_name}' failed.
        
        Here are the error lines from the logs:
        ---
        {error_text}
        ---
        
        Based on these errors, provide:
        1. A root cause analysis (1-2 sentences)
        2. Step-by-step fix instructions
        3. A docker or shell command to apply the fix
        
        Response format: plain text, not JSON.
        """

        try:
            planner = AIPlanner()
            # Override the system prompt for analysis mode
            raw = planner.provider.generate_response(
                prompt=prompt,
                system_prompt="You are a senior DevOps engineer. Analyze deployment errors and suggest fixes. Be concise and practical.",
                history=[]
            )
            return raw.strip()
        except Exception as e:
            return f"AI analysis unavailable: {e}\n\nRaw errors:\n{error_text}"
