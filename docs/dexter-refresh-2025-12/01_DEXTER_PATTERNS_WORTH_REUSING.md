# Dexter Patterns Worth Reusing in Affordabot (2025-12 Snapshot)

This is a “what Dexter actually does” inventory, focused on patterns that transfer cleanly to policy analysis.

## 1) Evidence plumbing via tool results

Dexter’s most reusable improvement is its invariant:
- every tool can return `{ data, sourceUrls }`
- the agent runtime preserves those sources through storage + selection + synthesis
- the final answer is prompt-contractually required to include a `Sources:` section when tool data exists

Why this matters for Affordabot:
- we already require evidence (`ImpactEvidence`) but we don’t currently have a single “provenance envelope” that every retrieval tool uses
- a unified evidence envelope makes review + validation far stronger

## 2) Persist tool outputs, select contexts at answer time

Dexter saves tool outputs to disk and uses a context-selection step to decide what to include later.

Affordabot fit:
- research artifacts (web search results, scrapes, retrieved chunks) can be large
- we can store the raw artifacts and only pass selected evidence into:
  - generation
  - review
  - refinement

## 3) Planning with real tool schemas

Dexter injects tool names + parameter schemas into the planning prompt.

Affordabot fit:
- it enables dynamic “find more sources / read URLs / retrieve prior analyses” planning
- it reduces “LLM makes up a tool” errors because the plan is grounded in a known registry

## 4) What to treat as inspiration, not a drop-in

Dexter 2025-12 does not strongly enforce:
- per-claim evidence binding
- citation validation (ensuring cited URLs were actually retrieved)

Affordabot should keep its stricter posture and add programmatic checks, using Dexter’s provenance plumbing as the backbone.

