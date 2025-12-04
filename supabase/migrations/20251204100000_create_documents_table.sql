-- Add processed status to raw_scrapes if not exists
ALTER TABLE raw_scrapes ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT NULL;
ALTER TABLE raw_scrapes ADD COLUMN IF NOT EXISTS document_id UUID;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table (compatible with llm-common SupabasePgVectorBackend)
-- Assuming the backend expects specific columns. 
-- Usually: id, content, embedding, metadata.
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB DEFAULT '{}'::jsonb,
  chunk_index INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING gin (metadata);
CREATE INDEX IF NOT EXISTS documents_document_id_idx ON documents (document_id);

-- Match function for similarity search (standard name often used)
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  filter jsonb
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.content,
    d.metadata,
    1 - (d.embedding <=> query_embedding) AS similarity
  FROM documents d
  WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
  AND d.metadata @> filter
  ORDER BY d.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
