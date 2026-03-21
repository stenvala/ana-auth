# Logging Patterns — Detailed Examples

## API Middleware Pattern

The API logger is initialized once at module level and wrapped in `StructuredLogger`. The middleware stores the raw logger on `request.state` so dependency injectors can pass it to services:

```python
from shared.logging import StructuredLogger, get_file_logger, set_transaction_id

api_logger = get_file_logger("api")

class ApiMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = StructuredLogger(api_logger)

    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        set_transaction_id(request_id)

        # Make logger available to dependency injectors via request.state
        request.state.logger = api_logger

        self.logger.info("REQUEST_START", method=request.method, path=str(request.url.path))
        response = await call_next(request)
        self.logger.info("REQUEST_END", method=request.method, path=str(request.url.path), status_code=response.status_code)
        return response
```

The middleware handles ALL error logging — services and routers do NOT catch or log exceptions.

## Gunicorn Multiprocessing

Each gunicorn worker forks and needs fresh file handles:

```python
def reinit_logging_on_worker_start(worker):
    get_file_logger("api", force_reconfigure=True)
```

## Dependency Injection: Logger to Services

All service dependency injectors live in a dedicated dependencies module, NOT in router files. The logger is extracted from `request.state` (set by middleware) and injected into every service:

```python
# dependencies/database.py
def get_db_session() -> Generator[Session, None, None]:
    with DBContext.get_session() as session:
        yield session

# dependencies/services.py
def get_logger(request: Request) -> logging.Logger:
    return request.state.logger

def get_some_service(
    logger: logging.Logger = Depends(get_logger),
    session: Session = Depends(get_db_session),
) -> SomeService:
    return SomeService(logger, session)

# dependencies/auth.py
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    logger: logging.Logger = Depends(get_logger),
    session: Session = Depends(get_db_session),
) -> SafeUserDTO:
    auth_service = AuthService(logger, session)
    return auth_service.validate_session(credentials.credentials)
```

## Router Pattern

Routers import dependency functions and use them with `Depends()`. They never create services directly:

```python
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_some_service

@router.get("")
def list_items(
    current_user: dict = Depends(get_current_user),
    service: SomeService = Depends(get_some_service),
) -> ItemListResponseDTO:
    return service.list_items()
```

## Worker Logging Pattern

### Logger initialization

```python
from shared.logging import get_file_logger, set_transaction_id

logger = get_file_logger("worker", force_reconfigure=True)
logger.setLevel(log_level)  # INFO in production, DEBUG in development
```

### Transaction IDs per job

```python
set_transaction_id(f"job-{job.id}")
try:
    process_job(session, job, logger)
finally:
    set_transaction_id("")
```

### Processors receive logger as argument

```python
def process_job(session: Session, job: Job, logger: logging.Logger) -> None:
    some_service = SomeService(logger, session)
    another_service = AnotherService(logger, session)
    # ...
```

### Per-job log files

Separate from the worker logger, each job can write detailed output to its own log file:

```python
from worker.common import append_to_log, run_script

append_to_log(log_file_path, "Job started\n")
exit_code = run_script(command, work_dir, log_file_path, "Running job")
```
