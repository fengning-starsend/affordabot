# LLM Framework - Implementation Summary

**Version:** 1.0  
**Date:** 2025-12-01  
**Status:** Ready for Implementation  

---

## 📋 Documentation Index

This implementation consists of four comprehensive documents:

1. **[Product Requirements Document (PRD)](./LLM_FRAMEWORK_PRD.md)**
   - Functional requirements for both projects
   - User stories and success metrics
   - Cost analysis and budget targets

2. **[Technical Specification](./LLM_FRAMEWORK_TECHNICAL_SPEC.md)**
   - Architecture diagrams and design decisions
   - Complete API reference with code examples
   - Database schema with SQL migrations
   - Testing strategy and coverage targets

3. **[Migration Plan](./LLM_FRAMEWORK_MIGRATION.md)**
   - Step-by-step migration instructions
   - Feature flag strategy for safe rollout
   - Rollback procedures
   - Timeline and milestones

4. **[Original Research](./LLM_FRAMEWORK_PLAN.md)**
   - Initial analysis and framework comparison
   - LiteLLM vs LangChain vs Custom
   - Cost-benefit analysis

---

## 🎯 Quick Start for Junior Developers

### What You're Building

A **shared LLM framework** (`llm-common`) that both `affordabot` and `prime-radiant-ai` will use for:
- **Multi-provider LLM calls** (OpenRouter, z.ai, OpenAI, Anthropic)
- **Web search with caching** (z.ai API + Supabase)
- **Cost tracking and budgets**
- **Structured outputs** (Pydantic models)

### Why This Matters

**Before:**
- `affordabot`: Custom `DualModelAnalyzer` (250 lines)
- `prime-radiant-ai`: Custom LLM client (1,000 lines)
- **Total:** ~1,250 lines of duplicated, brittle code

**After:**
- `llm-common`: ~300 lines (shared)
- `affordabot`: ~200 lines (domain-specific orchestration)
- `prime-radiant-ai`: ~100 lines (conversation memory)
- **Total:** ~600 lines (52% reduction)

---

## 📦 What's in the Package

### `llm-common` (Shared Library)

```
llm-common/
├── llm_common/
│   ├── llm_client.py       # LiteLLM wrapper (multi-provider)
│   ├── web_search.py       # z.ai search + 2-tier caching
│   ├── cost_tracker.py     # Budget enforcement
│   ├── models.py           # Pydantic models
│   └── exceptions.py       # Custom errors
├── tests/                  # 80% coverage target
└── examples/               # Usage examples
```

**Key Features:**
- ✅ **Multi-Provider:** Switch between OpenRouter, z.ai, OpenAI, Anthropic with one line
- ✅ **Caching:** 80% cache hit rate → $450/month → $90/month savings
- ✅ **Type-Safe:** Pydantic models for structured outputs
- ✅ **Budget Limits:** Automatic enforcement (daily/monthly)
- ✅ **Fallback Chain:** Try multiple models until one succeeds

---

## 🚀 Implementation Roadmap

### Week 1: Foundation
**Goal:** Create `llm-common` package with tests

**Tasks:**
1. Set up package structure
2. Implement `LLMClient` (LiteLLM wrapper)
3. Implement `WebSearchClient` (z.ai + caching)
4. Implement `CostTracker`
5. Write unit tests (80% coverage)
6. Create examples

**Deliverables:**
- Working `llm-common` package
- 30+ passing tests
- Documentation

---

### Week 2: Affordabot Migration
**Goal:** Migrate affordabot to use `llm-common`

**Tasks:**
1. Add `llm-common` as git submodule
2. Create database migrations (pipeline_runs, cost_tracking)
3. Implement `AnalysisPipeline` (Research → Generate → Review)
4. Implement `LegislationSearchService`
5. Add feature flag for safe rollout
6. Integration tests

**Deliverables:**
- New pipeline working alongside old one
- Feature flag for gradual rollout
- Model comparison dashboard

---

### Week 3: Prime-Radiant-AI Migration
**Goal:** Migrate prime-radiant-ai to use `llm-common`

**Tasks:**
1. Add `llm-common` as git submodule
2. Create database migrations (conversations)
3. Implement `ConversationMemory`
4. Implement `FinanceSearchService`
5. Update chat endpoints
6. Integration tests

**Deliverables:**
- Conversation history persistence
- Context injection (portfolio, tax pages)
- Working chat with memory

---

### Week 4: Cleanup & Optimization
**Goal:** Remove old code, optimize performance

**Tasks:**
1. Remove old implementations
2. Remove feature flags
3. Tune cache TTLs
4. Model comparison experiments
5. Documentation updates
6. Performance benchmarking

