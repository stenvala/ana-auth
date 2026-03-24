# Technical Specification: Database Schema and Multitenancy

**Domain**: auth/database-schema
**Last updated**: 2026-03-24

## Overview

Schema-based multitenancy with PostgreSQL, managed via a typer CLI tool and SQL migration files tracked by checksum.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| database-setup-postgres | Governs PostgreSQL setup patterns |
| database-schema-edit-postgres | Governs schema editing and migration patterns |
| database-model | Governs SQLModel class definitions |
| database-repository | Governs repository pattern for DB operations |

## Architecture

```
src/shared/db/
  schema/
    create_schema.sql    # Table definitions (IF NOT EXISTS)
    ensure_admin.sql     # Master admin user (ON CONFLICT DO NOTHING)
  migrations/
    001_initial.sql      # Initial migration
  context.py             # DBContext with search_path management
setup_db.py              # Typer CLI for schema management
```

## Data Model

See [auth data model](../../data-models/auth.md).

## Key Implementation Patterns

1. **Schema prefix**: All schemas use `ana-auth-{suffix}` naming convention.
2. **Migration tracking**: `_deployment_log` table stores filename and SHA checksum per applied migration.
3. **Idempotent creation**: `CREATE TABLE IF NOT EXISTS` and `INSERT ... ON CONFLICT DO NOTHING` ensure safe re-execution.
4. **SQLModel classes**: `UserAccount` and `UserEmail` in `src/shared/` map to the database tables.

## Migration / Deployment Notes

- Schema creation and migration are run during deployment by `mcc_deploy.py`.
- `setup_db.py` is the local development interface.
- Never remove existing data; ask user for manual intervention if migrations fail.
