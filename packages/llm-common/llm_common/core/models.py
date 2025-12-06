"""Core data models for LLM framework."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """Message role in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class LLMMessage(BaseModel):
    """Single message in conversation."""

    model_config = ConfigDict(use_enum_values=True)

    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[dict[str, Any]] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class LLMUsage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    """Response from LLM completion."""

    id: str
    model: str
    content: str
    role: MessageRole = MessageRole.ASSISTANT
    finish_reason: str
    usage: LLMUsage
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Provider-specific metadata
    provider: Optional[str] = None
    cost_usd: Optional[float] = None
    latency_ms: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMConfig(BaseModel):
    """Configuration for LLM client."""

    api_key: str
    base_url: Optional[str] = None
    default_model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0

    # Cost tracking
    track_costs: bool = True
    budget_limit_usd: Optional[float] = None
    alert_threshold: float = 0.8  # Alert at 80% of budget

    # Provider-specific
    provider: Literal["zai", "openrouter", "openai", "anthropic"] = "openrouter"
    metadata: dict[str, Any] = Field(default_factory=dict)


class WebSearchResult(BaseModel):
    """Single web search result."""

    url: str
    title: str
    snippet: str
    content: Optional[str] = None
    published_date: Optional[datetime] = None
    domain: str
    relevance_score: Optional[float] = None


class WebSearchResponse(BaseModel):
    """Response from web search."""

    query: str
    results: list[WebSearchResult]
    total_results: int
    search_time_ms: int
    cached: bool = False
    cost_usd: Optional[float] = None
    provider: str = "zai"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CostMetrics(BaseModel):
    """Cost tracking metrics."""

    provider: str
    model: str
    operation: Literal["chat", "search", "embedding"]
    cost_usd: float
    tokens_used: Optional[int] = None
    requests_count: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
