# Post-Merge Plan: pgvector Backend

**PR**: #3 (feature-bd-svse-pgvector-backend)
**Status**: Awaiting review and merge
**Feature-Key**: bd-svse

---

## Step 1: Tag v0.3.0 (After PR Merge)

### Version Bump Rationale

This release warrants a **minor version bump** (0.2.0 → 0.3.0) because:

1. **First Backend Implementation**: Concrete retrieval backend (not just interface)
2. **Production Ready**: Full Supabase pgvector integration with tests and docs
3. **New Public API**: `SupabasePgVectorBackend` exported
4. **Milestone Achievement**: Complete RAG stack now available

**Not a patch** (0.2.1) because:
- This is a significant feature addition, not a bugfix
- Adds substantial new functionality (backend implementation)
- Represents completion of retrieval module vision

**Not a major** (1.0.0) because:
- Still no breaking changes
- Core API remains stable and backward compatible
- Not yet ready to commit to full API stability

### Tagging Steps

```bash
# After PR #3 is merged to master
git checkout master
git pull origin master

# Verify tests still pass
poetry run pytest -v  # Should show 66 passing

# Update version in pyproject.toml
# Change: version = "0.2.0" → version = "0.3.0"

# Commit version bump
git add pyproject.toml
git commit -m "chore: Bump version to 0.3.0

First backend implementation milestone:
- SupabasePgVectorBackend production-ready
- Complete RAG retrieval stack
- 66 tests passing (15 new pgvector tests)
- Full documentation and examples

Feature-Key: bd-svse"

# Create annotated tag
git tag -a v0.3.0 -m "Release v0.3.0: Supabase pgvector backend

This release adds the first production-ready retrieval backend,
completing the RAG infrastructure for llm-common.

New features:
- SupabasePgVectorBackend: Postgres/pgvector integration
- RPC-based similarity search
- Configurable table/column schema
- Complete setup guide with SQL examples
- 15 comprehensive backend tests

Technical details:
- Supports async embedding delegation
- Metadata filtering and top_k/min_score
- Health checks and context managers
- Mock-based testing for zero dependencies

Use cases:
- Affordabot: Housing policy Q&A
- Prime Radiant: Conversation history retrieval

Breaking changes: None
New dependencies: None (Supabase client optional)
Tests: 66 passing (100%)

Feature-Key: bd-svse"

# Push tag
git push origin master
git push origin v0.3.0

# Verify tag on remote
git ls-remote --tags origin v0.3.0
```

### Release Notes (GitHub)

After tagging, create GitHub release notes highlighting:

1. **Key Feature**: First retrieval backend implementation
2. **Production Ready**: Supabase pgvector integration
3. **Setup Guide**: Complete SQL and example code
4. **Migration Path**: How to switch backends later
5. **Use Cases**: Affordabot and Prime Radiant integration plans

---

## Step 2: Downstream Integration

### Affordabot Integration

**Timeline**: After v0.3.0 tagged
**Branch**: `feature-affordabot-rdx-llm-common-pgvector`

#### Implementation Steps

1. **Add llm-common Submodule** (if not already added)
   ```bash
   cd ~/affordabot
   git submodule add git@github.com:stars-end/llm-common.git packages/llm-common
   cd packages/llm-common
   git checkout v0.3.0
   ```

2. **Create Document Chunks Table** in Supabase
   ```sql
   -- Affordabot housing policy knowledge base
   CREATE TABLE housing_policy_chunks (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     content TEXT NOT NULL,
     embedding VECTOR(1536),  -- OpenAI text-embedding-3-small
     source TEXT NOT NULL,     -- Policy document URL/ID
     jurisdiction TEXT,        -- City/county/state
     policy_type TEXT,         -- Zoning, affordability, etc.
     effective_date DATE,
     page_number INTEGER,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Create index for vector similarity search
   CREATE INDEX ON housing_policy_chunks
   USING ivfflat (embedding vector_cosine_ops)
   WITH (lists = 100);

   -- Create RPC function
   CREATE OR REPLACE FUNCTION match_housing_policies(
     query_embedding VECTOR(1536),
     match_count INT DEFAULT 5,
     match_threshold FLOAT DEFAULT 0.7,
     jurisdiction_filter TEXT DEFAULT NULL
   )
   RETURNS TABLE (
     id UUID,
     content TEXT,
     source TEXT,
     jurisdiction TEXT,
     policy_type TEXT,
     similarity FLOAT
   )
   LANGUAGE plpgsql
   AS $$
   BEGIN
     RETURN QUERY
     SELECT
       housing_policy_chunks.id,
       housing_policy_chunks.content,
       housing_policy_chunks.source,
       housing_policy_chunks.jurisdiction,
       housing_policy_chunks.policy_type,
       1 - (housing_policy_chunks.embedding <=> query_embedding) AS similarity
     FROM housing_policy_chunks
     WHERE
       (jurisdiction_filter IS NULL OR housing_policy_chunks.jurisdiction = jurisdiction_filter)
       AND 1 - (housing_policy_chunks.embedding <=> query_embedding) > match_threshold
     ORDER BY housing_policy_chunks.embedding <=> query_embedding
     LIMIT match_count;
   END;
   $$;
   ```

