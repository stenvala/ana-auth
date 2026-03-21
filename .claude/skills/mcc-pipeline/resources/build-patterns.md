# Build Patterns (`mcc_build.py`)

## Overview

The build script (`mcc_build.py`) runs in the project root on the CI server (or locally on macOS for testing). It produces an `output/` directory containing everything needed for deployment. **Only contents of `output/` are transferred to the remote server.**

The MCC pipeline invokes the build script as: `uv run mcc_build.py --link-mode=copy`. The `--link-mode=copy` is a `uv` flag (not passed to the script) that tells `uv` to copy packages instead of symlinking them, which is required for the build output to be portable across machines.

## Execution Order

1. Clean `output/` directory
2. Run tests and quality checks (fail-fast)
3. Build frontend (if applicable)
4. Copy backend source to `output/`
5. Copy deployment configs to `output/`
6. Copy deployment scripts and supporting files to `output/`

## Critical Rule: Output Directory Boundary

Everything the deploy script needs must be in `output/`. This includes:

- `mcc_deploy.py` itself
- `mcc_common.py`
- Any stage-specific conf files (`conf-prod.yml`, `conf-dev.yml`)
- `config.yml` (stage routing)
- `build_info.yml` (added by pipeline service, copy it to output)
- `pyproject.toml` + `uv.lock` (for remote venv sync)
- Any migration scripts, seed scripts, backup scripts
- Any additional deploy-time scripts (e.g., `mcc_clone.py`)

## Example: Full-Stack Python/Angular Project

```python
"""Build script for MyApp."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from mcc_common import run

PROJECT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = PROJECT_DIR / "output"
TEST_ARTIFACTS_DIR = PROJECT_DIR / "test-artifacts"

# Node.js path handling (macOS dev vs Linux CI)
NODE_ENV = os.environ.copy()
if sys.platform != "darwin":
    NODE_ENV["PATH"] = "/home/stenvala/.nvm/versions/node/v20.19.2/bin:" + NODE_ENV["PATH"]
NPM = "npm" if sys.platform == "darwin" else "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npm"
NPX = "npx" if sys.platform == "darwin" else "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npx"


def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if TEST_ARTIFACTS_DIR.exists():
        shutil.rmtree(TEST_ARTIFACTS_DIR)
    TEST_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    run_tests()
    build_ui()
    copy_api()
    copy_deploy_files()


def run_tests():
    """Run tests first. Build fails if tests fail."""
    print("Running tests...", flush=True)
    run(["uv", "run", "python", "run_tests.py", "all", "-cv"], cwd=PROJECT_DIR)
    print("All tests passed", flush=True)


def build_ui():
    """Build Angular UI and copy to output."""
    ui_dir = PROJECT_DIR / "src" / "ui"
    if not (ui_dir / "node_modules").exists():
        run([NPM, "ci"], cwd=ui_dir, env=NODE_ENV)
    run([NPX, "ng", "build", "--configuration=production"], cwd=ui_dir, env=NODE_ENV)
    browser_dir = ui_dir / "dist" / "app-name" / "browser"
    shutil.copytree(browser_dir, OUTPUT_DIR / "ui")


def copy_api():
    """Copy backend source to output."""
    shutil.copytree(PROJECT_DIR / "src" / "api", OUTPUT_DIR / "api")
    shutil.copytree(PROJECT_DIR / "src" / "shared", OUTPUT_DIR / "shared")


def copy_deploy_files():
    """Copy everything needed for deployment."""
    # Individual files
    for filename in [
        "pyproject.toml", "uv.lock", "config.yml", "build_info.yml",
        "mcc_deploy.py", "mcc_common.py",
    ]:
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / filename)

    # Stage conf files from mcc/ directory
    for conf_name in ("conf-prod.yml", "conf-dev.yml"):
        conf_src = PROJECT_DIR / "mcc" / conf_name
        if conf_src.exists():
            shutil.copy2(conf_src, OUTPUT_DIR / conf_name)


if __name__ == "__main__":
    try:
        print("Starting build", flush=True)
        main()
        print("Build finished", flush=True)
    except Exception as e:
        print(f"Build failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
```