**Deliverables:**
- Clean codebase (no old code)
- Optimized cache hit rate
- Model performance reports

---

## 💡 Key Design Decisions

### 1. LiteLLM vs Custom Client
**Decision:** Use LiteLLM

**Rationale:**
- ✅ Battle-tested (3M+ downloads/month)
- ✅ Supports 100+ providers
- ✅ Built-in retry, fallback, cost tracking
- ✅ Saves ~1,000 lines of custom code

**Alternative Considered:** LangChain (rejected: too heavy, opinionated)

---

### 2. Git Submodule vs PyPI
**Decision:** Git submodule (initially)

**Rationale:**
- ✅ Solo developer (no CI/CD overhead)
- ✅ Fast iteration during development
- ✅ Easy to migrate to PyPI later

**Future:** Publish to PyPI once stable (Week 9+)

---

### 3. Custom Orchestration vs LangGraph
**Decision:** Custom orchestration (~200 lines)

**Rationale:**
- ✅ Simple, maintainable
- ✅ No framework lock-in
- ✅ Easy to understand for junior devs

**Alternative Considered:** LangGraph (rejected: overkill for solo dev)

---

### 4. 2-Tier Caching Strategy
**Decision:** In-memory (L1) + Supabase (L2)

**Rationale:**
- ✅ 80% cache hit rate
- ✅ Cost savings: $450/month → $90/month
- ✅ Simple implementation

**Cache TTLs:**
- L1 (memory): 1 hour
- L2 (Supabase): 24 hours

---

## 📊 Success Metrics

### Primary Metrics
1. **Code Reduction:** 50% reduction (1,250 LOC → 600 LOC) ✅
2. **Cost Savings:** 60% reduction in web search costs ($450 → $90) ✅
3. **Model Experimentation:** 5+ model combinations tested/month ✅

### Secondary Metrics
1. **Cache Hit Rate:** ≥ 80%
2. **Pipeline Latency:** P95 < 10s
3. **Error Rate:** < 1%
4. **Test Coverage:** ≥ 80%

---

## 🔧 Technical Highlights

### Affordabot: Sequential Pipeline

```python
from llm_common import LLMClient, WebSearchClient
from services.llm.orchestrator import AnalysisPipeline

# Initialize
llm = LLMClient(provider="openrouter")
search = WebSearchClient(api_key="...", supabase_client=supabase)
pipeline = AnalysisPipeline(llm, search, cost_tracker, supabase)

# Run pipeline
result = await pipeline.run(
    bill_id="AB-1234",
    bill_text="...",
    jurisdiction="California",
    models={
        "research": "gpt-4o-mini",      # Cheap for queries
        "generate": "gpt-4o",            # Powerful for analysis
        "review": "claude-3.5-sonnet"    # Best for critique
    }
)

# Result is a validated Pydantic model
assert isinstance(result, BillAnalysis)
```

---

### Prime-Radiant-AI: Stateful Chat

```python
from llm_common import LLMClient
from services.memory import ConversationMemory

# Initialize
llm = LLMClient(provider="openrouter")
memory = ConversationMemory(db_client=supabase, user_id="user_123")

# Get context (history + page-specific)
messages = await memory.get_context(page="portfolio")

# Add user message
messages.append({"role": "user", "content": "Should I buy AAPL?"})

# Call LLM
response = await llm.chat(messages=messages, model="gpt-4o")

# Save conversation
await memory.save_message("user", "Should I buy AAPL?")
await memory.save_message("assistant", response)
```

---

## 🗄️ Database Schema

### Shared Tables
- `web_search_cache` - Persistent cache (24hr TTL)
- `cost_tracking` - LLM and search costs

### Affordabot Tables
- `pipeline_runs` - Track analysis runs for model comparison
- `pipeline_steps` - Log individual steps (debugging)

### Prime-Radiant-AI Tables
- `conversations` - Conversation history (90-day TTL)

**Total:** 5 new tables

---

## 🧪 Testing Strategy

### Unit Tests (80% coverage)
- `llm-common`: LLMClient, WebSearchClient, CostTracker
- Mock external APIs (OpenRouter, z.ai)

### Integration Tests
- Full pipeline (Research → Generate → Review)
- Conversation memory (save/retrieve)
- Cache hit rate validation

### Manual Tests
- Model comparison (3+ models)
- Cost tracking (verify budgets)
- UI testing (admin dashboard, chat)

---

## 📈 Cost Analysis

### Current State (Estimated)
- **Web Search:** $450/month (1,500 searches/day, no caching)
- **LLM Calls:** $150/month (mix of free + paid models)
- **Total:** $600/month

### After Implementation
- **Web Search:** $90/month (80% cache hit rate)
- **LLM Calls:** $150/month (same, but with better tracking)
- **Total:** $240/month

