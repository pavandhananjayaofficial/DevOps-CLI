import yaml
from typing import Dict, Any, List
from devai.connectors.vps_connector import VPSConnector
from devai.core.exceptions import DevAIException

class DeploymentManager:
    """
    Orchestrates the deployment of services to a remote VPS.
    Handles directory structure, compose generation, and execution.
    """
    
    def __init__(self, server_ip: str, username: str):
        self.connector = VPSConnector(server_ip, username)

    def deploy_project(self, project_name: str, services: List[Dict[str, Any]], env_vars: Dict[str, str] = {}):
        """
        Deploy a multi-service project.
        """
        print(f"🚢 Deploying project '{project_name}'...")
        
        # 1. Prepare structure
        self.connector.create_project_dir(project_name)
        
        # 2. Generate Docker Compose
        compose_content = self._generate_compose_yaml(services)
        
        # 3. Prepare .env content
        env_content = "\n".join([f"{k}={v}" for k, v in env_vars.items()])
        
        # 4. Upload files
        files = {
            "docker-compose.yml": compose_content,
            ".env": env_content
        }
        self.connector.deploy_files(project_name, files)
        
        # 5. Execute
        remote_path = f"/opt/devai/apps/{project_name}"
        self.connector.run_commands([
            f"cd {remote_path} && docker compose up -d"
        ])
        
        print(f"✅ Project '{project_name}' deployed successfully.")

    def _generate_compose_yaml(self, services: List[Dict[str, Any]]) -> str:
        compose_dict = {
            "version": "3.8",
            "services": {}
        }
        
        for svc in services:
            name = svc.get("name", "service")
            svc_config = {
                "image": svc.get("image"),
                "restart": "always",
                "environment": svc.get("env", [])
            }
            
            if "ports" in svc:
                svc_config["ports"] = svc["ports"]
                
            compose_dict["services"][name] = svc_config
            
        return yaml.dump(compose_dict)

    def close(self):
        self.connector.close()
