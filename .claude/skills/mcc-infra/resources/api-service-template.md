# API Service Template

Systemd service unit for the FastAPI/Gunicorn API process. Runs as `DIR_USER` (typically `www-data`).

## Template

Create this file in `mcc/{SERVICE_NAME}` (e.g., `mcc/mcc-pipeline.service`):

```ini
[Unit]
Description={{DESCRIPTION}}
After=network.target

[Service]
Type=simple
User={{DIR_USER}}
Group={{DIR_USER}}
WorkingDirectory={{API_SYMLINK}}
Environment="ENV_TYPE=production"
Environment="STAGE={{STAGE}}"
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
Environment="LOG_LEVEL={{LOG_LEVEL}}"
ExecStart={{REMOTE_BASE}}/.venv/bin/gunicorn api.main:app \
    --workers {{WORKERS}} \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:{{API_PORT}} \
    --access-logfile {{REMOTE_BASE}}/logs/access-gunicorn.log \
    --error-logfile {{REMOTE_BASE}}/logs/error-gunicorn.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ENV_TYPE` | Always | Set to `production` on server |
| `LOG_ROOT` | Always | Directory for application log files (`api.log`) |
| `STAGE` | Optional | Stage identifier (e.g., `prod`, `dev`) — include when the app reads `STAGE` |
| `LOG_LEVEL` | Optional | Python log level — include when the app reads `LOG_LEVEL` |
| `DATA_DIR` | Optional | Persistent data directory — add `Environment="DATA_DIR={{DATA_DIR}}"` if the app uses it |

## Customization

### Add DATA_DIR (for apps with persistent data):
```ini
Environment="DATA_DIR={{DATA_DIR}}"
```

### Remove optional variables:
If the app doesn't use `STAGE` or `LOG_LEVEL`, remove those `Environment=` lines from the template.

## Log Files

Gunicorn writes two log files directly:
- `{{REMOTE_BASE}}/logs/access-gunicorn.log` — HTTP access log
- `{{REMOTE_BASE}}/logs/error-gunicorn.log` — Gunicorn errors and startup messages

The application writes its own log via `LOG_ROOT`:
- `{{REMOTE_BASE}}/logs/api.log` — Application-level logging via `get_file_logger("api")`

See backend-logger skill for the full logging architecture.
