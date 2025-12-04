#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

errors=0
check() {
  if [ ! -e "$1" ]; then
    echo "❌ Missing: $1"; errors=$((errors+1))
  else
    echo "✅ Present: $1"
  fi
}

echo "🔍 Verifying DX assets..."
check scripts/cli
check scripts/git/install_hooks.sh
check .githooks

if [ $errors -gt 0 ]; then
  echo
  echo "Run: make dx-restore  (or 'git fetch origin && git checkout origin/master -- scripts/cli scripts/git/install_hooks.sh .githooks')"
  exit 2
else
  echo "✅ DX assets look good"
fi
