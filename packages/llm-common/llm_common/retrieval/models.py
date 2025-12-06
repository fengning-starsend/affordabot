"""Data models for retrieval operations."""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RetrievedChunk(BaseModel):
    """Represents a chunk of content retrieved from a knowledge base.

    This model encapsulates all information about a retrieved document chunk,
    including its content, metadata, and relevance scoring.

    Attributes:
        content: The actual text content of the retrieved chunk
        score: Relevance score (higher is more relevant), typically from similarity search
        source: Identifier for the source document (e.g., file path, URL, document ID)
        metadata: Additional metadata about the chunk (e.g., page number, section, author)
        chunk_id: Optional unique identifier for this specific chunk
        embedding: Optional embedding vector used for retrieval
    """

    content: str = Field(..., description="The text content of the chunk")
    score: float = Field(..., description="Relevance score (0.0 to 1.0)", ge=0.0, le=1.0)
    source: str = Field(..., description="Source identifier for the document")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the chunk"
    )
    chunk_id: Optional[str] = Field(None, description="Unique identifier for this chunk")
    embedding: Optional[list[float]] = Field(
        None,
        description="Embedding vector for this chunk"
    )

    def __str__(self) -> str:
        """Human-readable string representation."""
        preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"RetrievedChunk(source={self.source}, score={self.score:.3f}, content='{preview}')"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"RetrievedChunk(content={self.content!r}, score={self.score}, "
            f"source={self.source!r}, metadata={self.metadata!r}, "
            f"chunk_id={self.chunk_id!r})"
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "The quick brown fox jumps over the lazy dog.",
                "score": 0.95,
                "source": "documents/example.txt",
                "metadata": {"page": 1, "section": "introduction"},
                "chunk_id": "chunk_001",
            }
        }
    )
