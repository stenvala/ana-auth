#!/usr/bin/env python3
"""Linting wrapper for Python (ruff) and Angular (prettier)."""

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Lint and format code")

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
UI_DIR = SRC_DIR / "ui"


def _run(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and return whether it succeeded."""
    print(f"Running: {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, check=False)
    return result.returncode == 0


@app.command(name="python")
def lint_python(
    check_only: bool = typer.Option(
        False, "--check-only", help="Check without auto-fixing (for CI)"
    ),
) -> None:
    """Run ruff linting and formatting on Python code."""
    success = True

    if check_only:
        success &= _run(
            ["uv", "run", "ruff", "check", ".", "--exclude", "ui"], cwd=SRC_DIR
        )
        success &= _run(
            ["uv", "run", "ruff", "format", "--check", ".", "--exclude", "ui"],
            cwd=SRC_DIR,
        )
    else:
        success &= _run(
            [
                "uv",
                "run",
                "ruff",
                "check",
                "--fix",
                "--unsafe-fixes",
                ".",
                "--exclude",
                "ui",
            ],
            cwd=SRC_DIR,
        )
        success &= _run(
            ["uv", "run", "ruff", "format", ".", "--exclude", "ui"], cwd=SRC_DIR
        )

    if success:
        print("Python linting passed.")
    else:
        print("Python linting failed.")
        raise typer.Exit(1)


@app.command(name="angular")
def lint_angular(
    check_only: bool = typer.Option(
        False, "--check-only", help="Check without auto-fixing (for CI)"
    ),
) -> None:
    """Run prettier on Angular source files."""
    glob_pattern = "src/**/*.{ts,js,html,scss,css,json}"

    if check_only:
        cmd = ["npx", "prettier", "--check", glob_pattern]
    else:
        cmd = ["npx", "prettier", "--write", glob_pattern]

    success = _run(cmd, cwd=UI_DIR)

    if success:
        print("Angular linting passed.")
    else:
        print("Angular linting failed.")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