3. **Implement Embedding Service**
   ```python
   # affordabot/services/embedding_service.py
   from openai import AsyncOpenAI
   from llm_common import SupabasePgVectorBackend
   from supabase import create_async_client

   class EmbeddingService:
       def __init__(self, openai_api_key: str, supabase_url: str, supabase_key: str):
           self.openai = AsyncOpenAI(api_key=openai_api_key)
           self.supabase = create_async_client(supabase_url, supabase_key)

       async def embed_text(self, text: str) -> list[float]:
           response = await self.openai.embeddings.create(
               input=text,
               model="text-embedding-3-small"
           )
           return response.data[0].embedding

       async def create_retrieval_backend(self) -> SupabasePgVectorBackend:
           return SupabasePgVectorBackend(
               supabase_client=self.supabase,
               table="housing_policy_chunks",
               vector_col="embedding",
               text_col="content",
               metadata_cols=["jurisdiction", "policy_type", "effective_date"],
               embed_fn=self.embed_text,
               source_col="source",
               rpc_function="match_housing_policies"
           )
   ```

4. **Use in Analysis Pipeline**
   ```python
   # affordabot/analysis/policy_qa.py
   async def answer_policy_question(
       question: str,
       jurisdiction: str | None = None
   ) -> str:
       embedding_service = EmbeddingService(...)
       backend = await embedding_service.create_retrieval_backend()

       # Retrieve relevant policy chunks
       filters = {"jurisdiction": jurisdiction} if jurisdiction else None
       chunks = await backend.retrieve(
           query=question,
           top_k=5,
           min_score=0.7,
           filters=filters
       )

       # Format context for LLM
       context = "\n\n".join([
           f"[{i+1}] {chunk.source}\n{chunk.content}"
           for i, chunk in enumerate(chunks)
       ])

       # Generate answer using ZaiClient
       from llm_common import ZaiClient
       client = ZaiClient(...)
       response = await client.generate(
           messages=[{
               "role": "system",
               "content": "You are a housing policy expert. Answer questions based on the provided policy documents."
           }, {
               "role": "user",
               "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
           }]
       )

       return response.content
   ```

### Prime Radiant Integration

**Timeline**: After Affordabot integration proven
**Branch**: `feature-bd-svse-conversation-retrieval`

#### Use Case: Conversation History Search

1. **Table Schema**
   ```sql
   CREATE TABLE conversation_chunks (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     content TEXT NOT NULL,
     embedding VECTOR(384),  -- Smaller model for speed
     conversation_id UUID REFERENCES conversations(id),
     user_id UUID REFERENCES users(id),
     message_role TEXT,     -- 'user' or 'assistant'
     chunk_index INTEGER,   -- Position in conversation
     created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

2. **Integration Pattern**
   - Use smaller embedding model (384-dim) for speed
   - Retrieve relevant past conversations for context
   - Enable "similar question" suggestions

---

## Step 3: Future Backend Options (Not Implemented)

### ChromaDB (Development Only)

**Status**: Documented, not implemented
**When**: Local development, unit testing
**Why not now**: Not production-ready, no managed option

If implemented in future:
```python
# llm_common/retrieval/backends/chroma_backend.py
class ChromaBackend(RetrievalBackend):
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        import chromadb
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)
```

### Qdrant (High-Scale Option)

**Status**: Documented as migration path
**When**: If pgvector hits limits (>10M chunks, <100ms latency needed)
**Cost**: Free tier 1GB, $25/mo for 4GB

Migration criteria (from docs):
- Vector table > 50% of Postgres capacity
- Query p95 latency > 500ms
- CPU usage from vector ops > 30%

---

## Step 4: Documentation Updates

After merge and version bump:

1. **Update IMPLEMENTATION_STATUS.md**
   - Add pgvector backend to completed components
   - Update test count (51 → 66)
   - Add v0.3.0 to version history

2. **Update README.md** (if needed)
   - Add pgvector backend to features list
   - Update installation/usage examples

3. **Create CHANGELOG.md** entry
   ```markdown
   ## [0.3.0] - 2025-12-04

   ### Added
   - SupabasePgVectorBackend: Production-ready Postgres/pgvector retrieval backend
   - 15 comprehensive tests for pgvector backend (66 total tests)
   - Complete setup guide in examples/retrieval_usage.py
   - Backend choice rationale documentation

   ### Changed
   - None

   ### Deprecated
   - None

   ### Removed
   - None

   ### Fixed
   - None
   ```

---

## Timeline Summary

1. **Now**: PR #3 open for review
2. **After review**: Merge to master
3. **Immediately after merge**: Tag v0.3.0, update docs
4. **Week 1**: Affordabot integration (housing policy Q&A)
5. **Week 2-3**: Prime Radiant integration (conversation retrieval)
6. **Future**: Evaluate need for Qdrant based on scale metrics

---

## Success Metrics

### Technical
- ✅ All 66 tests passing
- ✅ Zero breaking changes
- ✅ Public API exports working
- 🎯 Affordabot RAG pipeline working
- 🎯 Prime Radiant conversation search working

### Cost/Performance
- 🎯 Affordabot: <$50/month for embeddings + storage
- 🎯 Query latency: p95 < 300ms
- 🎯 Cache hit rate: >80% (if caching implemented)

### Adoption
- 🎯 Both downstream projects using pgvector backend
- 🎯 No need to switch to Qdrant (pgvector scales adequately)
- 🎯 Documentation used successfully by other developers

---

**Status**: Ready for PR review
**Next Action**: Wait for PR #3 approval and merge
**Feature-Key**: bd-svse
