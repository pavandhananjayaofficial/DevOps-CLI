from __future__ import annotations

from collections.abc import Callable

from devai.core.exceptions import ApprovalRequiredError
from devai.core.models import DeploymentPlan, ResourceDefinition


ApprovalCallback = Callable[[str], bool]


class ApprovalGate:
    """
    Centralizes human approval checks for high-risk plans and actions.
    """

    def __init__(self, approval_callback: ApprovalCallback | None = None):
        self.approval_callback = approval_callback

    def require_plan_approval(self, plan: DeploymentPlan) -> None:
        if not plan.metadata.requires_manual_approval:
            return
        self._request_approval(
            f"Plan '{plan.description}' targets {plan.metadata.environment} and contains high-risk actions."
        )

    def require_resource_approval(self, resource: ResourceDefinition) -> None:
        if not resource.requires_approval:
            return
        self._request_approval(
            f"Resource '{resource.name}' ({resource.type}/{resource.action.value}) is marked as {resource.risk.value} risk."
        )

    def _request_approval(self, prompt: str) -> None:
        if self.approval_callback is None:
            raise ApprovalRequiredError(prompt)
        if not self.approval_callback(prompt):
            raise ApprovalRequiredError(prompt)
