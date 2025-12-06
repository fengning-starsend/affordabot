"""Tests for retrieval base interface."""

import pytest

from llm_common.retrieval.base import RetrievalBackend
from llm_common.retrieval.models import RetrievedChunk


class MockRetrievalBackend(RetrievalBackend):
    """Mock implementation for testing."""

    def __init__(self, return_chunks: list[RetrievedChunk] | None = None) -> None:
        self.return_chunks = return_chunks or []
        self.retrieve_calls: list[tuple] = []
        self.closed = False

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        filters: dict[str, any] | None = None,
    ) -> list[RetrievedChunk]:
        """Mock retrieve implementation."""
        self.retrieve_calls.append((query, top_k, min_score, filters))

        # Apply top_k limit
        chunks = self.return_chunks[:top_k]

        # Apply min_score filter if provided
        if min_score is not None:
            chunks = [c for c in chunks if c.score >= min_score]

        return chunks

    async def close(self) -> None:
        """Mock close implementation."""
        self.closed = True


class FailingRetrievalBackend(RetrievalBackend):
    """Mock backend that always fails for health check testing."""

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        filters: dict[str, any] | None = None,
    ) -> list[RetrievedChunk]:
        """Always raise an exception."""
        raise ConnectionError("Backend unavailable")


@pytest.mark.asyncio
async def test_retrieve_basic() -> None:
    """Test basic retrieve functionality."""
    chunks = [
        RetrievedChunk(content="First", score=0.9, source="doc1"),
        RetrievedChunk(content="Second", score=0.8, source="doc2"),
    ]
    backend = MockRetrievalBackend(return_chunks=chunks)

    results = await backend.retrieve("test query")

    assert len(results) == 2
    assert results[0].content == "First"
    assert results[1].content == "Second"
    assert len(backend.retrieve_calls) == 1
    assert backend.retrieve_calls[0][0] == "test query"


@pytest.mark.asyncio
async def test_retrieve_with_top_k() -> None:
    """Test retrieve with top_k parameter."""
    chunks = [
        RetrievedChunk(content=f"Chunk {i}", score=0.9 - i * 0.1, source=f"doc{i}")
        for i in range(10)
    ]
    backend = MockRetrievalBackend(return_chunks=chunks)

    results = await backend.retrieve("test", top_k=3)

    assert len(results) == 3
    assert results[0].content == "Chunk 0"
    assert results[2].content == "Chunk 2"


@pytest.mark.asyncio
async def test_retrieve_with_min_score() -> None:
    """Test retrieve with min_score filter."""
    chunks = [
        RetrievedChunk(content="High", score=0.95, source="doc1"),
        RetrievedChunk(content="Medium", score=0.75, source="doc2"),
        RetrievedChunk(content="Low", score=0.55, source="doc3"),
    ]
    backend = MockRetrievalBackend(return_chunks=chunks)

    results = await backend.retrieve("test", min_score=0.7)

    assert len(results) == 2
    assert all(c.score >= 0.7 for c in results)


@pytest.mark.asyncio
async def test_retrieve_with_filters() -> None:
    """Test retrieve with metadata filters."""
    backend = MockRetrievalBackend()

    await backend.retrieve("test", filters={"source": "docs/"})

    assert backend.retrieve_calls[0][3] == {"source": "docs/"}


@pytest.mark.asyncio
async def test_health_check_success() -> None:
    """Test health check with working backend."""
    chunks = [RetrievedChunk(content="test", score=0.9, source="doc")]
    backend = MockRetrievalBackend(return_chunks=chunks)

    is_healthy = await backend.health_check()

    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_failure() -> None:
    """Test health check with failing backend."""
    backend = FailingRetrievalBackend()

    is_healthy = await backend.health_check()

    assert is_healthy is False


@pytest.mark.asyncio
async def test_get_by_id_default() -> None:
    """Test default get_by_id implementation."""
    backend = MockRetrievalBackend()

    result = await backend.get_by_id("test_id")

    assert result is None


@pytest.mark.asyncio
async def test_close() -> None:
    """Test close method."""
    backend = MockRetrievalBackend()

    await backend.close()

    assert backend.closed is True


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test async context manager usage."""
    backend = MockRetrievalBackend(
        return_chunks=[RetrievedChunk(content="test", score=0.9, source="doc")]
    )

    async with backend as b:
        results = await b.retrieve("test")
        assert len(results) == 1

    assert backend.closed is True


@pytest.mark.asyncio
async def test_abstract_methods_not_implemented() -> None:
    """Test that abstract methods must be implemented."""
    class IncompleteBackend(RetrievalBackend):
        pass

    # Should not be able to instantiate without implementing retrieve
    with pytest.raises(TypeError):
        IncompleteBackend()


@pytest.mark.asyncio
async def test_retrieve_empty_results() -> None:
    """Test retrieve with no results."""
    backend = MockRetrievalBackend(return_chunks=[])

    results = await backend.retrieve("test")

    assert len(results) == 0
    assert results == []
