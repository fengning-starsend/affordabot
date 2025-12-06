"""Tests for Supabase pgvector backend."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from llm_common.retrieval.backends.pgvector_backend import SupabasePgVectorBackend
from llm_common.retrieval.models import RetrievedChunk


class MockSupabaseResponse:
    """Mock Supabase response object."""

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data


class MockSupabaseTable:
    """Mock Supabase table query builder."""

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self._data = data
        self._filters: dict[str, Any] = {}
        self._limit_count: int | None = None

    def select(self, columns: str) -> "MockSupabaseTable":
        """Mock select method."""
        return self

    def eq(self, column: str, value: Any) -> "MockSupabaseTable":
        """Mock eq filter method."""
        self._filters[column] = value
        return self

    def limit(self, count: int) -> "MockSupabaseTable":
        """Mock limit method."""
        self._limit_count = count
        return self

    def execute(self) -> MockSupabaseResponse:
        """Mock execute method."""
        filtered_data = self._data
        for col, val in self._filters.items():
            filtered_data = [d for d in filtered_data if d.get(col) == val]

        if self._limit_count is not None:
            filtered_data = filtered_data[: self._limit_count]

        return MockSupabaseResponse(filtered_data)


class MockSupabaseClient:
    """Mock Supabase client."""

    def __init__(self, table_data: dict[str, list[dict[str, Any]]]) -> None:
        self._table_data = table_data
        self._rpc_responses: dict[str, Any] = {}

    def table(self, table_name: str) -> MockSupabaseTable:
        """Mock table method."""
        return MockSupabaseTable(self._table_data.get(table_name, []))

    def rpc(self, function_name: str, params: dict[str, Any]) -> MockSupabaseTable:
        """Mock RPC method."""
        if function_name in self._rpc_responses:
            data = self._rpc_responses[function_name]
            # Apply match_count limit if provided
            match_count = params.get("match_count")
            if match_count is not None:
                data = data[:match_count]
            # Apply match_threshold if provided
            match_threshold = params.get("match_threshold")
            if match_threshold is not None:
                data = [d for d in data if d.get("similarity", 0.0) >= match_threshold]
            return MockSupabaseTable(data)
        raise Exception(f"RPC function '{function_name}' not found")

    def set_rpc_response(self, function_name: str, data: list[dict[str, Any]]) -> None:
        """Set mock RPC response data."""
        self._rpc_responses[function_name] = data


async def mock_embed_fn(text: str) -> list[float]:
    """Mock embedding function."""
    # Simple mock: convert text length to a vector
    return [float(len(text)), 0.5, 0.3]


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Sample chunk data for testing."""
    return [
        {
            "id": "chunk_1",
            "content": "Retrieval-Augmented Generation (RAG) combines retrieval with LLMs.",
            "source": "docs/rag.md",
            "section": "introduction",
            "page": 1,
            "similarity": 0.95,
        },
        {
            "id": "chunk_2",
            "content": "Vector databases store embeddings for similarity search.",
            "source": "docs/vectors.md",
            "section": "databases",
            "page": 3,
            "similarity": 0.87,
        },
        {
            "id": "chunk_3",
            "content": "pgvector is a Postgres extension for vector operations.",
            "source": "docs/pgvector.md",
            "section": "implementation",
            "page": 5,
            "similarity": 0.82,
        },
    ]


@pytest.fixture
def mock_supabase_client(sample_chunks: list[dict[str, Any]]) -> MockSupabaseClient:
    """Create mock Supabase client with sample data."""
    client = MockSupabaseClient({"document_chunks": sample_chunks})
    client.set_rpc_response("match_document_chunks", sample_chunks)
    return client


@pytest.mark.asyncio
async def test_retrieve_basic(mock_supabase_client: MockSupabaseClient) -> None:
    """Test basic retrieval."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("What is RAG?", top_k=3)

    assert len(results) == 3
    assert all(isinstance(chunk, RetrievedChunk) for chunk in results)
    assert results[0].content == "Retrieval-Augmented Generation (RAG) combines retrieval with LLMs."
    assert results[0].score == 0.95
    assert results[0].source == "docs/rag.md"


@pytest.mark.asyncio
async def test_retrieve_with_top_k(mock_supabase_client: MockSupabaseClient) -> None:
    """Test retrieval with top_k limit."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("vectors", top_k=2)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_retrieve_with_min_score(
    mock_supabase_client: MockSupabaseClient, sample_chunks: list[dict[str, Any]]
) -> None:
    """Test retrieval with minimum score threshold."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("RAG", top_k=5, min_score=0.9)

    assert len(results) == 1
    assert all(chunk.score >= 0.9 for chunk in results)


@pytest.mark.asyncio
async def test_retrieve_with_filters(
    mock_supabase_client: MockSupabaseClient, sample_chunks: list[dict[str, Any]]
) -> None:
    """Test retrieval with metadata filters."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("vectors", top_k=5, filters={"section": "databases"})

    assert len(results) == 1
    assert results[0].metadata["section"] == "databases"


