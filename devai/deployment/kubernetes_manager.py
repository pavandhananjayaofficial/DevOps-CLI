import yaml
from typing import Dict, Any, List, Optional

class KubernetesManager:
    """
    Manages Kubernetes resource generation and deployment.
    Generates Deployment, Service, and Ingress manifests.
    """

    def generate_deployment(self, name: str, image: str, replicas: int = 1, port: int = 80, env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generates a K8s Deployment manifest."""
        env_list = [{"name": k, "value": v} for k, v in (env or {}).items()]
        
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name, "labels": {"app": name}},
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image,
                            "ports": [{"containerPort": port}],
                            "env": env_list
                        }]
                    }
                }
            }
        }
        return deployment

    def generate_service(self, name: str, port: int = 80, target_port: int = 80, type: str = "ClusterIP") -> Dict[str, Any]:
        """Generates a K8s Service manifest."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": name},
            "spec": {
                "selector": {"app": name},
                "ports": [{"protocol": "TCP", "port": port, "targetPort": target_port}],
                "type": type
            }
        }
        return service

    def save_manifests(self, name: str, manifests: List[Dict[str, Any]], output_path: str) -> str:
        """Saves a list of K8s manifests to a single YAML file."""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = "---\n".join([yaml.dump(m, default_flow_style=False) for m in manifests])
        with open(output_path, "w") as f:
            f.write(content)
        print(f"[K8s] ✅ Manifests saved to: {output_path}")
        return output_path

    def apply_manifests(self, manifest_path: str, context: Optional[str] = None) -> str:
        """Simulates applying manifests using kubectl."""
        # In a real app, this would run: kubectl apply -f manifest_path
        print(f"[K8s] 🚀 Applying manifests from {manifest_path}...")
        return f"Manifests in {manifest_path} applied successfully."
