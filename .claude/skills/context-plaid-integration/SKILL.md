---
name: context-plaid-integration
description: |
  Plaid SDK integration for brokerage account linking, OAuth flows, and price data sync.
  Handles Plaid Link OAuth, historical price extraction, investment data, and sandbox users.
  Use when working with brokerage connections, Plaid Link OAuth, historical prices, or investment data,
  or when user mentions Plaid adapter, price extraction, sandbox users, OAuth flows, holdings sync,
  "Plaid error", "OAuth failed" errors, "Account linking failed" errors, or Plaid API integration.
tags: [external-api, brokerage, integration, plaid]
---

# Plaid Integration

Navigate Plaid brokerage connectivity, OAuth flows, and historical price data.

## Overview

Plaid provides brokerage account linking via OAuth (Plaid Link). See `docs/integrations/PLAID.md` for detailed patterns and gotchas.

## Backend Code

- `backend/brokers/plaid_adapter.py` - Main adapter (935 lines)
- `backend/brokers/plaid_client.py` - API client wrapper (372 lines)
- `backend/services/plaid_price_service.py` - Price data extraction (332 lines)

## Database

- `supabase/migrations/*plaid*` - Plaid-related migrations
- `supabase/schemas/public/tables/plaid_prices.sql` - Price table
- `supabase/schemas/public/tables/provider_security_mappings.sql` - Provider → canonical security mappings

**Provider Security Mappings (bd-k1c.3):**
- Natural key: `(brokerage_connection_id, provider_security_id)`
- `provider_security_id` is stable Plaid security ID (from Plaid `security.security_id`)
- `provider_payload` retained for audit, NOT in uniqueness constraint
- Enables robust upserts and reduces brittleness from payload changes

**Holdings Pipeline (bd-k1c.4):**
- Plaid sync **soft-closes** positions that disappear from broker snapshots
- `holdings.closed_at` marks closed positions (instead of deleting rows)
- Active holdings: `WHERE closed_at IS NULL`
- Enables historical position tracking and lifetime performance views

## Frontend

- Search for `plaid` or `react-plaid-link` in `frontend/src/`

## Tests

- `backend/tests/unit/test_plaid*.py` - Unit tests
- `backend/tests/manual/test_security_resolver_real_plaid.py` - Integration tests
- `backend/tests/fixtures/mock_external_services.py` - Plaid mocks

## Scripts

- `scripts/create_local_test_user.sh` - Create sandbox users

## Documentation

- **Internal**: `docs/integrations/PLAID.md`
- **External**: https://plaid.com/docs/api/products/investments/

## Key Workflows

**Plaid Holdings Sync:**
1. Fetch holdings from Plaid API
2. Store raw snapshot in `brokerage_raw_holdings`
3. Background processing resolves securities using `provider_security_mappings`
4. Upsert to canonical `holdings` table
5. Missing positions are soft-closed (set `closed_at`, not deleted)

**Provider Security Mapping:**
- Uses `(brokerage_connection_id, provider_security_id)` as natural key
- `SecurityResolver._link_provider_mapping` upserts on this key
- `RawDataService.get_existing_security_mapping` looks up by provider ID

## Related Areas

- See `context-symbol-resolution` for Plaid → EODHD symbol mapping
- See `context-brokerage` for account linking UI
- See `context-testing-infrastructure` for auth-stub patterns
- See `context-database-schema` for provider mappings and holdings schema
- See `docs/bd-k1c/EPIC_OVERVIEW.md` for Plaid pipeline hardening details
