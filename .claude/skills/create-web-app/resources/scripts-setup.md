# Development Scripts Reference

## 1. Utils Module

Create `utils.py` in project root:

```python
"""Basic logging utilities for scripts."""

import sys
from datetime import datetime


class Logger:
    """Simple logger with info and error methods."""

    def info(self, message: str) -> None:
        """Log info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")

    def error(self, message: str) -> None:
        """Log error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}", file=sys.stderr)


def get_logger() -> Logger:
    """Get a logger instance."""
    return Logger()
```

## 2. Service Orchestrator

Create `start_services.py` in project root:

```python
#!/usr/bin/env python3
"""
Service orchestrator for <PROJECT_NAME>.
Starts and manages all services with unified logging and graceful shutdown.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

import psutil

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("start_services")
logger.setLevel(logging.INFO)
logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(log_dir / "start_services.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.propagate = False


class ServiceOrchestrator:
    """Coordinate services with consolidated logging and process management."""

    def __init__(self):
        self.processes = {}
        self.running = True
        self.required_ports = [<API_PORT>, <UI_PORT>]  # API, UI ports
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        if sys.platform != 'win32':
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Shutdown signal received: {signum}")
        self.running = False

    def kill_processes_on_ports(self, ports: list[int]):
        """Kill processes using the specified ports."""
        for port in ports:
            try:
                import subprocess
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid_str in pids:
                        try:
                            pid = int(pid_str)
                            process = psutil.Process(pid)
                            logger.info(f"Killing process on port {port} (pid={pid})")
                            process.terminate()
                            process.wait(timeout=3)
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired, ValueError):
                            pass

            except Exception as e:
                logger.warning(f"Could not check processes on port {port}: {e}")

    async def start_service(self, name: str, command: list, cwd: Path = None):
        """Start a service with proper logging integration."""
        logger.info(f"Starting {name} service: {' '.join(command)}")

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        self.processes[name] = process
        asyncio.create_task(self._handle_service_output(name, process))
        logger.info(f"{name} service started (pid={process.pid})")

    async def _handle_service_output(self, service_name: str, process):
        """Handle service output and forward to main console."""
        async for line in process.stdout:
            line_text = line.decode('utf-8').strip()
            if line_text:
                print(f"[{service_name.upper()}] {line_text}")

    async def start_all_services(self):
        """Start all services."""
        logger.info("Starting services")

        # Kill any processes using our required ports
        logger.info(f"Checking for processes on required ports: {self.required_ports}")
        self.kill_processes_on_ports(self.required_ports)

        # Service configuration
        services = [
            ("api", ["uv", "run", "uvicorn", "api.main:app",
                    "--host", "0.0.0.0", "--port", "<API_PORT>", "--reload"], Path("src")),
            ("worker", ["uv", "run", "python", "-m", "worker.main"], Path("src")),
            ("ui", ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "<UI_PORT>"], Path("src/ui"))
        ]

        # Start services with staggered startup
        for name, command, cwd in services:
            if not self.running:
                break
            await self.start_service(name, command, cwd)
            await asyncio.sleep(1)

        logger.info("All services started")

        # Wait for services or shutdown signal
        try:
            while self.running and self.processes:
                for name, process in list(self.processes.items()):
                    if process.returncode is not None:
                        logger.warning(f"{name} service terminated unexpectedly")
                        del self.processes[name]

                if not self.processes:
                    logger.error("All services have terminated")
                    break

                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            await self.shutdown_all_services()

    async def shutdown_all_services(self):
        """Gracefully shutdown all services."""
        if not self.processes:
            return

        logger.info("Shutting down all services")

        for name, process in list(self.processes.items()):
            logger.info(f"Stopping {name} service")
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=10.0)
                logger.info(f"{name} service stopped")
            except asyncio.TimeoutError:
                logger.warning(f"Force killing {name} service")
                process.kill()
                await process.wait()
            del self.processes[name]

        logger.info("All services stopped")


async def main():
    """Main entry point."""
    orchestrator = ServiceOrchestrator()
    await orchestrator.start_all_services()
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        if exit_code:
            sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nShutdown complete")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
```

Replace `<API_PORT>` and `<UI_PORT>` with configured ports.

## 3. Test Runner

Create `run_tests.py` in project root:

