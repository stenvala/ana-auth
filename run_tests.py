#!/usr/bin/env python3
"""
Centralized test runner for the ana-auth project.
Coordinates Python tests and code quality checks.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import typer

COV_FAIL_UNDER = 20


@dataclass
class PytestConfig:
    """Configuration for a pytest run."""

    marker: str
    ignore_e2e: bool = True
    parallel: bool = True
    default_path: str = "tests/"
    junit_xml: str = "unit-tests.xml"
    cov_fail_under: Optional[int] = COV_FAIL_UNDER
    suite_name: str = ""
    headed: bool = False
    debug: bool = False


PYTEST_CONFIGS = {
    "unit": PytestConfig(
        marker="not integration and not e2e",
        suite_name="Python Unit Tests",
    ),
    "integration": PytestConfig(
        marker="integration",
        parallel=False,
        junit_xml="integration-tests.xml",
        cov_fail_under=None,
        suite_name="Python Integration Tests",
    ),
    "e2e": PytestConfig(
        marker="e2e",
        ignore_e2e=False,
        default_path="tests/e2e/",
        junit_xml="e2e-tests.xml",
        cov_fail_under=None,
        suite_name="E2E Browser Tests",
    ),
    "python": PytestConfig(
        marker="not e2e",
        suite_name="Python Tests",
    ),
}


@dataclass
class TestRunner:
    """Centralized test runner for all test suites."""

    verbose: bool = False
    project_root: Path = field(default_factory=lambda: Path(__file__).parent)
    failed_suites: list[str] = field(default_factory=list)

    @property
    def src_dir(self) -> Path:
        return self.project_root / "src"

    def log_header(self, message: str) -> None:
        separator = "=" * len(message)
        typer.echo(f"\n{separator}\n{message}\n{separator}")

    def run_command(
        self,
        command: list[str],
        cwd: Optional[Path] = None,
        description: str = "",
        env: Optional[dict[str, str]] = None,
    ) -> tuple[bool, str]:
        """Run a command and return success status and output."""
        if self.verbose:
            typer.echo(f"Running: {' '.join(command)}")

        try:
            run_env = os.environ.copy()
            if env:
                run_env.update(env)

            if self.verbose:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    text=True,
                    check=False,
                    env=run_env,
                )
                passed = result.returncode == 0
                label = description or "Command"
                typer.echo(
                    f"  {label} passed"
                    if passed
                    else f"  {label} failed with exit code: {result.returncode}"
                )
                return passed, ""

            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=False,
                env=run_env,
            )

            label = description or "Command"
            if result.returncode == 0:
                if result.stdout and result.stdout.strip():
                    typer.echo(result.stdout.strip())
                typer.echo(f"  {label} passed")
                return True, result.stdout

            full_output = result.stdout or ""
            if result.stderr:
                full_output = (
                    f"{full_output}\n{result.stderr}" if full_output else result.stderr
                )

            if full_output:
                typer.echo(f"  {label} failed:")
                typer.echo(full_output)
            else:
                typer.echo(f"  {label} failed with exit code: {result.returncode}")
            return False, full_output

        except FileNotFoundError:
            error_msg = f"Command not found: {command[0]}"
            typer.echo(f"  {description or 'Command'} failed: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            typer.echo(f"  {description or 'Command'} failed: {error_msg}")
            return False, error_msg

    def _run_tracked(
        self, suite_name: str, command: list[str], **kwargs: object
    ) -> bool:
        """Run a command and track failures by suite name."""
        success, _ = self.run_command(command, description=suite_name, **kwargs)  # type: ignore[arg-type]
        if not success:
            self.failed_suites.append(suite_name)
        return success

    def run_ruff_check(self) -> bool:
        success = self._run_tracked(
            "Ruff",
            ["uv", "run", "ruff", "check", ".", "--exclude", "ui"],
            cwd=self.src_dir,
        )
        # Generate JUnit XML artifact separately
        try:
            subprocess.run(
                [
                    "uv", "run", "ruff", "check", ".", "--exclude", "ui",
                    "--output-format=junit", "-o", str(self.project_root / "ruff.xml"),
                ],
                cwd=self.src_dir,
                capture_output=True,
                check=False,
            )
        except Exception:
            pass
        return success

    def run_ty_check(self) -> bool:
        success = self._run_tracked(
            "ty",
            ["uv", "run", "ty", "check"],
            cwd=self.src_dir,
        )
        # Generate JUnit XML artifact separately (ty has no --output-file)
        try:
            result = subprocess.run(
                ["uv", "run", "ty", "check", "--output-format", "junit"],
                cwd=self.src_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            ty_xml = self.project_root / "ty.xml"
            ty_xml.write_text(result.stdout)
        except Exception:
            pass
        return success

    def run_cyclomatic_complexity(self, max_complexity: int = 10) -> bool:
        return self._run_tracked(
            "Cyclomatic Complexity",
            [
                "uv",
                "run",
                "ruff",
                "check",
                ".",
                "--select=C901",
                f"--config=lint.mccabe.max-complexity={max_complexity}",
                "--exclude=tests",
                "--exclude=ui",
            ],
            cwd=self.src_dir,
        )

    def run_quality_checks(self) -> bool:
        self.log_header("PYTHON CODE QUALITY CHECKS")
        return self.run_ruff_check() & self.run_ty_check()

    def run_pytest(
        self,
        config: PytestConfig,
        coverage: bool = False,
        file_pattern: Optional[str] = None,
        stop_on_first_failure: bool = False,
        headed: bool = False,
        debug: bool = False,
    ) -> bool:
        """Run pytest with the given configuration."""
        self.log_header(config.suite_name.upper())

        command = ["uv", "run", "pytest"]

        if stop_on_first_failure:
            command.append("-x")

        command.extend(["-m", config.marker])

        if config.ignore_e2e:
            command.extend(["--ignore=tests/e2e"])

        if file_pattern:
            command.append(file_pattern)
        else:
            if config.parallel:
                command.extend(["-n", "auto"])
            command.append(config.default_path)

        if coverage:
            cov_args = [
                "--cov=.",
                "--cov-config=../pyproject.toml",
                "--cov-report=html:../htmlcov",
                "--cov-report=json:../coverage.json",
                "--cov-report=term-missing",
                "--cov-branch",
            ]
            if config.cov_fail_under is not None:
                cov_args.append(f"--cov-fail-under={config.cov_fail_under}")
            command.extend(cov_args)

        command.append("-v")
        command.extend([f"--junit-xml=../{config.junit_xml}"])

        if headed or debug:
            command.append("--headed")

        env: Optional[dict[str, str]] = None
        if debug:
            env = {"PWDEBUG": "1"}

        return self._run_tracked(config.suite_name, command, cwd=self.src_dir, env=env)

    def print_summary(self) -> None:
        self.log_header("TEST EXECUTION SUMMARY")
        if not self.failed_suites:
            typer.echo("All test suites passed!")
        else:
            typer.echo(f"{len(self.failed_suites)} test suite(s) failed:")
            for suite in self.failed_suites:
                typer.echo(f"   - {suite}")
        typer.echo("")


def _exit_on_failure(runner: TestRunner, success: bool) -> None:
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


app = typer.Typer(help="Centralized test runner for ana-auth project")


@app.command()
def unit(
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Include coverage reporting"
    ),
    file: Optional[str] = typer.Option(None, "--file", help="Run specific test file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    stop_on_first_failure: bool = typer.Option(
        False, "--stop-on-first-failure", "-x", help="Stop on first failure"
    ),
) -> None:
    """Run Python unit tests (excludes integration tests)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_pytest(
        PYTEST_CONFIGS["unit"],
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    _exit_on_failure(runner, success)


@app.command(name="int")
def integration(
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Include coverage reporting"
    ),
    file: Optional[str] = typer.Option(None, "--file", help="Run specific test file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    stop_on_first_failure: bool = typer.Option(
        False, "--stop-on-first-failure", "-x", help="Stop on first failure"
    ),
) -> None:
    """Run Python integration tests only."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_pytest(
        PYTEST_CONFIGS["integration"],
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    _exit_on_failure(runner, success)


@app.command()
def e2e(
    file: Optional[str] = typer.Option(None, "--file", help="Run specific test file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    stop_on_first_failure: bool = typer.Option(
        False, "--stop-on-first-failure", "-x", help="Stop on first failure"
    ),
    headed: bool = typer.Option(False, "--headed", help="Run with visible browser"),
    debug: bool = typer.Option(
        False, "--debug", help="Run with Playwright Inspector (implies --headed)"
    ),
) -> None:
    """Run E2E browser tests."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_pytest(
        PYTEST_CONFIGS["e2e"],
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
        headed=headed,
        debug=debug,
    )
    _exit_on_failure(runner, success)


