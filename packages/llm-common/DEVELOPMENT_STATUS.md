# llm-common Development Status

**Last Updated**: 2025-12-04
**Current Version**: v0.3.0
**Status**: 🟢 **Stable - Paused for Downstream Integration**

---

## Current State

### v0.3.0 Released ✅

**Release Date**: 2025-12-04
**Tag**: `v0.3.0`
**Commit**: b085b8b

**What's New:**
- ✅ **SupabasePgVectorBackend**: Production-ready Postgres/pgvector retrieval backend
- ✅ **15 New Tests**: Comprehensive pgvector backend test suite (66 total tests)
- ✅ **Complete Documentation**: Setup guides, SQL examples, production patterns
- ✅ **Zero Breaking Changes**: Fully backward compatible with v0.2.0

**Test Coverage:**
- 66/66 tests passing (100%)
- Core: 12 tests
- Providers: 11 tests
- Web Search: 7 tests
- Retrieval: 36 tests (21 base + 15 pgvector)

---

## Development Pause

### Why Pausing?

llm-common has reached a **natural stopping point** for new features:

1. ✅ **Core abstractions complete**: LLMClient, RetrievalBackend interfaces stable
2. ✅ **Production backends implemented**: z.ai, OpenRouter, Supabase pgvector
3. ✅ **Full test coverage**: 66 tests covering all functionality
4. ✅ **Documentation complete**: Integration guides, examples, setup instructions

**Next validation phase**: Real-world usage in downstream projects.

### What We're Waiting For

**Affordabot Integration** (housing policy Q&A)
- Integrate llm-common v0.3.0 as git submodule
- Implement RAG pipeline for housing policy documents
- Validate: Relevance, latency, cost metrics
- Learn: Chunking strategies, metadata requirements

**Prime Radiant Integration** (conversation retrieval)
- Integrate llm-common v0.3.0 as git submodule
- Implement conversation history search
- Validate: Performance with real conversation data
- Learn: Embedding model choices, cache patterns

### What We'll Learn

From downstream integration, we'll discover:
- **Common patterns**: Do both repos need similar Document/chunking helpers?
- **Pain points**: What boilerplate is repeated? What's missing?
- **Performance**: Does pgvector scale adequately? Do we need Qdrant?
- **API gaps**: Are there missing parameters or features?

---

## On Hold (Until Downstream Integration Complete)

### Deferred Features

These features are **documented but not implemented** pending real-world validation:

1. **Document Ingestion Helper** (initially proposed)
   ```python
   # Deferred: Wait to see actual chunking patterns in Affordabot/Prime Radiant
   class Document:
       content: str
       metadata: dict

   async def ingest_documents(backend, documents, chunk_size=500):
       # Wait to see if both projects need this or have different needs
       pass
   ```
   **Rationale**:
   - Chunking strategies may differ (policy docs vs conversations)
   - Risk of wrong abstraction before seeing usage patterns
   - Both repos can implement custom logic first

2. **ChromaDB Backend**
   - **Status**: Documented, not implemented
   - **Use case**: Local development only
   - **Reason**: Not production-ready, no managed option
   - **When**: If developers request local dev/test support

3. **Qdrant Backend**
   - **Status**: Documented as migration path
   - **Use case**: High-scale vector search (>10M chunks, <100ms latency)
   - **Reason**: pgvector sufficient for current needs
   - **When**: If pgvector hits documented limits (see INTEGRATION_AND_RETRIEVAL.md)

4. **Hybrid Search**
   - **Status**: Mentioned in future enhancements
   - **Use case**: Dense + sparse vector search
   - **When**: If downstream projects need it

5. **Reranking Support**
   - **Status**: Mentioned in future enhancements
   - **Use case**: Post-retrieval reranking with cross-encoders
   - **When**: If relevance metrics show need

---

## When to Resume Feature Work

Resume development when **any** of these conditions are met:

### Condition 1: Downstream Integration Complete
- ✅ Affordabot RAG pipeline working in production
- ✅ Prime Radiant conversation search working
- ✅ Clear patterns identified for common helpers
- 📋 **Action**: Review both implementations, extract common utilities

### Condition 2: Scale Limits Reached
- ⚠️ pgvector query latency p95 > 500ms
- ⚠️ Postgres resource pressure from vector operations
- ⚠️ Document collection > 10M chunks
- 📋 **Action**: Implement Qdrant backend per migration plan

### Condition 3: Feature Gaps Discovered
- 🐛 Missing functionality blocks downstream work
- 🐛 API design issues discovered during integration
- 🐛 Performance bottlenecks not addressable in downstream code
- 📋 **Action**: Create targeted PR to address specific gap

### Condition 4: New Use Case
- 🆕 Third project wants to use llm-common
- 🆕 Different backend needed (e.g., Elasticsearch, Weaviate)
- 🆕 New capability requested (hybrid search, reranking)
- 📋 **Action**: Evaluate against existing abstractions, extend if needed

---

## Current Recommendation

**For llm-common developers:**
- ⏸️ **Pause new features**
- 📚 **Monitor downstream integration** (Affordabot, Prime Radiant)
- 🐛 **Fix bugs** if discovered during integration
- 📖 **Improve docs** based on downstream developer feedback

**For downstream developers:**
- ✅ **Use v0.3.0** (stable, tested, documented)
- 📦 **Add as git submodule** and pin to v0.3.0
- 💡 **Implement your domain logic** (chunking, metadata, queries)
- 📣 **Report issues** if you hit problems

**For future contributors:**
- 📖 **Read documentation** (INTEGRATION_AND_RETRIEVAL.md, examples/)
- ✋ **Wait for downstream validation** before proposing new features
- 🤝 **Coordinate with downstream teams** to understand real needs
- 🎯 **Target specific pain points** rather than speculative features

---

## Success Metrics (To Be Measured)

After downstream integration, we'll evaluate:

### Technical Metrics
- ⏱️ Query latency (target: p95 < 500ms)
- 💰 Cost per 1000 queries (target: < $1)
- 📊 Retrieval relevance (qualitative evaluation)
- 🔧 Integration complexity (developer time to integrate)

### Scale Metrics
- 📚 Document collection size (chunks stored)
- 🔍 Query volume (QPS)
- 💾 Postgres resource usage (% CPU, storage)
- 📈 Need for dedicated vector service (Y/N)

### Developer Experience
- ⏰ Time to first working RAG pipeline
- 🐛 Bugs discovered during integration
- 📝 Documentation gaps identified
- 🔄 API friction points encountered

---

## Version History

| Version | Date | Milestone | Status |
|---------|------|-----------|--------|
| 0.1.0 | 2025-12-01 | Initial implementation (core, providers, web search) | ✅ Complete |
| 0.2.0 | 2025-12-03 | Retrieval module (interfaces, models) | ✅ Complete |
| **0.3.0** | **2025-12-04** | **First backend (pgvector)** | **✅ Complete** |
| 0.3.x | TBD | Bug fixes from downstream integration | 🔜 As needed |
| 0.4.0 | TBD | Common helpers (if patterns emerge) | ⏸️ Paused |
| 1.0.0 | TBD | API stability commitment | 🔮 Future |

---

## Contact & Coordination

**Feature Requests**: Wait for downstream integration validation
**Bug Reports**: Create GitHub issue immediately
**Questions**: Check documentation first, then ask
**Coordination**: Sync with Affordabot and Prime Radiant teams

**Feature-Keys**: bd-svse, affordabot-rdx

---

**Status**: 🟢 Stable and ready for downstream integration
**Next Milestone**: Downstream integration validation
**Recommendation**: Use v0.3.0, pause feature work, focus on integration
