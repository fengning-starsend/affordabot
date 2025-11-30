---
name: context-eodhd-integration
description: |
  EODHD market data API integration for stock prices, fundamentals, and exchange listings.
  Handles price refresh, fundamentals lookup, S&P 500 constituents, and API rate limiting.
  Use when working with EODHD API, market data, stock fundamentals, or price feeds,
  or when user mentions EODHD refresh, stock prices, EOD prices, price updates, fundamentals data,
  market data failures, "EODHD error", "API rate limit" errors, automated price refresh, or exchange listings.
tags: [external-api, data-provider, integration, eodhd]
---

# EODHD Integration

Navigate EODHD API integration for fundamental data, EOD prices, and exchange listings.

## Overview

EODHD provides fundamental data, historical prices, and exchange metadata. See `docs/integrations/EODHD.md` for integration patterns.

## Backend Code

- `backend/services/eodhd_service.py` - Main service client
- `backend/services/eodhd_*.py` - Various EODHD integrations
- `backend/utils/field_mapper.py` - Field mapping

## Database

- `supabase/migrations/*eodhd*` - EODHD-related migrations
- Multiple tables for fundamentals, prices

## Supabase Functions

- `supabase/functions/fetch-eodhd-constituents/` - Index constituents fetcher

## Tests

- `backend/tests/manual/test_enhanced_resolution.py`
- `backend/tests/unit/test_services/test_eodhd_*.py`

## Scripts

- `scripts/backfill_fundamentals.py` - Backfill fundamental data

## Documentation

- **Internal**: `docs/integrations/EODHD.md`
- **External**: https://eodhistoricaldata.com/financial-apis/

## Related Areas

- See `context-symbol-resolution` for EODHD normalization
- See `context-database-schema` for EODHD tables
