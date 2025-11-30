---
name: context-symbol-resolution
description: |
  Financial security symbol normalization across Plaid, EODHD, SnapTrade providers. Handles ticker resolution, CUSIP/ISIN lookups, cross-provider symbol mapping, and fallback security creation. Use when working with symbol mapping, ticker resolution, CUSIP/ISIN normalization, or when user mentions security resolver, ticker lookup, symbol normalization, fallback security creation, resolver fallbacks, lookup failures, "Symbol not found" errors, or "Ticker mismatch" issues.
tags: [data-layer, symbol-resolution, normalization]
---

# Symbol Resolution

Navigate symbol normalization logic that reconciles financial securities across data providers.

## Overview

Maps Plaid/SnapTrade symbols to EODHD format. See `docs/symbol-resolution/INDEX.md` for patterns.

## Backend Code

- `backend/services/security_resolver_eodhd_first.py` - Main resolution logic (48KB)
- `backend/utils/field_mapper.py` - Field mapping

## Tests

- `backend/tests/manual/test_complete_security_resolver.py`
- `backend/tests/manual/test_security_resolver_real_plaid.py`
- `backend/tests/unit/test_services/test_security_resolver.py`

## Scripts

- `scripts/test_enhanced_resolution.py`

## Documentation

- **Internal**: `docs/symbol-resolution/INDEX.md`

## Known Edge Cases

- Crypto assets (Plaid provides, EODHD doesn't)
- Options (complex symbol formats)
- International securities (exchange code differences)

## Related Areas

- See `context-plaid-integration` for Plaid symbol extraction
- See `context-eodhd-integration` for EODHD normalization
- See `context-database-schema` for securities table
