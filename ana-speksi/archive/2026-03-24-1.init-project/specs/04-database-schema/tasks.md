# Tasks: Database Schema and Multitenant Setup

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 04-database-schema

## Prerequisites

- 02-backend-skeleton must be complete (shared/db modules, config)

---

## Phase 1: Setup

### P01.T001 -- Create SQL schema directory structure

Create the directory structure for SQL schema and migration files.

Files:
- Create `src/shared/db/schema/` directory
- Create `src/shared/db/migrations/` directory

- [x] P01.T001

---

## Phase 2: Implementation

### Database Changes

### P02.T001 -- Create initial schema SQL

**Mandatory to use skills: /database-schema-edit-postgres**

Create `src/shared/db/schema/create_schema.sql` with:
- `user_account` table: id (UUID no hyphens), user_name (unique), password_hash, given_name, family_name, display_name, created_at, updated_at
- `user_email` table: id (UUID no hyphens), user_account_id (FK CASCADE), email (unique), is_primary, is_verified, created_at, updated_at
- `_deployment_log` table for migration tracking
- All using `IF NOT EXISTS` for idempotent creation

Files:
- Create `src/shared/db/schema/create_schema.sql`

- [x] P02.T001

### P02.T002 -- Create master admin seed SQL

**Mandatory to use skills: /database-schema-edit-postgres**

Create `src/shared/db/schema/ensure_admin.sql` with:
- INSERT ... ON CONFLICT (user_name) DO NOTHING for user 'stenvala'
- Pre-computed bcrypt hash (cost factor 12)
- Insert primary email for admin if no email exists

Files:
- Create `src/shared/db/schema/ensure_admin.sql`

- [x] P02.T002

### P02.T003 -- Create initial migration file

**Mandatory to use skills: /database-schema-edit-postgres**

Create `src/shared/db/migrations/001_initial.sql` matching the create_schema.sql content (for migration tracking purposes).

Files:
- Create `src/shared/db/migrations/001_initial.sql`

- [x] P02.T003

### P02.T004 -- Create setup_db.py typer CLI

**Mandatory to use skills: /database-setup-postgres, /python-coding-conventions**

Create `setup_db.py` at project root with commands:
- `create <suffix>`: Create schema `"ana-auth-{suffix}"`, run create_schema.sql, run ensure_admin.sql
- `drop <suffix> [--confirm]`: Drop schema with CASCADE
- `update <suffix>`: Apply pending migrations with checksum tracking via _deployment_log
- `main`: Drop and recreate main schema
- `e2e`: Drop and recreate e2e schema
- `local-update`: Run update on main schema with local DB config
- Connect using config from shared/config.py

Files:
- Create `setup_db.py`

Verify: `uv run setup_db.py --help` shows all commands.

- [x] P02.T004

### P02.T005 -- Create SQLModel classes for user tables

**Mandatory to use skills: /database-model**

Create SQLModel classes matching the SQL schema:
- `UserAccount` with all fields from user_account table
- `UserEmail` with all fields from user_email table
- Both extend BaseDBModelMixin

Files:
- Create `src/shared/db/models/user_account.py`
- Create `src/shared/db/models/user_email.py`

- [x] P02.T005

---

## Phase 3: Test Automation

### Backend Tests

### P03.T001 -- Create setup_db.py integration tests

**Mandatory to use skills: /test-python-integration**

Test against local Docker PostgreSQL:
- Create a test schema, verify tables exist
- Verify admin user is created
- Verify idempotent creation (run create twice)
- Drop schema and verify it's gone
- Run update on already-up-to-date schema, verify no changes

Files:
- Create `src/tests/integration/__init__.py`
- Create `src/tests/integration/db/__init__.py`
- Create `src/tests/integration/db/test_setup_db.py`

Verify: `uv run pytest src/tests/integration/db/test_setup_db.py -v` passes.

- [x] P03.T001

---

## Phase 4: Manual Verification

- Start local PostgreSQL: `docker compose up -d`
- Run `uv run setup_db.py create main` and verify schema exists
- Connect to PostgreSQL and inspect `"ana-auth-main"` schema tables
- Verify admin user exists: `SELECT * FROM user_account WHERE user_name = 'stenvala'`
- Run `uv run setup_db.py drop main --confirm` and verify schema is gone
- Run `uv run setup_db.py create main` again to verify idempotent creation
