# Affordabot Scripts

Canonical location for workflows, verification, and maintenance scripts.

## Directory Structure

- `cli/` - User-facing CLI tools (e.g., `dx_doctor.sh`)
- `ci/` - CI/CD pipeline scripts
- `maintenance/` - Database and one-off maintenance tasks
- `verification/` - Tests and system verification scripts
- `lib/` - Shared libraries
- `legacy/` - Deprecated scripts

## Key Tools

### `scripts/cli/dx_doctor.sh`
Fast health check for your local environment. checks:
- Git status
- Beads CLI presence
- Railway shell environment
- MCP Skills Validation (via `~/agent-skills`)

Usage:
```bash
./scripts/cli/dx_doctor.sh
```

## Skills Setup
Ensure `~/agent-skills` is mounted and symlinked:
```bash
ln -sfn ~/agent-skills ~/.agent/skills
```
