import time
import httpx
from typing import Any
from llm_common.providers import ZaiClient
from llm_common.core import LLMMessage, LLMResponse, MessageRole, LLMUsage, RateLimitError, LLMError, TimeoutError

# Copy of the fixed ZaiClient.chat_completion method
async def fixed_chat_completion(
    self,
    messages: list[LLMMessage],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> LLMResponse:
    """Send chat completion request to z.ai (Monkeypatched Fix)."""
    model = model or self.config.default_model
    temperature = temperature if temperature is not None else self.config.temperature
    max_tokens = max_tokens or self.config.max_tokens

    # Estimate cost and check budget
    estimated_cost = self._estimate_cost(model, len(str(messages)), max_tokens)
    self.check_budget(estimated_cost)

    start_time = time.time()

    try:
        # Merge extra_body to avoid collision
        extra_body_arg = kwargs.pop("extra_body", {})
        default_extra = {"thinking": {"type": "enabled"}} if "glm-4.7" in model or "glm-4.6v" in model else {}
        merged_extra = {**default_extra, **extra_body_arg}

        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": (msg.role if hasattr(msg, "role") else msg["role"]),
                    "content": (msg.content if hasattr(msg, "content") else msg["content"]),
                }
                for msg in messages
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            extra_body=merged_extra,
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
        raise TimeoutError(
            f"Request timed out after {self.config.timeout}s: {e}", provider="zai"
        )
    except Exception as e:
        if "rate_limit" in str(e).lower():
            raise RateLimitError(str(e), provider="zai")
        raise LLMError(f"Chat completion failed (patched): {e}", provider="zai")

def apply_patch():
    print("🩹 Applying ZaiClient monkeypatch for extra_body collision...")
    ZaiClient.chat_completion = fixed_chat_completion
