# SQLite Database Setup

SQLite is a file-based database ideal for local development and simple applications.

## Database Location

**CRITICAL**: The database file MUST always be named `data.db`. Never use project-specific names.

### Single-Tenant Mode (default)

SQLite database is stored at: `mcc/data/data.db`

In production, the `DATA_DIR` environment variable points to the data directory.

### Multitenant Mode

SQLite databases are stored per domain at: `mcc/domains/<domain>/data.db`

- `localhost` - Local development
- `example.com` - Production domain

## setup_db.py Template

### Single-Tenant Mode

```python
#!/usr/bin/env python3
"""Database setup script using SQLite."""

import sqlite3
import os
from pathlib import Path

import typer

app = typer.Typer(help="Setup SQLite database")


def get_data_dir() -> Path:
    """Get data directory. Uses DATA_DIR env var or defaults to mcc/data."""
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir)
    return Path(__file__).parent / "mcc" / "data"


def get_db_path() -> Path:
    """Get database path."""
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "data.db"


def get_scripts_path() -> Path:
    """Get path to SQL scripts."""
    return Path(__file__).parent / "src" / "shared" / "db" / "scripts"


def get_migrations_path() -> Path:
    """Get path to migration scripts."""
    return get_scripts_path() / "migrations"


def execute_sql_file(conn: sqlite3.Connection, file_path: Path, description: str) -> bool:
    """Execute SQL file."""
    if not file_path.exists():
        print(f"WARNING: {description} file not found at: {file_path}")
        return False

    with open(file_path, "r") as f:
        sql_content = f.read()

    cursor = conn.cursor()
    cursor.executescript(sql_content)
    conn.commit()
    print(f"PASS: {description} executed successfully.")
    return True


def run_migrations(conn: sqlite3.Connection) -> None:
    """Run pending migrations."""
    migrations_path = get_migrations_path()
    if not migrations_path.exists():
        print("WARNING: Migrations directory not found.")
        return

    cursor = conn.cursor()

    # Get list of already applied migrations
    cursor.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}

    # Get all migration files sorted by name
    migration_files = sorted(migrations_path.glob("*.sql"))

    for migration_file in migration_files:
        migration_name = migration_file.stem
        if migration_name in applied:
            print(f"SKIP: Migration {migration_name} already applied.")
            continue

        print(f"APPLY: Running migration {migration_name}...")
        with open(migration_file, "r") as f:
            sql_content = f.read()

        try:
            cursor.executescript(sql_content)
            cursor.execute(
                "INSERT INTO migrations (name) VALUES (?)", (migration_name,)
            )
            conn.commit()
            print(f"PASS: Migration {migration_name} applied successfully.")
        except sqlite3.Error as e:
            print(f"ERROR: Migration {migration_name} failed: {e}")
            raise


def _create_schema() -> None:
    """Create database schema and run migrations."""
    db_path = get_db_path()
    print(f"Creating schema in: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        scripts_path = get_scripts_path()
        execute_sql_file(conn, scripts_path / "create_schema.sql", "Schema creation")
        print(f"PASS: Schema created: {db_path}")
        run_migrations(conn)
    except sqlite3.Error as e:
        print(f"ERROR: Error creating schema: {e}")
    finally:
        conn.close()


def _drop_db() -> None:
    """Drop database by deleting the file."""
    db_path = get_db_path()
    print(f"Dropping database: {db_path}")

    if db_path.exists():
        db_path.unlink()
        print(f"PASS: Database dropped: {db_path}")
    else:
        print(f"WARNING: Database not found: {db_path}")


@app.command()
def create() -> None:
    """Create database schema and run migrations."""
    _create_schema()


@app.command()
def drop(
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation"),
) -> None:
    """Drop database."""
    if not confirm:
        db_path = get_db_path()
        typer.confirm(f"Drop database '{db_path}'? This cannot be undone!", abort=True)
    _drop_db()


@app.command()
def local() -> None:
    """Reset and initialize database."""
    print("Resetting and initializing database...")
    _drop_db()
    _create_schema()
    print("PASS: Database ready!")


@app.command()
def run(
    cmd: str = typer.Option(..., "--cmd", help="SQL command to execute"),
) -> None:
    """Execute arbitrary SQL command against database."""
    db_path = get_db_path()
    print(f"Executing SQL on: {db_path}")
    print(f"Command: {cmd}\n")

    if not db_path.exists():
        print("ERROR: Database does not exist.")
        raise typer.Exit(1)

    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute(cmd)

        if cursor.description:
            rows = cursor.fetchall()
            if rows:
                col_names = [desc[0] for desc in cursor.description]
                print(" | ".join(col_names))
                print("-" * (len(" | ".join(col_names))))
                for row in rows:
                    print(" | ".join(str(val) for val in row))
                print(f"\nPASS: Returned {len(rows)} row(s)")
            else:
                print("PASS: Query executed (0 rows)")
        else:
            conn.commit()
            print("PASS: Command executed")

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        raise typer.Exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    app()
```

### Multitenant Mode

The multitenant template adds `--domain` flag to each command and resolves per-domain data directories. Add `DEFAULT_DOMAIN = "localhost"` at the top and add `domain` parameter to `get_db_path()`:

```python
DEFAULT_DOMAIN = "localhost"


def get_data_dir_for_domain(domain: str) -> Path:
    """Get data directory for a specific domain."""
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir) / domain
    return Path(__file__).parent / "mcc" / "domains" / domain


def get_db_path(domain: str = DEFAULT_DOMAIN) -> Path:
    """Get database path for domain."""
    data_dir = get_data_dir_for_domain(domain)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "data.db"


# Commands use --domain flag:
@app.command()
def create(
    domain: str = typer.Option(DEFAULT_DOMAIN, "--domain", "-d", help="Domain name"),
) -> None:
    """Create database schema."""
    _create_schema(domain)
```

