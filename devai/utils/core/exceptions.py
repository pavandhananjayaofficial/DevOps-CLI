from enum import Enum

class DevAIException(Exception):
    """Base exception for all DevAI errors."""
    pass

class ValidationError(DevAIException):
    """Raised when a plan or configuration fails validation."""
    pass

class AIPlanningError(DevAIException):
    """Raised when the AI fails to generate a valid plan."""
    pass

class ExecutionError(DevAIException):
    """Raised when an operation fails during execution."""
    pass

class ApprovalRequiredError(DevAIException):
    """Raised when an action requires explicit user approval."""
    pass

class PolicyViolationError(DevAIException):
    """Raised when a plan violates a security or organizational policy."""
    pass
