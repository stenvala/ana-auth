---
name: backend-worker
description: Create background worker processes with database polling queues
---

# Backend Worker Creation

Create background worker processes that poll the database for pending tasks and process them sequentially with concurrency guarantees.

## When to Use

- Adding background processing (builds, deployments, imports, exports)
- Creating a polling-based task queue using the existing database
- Need sequential processing guarantees (one build at a time, one deploy per environment)
- Adding crash recovery for in-progress tasks

## Architecture Overview

The worker uses **database polling** as its queuing mechanism. No external message broker needed -- SQLite (or PostgreSQL) acts as the durable queue.

```
API (write)                    Worker (read + process)
    |                               |
    |  INSERT build                 |  SELECT ... WHERE status='pending'
    |  status='pending'             |  ORDER BY created_at LIMIT 1
    |         |                     |         |
    |         v                     |         v
    |   +------------------+        |  UPDATE status='ongoing'
    |   |   SQLite / DB    | <------+  ... process ...
    |   +------------------+        |  UPDATE status='succeeded'/'failed'
```

### How It Works

1. **API creates tasks**: Inserts records with `status = "pending"` into the database
2. **Worker polls**: Every N seconds, queries for the oldest pending task (FIFO by `created_at`)
3. **Worker processes**: Marks task as `"ongoing"`, does the work, marks as `"succeeded"` or `"failed"`
4. **Crash recovery**: On startup, any `"ongoing"` tasks are marked as `"failed"` (worker must have crashed)
5. **One at a time**: Worker picks only one pending task per poll cycle. For per-environment exclusivity (e.g., deployments), check for ongoing tasks before starting

## Prerequisites

1. Database schema must have task tables with a `status` column (use `/database-setup-sqlite` or `/database-setup-postgres`)
2. Task model must exist with status enum (use `/database-model`)
3. Shared common module must have `DEFAULT_WORKER_POLL_INTERVAL` and `get_audit_logs_dir()`

## File Locations

- **Worker entry point**: `main.py` in the worker module
- **Task processors**: `<task_type>_processor.py` in the worker module
- **Task models**: Task model files in the shared DB models module, organized by domain
- **Task enums**: Enum files in the shared DB models module, organized by domain
- **Services** (shared): `<feature>_service.py` in the shared services module, organized by domain

## Instructions

### 1. Create Status Enum

Ensure your task table has a status enum with at least these values:

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    ONGOING = "ongoing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
```

### 2. Create Worker Entry Point

Create the worker entry point from `resources/worker-template.md`. This contains:

- Signal handlers for graceful shutdown (SIGTERM, SIGINT)
- Database engine initialization
- Stale task recovery on startup
- Polling loop with configurable interval
- Error handling per poll cycle

### 3. Create Task Processors

Create one processor file per task type in the worker module. Each processor:

- Receives a database session and task model instance
- Marks task as `ongoing` at start
- Performs the actual work
- Marks task as `succeeded` or `failed`
- Logs progress via audit trail

### 4. Add Environment-Based Concurrency Checks

For tasks that need per-environment exclusivity (e.g., deployments):

```python
def _can_deploy(session, deployment) -> bool:
    ongoing = session.exec(
        select(Deployment)
        .where(Deployment.environment == deployment.environment)
        .where(Deployment.status == DeploymentStatus.ONGOING)
    ).first()
    return ongoing is None
```

### 5. Register Worker in Service Orchestrator

Add the worker to the service orchestrator:

```python
("worker", ["uv", "run", "python", "-m", "worker.main"], Path("src")),
```

### 6. Create Systemd Service (for production)

Create a systemd unit file for the worker process. See `resources/worker-template.md` for the template.

## Key Rules

1. **Sequential processing**: Worker processes ONE task at a time. No threading, no async concurrency in the polling loop
2. **Status lifecycle**: `pending` -> `ongoing` -> `succeeded` | `failed`. Never skip states
3. **Mark ongoing FIRST**: Before doing any work, update status to `ongoing` and commit. This ensures crash recovery works
4. **Separate sessions**: Use a fresh database session for each poll cycle. Do not hold sessions across polls
5. **Audit everything**: Log task start, completion, and failure to the audit trail
6. **Graceful shutdown**: Respect SIGTERM/SIGINT. Finish current task before exiting if possible
7. **No task loss**: If the worker crashes, the task remains `ongoing` and gets recovered to `failed` on next startup. The user can then retry
8. **Environment exclusivity**: For deployments, check that no other deployment is `ongoing` for the same target environment before starting
9. **Idempotent processors**: Design processors so they can be safely retried after failure

## Polling Loop

Poll in a loop: if work found, process immediately (no sleep); if no work or error, sleep for the poll interval. Within each cycle, check task types in priority order (e.g., builds before deployments).

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Task processing fails | Mark task as `failed`, log error, continue polling |
| Database connection error | Log error, sleep, retry on next cycle |
| Worker crash (SIGKILL) | On next startup, recover stale `ongoing` tasks to `failed` |
| Graceful shutdown (SIGTERM) | Finish current task, then exit cleanly |

## Templates

See `resources/` folder for:
- `worker-template.md` - Complete worker entry point, processor pattern, systemd service, and concurrency checks

