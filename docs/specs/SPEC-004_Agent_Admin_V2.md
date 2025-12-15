# SPEC-004: Agent Admin V2

**Status**: Ready (Pending Schema Recovery)
**Epic**: `affordabot-9g6`
**Dependencies**: SPEC-003 (S3 Storage)

## 1. Overview
Enhance the internal Admin Dashboard with Basic Auth and recovered schemas.

## 2. Gap Resolution

### 2.1 Authentication
**Decision**: Use HTTP Basic Auth for MVP.
**Future**: Migrate to Clerk (Tracked in `affordabot-dev-auth`).

**Implementation**:
- Add `Security` dependency to `routers/admin.py`.
- Validate against generic `ADMIN_USER` / `ADMIN_PASSWORD` (add to Railway vars).

### 2.2 Schema Recovery
**Issue**: Admin tables (`admin_tasks`, `pipeline_runs`) deleted during purge.
**Recovery Plan**:
1.  Attempt `supabase db dump --remote` to recover state from `affordabot-dev`.
2.  If fail, `git checkout` deleted files from history.
3.  Place consolidated schema in `backend/migrations/002_admin_schema_recovered.sql`.

## 3. Execution Order
1.  Recover Schema (Pre-req).
2.  Implement Basic Auth Middleware.
3.  Connect Admin Endpoints to recovered tables.
