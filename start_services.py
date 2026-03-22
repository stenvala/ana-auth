#!/usr/bin/env python3
"""Local development service orchestrator for ana-auth."""

import atexit
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import psutil

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
UI_DIR = SRC_DIR / "ui"

API_PORT = 6784
UI_PORT = 6785


@dataclass
class ServiceOrchestrator:
    """Manages local development services with graceful shutdown."""

    processes: list[subprocess.Popen] = field(default_factory=list)

    def kill_port(self, port: int) -> None:
        """Kill any process listening on the given port."""
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    print(f"Killing process {conn.pid} ({proc.name()}) on port {port}")
                    proc.terminate()
                    proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass

    def start_api(self) -> subprocess.Popen:
        """Start the FastAPI backend with uvicorn."""
        print(f"Starting API on port {API_PORT}...")
        proc = subprocess.Popen(
            [
                "uv",
                "run",
                "uvicorn",
                "api.main:app",
                "--port",
                str(API_PORT),
                "--reload",
            ],
            cwd=SRC_DIR,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        self.processes.append(proc)
        return proc

    def start_ui(self) -> subprocess.Popen:
        """Start the Angular dev server."""
        print(f"Starting UI on port {UI_PORT}...")
        proc = subprocess.Popen(
            [
                "bash",
                "-c",
                f"source ~/.nvm/nvm.sh && nvm use && npx ng serve --port {UI_PORT} --proxy-config proxy.conf.json",
            ],
            cwd=UI_DIR,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        self.processes.append(proc)
        return proc

    def shutdown(self) -> None:
        """Gracefully terminate all managed processes."""
        print("\nShutting down services...")
        for proc in self.processes:
            if proc.poll() is None:
                proc.terminate()
        for proc in self.processes:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("All services stopped.")

    def run(self) -> None:
        """Start all services and wait for interrupt."""
        # Kill existing processes on our ports
        self.kill_port(API_PORT)
        self.kill_port(UI_PORT)

        # Register shutdown handler
        atexit.register(self.shutdown)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

        # Start services with staggered startup
        self.start_api()
        time.sleep(1)
        self.start_ui()

        print(f"\nServices running:")
        print(f"  API: http://localhost:{API_PORT}")
        print(f"  UI:  http://localhost:{UI_PORT}")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                for proc in self.processes:
                    if proc.poll() is not None:
                        print(
                            f"Process {proc.pid} exited with code {proc.returncode}"
                        )
                        self.shutdown()
                        sys.exit(1)
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()


def main() -> None:
    orchestrator = ServiceOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
