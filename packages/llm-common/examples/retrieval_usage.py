"""Example usage of llm-common retrieval module."""

import asyncio
from typing import Any

from llm_common.retrieval import RetrievalBackend, RetrievedChunk


class DummyRetrievalBackend(RetrievalBackend):
    """Dummy retrieval backend for demonstration purposes.

    In practice, this would connect to a vector database like:
    - ChromaDB (local, simple)
    - Pinecone (managed, scalable)
    - Weaviate (hybrid search)
    - Elasticsearch (full-text + vector)
    """

    def __init__(self) -> None:
        """Initialize with dummy data."""
        self.documents = [
            {
                "content": "Retrieval-Augmented Generation (RAG) is a technique that combines "
                "retrieval of relevant documents with language model generation.",
                "source": "docs/rag_intro.md",
                "metadata": {"section": "introduction", "page": 1},
            },
            {
                "content": "Vector databases store embeddings and enable similarity search. "
                "Popular options include ChromaDB, Pinecone, and Weaviate.",
                "source": "docs/vector_databases.md",
                "metadata": {"section": "databases", "page": 3},
            },
            {
                "content": "Embeddings are dense vector representations of text that capture "
                "semantic meaning. Models like OpenAI's text-embedding-3-small can "
                "generate these embeddings.",
                "source": "docs/embeddings.md",
                "metadata": {"section": "concepts", "page": 5},
            },
            {
                "content": "To implement RAG: 1) Chunk documents, 2) Generate embeddings, "
                "3) Store in vector DB, 4) Retrieve relevant chunks for queries, "
                "5) Augment prompts with retrieved context.",
                "source": "docs/rag_implementation.md",
                "metadata": {"section": "implementation", "page": 7},
            },
        ]

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant chunks (dummy implementation).

        In a real implementation, this would:
        1. Generate embedding for the query
        2. Perform similarity search in vector database
        3. Apply filters and scoring thresholds
        4. Return ranked results
        """
        # Dummy scoring based on keyword overlap
        results = []
        query_lower = query.lower()

        for doc in self.documents:
            # Apply metadata filters if provided
            if filters:
                if not all(doc["metadata"].get(k) == v for k, v in filters.items()):
                    continue

            # Simple keyword-based scoring (in practice, use embeddings)
            keywords = query_lower.split()
            content_lower = doc["content"].lower()
            matches = sum(1 for word in keywords if word in content_lower)
            score = min(matches / len(keywords), 1.0) if keywords else 0.0

            # Apply min_score threshold
            if min_score is not None and score < min_score:
                continue

            results.append(
                RetrievedChunk(
                    content=doc["content"],
                    score=score,
                    source=doc["source"],
                    metadata=doc["metadata"],
                    chunk_id=f"chunk_{len(results)}",
                )
            )

        # Sort by score (descending) and apply top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]


async def basic_retrieval_example() -> None:
    """Demonstrate basic retrieval usage."""
    print("=== Basic Retrieval Example ===\n")

    backend = DummyRetrievalBackend()

    # Query 1: Simple retrieval
    print("Query: 'What is RAG?'")
    results = await backend.retrieve("What is RAG?", top_k=2)

    for i, chunk in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Score: {chunk.score:.2f}")
        print(f"  Source: {chunk.source}")
        print(f"  Content: {chunk.content[:100]}...")

    # Query 2: With filtering
    print("\n\nQuery: 'embeddings' (filter: section='concepts')")
    results = await backend.retrieve(
        "embeddings",
        top_k=5,
        filters={"section": "concepts"}
    )

    for i, chunk in enumerate(results, 1):
        print(f"\nFiltered Result {i}:")
        print(f"  Score: {chunk.score:.2f}")
        print(f"  Source: {chunk.source}")
        print(f"  Metadata: {chunk.metadata}")


async def context_manager_example() -> None:
    """Demonstrate context manager usage for resource cleanup."""
    print("\n\n=== Context Manager Example ===\n")

    async with DummyRetrievalBackend() as backend:
        # Check backend health
        is_healthy = await backend.health_check()
        print(f"Backend healthy: {is_healthy}")

        # Retrieve with min_score threshold
        results = await backend.retrieve(
            "vector databases",
            top_k=3,
            min_score=0.3
        )

        print(f"\nFound {len(results)} results above score threshold 0.3:")
        for chunk in results:
            print(f"  - {chunk.source} (score: {chunk.score:.2f})")

    print("\nBackend automatically closed via context manager")


async def rag_context_formatting_example() -> None:
    """Demonstrate formatting retrieved chunks for LLM context."""
    print("\n\n=== RAG Context Formatting Example ===\n")

    backend = DummyRetrievalBackend()

    # Retrieve relevant chunks
    query = "How do I implement RAG?"
    chunks = await backend.retrieve(query, top_k=3)

    # Format for LLM prompt
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[{i}] {chunk.source}\n{chunk.content}"
        )

    context = "\n\n".join(context_parts)

    # Build RAG prompt
    prompt = f"""Answer the following question using the provided context.

Context:
{context}

Question: {query}

