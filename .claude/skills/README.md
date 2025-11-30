# Claude Code Skills

This directory contains context skills for efficient codebase navigation and epic tracking.

## Skill Types

### Static Skills (14)

Long-lived reference skills for codebase areas. Manually maintained, weekly drift detection.

**Integration Points**:
- `context-plaid-integration` - Plaid SDK for brokerage connectivity
- `context-eodhd-integration` - EODHD financial data provider
- `context-clerk-integration` - Clerk authentication & RLS
- `context-snaptrade-integration` - SnapTrade brokerage provider

**Data Layer**:
- `context-symbol-resolution` - Symbol normalization (Plaid ↔ EODHD)
- `context-database-schema` - Supabase schema, 86+ migrations
- `context-api-contracts` - Frontend ↔ Backend API contracts

**Infrastructure**:
- `context-testing-infrastructure` - Tiered testing strategy
- `context-infrastructure` - Railway deployment, CI/CD
- `context-dx-meta` - DX V3 system itself

**Features**:
- `context-analytics` - Portfolio analytics
- `context-portfolio` - Portfolio management
- `context-brokerage` - Brokerage connections
- `context-ui-design` - UI theme & patterns

### Dynamic Epic Context (N)

Ephemeral skills for active epics. Auto-created per epic, auto-updated on push, archived when done.

**Format**: `context-epic-<beads-id>` (e.g., `context-epic-bd-7vu`)

**Lifecycle**:
1. Create: `scripts/epic-context-create.sh bd-7vu`
2. Auto-update: GitHub Action regenerates work log on push
3. Resume: Invoke skill to see complete work history
4. Archive: `scripts/epic-context-archive.sh bd-7vu` → `docs/epics/bd-7vu/`

## Usage

### Invoking Skills

Skills are invoked by name during Claude Code sessions:

```
User: "Add Plaid webhook handler"
Agent: Invoke context-plaid-integration
       → See backend/brokers/plaid_adapter.py, patterns, tests
       → Implement following patterns
```

### Creating Dynamic Epic Context

```bash
# Auto-created by issue-first skill, or manually:
scripts/epic-context-create.sh bd-7vu

# Add external docs to epic context (via docs-create skill):
docs-create bd-7vu https://firebase.google.com/docs/cloud-messaging
```

### Refreshing Static Skills

```bash
# Manual refresh (when drift detected)
scripts/skill-refresh.sh context-plaid-integration

# Weekly drift check runs automatically (GitHub Action)
```

## Documentation

- **Full System Guide**: `docs/DX_CONTEXT_SKILLS.md`
- **Quick Reference**: `AGENTS.md` → Core Tools → Context Skills
- **Internal Docs**: `docs/integrations/`, `docs/testing/`, `docs/deployment/`

## Auto-Update System

**Dynamic Epic Context**: GitHub Action (`.github/workflows/epic-context-update.yml`)
- Triggers: Push to `feature-bd-*` or `claude/**` branches
- Regenerates work logs from git history
- Commits back with `[skip ci]`
- Non-blocking (30-60s async)

**Static Skill Drift Detection**: GitHub Action (`.github/workflows/skill-drift-check.yml`)
- Triggers: Weekly on Sunday midnight UTC
- Detects file listing drift
- Creates GitHub issue if drift found

## Scripts

- `scripts/epic-context-create.sh <epic-id>` - Create epic context
- `scripts/epic-context-regenerate.sh <epic-id>` - Regenerate work log
- `scripts/epic-context-archive.sh <epic-id>` - Archive epic context
- `scripts/skill-refresh.sh <skill-name>` - Refresh static skill

## Archived Epics

Completed epics are archived to `docs/epics/<beads-id>/`:
- `README.md` - Epic overview
- `WORK_LOG.md` - Complete commit history
- `EXTERNAL_DOCS.md` - Cached external docs
- `NOTES.md` - Manual notes, blockers, discoveries

---

**Created**: 2025-01-17
**System**: DX V3 Context Skills
**Documentation**: docs/DX_CONTEXT_SKILLS.md
