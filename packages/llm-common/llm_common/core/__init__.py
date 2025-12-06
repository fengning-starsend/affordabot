"""Core abstractions and models."""

from llm_common.core.client import LLMClient
from llm_common.core.exceptions import (
    APIKeyError,
    BudgetExceededError,
    CacheError,
    LLMError,
    ModelNotFoundError,
    RateLimitError,
    TimeoutError,
)
from llm_common.core.models import (
    CostMetrics,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMUsage,
    MessageRole,
    WebSearchResponse,
    WebSearchResult,
)

__all__ = [
    # Client
    "LLMClient",
    # Exceptions
    "LLMError",
    "BudgetExceededError",
    "APIKeyError",
    "ModelNotFoundError",
    "RateLimitError",
    "TimeoutError",
    "CacheError",
    # Models
    "LLMConfig",
    "LLMMessage",
    "LLMResponse",
    "LLMUsage",
    "MessageRole",
    "WebSearchResult",
    "WebSearchResponse",
    "CostMetrics",
]
