"""Embedding services module."""

from llm_common.embeddings.base import EmbeddingService
from llm_common.embeddings.openai import OpenAIEmbeddingService

__all__ = ["EmbeddingService", "OpenAIEmbeddingService"]
