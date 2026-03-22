"""Shared utilities for MCC build and deploy scripts."""

import subprocess
import sys


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, print it, and fail immediately on non-zero exit code."""
    if (
        len(cmd) >= 2
        and cmd[0] == "uv"
        and cmd[1] == "run"
        and sys.platform != "darwin"
    ):
        if len(cmd) < 3 or cmd[2] != "--frozen":
            cmd = [cmd[0], cmd[1], "--frozen"] + cmd[2:]
    print("Running command:", " ".join(cmd), flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    check = kwargs.pop("check", True)
    result = subprocess.run(cmd, check=check, **kwargs)
    return result
