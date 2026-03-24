#!/usr/bin/env python3
"""Deployment script for ana-auth.

Handles symlink-based versioned deployments for API and UI.
Runs on the remote server after CI/CD transfers the build output.

Usage:
  uv run mcc_deploy.py --stage prod

Exit Code:
  0 - Deployment succeeded
  1 - Deployment failed
"""

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import typer
import yaml

from mcc_common import run

PROJECT_NAME = "ana-auth"
CRON_MARKER = "MCC-AUTH"


def load_conf(cwd: Path, conf_file: str = "conf.yml") -> dict:
    """Load deployment configuration from the given conf file."""
    conf_path = cwd / conf_file
    if not conf_path.exists():
        raise FileNotFoundError(f"{conf_file} not found in {cwd}")
    raw = yaml.safe_load(conf_path.read_text())

    # Resolve {{REMOTE_BASE}} templates
    remote_base = raw.get("REMOTE_BASE", "")
    resolved = {}
    for key, value in raw.items():
        if isinstance(value, str):
            resolved[key] = value.replace("{{REMOTE_BASE}}", remote_base)
        else:
            resolved[key] = value
    return resolved


def cleanup_old_versions(base_dir: Path, keep_count: int) -> None:
    """Clean up old version directories, keeping only N most recent."""
    dirs = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("vrs-")],
        key=lambda p: p.name,
        reverse=True,
    )
    for old_dir in dirs[keep_count:]:
        print(f"Removing old version: {old_dir.name}", flush=True)
        shutil.rmtree(old_dir)


def copy_api_files(cwd: Path, version_dir: Path) -> None:
    """Copy API and shared source to the version directory."""
    shutil.copytree(cwd / "src" / "api", version_dir / "api")
    print("Copied api/", flush=True)

    shutil.copytree(cwd / "src" / "shared", version_dir / "shared")
    print("Copied shared/", flush=True)


def copy_ui_files(cwd: Path, version_dir: Path) -> None:
    """Copy UI build contents into the version directory."""
    ui_src = cwd / "ui-dist"
    if ui_src.exists():
        shutil.copytree(ui_src, version_dir / "ui-dist", dirs_exist_ok=True)
        print("Copied ui-dist/", flush=True)
    else:
        print("WARNING: ui-dist not found in build output", flush=True)


def sync_virtual_environment(cwd: Path, deployment_path: Path) -> None:
    """Copy pyproject.toml and uv.lock to deployment path and sync venv."""
    shutil.copy2(cwd / "pyproject.toml", deployment_path / "pyproject.toml")
    shutil.copy2(cwd / "uv.lock", deployment_path / "uv.lock")
    print("Copied pyproject.toml and uv.lock to deployment path", flush=True)

    print("Syncing virtual environment...", flush=True)
    run(["uv", "sync", "--frozen"], cwd=deployment_path)
    print("Virtual environment synchronized", flush=True)


def update_symlinks(
    deployment_path: Path,
    api_version_dir: Path,
    ui_version_dir: Path,
) -> None:
    """Update symlinks to point to new version directories."""
    api_link = deployment_path / "current-api"
    if api_link.exists() or api_link.is_symlink():
        api_link.unlink()
    api_link.symlink_to(api_version_dir)
    print(f"Updated symlink: current-api -> {api_version_dir}", flush=True)

    ui_link = deployment_path / "current-ui"
    if ui_link.exists() or ui_link.is_symlink():
        ui_link.unlink()
    ui_link.symlink_to(ui_version_dir)
    print(f"Updated symlink: current-ui -> {ui_version_dir}", flush=True)


def setup_database(cwd: Path, conf: dict) -> None:
    """Create schema, apply migrations, and ensure admin user.

    Uses setup_db.py which is included in the build output.
    Sets DB environment variables from the stage config.
    """
    schema_suffix = conf["DB_SCHEMA_SUFFIX"]
    print(f"\nSetting up database for schema suffix: {schema_suffix}", flush=True)

    # Set DB environment for setup_db.py
    db_env = os.environ.copy()
    db_env["DB_HOST"] = conf["DB_HOST"]
    db_env["DB_PORT"] = str(conf["DB_PORT"])
    db_env["DB_USER"] = conf["DB_USER"]
    db_env["DB_PASSWORD"] = conf["DB_PASSWORD"]
    db_env["DB_NAME"] = conf.get("DB_NAME", "postgres")

    setup_db = cwd / "setup_db.py"

    # Create schema and tables
    print("Creating schema (if not exists)...", flush=True)
    run(
        ["uv", "run", "python", str(setup_db), "create", schema_suffix],
        env=db_env,
    )

    # Apply pending migrations
    print("Applying pending migrations...", flush=True)
    run(
        ["uv", "run", "python", str(setup_db), "update", schema_suffix],
        env=db_env,
    )

    print("Database setup complete.", flush=True)


