# llm-common

Shared LLM framework for affordabot and prime-radiant-ai.

## Features

- **Multi-Provider Support**: z.ai, OpenRouter, and any OpenAI-compatible endpoint
- **Web Search**: z.ai web search with intelligent caching
- **Retrieval**: Interfaces and models for retrieval-augmented generation (RAG)
- **Structured Outputs**: Built-in support for instructor and Pydantic models
- **Cost Tracking**: Per-request cost monitoring and budget alerts
- **Retry Logic**: Exponential backoff with jitter for reliability
- **Type Safety**: Full mypy strict mode compliance

## Installation

```bash
# Via Poetry
poetry add llm-common

# Via pip
pip install llm-common
```

## Quick Start

### Basic LLM Usage

```python
from llm_common.providers import ZaiClient, OpenRouterClient
from llm_common.core import LLMMessage

# z.ai client
zai = ZaiClient(api_key="your-zai-key")
response = await zai.chat_completion(
    messages=[LLMMessage(role="user", content="Hello!")],
    model="glm-4.5"
)

# OpenRouter client (access to 400+ models)
router = OpenRouterClient(api_key="your-openrouter-key")
response = await router.chat_completion(
    messages=[LLMMessage(role="user", content="Hello!")],
    model="anthropic/claude-3.5-sonnet"
)
```

### Web Search with Caching

```python
from llm_common.web_search import WebSearchClient

search = WebSearchClient(
    zai_api_key="your-zai-key",
    cache_backend="supabase",  # or "memory"
    cache_ttl=86400  # 24 hours
)

results = await search.search(
    query="California AB 1234 housing regulations",
    count=10,
    domains=["*.gov"],
    recency="1y"
)
```

### Retrieval (RAG)

```python
from llm_common.retrieval import RetrievalBackend, RetrievedChunk

# Implement a custom retrieval backend
class MyRetrieval(RetrievalBackend):
    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        # Your implementation here
        pass

# Use the backend
async with MyRetrieval() as backend:
    results = await backend.retrieve("What is RAG?", top_k=3)
    for chunk in results:
        print(f"{chunk.source}: {chunk.content}")
```

### Structured Outputs with instructor

```python
from pydantic import BaseModel
from llm_common.integrations import get_instructor_client

class Analysis(BaseModel):
    summary: str
    sentiment: str
    key_points: list[str]

client = get_instructor_client(
    provider="openrouter",
    api_key="your-key"
)

analysis = await client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",
    response_model=Analysis,
    messages=[{"role": "user", "content": "Analyze this bill..."}]
)
```

## Architecture

```
llm_common/
├── core/           # Abstract interfaces and data models
├── providers/      # Provider implementations (Zai, OpenRouter, Unified)
├── retrieval/      # RAG interfaces (RetrievalBackend, RetrievedChunk)
├── web_search/     # Web search with caching
├── utils/          # Retry logic, cost tracking, logging
└── integrations/   # instructor, Pydantic helpers
```

This library is designed to be driven by primary repos (Prime Radiant, Affordabot) that track work in Beads. All commits should carry Feature-Keys from controlling epics (bd-svse, affordabot-rdx, etc.).

## Cost Optimization

The framework includes aggressive caching to reduce costs:

- **Web Search**: 80% cache hit rate target (reduces $450/month → $90/month)
- **Model Selection**: Free tier → Budget → Premium model degradation
- **Cost Tracking**: Per-request monitoring with budget alerts

## Development

```bash
# Setup
poetry install

# Run tests
poetry run pytest

# Type checking
poetry run mypy llm_common

# Formatting
poetry run black llm_common
poetry run ruff llm_common
```

## Documentation

See `docs/` for detailed documentation:

- [Integration and Retrieval Guide](docs/LLM_COMMON_WORKSTREAMS/INTEGRATION_AND_RETRIEVAL.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)

## License

MIT
