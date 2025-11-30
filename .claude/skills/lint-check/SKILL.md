---
name: lint-check
description: |
  Run quick linting checks on changed files. MUST BE USED when user wants to check code quality.
  Fast validation (<5s) following V3 trust-environments philosophy.
  Use when user says "lint my code", "check formatting", or "run linters",
  or when user mentions uncommitted changes, pre-commit state, formatting issues,
  code quality, style checks, validation, prettier, eslint, pylint, or ruff.
tags: [workflow, quality, linting, validation]
allowed-tools:
  - Bash(git:*)
  - Bash(eslint:*)
  - Bash(prettier:*)
  - Bash(pylint:*)
  - Bash(ruff:*)
  - Read
---

# Lint Check

Quick linting validation (<5 seconds).

## Purpose

Run fast linting checks on changed files before commits.

**Philosophy:** Quick checks only (<5s) + Trust CI for comprehensive validation

## When to Use This Skill

**Trigger phrases:**
- "lint my code"
- "check formatting"
- "run linters"
- "check code quality"

**Use when:**
- Before committing changes
- Quick validation during development
- Checking specific files

## Workflow

### 1. Detect Changed Files

```bash
# Get staged and unstaged changes
git diff --name-only HEAD
git diff --name-only --cached
```

**File categories:**
- Frontend: `*.ts`, `*.tsx`, `*.js`, `*.jsx`
- Backend: `*.py`
- Config: `*.json`, `*.yaml`, `*.yml`

### 2. Run Linters by File Type

**Frontend (TypeScript/JavaScript):**
```bash
# ESLint for code quality
npx eslint --max-warnings 0 <files>

# Prettier for formatting
npx prettier --check <files>
```

**Backend (Python):**
```bash
# Ruff for fast linting (replaces pylint/flake8/black)
ruff check <files>

# Type checking (if mypy available)
mypy <files> 2>/dev/null || true
```

**Config files:**
```bash
# JSON validation
jq empty <file.json>

# YAML validation
yamllint <file.yaml> 2>/dev/null || true
```

### 3. Report Results

**Success:**
```
✅ Linting passed!
   Checked: 12 files
   - 8 TypeScript files
   - 3 Python files
   - 1 JSON file

   No issues found.
```

**Failure:**
```
❌ Linting failed!
   Checked: 12 files
   Found: 5 issues

   frontend/src/App.tsx:
     - Line 23: Missing semicolon (eslint)
     - Line 45: Unused variable 'data' (eslint)

   backend/api/routes.py:
     - Line 12: Line too long (89 > 88 characters) (ruff)

   Fix these issues and run again.
```

### 4. Exit Fast

**No auto-fixing:**
- Report issues only
- User fixes manually
- Trust CI for comprehensive checks

## Integration Points

### With sync-feature-branch

**Optional pre-commit check:**
```bash
# In sync-feature-branch skill
if user wants quick lint:
  lint-check skill
  if fails:
    echo "Fix linting issues before committing"
    exit 1
```

### With Git

**Staged files only:**
```bash
# Only lint what's about to be committed
git diff --cached --name-only | xargs <linter>
```

## Linter Configuration

### Frontend (package.json required)

**ESLint:**
```bash
npx eslint --ext .ts,.tsx,.js,.jsx <files>
```

**Prettier:**
```bash
npx prettier --check <files>
```

### Backend (ruff preferred)

**Ruff (fast):**
```bash
ruff check <files>
```

**Fallback to pylint:**
```bash
pylint <files>
```

## Best Practices

### Do

✅ Run on changed files only (fast)
✅ Report issues clearly
✅ Exit fast (<5s target)
✅ Trust CI for full validation
✅ Use project's linter config (.eslintrc, ruff.toml)

### Don't

❌ Auto-fix issues (user fixes manually)
❌ Run on entire codebase (too slow)
❌ Block commits (advisory only)
❌ Run comprehensive type checking (CI does this)
❌ Ignore project config

## What This Skill Does

✅ Detects changed files (git diff)
✅ Runs appropriate linters (eslint, ruff, prettier)
✅ Reports issues clearly
✅ Exits fast (<5s)
✅ Respects project linter config

## What This Skill DOESN'T Do

❌ Auto-fix issues
❌ Run on entire codebase
❌ Block commits
❌ Run comprehensive type checking
❌ Replace CI validation

## Examples

### Example 1: Clean Code

```
User: "lint my code"

lint-check:

1. Detect files:
   - frontend/src/App.tsx
   - frontend/src/utils.ts
   - backend/api/routes.py

2. Run linters:
   - ESLint: ✓ pass (2 files)
   - Ruff: ✓ pass (1 file)

3. Report:
   ✅ Linting passed!
   Checked: 3 files
   No issues found.
```

### Example 2: Issues Found

```
User: "check formatting"

lint-check:

1. Detect files:
   - frontend/src/Dashboard.tsx
   - backend/services/auth.py

2. Run linters:
   - ESLint: ✗ fail (1 issue)
   - Ruff: ✗ fail (2 issues)

3. Report:
   ❌ Linting failed!

   frontend/src/Dashboard.tsx:
     Line 34: 'data' is assigned but never used (no-unused-vars)

   backend/services/auth.py:
     Line 12: Line too long (92 > 88 characters)
     Line 45: Undefined name 'UserModel'

   Fix these issues and run again.
```

### Example 3: No Changed Files

```
User: "lint my code"

lint-check:

1. Detect files:
   (no changed files)

2. Report:
   ℹ️  No changed files to lint.

   Stage changes first: git add <files>
```

## Troubleshooting

### Linter Not Found

**Symptom:** `eslint: command not found`

**Fix:**
```bash
# Install linters
cd frontend && npm install
cd backend && pip install ruff
```

### Config Missing

**Symptom:** Linter uses default config instead of project config

**Check:**
```bash
ls -la .eslintrc* ruff.toml .prettierrc*
```

**Fix:** Use project config if present

### Too Slow

**Symptom:** Takes >5 seconds

**Fix:** Reduce scope to staged files only
```bash
git diff --cached --name-only | xargs <linter>
```

## Related Skills

- **sync-feature-branch**: May call lint-check before commit
- **fix-pr-feedback**: May suggest running linters for CI failures

## Resources

**Linter docs:**
- ESLint: https://eslint.org/docs/latest/
- Prettier: https://prettier.io/docs/
- Ruff: https://docs.astral.sh/ruff/
- Pylint: https://pylint.readthedocs.io/

**Project config:**
- `.eslintrc.json` - ESLint rules
- `.prettierrc` - Prettier config
- `ruff.toml` - Ruff config
- `pyproject.toml` - Python tools config

---

**Last Updated:** 2025-01-12
**Skill Type:** Workflow
**Average Duration:** <5 seconds
**Related Docs:**
- AGENTS.md (V3 trust environments)
- .claude/skills/sync-feature-branch/SKILL.md
