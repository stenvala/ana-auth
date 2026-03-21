#!/usr/bin/env python3
"""Deploy API to remote server."""

import time
from pathlib import Path

from fabric import Connection
from invoke import UnexpectedExit

from config_loader import Config, load_config


def get_connection() -> Connection:
    """Get SSH connection using configuration."""
    config = load_config()
    remote_user = config.remote_user
    remote_host = config.remote_host
    return Connection(f"{remote_user}@{remote_host}")


def upload_api_release(
    c: Connection,
    config: Config,
    remote_release_dir: str,
) -> None:
    """Upload API files to remote release directory."""
    local_api_dir = config.local_api_dir
    remote_user = config.remote_user
    remote_host = config.remote_host

    print(f"Creating remote build directory: {remote_release_dir}")
    c.run(f"mkdir -p {remote_release_dir}", echo=True)

    print(f"Uploading API files from {local_api_dir} to {remote_release_dir}")
    c.local(
        f"rsync -r {local_api_dir}/ {remote_user}@{remote_host}:{remote_release_dir}",
        echo=True,
    )


def sync_virtual_environment(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Sync virtual environment with current release dependencies."""
    remote_base = config.remote_base

    print("Copying pyproject.toml and uv.lock to REMOTE_BASE...")
    c.run(f"cp {remote_release_dir}/pyproject.toml {remote_base}/", echo=True)
    c.run(f"cp {remote_release_dir}/uv.lock {remote_base}/", echo=True)

    print("Syncing virtual environment with release dependencies...")
    c.run(f"cd {remote_base} && uv sync --frozen", echo=True)
    print("Virtual environment synchronized")


def update_api_symlink(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Update symlink to point to new API release."""
    symlink = config.api_symlink

    print(f"Updating symlink {symlink} to point to {remote_release_dir}")
    c.run(f"rm -f {symlink}", echo=True)
    c.run(f"ln -s {remote_release_dir} {symlink}", echo=True)


def cleanup_old_api_builds(c: Connection, config: Config) -> None:
    """Remove old API builds keeping only the specified number."""
    remote_builds = config.api_remote_builds
    keep_builds = config.keep_builds

    print("Cleaning up old builds...")
    result = c.run(f"ls -1 {remote_builds}", hide=True)
    dirs = [d for d in result.stdout.strip().split("\n") if d]
    dirs.sort()

    while len(dirs) > keep_builds:
        old = dirs.pop(0)
        print(f"Removing old release: {old}")
        c.run(f"rm -rf {remote_builds}/{old}", echo=True)


def setup_api_permissions(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Set up proper file permissions for API files."""
    remote_base = config.remote_base
    remote_builds = config.api_remote_builds
    dir_user = config.dir_user
    dir_group = config.dir_group

    # If this is not done, after chown old version cleanups don't work
    print("Setting group write permissions on API builds directory")
    c.run(f"sudo chmod -R g+w {remote_builds}", echo=True)

    print(f"Changing ownership of API builds directory to {dir_user}:{dir_group}")
    c.run(f"sudo chown -R {dir_user}:{dir_group} {remote_builds}", echo=True)

    print("Setting group read permissions on API builds directory")
    c.run(f"sudo chmod -R g+r {remote_builds}", echo=True)

    print(f"Changing ownership of new API build to {dir_user}:{dir_group}")
    c.run(f"sudo chown -R {dir_user}:{dir_group} {remote_release_dir}", echo=True)

    print("Setting group read permissions on new API build")
    c.run(f"sudo chmod -R g+r {remote_release_dir}", echo=True)

    # Domains directory (SQLite mode)
    domains_dir = f"{remote_base}/domains"
    try:
        c.run(f"test -d {domains_dir}", hide=True)
        c.run(f"sudo chown -R {dir_user}:{dir_group} {domains_dir}", echo=True)
        c.run(f"sudo chmod -R g+rw {domains_dir}", echo=True)
    except UnexpectedExit:
        pass  # No domains directory

    # Logs directory
    print("Ensuring logs directory exists")
    c.run(f"mkdir -p {remote_base}/logs", echo=True)
    c.run(f"sudo chown {dir_user}:{dir_group} {remote_base}/logs", echo=True)
    c.run(f"sudo chmod g+rw {remote_base}/logs", echo=True)

    # Virtual environment permissions
    c.run(f"sudo chown -R {dir_user}:{dir_group} {remote_base}/.venv", echo=True)
    c.run(f"sudo chmod -R g+rw {remote_base}/.venv", echo=True)
    c.run(f"sudo chmod -R g+rx {remote_base}/.venv/bin", echo=True)


def sync_domain_configs(c: Connection, config: Config) -> None:
    """Copy domain config.yml files to the remote domains directory."""
    domains = config.domains

    # Only for multi-domain SQLite mode
    if not domains:
        return

    remote_base = config.remote_base
    remote_user = config.remote_user
    remote_host = config.remote_host
    local_domains_dir = Path(__file__).parent / "domains"

    print("Syncing domain config files...")

    for domain in domains:
        local_config = local_domains_dir / domain / "config.yml"
        remote_domain_dir = f"{remote_base}/domains/{domain}"

        if local_config.exists():
            print(f"Copying config.yml for domain: {domain}")
            c.run(f"mkdir -p {remote_domain_dir}", echo=True)
            c.local(
                f"rsync {local_config} {remote_user}@{remote_host}:{remote_domain_dir}/config.yml",
                echo=True,
            )
        else:
            print(f"Warning: No config.yml found for domain {domain}")


def refresh_databases(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Refresh SQLite databases for all domains by running schema creation."""
    domains = config.domains

    # Only for multi-domain SQLite mode
    if not domains:
        return

    remote_base = config.remote_base

    print("Refreshing SQLite databases for all domains...")

    for domain in domains:
        print(f"Refreshing database for domain: {domain}")

        schema_script = f"{remote_release_dir}/shared/db/scripts/create_schema.sql"
        db_dir = f"{remote_base}/domains/{domain}"
        db_path = f"{db_dir}/data.db"

        # Ensure domain directory exists
        c.run(f"mkdir -p {db_dir}", echo=True)

        # Run schema creation (CREATE TABLE IF NOT EXISTS is idempotent)
        try:
            c.run(f"sqlite3 {db_path} < {schema_script}", echo=True)
            print(f"Database refreshed: {db_path}")
        except UnexpectedExit as e:
            print(f"Warning: Could not refresh database for {domain}: {e}")


def run_migrations(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Run pending migrations for all domains."""
    domains = config.domains

    # Only for multi-domain SQLite mode
    if not domains:
        return

    remote_base = config.remote_base
    migrations_dir = f"{remote_release_dir}/shared/db/scripts/migrations"

    print("Running migrations for all domains...")

    for domain in domains:
        db_dir = f"{remote_base}/domains/{domain}"
        db_path = f"{db_dir}/data.db"

        print(f"Running migrations for domain: {domain}")

        try:
            # Ensure migrations table exists
            c.run(
                f"sqlite3 {db_path} \"CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, applied_at INTEGER DEFAULT (strftime('%s', 'now')))\"",
                hide=True,
            )

            # Get list of migration files
            result = c.run(f"ls -1 {migrations_dir}/*.sql 2>/dev/null || true", hide=True)
            migration_files = [f for f in result.stdout.strip().split("\n") if f]

            if not migration_files:
                print(f"No migrations found for {domain}")
                continue

            for migration_file in sorted(migration_files):
                migration_name = migration_file.rsplit("/", 1)[-1].replace(".sql", "")

                # Check if migration already applied
                check_result = c.run(
                    f"sqlite3 {db_path} \"SELECT COUNT(*) FROM migrations WHERE name='{migration_name}'\"",
                    hide=True,
                )
                if int(check_result.stdout.strip()) > 0:
                    print(f"SKIP: {migration_name} already applied for {domain}")
                    continue

                # Apply migration
                print(f"APPLY: {migration_name} for {domain}")
                c.run(f"sqlite3 {db_path} < {migration_file}", echo=True)
                c.run(
                    f"sqlite3 {db_path} \"INSERT INTO migrations (name) VALUES ('{migration_name}')\"",
                    echo=True,
                )
                print(f"PASS: {migration_name} applied for {domain}")

        except UnexpectedExit as e:
            print(f"Warning: Could not run migrations for {domain}: {e}")


def seed_auth_data(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Run seed_auth.sql for all domains that have no users."""
    domains = config.domains

    # Only for multi-domain SQLite mode
    if not domains:
        return

    remote_base = config.remote_base
    seed_script = f"{remote_release_dir}/shared/db/scripts/seed_auth.sql"

    print("Seeding auth data for domains without users...")

    for domain in domains:
        db_dir = f"{remote_base}/domains/{domain}"
        db_path = f"{db_dir}/data.db"

        try:
            # Check if user table has any rows
            result = c.run(
                f"sqlite3 {db_path} 'SELECT COUNT(*) FROM user'",
                hide=True,
            )
            user_count = int(result.stdout.strip())

            if user_count > 0:
                print(f"SKIP: {domain} - already has {user_count} user(s)")
            else:
                print(f"SEED: {domain} - no users found, adding initial admin...")
                c.run(f"sqlite3 {db_path} < {seed_script}", echo=True)
                print(f"Auth data seeded for: {domain}")

        except UnexpectedExit as e:
            print(f"Warning: Could not seed auth data for {domain}: {e}")


def restart_service(c: Connection, config: Config) -> None:
    """Restart the systemd service."""
    service_name = config.service_name

    print(f"Restarting service {service_name}")

    try:
        c.run(f"sudo /bin/systemctl restart {service_name}", echo=True)
        print(f"Service {service_name} restarted successfully")

        print("Waiting 5 seconds for service to start...")
        time.sleep(5)

        print("Checking service status...")
        c.run(f"sudo /bin/systemctl status {service_name}", echo=True)

        print("Recent service logs:")
        c.run(f"sudo /usr/bin/journalctl -u {service_name} -n 10 --no-pager", echo=True)

    except UnexpectedExit as e:
        print(f"Warning: Service restart failed: {e}")
        print("Recent service logs (for debugging):")
        try:
            c.run(f"sudo /usr/bin/journalctl -u {service_name} -n 10 --no-pager", echo=True)
        except UnexpectedExit:
            print("Could not retrieve service logs")


def deploy_api(c: Connection) -> None:
    """Deploy API backend application."""
    config = load_config()
    remote_builds = config.api_remote_builds

    ts = time.strftime("%Y%m%d%H%M%S")
    remote_release_dir = f"{remote_builds}/{ts}"

    print("=== DEPLOYING API ===")

    upload_api_release(c, config, remote_release_dir)
    sync_virtual_environment(c, config, remote_release_dir)
    update_api_symlink(c, config, remote_release_dir)

    # Database operations (multi-domain SQLite mode)
    sync_domain_configs(c, config)
    refresh_databases(c, config, remote_release_dir)
    run_migrations(c, config, remote_release_dir)
    seed_auth_data(c, config, remote_release_dir)

    setup_api_permissions(c, config, remote_release_dir)
    cleanup_old_api_builds(c, config)
    restart_service(c, config)

    print(f"=== RELEASED {ts} ===")


def main() -> None:
    """Main deployment function."""
    c = get_connection()
    deploy_api(c)


if __name__ == "__main__":
    main()
