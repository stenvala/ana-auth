#!/usr/bin/env python3
"""MCC deploy script for ana-auth.

Runs on the remote server from within the output/ directory.
Handles versioned deployments, database setup, and service management.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extensions
import typer
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from mcc_common import run
from mcc_config import load_config

app = typer.Typer(help="Deploy ana-auth to remote server")

PROJECT_NAME = "ana-auth"
DEPLOY_DIR = Path(__file__).parent
CRON_MARKER = "MCC-AUTH"


def _get_config(stage: str) -> dict[str, str]:
    """Load stage configuration."""
    return load_config(stage, config_dir=DEPLOY_DIR / "mcc")


def _connect_db(config: dict[str, str]) -> psycopg2.extensions.connection:
    """Connect to PostgreSQL using stage config."""
    return psycopg2.connect(
        host=config["DB_HOST"],
        port=int(config["DB_PORT"]),
        database=config.get("DB_NAME", "postgres"),
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
    )


def _create_versioned_dir(config: dict[str, str]) -> Path:
    """Create a versioned deployment directory."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    vrs_dir = Path(config["REMOTE_BASE"]) / f"vrs-{timestamp}"
    vrs_dir.mkdir(parents=True)
    print(f"Created version directory: {vrs_dir}")
    return vrs_dir


def _deploy_files(vrs_dir: Path) -> None:
    """Copy API and UI files to the versioned directory."""
    # API source
    api_src = DEPLOY_DIR / "src"
    if api_src.exists():
        shutil.copytree(api_src, vrs_dir / "src", dirs_exist_ok=True)

    # UI dist
    ui_dist = DEPLOY_DIR / "ui-dist"
    if ui_dist.exists():
        shutil.copytree(ui_dist, vrs_dir / "ui-dist", dirs_exist_ok=True)

    # pyproject.toml and uv.lock for venv sync
    for f in ["pyproject.toml", "uv.lock"]:
        src = DEPLOY_DIR / f
        if src.exists():
            shutil.copy2(src, vrs_dir / f)

    print(f"Files deployed to {vrs_dir}")


def _sync_venv(config: dict[str, str]) -> None:
    """Sync virtual environment in the deployment base."""
    base = Path(config["REMOTE_BASE"])
    venv_path = base / ".venv"
    if not venv_path.exists():
        run(["uv", "venv", str(venv_path)])
    run(["uv", "sync", "--frozen"], cwd=str(base))


def _setup_database(config: dict[str, str]) -> None:
    """Create schema if not exists and apply migrations."""
    schema_name = f"{PROJECT_NAME}-{config['DB_SCHEMA_SUFFIX']}"
    print(f"\nSetting up database schema: {schema_name}")

    conn = _connect_db(config)
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create schema if not exists
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')

        # Create deployment log table
        cursor.execute(f'SET search_path = "{schema_name}";')
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS _deployment_log (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL UNIQUE,
                checksum VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        )

        # Apply schema creation SQL (checksum-tracked)
        schema_sql = DEPLOY_DIR / "db" / "schema" / "create_schema.sql"
        if schema_sql.exists():
            _apply_sql_if_changed(cursor, schema_name, schema_sql, "create_schema.sql")

        # Apply migrations
        migrations_dir = DEPLOY_DIR / "db" / "migrations"
        if migrations_dir.exists():
            for migration in sorted(migrations_dir.glob("*.sql")):
                _apply_sql_if_changed(cursor, schema_name, migration, migration.name)

        cursor.close()
        print("Database setup complete.")
    except psycopg2.Error as e:
        print(f"Database setup error: {e}")
        sys.exit(1)
    finally:
        conn.close()


