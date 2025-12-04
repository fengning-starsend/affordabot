#!/usr/bin/env bash
cat <<'TXT'
OpenCode Slash Commands — Quick Usage

- Slash commands like `/feature-new`, `/sync-i`, `/merge-i`, `/rescue-i`, `/pr-rescue-i` are agent prompts.
- Do NOT run them in your shell or Python scripts.

How to invoke:
- OpenCode Task input (chat): `/sync-i --force true`
- OpenCode PR ChatOps: `/oc run "/rescue-i --pr 123"`

Discovery vs Protected
- Discovery (read-only): Serena search, GitHub metadata → OK outside Railway.
- Protected (mutations/secrets): requires Railway shell. If missing, commands print the exact hint to run `railway shell`.

Local helpers (shell):
- make branch-status       # status + one “Next step”
- make guardrails-stamp    # writes .command-proof/guardrails.json
- make rescue-checklist    # prints manual rescue steps for PR=<N>

More: see AGENTS.md and docs/DX_PARITY_GUARDRAILS/SPEC.md.
TXT
