# Affordabot Agentic Flow Upgrades (Dexter-Inspired, Evidence-First)

Affordabot already has strong intent around evidence (`ImpactEvidence`) and a research → generate → review loop (`DualModelAnalyzer`). This proposal focuses on making evidence first-class and enforceable end-to-end.

## 1) Current gaps (observed)

### 1.1 Inconsistent “sources” representations
- `backend/schemas/analysis.py` models per-impact evidence (good), but not all pipelines populate it consistently.
- `backend/services/llm/orchestrator.py` defines a separate `BillAnalysis` with `sources: List[str]` (weak / mismatched).
- `services/research/zai.py` returns `ResearchPackage.sources` with URL/title/snippet, but generation currently surfaces mostly URL lists.

### 1.2 Review is “prompt-based” for citations
The review prompt says “ensure all impacts are supported by evidence”, but there is little programmatic enforcement ensuring:
- every impact has evidence items
- every evidence URL exists in collected sources

## 2) Dexter-inspired changes (practical + high leverage)

### 2.1 Introduce a unified `ToolResult`/`EvidenceBundle` envelope
All research/retrieval tools should return a shared shape:
- `data`: tool payload
- `sources`: structured evidence items (URLs + metadata + optional excerpts)

This includes:
- z.ai search results
- web reader outputs (full text + extracted quotes)
- retrieval outputs (chunk ids + snippets + original document URLs)

### 2.2 Add a “citation validator” step before persistence
Before storing an analysis:
- verify every cited URL in output exists in collected `sources`
- verify every impact has ≥1 evidence item
- optionally require at least one “official” source for certain impact categories (e.g., fiscal impacts → state/county budget docs)

### 2.3 Store claim-level evidence
Evolve output to bind evidence at the claim level:
- keep `Impacts[i].evidence[]` as the canonical list
- encourage `excerpt`/quote fields to make audits human-checkable

## 3) How this aligns with Dexter (without copying blindly)

Reuse:
- provenance plumbing (`sources` carried through tool results and contexts)
- context selection to avoid token blowups

Strengthen beyond Dexter:
- programmatic citation validation
- claim-level evidence binding

## Tracking

**Beads Epic (Affordabot):** `affordabot-1mz`  
Epic plan: `docs/bd-affordabot-1mz/EPIC_PLAN.md`

