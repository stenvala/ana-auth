---
name: database-setup-postgres
description: Set up PostgreSQL database with setup script and schema initialization
---

# Setup PostgreSQL Database

Create a PostgreSQL database with setup script and schema initialization.

## When to Use

- Setting up a new PostgreSQL database for a project
- Creating PostgreSQL schema in Docker (already running on port 5432)
- Need schema-based multitenancy (main, e2e suffixes)

## Prerequisites

PostgreSQL must be running in Docker on port 5432 with default credentials:

- Host: localhost
- Port: 5432
- Database: postgres
- User: postgres
- Password: postgres

## Instructions

### 1. Get Project Name

Ask the user for the project/schema name (e.g., "my-app" becomes "my-app-main" schema).

### 2. Create setup_db.py

Create the setup script from `resources/postgres-setup.md` template in the project root.

Update the `PROJECT_NAME` constant to match the user's project name.

### 3. Create Schema Directory

Create `src/shared/db/scripts/` directory structure:

```
src/
└── shared/
    └── db/
        └── scripts/
            ├── create_schema.sql
            └── demo_data.sql (optional)
```

### 4. Create Schema File

Create `src/shared/db/scripts/create_schema.sql` with basic template or project-specific tables.

### 5. Add Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "psycopg2-binary>=2.9.0",
    "typer>=0.9.0",
]
```

### 6. Run Database Setup

```bash
# Create main schema
uv run python setup_db.py create main

# Or reset with demo data
uv run python setup_db.py main
```

### 7. Update README.md

Add database section to README.md with connection details and commands.

## File Structure

After setup:

```
<project-root>/
├── setup_db.py                    # Database setup script
├── src/
│   └── shared/
│       └── db/
│           └── scripts/
│               ├── create_schema.sql
│               ├── demo_data.sql        # Optional
│               └── create_initial_data_*.sql  # Optional
└── README.md
```

## Commands

| Command                               | Description                      |
| ------------------------------------- | -------------------------------- |
| `create <suffix>`                     | Create schema with tables        |
| `drop <suffix>`                       | Drop schema                      |
| `demo_data <suffix>`                  | Add demo data                    |
| `main`                                | Reset main schema with demo data |
| `main_update`                         | Update main schema (no drop)     |
| `e2e`                                 | Reset e2e test schema            |
| `run --schema-suffix <s> --cmd <sql>` | Execute SQL                      |

## Templates

See `resources/postgres-setup.md` for complete setup_db.py template.