@app.command()
def python(
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Include coverage reporting"
    ),
    file: Optional[str] = typer.Option(None, "--file", help="Run specific test file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    stop_on_first_failure: bool = typer.Option(
        False, "--stop-on-first-failure", "-x", help="Stop on first failure"
    ),
) -> None:
    """Run all Python tests (unit + integration)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_pytest(
        PYTEST_CONFIGS["python"],
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    _exit_on_failure(runner, success)


@app.command()
def quality(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run all code quality checks."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_quality_checks()
    _exit_on_failure(runner, success)


@app.command()
def ruff(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run Ruff linting and import sorting."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_ruff_check()
    _exit_on_failure(runner, success)


@app.command()
def ty(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run ty type checking."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_ty_check()
    _exit_on_failure(runner, success)


@app.command()
def cc(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    max_complexity: int = typer.Option(
        10, "--max-complexity", "-m", help="Maximum allowed cyclomatic complexity"
    ),
) -> None:
    """Run cyclomatic complexity analysis on src (excluding tests and ui)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_cyclomatic_complexity(max_complexity=max_complexity)
    _exit_on_failure(runner, success)


@app.command(name="all")
def all_tests(
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Include coverage for Python tests"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    max_complexity: int = typer.Option(
        10, "--max-complexity", "-m", help="Maximum allowed cyclomatic complexity"
    ),
) -> None:
    """Run all tests."""
    runner = TestRunner(verbose=verbose)
    success = True
    try:
        success &= runner.run_quality_checks()
        success &= runner.run_cyclomatic_complexity(max_complexity=max_complexity)
        success &= runner.run_pytest(PYTEST_CONFIGS["python"], coverage=coverage)
    except KeyboardInterrupt:
        typer.echo("\nTest execution interrupted by user")
        success = False
    finally:
        runner.print_summary()
    if not success:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
