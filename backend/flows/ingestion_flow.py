"""Prefect flow for ingesting raw scrapes into vector database."""

from prefect import flow, task
from supabase import create_client
import os
import asyncio
from services.ingestion_service import IngestionService
from llm_common import LLMClient
from llm_common.retrieval import SupabasePgVectorBackend

@task(name="fetch_unprocessed_scrapes", retries=2)
def fetch_unprocessed_scrapes():
    """Fetch raw scrapes that haven't been processed yet."""
    supabase = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_ROLE_KEY']
    )
    
    # Check if 'processed' column exists or handle it. 
    # Assuming we added 'processed' boolean to raw_scrapes or we check against documents table.
    # For now, let's assume we added a 'processed' column in a migration or we query for 
    # scrapes that don't have a corresponding entry in documents (if we had a link).
    # The IngestionService updates 'processed' = True.
    
    result = supabase.table('raw_scrapes')\
        .select('id')\
        .is_('processed', 'null')\
        .execute()
    
    return [row['id'] for row in result.data]

@task(name="ingest_scrape", retries=3)
async def ingest_scrape(scrape_id: str):
    """Process a single raw scrape into embedded chunks."""
    supabase = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_ROLE_KEY']
    )
    
    # Initialize components
    llm_client = LLMClient(provider="openai") # Provider config might vary
    
    # Initialize Vector Backend
    # Assuming SupabasePgVectorBackend takes the supabase client and table name
    vector_backend = SupabasePgVectorBackend(
        supabase_client=supabase,
        table_name="documents"
    )
    
    ingestion_service = IngestionService(
        supabase_client=supabase,
        llm_client=llm_client,
        vector_backend=vector_backend
    )
    
    # Process scrape
    num_chunks = await ingestion_service.process_raw_scrape(scrape_id)
    
    return {
        "scrape_id": scrape_id,
        "chunks_created": num_chunks
    }

@flow(name="ingest_all_scrapes", log_prints=True)
async def ingest_all():
    """Ingest all unprocessed raw scrapes."""
    print("🔍 Fetching unprocessed scrapes...")
    scrape_ids = fetch_unprocessed_scrapes()
    
    if not scrape_ids:
        print("✅ No unprocessed scrapes found")
        return {"processed": 0}
    
    print(f"📊 Found {len(scrape_ids)} unprocessed scrapes")
    
    # Process in parallel
    results = await ingest_scrape.map(scrape_ids)
    
    total_chunks = sum(r["chunks_created"] for r in results)
    print(f"✅ Processed {len(scrape_ids)} scrapes → {total_chunks} chunks")
    
    return {
        "processed": len(scrape_ids),
        "total_chunks": total_chunks
    }

if __name__ == "__main__":
    asyncio.run(ingest_all())
