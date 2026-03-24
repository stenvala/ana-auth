# Technical Specification: Database Schema and Multitenant Setup

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Create the PostgreSQL database setup tooling (`setup_db.py`) with schema-based multitenancy, initial user schema (user_account, user_email tables), master admin user seeding, and migration support. Uses typer CLI following events.3rdb.com patterns.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| database-setup-postgres | Setup script pattern -- typer CLI, create/drop/update commands |
| database-schema-edit-postgres | SQL conventions -- UUID generation, constraints, indexes |
| database-model | SQLModel class definitions matching the SQL schema |
| database-repository | Repository pattern for data access (establishes conventions) |
| database-design | Data model documentation structure |

## Architecture

```
project root/
  setup_db.py                       # Typer CLI for schema management
  src/
    shared/
      db/
        schema/
          create_schema.sql         # Table definitions
          ensure_admin.sql          # Master admin user (idempotent)
        migrations/
          001_initial.sql           # Initial migration (matches create_schema.sql)
        models/
          user_account.py           # SQLModel for user_account table
          user_email.py             # SQLModel for user_email table
```

### Schema Multitenancy

Each deployment/test environment gets its own PostgreSQL schema:
- `"ana-auth-main"` -- production
- `"ana-auth-dev"` -- development stage
- `"ana-auth-e2e"` -- manual E2E testing
- `"ana-auth-test-{uuid}"` -- automated test workers (created/destroyed per session)

Schema names contain hyphens and must be quoted in SQL: `CREATE SCHEMA IF NOT EXISTS "ana-auth-main"`.

### Migration Strategy

- Migrations are SQL files in `src/shared/db/migrations/` named with numeric prefixes (001_, 002_, etc.)
- A `_deployment_log` table tracks which migrations have been applied (by filename and checksum)
- `setup_db.py update <suffix>` applies pending migrations in order
- If a migration fails, subsequent migrations do not run

## Data Model Changes

See [data-model.md](../../data-model.md) for the full auth domain data model. This story creates:
- `user_account` table -- user identity and authentication
- `user_email` table -- user email addresses with primary/verified flags

## API Changes

None -- this is a database setup tool, not an API change.

## Implementation Approach

1. **Create SQL schema file** (`src/shared/db/schema/create_schema.sql`):
   - `user_account` table with UUID primary key (no hyphens), user_name unique, password_hash, name fields, timestamps
   - `user_email` table with UUID primary key, foreign key to user_account with CASCADE, unique email, is_primary, is_verified, timestamps
   - Use `IF NOT EXISTS` for idempotent creation

2. **Create admin seed script** (`src/shared/db/schema/ensure_admin.sql`):
   - Insert master admin user (username: stenvala) with pre-computed bcrypt hash
   - INSERT ... ON CONFLICT (user_name) DO NOTHING
   - Insert primary email for admin if no email exists

3. **Create setup_db.py** (typer CLI):
   - `create <suffix>`: Create schema, run create_schema.sql, run ensure_admin.sql
   - `drop <suffix> [--confirm]`: Drop schema with CASCADE (prompt if no --confirm)
   - `update <suffix>`: Apply pending migrations from migrations directory
   - `main`: Convenience -- drop and recreate main schema
   - `e2e`: Convenience -- drop and recreate e2e schema
   - `local-update`: Convenience -- run update on main schema with local DB config
   - Connect to DB using config from environment or defaults (localhost:5432, postgres/postgres)

4. **Create SQLModel classes**:
   - `UserAccount` model matching user_account table
   - `UserEmail` model matching user_email table
   - Both extend BaseDBModelMixin

5. **Create initial migration** (`src/shared/db/migrations/001_initial.sql`):
   - Contains the same SQL as create_schema.sql (for tracking purposes)

## Testing Strategy

### Automated Tests

- Unit test: Verify setup_db.py CLI commands are registered correctly
- Integration test: Create a test schema, verify tables exist, verify admin user exists, drop schema
- Integration test: Run update on an already-up-to-date schema, verify no changes

### Manual Testing

- `docker compose up -d` to start PostgreSQL
- `uv run setup_db.py create main` -- verify schema and tables created
- `uv run setup_db.py drop main --confirm` -- verify schema dropped
- Connect to PostgreSQL and inspect `"ana-auth-main"` schema

## Out of Scope

- User registration or sign-up logic
- Password change or reset functionality
- Role or permission management

## Migration / Deployment Notes

- The deploy script (story 06) calls setup_db.py commands during deployment
- Schema creation is idempotent -- safe to run multiple times
- Admin password hash must be pre-computed and embedded in ensure_admin.sql
- Production DB is on LAN (192.168.0.x:5432), not localhost

## Security Considerations

- Admin password hash is a bcrypt hash with cost factor 12 -- pre-computed, not generated at runtime
- The actual admin password must not be committed to the repository; only the hash
- Database credentials for production come from deployment config, not code
