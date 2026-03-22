#!/usr/bin/env python3
"""MCC build script for ana-auth.

Runs quality checks, tests, builds frontend/backend, and packages
everything into output/ for deployment.
"""

import shutil
import sys
from pathlib import Path
import os

import typer

from mcc_common import run

app = typer.Typer(help="Build ana-auth for deployment")

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
UI_DIR = SRC_DIR / "ui"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEST_ARTIFACTS_DIR = PROJECT_ROOT / "test-artifacts"

NODE_ENV = os.environ.copy()
NODE_ENV["PATH"] = "/home/stenvala/.nvm/versions/node/v20.19.2/bin:" + NODE_ENV["PATH"]

if sys.platform == "darwin":
    print("Running on macOS")
    NPM = "npm"
    NPX = "npx"
else:
    print("Running on Linux")
    NPM = "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npm"
    NPX = "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npx"


def clean_output() -> None:
    """Remove and recreate output and test-artifacts directories."""
    for d in [OUTPUT_DIR, TEST_ARTIFACTS_DIR]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()


def run_quality_checks() -> None:
    """Run ruff and ty quality checks."""
    print("\n=== QUALITY CHECKS ===")
    run(["uv", "run", "run_tests.py", "quality"])


def run_unit_tests() -> None:
    """Run unit tests with coverage gate."""
    print("\n=== UNIT TESTS ===")
    run(
        [
            "uv",
            "run",
            "run_tests.py",
            "unit",
            "--coverage",
        ]
    )
    # Copy test artifacts
    for artifact in PROJECT_ROOT.glob("pytest-*.xml"):
        shutil.copy2(artifact, TEST_ARTIFACTS_DIR)
    htmlcov = PROJECT_ROOT / "htmlcov"
    if htmlcov.exists():
        shutil.copytree(htmlcov, TEST_ARTIFACTS_DIR / "htmlcov", dirs_exist_ok=True)


def run_integration_tests() -> None:
    """Run integration tests."""
    print("\n=== INTEGRATION TESTS ===")
    run(["uv", "run", "run_tests.py", "int"])
    for artifact in PROJECT_ROOT.glob("integation-*.xml"):
        shutil.copy2(artifact, TEST_ARTIFACTS_DIR)


def build_frontend() -> None:
    """Build Angular frontend."""
    print("\n=== FRONTEND BUILD ===")

    if not (UI_DIR / "node_modules").exists():
        run([NPM, "ci"], cwd=UI_DIR, env=NODE_ENV)

    run([NPX, "ng", "build", "--configuration=production"], cwd=UI_DIR, env=NODE_ENV)


def assemble_output() -> None:
    """Copy all deployment artifacts to output/."""
    print("\n=== ASSEMBLING OUTPUT ===")

    # Backend source
    api_out = OUTPUT_DIR / "src" / "api"
    shared_out = OUTPUT_DIR / "src" / "shared"
    _copy_tree(SRC_DIR / "api", api_out)
    _copy_tree(SRC_DIR / "shared", shared_out)

    # Frontend dist
    ui_dist = UI_DIR / "dist" / "ui"
    if ui_dist.exists():
        _copy_tree(ui_dist, OUTPUT_DIR / "ui-dist")
    else:
        print(f"WARNING: Frontend dist not found at {ui_dist}")

    # Database scripts
    db_out = OUTPUT_DIR / "db"
    db_out.mkdir(parents=True)
    schema_dir = SRC_DIR / "shared" / "db" / "schema"
    migrations_dir = SRC_DIR / "shared" / "db" / "migrations"
    if schema_dir.exists():
        _copy_tree(schema_dir, db_out / "schema")
    if migrations_dir.exists():
        _copy_tree(migrations_dir, db_out / "migrations")

    # Deploy scripts
    for script in [
        "mcc_deploy.py",
        "mcc_common.py",
        "mcc_config.py",
        "mcc_config.yml",
        "setup_db.py",
        "backup_db.py",
        "pyproject.toml",
        "uv.lock",
    ]:
        src = PROJECT_ROOT / script
        shutil.copy2(src, OUTPUT_DIR / script)

    # MCC config files
    mcc_out = OUTPUT_DIR / "mcc"
    mcc_out.mkdir(parents=True)
    mcc_dir = PROJECT_ROOT / "mcc"
    for f in mcc_dir.glob("conf-*.yml"):
        shutil.copy2(f, mcc_out / f.name)
    ensure_admin = mcc_dir / "ensure_admin.sql"
    shutil.copy2(ensure_admin, mcc_out / "ensure_admin.sql")

    # Project metadata
    for f in ["pyproject.toml", "uv.lock"]:
        src = PROJECT_ROOT / f
        shutil.copy2(src, OUTPUT_DIR / f)

    # Build info
    build_info = PROJECT_ROOT / "build_info.yml"
    if build_info.exists():
        shutil.copy2(build_info, OUTPUT_DIR / "build_info.yml")
    print(f"Output assembled in {OUTPUT_DIR}")


def _copy_tree(src: Path, dst: Path) -> None:
    """Copy directory tree, creating parents as needed."""
    shutil.copytree(src, dst, dirs_exist_ok=True)


@app.command()
def build(
    no_tests: bool = typer.Option(
        False, "--no-tests", help="Skip quality checks and tests"
    ),
) -> None:
    """Build ana-auth for deployment."""
    clean_output()

    if not no_tests:
        run_quality_checks()
        run_unit_tests()
        run_integration_tests()

    build_frontend()
    assemble_output()

    print("\n=== BUILD COMPLETE ===")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    app()
