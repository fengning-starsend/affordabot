"""Factory for creating vector retrieval backends."""

from typing import Optional, Callable, Awaitable
from llm_common.retrieval import RetrievalBackend


def create_vector_backend(
    postgres_client=None, # Not used directly by create_pg_backend but kept for signature compat if needed, or better, remove it?
    # Actually, create_pg_backend takes database_url.
    # Caller can pass DSN if they have it, or we read Env.
    # postgres_client argument was added by me in run_rag_spiders.py.
    # Let's support it or just rely on Env.
    # Best to rely on Env for create_pg_backend as it handles connection pool itself.
    embedding_fn: Optional[Callable[[str], Awaitable[list[float]]]] = None,
    **kwargs # Swallow legacy args like supabase_client
) -> RetrievalBackend:
    """
    Create vector retrieval backend (LocalPgVector for V3).
    
    Args:
        postgres_client: PostgresDB instance (required for LocalPgVector)
        embedding_fn: Async function to generate embeddings
        
    Returns:
        RetrievalBackend instance
    """
    # V3: Use LocalPgVectorBackend to fix JSONB encoding issues and control logic
    from services.retrieval.local_pgvector import LocalPgVectorBackend
    from db.postgres_client import PostgresDB
    
    if not postgres_client:
        # If not provided, assume Env var available and instantiate
        # But allow fallback if caller intends to set it later? 
        # LocalPgVectorBackend checks for db presence lazily in upsert usually,
        # but better to provide it.
        try:
             postgres_client = PostgresDB()
             # Note: connecting might be required later
        except Exception:
             pass

    return LocalPgVectorBackend(
        table_name="documents",
        postgres_client=postgres_client
    )
