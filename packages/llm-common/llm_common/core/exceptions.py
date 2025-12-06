"""Custom exceptions for LLM framework."""


class LLMError(Exception):
    """Base exception for LLM errors."""

    def __init__(self, message: str, provider: str = "unknown") -> None:
        """Initialize error.

        Args:
            message: Error message
            provider: Provider name
        """
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class BudgetExceededError(LLMError):
    """Raised when budget limit is exceeded."""

    def __init__(
        self, current_cost: float, budget_limit: float, estimated_cost: float
    ) -> None:
        """Initialize error.

        Args:
            current_cost: Current total cost in USD
            budget_limit: Budget limit in USD
            estimated_cost: Estimated cost of next request in USD
        """
        self.current_cost = current_cost
        self.budget_limit = budget_limit
        self.estimated_cost = estimated_cost
        message = (
            f"Budget exceeded: ${current_cost:.2f} spent, ${budget_limit:.2f} limit. "
            f"Next request would cost ${estimated_cost:.2f}."
        )
        super().__init__(message, provider="budget")


class APIKeyError(LLMError):
    """Raised when API key is invalid or missing."""

    pass


class ModelNotFoundError(LLMError):
    """Raised when requested model is not available."""

    def __init__(self, model: str, provider: str = "unknown") -> None:
        """Initialize error.

        Args:
            model: Model name
            provider: Provider name
        """
        self.model = model
        super().__init__(f"Model '{model}' not found", provider=provider)


class RateLimitError(LLMError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        retry_after: int | None = None,
    ) -> None:
        """Initialize error.

        Args:
            message: Error message
            provider: Provider name
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(message, provider=provider)


class TimeoutError(LLMError):
    """Raised when request times out."""

    pass


class CacheError(LLMError):
    """Raised when cache operation fails."""

    pass
