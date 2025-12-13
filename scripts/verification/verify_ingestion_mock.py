import asyncio
from unittest.mock import MagicMock, AsyncMock
from typing import List

from services.ingestion_service import IngestionService
from llm_common.embeddings import EmbeddingService
from llm_common.retrieval import SupabasePgVectorBackend, RetrievedChunk

class MockEmbeddingService(EmbeddingService):
    async def embed_query(self, text: str) -> List[float]:
        return [0.1] * 1536
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Return fake 1536-dim vectors
        return [[0.1] * 1536 for _ in range(len(texts))]

async def main():
    print("🧪 Starting Mock Ingestion Verification...")
    
    # Mocks
    mock_supabase = MagicMock()
    # Mock extract text return
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "test-scrape-id",
        "source_id": "test-source",
        "url": "http://example.com",
        "data": {"text": "This is a long text that should be chunked into pieces. " * 50},
        "content_type": "text/html",
        "metadata": {"test": "true"}
    }
    # Mock update
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = None

    mock_vector_backend = AsyncMock(spec=SupabasePgVectorBackend)
    mock_vector_backend.upsert.return_value = 2 # Assume 2 chunks
    
    msg_service = MockEmbeddingService()
    
    service = IngestionService(
        supabase_client=mock_supabase,
        vector_backend=mock_vector_backend,
        embedding_service=msg_service,
        chunk_size=100,
        chunk_overlap=20
    )
    
    print("▶️ Processing mock scrape...")
    count = await service.process_raw_scrape("test-scrape-id")
    
    print(f"✅ Processed {count} chunks.")
    
    # Assertions
    assert count > 0, "Should have created chunks"
    
    # Verify Upsert called
    mock_vector_backend.upsert.assert_called_once()
    call_args = mock_vector_backend.upsert.call_args[0][0]
    print(f"✅ Upsert called with {len(call_args)} chunks")
    
    first_chunk = call_args[0]
    assert isinstance(first_chunk, RetrievedChunk)
    assert len(first_chunk.embedding) == 1536
    assert first_chunk.metadata["source_id"] == "test-source"
    print("✅ Chunk structure valid")
    
    print("🎉 Verification Successful: IngestionService logic works!")

if __name__ == "__main__":
    asyncio.run(main())
