# Worker Service Template

Systemd service unit for background worker processes. Runs as `DIR_GROUP` (typically `stenvala`) — the directory owner — because the worker needs file system access to deployment directories.

## Template

Create this file in `mcc/{WORKER_SERVICE_NAME}` (e.g., `mcc/mcc-pipeline-worker.service`):

```ini
[Unit]
Description={{WORKER_DESCRIPTION}}
After=network.target

[Service]
Type=simple
User={{DIR_GROUP}}
Group={{DIR_GROUP}}
WorkingDirectory={{API_SYMLINK}}
Environment="ENV_TYPE=production"
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
Environment="DATA_DIR={{DATA_DIR}}"
ExecStart={{REMOTE_BASE}}/.venv/bin/python -m worker.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ENV_TYPE` | Always | Set to `production` on server |
| `LOG_ROOT` | Always | Directory for application log files (`worker.log`) |
| `DATA_DIR` | Typical | Persistent data directory for worker artifacts (build logs, deploy logs) |

## Why DIR_GROUP (not DIR_USER)?

The worker runs as the directory owner (`stenvala`) instead of the web server user (`www-data`) because:
- It needs read/write access to deployment directories
- It may execute build/deploy scripts that manipulate files
- The logs directory is `chown DIR_USER:DIR_GROUP` with `g+rw`, so both users can write logs

## Log Files

The worker writes its application log via `LOG_ROOT`:
- `{{REMOTE_BASE}}/logs/worker.log` — Application-level logging via `get_file_logger("worker")`

See backend-logger skill for the full logging architecture.
