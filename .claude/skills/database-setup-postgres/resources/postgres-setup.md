# PostgreSQL Database Setup

PostgreSQL runs in Docker container on port 5432 with default credentials.

## Connection Details

- Host: localhost
- Port: 5432
- Database: postgres
- User: postgres
- Password: postgres

## Schema Naming

Schemas are named as: `<project-name>-<suffix>` (e.g., `my-app-main`, `my-app-e2e`)

## setup_db.py Template

```python
#!/usr/bin/env python3
"""Database setup script using PostgreSQL."""

import glob
import os
import sys

import psycopg2
import typer
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = typer.Typer(help="Setup PostgreSQL database")

# Update this to match your project name
PROJECT_NAME = "my-project"


def connect_to_postgres():
    """Connect to PostgreSQL database."""
    try:
        return psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres",
        )
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)


def execute_sql_file(conn, schema_name: str, file_path: str, description: str):
    """Execute SQL file in specified schema."""
    possible_paths = [
        file_path,
        os.path.join(os.getcwd(), file_path),
        os.path.join(os.path.dirname(__file__), file_path),
    ]

    actual_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            actual_path = path
            break

    if not actual_path:
        print(f"{description} file not found at: {file_path}")
        return False

    with open(actual_path, "r") as f:
        sql_content = f.read()

    cursor = conn.cursor()
    cursor.execute(f'SET search_path = "{schema_name}";')
    cursor.execute(sql_content)
    conn.commit()
    cursor.close()
    print(f"{description} executed successfully.")
    return True


def _create(schema_suffix: str) -> None:
    """Create schema with tables."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Creating schema: {schema_name}")

    conn = connect_to_postgres()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create schema
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')
        cursor.close()

        # Create tables
        execute_sql_file(
            conn,
            schema_name,
            "src/shared/db/scripts/create_schema.sql",
            "Schema creation",
        )
        print(f"Schema created: {schema_name}")

    except psycopg2.Error as e:
        print(f"Error creating schema: {e}")
    finally:
        conn.close()


def _drop(schema_suffix: str) -> None:
    """Drop schema."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Dropping schema: {schema_name}")

    conn = connect_to_postgres()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')
        cursor.close()
        print(f"Schema dropped: {schema_name}")
    except psycopg2.Error as e:
        print(f"Error dropping schema: {e}")
    finally:
        conn.close()


def _demo_data(schema_suffix: str) -> None:
    """Add demo/initial data to schema."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Adding demo data to: {schema_name}")

    conn = connect_to_postgres()
    try:
        # Look for initial data files
        initial_data_files = glob.glob(
            "src/shared/db/scripts/create_initial_data_*.sql"
        )
        if not initial_data_files:
            # Try single demo data file
            demo_file = "src/shared/db/scripts/demo_data.sql"
            if os.path.exists(demo_file):
                execute_sql_file(conn, schema_name, demo_file, "Demo data")
            else:
                print("No demo data files found.")
            return

        for file_path in sorted(initial_data_files):
            execute_sql_file(
                conn,
                schema_name,
                file_path,
                f"Initial data: {os.path.basename(file_path)}",
            )

        print("Demo data added successfully.")
    except psycopg2.Error as e:
        print(f"Error adding demo data: {e}")
    finally:
        conn.close()


@app.command()
def create(schema_suffix: str = typer.Argument(..., help="Schema suffix")):
    """Create schema with tables."""
    _create(schema_suffix)


@app.command()
def drop(
    schema_suffix: str = typer.Argument(..., help="Schema suffix"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation"),
):
    """Drop schema."""
    if not confirm:
        typer.confirm(
            f"Drop schema '{PROJECT_NAME}-{schema_suffix}'? This cannot be undone!",
            abort=True,
        )
    _drop(schema_suffix)


@app.command()
def demo_data(schema_suffix: str = typer.Argument(..., help="Schema suffix")):
    """Add demo data to schema."""
    _demo_data(schema_suffix)


@app.command()
def main_update():
    """Update main database with latest schema."""
    print("Updating main database with latest schema...")
    _create("main")
    print("Main database ready!")


@app.command()
def main():
    """Reset and initialize main database with demo data."""
    print("Resetting and initializing main database...")
    _drop("main")
    _create("main")
    _demo_data("main")
    print("Main database ready!")


@app.command()
def e2e():
    """Reset and initialize e2e database."""
    print("Resetting and initializing e2e database...")
    _drop("e2e")
    _create("e2e")
    print("E2E database ready!")


@app.command()
def run(
    schema_suffix: str = typer.Option(..., "--schema-suffix", help="Schema suffix"),
    cmd: str = typer.Option(..., "--cmd", help="SQL command to execute"),
):
    """Execute arbitrary SQL command against specified schema."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Executing SQL on schema: {schema_name}")
    print(f"Command: {cmd}\n")

    conn = connect_to_postgres()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')
        cursor.execute(cmd)

        if cursor.description:
            rows = cursor.fetchall()
            if rows:
                col_names = [desc[0] for desc in cursor.description]
                print(" | ".join(col_names))
                print("-" * (len(" | ".join(col_names))))
                for row in rows:
                    print(" | ".join(str(val) for val in row))
                print(f"\nReturned {len(rows)} row(s)")
            else:
                print("Query executed successfully (0 rows)")
        else:
            print("Command executed successfully")

        cursor.close()
    except psycopg2.Error as e:
        print(f"Error executing command: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    app()
```

## Basic Schema Template

Create `src/shared/db/scripts/create_schema.sql`:

```sql
-- Add your tables below
-- Example:
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     email VARCHAR(255) NOT NULL UNIQUE,
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
```

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "psycopg2-binary>=2.9.0",
    "typer>=0.9.0",
]
```

## README.md Section

Add to project README.md:

```markdown
## Database

This project uses **PostgreSQL** running in Docker on port 5432.

### Connection Details

- Host: localhost
- Port: 5432
- Database: postgres
- User: postgres
- Password: postgres

### Setup

```bash
# Create main schema
uv run python setup_db.py create main

# Reset and initialize main database with demo data
uv run python setup_db.py main

# Create e2e test database
uv run python setup_db.py e2e

# Drop schema
uv run python setup_db.py drop main --confirm

# Execute SQL command
uv run python setup_db.py run --schema-suffix main --cmd "SELECT * FROM users"
```
```