```python
#!/usr/bin/env python3
"""
Centralized test runner for the <PROJECT_NAME> project.
Coordinates Python tests and code quality checks.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer


class TestRunner:
    """Centralized test runner for all test suites."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.failed_suites: list[str] = []

    def log(self, message: str) -> None:
        """Print log message."""
        typer.echo(message)

    def log_header(self, message: str) -> None:
        """Print section header."""
        separator = "=" * len(message)
        typer.echo(f"\n{separator}")
        typer.echo(f"{message}")
        typer.echo(f"{separator}")

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
            # Merge environment variables
            run_env = os.environ.copy()
            if env:
                run_env.update(env)

            if self.verbose:
                # In verbose mode, let output stream directly to terminal
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    text=True,
                    check=False,
                    env=run_env,
                )
                if result.returncode == 0:
                    typer.echo(f"  {description or 'Command'} passed")
                    return True, ""
                else:
                    typer.echo(
                        f"  {description or 'Command'} failed with exit code: {result.returncode}"
                    )
                    return False, ""
            else:
                # In non-verbose mode, capture output
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=run_env,
                )

                if result.returncode == 0:
                    # Show stdout output if available and not empty
                    if result.stdout and result.stdout.strip():
                        typer.echo(result.stdout.strip())
                    typer.echo(f"  {description or 'Command'} passed")
                    return True, result.stdout
                else:
                    # Show both stdout and stderr for failures to get full test output
                    full_output = ""
                    if result.stdout:
                        full_output += result.stdout
                    if result.stderr:
                        if full_output:
                            full_output += "\n"
                        full_output += result.stderr

                    if full_output:
                        typer.echo(f"  {description or 'Command'} failed:")
                        typer.echo(full_output)
                    else:
                        typer.echo(
                            f"  {description or 'Command'} failed with exit code: {result.returncode}"
                        )
                    return False, full_output

        except FileNotFoundError:
            error_msg = f"Command not found: {command[0]}"
            typer.echo(f"  {description or 'Command'} failed: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            typer.echo(f"  {description or 'Command'} failed: {error_msg}")
            return False, error_msg

    def run_ruff_check(self) -> bool:
        """Run Ruff linting and import sorting."""
        success, _ = self.run_command(
            ["uv", "run", "ruff", "check", ".", "--exclude", "ui"],
            cwd=self.src_dir,
            description="Ruff linting and import sorting",
        )
        if not success:
            self.failed_suites.append("Ruff")
        return success

    def run_ty_check(self) -> bool:
        """Run ty type checking on src directory."""
        success, _ = self.run_command(
            ["uv", "run", "ty", "check"],
            cwd=self.project_root,
            description="ty type checking",
        )
        if not success:
            self.failed_suites.append("ty")
        return success

    def run_cyclomatic_complexity(self, max_complexity: int = 10) -> bool:
        """Run cyclomatic complexity analysis using Ruff's mccabe plugin."""
        success, _ = self.run_command(
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
            description="Cyclomatic complexity analysis",
        )
        if not success:
            self.failed_suites.append("Cyclomatic Complexity")
        return success

    def run_python_quality_checks(self) -> bool:
        """Run all Python code quality checks."""
        self.log_header("PYTHON CODE QUALITY CHECKS")

        all_passed = True
        all_passed &= self.run_ruff_check()
        all_passed &= self.run_ty_check()

        return all_passed

    def run_unit_tests(
        self,
        coverage: bool = False,
        file_pattern: Optional[str] = None,
        stop_on_first_failure: bool = False,
    ) -> bool:
        """Run Python unit tests (excluding integration tests)."""
        self.log_header("PYTHON UNIT TESTS")

        command = ["uv", "run", "pytest"]

        if stop_on_first_failure:
            command.append("-x")

        # Exclude integration and e2e tests
        command.extend(["-m", "not integration and not e2e"])
        command.extend(["--ignore=tests/e2e"])

        if file_pattern:
            command.append(file_pattern)
        else:
            # Enable parallel execution with auto-detection of CPU cores
            command.extend(["-n", "auto"])
            command.append("tests/")

        if coverage:
            command.extend(
                [
                    "--cov=.",
                    "--cov-config=../pyproject.toml",
                    "--cov-report=html:../htmlcov",
                    "--cov-report=term-missing",
                    "--cov-branch",
                    "--cov-fail-under=90",
                ]
            )

        # Always use verbose output to show test progress
        command.append("-v")

        # Add junit output for CI
        command.extend(["--junit-xml=../pytest-report.xml"])

        success, _ = self.run_command(
            command, cwd=self.src_dir, description="Python unit tests"
        )

        if not success:
            self.failed_suites.append("Python Unit Tests")

        return success

    def run_integration_tests(
        self,
        coverage: bool = False,
        file_pattern: Optional[str] = None,
        stop_on_first_failure: bool = False,
    ) -> bool:
        """Run Python integration tests only."""
        self.log_header("PYTHON INTEGRATION TESTS")

        command = ["uv", "run", "pytest"]

        if stop_on_first_failure:
            command.append("-x")

        # Only run integration tests
        command.extend(["-m", "integration"])
        command.extend(["--ignore=tests/e2e"])

        if file_pattern:
            command.append(file_pattern)
        else:
            command.append("tests/")

        if coverage:
            command.extend(
                [
                    "--cov=.",
                    "--cov-config=../pyproject.toml",
                    "--cov-report=html:../htmlcov",
                    "--cov-report=term-missing",
                    "--cov-branch",
                    "--cov-fail-under=90",
                ]
            )

        # Always use verbose output to show test progress
        command.append("-v")

        # Add junit output for CI
        command.extend(["--junit-xml=../pytest-integration-report.xml"])

        success, _ = self.run_command(
            command, cwd=self.src_dir, description="Python integration tests"
        )

        if not success:
            self.failed_suites.append("Python Integration Tests")

        return success

    def run_e2e_tests(
        self,
        file_pattern: Optional[str] = None,
        stop_on_first_failure: bool = False,
        headed: bool = False,
        debug: bool = False,
    ) -> bool:
        """Run E2E browser tests."""
        self.log_header("E2E BROWSER TESTS")

        command = ["uv", "run", "pytest"]

        if stop_on_first_failure:
            command.append("-x")

        command.extend(["-m", "e2e"])

        if file_pattern:
            command.append(file_pattern)
        else:
            # Enable parallel execution with auto-detection of CPU cores
            command.extend(["-n", "auto"])
            command.append("tests/e2e/")

        command.append("-v")
        command.extend(["--junit-xml=../pytest-e2e-report.xml"])

        if headed or debug:
            command.append("--headed")

        env: Optional[dict[str, str]] = None
        if debug:
            env = {"PWDEBUG": "1"}

        success, _ = self.run_command(
            command, cwd=self.src_dir, description="E2E browser tests", env=env
        )

        if not success:
            self.failed_suites.append("E2E Browser Tests")

        return success

    def run_all_python_tests(
        self,
        coverage: bool = False,
        file_pattern: Optional[str] = None,
        stop_on_first_failure: bool = False,
    ) -> bool:
        """Run all Python tests (unit + integration)."""
        self.log_header("PYTHON TESTS (ALL)")

        command = ["uv", "run", "pytest"]

        if stop_on_first_failure:
            command.append("-x")

        # Exclude e2e tests (run unit + integration only)
        command.extend(["-m", "not e2e"])
        command.extend(["--ignore=tests/e2e"])

        if file_pattern:
            command.append(file_pattern)
        else:
            # Enable parallel execution with auto-detection of CPU cores
            command.extend(["-n", "auto"])
            command.append("tests/")

        if coverage:
            command.extend(
                [
                    "--cov=.",
                    "--cov-config=../pyproject.toml",
                    "--cov-report=html:../htmlcov",
                    "--cov-report=term-missing",
                    "--cov-branch",
                    "--cov-fail-under=90",
                ]
            )

        # Always use verbose output to show test progress
        command.append("-v")

        # Add junit output for CI
        command.extend(["--junit-xml=../pytest-report.xml"])

        success, _ = self.run_command(
            command, cwd=self.src_dir, description="Python tests"
        )

        if not success:
            self.failed_suites.append("Python Tests")

        return success

    def print_summary(self) -> None:
        """Print test execution summary."""
        self.log_header("TEST EXECUTION SUMMARY")

        if not self.failed_suites:
            typer.echo("All test suites passed!")
        else:
            typer.echo(f"{len(self.failed_suites)} test suite(s) failed:")
            for suite in self.failed_suites:
                typer.echo(f"   - {suite}")

        typer.echo("")


# Create the Typer app
app = typer.Typer(help="Centralized test runner for <PROJECT_NAME> project")


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
):
    """Run Python unit tests (excludes integration tests)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_unit_tests(
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


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
):
    """Run Python integration tests only."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_integration_tests(
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


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
):
    """Run E2E browser tests."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_e2e_tests(
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
        headed=headed,
        debug=debug,
    )
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


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
):
    """Run all Python tests (unit + integration)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_all_python_tests(
        coverage=coverage,
        file_pattern=file,
        stop_on_first_failure=stop_on_first_failure,
    )
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


@app.command()
def quality(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run all code quality checks."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_python_quality_checks()
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


@app.command()
def ruff(verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")):
    """Run Ruff linting and import sorting."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_ruff_check()
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


@app.command()
def ty(verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")):
    """Run ty type checking."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_ty_check()
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


@app.command()
def cc(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    max_complexity: int = typer.Option(
        10, "--max-complexity", "-m", help="Maximum allowed cyclomatic complexity"
    ),
):
    """Run cyclomatic complexity analysis on src (excluding tests and ui)."""
    runner = TestRunner(verbose=verbose)
    success = runner.run_cyclomatic_complexity(max_complexity=max_complexity)
    runner.print_summary()
    if not success:
        raise typer.Exit(1)


@app.command(name="all")
def all_tests(
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Include coverage for Python tests"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    max_complexity: int = typer.Option(
        10, "--max-complexity", "-m", help="Maximum allowed cyclomatic complexity"
    ),
):
    """Run all tests."""
    runner = TestRunner(verbose=verbose)
    success = True

    try:
        success &= runner.run_python_quality_checks()
        success &= runner.run_cyclomatic_complexity(max_complexity=max_complexity)
        success &= runner.run_all_python_tests(coverage=coverage)

    except KeyboardInterrupt:
        typer.echo("\nTest execution interrupted by user")
        success = False

    finally:
        runner.print_summary()

    if not success:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
```

