---
name: database-setup-sqlite
description: Set up SQLite database with setup script, schema, and migrations
---

# Setup SQLite Database

Create an SQLite database with setup script, schema initialization, and migration support.

## When to Use

- Setting up a new SQLite database for local development
- Need file-based database with migration support
- Simple applications without PostgreSQL dependency

## Tenancy Modes

This skill supports two modes:

### Single-Tenant (default)

- One database file in a data directory
- Simpler code: no domain parameter needed

### Multitenant

- Database per domain in separate directories
- Use `--domain` flag on setup_db.py commands
- Use domain-specific session context

Choose based on project requirements. If in doubt, use single-tenant.

## Instructions

### 1. Create Directory Structure

```
src/
└── shared/
    ├── common.py                 # Shared utilities (path resolution)
    └── db/
        ├── __init__.py
        ├── db_context.py         # Database session manager
        └── scripts/
            ├── create_schema.sql  # Initial schema (with migrations table)
            ├── demo_data.sql      # Optional demo data
            └── migrations/        # Migration files
                └── 001_example.sql
```

### 2. Create setup_db.py

Create the setup script from `resources/sqlite-setup.md` template in the project root. Choose the single-tenant or multitenant template based on project needs.

### 3. Create Schema File

Always include the migrations tracking table:

```sql
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add your tables below
```

### 4. Create Common Utilities and DBContext

See `resources/sqlite-setup.md` for complete templates including:
- Path resolution utilities (single-tenant and multitenant)
- DBContext session manager with WAL mode
- setup_db.py command implementations

### 5. Add Dependencies

```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "typer>=0.9.0",
]
```

### 6. Run Database Setup

```bash
uv run python setup_db.py create    # Create schema and run migrations
uv run python setup_db.py local     # Reset database
```

## Database Naming Convention

**CRITICAL**: The SQLite database file MUST always be named `data.db`.

## Migration System

Migrations are SQL files in the migrations subdirectory.

- **Naming**: `NNN_description.sql` (e.g., `001_add_can_edit_users.sql`)
- **Execution**: Schema runs first, then migrations are applied in sorted order
- **Tracking**: Each applied migration is recorded in the `migrations` table

## Commands

| Command           | Description                             |
| ----------------- | --------------------------------------- |
| `create`          | Create schema and run migrations        |
| `drop`            | Drop database file                      |
| `local`           | Reset database                          |
| `run --cmd <sql>` | Execute SQL command                     |

Multitenant mode adds `--domain` / `-d` flag to each command.

## Templates

See `resources/sqlite-setup.md` for complete templates:
- setup_db.py (both tenancy modes)
- DBContext classes (both modes)
- Common utilities (both modes)
- Schema and migration patterns