def deploy_cron_jobs(conf: dict) -> None:
    """Deploy cron jobs using marker-based crontab management."""
    cron_jobs_raw = conf.get("CRON_JOBS", "")
    if isinstance(cron_jobs_raw, str):
        cron_jobs = cron_jobs_raw.strip()
    else:
        cron_jobs = ""

    if not cron_jobs:
        print("No cron jobs to deploy", flush=True)
        return

    print("Deploying cron jobs...", flush=True)

    # Read existing crontab
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

    print("Crontab before:", flush=True)
    run(["bash", "-c", "crontab -l 2>/dev/null || echo '(no crontab)'"])

    subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)

    print("Crontab after:", flush=True)
    run(["crontab", "-l"])
    print("Cron jobs deployed.", flush=True)


def deploy_backup_script(cwd: Path, deployment_path: Path) -> None:
    """Copy backup_db.py to deployment path."""
    backup_script = cwd / "backup_db.py"
    if backup_script.exists():
        shutil.copy2(backup_script, deployment_path / "backup_db.py")
        print("Deployed backup_db.py", flush=True)


def setup_permissions(
    deployment_path: Path,
    dir_user: str,
    dir_group: str,
) -> None:
    """Set up proper file permissions."""
    print("Setting up permissions...", flush=True)

    # Python executable permissions
    venv_python = deployment_path / ".venv" / "bin" / "python"
    if venv_python.is_symlink():
        python_path = venv_python.resolve()
        python_dir = str(python_path.parent)
        run(["sudo", "chmod", "-R", "o+rx", python_dir + "/"])

    run(["sudo", "chmod", "o+x", str(deployment_path.parent) + "/"])
    run(["sudo", "chmod", "o+x", str(deployment_path) + "/"])

    # Versions directory (www-data needs to read API/UI files)
    versions_dir = deployment_path / "versions"
    if versions_dir.exists():
        run(["sudo", "chown", "-R", f"{dir_user}:{dir_group}", str(versions_dir)])
        run(["sudo", "chmod", "-R", "g+rw", str(versions_dir)])

    # Logs directory
    logs_dir = deployment_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    run(["sudo", "chown", "-R", f"{dir_user}:{dir_group}", str(logs_dir)])
    run(["sudo", "chmod", "g+rw", str(logs_dir)])

    # Backup directory (owned by deployer user, not www-data)
    backup_dir = deployment_path / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Virtual environment permissions
    venv_dir = deployment_path / ".venv"
    if venv_dir.exists():
        run(["sudo", "chown", "-R", f"{dir_user}:{dir_group}", str(venv_dir)])
        run(["sudo", "chmod", "-R", "g+rw", str(venv_dir)])
        run(["sudo", "chmod", "-R", "g+rx", str(venv_dir / "bin")])


def restart_service(service_name: str) -> None:
    """Restart the systemd service and verify it started."""
    print(f"Restarting service {service_name}...", flush=True)
    run(["sudo", "/bin/systemctl", "restart", service_name])

    print("Waiting 5 seconds for service to start...", flush=True)
    time.sleep(5)
    run(["sudo", "/bin/systemctl", "status", service_name])


def smoke_test(conf: dict) -> None:
    """Run health checks against the deployed service (local port and public domain)."""
    port = conf["API_PORT"]
    domain = conf.get("DOMAIN", "")
    urls = [
        f"http://127.0.0.1:{port}/api/health",
        f"https://{domain}/api/health",
        f"https://{domain}/",
    ]

    for url in urls:
        print(f"Smoke test: {url}", flush=True)
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
                    print(
                        f"Health check passed: {result.stdout.strip()}", flush=True
                    )
                    break
            except subprocess.TimeoutExpired:
                pass
            if i < max_retries - 1:
                print(f"  Retry {i + 1}/{max_retries}...", flush=True)
                time.sleep(2)
        else:
            raise RuntimeError(
                f"Health check failed after {max_retries} retries: {url}"
            )


