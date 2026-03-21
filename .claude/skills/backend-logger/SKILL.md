---
name: backend-logger
description: Backend logging patterns for Python API and worker processes. Use when adding logging to new services, routers, or worker processors, building API middleware, or setting up transaction ID correlation. Covers logger injection, file-only loggers, StructuredLogger, and the middleware-to-service logging chain.
---

# Backend Logger

## Resources

- [resources/logging.py](resources/logging.py) — Reference implementation of the logging module
- [resources/logging-patterns.md](resources/logging-patterns.md) — Detailed code examples for API middleware, dependency injection, worker patterns

For **infrastructure** concerns (log file ownership, systemd LOG_ROOT config, nginx logs, remote permissions, troubleshooting remote logs), see the **mcc-infra** skill's `resources/logging-infrastructure.md`.

## Core Principle: Logger Injection

**All services accept `logger: logging.Logger` as the first constructor argument.** The logger is never created inside a service — it is always injected from the caller:

- **API context**: Middleware initializes the logger and stores it on `request.state`. Dependency injectors extract it and pass it to services.
- **Worker context**: The worker entry point initializes the logger. Processors and services receive it as an argument.

## Logger Factory Functions

| Function | Output | Use case |
|----------|--------|----------|
| `get_file_logger(name)` | File only (no stdout) | API and worker processes |
| `get_logger(name, add_file_handler=True)` | Stdout + optional file | Local dev orchestrator |

Both use `ReadableFormatter` and `RotatingFileHandler` (1 MB, 10 backups).

```python
from shared.logging import get_file_logger
logger = get_file_logger("api")  # writes to {LOG_ROOT}/api.log
logger = get_file_logger("worker", force_reconfigure=True)  # fresh handles after fork
```

`force_reconfigure=True` clears existing handlers (needed after fork/reload). Falls back to console on `OSError`.

## Transaction IDs

Correlate all log lines for a single request or job. Uses `ContextVar` — safe for async/concurrent contexts.

```python
from shared.logging import set_transaction_id
set_transaction_id("some-correlation-id")
# All output: [some-correlation-id] 2025-... - name - INFO - message
set_transaction_id("")  # clear when done
```

## StructuredLogger

Wraps a standard logger to append `| key=value` fields:

```python
from shared.logging import StructuredLogger
structured = StructuredLogger(logger)
structured.info("REQUEST_START", method="GET", path="/api/health")
# => 2025-... - api - INFO - REQUEST_START | method=GET path=/api/health
```

## Service Constructor Pattern

Every service takes `logger` as the first argument, followed by `session`:

```python
class SomeService:
    def __init__(self, logger: logging.Logger, session: Session) -> None:
        self.logger = logger
        self.session = session
        self.some_repo = SomeRepository(session)
```

## When to Use What

| Context | Logger source | Transaction ID | Error handling |
|---------|--------------|----------------|----------------|
| API middleware | `get_file_logger("api")` + `StructuredLogger` | `set_transaction_id(request_id)` | Middleware catches all |
| API dependency injectors | `request.state.logger` | Inherited | Let exceptions bubble |
| API services/routers | `self.logger` (injected) | Inherited | Let exceptions bubble |
| Worker main loop | `get_file_logger("worker")` | `set_transaction_id(f"job-{id}")` | Caught in poll loop |
| Worker processors | `logger` argument | Inherited | Let exceptions bubble |
| Per-job output | `append_to_log()` / `run_script()` | N/A (separate file) | Written to data dir |

## Local Troubleshooting

```python
from shared.logging import diagnose_logging
diagnose_logging()
```

