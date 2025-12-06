"""OpenAI implementation of EmbeddingService."""

import os
from typing import List, Optional, Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from llm_common.embeddings.base import EmbeddingService


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI-based embedding service.
    
    Uses standard OpenAI embeddings API (e.g. text-embedding-3-small).
    Authentication is handled via explicit api_key or OPENAI_API_KEY env var.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        base_url: Optional[str] = None,
        dimensions: Optional[int] = None,
        organization: Optional[str] = None,
    ):
        """Initialize the OpenAI embedding service.

        Args:
            api_key: OpenAI API key. If None, checks OPENAI_API_KEY env var.
            model: Embedding model to use. Default: text-embedding-3-small.
            base_url: Optional override for API base URL.
            dimensions: Optional vector dimensions (supported by v3 models).
            organization: Optional OpenAI organization ID.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable."
            )
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url,
            organization=organization
        )
        self.model = model
        self.dimensions = dimensions

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query string.
        
        Removes newlines which can affect performance of some models, 
        though less critical for v3.
        """
        text = text.replace("\n", " ")
        
        kwargs = {"model": self.model, "input": text}
        if self.dimensions:
            kwargs["dimensions"] = self.dimensions
            
        response = await self.client.embeddings.create(**kwargs)
        return response.data[0].embedding

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents.
        
        Handles batching implicitly via the API call, though large lists
        should be chunked by the caller if they exceed token limits.
        """
        # Simple newline cleanup
        cleaned_texts = [t.replace("\n", " ") for t in texts]
        
        kwargs = {"model": self.model, "input": cleaned_texts}
        if self.dimensions:
            kwargs["dimensions"] = self.dimensions

        response = await self.client.embeddings.create(**kwargs)
        
        # Ensure order is preserved (data is list of objects with index)
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
