#!/usr/bin/env python3
"""
Build script for MCC-style web applications.
Builds Angular UI and prepares API files for deployment.
Supports both SQLite (multi-domain) and PostgreSQL (single-domain) configurations.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from config_loader import load_config


def build_ui() -> None:
    """Build Angular UI using nvm for consistent Node.js version."""
    print("Building Angular UI...")

    ui_dir = Path(__file__).parent.parent / "src" / "ui"

    # Check if npm install is needed (skip if node_modules is up-to-date)
    # This prevents breaking ng serve which crashes if npm ci deletes node_modules mid-run
    package_lock = ui_dir / "package-lock.json"
    node_modules_lock = ui_dir / "node_modules" / ".package-lock.json"

    needs_install = True
    if node_modules_lock.exists() and package_lock.exists():
        if node_modules_lock.stat().st_mtime >= package_lock.stat().st_mtime:
            needs_install = False
            print("node_modules is up-to-date, skipping npm ci")

    npm_cmd = "npm ci" if needs_install else "true"

    # Use nvm to ensure correct Node version
    if sys.platform == "win32":
        command = ["npx", "ng", "build", "--configuration", "production"]
    else:
        command = [
            "bash",
            "-c",
            f"source ~/.nvm/nvm.sh && nvm use && {npm_cmd} && npx ng build --configuration=production",
        ]

    result = subprocess.run(command, cwd=ui_dir, capture_output=False)

    if result.returncode != 0:
        raise RuntimeError("UI build failed")

    print("UI build completed")


def build_api() -> None:
    """Copy API files to dist/api/."""
    print("Preparing API files...")

    project_root = Path(__file__).parent.parent
    dist_api = project_root / "dist" / "api"

    # Remove old dist
    if dist_api.exists():
        shutil.rmtree(dist_api)

    dist_api.mkdir(parents=True, exist_ok=True)

    # Copy API and shared directories (excluding __pycache__)
    shutil.copytree(
        project_root / "src" / "api",
        dist_api / "api",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(
        project_root / "src" / "shared",
        dist_api / "shared",
        ignore=shutil.ignore_patterns("__pycache__"),
    )

    # Copy dependency files
    shutil.copy2(project_root / "pyproject.toml", dist_api / "pyproject.toml")
    shutil.copy2(project_root / "uv.lock", dist_api / "uv.lock")

    print(f"API files prepared at {dist_api}")


def build_database() -> None:
    """Copy database schema files to dist/db/ (for PostgreSQL deployments)."""
    config = load_config()

    # Only build database package for PostgreSQL mode (single domain)
    if config.domains:
        print("SQLite mode detected - skipping database build (schema in shared/)")
        return

    print("Preparing database files...")

    project_root = Path(__file__).parent.parent
    dist_db = project_root / "dist" / "db"

    if dist_db.exists():
        shutil.rmtree(dist_db)

    dist_db.mkdir(parents=True, exist_ok=True)

    # Copy schema file
    schema_source = project_root / "src" / "shared" / "db" / "scripts" / "create_schema.sql"
    if schema_source.exists():
        shutil.copy2(schema_source, dist_db / "create_schema.sql")
        print(f"Database files prepared at {dist_db}")
    else:
        print(f"Warning: Schema file not found at {schema_source}")


def main() -> None:
    """Main build process."""
    print("=== STARTING BUILD ===")

    # Create dist directory
    project_root = Path(__file__).parent.parent
    (project_root / "dist").mkdir(exist_ok=True)

    # Build all components
    build_ui()
    build_api()
    build_database()

    print("=== BUILD COMPLETED ===")


if __name__ == "__main__":
    main()
