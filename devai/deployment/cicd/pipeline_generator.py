import os
import yaml
from typing import Dict, Any, List, Optional


class PipelineGenerator:
    """
    Generates CI/CD pipeline configuration files.
    Currently supports GitHub Actions workflow YAML.
    """

    def generate_github_actions(
        self,
        project_name: str,
        server_ip: str,
        username: str = "root",
        services: Optional[List[str]] = None,
        branch: str = "main"
    ) -> str:
        """Returns a GitHub Actions YAML string for automated deploys."""
        services = services or ["app"]
        
        deploy_steps = "\n".join([
            f"          docker compose restart {svc}"
            for svc in services
        ])

        workflow = {
            "name": f"DevAI Deploy – {project_name}",
            "on": {
                "push": {"branches": [branch]}
            },
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Deploy to VPS",
                            "uses": "appleboy/ssh-action@master",
                            "with": {
                                "host": server_ip,
                                "username": username,
                                "key": "${{ secrets.SSH_PRIVATE_KEY }}",
                                "script": "\n".join([
                                    f"cd /opt/devai/apps/{project_name}",
                                    "git pull",
                                    "docker compose pull",
                                    f"docker compose up -d"
                                ])
                            }
                        }
                    ]
                }
            }
        }
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    def save_pipeline(self, project_path: str, project_name: str, server_ip: str, username: str = "root") -> str:
        """Writes the GitHub Actions workflow file into the project directory."""
        output_dir = os.path.join(project_path, ".github", "workflows")
        os.makedirs(output_dir, exist_ok=True)
        
        yaml_content = self.generate_github_actions(project_name, server_ip, username)
        output_path = os.path.join(output_dir, "devai-deploy.yml")
        
        with open(output_path, "w") as f:
            f.write(yaml_content)
        
        print(f"[CI/CD] ✅ Pipeline written to: {output_path}")
        return output_path
