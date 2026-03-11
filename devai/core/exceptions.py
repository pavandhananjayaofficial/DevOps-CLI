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
