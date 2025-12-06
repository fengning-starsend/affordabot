"""Tests for LLM clients."""

import pytest

from llm_common.core import (
    APIKeyError,
    BudgetExceededError,
    LLMConfig,
    LLMMessage,
    MessageRole,
)
from llm_common.providers import OpenRouterClient, ZaiClient


def test_zai_client_requires_api_key():
    """Test ZaiClient raises error without API key."""
    config = LLMConfig(api_key="", default_model="glm-4.5")

    with pytest.raises(APIKeyError):
        ZaiClient(config)


def test_openrouter_client_requires_api_key():
    """Test OpenRouterClient raises error without API key."""
    config = LLMConfig(api_key="", default_model="gpt-4")

    with pytest.raises(APIKeyError):
        OpenRouterClient(config)


def test_zai_client_initialization():
    """Test ZaiClient initializes correctly."""
    config = LLMConfig(api_key="test-key", default_model="glm-4.5", provider="zai")

    client = ZaiClient(config)

    assert client.config.api_key == "test-key"
    assert client.config.default_model == "glm-4.5"
    assert client.get_total_cost() == 0.0
    assert client.get_request_count() == 0


def test_openrouter_client_initialization():
    """Test OpenRouterClient initializes correctly."""
    config = LLMConfig(
        api_key="test-key",
        default_model="gpt-4",
        provider="openrouter",
        metadata={"site_url": "https://test.com"},
    )

    client = OpenRouterClient(config)

    assert client.config.api_key == "test-key"
    assert client.config.default_model == "gpt-4"
    assert client.get_total_cost() == 0.0
    assert client.get_request_count() == 0


def test_budget_check_passes():
    """Test budget check passes when under limit."""
    config = LLMConfig(
        api_key="test-key",
        default_model="glm-4.5",
        budget_limit_usd=10.0,
        provider="zai",
    )

    client = ZaiClient(config)
    # Should not raise
    client.check_budget(0.01)


def test_budget_check_fails():
    """Test budget check fails when over limit."""
    config = LLMConfig(
        api_key="test-key",
        default_model="glm-4.5",
        budget_limit_usd=0.10,
        provider="zai",
    )

    client = ZaiClient(config)

    # Simulate some spending
    client._track_request(0.05)

    # This should raise BudgetExceededError
    with pytest.raises(BudgetExceededError):
        client.check_budget(0.10)


def test_cost_tracking():
    """Test cost tracking functionality."""
    config = LLMConfig(
        api_key="test-key",
        default_model="glm-4.5",
        track_costs=True,
        provider="zai",
    )

    client = ZaiClient(config)

    # Track some requests
    client._track_request(0.01)
    client._track_request(0.02)
    client._track_request(0.03)

    assert client.get_total_cost() == 0.06
    assert client.get_request_count() == 3


def test_reset_metrics():
    """Test resetting metrics."""
    config = LLMConfig(api_key="test-key", default_model="glm-4.5", provider="zai")

    client = ZaiClient(config)

    # Track some activity
    client._track_request(0.05)

    assert client.get_total_cost() == 0.05
    assert client.get_request_count() == 1

    # Reset
    client.reset_metrics()

    assert client.get_total_cost() == 0.0
    assert client.get_request_count() == 0


def test_zai_estimate_cost():
    """Test cost estimation for z.ai."""
    config = LLMConfig(api_key="test-key", default_model="glm-4.5", provider="zai")

    client = ZaiClient(config)

    # Free tier model
    cost = client._estimate_cost("glm-4.5-air", 1000, 100)
    assert cost == 0.0

    # Paid model (rough estimate)
    cost = client._estimate_cost("glm-4.5", 1000, 100)
    assert cost > 0.0


def test_openrouter_estimate_cost():
    """Test cost estimation for OpenRouter."""
    config = LLMConfig(api_key="test-key", default_model="gpt-4", provider="openrouter")

    client = OpenRouterClient(config)

    # Known model
    cost = client._estimate_cost("openai/gpt-4o-mini", 1000, 100)
    assert cost > 0.0

    # Unknown model (should use default pricing)
    cost = client._estimate_cost("unknown/model", 1000, 100)
    assert cost > 0.0


@pytest.mark.asyncio
async def test_zai_chat_completion_mock(mocker):
    """Test z.ai chat completion with mocked API."""
    config = LLMConfig(api_key="test-key", default_model="glm-4.5", provider="zai")

    client = ZaiClient(config)

    # Mock the OpenAI client response
    mock_response = mocker.MagicMock()
    mock_response.id = "test-123"
    mock_response.model = "glm-4.5"
    mock_response.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(content="Test response"), finish_reason="stop"
        )
    ]
    mock_response.usage = mocker.MagicMock(
        prompt_tokens=10, completion_tokens=20, total_tokens=30
    )
    mock_response.model_dump = lambda: {}

    # Use AsyncMock for async method
    mocker.patch.object(
        client.client.chat.completions,
        "create",
        return_value=mock_response,
        new_callable=mocker.AsyncMock,
    )

    messages = [LLMMessage(role=MessageRole.USER, content="Hello")]
    response = await client.chat_completion(messages)

    assert response.content == "Test response"
    assert response.model == "glm-4.5"
    assert response.usage.total_tokens == 30
    assert response.provider == "zai"
