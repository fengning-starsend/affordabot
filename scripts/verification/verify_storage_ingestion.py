import asyncio
import sys
import os
from uuid import uuid4

# Add backend to path (still needed for local script)
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from services.ingestion_service import IngestionService
from contracts.storage import BlobStorage
# Mocks
from unittest.mock import MagicMock, AsyncMock

class MockBlobStorage(BlobStorage):
    async def upload(self, path: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        print(f"✅ Mock Upload: {path} ({len(content)} bytes)")
        return f"s3://mock-bucket/{path}"

    async def download(self, path: str) -> bytes:
        return b"mock content"

    async def get_url(self, path: str, expiry_seconds: int = 3600) -> str:
        return f"https://mock-storage.com/{path}"

async def main():
    print("Initializing IngestionService with Mock Storage...")
    
    # Mock dependencies
    supabase = MagicMock()
    # Mock raw scrape fetch
    scrape_id = str(uuid4())
    supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": scrape_id,
        "source_id": "test_jurisdiction",
        "data": {"content": "Test content for storage verification"},
        "url": "http://example.com/doc.pdf",
        "content_type": "application/pdf"
    }
    
    vector_backend = AsyncMock()
    embedding_service = AsyncMock()
    embedding_service.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    
    storage = MockBlobStorage()
    
    service = IngestionService(
        supabase_client=supabase,
        vector_backend=vector_backend,
        embedding_service=embedding_service,
        storage_backend=storage
    )
    
    print(f"Processing scrape {scrape_id}...")
    await service.process_raw_scrape(scrape_id)
    
    # Verify update call includes storage_uri
    update_calls = supabase.table.return_value.update.call_args_list
    # Look for the call that updates 'storage_uri'
    storage_update_found = False
    for call in update_calls:
        if 'storage_uri' in call[0][0]:
            print(f"✅ Database Update Verified: {call[0][0]}")
            storage_update_found = True
            
    if not storage_update_found:
        print("❌ Database was NOT updated with storage_uri")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