## Example: API-Only Python Project (No Frontend)

```python
def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_tests()
    copy_api()
    copy_migrations()
    copy_deploy_files()


def copy_migrations():
    """Copy database migration files to output."""
    migrations_dir = PROJECT_DIR / "migrations"
    if migrations_dir.exists():
        shutil.copytree(migrations_dir, OUTPUT_DIR / "migrations")
```

## Example: Project with Worker Process

```python
def copy_deploy_files():
    """Copy deploy files including worker code."""
    for filename in [
        "pyproject.toml", "uv.lock", "config.yml", "build_info.yml",
        "mcc_deploy.py", "mcc_common.py",
    ]:
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / filename)

    # Worker source
    shutil.copytree(PROJECT_DIR / "src" / "worker", OUTPUT_DIR / "worker")
```

## Test Artifacts

The MCC pipeline automatically collects test artifacts from builds. The build script creates a `test-artifacts/` directory at the project root (alongside `output/`), and the pipeline worker:

1. Parses each file in `test-artifacts/` and stores summaries in the database
2. Copies raw files to permanent storage for later download
3. Logs all discovered artifacts to the build log

**Important**: `test-artifacts/` is NOT inside `output/`. It lives at the project root, next to `output/`. The pipeline worker handles it separately.

### Supported Formats

| Extension | Format        | Parser                | Summary fields                                                |
| --------- | ------------- | --------------------- | ------------------------------------------------------------- |
| `.xml`    | JUnit XML     | `parse_junit_xml`     | tests, failures, errors, skipped, time                        |
| `.json`   | Coverage JSON | `parse_coverage_json` | percent_covered, num_statements, covered_lines, missing_lines |

### Category Naming Convention

The file stem becomes the artifact **category** displayed in the UI:

- `unit-tests.xml` → category `unit-tests`
- `integration-tests.xml` → category `integration-tests`
- `coverage.json` → category `coverage`
- `ruff.xml` → category `ruff`
- `ty.xml` → category `ty`

### Build Script Integration

The build script must:

1. Create and clean the `test-artifacts/` directory at the start
2. Configure test tools to write their output there

```python
PROJECT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = PROJECT_DIR / "output"
TEST_ARTIFACTS_DIR = PROJECT_DIR / "test-artifacts"


def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if TEST_ARTIFACTS_DIR.exists():
        shutil.rmtree(TEST_ARTIFACTS_DIR)
    TEST_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    run_tests()
    build_ui()
    copy_api()
    copy_deploy_files()
```

### Test Runner Integration (`run_tests.py`)

The test runner checks `self.test_artifacts_dir.is_dir()` to decide whether to write artifacts. This way, running tests locally (without the directory) produces no artifact files, but the build script creates the directory first so artifacts are captured during CI builds.

#### pytest with JUnit XML

```python
def run_unit_tests(self, coverage: bool = False):
    command = ["uv", "run", "pytest", "-m", "not integration and not e2e",
               "--ignore=tests/e2e", "tests/", "-v"]

    # JUnit XML output — always write when test-artifacts/ exists
    junit_path = "../test-artifacts/unit-tests.xml" if self.has_artifacts_dir else "../pytest-report.xml"
    command.extend([f"--junit-xml={junit_path}"])

    # Coverage JSON — only when coverage is enabled AND test-artifacts/ exists
    if coverage:
        command.extend(["--cov=.", "--cov-config=../pyproject.toml",
                        "--cov-report=term-missing", "--cov-branch",
                        "--cov-fail-under=90"])
        if self.has_artifacts_dir:
            command.append("--cov-report=json:../test-artifacts/coverage.json")

    self.run_command(command, cwd=self.src_dir, description="Python unit tests")
```

#### Integration tests (separate JUnit file)

