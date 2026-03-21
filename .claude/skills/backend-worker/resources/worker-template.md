# Worker Template

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
    audit_dir = str(get_audit_logs_dir())

    # Recover stale builds
    with DBContext.get_session() as session:
        # Example for Build model:
        # from shared.db.models.core_models.build import Build
        # from shared.db.models.core_models.core_enums import BuildStatus
        #
        # stale_builds = session.exec(
        #     select(Build).where(Build.status == BuildStatus.ONGOING)
        # ).all()
        # for build in stale_builds:
        #     build.status = BuildStatus.FAILED
        #     session.add(build)
        #     write_audit_entry(
        #         audit_dir, "BUILD_RECOVERY",
        #         f"Marked stale build {build.id} as failed (worker restart)",
        #     )
        # if stale_builds:
        #     print(f"Recovered {len(stale_builds)} stale build(s).")
        pass

    # Recover stale deployments (separate session for separate transaction)
    with DBContext.get_session() as session:
        # Similar pattern for Deployment model
        pass


def _poll_once() -> bool:
    """Check for pending work. Returns True if work was done.

    Processing priority:
    1. Builds (deployments depend on completed builds)
    2. Deployments (check environment exclusivity)
    3. Other task types
    """
    # --- Check for pending builds ---
    with DBContext.get_session() as session:
        # from shared.db.models.core_models.build import Build
        # from shared.db.models.core_models.core_enums import BuildStatus
        # from worker.build_processor import process_build
        #
        # pending_build = session.exec(
        #     select(Build)
        #     .where(Build.status == BuildStatus.PENDING)
        #     .order_by(Build.created_at)
        #     .limit(1)
        # ).first()
        # if pending_build:
        #     process_build(session, pending_build)
        #     return True
        pass

    # --- Check for pending deployments ---
    with DBContext.get_session() as session:
        # from shared.db.models.core_models.deployment import Deployment
        # from shared.db.models.core_models.core_enums import DeploymentStatus
        # from worker.deploy_processor import process_deployment
        #
        # pending_deployment = session.exec(
        #     select(Deployment)
        #     .where(Deployment.status == DeploymentStatus.PENDING)
        #     .order_by(Deployment.created_at)
        #     .limit(1)
        # ).first()
        # if pending_deployment:
        #     # Check environment exclusivity before processing
        #     if _can_deploy(session, pending_deployment):
        #         process_deployment(session, pending_deployment)
        #         return True
        pass

    return False


def _can_deploy(session, deployment) -> bool:
    """Check if deployment can proceed (no ongoing deploy to same environment)."""
    # from shared.db.models.core_models.deployment import Deployment
    # from shared.db.models.core_models.core_enums import DeploymentStatus
    #
    # ongoing = session.exec(
    #     select(Deployment)
    #     .where(Deployment.environment == deployment.environment)
    #     .where(Deployment.status == DeploymentStatus.ONGOING)
    # ).first()
    # return ongoing is None
    return True


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

## Task Processor Pattern

Create one file per task type at `src/worker/<task_type>_processor.py`:

```python
"""<TaskType> processor."""

import traceback
from datetime import datetime, timezone

from sqlmodel import Session

from shared.audit import write_audit_entry
from shared.common import get_audit_logs_dir
from shared.db.models.core_models.<task_type> import <TaskType>
from shared.db.models.core_models.core_enums import <TaskType>Status


def process_<task_type>(session: Session, task: <TaskType>) -> None:
    """Process a pending <task_type>.

    Status lifecycle: pending -> ongoing -> succeeded | failed

    Args:
        session: Active database session (will be committed by caller)
        task: Task model instance with status='pending'
    """
    audit_dir = str(get_audit_logs_dir())

    # 1. Mark as ongoing FIRST (commit immediately for crash recovery)
    task.status = <TaskType>Status.ONGOING
    task.started_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()

    write_audit_entry(
        audit_dir, "<TASK_TYPE>_STARTED",
        f"Processing <task_type> {task.id}",
    )

    try:
        # 2. Do the actual work
        _do_work(task)

        # 3. Mark as succeeded
        task.status = <TaskType>Status.SUCCEEDED
        task.completed_at = datetime.now(timezone.utc)
        session.add(task)

        write_audit_entry(
            audit_dir, "<TASK_TYPE>_SUCCEEDED",
            f"<TaskType> {task.id} completed successfully",
        )

    except Exception as e:
        # 4. Mark as failed on any error
        task.status = <TaskType>Status.FAILED
        task.completed_at = datetime.now(timezone.utc)
        session.add(task)

        error_msg = f"<TaskType> {task.id} failed: {e}"
        print(error_msg)
        traceback.print_exc()

        write_audit_entry(audit_dir, "<TASK_TYPE>_FAILED", error_msg)


def _do_work(task: <TaskType>) -> None:
    """Execute the actual task work.

    Raises:
        Exception: Any error causes the task to be marked as failed.
    """
    # Implementation goes here
    # e.g., clone repo, run build, deploy artifacts, etc.
    raise NotImplementedError("Processor not yet implemented")
```

