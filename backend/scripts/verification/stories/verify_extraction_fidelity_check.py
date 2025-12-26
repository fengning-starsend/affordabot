
import asyncio
import sys
import uuid
import json
from pathlib import Path

# Add backend root to path
backend_root = str(Path(__file__).parent.parent.parent.parent)
if backend_root not in sys.path:
    sys.path.append(backend_root)

from db.postgres_client import PostgresDB
from services.storage.s3_storage import S3Storage
from services.ingestion_service import IngestionService
from services.retrieval.local_pgvector import LocalPgVectorBackend
from llm_common.embeddings import EmbeddingService

# --- MOCKS ---
class MockEmbeddingService(EmbeddingService):
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 4096 for _ in texts]
    async def embed_query(self, text: str) -> list[float]:
        return [0.1] * 4096

# --- STORY EXECUTION ---

def run_story() -> tuple[bool, str]:
    try:
        return asyncio.run(_async_run_story())
    except Exception as e:
        return False, f"Exception: {e}"

async def _async_run_story() -> tuple[bool, str]:
    db = PostgresDB()
    await db.connect()
    
    storage = S3Storage()
    embedding_service = MockEmbeddingService()
    vector_backend = LocalPgVectorBackend(table_name="document_chunks", postgres_client=db)
    
    ingestion = IngestionService(
        postgres_client=db,
        storage_backend=storage,
        vector_backend=vector_backend,
        embedding_service=embedding_service,
        chunk_size=500
    )
    
    # 1. Setup Golden Input
    test_id = str(uuid.uuid4())
    # A tricky input: HTML with tables or formatting that might break extractors
    # We want to ensure "$5,000" and "Section 8" are preserved explicitly.
    html_content = """
    <html>
        <body>
            <div id="content">
                <h1>Housing Bill</h1>
                <p>Whereas housing is expensive;</p>
                <table>
                    <tr><td>Fee Type</td><td>Amount</td></tr>
                    <tr><td>Development Check</td><td>$5,000</td></tr>
                </table>
                <p>Refer to <strong>Section 8</strong> for details.</p>
            </div>
        </body>
    </html>
    """
    
    # Setup DB Prereqs
    JURISDICTION_ID = "11111111-1111-1111-1111-111111111111"
    await db._execute("INSERT INTO jurisdictions (id, name, type) VALUES ($1, 'Verification City', 'city') ON CONFLICT DO NOTHING", JURISDICTION_ID)
    source_rows = await db._fetch("SELECT id FROM sources WHERE jurisdiction_id = $1 LIMIT 1", JURISDICTION_ID)
    if not source_rows:
        await db._execute("INSERT INTO sources (jurisdiction_id, url, type, status) VALUES ($1, 'http://verify.com', 'test', 'active')", JURISDICTION_ID)
        source_rows = await db._fetch("SELECT id FROM sources WHERE jurisdiction_id = $1 LIMIT 1", JURISDICTION_ID)
    source_id = source_rows[0]['id']
    
    data_json = json.dumps({"content": html_content})
    await db._execute("""
        INSERT INTO raw_scrapes (id, source_id, url, content_hash, content_type, data, processed)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """, test_id, source_id, "http://verify.com/extract_test", "hash_extract", "text/html", data_json, False)
    
    # 2. Run Ingestion
    await ingestion.process_raw_scrape(test_id)
    
    # 3. Verify Chunks
    # We need to find the chunks associated with this scrape. 
    # raw_scrapes -> document_id (after process) -> document_chunks
    row = await db._fetchrow("SELECT document_id FROM raw_scrapes WHERE id = $1", test_id)
    if not row or not row['document_id']:
        return False, "Ingestion failed to create document_id."
        
    doc_id = row['document_id']
    chunks = await db._fetch("SELECT content FROM document_chunks WHERE document_id = $1", doc_id)
    
    if not chunks:
        return False, "No chunks generated in DB."
        
    # Combine all text to search
    full_text = " ".join([c['content'] for c in chunks])
    
    failures = []
    if "$5,000" not in full_text:
        failures.append("Failed to extract '$5,000' from table.")
    if "Section 8" not in full_text:
        failures.append("Failed to extract 'Section 8'.")
        
    if failures:
        return False, "; ".join(failures)
        
    return True, f"Extraction Fidelity Verified: Found {len(chunks)} chunks containing all golden tokens."

if __name__ == "__main__":
    success, message = run_story()
    print(f"{'✅' if success else '❌'} {message}")
    sys.exit(0 if success else 1)
