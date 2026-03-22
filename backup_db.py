#!/usr/bin/env python3
"""Database backup script with retention policy.

Creates gzipped pg_dump backups and enforces retention:
- Daily: keep last 30 days
- Monthly: keep last day of each month for 12 months
"""

import calendar
import gzip
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import typer

app = typer.Typer(help="Database backup with retention cleanup")

PROJECT_NAME = "ana-auth"
DEFAULT_BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "backup"))
DAILY_RETENTION_DAYS = 30
MONTHLY_RETENTION_DAYS = 365


def is_last_day_of_month(d: date) -> bool:
    """Check if a date is the last day of its month."""
    _, last_day = calendar.monthrange(d.year, d.month)
    return d.day == last_day


def parse_backup_date(filename: str) -> date | None:
    """Extract date from backup filename (YYYY-MM-DD-suffix.gz)."""
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-", filename)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def should_keep(backup_date: date, today: date) -> bool:
    """Determine if a backup file should be kept based on retention policy."""
    age = (today - backup_date).days

    # Keep daily backups within retention period
    if age <= DAILY_RETENTION_DAYS:
        return True

    # Keep monthly snapshots (last day of month) within yearly retention
    if is_last_day_of_month(backup_date) and age <= MONTHLY_RETENTION_DAYS:
        return True

    return False


def cleanup_backups(backup_dir: Path, today: date | None = None) -> list[Path]:
    """Remove backup files that don't match retention policy. Returns deleted files."""
    if today is None:
        today = date.today()

    deleted: list[Path] = []
    for f in sorted(backup_dir.glob("*.gz")):
        backup_date = parse_backup_date(f.name)
        if backup_date is None:
            continue
        if not should_keep(backup_date, today):
            print(f"Deleting expired backup: {f.name}")
            f.unlink()
            deleted.append(f)

    return deleted


@app.command()
def backup(
    suffix: str = typer.Argument(..., help="Schema suffix (e.g., main)"),
    backup_dir: Path = typer.Option(
        DEFAULT_BACKUP_DIR, "--backup-dir", help="Backup output directory"
    ),
) -> None:
    """Create a gzipped pg_dump backup and run retention cleanup."""
    schema_name = f"{PROJECT_NAME}-{suffix}"
    today = date.today()
    output_file = backup_dir / f"{today.isoformat()}-{suffix}.gz"

    backup_dir.mkdir(parents=True, exist_ok=True)

    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")
    db_name = os.environ.get("DB_NAME", "postgres")

    cmd = [
        "pg_dump",
        "-h", db_host,
        "-p", db_port,
        "-U", db_user,
        "-n", schema_name,
        db_name,
    ]

    print(f"Backing up schema '{schema_name}' to {output_file}")

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            env=env,
        )
    except FileNotFoundError:
        print("Error: pg_dump not found. Is PostgreSQL client installed?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: pg_dump failed: {e.stderr.decode().strip()}")
        sys.exit(1)

    with gzip.open(output_file, "wb") as f:
        f.write(result.stdout)

    size_kb = output_file.stat().st_size / 1024
    print(f"Backup complete: {output_file} ({size_kb:.1f} KB)")

    # Run retention cleanup
    deleted = cleanup_backups(backup_dir)
    if deleted:
        print(f"Retention cleanup: removed {len(deleted)} expired backup(s)")
    else:
        print("Retention cleanup: no expired backups to remove")


if __name__ == "__main__":
    app()
