#!/usr/bin/env python3
"""
Deploy scripts directory to remote server.
Syncs local scripts directory to remote_base/scripts and sets up cron jobs.
"""

from pathlib import Path

from fabric import Connection

from config_loader import load_config


def get_connection() -> Connection:
    """Get SSH connection using configuration."""
    config = load_config()
    remote_user = config.remote_user
    remote_host = config.remote_host
    return Connection(f"{remote_user}@{remote_host}")


def sync_scripts(c: Connection) -> None:
    """Sync scripts directory to remote server."""
    config = load_config()

    remote_base = config.remote_base
    remote_user = config.remote_user
    remote_host = config.remote_host

    local_scripts_dir = Path(__file__).parent / "scripts"
    remote_scripts_dir = f"{remote_base}/scripts"

    # Check if local scripts directory exists
    if not local_scripts_dir.exists():
        print(f"No scripts directory found at {local_scripts_dir} - skipping sync")
        return

    print(f"Checking if remote scripts directory exists: {remote_scripts_dir}")
    check_result = c.run(f"test -d {remote_scripts_dir}", echo=True, warn=True)

    if check_result.failed:
        print(f"Directory does not exist, creating: {remote_scripts_dir}")
        c.run(f"mkdir -p {remote_scripts_dir}", echo=True)
    else:
        print(f"Directory already exists: {remote_scripts_dir}")

    print(f"Syncing scripts from {local_scripts_dir} to {remote_scripts_dir}")
    result = c.local(
        f"rsync -rlpt --delete {local_scripts_dir}/ {remote_user}@{remote_host}:{remote_scripts_dir}/",
        echo=True,
        warn=True,
    )

    if result.failed:
        raise Exception(f"Failed to sync scripts. Exit code: {result.return_code}")

    print("Scripts deployed successfully")


def setup_crontab(c: Connection) -> None:
    """Ensure crontab entries exist for configured cron jobs."""
    config = load_config()
    remote_base = config.remote_base
    backup_dir = f"{remote_base}/db-backups"

    # Ensure backup directory exists on remote
    print(f"Ensuring backup directory exists: {backup_dir}")
    c.run(f"mkdir -p {backup_dir}", echo=True)

    # Default backup job configuration
    cron_jobs = [
        {
            "name": "db-backup",
            "hour": 3,  # Run at 3 AM
            "minute": 0,
            "scripts_dir": f"{remote_base}/scripts",
            "commands": ["backup_db.py"],
            "env_vars": {"BACKUP_DIR": backup_dir},
        }
    ]

    print("Checking current crontab entries")
    result = c.run("crontab -l", echo=True, warn=True)

    if result.failed:
        print("No existing crontab, creating new one")
        current_crontab = ""
    else:
        current_crontab = result.stdout

    # Remove all existing entries for our jobs
    lines = current_crontab.split("\n")
    filtered_lines = []
    for line in lines:
        # Keep lines that don't contain any of our job identifiers
        should_keep = True
        for job in cron_jobs:
            if job["name"] in line or (
                job["commands"][0] in line and "backup" in line.lower()
            ):
                should_keep = False
                break
        if should_keep:
            filtered_lines.append(line)

    new_crontab = "\n".join(filtered_lines).strip()

    # Add all cron job entries
    for job in cron_jobs:
        scripts_dir = job["scripts_dir"]
        log_file = job.get("log_file", f"{scripts_dir}/logs.txt")
        commands = " && ".join([f"uv run {cmd}" for cmd in job["commands"]])

        # Build environment variable exports
        env_exports = ""
        if job.get("env_vars"):
            env_exports = (
                " && ".join(
                    [
                        f'export {key}="{value}"'
                        for key, value in job["env_vars"].items()
                    ]
                )
                + " && "
            )

        # Build cron command
        minute = job.get("minute", 0)
        hour = job["hour"]

        cron_command = (
            f'/bin/sh -c "cd {scripts_dir} && '
            f"{env_exports}"
            f'date >> {log_file} && '
            f'echo \\"=== Execution started ===\\" >> {log_file} && '
            f'{commands} >> {log_file} 2>&1"'
        )
        cron_entry = f"{minute} {hour} * * * {cron_command}"

        new_crontab += "\n" + cron_entry
        print(f"Adding/updating {job['name']} job: runs at {hour:02d}:{minute:02d} daily")
        print(f"  Commands: {' && '.join(job['commands'])}")
        print(f"  Logs: {log_file}")

    # Install new crontab using a temporary file
    new_crontab += "\n"  # Ensure trailing newline
    temp_file = "/tmp/new_crontab.txt"

    # Write crontab to temporary file
    c.run(f"cat > {temp_file} << 'CRONTAB_EOF'\n{new_crontab}\nCRONTAB_EOF", echo=True)

    # Install from temporary file
    c.run(f"crontab {temp_file}", echo=True)

    # Clean up temporary file
    c.run(f"rm {temp_file}", echo=True)

    print("\nCrontab configured successfully!")
    print("\nVerifying crontab entries:")
    c.run("crontab -l", echo=True)


def setup_permissions(c: Connection) -> None:
    """Set up proper permissions for scripts and backup directories."""
    config = load_config()
    remote_base = config.remote_base
    dir_user = config.dir_user
    dir_group = config.dir_group

    scripts_dir = f"{remote_base}/scripts"
    backup_dir = f"{remote_base}/db-backups"

    print("Setting up permissions...")

    # Scripts directory
    try:
        c.run(f"test -d {scripts_dir}", hide=True)
        c.sudo(f"chown -R {dir_user}:{dir_group} {scripts_dir}", echo=True)
        c.sudo(f"chmod -R g+rw {scripts_dir}", echo=True)
    except Exception:
        print(f"Scripts directory {scripts_dir} does not exist - skipping")

    # Backup directory
    try:
        c.run(f"test -d {backup_dir}", hide=True)
        c.sudo(f"chown -R {dir_user}:{dir_group} {backup_dir}", echo=True)
        c.sudo(f"chmod -R g+rw {backup_dir}", echo=True)
    except Exception:
        print(f"Backup directory {backup_dir} does not exist - skipping")

    print("Permissions configured")


def main() -> None:
    """Main deployment function."""
    c = get_connection()

    print("=== DEPLOYING SCRIPTS ===")
    sync_scripts(c)
    setup_crontab(c)
    setup_permissions(c)
    print("=== SCRIPTS DEPLOYED ===")


if __name__ == "__main__":
    main()