# Beads Workflow for llm-common

## TL;DR

**llm-common uses CLI-only Beads workflow:**

1. **No .beads/ directory** - This is a secondary repo, work tracking happens in primary repos (Affordabot, Prime Radiant)
2. **Use bd CLI only** - No MCP tools needed
3. **Install hooks**: Run `bd hooks install` in your primary repo
4. **Sync at session end**: Run `bd sync` when done with your work session

## Secondary Repository Pattern

llm-common is a **secondary repository** in the multi-repo agent pattern:

```
Primary Repos (with .beads/):        Secondary Repos (no .beads/):
├── affordabot                       ├── llm-common
│   ├── .beads/                      │   ├── (no .beads/)
│   └── packages/llm-common/  ──────►│   └── (driven by Feature-Keys)
└── prime-radiant
    ├── .beads/
    └── backend/llm-common/  ────────────►
```

**Work tracking** happens in primary repos using their Feature-Keys (bd-svse, affordabot-rdx, etc.)

## CLI-Only Workflow

### 1. Setup (One-Time)

In your **primary repository** (Affordabot or Prime Radiant):

```bash
# Install bd CLI
npm install -g @beads/cli

# Initialize Beads (if not already done)
cd ~/affordabot  # or ~/prime-radiant-ai
bd init

# Install git hooks
bd hooks install
```

### 2. Daily Workflow

When working on llm-common changes:

```bash
# In your primary repo, reference the Feature-Key
cd ~/affordabot

# View ready issues
bd ready

# Start work on an issue
bd update bd-svse-123 --status in_progress

# Make changes in llm-common submodule
cd packages/llm-common
git checkout -b feature-bd-svse-123-description
# ... make changes ...
git commit -m "feat: add feature" -m "Feature-Key: bd-svse-123"

# Back to primary repo
cd ~/affordabot

# Sync when done with session
bd sync
```

### 3. No MCP Tools

llm-common uses **CLI-only** Beads:
- ❌ No MCP server
- ❌ No MCP tools
- ✅ Use `bd` CLI commands
- ✅ Feature-Keys in commit trailers

### 4. Commit Trailers

All commits in llm-common must include Feature-Key from the primary repo:

```
Feature-Key: bd-svse
Agent: claude-code
Role: backend-engineer
```

See `AGENTS.md` for full commit format details.

## Common bd Commands

### Viewing Issues
```bash
bd list                    # List all issues
bd list --status open      # Filter by status
bd ready                   # Show ready-to-work issues
bd show bd-svse-123       # Show specific issue
```

### Managing Work
```bash
bd update bd-svse-123 --status in_progress    # Claim work
bd update bd-svse-123 --status closed         # Complete work
bd comments bd-svse-123                       # View/add comments
```

### Synchronization
```bash
bd sync                    # Sync with git remote
bd sync --dry-run         # Preview sync changes
bd stats                  # Show project statistics
```

### Dependencies
```bash
bd dep add bd-svse-123 bd-svse-124   # Add dependency
bd dep list bd-svse-123              # View dependencies
bd blocked                           # Show blocked issues
```

## Full CLI Reference

For complete command documentation, see:
https://github.com/steveyegge/beads/blob/main/docs/CLI_REFERENCE.md

## Integration with Git Submodules

llm-common is typically used as a git submodule:

### In Primary Repo (Affordabot Example)

```bash
# Add llm-common submodule
cd ~/affordabot
git submodule add git@github.com:stars-end/llm-common.git packages/llm-common

# Pin to stable version
cd packages/llm-common
git checkout v0.3.0

# Make changes on feature branch
git checkout -b feature-bd-svse-123-new-backend
# ... make changes ...
git commit -m "feat: add new backend" -m "Feature-Key: bd-svse-123"
git push -u origin feature-bd-svse-123-new-backend

# Back to primary repo
cd ~/affordabot

# Commit submodule update
git add packages/llm-common
git commit -m "feat: update llm-common with new backend" -m "Feature-Key: bd-svse-123"

# Sync Beads
bd sync
```

