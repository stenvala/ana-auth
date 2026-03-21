#!/usr/bin/env python3
"""Deploy UI to remote server."""

import time

from fabric import Connection

from config_loader import Config, load_config


def get_connection() -> Connection:
    """Get SSH connection using configuration."""
    config = load_config()
    remote_user = config.remote_user
    remote_host = config.remote_host
    return Connection(f"{remote_user}@{remote_host}")


def upload_ui_release(
    c: Connection,
    config: Config,
    remote_release_dir: str,
) -> None:
    """Upload UI files to remote release directory."""
    local_ui_dir = config.local_ui_dir
    remote_user = config.remote_user
    remote_host = config.remote_host

    print(f"Creating remote build directory: {remote_release_dir}")
    c.run(f"mkdir -p {remote_release_dir}", echo=True)

    print(f"Uploading UI files from {local_ui_dir} to {remote_release_dir}")
    c.local(
        f"rsync -r {local_ui_dir}/ {remote_user}@{remote_host}:{remote_release_dir}",
        echo=True,
    )


def update_ui_symlink(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Update symlink to point to new UI release."""
    symlink = config.ui_symlink

    print(f"Updating symlink {symlink} to point to {remote_release_dir}")
    c.run(f"rm -f {symlink}", echo=True)
    c.run(f"ln -s {remote_release_dir} {symlink}", echo=True)


def cleanup_old_ui_builds(c: Connection, config: Config) -> None:
    """Remove old UI builds keeping only the specified number."""
    remote_builds = config.ui_remote_builds
    keep_builds = config.keep_builds

    print("Cleaning up old builds...")
    result = c.run(f"ls -1 {remote_builds}", hide=True)
    dirs = [d for d in result.stdout.strip().split("\n") if d]
    dirs.sort()

    while len(dirs) > keep_builds:
        old = dirs.pop(0)
        print(f"Removing old release: {old}")
        c.run(f"rm -rf {remote_builds}/{old}", echo=True)


def setup_ui_permissions(c: Connection, config: Config, remote_release_dir: str) -> None:
    """Set up proper file permissions for UI files."""
    remote_builds = config.ui_remote_builds
    dir_user = config.dir_user
    dir_group = config.dir_group

    # If this is not done, after chown old version cleanups don't work
    print("Setting group write permissions on UI builds directory")
    c.run(f"sudo chmod -R g+w {remote_builds}", echo=True)

    print(f"Changing ownership of UI builds directory to {dir_user}:{dir_group}")
    c.run(f"sudo chown -R {dir_user}:{dir_group} {remote_builds}", echo=True)

    print("Setting group read permissions on UI builds directory")
    c.run(f"sudo chmod -R g+r {remote_builds}", echo=True)

    print(f"Changing ownership of new UI build to {dir_user}:{dir_group}")
    c.run(f"sudo chown -R {dir_user}:{dir_group} {remote_release_dir}", echo=True)

    print("Setting group read permissions on new UI build")
    c.run(f"sudo chmod -R g+r {remote_release_dir}", echo=True)


def deploy_ui(c: Connection) -> None:
    """Deploy UI frontend application."""
    config = load_config()
    remote_builds = config.ui_remote_builds

    ts = time.strftime("%Y%m%d%H%M%S")
    remote_release_dir = f"{remote_builds}/{ts}"

    print("=== DEPLOYING UI ===")

    upload_ui_release(c, config, remote_release_dir)
    update_ui_symlink(c, config, remote_release_dir)
    setup_ui_permissions(c, config, remote_release_dir)
    cleanup_old_ui_builds(c, config)

    print(f"=== RELEASED {ts} ===")


def main() -> None:
    """Main deployment function."""
    c = get_connection()
    deploy_ui(c)


if __name__ == "__main__":
    main()
