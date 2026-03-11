class DevAIException(Exception):
    """Base exception for all DevAI errors."""

    pass


class ValidationError(DevAIException):
    """Raised when a deployment plan fails deterministic validation."""

    pass


class ExecutionError(DevAIException):
    """Raised when an infrastructure connector fails to execute an action."""

    pass


class AIPlanningError(DevAIException):
    """Raised when the AI fails to generate a valid plan."""

    pass


class ApprovalRequiredError(DevAIException):
    """Raised when a high-risk action requires explicit human approval."""

    pass


class PolicyViolationError(DevAIException):
    """Raised when a plan violates non-overridable policy constraints."""

    pass
