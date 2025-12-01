# LLM Framework - Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** 2025-12-01  
**Status:** Draft for Review  
**Owner:** Engineering Team

---

## Executive Summary

This PRD defines the requirements for a unified LLM framework to be shared between `affordabot` (legislation analysis) and `prime-radiant-ai` (financial advisory chat). The framework will use **LiteLLM** for multi-provider support, **custom orchestration** for workflow management, and **Supabase** for state persistence.

### Goals
1. **Eliminate code duplication** between `affordabot` and `prime-radiant-ai`
2. **Enable model experimentation** (easy A/B testing across providers)
3. **Track model performance** (generation vs review, model comparison)
4. **Maintain simplicity** (solo developer, minimal maintenance overhead)

### Non-Goals
- Building a general-purpose LLM framework for external use
- Supporting non-OpenAI-compatible providers
- Real-time streaming UI (future consideration)

---

## Background

### Current State

#### Affordabot
- **Status:** Custom `DualModelAnalyzer` with fallback logic
- **Dependencies:** `instructor`, `openai`, custom clients
- **Workflow:** Research → Generate → Review → Refine
- **Pain Points:**
  - No model performance tracking
  - Hardcoded model priorities
  - No multi-round evaluation support

#### Prime-Radiant-AI
- **Status:** No conversation memory implementation
- **Dependencies:** Custom LLM client (8 files, ~1,000 LOC)
- **Workflow:** Stateful chat with context injection
- **Pain Points:**
  - No conversation history persistence
  - No page-specific context injection
  - Heavy custom implementation

---

## Functional Requirements

### FR-1: Multi-Provider LLM Support

**Priority:** P0 (Must Have)

**Description:** Support multiple LLM providers through a unified interface.

**Acceptance Criteria:**
- [ ] Support OpenRouter (400+ models)
- [ ] Support z.ai (GLM-4.5, GLM-4.6)
- [ ] Support direct OpenAI API (fallback)
- [ ] Support direct Anthropic API (fallback)
- [ ] Model switching via configuration (no code changes)

**Technical Notes:**
- Use LiteLLM for provider abstraction
- Environment variables for API keys (`OPENROUTER_API_KEY`, `ZAI_API_KEY`)

---

### FR-2: Web Search with Intelligent Caching

**Priority:** P0 (Must Have)

**Description:** z.ai web search with 2-tier caching to reduce costs.

**Acceptance Criteria:**
- [ ] Support z.ai web search API
- [ ] In-memory cache (TTL: 1 hour)
- [ ] Supabase persistent cache (TTL: 24 hours)
- [ ] Cache hit rate tracking
- [ ] Cost tracking per search

**Cost Savings:**
- Target: 80% cache hit rate
- Estimated savings: $450/month → $90/month (for 1,500 searches/day)

**Technical Notes:**
- Cache key: `hash(query + domains + recency)`
- Invalidation: Manual or TTL-based

---

### FR-3: Sequential Pipeline Orchestration (Affordabot)

**Priority:** P0 (Must Have)

**Description:** Orchestrate multi-step analysis pipeline with different models per step.

**Acceptance Criteria:**
- [ ] Support Research → Generate → Review workflow
- [ ] Allow different models per step (e.g., GPT-4 for generation, Claude for review)
- [ ] Log each step to database (model used, timestamp, output)
- [ ] Support conditional branching (if review fails → regenerate)
- [ ] Support multi-round evaluation (Generate v1 → Review v1 → Generate v2 → Review v2)

**Example Workflow:**
```
1. Research: z.ai web search (20-30 queries)
2. Generate: GPT-4o (structured output via instructor)
3. Review: Claude 3.5 Sonnet (critique)
4. Refine: GPT-4o (if review failed)
```

**Technical Notes:**
- Custom `AnalysisPipeline` class (~200 lines)
- No framework dependencies (LangChain, LangGraph)

---

### FR-4: Conversation Memory (Prime-Radiant-AI)

**Priority:** P0 (Must Have)

**Description:** Persist and retrieve conversation history for stateful chat.

**Acceptance Criteria:**
- [ ] Store conversation messages in Supabase
- [ ] Retrieve last N messages on session start
- [ ] Support context injection based on page navigation
- [ ] Support conversation summarization (for long histories)

**Example:**
```
User navigates to /portfolio → Inject portfolio data as context
User asks: "Should I buy AAPL?" → LLM sees portfolio + conversation history
```

**Technical Notes:**
- Custom `ConversationMemory` class (~100 lines)
- Supabase table: `conversations` (user_id, role, content, timestamp)

---

### FR-5: Model Performance Tracking

**Priority:** P1 (Should Have)

**Description:** Track and compare model performance across steps and time.

**Acceptance Criteria:**
- [ ] Log every LLM call (model, step, timestamp, cost, tokens)
- [ ] Support manual quality scoring (admin UI)
- [ ] Generate comparison reports (DeepSeek vs Kimi, Generation vs Review)
- [ ] Track cost per model per step

**Example Queries:**
```sql
-- Compare generation models
SELECT generate_model, AVG(quality_score), AVG(cost_usd)
FROM pipeline_runs
WHERE timestamp >= '2024-11-30'
GROUP BY generate_model;

-- Compare review models
SELECT review_model, AVG(review_confidence), COUNT(*)
FROM pipeline_runs
WHERE timestamp >= '2024-12-01'
GROUP BY review_model;
```

**Technical Notes:**
- Supabase table: `pipeline_runs` (see DB schema section)

---

