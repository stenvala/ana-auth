#!/usr/bin/env python3
"""Database setup script for ana-auth using PostgreSQL schema-based multitenancy."""

import hashlib
import os
import sys
from pathlib import Path

import psycopg2
import psycopg2.extensions
import typer
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = typer.Typer(help="Setup PostgreSQL database for ana-auth")

PROJECT_NAME = "ana-auth"

SCHEMA_DIR = Path(__file__).parent / "src" / "shared" / "db" / "schema"
MIGRATIONS_DIR = Path(__file__).parent / "src" / "shared" / "db" / "migrations"


def connect_to_postgres() -> psycopg2.extensions.connection:
    """Connect to PostgreSQL database using environment or defaults."""
    try:
        return psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
        )
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)


def execute_sql_file(
    conn: psycopg2.extensions.connection,
    schema_name: str,
    file_path: Path,
    description: str,
) -> bool:
    """Execute SQL file in specified schema."""
    if not file_path.exists():
        print(f"{description} file not found at: {file_path}")
        return False

    sql_content = file_path.read_text()
    cursor = conn.cursor()
    cursor.execute(f'SET search_path = "{schema_name}";')
    cursor.execute(sql_content)
    conn.commit()
    cursor.close()
    print(f"{description} executed successfully.")
    return True


def _create(schema_suffix: str) -> None:
    """Create schema with tables and admin user."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Creating schema: {schema_name}")

    conn = connect_to_postgres()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')
        cursor.close()

        execute_sql_file(
            conn,
            schema_name,
            SCHEMA_DIR / "create_schema.sql",
            "Schema creation",
        )

        execute_sql_file(
            conn,
            schema_name,
            SCHEMA_DIR / "ensure_admin.sql",
            "Admin user creation",
        )

        print(f"Schema created: {schema_name}")
    except psycopg2.Error as e:
        print(f"Error creating schema: {e}")
        sys.exit(1)
    finally:
        conn.close()


def _drop(schema_suffix: str) -> None:
    """Drop schema with CASCADE."""
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
        sys.exit(1)
    finally:
        conn.close()


def _update(schema_suffix: str) -> None:
    """Apply pending migrations to schema."""
    schema_name = f"{PROJECT_NAME}-{schema_suffix}"
    print(f"Updating schema: {schema_name}")

    if not MIGRATIONS_DIR.exists():
        print("No migrations directory found.")
        return

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        print("No migration files found.")
        return

    conn = connect_to_postgres()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')

        # Ensure _deployment_log exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _deployment_log (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                checksum VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Get already applied migrations
        cursor.execute("SELECT filename, checksum FROM _deployment_log;")
        applied = {row[0]: row[1] for row in cursor.fetchall()}

        pending_count = 0
        for migration_file in migration_files:
            filename = migration_file.name
            content = migration_file.read_text()
            checksum = hashlib.sha256(content.encode()).hexdigest()

            if filename in applied:
                if applied[filename] != checksum:
                    print(
                        f"CHECKSUM MISMATCH for {filename}! "
                        f"Expected {applied[filename]}, got {checksum}. "
                        "Aborting."
                    )
                    sys.exit(1)
                continue

            print(f"Applying migration: {filename}")
            cursor.execute(f'SET search_path = "{schema_name}";')
            cursor.execute(content)
            cursor.execute(
                "INSERT INTO _deployment_log (filename, checksum) VALUES (%s, %s);",
                (filename, checksum),
            )
            pending_count += 1
            print(f"Migration {filename} applied successfully.")

        if pending_count == 0:
            print("Schema is up to date. No migrations to apply.")
        else:
            print(f"Applied {pending_count} migration(s).")

        cursor.close()
    except psycopg2.Error as e:
        print(f"Error applying migrations: {e}")
        sys.exit(1)
    finally:
        conn.close()


@app.command()
def create(schema_suffix: str = typer.Argument(..., help="Schema suffix")) -> None:
    """Create schema with tables and admin user."""
    _create(schema_suffix)


@app.command()
def drop(
    schema_suffix: str = typer.Argument(..., help="Schema suffix"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation"),
) -> None:
    """Drop schema with CASCADE."""
    if not confirm:
        typer.confirm(
            f"Drop schema '{PROJECT_NAME}-{schema_suffix}'? This cannot be undone!",
            abort=True,
        )
    _drop(schema_suffix)


@app.command()
def update(schema_suffix: str = typer.Argument(..., help="Schema suffix")) -> None:
    """Apply pending migrations to schema."""
    _update(schema_suffix)


@app.command()
def main() -> None:
    """Reset main schema (drop and recreate)."""
    print("Resetting main database...")
    _drop("main")
    _create("main")
    print("Main database ready!")


@app.command()
def e2e() -> None:
    """Reset e2e schema (drop and recreate)."""
    print("Resetting e2e database...")
    _drop("e2e")
    _create("e2e")
    print("E2E database ready!")


@app.command(name="local-update")
def local_update() -> None:
    """Run update on main schema with local DB config."""
    _update("main")


@app.command()
def run(
    schema_suffix: str = typer.Option(..., "--schema-suffix", help="Schema suffix"),
    cmd: str = typer.Option(..., "--cmd", help="SQL command to execute"),
) -> None:
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