**Savings:** $360/month (60% reduction)

---

## 🚨 Risk Mitigation

### Risk 1: Migration Breaks Production
**Mitigation:** Feature flags + gradual rollout (10% → 50% → 100%)

### Risk 2: Performance Degradation
**Mitigation:** Benchmarking before/after, rollback plan

### Risk 3: Cost Overruns
**Mitigation:** Budget limits, daily/monthly alerts

### Risk 4: Cache Misses
**Mitigation:** Monitor hit rate, tune TTLs

---

## 📚 Resources for Junior Developers

### Required Reading
1. [LiteLLM Documentation](https://docs.litellm.ai/)
2. [Instructor Documentation](https://python.useinstructor.com/)
3. [Pydantic Documentation](https://docs.pydantic.dev/)

### Recommended Reading
1. [z.ai Web Search API](https://docs.z.ai/guides/tools/web-search)
2. [OpenRouter Documentation](https://openrouter.ai/docs)

### Code Examples
- See `llm-common/examples/` for working examples
- See [Technical Spec](./LLM_FRAMEWORK_TECHNICAL_SPEC.md) for full API reference

---

## ✅ Implementation Checklist

### Pre-Implementation
- [ ] Review all 4 documents (PRD, Tech Spec, Migration, Summary)
- [ ] Set up development environment
- [ ] Get API keys (OpenRouter, z.ai)
- [ ] Backup databases

### Week 1: `llm-common`
- [ ] Create package structure
- [ ] Implement `LLMClient`
- [ ] Implement `WebSearchClient`
- [ ] Implement `CostTracker`
- [ ] Write tests (80% coverage)
- [ ] Create examples

### Week 2: Affordabot
- [ ] Add submodule
- [ ] Database migrations
- [ ] Implement `AnalysisPipeline`
- [ ] Implement `LegislationSearchService`
- [ ] Feature flag
- [ ] Integration tests
- [ ] Deploy with flag OFF
- [ ] Enable for 10% traffic
- [ ] Enable for 100% traffic

### Week 3: Prime-Radiant-AI
- [ ] Add submodule
- [ ] Database migrations
- [ ] Implement `ConversationMemory`
- [ ] Implement `FinanceSearchService`
- [ ] Update chat endpoints
- [ ] Integration tests
- [ ] Deploy with flag OFF
- [ ] Enable for 10% traffic
- [ ] Enable for 100% traffic

### Week 4: Cleanup
- [ ] Remove old code
- [ ] Remove feature flags
- [ ] Optimize cache TTLs
- [ ] Model comparison experiments
- [ ] Update documentation
- [ ] Performance benchmarking

---

## 🎓 Learning Objectives

By the end of this implementation, you will understand:

1. **Multi-Provider LLM Integration**
   - How to use LiteLLM for provider abstraction
   - How to implement fallback chains
   - How to track costs

2. **Caching Strategies**
   - 2-tier caching (memory + database)
   - Cache invalidation and TTLs
   - Cost optimization via caching

3. **Workflow Orchestration**
   - Sequential pipelines (Research → Generate → Review)
   - Conditional branching (if review fails → regenerate)
   - State management

4. **Structured Outputs**
   - Using `instructor` for type-safe LLM responses
   - Pydantic model validation
   - Error handling

5. **Database Design**
   - Schema design for LLM tracking
   - JSONB for flexible storage
   - Performance optimization (indexes)

---

## 🤝 Getting Help

### Questions?
1. **Check the docs:** All 4 documents are comprehensive
2. **Read the code examples:** `llm-common/examples/`
3. **Run the tests:** See how things work
4. **Ask specific questions:** Reference the document and section

### Common Issues
- **"Import error for llm_common"** → Install submodule: `pip install -e packages/llm-common`
- **"API key not found"** → Set environment variables (see Migration Plan)
- **"Cache not working"** → Check Supabase connection, verify schema
- **"Tests failing"** → Check mock setup, verify API keys for integration tests

---

## 🎉 Success Criteria

You've successfully completed the implementation when:

1. ✅ All tests pass (unit + integration)
2. ✅ Both projects use `llm-common`
3. ✅ Cache hit rate ≥ 80%
4. ✅ Cost < $300/month
5. ✅ Pipeline latency P95 < 10s
6. ✅ Old code removed
7. ✅ Documentation updated

---

## 📞 Next Steps

1. **Read the PRD** to understand requirements
2. **Read the Technical Spec** to understand architecture
3. **Read the Migration Plan** to understand implementation steps
4. **Start with Week 1** (create `llm-common` package)
5. **Test frequently** (don't wait until the end)
6. **Ask questions** (better to clarify than guess)

**Good luck! 🚀**