def _apply_sql_if_changed(
    cursor, schema_name: str, sql_path: Path, filename: str
) -> None:
    """Apply SQL file if its checksum has changed."""
    content = sql_path.read_text()
    checksum = hashlib.sha256(content.encode()).hexdigest()

    cursor.execute(f'SET search_path = "{schema_name}";')
    cursor.execute(
        "SELECT checksum FROM _deployment_log WHERE filename = %s;",
        (filename,),
    )
    row = cursor.fetchone()

    if row and row[0] == checksum:
        print(f"  {filename}: already up to date (skipped)")
        return

    print(f"  {filename}: applying...")
    cursor.execute(f'SET search_path = "{schema_name}";')
    cursor.execute(content)

    if row:
        cursor.execute(
            "UPDATE _deployment_log SET checksum = %s, applied_at = CURRENT_TIMESTAMP WHERE filename = %s;",
            (checksum, filename),
        )
    else:
        cursor.execute(
            "INSERT INTO _deployment_log (filename, checksum) VALUES (%s, %s);",
            (filename, checksum),
        )


def _ensure_admin(config: dict[str, str]) -> None:
    """Ensure master admin user exists."""
    schema_name = f"{PROJECT_NAME}-{config['DB_SCHEMA_SUFFIX']}"
    ensure_sql = DEPLOY_DIR / "mcc" / "ensure_admin.sql"
    if not ensure_sql.exists():
        ensure_sql = DEPLOY_DIR / "db" / "schema" / "ensure_admin.sql"
    if not ensure_sql.exists():
        print("WARNING: ensure_admin.sql not found, skipping admin user setup")
        return

    conn = _connect_db(config)
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')
        cursor.execute(ensure_sql.read_text())
        cursor.close()
        print("Admin user ensured.")
    except psycopg2.Error as e:
        print(f"Error ensuring admin: {e}")
        sys.exit(1)
    finally:
        conn.close()


def _update_symlinks(config: dict[str, str], vrs_dir: Path) -> None:
    """Update current-api and current-ui symlinks."""
    base = Path(config["REMOTE_BASE"])

    api_link = base / "current-api"
    ui_link = base / "current-ui"

    api_target = vrs_dir / "src"
    ui_target = vrs_dir / "ui-dist"

    for link, target in [(api_link, api_target), (ui_link, ui_target)]:
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target)
        print(f"Symlink: {link} -> {target}")


def _deploy_cron_jobs(config: dict[str, str]) -> None:
    """Deploy cron jobs for prod stage only."""
    cron_jobs = config.get("CRON_JOBS", "").strip()
    if not cron_jobs:
        print("No crong jobs")
        return

    print("Deploying cron jobs...")
    # Read existing crontab, filter out our marker lines
    result = subprocess.run(
        ["crontab", "-l"], capture_output=True, text=True, check=False
    )
    existing = result.stdout if result.returncode == 0 else ""

    # Remove existing MCC-AUTH entries
    lines = [line for line in existing.splitlines() if CRON_MARKER not in line]

    # Add new cron jobs with marker
    for job in cron_jobs.strip().splitlines():
        job = job.strip()
        if job:
            lines.append(f"{job}  # {CRON_MARKER}")

    new_crontab = "\n".join(lines) + "\n"
    subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
    print("Cron jobs deployed.")


def _set_permissions(config: dict[str, str]) -> None:
    """Set file permissions for www-data access."""
    base = Path(config["REMOTE_BASE"])
    run(["chmod", "-R", "g+rw", str(base)])
    run(["chown", "-R", "www-data:stenvala", str(base)], check=False)


def _restart_service(config: dict[str, str]) -> None:
    """Restart the systemd service."""
    service = config["SERVICE_NAME"]
    print(f"Restarting {service}...")
    run(["sudo", "/bin/systemctl", "restart", service])


