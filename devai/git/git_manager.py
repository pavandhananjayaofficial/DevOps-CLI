import os
import shutil
import subprocess
from typing import Optional, Dict, Any

from devai.core.exceptions import DevAIException

class GitManager:
    """
    Manages Git repository interactions for source-based deployments.
    Supports cloning, pulling, and detecting project type from a repo URL.
    """

    def __init__(self, workspace_dir: str = os.path.expanduser("~/.devai/repos")):
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)

    def clone_or_pull(self, repo_url: str) -> str:
        """
        Clones a repo if it does not exist, otherwise pulls the latest changes.
        Returns the local path to the repo.
        """
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        local_path = os.path.join(self.workspace_dir, repo_name)

        if os.path.exists(local_path):
            print(f"[Git] 🔄 Pulling latest changes for '{repo_name}'...")
            result = subprocess.run(["git", "pull"], cwd=local_path, capture_output=True, text=True)
            if result.returncode != 0:
                raise DevAIException(f"git pull failed: {result.stderr}")
        else:
            print(f"[Git] 📥 Cloning {repo_url}...")
            result = subprocess.run(["git", "clone", repo_url, local_path], capture_output=True, text=True)
            if result.returncode != 0:
                raise DevAIException(f"git clone failed: {result.stderr}")
        
        print(f"[Git] ✅ Repo ready at: {local_path}")
        return local_path

    def get_repo_info(self, repo_path: str) -> Dict[str, Any]:
        """Returns metadata about the cloned repo."""
        result = subprocess.run(["git", "log", "-1", "--format=%H|%s|%an"], cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            return {"commit": "unknown", "message": "unknown", "author": "unknown"}
        parts = result.stdout.strip().split("|")
        return {
            "commit": parts[0] if len(parts) > 0 else "unknown",
            "message": parts[1] if len(parts) > 1 else "",
            "author": parts[2] if len(parts) > 2 else "",
            "path": repo_path
        }

    def clean_repo(self, repo_name: str):
        """Deletes a cloned repo from workspace."""
        local_path = os.path.join(self.workspace_dir, repo_name)
        if os.path.exists(local_path):
            shutil.rmtree(local_path)
            print(f"[Git] 🗑️  Removed repo: {repo_name}")