## Schema Template

Create `src/shared/db/scripts/create_schema.sql`:

```sql
-- Migrations tracking table (required for migration support)
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example tables below (customize for your project)

-- Users/Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);

-- Sessions table for authentication
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL UNIQUE,
    admin_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_admin_id ON sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
```

## Migration Examples

### Migration: `001_add_can_edit_users.sql`

```sql
-- Migration: 001_add_can_edit_users
-- Add can_edit_users column to admins table for user management permissions

ALTER TABLE admins ADD COLUMN can_edit_users INTEGER NOT NULL DEFAULT 0;
```

### Migration: `002_add_must_change_password.sql`

```sql
-- Migration: 002_add_must_change_password
-- Add must_change_password column to admins table

ALTER TABLE admins ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
```

## DBContext Class

Create `src/shared/db/db_context.py` for database session management.

### Single-Tenant Mode

```python
"""Database context manager for SQLite session management with WAL mode."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine, event
from sqlmodel import Session, create_engine

from shared.common import get_data_dir


class DBContext:
    """Database context manager for session handling."""

    _engine: Engine | None = None

    @staticmethod
    def _get_db_path() -> Path:
        """Get database path."""
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "data.db"

    @staticmethod
    def _get_engine() -> Engine:
        """Get or create database engine with WAL mode."""
        if DBContext._engine is None:
            db_path = DBContext._get_db_path()
            database_url = f"sqlite:///{db_path}"
            DBContext._engine = create_engine(
                database_url,
                echo=False,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
            )

            @event.listens_for(DBContext._engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()

        return DBContext._engine

    @staticmethod
    def dispose_engine() -> None:
        """Dispose cached engine to free database connections."""
        if DBContext._engine is not None:
            DBContext._engine.dispose()
            DBContext._engine = None

    @staticmethod
    @contextmanager
    def get_session() -> Generator[Session, None, None]:
        """Get a database session with automatic transaction management."""
        engine = DBContext._get_engine()

        with Session(engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
```

### Multitenant Mode

For multitenant applications, use instance-based DBContext with per-domain engines:

```python
"""Database context manager for SQLite with domain-based multitenancy."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine, event
from sqlmodel import Session, create_engine

from shared.common import get_directory_for_domain


class DBContext:
    """Database context manager with domain-based multitenancy."""

    _engines: dict[str, Engine] = {}

    def __init__(self, domain: str = "localhost") -> None:
        self.domain = domain

    def _get_db_path(self) -> Path:
        """Get database path for current domain."""
        db_dir = get_directory_for_domain(self.domain)
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "data.db"

    def _get_engine(self) -> Engine:
        """Get or create database engine for current domain."""
        if self.domain not in DBContext._engines:
            db_path = self._get_db_path()
            database_url = f"sqlite:///{db_path}"
            engine = create_engine(
                database_url,
                echo=False,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
            )

            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA busy_timeout=5000")
                cursor.close()

            DBContext._engines[self.domain] = engine

        return DBContext._engines[self.domain]

    @classmethod
    def dispose_engines(cls) -> None:
        """Dispose all cached engines."""
        for engine in cls._engines.values():
            engine.dispose()
        cls._engines.clear()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic transaction management."""
        engine = self._get_engine()

        with Session(engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
```

## Common Utilities

Create `src/shared/common.py` for shared utilities.

### Single-Tenant Mode

```python
"""Common utilities shared across modules."""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get the data directory path.

    In production, uses DATA_DIR environment variable.
    In development, defaults to mcc/data relative to project root.
    """
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir)
    return Path(__file__).parent.parent.parent.absolute() / "mcc" / "data"
```

### Multitenant Mode

```python
"""Common utilities shared across modules."""

import os
from pathlib import Path


def get_directory_for_domain(domain: str) -> Path:
    """Get the directory path for a domain's data."""
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir) / domain
    return Path(__file__).parent.parent.parent.absolute() / "mcc" / "domains" / domain
```

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "typer>=0.9.0",
]
```

## README.md Section

Add to project README.md:

```markdown
## Database

This project uses **SQLite** for data storage. Database file is stored at `mcc/data/data.db`.

### Setup

```bash
# Create database schema
uv run python setup_db.py create

# Reset and initialize
uv run python setup_db.py local

# Drop database
uv run python setup_db.py drop --confirm

# Execute SQL command
uv run python setup_db.py run --cmd "SELECT * FROM admins"
```

### Migrations

Migrations are stored in `src/shared/db/scripts/migrations/` and run automatically during schema creation.

To add a new migration:
1. Create `src/shared/db/scripts/migrations/NNN_description.sql`
2. Run `uv run python setup_db.py create` to apply
```

## SQLite Type Mappings

| Python Type | SQLite Type | Notes |
|-------------|-------------|-------|
| `int` | `INTEGER` | |
| `str` | `TEXT` | |
| `float` | `REAL` | |
| `bool` | `INTEGER` | 0=False, 1=True |
| `datetime` | `TIMESTAMP` | Stored as TEXT |
| `bytes` | `BLOB` | |

## Index Best Practices

```sql
-- Single column index for lookups
CREATE INDEX IF NOT EXISTS idx_table_column ON table(column);

-- Composite index for multi-column queries
CREATE INDEX IF NOT EXISTS idx_table_col1_col2 ON table(col1, col2);

-- Partial index for filtered queries
CREATE INDEX IF NOT EXISTS idx_table_active ON table(column) WHERE is_active = 1;
```

## Foreign Key Patterns

```sql
-- Cascade delete (remove child when parent deleted)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE

-- Set null (keep child, set FK to null)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE SET NULL

-- Restrict (prevent parent deletion if children exist)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE RESTRICT
```