### FR-6: Structured Outputs

**Priority:** P0 (Must Have)

**Description:** Type-safe LLM responses using Pydantic models.

**Acceptance Criteria:**
- [ ] Support Pydantic models as `response_model`
- [ ] Automatic validation and retry on schema mismatch
- [ ] Support nested models (e.g., `List[Impact]`)

**Example:**
```python
class BillAnalysis(BaseModel):
    summary: str
    impacts: List[Impact]
    confidence: float

analysis = await client.chat(
    messages=[...],
    response_model=BillAnalysis
)
# analysis is a validated BillAnalysis instance
```

**Technical Notes:**
- Use `instructor` library (already in affordabot)
- Works with LiteLLM via OpenAI-compatible interface

---

### FR-7: Cost Management

**Priority:** P1 (Should Have)

**Description:** Track and enforce budget limits.

**Acceptance Criteria:**
- [ ] Track cost per request (LLM + web search)
- [ ] Enforce daily/monthly budget limits
- [ ] Alert when approaching budget threshold (80%)
- [ ] Cost breakdown by model, step, and date

**Example:**
```python
config = LLMConfig(
    daily_budget_usd=10.0,
    alert_threshold=0.8
)
# Raises BudgetExceededError when limit reached
```

**Technical Notes:**
- LiteLLM provides `completion_cost()` function
- Store costs in Supabase for aggregation

---

### FR-8: Retry and Fallback Logic

**Priority:** P0 (Must Have)

**Description:** Automatic retries and fallback to alternative models.

**Acceptance Criteria:**
- [ ] Retry failed requests (max 3 attempts)
- [ ] Exponential backoff (1s, 2s, 4s)
- [ ] Fallback to alternative model on persistent failure
- [ ] Log all retry attempts

**Example:**
```python
models = [
    "openrouter/anthropic/claude-3.5-sonnet",  # Primary
    "openrouter/openai/gpt-4o",                # Fallback 1
    "z-ai/glm-4.5"                             # Fallback 2
]
# Tries each model in sequence until success
```

**Technical Notes:**
- LiteLLM has built-in retry logic
- Custom fallback chain for model selection

---

## Non-Functional Requirements

### NFR-1: Performance
- **Latency:** P95 < 10s for full pipeline (Research → Generate → Review)
- **Throughput:** Support 50 bills/day (affordabot)
- **Cache Hit Rate:** ≥ 80% for web search

### NFR-2: Reliability
- **Uptime:** 99.5% (excluding provider outages)
- **Error Rate:** < 1% (excluding rate limits)
- **Data Loss:** Zero tolerance (all LLM calls logged)

### NFR-3: Maintainability
- **Code Complexity:** < 1,000 LOC for shared framework
- **Dependencies:** < 10 direct dependencies
- **Documentation:** 100% coverage for public APIs

### NFR-4: Cost
- **Web Search:** < $100/month (with caching)
- **LLM Calls:** < $200/month (using free tier + paid models)
- **Total:** < $300/month

---

## User Stories

### US-1: Affordabot Admin - Model Experimentation
**As an** admin,  
**I want to** easily switch between models for generation and review,  
**So that** I can find the best model combination for legislation analysis.

**Acceptance Criteria:**
- Admin UI to configure model priorities
- No code deployment required to change models
- A/B test results visible in dashboard

---

### US-2: Affordabot Admin - Performance Tracking
**As an** admin,  
**I want to** compare model performance over time,  
**So that** I can optimize for quality and cost.

**Acceptance Criteria:**
- View quality scores by model
- View cost per model per step
- Export data for analysis

---

### US-3: Prime-Radiant-AI User - Conversation Continuity
**As a** user,  
**I want to** resume my conversation from where I left off,  
**So that** I don't have to re-explain my financial situation.

**Acceptance Criteria:**
- Conversation history loads on login
- Context is preserved across sessions
- Summaries for long conversations

---

### US-4: Prime-Radiant-AI User - Context-Aware Responses
**As a** user,  
**I want to** get responses tailored to my current page (e.g., portfolio, tax planning),  
**So that** the advice is relevant to my current task.

**Acceptance Criteria:**
- Portfolio page → LLM sees portfolio data
- Tax page → LLM sees tax bracket info
- Seamless context switching

---

## Success Metrics

### Primary Metrics
1. **Code Reduction:** 50% reduction in LLM-related code (vs. current custom implementations)
2. **Cost Savings:** 60% reduction in web search costs (via caching)
3. **Model Experimentation:** 5+ model combinations tested per month

### Secondary Metrics
1. **Cache Hit Rate:** ≥ 80%
2. **Pipeline Latency:** P95 < 10s
3. **Error Rate:** < 1%

---

## Out of Scope (Future Considerations)

1. **Real-time Streaming:** Streaming LLM responses to UI (future)
2. **Multi-User Collaboration:** Shared conversations (prime-radiant-ai)
3. **Custom Model Fine-Tuning:** Training custom models
4. **On-Premise Deployment:** Self-hosted LLMs (e.g., Llama)
5. **Advanced Observability:** Distributed tracing, APM integration

---

## Appendix

### Glossary
- **LiteLLM:** Open-source library for unified LLM API access
- **Instructor:** Library for structured LLM outputs (Pydantic)
- **Pipeline:** Sequential workflow (Research → Generate → Review)
- **Fallback:** Alternative model used when primary fails

### References
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Instructor Documentation](https://python.useinstructor.com/)
- [z.ai Web Search API](https://docs.z.ai/guides/tools/web-search)
