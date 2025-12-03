# affordabot-ycs Implementation Notes

## Current State (2025-12-03)

### What Was Done
1. ✅ Created canonical `~/llm-common` repository
   - Copied from `packages/llm-common`
   - Initialized as git repo
   - Location: `/home/fengning/llm-common`

2. ✅ Removed inline `backend/llm_common/` copy
   - This was created in affordabot-0dz for Railway deployment
   - Deleted to avoid duplication

3. ✅ Updated `backend/requirements.txt`
   - Changed from inline copy to `-e ../packages/llm-common`

### Current Setup
- **Canonical repo**: `~/llm-common` (exists, git-tracked)
- **Affordabot uses**: `packages/llm-common` (via requirements.txt)
- **Imports work**: `from llm_common import ...` ✅

### Blocker: Railway Deployment

**Problem**: Railway build environment cannot access `~/llm-common`

**Options**:
1. **Keep current** (`packages/llm-common`):
   - ✅ Works in Railway
   - ✅ No changes needed
   - ❌ Not truly "canonical" (each repo has copy)

2. **Git submodule** (`~/llm-common` → `packages/llm-common`):
   ```bash
   cd ~/affordabot
   rm -rf packages/llm-common
   git submodule add ~/llm-common packages/llm-common
   ```
   - ✅ Single source of truth (`~/llm-common`)
   - ✅ Works in Railway (submodule checked out)
   - ✅ Shareable with prime-radiant-ai
   - ⚠️ Requires submodule workflow

3. **Inline copy** (revert to affordabot-0dz approach):
   - Copy `~/llm-common` → `backend/llm_common/`
   - ✅ Works in Railway
   - ❌ Duplication
   - ❌ Manual sync needed

### Recommendation: Git Submodule

Use git submodule to link `~/llm-common` into `packages/llm-common`:

```bash
cd ~/affordabot
rm -rf packages/llm-common
git submodule add ~/llm-common packages/llm-common
git commit -m "feat: Add llm-common as git submodule"
```

This achieves:
- ✅ Single canonical source (`~/llm-common`)
- ✅ Railway compatibility (submodule in repo)
- ✅ Shareable with prime-radiant-ai (same submodule)
- ✅ Automatic sync via git

### Next Steps

**If proceeding with submodule**:
1. Remove `packages/llm-common` directory
2. Add `~/llm-common` as submodule
3. Test Railway build
4. Update prime-radiant-ai to use same submodule

**If keeping current**:
1. Document that `packages/llm-common` is the canonical copy
2. Update `~/llm-common` to be a symlink or remove it
3. Mark epic as complete with caveat

### Testing Needed

- [ ] Railway build with submodule
- [ ] Local development with submodule
- [ ] prime-radiant-ai integration
- [ ] Submodule update workflow

### Files Changed

- `backend/llm_common/` → Deleted
- `backend/requirements.txt` → `-e ../packages/llm-common`
- `~/llm-common/` → Created (canonical repo)

### Commits

- `cea8bf3` - feat: Migrate to canonical ~/llm-common
- `e5ddb90` - fix: Use relative path for llm-common (Railway compat)
