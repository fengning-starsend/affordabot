"""OpenRouter LLM client implementation."""

import time
from typing import Any, AsyncIterator, Optional

import httpx
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from llm_common.core import (
    APIKeyError,
    LLMClient,
    LLMConfig,
    LLMError,
    LLMMessage,
    LLMResponse,
    LLMUsage,
    MessageRole,
    RateLimitError,
    TimeoutError,
)


class OpenRouterClient(LLMClient):
    """OpenRouter LLM client with access to 400+ models."""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Sample pricing (per 1M tokens) - OpenRouter provides dynamic pricing
    # These are rough estimates for common models
    PRICING_ESTIMATES = {
        "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
        "openai/gpt-4o": {"input": 2.5, "output": 10.0},
        "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "deepseek/deepseek-r1": {"input": 0.55, "output": 2.19},
        "google/gemini-2.0-flash-exp:free": {"input": 0.0, "output": 0.0},
        "z-ai/glm-4.5-air:free": {"input": 0.0, "output": 0.0},
        "z-ai/glm-4.5": {"input": 0.50, "output": 0.50},
    }

    def __init__(self, config: LLMConfig) -> None:
        """Initialize OpenRouter client.

        Args:
            config: LLM configuration

        Raises:
            APIKeyError: If API key is missing
        """
        super().__init__(config)

        if not config.api_key:
            raise APIKeyError("OpenRouter API key is required", provider="openrouter")

        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or self.BASE_URL,
            timeout=config.timeout,
            default_headers={
                "HTTP-Referer": config.metadata.get("site_url", "https://affordabot.com"),
                "X-Title": config.metadata.get("site_name", "Affordabot"),
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, TimeoutError)),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: list[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send chat completion request to OpenRouter.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to config.default_model)
            temperature: Sampling temperature (defaults to config.temperature)
            max_tokens: Maximum tokens to generate (defaults to config.max_tokens)
            **kwargs: Additional OpenRouter-specific parameters

        Returns:
            LLM response with content and metadata

        Raises:
            LLMError: If request fails
            BudgetExceededError: If budget limit reached
        """
        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        # Estimate cost and check budget
        estimated_cost = self._estimate_cost(model, len(str(messages)), max_tokens)
        self.check_budget(estimated_cost)

        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Calculate actual cost from OpenRouter's response if available
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

            # Try to get actual cost from OpenRouter's metadata
            cost = self._extract_cost_from_response(response) or self._calculate_cost(
                model, usage
            )

            # Track metrics
            if self.config.track_costs:
                self._track_request(cost)

            return LLMResponse(
                id=response.id,
                model=response.model,
                content=response.choices[0].message.content or "",
                role=MessageRole.ASSISTANT,
                finish_reason=response.choices[0].finish_reason,
                usage=usage,
                provider="openrouter",
                cost_usd=cost,
                latency_ms=latency_ms,
                metadata={"raw_response": response.model_dump()},
            )

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Request timed out after {self.config.timeout}s: {e}", provider="openrouter"
            )
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), provider="openrouter")
            raise LLMError(f"Chat completion failed: {e}", provider="openrouter")

    async def stream_completion(
        self,
        messages: list[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream chat completion response from OpenRouter.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to config.default_model)
            temperature: Sampling temperature (defaults to config.temperature)
            max_tokens: Maximum tokens to generate (defaults to config.max_tokens)
            **kwargs: Additional OpenRouter-specific parameters

        Yields:
            Response chunks as they arrive

        Raises:
            LLMError: If request fails
            BudgetExceededError: If budget limit reached
        """
        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        # Estimate cost and check budget
        estimated_cost = self._estimate_cost(model, len(str(messages)), max_tokens)
        self.check_budget(estimated_cost)

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": msg.role, "content": msg.content} for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Stream timed out after {self.config.timeout}s: {e}", provider="openrouter"
            )
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), provider="openrouter")
            raise LLMError(f"Stream completion failed: {e}", provider="openrouter")

    async def validate_api_key(self) -> bool:
        """Validate OpenRouter API key by making a minimal request.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            await self.client.chat.completions.create(
                model=self.config.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False

    def _estimate_cost(self, model: str, input_length: int, max_tokens: int) -> float:
        """Estimate cost of request.

        Args:
            model: Model name
            input_length: Approximate input length (chars)
            max_tokens: Maximum output tokens

        Returns:
            Estimated cost in USD
        """
        # Rough estimate: 4 chars per token
        input_tokens = input_length // 4

        pricing = self.PRICING_ESTIMATES.get(
            model, {"input": 1.0, "output": 5.0}  # Conservative default
        )

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (max_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def _calculate_cost(self, model: str, usage: LLMUsage) -> float:
        """Calculate actual cost based on usage.

        Args:
            model: Model name
            usage: Token usage

        Returns:
            Cost in USD
        """
        pricing = self.PRICING_ESTIMATES.get(
            model, {"input": 1.0, "output": 5.0}  # Conservative default
        )

        input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def _extract_cost_from_response(self, response: Any) -> Optional[float]:
        """Extract actual cost from OpenRouter's response metadata.

        OpenRouter includes cost information in the response headers/metadata.

        Args:
            response: OpenRouter response object

        Returns:
            Cost in USD if available, None otherwise
        """
        try:
            # OpenRouter may include cost in response metadata
            # This is implementation-specific and may need adjustment
            metadata = getattr(response, "metadata", {})
            if "cost" in metadata:
                return float(metadata["cost"])
        except (AttributeError, ValueError, TypeError):
            pass
        return None
