"""Basic usage examples for llm-common."""

import asyncio
import os

from llm_common import (
    LLMConfig,
    LLMMessage,
    MessageRole,
    OpenRouterClient,
    ZaiClient,
)


async def example_zai_client() -> None:
    """Example: Using z.ai client for chat completion."""
    print("\n=== z.ai Client Example ===\n")

    config = LLMConfig(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        default_model="glm-4.5-air",  # Free tier
        temperature=0.7,
        max_tokens=100,
        provider="zai",
    )

    client = ZaiClient(config)

    messages = [
        LLMMessage(role=MessageRole.USER, content="What is the capital of California?")
    ]

    response = await client.chat_completion(messages)

    print(f"Model: {response.model}")
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.6f}")
    print(f"Latency: {response.latency_ms}ms")
    print(f"Tokens: {response.usage.total_tokens}")


async def example_openrouter_client() -> None:
    """Example: Using OpenRouter client with multiple models."""
    print("\n=== OpenRouter Client Example ===\n")

    config = LLMConfig(
        api_key=os.getenv("OPENROUTER_API_KEY", "your-openrouter-key"),
        default_model="google/gemini-2.0-flash-exp:free",
        temperature=0.7,
        max_tokens=100,
        provider="openrouter",
        metadata={"site_url": "https://affordabot.com", "site_name": "Affordabot"},
    )

    client = OpenRouterClient(config)

    messages = [
        LLMMessage(
            role=MessageRole.USER, content="Explain quantum computing in one sentence."
        )
    ]

    # Test multiple models
    models = [
        "google/gemini-2.0-flash-exp:free",
        "z-ai/glm-4.5-air:free",
        "openai/gpt-4o-mini",
    ]

    for model in models:
        print(f"\nTesting model: {model}")
        response = await client.chat_completion(messages, model=model)
        print(f"Response: {response.content[:100]}...")
        print(f"Cost: ${response.cost_usd:.6f}")
        print(f"Tokens: {response.usage.total_tokens}")


async def example_streaming() -> None:
    """Example: Streaming responses."""
    print("\n=== Streaming Example ===\n")

    config = LLMConfig(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        default_model="glm-4.5-air",
        provider="zai",
    )

    client = ZaiClient(config)

    messages = [
        LLMMessage(
            role=MessageRole.USER, content="Write a haiku about artificial intelligence."
        )
    ]

    print("Streaming response: ", end="", flush=True)
    async for chunk in client.stream_completion(messages):
        print(chunk, end="", flush=True)
    print("\n")


async def example_cost_tracking() -> None:
    """Example: Cost tracking and budget limits."""
    print("\n=== Cost Tracking Example ===\n")

    config = LLMConfig(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        default_model="glm-4.5",  # Paid model
        budget_limit_usd=0.10,  # $0.10 budget
        alert_threshold=0.5,  # Alert at 50%
        track_costs=True,
        provider="zai",
    )

    client = ZaiClient(config)

    messages = [LLMMessage(role=MessageRole.USER, content="Hello!")]

    # Make several requests
    for i in range(3):
        print(f"\nRequest {i + 1}:")
        response = await client.chat_completion(messages)
        print(f"Cost: ${response.cost_usd:.6f}")
        print(f"Total Cost: ${client.get_total_cost():.6f}")
        print(f"Total Requests: {client.get_request_count()}")


async def main() -> None:
    """Run all examples."""
    await example_zai_client()
    await example_openrouter_client()
    await example_streaming()
    await example_cost_tracking()


if __name__ == "__main__":
    asyncio.run(main())
