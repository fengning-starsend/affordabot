"""z.ai LLM client implementation."""

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


class ZaiClient(LLMClient):
    """z.ai LLM client with OpenAI compatibility."""

    BASE_URL = "https://open.z.ai/api/v1"

    # Pricing per 1M tokens (as of 2025-01)
    PRICING = {
        "glm-4.5-air": {"input": 0.0, "output": 0.0},  # Free tier
        "glm-4.5": {"input": 0.50, "output": 0.50},
        "glm-4.6": {"input": 1.00, "output": 1.00},
    }

    def __init__(self, config: LLMConfig) -> None:
        """Initialize z.ai client.

        Args:
            config: LLM configuration

        Raises:
            APIKeyError: If API key is missing
        """
        super().__init__(config)

        if not config.api_key:
            raise APIKeyError("z.ai API key is required", provider="zai")

        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or self.BASE_URL,
            timeout=config.timeout,
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
        """Send chat completion request to z.ai.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to config.default_model)
            temperature: Sampling temperature (defaults to config.temperature)
            max_tokens: Maximum tokens to generate (defaults to config.max_tokens)
            **kwargs: Additional z.ai-specific parameters

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

            # Calculate actual cost
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
            cost = self._calculate_cost(model, usage)

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
                provider="zai",
                cost_usd=cost,
                latency_ms=latency_ms,
                metadata={"raw_response": response.model_dump()},
            )

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {self.config.timeout}s: {e}", provider="zai")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), provider="zai")
            raise LLMError(f"Chat completion failed: {e}", provider="zai")

    async def stream_completion(
        self,
        messages: list[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream chat completion response from z.ai.

        Args:
            messages: Conversation messages
            model: Model to use (defaults to config.default_model)
            temperature: Sampling temperature (defaults to config.temperature)
            max_tokens: Maximum tokens to generate (defaults to config.max_tokens)
            **kwargs: Additional z.ai-specific parameters

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
            raise TimeoutError(f"Stream timed out after {self.config.timeout}s: {e}", provider="zai")
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(str(e), provider="zai")
            raise LLMError(f"Stream completion failed: {e}", provider="zai")

    async def validate_api_key(self) -> bool:
        """Validate z.ai API key by making a minimal request.

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

        model_key = model.replace("z-ai/", "")
        pricing = self.PRICING.get(model_key, {"input": 1.0, "output": 1.0})

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
        model_key = model.replace("z-ai/", "")
        pricing = self.PRICING.get(model_key, {"input": 1.0, "output": 1.0})

        input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
