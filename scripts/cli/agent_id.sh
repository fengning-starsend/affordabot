#!/usr/bin/env bash
set -euo pipefail

# Normalize and display the current agent identity used for DX and stamping

# Node (VM/host)
AGENT_NODE=${AGENT_NODE:-$(hostname -s 2>/dev/null || uname -n 2>/dev/null || echo unknown)}

# Platform detection (Claude Code vs OpenCode) — allow override via env
if [ -n "${AGENT_PLATFORM:-}" ]; then
  PLATFORM="$AGENT_PLATFORM"
else
  if [ -n "${OPENCODE:-}" ] || [ -d ".opencode" ]; then
    PLATFORM="opencode"
  elif [ -d ".claude" ]; then
    PLATFORM="claude-code"
  else
    PLATFORM="unknown"
  fi
fi

# Model identifier (optional; set by harness), fallback to unknown
MODEL=${AGENT_MODEL:-${MODEL:-unknown}}

# Logical agent id (required for parallel sessions): A, B, C, A1, etc.
LOGICAL=${AGENT_ID:-${AGENT:-}}
if [ -z "$LOGICAL" ]; then
  echo "⚠️  AGENT_ID not set. Set AGENT_ID=A (or pass AGENT=A to make targets)." >&2
  LOGICAL="unknown"
fi

# Session stamp for uniqueness (epoch seconds)
STAMP=${AGENT_STAMP:-$(date +%s)}

AGENT_KEY="${AGENT_NODE}-${PLATFORM}-${MODEL}-${LOGICAL}-${STAMP}"

cat <<EOF
Agent Identity
--------------
Node     : $AGENT_NODE
Platform : $PLATFORM
Model    : $MODEL
Agent ID : $LOGICAL
Session  : $STAMP
Key      : $AGENT_KEY

Exports you can set:
  export AGENT_ID=A            # logical id (required for parallel sessions)
  export AGENT_PLATFORM=$PLATFORM
  export AGENT_MODEL=$MODEL
  export AGENT_NODE=$AGENT_NODE
  export AGENT_STAMP=$STAMP

Usage in DX:
  - Pass AGENT=<ID> to make worktree-add / branch-new
  - Commit trailer: Agent: ${PLATFORM}-${LOGICAL}
EOF

