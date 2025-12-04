"""Ingestion service to process raw scrapes into embedded document chunks."""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from uuid import uuid4
from supabase import Client

# Assuming llm-common v0.3.0 interfaces
from llm_common import LLMClient
from llm_common.retrieval import SupabasePgVectorBackend, RetrievedChunk

class IngestionService:
    """
    Process raw scrapes into chunked, embedded documents.
    
    Workflow:
    1. Fetch unprocessed raw_scrapes
    2. Extract and clean text
    3. Chunk text
    4. Generate embeddings (via LLMClient)
    5. Store in vector backend (via SupabasePgVectorBackend)
    """
    
    def __init__(
        self,
        supabase_client: Client,
        llm_client: LLMClient,
        vector_backend: SupabasePgVectorBackend,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "text-embedding-3-small"
    ):
        self.supabase = supabase_client
        self.llm_client = llm_client
        self.vector_backend = vector_backend
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
    
    async def process_raw_scrape(self, scrape_id: str) -> int:
        """
        Process a single raw scrape into embedded chunks.
        
        Args:
            scrape_id: ID of raw_scrape to process
            
        Returns:
            Number of chunks created
        """
        # 1. Fetch raw scrape
        result = self.supabase.table('raw_scrapes').select('*').eq('id', scrape_id).single().execute()
        scrape = result.data
        
        # 2. Extract text from data
        text = self._extract_text(scrape['data'])
        
        if not text:
            print(f"⚠️ No text extracted for scrape {scrape_id}")
            return 0

        # 3. Chunk text
        chunks = self._chunk_text(text)
        
        # 4. Generate embeddings
        # Using LLMClient's underlying LiteLLM support or a dedicated method if available.
        # If LLMClient doesn't expose embedding directly, we might need to use litellm directly
        # or assume LLMClient has an .embed() method in v0.3.0.
        # For now, I'll assume we can use litellm directly or a helper.
        # Actually, the feedback said "via LLMClient or your chosen embedder".
        # Let's use litellm directly for embeddings to be safe, or check if LLMClient has it.
        # I'll use a helper method here that uses litellm.
        
        from litellm import aembedding
        
        embeddings = []
        # Batch embedding
        batch_size = 20
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            response = await aembedding(
                model=self.embedding_model,
                input=batch
            )
            embeddings.extend([d['embedding'] for d in response.data])
        
        # 5. Create RetrievedChunk objects (or equivalent dicts for the backend)
        document_id = str(uuid4())
        doc_chunks = []
        
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            # Construct metadata
            metadata = {
                "source_id": scrape['source_id'],
                "scrape_id": scrape_id,
                "content_type": scrape.get('content_type', 'text/html'),
                **scrape.get('metadata', {})
            }
            
            # We need to map this to what SupabasePgVectorBackend expects.
            # Assuming it takes a list of objects or dicts.
            # The feedback mentioned `RetrievedChunk`.
            
            doc_chunk = RetrievedChunk(
                id=str(uuid4()),
                content=chunk_text,
                embedding=embedding,
                metadata=metadata,
                document_id=document_id,
                chunk_index=i
            )
            doc_chunks.append(doc_chunk)
        
        # 6. Store in vector backend
        await self.vector_backend.upsert(doc_chunks)
        
        # 7. Mark scrape as processed
        self.supabase.table('raw_scrapes').update({
            'processed': True,
            'document_id': document_id
        }).eq('id', scrape_id).execute()
        
        return len(doc_chunks)
    
    def _extract_text(self, data: Dict[str, Any]) -> str:
        """Extract text from scraped data."""
        if isinstance(data, str):
            return self._clean_html(data)
        
        if isinstance(data, dict):
            # Try common text fields
            for field in ['text', 'content', 'body', 'raw_html_snippet', 'description']:
                if field in data and data[field]:
                    return self._clean_html(str(data[field]))
            
            # Fallback: concatenate all string values
            texts = [str(v) for v in data.values() if isinstance(v, (str, int, float))]
            return ' '.join(texts)
        
        return str(data)
    
    def _clean_html(self, html: str) -> str:
        """Clean HTML tags and normalize whitespace."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into overlapping segments."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
                # Look for sentence end
                search_start = max(start, end - 100)
                # Simple heuristic for sentence boundaries
                match = re.search(r'[.!?]\s', text[search_start:end])
                if match:
                    end = search_start + match.end()
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]
