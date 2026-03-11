from typing import Dict, Any, List, Optional

class PolicyEngine:
    """
    Enforces organizational infrastructure policies and constraints.
    Prevents insecure or non-compliant deployments.
    """

    def __init__(self):
        self.policies = [
            {"id": "no_root_containers", "severity": "ALARM"},
            {"id": "limit_replicas", "max": 10},
            {"id": "require_monitoring", "severity": "WARN"}
        ]

    def validate_plan(self, plan: Dict[str, Any], env: str) -> List[Dict[str, str]]:
        """
        Validates an AI-generated plan against active policies.
        Returns a list of violations.
        """
        violations = []
        
        for resource in plan.get("resources", []):
            # 1. Limit replicas in non-prod
            if env != "production":
                replicas = resource.get("properties", {}).get("replicas", 1)
                if replicas > 5:
                    violations.append({
                        "policy": "replica_limit",
                        "message": f"Environment {env} is limited to 5 replicas. Requested: {replicas}"
                    })

            # 2. Prevent privileged containers (MOCK)
            if resource.get("type") == "docker_container":
                if resource.get("properties", {}).get("privileged", False):
                    violations.append({
                        "policy": "no_privileged_containers",
                        "message": "Privileged containers are prohibited by security policy."
                    })

        return violations
