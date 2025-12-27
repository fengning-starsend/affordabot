# Verification Policy (Solo + Agents)

Goal: keep regressions low while avoiding unnecessary `make verify-pr` cost.

## Default
- For most PRs: run `make ci-lite` locally.

## When to run `make verify-pr PR=<N>`
Run the full Railway PR environment verification when changes are likely to affect deploy/runtime wiring or core flows:
- Touches verification harness or auth behavior: `backend/scripts/verification/**`, `frontend/src/middleware.ts`, Clerk config, `Makefile` verification targets.
- Touches deployment/infra: `railway.toml`, `frontend/railway.toml`, `backend/railway.toml`, `.github/workflows/**`, `scripts/railway-*`, env wiring scripts.
- Touches cross-cutting data/DB or ingestion: migrations, `backend/db/**`, `backend/services/**` (pipeline), retrieval/pgvector, storage.
- “Large” PR: many files across multiple areas, or anything you’re not confident is low risk.

## Middle ground
- For moderate UI/backend changes: run `make verify-pr-lite` (if appropriate) + `make ci-lite`.

## Helper
- Use `scripts/cli/verify_recommend.sh` to get a recommended command for the current branch diff.

