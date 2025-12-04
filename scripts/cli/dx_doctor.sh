#!/usr/bin/env bash
set -euo pipefail

echo "DX Doctor — quick preflight"

# 1) Railway env
if [[ -z "${RAILWAY_ENVIRONMENT:-}" ]]; then
  echo "[!] Railway env: missing (run 'railway shell' for protected steps)"
else
  echo "[✓] Railway env: ${RAILWAY_ENVIRONMENT}"
fi

# 2) Git hooks
if [[ -x .githooks/pre-push ]]; then
  echo "[✓] Git hooks installed (.githooks/pre-push)"
else
  echo "[!] Git hooks not installed — run: make setup-git-hooks"
fi

# 3) GH auth
if gh auth status >/dev/null 2>&1; then
  echo "[✓] gh auth: ok"
else
  echo "[!] gh auth: please run 'gh auth login'"
fi

# 4) Guardrails stamp
if [[ -f .command-proof/guardrails.json ]]; then
  echo "[✓] guardrails stamp present (.command-proof/guardrails.json)"
else
  echo "[!] missing guardrails stamp. Run '/sync-i --force true' in CC/OC"
fi

echo "Done. See AGENTS.md for next steps."