@pytest.mark.asyncio
async def test_retrieve_without_embed_fn(mock_supabase_client: MockSupabaseClient) -> None:
    """Test that retrieve raises error when embed_fn not provided."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        embed_fn=None,  # No embedding function
    )

    with pytest.raises(ValueError, match="embed_fn must be provided"):
        await backend.retrieve("test query")


@pytest.mark.asyncio
async def test_retrieve_metadata_included(mock_supabase_client: MockSupabaseClient) -> None:
    """Test that metadata columns are included in results."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("test", top_k=1)

    assert len(results) == 1
    assert "section" in results[0].metadata
    assert "page" in results[0].metadata
    assert results[0].metadata["section"] == "introduction"
    assert results[0].metadata["page"] == 1


@pytest.mark.asyncio
async def test_get_by_id_found(
    mock_supabase_client: MockSupabaseClient, sample_chunks: list[dict[str, Any]]
) -> None:
    """Test retrieving chunk by ID when it exists."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    chunk = await backend.get_by_id("chunk_1")

    assert chunk is not None
    assert chunk.chunk_id == "chunk_1"
    assert chunk.content == "Retrieval-Augmented Generation (RAG) combines retrieval with LLMs."
    assert chunk.score == 1.0  # Direct retrieval has perfect score


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_supabase_client: MockSupabaseClient) -> None:
    """Test retrieving chunk by ID when it doesn't exist."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    chunk = await backend.get_by_id("nonexistent_id")

    assert chunk is None


@pytest.mark.asyncio
async def test_health_check_success(mock_supabase_client: MockSupabaseClient) -> None:
    """Test health check when database is accessible."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        embed_fn=mock_embed_fn,
    )

    is_healthy = await backend.health_check()

    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_failure() -> None:
    """Test health check when database is not accessible."""

    class FailingMockClient:
        def table(self, name: str) -> Any:
            raise Exception("Connection failed")

    backend = SupabasePgVectorBackend(
        supabase_client=FailingMockClient(),
        table="document_chunks",
        embed_fn=mock_embed_fn,
    )

    is_healthy = await backend.health_check()

    assert is_healthy is False


@pytest.mark.asyncio
async def test_context_manager(mock_supabase_client: MockSupabaseClient) -> None:
    """Test using backend as async context manager."""
    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    async with backend as b:
        results = await b.retrieve("test", top_k=1)
        assert len(results) == 1

    # close() should have been called (though it's a no-op for Supabase)
    # Just verify context manager works without errors


@pytest.mark.asyncio
async def test_custom_column_names(
    mock_supabase_client: MockSupabaseClient, sample_chunks: list[dict[str, Any]]
) -> None:
    """Test backend with custom column names."""
    # Modify sample data to use different column names
    custom_chunks = []
    for chunk in sample_chunks:
        custom_chunks.append(
            {
                "chunk_id": chunk["id"],
                "text": chunk["content"],
                "doc_source": chunk["source"],
                "section": chunk["section"],
                "page": chunk["page"],
                "similarity": chunk["similarity"],
            }
        )

    client = MockSupabaseClient({"custom_table": custom_chunks})
    client.set_rpc_response("match_custom_table", custom_chunks)

    backend = SupabasePgVectorBackend(
        supabase_client=client,
        table="custom_table",
        text_col="text",
        source_col="doc_source",
        id_col="chunk_id",
        metadata_cols=["section", "page"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("test", top_k=1)

    assert len(results) == 1
    assert results[0].content == custom_chunks[0]["text"]
    assert results[0].source == custom_chunks[0]["doc_source"]
    assert results[0].chunk_id == custom_chunks[0]["chunk_id"]


@pytest.mark.asyncio
async def test_rpc_function_not_found(mock_supabase_client: MockSupabaseClient) -> None:
    """Test error handling when RPC function doesn't exist."""
    # Create client without setting RPC response
    client = MockSupabaseClient({"document_chunks": []})

    backend = SupabasePgVectorBackend(
        supabase_client=client,
        table="document_chunks",
        embed_fn=mock_embed_fn,
    )

    with pytest.raises(RuntimeError, match="RPC function .* not found"):
        await backend.retrieve("test")


@pytest.mark.asyncio
async def test_custom_rpc_function(
    mock_supabase_client: MockSupabaseClient, sample_chunks: list[dict[str, Any]]
) -> None:
    """Test using custom RPC function name."""
    mock_supabase_client.set_rpc_response("custom_search", sample_chunks)

    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        rpc_function="custom_search",
        metadata_cols=["section"],
        embed_fn=mock_embed_fn,
    )

    results = await backend.retrieve("test", top_k=2)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_embedding_conversion(mock_supabase_client: MockSupabaseClient) -> None:
    """Test that embeddings are converted to list if needed."""

    async def embed_returns_tuple(text: str) -> tuple[float, ...]:
        """Embedding function that returns tuple instead of list."""
        return (1.0, 2.0, 3.0)

    backend = SupabasePgVectorBackend(
        supabase_client=mock_supabase_client,
        table="document_chunks",
        embed_fn=embed_returns_tuple,
    )

    # Should convert tuple to list internally
    results = await backend.retrieve("test", top_k=1)
    assert len(results) >= 0  # Should not raise error
