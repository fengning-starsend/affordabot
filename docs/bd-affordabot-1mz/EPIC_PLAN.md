# Epic Plan: Dexter Refresh → Evidence-First Policy Pipeline

**Epic ID:** `affordabot-1mz`  
**Repo:** `~/affordabot`  
**Title:** `DEXTER_REFRESH_2025_12_EVIDENCE_FIRST_POLICY_PIPELINE`

## Context

Dexter’s 2025-12 snapshot introduced a clean provenance pattern:
- tools return `{ data, sourceUrls }`
- sources survive persistence + context selection + synthesis
- answers can be required to include a `Sources:` section when tool data was used

Affordabot already aims for evidence-first outputs (see `backend/schemas/analysis.py`), but enforcement is inconsistent across pipelines. This epic unifies evidence plumbing and adds programmatic citation validation.

Primary references:
- `docs/dexter-refresh-2025-12/01_DEXTER_PATTERNS_WORTH_REUSING.md`
- `docs/dexter-refresh-2025-12/02_AFFORDABOT_AGENTIC_FLOW_UPGRADES.md`

## Scope (What “Done” Looks Like)

### 1) Unified evidence envelope
- All research/retrieval tools return a shared `ToolResult`/`EvidenceBundle` shape including structured sources.
- Raw artifacts (docs, chunks, scrapes) are persisted separately from prompts.

### 2) Claim-linked evidence
- Analysis outputs bind evidence at the impact level (and ideally per claim), with excerpts/snippets.

### 3) Citation validation
- Validator blocks persistence of analyses containing:
  - hallucinated URLs
  - missing evidence for impacts
  - evidence URLs that were never retrieved

## Work Breakdown (Suggested Child Issues)

1. Spec: EvidenceItem model + ToolResult envelope (shared across pipeline)
2. Impl: Wrap research tools to emit evidence envelope
3. Impl: Evidence store / context pointers (phase boundaries)
4. Impl: Citation validator (must exist in collected sources)
5. Impl: Review/refine hooks to request more evidence when missing
6. UI/DB: Persist + render evidence for impacts in admin/user views
7. Tests: Unit + integration tests for citation correctness

## Acceptance Criteria (from Epic)

1) All retrieval/research tools return a unified evidence/provenance envelope.  
2) Generation outputs bind evidence at the impact level with excerpts (no bare source lists).  
3) Review/refine steps can detect missing/invalid citations and trigger targeted research.  
4) A validator blocks persistence of analyses with hallucinated URLs or missing evidence.  
5) Evidence is stored in a way that the UI can render and admins can audit.  

## Optional enhancements (Dexter-inspired, P3 follow-on)

These are valuable but not required for the core evidence/citation correctness epic above. Tracking epic: `affordabot-dwe` (plan: `docs/bd-affordabot-dwe/EPIC_PLAN.md`).

1. **Conversation memory + relevance selection**
   - Summarize prior analysis/review turns and select only relevant context per new run.
   - Useful for iterative admin workflows (“refine this analysis”, “compare to prior run”).

2. **Deterministic context pointer store + dedupe**
   - Stable IDs for search/read/retrieve results keyed by args (hash) so repeated runs can reuse artifacts.
   - Complements the existing `raw_scrapes`/`document_chunks` storage model.

3. **Tool output summarization layer**
   - Store full retrieved docs, but provide concise summaries for the LLM context window.
   - Improves cost and reduces prompt length during multi-source research.

4. **“Available sources” inventory vs “Used sources” citations**
   - Always pass an “Available sources” list into generate/review prompts.
   - Require outputs to cite only sources actually used; validator enforces subset membership.

5. **Tool schema injection into planning**
   - If/when Affordabot adds a tool registry for research tools, inject schemas into planning prompts to reduce made-up tool calls.
