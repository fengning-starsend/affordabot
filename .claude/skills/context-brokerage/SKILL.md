---
name: context-brokerage
description: |
  Trading systems, broker integrations, account management, and external broker APIs. Use when working with brokerage code, files, or integration. Invoke when navigating brokerage codebase, searching for brokerage files, debugging brokerage errors, or discussing brokerage patterns. Keywords: brokerage, {{KEYWORDS}}
tags: {{TAGS}}
---

# brokerage Context

**Files:** 22 files, 4890 LOC

Quick navigation for brokerage area. Indexed 2025-11-22.

## Quick Navigation

### Database (Active)
- supabase/migrations/20251024221800_fix_brokerage_raw_securities_timestamps.sql ✅ CURRENT
- supabase/migrations/20250929130000_add_raw_brokerage_data_tables.sql ✅ CURRENT
- supabase/migrations/20250922180000_create_generic_brokerage_schema.sql ✅ CURRENT
- supabase/migrations/20251024214554_fix_brokerage_connections_timestamps.sql ✅ CURRENT
- supabase/migrations/20250922131700_fix_accounts_rls_jwt_claims.sql ✅ CURRENT
- supabase/migrations/20250926231500_ensure_all_users_have_accounts.sql ✅ CURRENT
- supabase/migrations/20250930201800_enhance_accounts_table_for_multi_provider_support.sql ✅ CURRENT
- supabase/migrations/20250930201802_enhance_accounts_table_for_multi_provider_support.sql ✅ CURRENT

### Backend (Active)
- backend/brokers/models.py ✅ CURRENT
- backend/brokers/plaid_adapter.py ✅ CURRENT
- backend/brokers/plaid_client.py ✅ CURRENT
- backend/brokers/factory.py ✅ CURRENT
- backend/brokers/snaptrade_adapter.py ✅ CURRENT
- backend/brokers/base.py ✅ CURRENT
- backend/brokers/__init__.py ✅ CURRENT

### Frontend (Active)
- frontend/src/components/AdminBrokeragePage.tsx ✅ CURRENT
- frontend/src/components/BrokerageConnections.tsx ✅ CURRENT
- frontend/src/components/AccountManagement.tsx ✅ CURRENT

### Backend (Active)
- backend/api/brokerage_connections.py ✅ CURRENT
- backend/api/accounts.py ✅ CURRENT

### Database (Deprecated)
- supabase/migrations/20251024221600_fix_brokerage_raw_holdings_timestamps.sql ❌ DO NOT EDIT

### Backend (Deprecated)
- backend/api/snaptrade_connections_backup_pre_clerk.py ❌ DO NOT EDIT



## How to Use This Skill

**When navigating brokerage code:**
- Use file paths with line numbers for precise navigation
- Check "CURRENT" markers for actively maintained files
- Avoid "DO NOT EDIT" files (backups, deprecated)
- Look for entry points (classes, main functions)

**Common tasks:**
- Find API endpoints: Look for `*_api.py:*` files
- Find business logic: Look for `*_service*.py` or engine classes
- Find data models: Look for `*_models.py` or schema definitions
- Find tests: Check "Tests" section

## Serena Quick Commands

```python
# Get symbol overview for a file
mcp__serena__get_symbols_overview(
  relative_path="<file_path_from_above>"
)

# Find specific symbol
mcp__serena__find_symbol(
  name_path="ClassName.method_name",
  relative_path="<file_path>",
  include_body=True
)

# Search for pattern
mcp__serena__search_for_pattern(
  substring_pattern="search_term",
  relative_path="<directory>"
)
```

## Maintenance

**Regenerate this skill:**
```bash
scripts/area-context-update brokerage
```

**Edit area definition:**
```bash
# Edit .context/area-config.yml
# Then regenerate
scripts/area-context-update brokerage
```

---

**Area:** brokerage
**Last Updated:** 2025-11-22
**Maintenance:** Manual (regenerate as needed)
**Auto-activation:** Triggers on "brokerage", "navigate brokerage", "brokerage files"
