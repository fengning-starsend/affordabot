---
name: context-portfolio
description: |
  Portfolio management, account aggregation, holdings, and positions tracking.
  Handles portfolio views, account management, holdings display, position tracking, and portfolio analytics.
  Use when working with portfolio views, account management, holdings display, or position tracking,
  or when user mentions portfolio features, accounts table, holdings sync, portfolio data issues,
  portfolio value, asset allocation, aggregation, or account management.
tags: [feature, portfolio, user-facing]
---

# Portfolio

Navigate portfolio management features, account aggregation, and holdings.

## Overview

Core portfolio management functionality - accounts, holdings, positions.

## Backend Code

- `backend/api/accounts.py` - Accounts API
- `backend/services/account_service.py` - Account business logic
- Search for "portfolio", "account", "holdings" in `backend/`

## Frontend Code

- Search for "portfolio", "account", "holdings" in `frontend/src/`
- Portfolio dashboard components
- Account management UI

## Database

- `portfolios` table - User portfolios
- `accounts` table - Brokerage accounts
- `holdings` table - Current and closed positions
  - **Active positions**: Filter with `WHERE closed_at IS NULL`
  - **Closed positions**: `closed_at IS NOT NULL` (soft-close, not deleted)
- `holdings_snapshots` table - Time-series snapshots for historical analytics
  - Point-in-time positions with market values
  - Enables portfolio value over time, performance tracking
  - Created by `backend/scripts/create_holdings_snapshot.py`
- See `context-database-schema` for full schema details

## Tests

- Portfolio feature tests
- Account management tests

## Documentation

- **Internal**: `docs/features/PORTFOLIO.md` (create if needed)

## Key Patterns

**Current Portfolio Views:**
- Query active holdings with `WHERE closed_at IS NULL`
- Exclude closed positions from current portfolio value calculations

**Historical Analytics:**
- Use `holdings_snapshots` for point-in-time portfolio composition
- Snapshots capture quantity, cost basis, and market value at snapshot time
- Enables time-series analysis, performance attribution, and trend visualization

## Related Areas

- See `context-brokerage` for account linking
- See `context-analytics` for portfolio analytics
- See `context-database-schema` for portfolio schema (including bd-k1c enhancements)
- See `docs/bd-k1c/EPIC_OVERVIEW.md` for Plaid pipeline hardening details
