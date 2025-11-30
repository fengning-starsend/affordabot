---
name: context-snaptrade-integration
description: |
  SnapTrade alternative brokerage connectivity provider for account linking and trading.
  Handles SnapTrade API integration, OAuth flows, account linking, and multi-provider strategy.
  Use when working with SnapTrade API, alternative brokerage connections, or comparing with Plaid,
  or when user mentions SnapTrade integration, multi-provider strategy, SnapTrade connection issues,
  alternative brokerage provider, SnapTrade OAuth, or trading functionality.
tags: [external-api, brokerage, integration, snaptrade]
---

# SnapTrade Integration

Navigate SnapTrade brokerage connectivity (alternative to Plaid).

## Overview

SnapTrade provides brokerage account connectivity. See `docs/integrations/SNAPTRADE.md`.

## Backend Code

- `backend/brokers/snaptrade_adapter.py` - SnapTrade adapter (538 lines)

## Supabase Functions

- `supabase/functions/snaptrade-user/` - User management
- `supabase/functions/snaptrade-oauth/` - OAuth flow

## Status

**Current**: Partial integration
**Future**: May complement or replace Plaid

## Documentation

- **Internal**: `docs/integrations/SNAPTRADE.md`
- **External**: https://snaptrade.com/docs

## Related Areas

- See `context-brokerage` for account linking patterns
- See `context-plaid-integration` for comparison
