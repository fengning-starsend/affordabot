#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

# Guarded PR open helper: refuse to open PR if workspace is dirty or off-scope changes present.
# Usage: ./scripts/cli/pr_open.sh --base master --title "..." --body "..."
#        or provide env vars: BASE, TITLE, BODY, optional HEAD

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️  Uncommitted changes detected. Commit or stash before opening a PR." >&2
  exit 2
fi

# Detect off-scope changes staged for commit (none here since we guard cleanliness),
# but also detect last commit content if needed; for simplicity, we just warn when
# scenario branches include .github/workflows edits (common accidental noise).

CHANGES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || true)
if echo "$CHANGES" | grep -E '^\.github/workflows/' >/dev/null 2>&1; then
  echo "⚠️  Recent commit includes workflow edits (.github/workflows)." >&2
  echo "   For scenario branches, exclude these or commit them on a dedicated infra branch." >&2
fi

echo "💡 Tip: If base is wrong later, comment on PR: /oc retarget master"

if [ "$#" -eq 0 ]; then
  BASE=${BASE:-master}
  TITLE=${TITLE:-}
  BODY=${BODY:-}
  HEAD=${HEAD:-}
  if [ -z "$TITLE" ] || [ -z "$BODY" ]; then
    echo "must provide --title/--body or set TITLE and BODY env vars" >&2
    exit 2
  fi
  ARGS=(--base "$BASE" --title "$TITLE" --body "$BODY")
  if [ -n "$HEAD" ]; then
    ARGS+=(--head "$HEAD")
  fi
  echo "Now running: gh pr create ${ARGS[*]}"
  gh pr create "${ARGS[@]}"
else
  echo "Now running: gh pr create $*"
  gh pr create "$@"
fi
