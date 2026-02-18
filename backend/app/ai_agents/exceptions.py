"""
Custom exceptions for AI agent ML pipeline failures.

These exceptions make ML pipeline failures LOUD and VISIBLE.
No silent continues. No hidden defaults. Fail explicitly.
"""


class MLPipelineFailure(Exception):
    """
    Base exception for ML pipeline failures.
    
    Raised when any part of the ML decision-making pipeline fails:
    - Perception layer failures
    - Reasoning layer failures
    - Action selection failures
    - Learning system failures
    
    This exception should NEVER be silently caught.
    It indicates the agent cannot make an informed decision.
    """
    pass


class ActionSelectionFailure(MLPipelineFailure):
    """
    Raised when action selection/scoring fails.
    
    This means the agent's learned action effectiveness model is broken.
    The agent cannot determine which action to take based on past learning.
    """
    pass


class ValidationSystemFailure(MLPipelineFailure):
    """
    Raised when The Stick's validation system fails.
    
    This means learning cannot be validated for correctness.
    Without validation, bad learning could become doctrine.
    Learning MUST NOT proceed when validation fails.
    """
    pass


class MetricsServiceFailure(MLPipelineFailure):
    """
    Raised when metrics service fails to provide fresh data.
    
    This means the agent cannot see current system state.
    Actions cannot be taken without knowing current metrics.
    Stale data is NOT acceptable.
    """
    pass


class DatabaseWriteFailure(MLPipelineFailure):
    """
    Raised when database write operations fail.
    
    This means learning records cannot be stored.
    If learning isn't persisted, the agent didn't actually learn.
    """
    pass


class PerceptionFailure(MLPipelineFailure):
    """
    Raised when perception layer fails to gather context.
    
    This means the agent cannot understand the current situation.
    Decisions cannot be made without proper perception.
    """
    pass


class ReasoningFailure(MLPipelineFailure):
    """
    Raised when reasoning layer fails to analyze situation.
    
    This means the agent cannot determine root cause or severity.
    Action selection requires valid reasoning.
    """
    pass
