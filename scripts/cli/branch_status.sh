#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

if ! command -v gh >/dev/null 2>&1; then
  echo "⚠️  GitHub CLI (gh) not found. Install and run 'gh auth login'."
fi

CURRENT=$(git rev-parse --abbrev-ref HEAD)
DEFAULT=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null || echo "master")
TRACKING=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "(none)")

# Optional agent metadata
if [ -f .agent/.env.agent ]; then
  # shellcheck disable=SC1091
  . .agent/.env.agent
fi

echo "Current branch   : $CURRENT"
echo "Default branch   : $DEFAULT"
echo "Tracking         : $TRACKING"
if [ -n "${AGENT_ID:-}" ] || [ -n "${VM_ID:-}" ]; then
  echo "Agent/VM         : ${AGENT_ID:-unknown}/${VM_ID:-unknown}"
fi

STAMP=".command-proof/guardrails.json"
if [ -f "$STAMP" ]; then
  echo "Guardrails stamp : present ($STAMP)"
else
  echo "Guardrails stamp : missing ($STAMP)"
fi

# Next step heuristic
NEXT=""
if [[ ! "$CURRENT" =~ ^(feature|hotfix|bugfix|docs|sync|release)(-|/) ]]; then
  NEXT="Rename branch to feature/KEY (UPPER_SNAKE) or use /rescue-i"
elif [ ! -f "$STAMP" ]; then
  NEXT="Create guardrails stamp: make guardrails-stamp (or run /sync-i)"
elif [[ "$TRACKING" == "(none)" ]]; then
  NEXT="Push branch: git push -u origin $CURRENT"
else
  NEXT="Open PR to $DEFAULT, then run /merge-i"
fi

echo "Next step        : $NEXT"

# Port suggestion (if env present)
if [ -n "${PORT_OFFSET:-}" ]; then
  echo "Ports            : backend=$((8000 + PORT_OFFSET)) | frontend=$((5173 + PORT_OFFSET))"
fi

echo
echo "IMPORTANT (OpenCode): Slash commands like '/sync-i' are agent prompts — not shell/Python commands."
echo "Use the OpenCode Task input (chat) or comment: /oc run \"/sync-i --force true\" on a PR."
echo "Local helpers: 'make slash-help', 'make guardrails-stamp'."
