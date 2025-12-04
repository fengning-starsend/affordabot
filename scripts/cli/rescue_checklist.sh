#!/usr/bin/env bash
set -euo pipefail

# Require Railway shell for dev commands
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
"${REPO_ROOT}/scripts/ensure-railway-env.sh"

# Print a precise, filled-out rescue checklist for the current repo.
# Optional: PR=<number> to reference original PR.

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null || echo master)
PR=${PR:-}

cat <<EOF
Rescue Checklist (manual, fast) — OpenCode

1) From $DEFAULT_BRANCH, create a stamped rescue branch:
   STAMP=\$(date +%s)
   git checkout $DEFAULT_BRANCH && git pull --ff-only && git checkout -b rescue/KEY-\$STAMP

2) Port minimal diffs only (exclude workflow edits):
   # Apply only the necessary file changes; avoid .github/workflows/*

3) Generate guardrails stamp:
   # Preferred: run in Task input (chat): /sync-i --force true
   # Fallback: make guardrails-stamp

4) Open a clean PR to $DEFAULT_BRANCH and link original PR${PR:+: #$PR}
   gh pr create --base $DEFAULT_BRANCH --title "Rescue KEY" --body "Clean rescue PR${PR:+ for #$PR}."

5) Approve docbot patches if any (optional, async):
   /oc docbot approve

6) Merge when ready (Task input):
   /merge-i --execute true

Notes:
- Slash commands are agent prompts (Task input), not shell/Python.
- Local helpers: make slash-help | make branch-status | make guardrails-stamp
EOF
