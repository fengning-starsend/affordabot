---
name: context-clerk-integration
description: |
  Clerk authentication integration for user login, webhooks, and session management.
  Handles auth flows, webhook processing, JWT validation, user creation, and RLS policies.
  Use when working with authentication, user management, Clerk integration, or RLS policies,
  or when user mentions Clerk webhooks, user login, auth errors, session issues, JWT validation,
  "User not found" errors, "Invalid token" errors, "Webhook verification failed" errors, or access control.
tags: [external-api, auth, security, clerk]
---

# Clerk Integration

Navigate Clerk authentication flows, JWT validation, and RLS integration.

## Overview

Clerk provides user authentication and session management. See `docs/integrations/CLERK.md` for auth patterns.

## Backend Code

- `backend/auth/clerk.py` - Authentication middleware
- `backend/config/clerk_config.py` - Configuration
- `backend/middleware/*clerk*` - Request authentication

## Frontend Code

- Search for `@clerk/clerk-react` or `useClerk` in `frontend/src/`

## Database

- `supabase/migrations/*clerk*` - Clerk integration (15+ migrations)
- RLS policies tied to `clerk_user_id`

## Tests

- `backend/tests/manual/test_clerk.py`
- `backend/tests/manual/test_auth_stub.py` - Auth stub pattern
- `backend/tests/unit/test_auth/test_clerk_auth.py`

## Scripts

- `scripts/create_local_test_user.sh` - Create test users

## User ID System

**Critical:** See `docs/USER_ID_DOCUMENTATION.md` for complete ID field reference.

**Four ID fields:**
- `id` (UUID): Internal database primary key
- `auth_id` (TEXT): **Authentication key - MUST NEVER CHANGE**
- `clerk_id` (TEXT): Redundant copy of Clerk ID
- `email` (TEXT): User contact

**Validation (bd-eol):**
- `auth_id` must match: `user_*` (Clerk) or `test_*` (test users)
- UUIDs are **NOT valid** auth_ids
- Validation enforced in `backend/crud_supabase.py:validate_auth_id()`

**Normal flow:** Clerk webhook → `get_or_create_user()` → validates `auth_id` → creates user

**Test users:** 7 users with `test_*` auth_ids for integration testing (intentional, safe)

## Documentation

- **Internal**:
  - `docs/integrations/CLERK.md` - Auth patterns
  - `docs/USER_ID_DOCUMENTATION.md` - ID fields, validation, troubleshooting (bd-eol)
- **External**: https://clerk.com/docs

## Related Areas

- See `context-testing-infrastructure` for auth stub patterns
- See `context-database-schema` for RLS policies
