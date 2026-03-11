class DevAIException(Exception):
    """Base exception for all DevAI errors."""


class ValidationError(DevAIException):
    """Raised when a deployment plan fails deterministic validation."""


class ExecutionError(DevAIException):
    """Raised when an infrastructure connector fails to execute an action."""


class AIPlanningError(DevAIException):
    """Raised when the AI fails to generate a valid plan."""


class ApprovalRequiredError(DevAIException):
    """Raised when a high-risk action requires explicit human approval."""


class PolicyViolationError(DevAIException):
    """Raised when a plan violates non-overridable policy constraints."""
