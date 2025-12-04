#!/usr/bin/env bash
set -euo pipefail

echo "🩺 DX Self-Heal: restoring critical developer assets"

missing=0
restore() {
  local path="$1"
  if [ ! -e "$path" ]; then
    echo "↺ Restoring $path from origin/master"
    git fetch origin >/dev/null 2>&1 || true
    git checkout origin/master -- "$path" 2>/dev/null || true
    if [ -e "$path" ]; then echo "✅ Restored $path"; else echo "⚠️  Could not restore $path"; missing=1; fi
  else
    echo "✓ Present: $path"
  fi
}

# Hooks and installer
mkdir -p .githooks
restore .githooks/pre-commit
restore .githooks/pre-push
restore .githooks/commit-msg
restore scripts/git/install_hooks.sh

# DX helper scripts
mkdir -p scripts/cli
restore scripts/cli/branch_new.sh
restore scripts/cli/pr_open.sh
restore scripts/cli/rescue_checklist.sh

# Makefile targets are versioned; just ensure file exists
restore Makefile

# Ensure hooks are executable and active
chmod +x .githooks/* 2>/dev/null || true
bash scripts/git/install_hooks.sh || true

if [ "$missing" -eq 0 ]; then
  echo "🎉 DX self-heal completed successfully"
else
  echo "⚠️  DX self-heal completed with warnings; see messages above"
fi

