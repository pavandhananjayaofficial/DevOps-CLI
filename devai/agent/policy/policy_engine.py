from typing import List
from devai.utils.core.models import DeploymentPlan, PolicyDecision, PolicyViolation

class PolicyEngine:
    """
    Evaluates deployment plans against organizational and security policies.
    """
    def evaluate(self, plan: DeploymentPlan, environment: str) -> PolicyDecision:
        violations = []
        
        # Example Policy: No production deployments on Fridays (for fun/safety)
        # import datetime
        # if environment == "production" and datetime.datetime.now().weekday() == 4:
        #     violations.append(PolicyViolation(
        #         resource_name="global",
        #         policy_id="P001",
        #         message="Production deployments are restricted on Fridays.",
        #         severity="error"
        #     ))

        # Example Policy: Always require approval for high risk
        if plan.metadata.risk_level == "CRITICAL" and not plan.metadata.author == "human":
            violations.append(PolicyViolation(
                resource_name="plan",
                policy_id="P002",
                message="Critical risk plans must be authored by humans.",
                severity="error"
            ))

        allowed = len([v for v in violations if v.severity == "error"]) == 0
        return PolicyDecision(
            allowed=allowed,
            violations=violations,
            reason="Policy evaluation completed." if allowed else "Restricted by security policies."
        )