## Environment Exclusivity Check

For deployments or any task that needs per-target exclusivity:

```python
from sqlmodel import select

from shared.db.models.core_models.deployment import Deployment
from shared.db.models.core_models.core_enums import DeploymentStatus


def can_deploy(session, deployment) -> bool:
    """Check if deployment can proceed.

    Only one deployment per environment can be ongoing at a time.
    """
    ongoing = session.exec(
        select(Deployment)
        .where(Deployment.environment == deployment.environment)
        .where(Deployment.status == DeploymentStatus.ONGOING)
    ).first()
    return ongoing is None
```

Use this in `_poll_once()` before calling the processor:

```python
pending_deployment = session.exec(
    select(Deployment)
    .where(Deployment.status == DeploymentStatus.PENDING)
    .order_by(Deployment.created_at)
    .limit(1)
).first()

if pending_deployment and can_deploy(session, pending_deployment):
    process_deployment(session, pending_deployment)
    return True
```

If `can_deploy` returns False, the deployment stays `pending` and will be retried on the next poll cycle (after the ongoing deployment finishes).

## Status Enum Pattern

Every task type needs a status enum:

```python
from enum import Enum

class TaskStatus(str, Enum):
    """Task status values."""
    PENDING = "pending"      # Waiting to be processed
    ONGOING = "ongoing"      # Currently being processed by worker
    SUCCEEDED = "succeeded"  # Completed successfully
    FAILED = "failed"        # Processing failed
```

And the corresponding SQLite schema column:

```sql
status TEXT NOT NULL DEFAULT 'pending'
    CHECK(status IN ('pending', 'ongoing', 'succeeded', 'failed')),
```

## Configuration

Add to `src/shared/common.py`:

```python
DEFAULT_WORKER_POLL_INTERVAL = 2  # seconds between polls when idle
```

## Systemd Service Template

Create `mcc/<project>-worker.service` for production deployment:

```ini
[Unit]
Description=<Project> Worker Service
After=network.target

[Service]
Type=simple
User=www-data
Group=<deploy_user>
WorkingDirectory=/home/<deploy_user>/live/<project>/current-api
ExecStart=/home/<deploy_user>/live/<project>/current-api/.venv/bin/python -m worker.main
Restart=always
RestartSec=10
Environment=ENV_TYPE=PROD
Environment=DATA_DIR=/home/<deploy_user>/live/<project>/data
Environment=PYTHONPATH=/home/<deploy_user>/live/<project>/current-api

[Install]
WantedBy=multi-user.target
```

## Adding Worker to start_services.py

The worker runs alongside API and UI in development:

```python
services = [
    ("api", ["uv", "run", "uvicorn", "api.main:app",
            "--host", "0.0.0.0", "--port", "<API_PORT>", "--reload"], Path("src")),
    ("worker", ["uv", "run", "python", "-m", "worker.main"], Path("src")),
    ("ui", ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "<UI_PORT>"], Path("src/ui")),
]
```

## API Side: Creating Tasks

From the API router/service, create pending tasks for the worker:

```python
from datetime import datetime, timezone

from shared.db.models.core_models.build import Build
from shared.db.models.core_models.core_enums import BuildStatus


def trigger_build(session, repository_id: int, branch: str, user_id: int) -> Build:
    """Create a pending build for the worker to pick up."""
    build = Build(
        repository_id=repository_id,
        branch=branch,
        commit_hash="",  # Will be resolved by worker
        status=BuildStatus.PENDING,
        triggered_by_user_id=user_id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(build)
    # Session commit handled by middleware/context manager
    return build
```

The worker will pick this up on its next poll cycle (within `DEFAULT_WORKER_POLL_INTERVAL` seconds).

## Testing Workers

### Unit Testing Processors

Test processors in isolation by passing mock sessions:

```python
from unittest.mock import MagicMock

from worker.build_processor import process_build


def test_process_build_marks_ongoing():
    """Test that processor marks build as ongoing first."""
    session = MagicMock()
    build = MagicMock()
    build.id = 1
    build.status = "pending"

    process_build(session, build)

    # Verify status was set to ongoing
    assert build.status in ("ongoing", "succeeded", "failed")
```

### Integration Testing

Use the `db_session` fixture from conftest.py to test with a real database:

```python
def test_poll_picks_oldest_pending(db_session):
    """Test that polling picks the oldest pending task."""
    # Create two pending builds with different timestamps
    # Poll once
    # Verify the older one was picked
```
