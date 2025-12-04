#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

# Create a unique, stamped branch to avoid non-fast-forward conflicts.
# Usage: KIND=feature KEY=QA_DOCBOT_V3 AGENT=B ./scripts/cli/branch_new.sh

KIND=${KIND:-}
KEY=${KEY:-}
AGENT=${AGENT:-}

if [ -z "$KIND" ] || [ -z "$KEY" ]; then
  echo "Usage: KIND=<feature|hotfix|messy|rescue|sync> KEY=<UPPER_SNAKE> [AGENT=A] $0" >&2
  exit 1
fi

STAMP=$(date +%s)
SUFFIX=${AGENT:+_${AGENT}}
BRANCH="${KIND}/${KEY}${SUFFIX}-${STAMP}"

echo "🌿 Creating branch: $BRANCH"
git checkout -b "$BRANCH"
echo "✅ Branch ready: $BRANCH"
