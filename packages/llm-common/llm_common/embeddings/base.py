"""Base interface for embedding services."""

from abc import ABC, abstractmethod
from typing import List

class EmbeddingService(ABC):
    """Abstract base class for embedding services.
    
    Provides an interface for generating vector embeddings from text,
    supporting both single query and batch document operations.
    """

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query string.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents.

        Args:
            texts: List of text strings to embed.

        Returns:
            A list of embedding vectors (list of floats).
        """
        pass