def _smoke_test(config: dict[str, str]) -> None:
    """Run health check against the deployed service."""
    port = config["API_PORT"]
    url = f"http://127.0.0.1:{port}/api/health"
    print(f"Smoke test: {url}")

    max_retries = 10
    for i in range(max_retries):
        try:
            result = subprocess.run(
                ["curl", "-sf", url],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if result.returncode == 0:
                print(f"Health check passed: {result.stdout.strip()}")
                return
        except subprocess.TimeoutExpired:
            pass
        if i < max_retries - 1:
            time.sleep(2)

    print("WARNING: Health check failed after retries")
    sys.exit(1)


def _cleanup_old_versions(config: dict[str, str], keep: int = 5) -> None:
    """Remove old version directories, keeping the most recent N."""
    base = Path(config["REMOTE_BASE"])
    versions = sorted(base.glob("vrs-*"), key=lambda p: p.name)
    to_remove = versions[:-keep] if len(versions) > keep else []
    for v in to_remove:
        print(f"Removing old version: {v.name}")
        shutil.rmtree(v)


def _deploy_stage(config: dict[str, str]) -> None:
    """Execute full deployment for a stage."""
    stage = config["STAGE"]
    print(f"\n{'=' * 40}")
    print(f"DEPLOYING: {stage}")
    print(f"{'=' * 40}")

    # Ensure logs directory
    logs_dir = Path(config["REMOTE_BASE"]) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    vrs_dir = _create_versioned_dir(config)
    _deploy_files(vrs_dir)
    _sync_venv(config)
    _setup_database(config)
    _ensure_admin(config)
    _update_symlinks(config, vrs_dir)

    if stage == "prod":
        _deploy_cron_jobs(config)

    _set_permissions(config)
    _restart_service(config)
    _smoke_test(config)
    _cleanup_old_versions(config)

    print(f"\nDeployment to {stage} complete.")


def _clone_prod_to_dev() -> None:
    """Copy prod schema data to dev schema."""
    prod_config = _get_config("prod")
    dev_config = _get_config("dev")

    prod_schema = f"{PROJECT_NAME}-{prod_config['DB_SCHEMA_SUFFIX']}"
    dev_schema = f"{PROJECT_NAME}-{dev_config['DB_SCHEMA_SUFFIX']}"

    print(f"\nCloning {prod_schema} -> {dev_schema}")

    conn = _connect_db(prod_config)
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Drop and recreate dev schema
        cursor.execute(f'DROP SCHEMA IF EXISTS "{dev_schema}" CASCADE;')
        cursor.execute(f'CREATE SCHEMA "{dev_schema}";')

        # Get all tables from prod schema
        cursor.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = %s;",
            (prod_schema,),
        )
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            # Create table structure
            cursor.execute(
                f'CREATE TABLE "{dev_schema}"."{table}" (LIKE "{prod_schema}"."{table}" INCLUDING ALL);'
            )
            # Copy data
            cursor.execute(
                f'INSERT INTO "{dev_schema}"."{table}" SELECT * FROM "{prod_schema}"."{table}";'
            )
            print(f"  Copied table: {table}")

        # Copy sequences
        cursor.execute(
            "SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = %s;",
            (prod_schema,),
        )
        for (seq_name,) in cursor.fetchall():
            cursor.execute(f'SELECT last_value FROM "{prod_schema}"."{seq_name}";')
            last_val = cursor.fetchone()[0]
            cursor.execute(
                f'SELECT setval(\'"{dev_schema}"."{seq_name}"\', %s);',
                (last_val,),
            )

        cursor.close()
        print(f"\nClone complete: {prod_schema} -> {dev_schema}")
    except psycopg2.Error as e:
        print(f"Clone error: {e}")
        sys.exit(1)
    finally:
        conn.close()


@app.command()
def deploy(
    stage: str = typer.Option(
        ..., "--stage", help="Deployment stage (prod, dev, clone-prod-to-dev)"
    ),
) -> None:
    """Deploy ana-auth to the specified stage."""
    if stage == "clone-prod-to-dev":
        _clone_prod_to_dev()
        return

    config = _get_config(stage)
    _deploy_stage(config)


if __name__ == "__main__":
    app()
