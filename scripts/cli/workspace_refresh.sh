#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

# Refresh the current workspace to reduce drift and missing helpers.
# - Verifies gh auth
# - Ensures on a git repo, fetches origin, and updates local master (ff-only)
# - Warns if uncommitted changes exist
# - Prints a concise next-step guide

if ! command -v git >/dev/null 2>&1; then
  echo "git not found" >&2; exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "⚠️  GitHub CLI (gh) not found. Install and run 'gh auth login'." >&2
else
  gh auth status || true
fi

echo "🔄 Fetching origin..."
git fetch origin --prune || true

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null || echo master)

CURR=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURR" = "$DEFAULT_BRANCH" ]; then
  echo "📦 On $DEFAULT_BRANCH; updating (ff-only)..."
  git pull --ff-only || echo "⚠️  Fast-forward failed; you may need to resolve manually."
else
  echo "📦 Not on $DEFAULT_BRANCH; ensuring $DEFAULT_BRANCH is up-to-date (ff-only)..."
  git rev-parse --verify "$DEFAULT_BRANCH" >/dev/null 2>&1 || git branch "$DEFAULT_BRANCH" origin/"$DEFAULT_BRANCH" || true
  git checkout "$DEFAULT_BRANCH" >/dev/null 2>&1 || true
  git pull --ff-only || echo "⚠️  Fast-forward failed; you may need to resolve manually."
  git checkout - >/dev/null 2>&1 || true
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  Uncommitted changes detected. Consider:"
  echo "    git add -A && git commit -m 'WIP'  (or)  git stash"
else
  echo "✅ Workspace clean"
fi

echo
echo "Next steps (OpenCode):"
echo "- Slash commands are agent prompts — not shell/Python."
echo "- Use Task input (chat): /sync-i --force true"
echo "- Helpers: make slash-help | make branch-status | make guardrails-stamp"