## 4. Lint Tool

Create `lint.py` in project root:

```python
#!/usr/bin/env python3
"""
Code formatting and linting tool for <PROJECT_NAME>.
"""

import subprocess
from pathlib import Path

import typer

from utils import get_logger

logger = get_logger()


class LintRunner:
    """Centralized runner for code formatting and linting."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent

    def run_command(self, command: list[str], description: str) -> bool:
        """Run a command and return success status."""
        if self.verbose:
            typer.echo(f"Running: {' '.join(command)}", color=typer.colors.YELLOW)

        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=not self.verbose,
                text=True,
                check=False
            )

            if result.returncode == 0:
                if hasattr(result, 'stdout') and result.stdout:
                    typer.echo(result.stdout.rstrip())
                print(f"✅ {description} completed successfully")
                return True
            else:
                if hasattr(result, 'stdout') and result.stdout:
                    typer.echo(result.stdout.rstrip())
                if hasattr(result, 'stderr') and result.stderr:
                    typer.echo(result.stderr, color=typer.colors.RED)
                logger.error(f"{description} failed")
                return False

        except FileNotFoundError:
            logger.error(f"Command not found: {command[0]}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False

    def lint_python(self, check_only: bool = False) -> bool:
        """Run Python linting and formatting with ruff."""
        action = "check" if check_only else "fix"
        typer.echo(f"\n🐍 Running Python linting ({action})...", color=typer.colors.CYAN)

        command = ["uv", "run", "ruff", "check"]
        if not check_only:
            command.append("--fix")
            command.append("--unsafe-fixes")
        command.append("src")

        return self.run_command(command, f"Ruff linting ({action})")

    def lint_typescript(self, check_only: bool = False) -> bool:
        """Run TypeScript/JavaScript formatting with Prettier."""
        action = "check" if check_only else "format"
        typer.echo(f"\n📝 Running TypeScript formatting ({action})...", color=typer.colors.CYAN)

        ui_path = self.project_root / "src" / "ui"
        if not ui_path.exists():
            print("⚠️ UI directory not found, skipping TypeScript linting")
            return True

        command = ["npx", "prettier"]
        if check_only:
            command.extend(["--check", "src/**/*.{ts,js,html,scss,css,json}"])
        else:
            command.extend(["--write", "src/**/*.{ts,js,html,scss,css,json}"])

        try:
            result = subprocess.run(
                command,
                cwd=ui_path,
                capture_output=not self.verbose,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print(f"✅ Prettier formatting ({action}) completed successfully")
                return True
            else:
                logger.error(f"Prettier formatting ({action}) failed")
                return False

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False


app = typer.Typer(help="Code formatting and linting tool")

@app.command()
def python(
    check_only: bool = typer.Option(False, "--check-only", help="Check only, don't fix"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run Python linting with ruff."""
    runner = LintRunner(verbose=verbose)
    if not runner.lint_python(check_only=check_only):
        raise typer.Exit(1)

@app.command()
def typescript(
    check_only: bool = typer.Option(False, "--check-only", help="Check only, don't fix"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run TypeScript formatting with Prettier."""
    runner = LintRunner(verbose=verbose)
    if not runner.lint_typescript(check_only=check_only):
        raise typer.Exit(1)

@app.command()
def all(
    check_only: bool = typer.Option(False, "--check-only", help="Check only, don't fix"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Run linting for all languages."""
    runner = LintRunner(verbose=verbose)
    success = runner.lint_python(check_only=check_only)
    success &= runner.lint_typescript(check_only=check_only)

    if success:
        print("✅ All linting completed successfully")
    else:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
```

## Usage

```bash
# Start all services
uv run python start_services.py

# Run tests
uv run python run_tests.py all
uv run python run_tests.py unit
uv run python run_tests.py int
uv run python run_tests.py e2e
uv run python run_tests.py python
uv run python run_tests.py quality
uv run python run_tests.py ruff
uv run python run_tests.py ty
uv run python run_tests.py cc

# Lint code
uv run python lint.py all
uv run python lint.py python
uv run python lint.py typescript
uv run python lint.py all --check-only
```