Answer:"""

    print("Generated RAG Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print("\nThis prompt would be sent to an LLM (ZaiClient, OpenRouterClient, etc.)")


async def pgvector_backend_example() -> None:
    """Demonstrate Supabase pgvector backend usage (with mocked Supabase client).

    In production, you would:
    1. Create actual Supabase client: supabase = create_client(url, key)
    2. Implement real embedding function (OpenAI, local model, etc.)
    3. Create database table with pgvector extension
    4. Create RPC function for similarity search
    """
    print("\n\n=== Supabase pgvector Backend Example ===\n")

    # Mock Supabase client for demonstration
    # In production, use: from supabase import create_client
    class MockSupabaseClient:
        """Mock Supabase client for demo purposes."""
        def rpc(self, function_name: str, params: dict) -> Any:
            class Response:
                def __init__(self):
                    self.data = [
                        {
                            "id": "doc_001",
                            "content": "pgvector is a Postgres extension for vector similarity search.",
                            "source": "docs/pgvector.md",
                            "section": "overview",
                            "page": 1,
                            "similarity": 0.92,
                        },
                        {
                            "id": "doc_002",
                            "content": "Supabase provides managed Postgres with pgvector support.",
                            "source": "docs/supabase.md",
                            "section": "features",
                            "page": 3,
                            "similarity": 0.88,
                        },
                    ]
                    # Apply match_count limit
                    if "match_count" in params:
                        self.data = self.data[:params["match_count"]]

                def execute(self):
                    return self

            return Response()

        def table(self, name: str) -> Any:
            class Table:
                def select(self, cols: str) -> Any:
                    class Query:
                        def limit(self, n: int) -> Any:
                            class Execute:
                                def execute(self) -> Any:
                                    class Resp:
                                        data = [{"count": 100}]
                                    return Resp()
                            return Execute()
                    return Query()
            return Table()

    # Mock embedding function
    # In production, use OpenAI, Sentence Transformers, or similar
    async def embed_query(text: str) -> list[float]:
        """Generate embedding vector from text (mock implementation)."""
        # In production: return openai.embeddings.create(input=text, model="text-embedding-3-small")
        # For demo: return dummy vector
        return [0.1, 0.2, 0.3] * 128  # 384-dimensional vector

    # Import the backend
    try:
        from llm_common.retrieval.backends import SupabasePgVectorBackend

        # Create backend with mock client
        backend = SupabasePgVectorBackend(
            supabase_client=MockSupabaseClient(),
            table="document_chunks",
            vector_col="embedding",
            text_col="content",
            metadata_cols=["section", "page"],
            embed_fn=embed_query,
        )

        # Perform similarity search
        print("Query: 'What is pgvector?'")
        results = await backend.retrieve("What is pgvector?", top_k=2)

        print(f"\nFound {len(results)} results:\n")
        for i, chunk in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Score: {chunk.score:.2f}")
            print(f"  Source: {chunk.source}")
            print(f"  Content: {chunk.content[:80]}...")
            print(f"  Metadata: {chunk.metadata}\n")

        # Health check
        is_healthy = await backend.health_check()
        print(f"Backend health check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")

        print("\n" + "=" * 60)
        print("Production Setup Notes:")
        print("=" * 60)
        print("""
1. Install Supabase client:
   pip install supabase

2. Enable pgvector extension in Supabase:
   CREATE EXTENSION IF NOT EXISTS vector;

3. Create table with vector column:
   CREATE TABLE document_chunks (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     content TEXT NOT NULL,
     embedding VECTOR(384),  -- or 1536 for OpenAI
     source TEXT,
     section TEXT,
     page INTEGER
   );

4. Create similarity search RPC function:
   CREATE OR REPLACE FUNCTION match_document_chunks(
     query_embedding VECTOR(384),
     match_count INT DEFAULT 5,
     match_threshold FLOAT DEFAULT 0.0
   )
   RETURNS TABLE (
     id UUID,
     content TEXT,
     source TEXT,
     section TEXT,
     page INTEGER,
     similarity FLOAT
   )
   LANGUAGE plpgsql
   AS $$
   BEGIN
     RETURN QUERY
     SELECT
       document_chunks.id,
       document_chunks.content,
       document_chunks.source,
       document_chunks.section,
       document_chunks.page,
       1 - (document_chunks.embedding <=> query_embedding) AS similarity
     FROM document_chunks
     WHERE 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
     ORDER BY document_chunks.embedding <=> query_embedding
     LIMIT match_count;
   END;
   $$;

5. Use in production:
   from supabase import create_client
   from openai import OpenAI

   supabase = create_client(url, key)
   openai_client = OpenAI()

   async def embed(text: str) -> list[float]:
       response = openai_client.embeddings.create(
           input=text,
           model="text-embedding-3-small"
       )
       return response.data[0].embedding

   backend = SupabasePgVectorBackend(
       supabase_client=supabase,
       table="document_chunks",
       embed_fn=embed
   )
""")

    except ImportError:
        print("SupabasePgVectorBackend not available (backend implementation needed)")


async def main() -> None:
    """Run all examples."""
    await basic_retrieval_example()
    await context_manager_example()
    await rag_context_formatting_example()
    await pgvector_backend_example()


if __name__ == "__main__":
    asyncio.run(main())