```python
def run_integration_tests(self):
    command = ["uv", "run", "pytest", "-m", "integration",
               "--ignore=tests/e2e", "tests/", "-v"]

    junit_path = "../test-artifacts/integration-tests.xml" if self.has_artifacts_dir else "../pytest-integration-report.xml"
    command.extend([f"--junit-xml={junit_path}"])

    self.run_command(command, cwd=self.src_dir, description="Python integration tests")
```

#### Ruff linting (JUnit output)

```python
def run_ruff_check(self):
    success, _ = self.run_command(
        ["uv", "run", "ruff", "check", ".", "--exclude", "ui"],
        cwd=self.src_dir, description="Ruff linting",
    )
    if self.has_artifacts_dir:
        self.run_command(
            ["uv", "run", "ruff", "check", ".", "--exclude", "ui",
             "--output-format", "junit",
             "--output-file", str(self.test_artifacts_dir / "ruff.xml")],
            cwd=self.src_dir, description="Ruff JUnit artifact",
        )
    return success
```

#### ty type checking (JUnit output)

```python
def run_ty_check(self):
    success, _ = self.run_command(
        ["uv", "run", "ty", "check"], cwd=self.project_root, description="ty type checking",
    )
    if self.has_artifacts_dir:
        artifact_path = self.test_artifacts_dir / "ty.xml"
        result = subprocess.run(
            ["uv", "run", "ty", "check", "--output-format", "junit"],
            cwd=self.project_root, capture_output=True, text=True, check=False,
        )
        output = result.stdout.strip()
        if output:
            artifact_path.write_text(output)
        else:
            # ty outputs nothing when there are no issues — write empty testsuite
            artifact_path.write_text(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<testsuite name="ty" tests="0" failures="0" errors="0" skipped="0" time="0.0"/>\n'
            )
    return success
```

### What the Pipeline Does Automatically

After `mcc_build.py` finishes (whether it succeeds or fails):

1. **Collects artifacts**: Scans `test-artifacts/`, parses each file by extension, stores summaries as JSON in `build_test_artifacts` table
2. **Copies raw files**: Copies `test-artifacts/` to permanent storage (`<DATA_DIR>/build-outputs/<build_id>/test-artifacts/`)
3. **Logs to build log**: Lists all discovered files with sizes

The UI then shows:

- **Build detail page**: Test Results card with pass/fail counts and coverage percentages
- **Repository detail page → Trends tab**: Charts tracking test counts and coverage over time

### Minimal Example: Adding Test Artifacts to an Existing Project

If a project already has `mcc_build.py` with tests but no artifacts:

1. Add `TEST_ARTIFACTS_DIR` setup to `main()`:

```python
TEST_ARTIFACTS_DIR = PROJECT_DIR / "test-artifacts"

def main():
    # ... existing output dir cleanup ...
    if TEST_ARTIFACTS_DIR.exists():
        shutil.rmtree(TEST_ARTIFACTS_DIR)
    TEST_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    # ... rest of build ...
```

2. Add `--junit-xml=../test-artifacts/unit-tests.xml` to pytest commands
3. Add `--cov-report=json:../test-artifacts/coverage.json` if using coverage
4. Add `--output-format junit --output-file <path>` to ruff/ty if used

No changes needed to `mcc_deploy.py` — test artifacts are handled entirely by the pipeline worker.

## Adapting to Your Project

Key decisions when creating `mcc_build.py`:

| Concern                  | Options                                                   |
| ------------------------ | --------------------------------------------------------- |
| **Testing**              | `uv run run_tests.py`, custom test runner                 |
| **Frontend**             | Angular (`npx ng build`)                                  |
| **Backend**              | Single `api/` dir, `api/` + `shared/`, multiple modules   |
| **Migrations**           | SQL files in `migrations/`, Alembic directory, none       |
| **Extra scripts**        | Backup scripts, cron scripts, seed scripts                |
| **Extra deploy scripts** | `mcc_clone.py` or similar non-deployment stage scripts    |
| **Domain configs**       | Per-domain config.yml files (multi-tenant), single config |
| **Test artifacts**       | JUnit XML for tests/linting, coverage JSON for coverage   |
