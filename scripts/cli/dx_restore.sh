#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

echo "🔄 Restoring critical DX assets from origin/master..."
git fetch origin --prune
git checkout origin/master -- scripts/cli scripts/git/install_hooks.sh .githooks 2>/dev/null || true

echo "✅ Restore attempted. Verify with: make dx-verify"
