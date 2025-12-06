"""Abstract LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from llm_common.core.models import LLMConfig, LLMMessage, LLMResponse


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize client with configuration.

        Args:
            config: LLM configuration
        """
        self.config = config
        self._total_cost_usd: float = 0.0
        self._request_count: int = 0

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send chat completion request.

        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            **kwargs: Provider-specific parameters

        Returns:
            LLM response with content and metadata

        Raises:
            LLMError: If request fails
            BudgetExceededError: If budget limit reached
        """
        pass

    @abstractmethod
    async def stream_completion(
        self,
        messages: list[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        """Stream chat completion response.

        Args:
            messages: Conversation messages
            model: Model to use (overrides default)
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            **kwargs: Provider-specific parameters

        Yields:
            Response chunks as they arrive

        Raises:
            LLMError: If request fails
            BudgetExceededError: If budget limit reached
        """
        pass

    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate API key is working.

        Returns:
            True if API key is valid, False otherwise
        """
        pass

    def get_total_cost(self) -> float:
        """Get total cost of all requests.

        Returns:
            Total cost in USD
        """
        return self._total_cost_usd

    def get_request_count(self) -> int:
        """Get total number of requests made.

        Returns:
            Request count
        """
        return self._request_count

    def reset_metrics(self) -> None:
        """Reset cost and request metrics."""
        self._total_cost_usd = 0.0
        self._request_count = 0

    def check_budget(self, estimated_cost: float) -> None:
        """Check if request would exceed budget.

        Args:
            estimated_cost: Estimated cost of next request in USD

        Raises:
            BudgetExceededError: If budget would be exceeded
        """
        if not self.config.budget_limit_usd:
            return

        projected_cost = self._total_cost_usd + estimated_cost
        if projected_cost > self.config.budget_limit_usd:
            from llm_common.core.exceptions import BudgetExceededError

            raise BudgetExceededError(
                current_cost=self._total_cost_usd,
                budget_limit=self.config.budget_limit_usd,
                estimated_cost=estimated_cost,
            )

        # Alert if approaching budget
        if projected_cost > self.config.budget_limit_usd * self.config.alert_threshold:
            percentage = (projected_cost / self.config.budget_limit_usd) * 100
            print(
                f"⚠️  Budget Alert: {percentage:.1f}% of budget used "
                f"(${projected_cost:.2f} / ${self.config.budget_limit_usd:.2f})"
            )

    def _track_request(self, cost: float) -> None:
        """Track request cost and count.

        Args:
            cost: Cost of request in USD
        """
        self._total_cost_usd += cost
        self._request_count += 1
