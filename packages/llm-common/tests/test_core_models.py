"""Tests for core data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from llm_common.core import (
    CostMetrics,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMUsage,
    MessageRole,
    WebSearchResponse,
    WebSearchResult,
)


def test_message_role_enum():
    """Test MessageRole enum."""
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    assert MessageRole.SYSTEM == "system"


def test_llm_message_creation():
    """Test LLMMessage creation."""
    msg = LLMMessage(role=MessageRole.USER, content="Hello!")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello!"
    assert msg.name is None


def test_llm_usage_creation():
    """Test LLMUsage creation."""
    usage = LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30


def test_llm_response_creation():
    """Test LLMResponse creation."""
    usage = LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)

    response = LLMResponse(
        id="test-123",
        model="gpt-4",
        content="Hello!",
        finish_reason="stop",
        usage=usage,
        provider="openai",
        cost_usd=0.001,
    )

    assert response.id == "test-123"
    assert response.model == "gpt-4"
    assert response.content == "Hello!"
    assert response.provider == "openai"
    assert response.cost_usd == 0.001
    assert isinstance(response.created_at, datetime)


def test_llm_config_defaults():
    """Test LLMConfig default values."""
    config = LLMConfig(api_key="test-key", default_model="gpt-4")

    assert config.api_key == "test-key"
    assert config.default_model == "gpt-4"
    assert config.temperature == 0.7
    assert config.max_tokens == 4096
    assert config.timeout == 60
    assert config.max_retries == 3
    assert config.track_costs is True
    assert config.provider == "openrouter"


def test_llm_config_custom_values():
    """Test LLMConfig with custom values."""
    config = LLMConfig(
        api_key="test-key",
        default_model="gpt-4",
        temperature=0.5,
        max_tokens=2048,
        timeout=30,
        budget_limit_usd=10.0,
        provider="zai",
    )

    assert config.temperature == 0.5
    assert config.max_tokens == 2048
    assert config.timeout == 30
    assert config.budget_limit_usd == 10.0
    assert config.provider == "zai"


def test_web_search_result_creation():
    """Test WebSearchResult creation."""
    result = WebSearchResult(
        url="https://example.com",
        title="Example",
        snippet="This is an example",
        domain="example.com",
    )

    assert result.url == "https://example.com"
    assert result.title == "Example"
    assert result.snippet == "This is an example"
    assert result.domain == "example.com"


def test_web_search_response_creation():
    """Test WebSearchResponse creation."""
    results = [
        WebSearchResult(
            url="https://example.com",
            title="Example",
            snippet="Test",
            domain="example.com",
        )
    ]

    response = WebSearchResponse(
        query="test query",
        results=results,
        total_results=1,
        search_time_ms=100,
        cached=False,
        cost_usd=0.01,
    )

    assert response.query == "test query"
    assert len(response.results) == 1
    assert response.total_results == 1
    assert response.cached is False
    assert response.cost_usd == 0.01


def test_cost_metrics_creation():
    """Test CostMetrics creation."""
    metrics = CostMetrics(
        provider="openai",
        model="gpt-4",
        operation="chat",
        cost_usd=0.05,
        tokens_used=1000,
    )

    assert metrics.provider == "openai"
    assert metrics.model == "gpt-4"
    assert metrics.operation == "chat"
    assert metrics.cost_usd == 0.05
    assert metrics.tokens_used == 1000
    assert isinstance(metrics.timestamp, datetime)


def test_invalid_message_role():
    """Test invalid message role."""
    with pytest.raises(ValidationError):
        LLMMessage(role="invalid", content="test")


def test_invalid_operation_type():
    """Test invalid operation type in CostMetrics."""
    with pytest.raises(ValidationError):
        CostMetrics(
            provider="openai",
            model="gpt-4",
            operation="invalid",
            cost_usd=0.05,
        )
