#!/bin/bash
# dx-doctor: Fast checks for V3 DX compliance (Affordabot)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo "🩺 dx-doctor checking Affordabot environment..."

ERRORS=0

# 1. Git Clean Check
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Git workspace dirty${RESET}"
    echo "   Fix: git commit -m \"...\" or git stash"
    # Not an error, just warning
else
    echo -e "${GREEN}✅ Git workspace clean${RESET}"
fi

# 2. Beads Sync Check
if [ -f ".beads/issues.jsonl" ]; then
    # Simple check if jsonl exists; reliable check requires 'bd status' or similar
    # We can check if 'bd' is in path
    if command -v bd &> /dev/null; then
        echo -e "${GREEN}✅ Beads CLI found${RESET}"
    else
        echo -e "${RED}❌ Beads CLI missing${RESET}"
        echo "   Fix: pip install beads-cli"
        ERRORS=$((ERRORS+1))
    fi
fi

# 3. Railway Shell Check (if RAILWAY_ENVIRONMENT not set)
if [ -z "$RAILWAY_ENVIRONMENT" ]; then
    echo -e "${YELLOW}⚠️  Not in Railway shell${RESET}"
    echo "   Fix: railway shell (for db access)"
else
    echo -e "${GREEN}✅ Railway environment: $RAILWAY_ENVIRONMENT${RESET}"
fi

# 4. Agent Skills Check (Warn Only)
if [ -x ~/agent-skills/mcp-doctor/check.sh ]; then
    echo "Running skills check..."
    ~/agent-skills/mcp-doctor/check.sh || true
else
    echo -e "${YELLOW}⚠️  Skills check script missing${RESET}"
    echo "   Fix: Ensure ~/agent-skills is mounted and symlinked to ~/.agent/skills"
fi

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✨ DX Doctor passed (warnings can be ignored)${RESET}"
    exit 0
else
    echo -e "${RED}❌ DX Doctor found $ERRORS errors${RESET}"
    exit 1
fi
