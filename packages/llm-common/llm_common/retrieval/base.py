"""Base interface for retrieval backends."""

from abc import ABC, abstractmethod
from typing import Optional

from llm_common.retrieval.models import RetrievedChunk


class RetrievalBackend(ABC):
    """Abstract base class for retrieval backends.

    This interface defines the contract that all retrieval implementations must follow,
    whether they use vector databases, traditional search, or hybrid approaches.

    Implementations should handle:
    - Query processing and embedding
    - Similarity search or ranking
    - Result filtering and formatting
    - Connection management and error handling

    Example:
        >>> class MyRetrieval(RetrievalBackend):
        ...     async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        ...         # Implementation here
        ...         return chunks
        ...
        >>> backend = MyRetrieval()
        >>> results = await backend.retrieve("What is RAG?", top_k=3)
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: Optional[float] = None,
        filters: Optional[dict[str, any]] = None,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant chunks for a query.

        Args:
            query: The search query or question
            top_k: Maximum number of chunks to retrieve (default: 5)
            min_score: Minimum relevance score threshold (0.0 to 1.0)
            filters: Optional metadata filters to apply (e.g., {"source": "docs/"})

        Returns:
            List of RetrievedChunk objects, sorted by relevance (highest first)

        Raises:
            ValueError: If query is empty or parameters are invalid
            ConnectionError: If the backend is unavailable
            NotImplementedError: If the method is not implemented by subclass
        """
        pass

    async def health_check(self) -> bool:
        """Check if the retrieval backend is healthy and accessible.

        Returns:
            True if the backend is operational, False otherwise
        """
        try:
            # Default implementation: try a minimal query
            await self.retrieve("test", top_k=1)
            return True
        except Exception:
            return False

    async def get_by_id(self, chunk_id: str) -> Optional[RetrievedChunk]:
        """Retrieve a specific chunk by its ID.

        Args:
            chunk_id: The unique identifier of the chunk

        Returns:
            The RetrievedChunk if found, None otherwise

        Note:
            This is an optional method. Backends that don't support
            ID-based retrieval can leave this as the default implementation.
        """
        return None

    async def close(self) -> None:
        """Clean up resources and close connections.

        This method should be called when the backend is no longer needed.
        Implementations should override this to clean up database connections,
        file handles, or other resources.
        """
        pass

    async def __aenter__(self) -> "RetrievalBackend":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: any) -> None:
        """Async context manager exit."""
        await self.close()
