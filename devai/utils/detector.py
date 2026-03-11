import os
from typing import List, Optional

class ProjectDetector:
    """
    Scans the current directory to detect project types and dependencies.
    Provides context for the AI Planner to make better deployment decisions.
    """
    
    @staticmethod
    def detect_project_type() -> Optional[str]:
        files = os.listdir(".")
        
        if "main.py" in files and any(f in os.listdir(".") for f in ["requirements.txt", "pyproject.toml"]):
            # Check for FastAPI/Flask in requirements
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", "r") as f:
                    content = f.read().lower()
                    if "fastapi" in content:
                        return "fastapi"
                    if "flask" in content:
                        return "flask"
            return "python_generic"
            
        if "package.json" in files:
            return "nodejs"
            
        if "Dockerfile" in files:
            return "dockerized"
            
        return None

    @staticmethod
    def get_project_summary() -> str:
        project_type = ProjectDetector.detect_project_type()
        if not project_type:
            return "Undetected project type."
            
        summary = f"Detected Project Type: {project_type}\n"
        
        if project_type == "fastapi" or project_type == "python_generic":
            if os.path.exists("requirements.txt"):
                summary += "Found requirements.txt\n"
        elif project_type == "nodejs":
            summary += "Found package.json\n"
            
        return summary
