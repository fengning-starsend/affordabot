# Epic Plan: Optional Dexter-Inspired Context Enhancements (Affordabot)

**Epic ID:** `affordabot-dwe`  
**Repo:** `~/affordabot`  
**Priority:** P3  
**Title:** `DEXTER_OPTIONAL_AGENT_CONTEXT_ENHANCEMENTS`

This epic is a **post-MVP** follow-on to `affordabot-1mz` and focuses on improving quality/cost/UX once evidence+citation correctness is in place.

Primary epic (MVP): `affordabot-1mz`  
MVP plan: `docs/bd-affordabot-1mz/EPIC_PLAN.md`

## Scope

### 1) Conversation memory + relevance selection
- Store short summaries for related runs (research/generate/review/refine).
- For a new run (“refine this”, “compare runs”), select only relevant prior summaries/chunks.

### 2) Deterministic context pointer store + dedupe
- Stable IDs for search/read/retrieve results keyed by args (hash).
- Reuse artifacts across retries and across similar runs (with TTL/versioning).
- Complements `raw_scrapes` / `document_chunks` storage.

### 3) Tool output summarization layer
- Use summaries for LLM context; keep raw artifacts for audit.
- Useful for large municipal docs and repeated retrieval passes.

### 4) Available Sources inventory vs Used citations
- Always provide “Available Sources” with IDs/labels.
- Require outputs to cite only used sources; validator enforces `used ⊆ available`.

### 5) Tool schema injection into planning (when applicable)
- If/when Affordabot formalizes tools (search/read/retrieve/store) into a registry, inject schemas into planning prompts to reduce made-up calls.

## Non-goals
- Does not replace the core evidence envelope + citation validator work (handled in `affordabot-1mz`).
- Does not mandate a new UI; focuses on agent/data contracts.

## Acceptance Criteria

1) Related runs can include selected relevant prior context, not full history.  
2) Research artifacts are cached/deduped via stable keys.  
3) Prompts use summaries; raw artifacts remain available for audit.  
4) Citations are a subset of Available Sources, enforced by validation.  
5) Planning prompts can be grounded by tool schemas when applicable.  

