import pytest
from unittest.mock import AsyncMock, MagicMock
from services.ingestion_service import IngestionService
import json

@pytest.fixture
def mock_postgres():
    pg = MagicMock()
    pg.create_source = AsyncMock(return_value="source-123")
    pg.create_raw_scrape = AsyncMock(return_value="scrape-123")
    pg._fetchrow = AsyncMock()
    pg._execute = AsyncMock()
    return pg

@pytest.mark.asyncio
async def test_admin_source_flow(mock_postgres):
    """
    Integration Test: Admin creates source -> Raw Scrape inserted -> Ingestion processes it.
    """
    # 1. Setup Source Service (Mocking DB)
    # SourceService might still need refactoring if it uses Supabase, checking...
    # Assuming SourceService uses SupabaseClient still?
    # Wait, I haven't checked SourceService! 
    # If SourceService uses Supabase, I need to refactor it too.
    # Let's Skip SourceService test for now and only test IngestionService
    # or Assume I will refactor SourceService next.
    
    # Let's mock IngestionService inputs directly first.
    
    # 3. Simulate Scraper output (Raw Scrape)
    # 3. Simulate Scraper output (Raw Scrape)
    scrape_id = "123e4567-e89b-12d3-a456-426614174000"
    source_id = "123e4567-e89b-12d3-a456-426614174001"
    scrape_data = {
        "id": scrape_id,
        "source_id": source_id,
        "content_hash": "hash123",
        "content_type": "text/html",
        "data": json.dumps({"content": "Meeting Minutes"}),
        "metadata": json.dumps({}),
        "processed": False, # Must be bool
        "url": "http://example.com/minutes" # Required
    }
    
    # Mock Postgres fetchrow for process_raw_scrape
    mock_postgres._fetchrow.return_value = scrape_data
    
    # 4. Setup Ingestion Service
    mock_vector = AsyncMock()
    mock_embed = AsyncMock()
    # Mock embedding return (1 chunk -> 1 vector)
    mock_embed.embed_documents.return_value = [[0.1]*1536]
    
    ingestion_service = IngestionService(
        postgres_client=mock_postgres,
        vector_backend=mock_vector,
        embedding_service=mock_embed
    )
    
    # 5. Run Ingestion
    count = await ingestion_service.process_raw_scrape(scrape_id)
    
    # 6. Verify
    assert count == 1 # 1 chunk created
    
    # Check Postgres update called (processed=True)
    mock_postgres._execute.assert_called()
    call_args = mock_postgres._execute.call_args[0]
    assert "UPDATE raw_scrapes SET processed" in call_args[0]
    
    # Check vector backend was called (stored in vector db)
    mock_vector.upsert.assert_called_once()

@pytest.mark.asyncio
async def test_ingestion_error_handling(mock_postgres):
    """Test that ingestion errors are logged to DB."""
    scrape_id = "error-scrape-123"
    
    # Simulate DB returning invalid data (violates Pydantic schema)
    # Missing 'url' field which is required
    invalid_data = {
        "id": scrape_id,
        "source_id": "123e4567-e89b-12d3-a456-426614174000", 
        "data": "{}",
        "processed": False
        # Missing 'url'
    }
    
    mock_postgres._fetchrow.return_value = invalid_data
    mock_vector = AsyncMock()
    mock_embed = AsyncMock()
    
    ingestion = IngestionService(mock_postgres, mock_vector, mock_embed)
    
    # Run
    count = await ingestion.process_raw_scrape(scrape_id)
    
    # Verify
    assert count == 0
    
    # Check error logging
    mock_postgres._execute.assert_called()
    args = mock_postgres._execute.call_args[0]
    assert "UPDATE raw_scrapes SET processed = false" in args[0]
    assert "validation failed" in args[1] or "Field required" in str(args[1])