## Workflow Examples

### Example 1: Bug Fix in llm-common

```bash
# In primary repo (Affordabot)
cd ~/affordabot
bd update bd-svse-456 --status in_progress

# Fix bug in submodule
cd packages/llm-common
git checkout -b feature-bd-svse-456-fix-pgvector-error
# ... fix bug, add test ...
git commit -m "fix: handle null embeddings in pgvector" \
  -m "Feature-Key: bd-svse-456\nAgent: claude-code\nRole: backend-engineer"
git push -u origin feature-bd-svse-456-fix-pgvector-error

# Open PR in llm-common repo
gh pr create --title "[bd-svse-456] Fix null embedding handling"

# Back to primary repo
cd ~/affordabot

# Note the fix in Beads
bd comments bd-svse-456 "Fixed in llm-common PR #4"

# Sync
bd sync
```

### Example 2: New Feature Driven by Affordabot

```bash
# In Affordabot, create epic for new feature
cd ~/affordabot
bd create "Add document chunking helper to llm-common" \
  --type epic \
  --priority 2

# Create subtask
bd create "Implement Document dataclass" \
  --type task \
  --priority 2

# Work on it
bd update bd-svse-789 --status in_progress

# Implement in llm-common
cd packages/llm-common
git checkout -b feature-bd-svse-789-document-helper
# ... implement ...
git commit -m "feat: add Document dataclass for chunking" \
  -m "Feature-Key: bd-svse-789"

# Complete and sync
cd ~/affordabot
bd update bd-svse-789 --status closed --reason "Implemented and tested"
bd sync
```

## Status Tracking

Issue statuses in primary repo:
- **open**: Ready to work, no dependencies blocking
- **in_progress**: Currently being worked on
- **blocked**: Waiting on dependencies
- **closed**: Completed

llm-common work is tracked in primary repo issues, not in llm-common itself.

## Git Hooks

The `bd hooks install` command sets up:
- **pre-commit**: Validates commit trailers (Feature-Key, Agent, Role)
- **commit-msg**: Ensures proper format
- **post-commit**: Updates local Beads state

These hooks run in your **primary repository**, not in llm-common.

## Troubleshooting

### "Feature-Key not found"
Make sure you're using a Feature-Key that exists in your primary repo:
```bash
cd ~/affordabot  # or prime-radiant-ai
bd list | grep bd-svse
```

### "bd command not found"
Install the Beads CLI:
```bash
npm install -g @beads/cli
```

### "No .beads/ directory"
This is expected! llm-common is a secondary repo. Work from your primary repo (Affordabot or Prime Radiant).

### Submodule not updating
```bash
# In primary repo
cd ~/affordabot
git submodule update --remote packages/llm-common
```

## Best Practices

1. **Always work from primary repo** - Don't try to run `bd` commands in llm-common
2. **Use Feature-Keys consistently** - Same key across primary repo issue and llm-common commits
3. **Sync regularly** - Run `bd sync` at end of each work session
4. **Pin to releases** - Use tagged versions (v0.3.0) in production submodules
5. **Test before syncing** - Run `poetry run pytest` in llm-common before pushing

## Development Status

llm-common is currently in a **validation phase**:
- ⏸️ New features paused until downstream integration
- 🐛 Bug fixes welcome
- 📚 Documentation improvements encouraged
- 🎯 Waiting for usage metrics from Affordabot and Prime Radiant

See `DEVELOPMENT_STATUS.md` for full details.

## Resources

- **Beads CLI Reference**: https://github.com/steveyegge/beads/blob/main/docs/CLI_REFERENCE.md
- **Multi-Repo Agents**: See primary repo documentation
- **Agent Guidelines**: `AGENTS.md` in this repo
- **Development Status**: `DEVELOPMENT_STATUS.md`

---

**Remember**: Use `bd` CLI in your primary repo, not in llm-common. Commit trailers must include Feature-Key from primary repo issues.
