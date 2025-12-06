"""Tests for retrieval models."""

import pytest
from pydantic import ValidationError

from llm_common.retrieval.models import RetrievedChunk


def test_retrieved_chunk_basic_creation() -> None:
    """Test basic creation of RetrievedChunk."""
    chunk = RetrievedChunk(
        content="This is a test chunk",
        score=0.95,
        source="test_document.txt"
    )

    assert chunk.content == "This is a test chunk"
    assert chunk.score == 0.95
    assert chunk.source == "test_document.txt"
    assert chunk.metadata == {}
    assert chunk.chunk_id is None
    assert chunk.embedding is None


def test_retrieved_chunk_with_metadata() -> None:
    """Test RetrievedChunk with metadata."""
    metadata = {"page": 5, "section": "introduction", "author": "John Doe"}
    chunk = RetrievedChunk(
        content="Content with metadata",
        score=0.88,
        source="document.pdf",
        metadata=metadata,
        chunk_id="chunk_123"
    )

    assert chunk.metadata == metadata
    assert chunk.chunk_id == "chunk_123"


def test_retrieved_chunk_with_embedding() -> None:
    """Test RetrievedChunk with embedding vector."""
    embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    chunk = RetrievedChunk(
        content="Content with embedding",
        score=0.92,
        source="embedded_doc.txt",
        embedding=embedding
    )

    assert chunk.embedding == embedding


def test_retrieved_chunk_score_validation() -> None:
    """Test that score is validated to be between 0 and 1."""
    # Valid scores
    RetrievedChunk(content="test", score=0.0, source="test")
    RetrievedChunk(content="test", score=0.5, source="test")
    RetrievedChunk(content="test", score=1.0, source="test")

    # Invalid scores
    with pytest.raises(ValidationError):
        RetrievedChunk(content="test", score=-0.1, source="test")

    with pytest.raises(ValidationError):
        RetrievedChunk(content="test", score=1.1, source="test")


def test_retrieved_chunk_required_fields() -> None:
    """Test that required fields are enforced."""
    with pytest.raises(ValidationError):
        RetrievedChunk(score=0.5, source="test")  # Missing content

    with pytest.raises(ValidationError):
        RetrievedChunk(content="test", source="test")  # Missing score

    with pytest.raises(ValidationError):
        RetrievedChunk(content="test", score=0.5)  # Missing source


def test_retrieved_chunk_str_representation() -> None:
    """Test string representation of RetrievedChunk."""
    chunk = RetrievedChunk(
        content="Short content",
        score=0.85,
        source="test.txt"
    )

    str_repr = str(chunk)
    assert "test.txt" in str_repr
    assert "0.850" in str_repr
    assert "Short content" in str_repr


def test_retrieved_chunk_str_representation_long_content() -> None:
    """Test string representation with long content is truncated."""
    long_content = "A" * 200
    chunk = RetrievedChunk(
        content=long_content,
        score=0.75,
        source="long.txt"
    )

    str_repr = str(chunk)
    assert "..." in str_repr
    assert len(str_repr) < len(long_content)


def test_retrieved_chunk_repr() -> None:
    """Test detailed repr of RetrievedChunk."""
    chunk = RetrievedChunk(
        content="Test content",
        score=0.9,
        source="test.txt",
        chunk_id="abc123"
    )

    repr_str = repr(chunk)
    assert "RetrievedChunk" in repr_str
    assert "Test content" in repr_str
    assert "0.9" in repr_str
    assert "test.txt" in repr_str
    assert "abc123" in repr_str


def test_retrieved_chunk_json_serialization() -> None:
    """Test JSON serialization and deserialization."""
    original = RetrievedChunk(
        content="JSON test",
        score=0.88,
        source="json.txt",
        metadata={"key": "value"},
        chunk_id="json_123"
    )

    # Serialize to JSON
    json_str = original.model_dump_json()

    # Deserialize back
    restored = RetrievedChunk.model_validate_json(json_str)

    assert restored.content == original.content
    assert restored.score == original.score
    assert restored.source == original.source
    assert restored.metadata == original.metadata
    assert restored.chunk_id == original.chunk_id


def test_retrieved_chunk_dict_conversion() -> None:
    """Test conversion to and from dictionary."""
    original = RetrievedChunk(
        content="Dict test",
        score=0.77,
        source="dict.txt",
        metadata={"nested": {"key": "value"}}
    )

    # Convert to dict
    chunk_dict = original.model_dump()

    assert chunk_dict["content"] == "Dict test"
    assert chunk_dict["score"] == 0.77
    assert chunk_dict["metadata"]["nested"]["key"] == "value"

    # Convert back from dict
    restored = RetrievedChunk(**chunk_dict)
    assert restored.content == original.content
    assert restored.score == original.score
