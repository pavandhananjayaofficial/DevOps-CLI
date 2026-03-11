from devai.utils.core.models import DeploymentPlan, PolicyDecision, PolicyViolation, RiskLevel


class PolicyEngine:
    """
    Enforces organizational infrastructure policies and constraints.
    Prevents insecure or non-compliant deployments.
    """

    def __init__(self):
        self.policies = [
            {"id": "no_root_containers", "severity": "ALARM"},
            {"id": "limit_replicas", "max": 10},
            {"id": "require_monitoring", "severity": "WARN"},
        ]

    def evaluate(self, plan: DeploymentPlan, env: str) -> PolicyDecision:
        """
        Validates a typed plan against active policies and returns a structured decision.
        """
        decision = PolicyDecision(environment=env)

        for resource in plan.resources:
            if env != "production":
                replicas = resource.properties.get("replicas", 1)
                if replicas > 5:
                    decision.violations.append(
                        PolicyViolation(
                            policy="replica_limit",
                            message=f"Environment {env} is limited to 5 replicas. Requested: {replicas}",
                            severity="error",
                        )
                    )

            if resource.type == "docker_container" and resource.properties.get("privileged", False):
                decision.violations.append(
                    PolicyViolation(
                        policy="no_privileged_containers",
                        message="Privileged containers are prohibited by security policy.",
                        severity="error",
                    )
                )

            if resource.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
                decision.warnings.append(
                    PolicyViolation(
                        policy="high_risk_change",
                        message=f"Resource '{resource.name}' is marked {resource.risk.value} risk.",
                        severity="warn",
                        requires_approval=True,
                    )
                )

            if env == "production" and resource.action.value in {"DELETE", "SETUP"}:
                decision.violations.append(
                    PolicyViolation(
                        policy="production_change_control",
                        message=f"Production action '{resource.action.value}' requires a manual approval checkpoint.",
                        severity="error",
                        requires_approval=True,
                    )
                )

        decision.requires_manual_approval = (
            plan.metadata.requires_manual_approval
            or any(item.requires_approval for item in decision.violations)
            or any(item.requires_approval for item in decision.warnings)
        )
        return decision

    def validate_plan(self, plan: DeploymentPlan, env: str) -> list[dict[str, str]]:
        """
        Backwards-compatible wrapper for older callers.
        """
        decision = self.evaluate(plan, env)
        return [item.model_dump() for item in decision.violations]