def clone_prod_to_dev(prod_conf: dict, dev_conf: dict) -> None:
    """Clone prod schema data to dev schema via PostgreSQL.

    Drops and recreates the dev schema, copies all tables, data,
    and sequences from prod. Restarts the dev service after.
    """
    import psycopg2
    import psycopg2.extensions
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    prod_schema = f"{PROJECT_NAME}-{prod_conf['DB_SCHEMA_SUFFIX']}"
    dev_schema = f"{PROJECT_NAME}-{dev_conf['DB_SCHEMA_SUFFIX']}"
    dev_service = dev_conf.get("SERVICE_NAME", "ana-auth-dev.service")

    print(f"\nCloning {prod_schema} -> {dev_schema}", flush=True)

    # Stop dev service
    print(f"Stopping {dev_service}...", flush=True)
    run(["sudo", "/bin/systemctl", "stop", dev_service])
    time.sleep(5)

    conn = psycopg2.connect(
        host=prod_conf["DB_HOST"],
        port=int(prod_conf["DB_PORT"]),
        database=prod_conf.get("DB_NAME", "postgres"),
        user=prod_conf["DB_USER"],
        password=prod_conf["DB_PASSWORD"],
    )
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
            cursor.execute(
                f'CREATE TABLE "{dev_schema}"."{table}" '
                f'(LIKE "{prod_schema}"."{table}" INCLUDING ALL);'
            )
            cursor.execute(
                f'INSERT INTO "{dev_schema}"."{table}" '
                f'SELECT * FROM "{prod_schema}"."{table}";'
            )
            print(f"  Copied table: {table}", flush=True)

        # Copy sequences
        cursor.execute(
            "SELECT sequence_name FROM information_schema.sequences "
            "WHERE sequence_schema = %s;",
            (prod_schema,),
        )
        for (seq_name,) in cursor.fetchall():
            cursor.execute(
                f'SELECT last_value FROM "{prod_schema}"."{seq_name}";'
            )
            last_val = cursor.fetchone()[0]
            cursor.execute(
                f"SELECT setval('\"{dev_schema}\".\"{seq_name}\"', %s);",
                (last_val,),
            )

        cursor.close()
        print(f"\nClone complete: {prod_schema} -> {dev_schema}", flush=True)
    except psycopg2.Error as e:
        print(f"Clone error: {e}", flush=True)
        sys.exit(1)
    finally:
        conn.close()

    # Start dev service
    print(f"Starting {dev_service}...", flush=True)
    run(["sudo", "/bin/systemctl", "start", dev_service])
    time.sleep(5)
    run(["sudo", "/bin/systemctl", "status", dev_service])


def deploy(keep_versions: int, conf: dict) -> None:
    """Core deployment logic."""
    cwd = Path.cwd()
    stage = conf.get("STAGE", "unknown")
    deployment_path = Path(conf["REMOTE_BASE"])
    service_name = conf.get("SERVICE_NAME", "ana-auth.service")
    dir_user = conf.get("DIR_USER", "www-data")
    dir_group = conf.get("DIR_GROUP", "stenvala")

    deployment_path.mkdir(parents=True, exist_ok=True)
    versions_path = deployment_path / "versions"
    versions_path.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
    version_name = f"vrs-{timestamp}"
    version_dir = versions_path / version_name

    print(f"Deploying version {version_name} to {deployment_path}...", flush=True)

    # Log build info if available
    build_info_path = cwd / "build_info.yml"
    if build_info_path.exists():
        info = yaml.safe_load(build_info_path.read_text())
        print(
            f"Deploying build from {info.get('git_branch', '?')} "
            f"@ {info.get('git_commit', '?')[:8]}",
            flush=True,
        )

    # Copy files to version directory
    version_dir.mkdir(parents=True)
    copy_api_files(cwd, version_dir)
    copy_ui_files(cwd, version_dir)

    # Sync virtual environment
    sync_virtual_environment(cwd, deployment_path)

    # Update symlinks
    update_symlinks(deployment_path, version_dir, version_dir / "ui-dist")

    # Database operations
    setup_database(cwd, conf)

    # Deploy backup script
    deploy_backup_script(cwd, deployment_path)

    # Deploy cron jobs (prod only)
    if stage == "prod":
        deploy_cron_jobs(conf)

    # Permissions and cleanup
    setup_permissions(deployment_path, dir_user, dir_group)
    cleanup_old_versions(versions_path, keep_versions)

    # Restart service
    restart_service(service_name)

    print(f"Deployment succeeded: {version_name}", flush=True)

    # Smoke tests
    smoke_test(conf)


def main(
    stage: str = typer.Option(
        ..., help="Deployment stage (prod, dev, clone-prod-to-dev, etc.)"
    ),
) -> None:
    """CLI entry point. Reads mcc_config.yml for stage parameters and the correct conf file."""
    try:
        cwd = Path.cwd()
        config_path = Path("mcc_config.yml")
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        stage_config = config["deploy"][stage]
        params = stage_config.get("parameters", {})

        if stage == "clone-prod-to-dev":
            prod_conf = load_conf(cwd / "mcc", params.get("conf-source", "conf-prod.yml"))
            dev_conf = load_conf(cwd / "mcc", params.get("conf-target", "conf-dev.yml"))
            clone_prod_to_dev(prod_conf, dev_conf)
            return

        conf_file = params.get("conf", "conf.yml")
        conf = load_conf(cwd / "mcc", conf_file)
        keep_versions = params.get("keep_builds", 10)

        deploy(keep_versions, conf)

    except Exception as e:
        print(f"Deployment failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("Starting deployment", flush=True)
    app = typer.Typer()
    app.command()(main)
    app()
    print("Finished deployment", flush=True)
