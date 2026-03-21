# Worker Setup Reference

## Worker Entry Point

Create `src/worker/main.py`:

```python
"""Worker entry point with database polling loop."""

import signal
import sys
import time

from shared.audit import write_audit_entry
from shared.common import DEFAULT_WORKER_POLL_INTERVAL, get_audit_logs_dir
from shared.db.db_context import DBContext

from sqlmodel import select

_running = True


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _running
    print(f"Received signal {signum}, shutting down...")
    _running = False


def _recover_stale_tasks() -> None:
    """Mark any ongoing tasks as failed on startup (crash recovery).

    This handles the case where the worker crashed mid-processing.
    Any tasks left in 'ongoing' state are marked as 'failed'.
    """
    # Example for builds:
    # with DBContext.get_session() as session:
    #     stale = session.exec(
    #         select(Build).where(Build.status == BuildStatus.ONGOING)
    #     ).all()
    #     for item in stale:
    #         item.status = BuildStatus.FAILED
    #         session.add(item)
    #     if stale:
    #         print(f"Recovered {len(stale)} stale build(s).")
    pass


def _poll_once() -> bool:
    """Check for pending work. Returns True if work was done.

    Processing order:
    1. Check for pending builds (FIFO by created_at)
    2. Check for pending deployments (FIFO by created_at, one per environment)
    """
    # Example:
    # with DBContext.get_session() as session:
    #     pending = session.exec(
    #         select(Task)
    #         .where(Task.status == "pending")
    #         .order_by(Task.created_at)
    #         .limit(1)
    #     ).first()
    #     if pending:
    #         process_task(session, pending)
    #         return True
    return False


def run_worker() -> None:
    """Run the worker polling loop."""
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    print("Worker starting...")
    DBContext._get_engine()
    _recover_stale_tasks()

    audit_dir = str(get_audit_logs_dir())
    write_audit_entry(audit_dir, "WORKER_STARTED", "Worker polling loop started")
    print("Worker polling loop started.")

    while _running:
        try:
            did_work = _poll_once()
            if not did_work:
                time.sleep(DEFAULT_WORKER_POLL_INTERVAL)
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(DEFAULT_WORKER_POLL_INTERVAL)

    write_audit_entry(audit_dir, "WORKER_STOPPED", "Worker polling loop stopped")
    DBContext.dispose_engine()
    print("Worker shut down.")


if __name__ == "__main__":
    run_worker()
```

## Stub Processor Files

Create `src/worker/build_processor.py`:

```python
"""Build task processor."""


def process_build(session, build):
    """Process a pending build.

    Args:
        session: Database session
        build: Build model instance with status='pending'
    """
    # TODO: Implement build processing
    # 1. Mark build as 'ongoing'
    # 2. Clone/pull repository
    # 3. Run build commands
    # 4. Store build artifacts
    # 5. Mark build as 'completed' or 'failed'
    pass
```

Create `src/worker/deploy_processor.py`:

```python
"""Deployment task processor."""


def process_deployment(session, deployment):
    """Process a pending deployment.

    Args:
        session: Database session
        deployment: Deployment model instance with status='pending'
    """
    # TODO: Implement deployment processing
    # 1. Check no other deployment is ongoing for same environment
    # 2. Mark deployment as 'ongoing'
    # 3. Deploy build artifacts to target environment
    # 4. Mark deployment as 'completed' or 'failed'
    pass
```

## Queuing Guarantees

The worker enforces these rules:

1. **Sequential builds**: Only one build processes at a time. The polling loop picks one pending build, processes it completely, then checks for the next.

2. **One deployment per environment**: Before starting a deployment, check if another deployment is ongoing for the same environment:

```python
def _can_deploy(session, deployment) -> bool:
    """Check if deployment can proceed (no ongoing deploy to same env)."""
    ongoing = session.exec(
        select(Deployment)
        .where(Deployment.environment == deployment.environment)
        .where(Deployment.status == DeploymentStatus.ONGOING)
    ).first()
    return ongoing is None
```

3. **FIFO ordering**: Tasks ordered by `created_at` timestamp.

4. **Crash recovery**: On startup, mark all `ongoing` tasks as `failed`.

## Adding Worker to start_services.py

Add the worker to the services list in `start_services.py`:

```python
services = [
    ("api", ["uv", "run", "uvicorn", "api.main:app",
            "--host", "0.0.0.0", "--port", "<API_PORT>", "--reload"], Path("src")),
    ("worker", ["uv", "run", "python", "-m", "worker.main"], Path("src")),
    ("ui", ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "<UI_PORT>"], Path("src/ui")),
]
```

## Configuration

Add to `src/shared/common.py`:

```python
DEFAULT_WORKER_POLL_INTERVAL = 2  # seconds between polls
```
