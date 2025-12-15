"""Verification script for IngestionService (Zero Dependency)."""

import asyncio
import os
import sys
import re
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from typing import List, Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# --- MOCKS ---
# Mock modules that might not be installed
sys.modules['supabase'] = MagicMock()
sys.modules['litellm'] = MagicMock()
sys.modules['prefect'] = MagicMock()
sys.modules['llm_common'] = MagicMock()
sys.modules['llm_common.retrieval'] = MagicMock()

# Mock specific classes/functions
class MockClient:
    def __init__(self, *args, **kwargs):
        self.table = MagicMock()

class MockLLMClient:
    def __init__(self, provider="openai"):
        pass

class MockSupabasePgVectorBackend:
    def __init__(self, supabase_client, table_name):
        self.upsert = AsyncMock()

class MockRetrievedChunk:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

async def mock_aembedding(*args, **kwargs):
    input_text = kwargs.get('input', [])
    if isinstance(input_text, str):
        input_text = [input_text]
    # Return dummy embeddings
    return MagicMock(data=[
        {'embedding': [0.1] * 1536} for _ in input_text
    ])

# Apply mocks to sys.modules
sys.modules['supabase'].Client = MockClient
sys.modules['supabase'].create_client = MagicMock(return_value=MockClient())
sys.modules['llm_common'].LLMClient = MockLLMClient
sys.modules['llm_common.retrieval'].SupabasePgVectorBackend = MockSupabasePgVectorBackend
sys.modules['llm_common.retrieval'].RetrievedChunk = MockRetrievedChunk
sys.modules['litellm'].aembedding = mock_aembedding

# --- IMPORT SERVICE ---
# Now we can import the service, and it will use our mocks
from services.ingestion_service import IngestionService

async def verify_ingestion():
    print("🧪 Starting Ingestion Verification (Zero-Dep Mode)...")
    
    # Setup Mock Supabase
    mock_supabase = MockClient()
    
    # Mock raw_scrapes data
    scrape_id = str(uuid4())
    mock_scrape_data = {
        'id': scrape_id,
        'source_id': 'test-source',
        'data': {'content': 'This is a test document. It has multiple sentences. We want to see if it chunks correctly.'},
        'metadata': {'date': '2024-01-01'},
        'content_type': 'text/html'
    }
    
    # Mock the chain: table('raw_scrapes').select(...).eq(...).single().execute()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = mock_scrape_data
    
    mock_supabase.table.return_value \
        .select.return_value \
        .eq.return_value \
        .single.return_value = mock_query
        
    # Initialize Service
    llm_client = MockLLMClient()
    vector_backend = MockSupabasePgVectorBackend(mock_supabase, "documents")
    
    service = IngestionService(
        supabase_client=mock_supabase,
        llm_client=llm_client,
        vector_backend=vector_backend,
        chunk_size=50,
        chunk_overlap=10
    )
    
    print(f"Processing scrape {scrape_id}...")
    num_chunks = await service.process_raw_scrape(scrape_id)
    
    print(f"✅ Processed {num_chunks} chunks")
    
    # Verify Backend Upsert
    vector_backend.upsert.assert_called_once()
    chunks_upserted = vector_backend.upsert.call_args[0][0]
    print(f"✅ Backend received {len(chunks_upserted)} chunks")
    
    for i, chunk in enumerate(chunks_upserted):
        print(f"  Chunk {i}: {chunk.content[:30]}...")
        if hasattr(chunk, 'embedding') and chunk.embedding:
             print(f"    - Embedding: {len(chunk.embedding)} dims")
        else:
             print("    - ❌ Missing embedding")
             
    # Verify Update to raw_scrapes
    # table('raw_scrapes').update(...).eq(...).execute()
    mock_supabase.table('raw_scrapes').update.assert_called_once()
    update_args = mock_supabase.table('raw_scrapes').update.call_args[0][0]
    print(f"✅ Updated raw_scrapes status: {update_args}")
    
    print("✅ Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_ingestion())
