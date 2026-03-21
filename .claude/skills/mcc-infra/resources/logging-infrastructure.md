# Logging Infrastructure

Server-side logging setup: log files, directory permissions, systemd environment, and troubleshooting.

## Log Files

All logs go to `{{REMOTE_BASE}}/logs/`.

| File | Writer | Owner (remote) | Created by |
|------|--------|----------------|------------|
| `api.log` / `api.log.1`..`.10` | API process (gunicorn workers) | `DIR_USER:DIR_USER` | Application `get_file_logger("api")` |
| `worker.log` / `worker.log.1`..`.10` | Worker process | `DIR_GROUP:DIR_GROUP` | Application `get_file_logger("worker")` |
| `access-gunicorn.log` | Gunicorn | `DIR_USER:DIR_USER` | Gunicorn `--access-logfile` flag |
| `error-gunicorn.log` | Gunicorn | `DIR_USER:DIR_USER` | Gunicorn `--error-logfile` flag |
| `access-nginx.log` | Nginx | `DIR_USER:root` | Nginx `access_log` directive |
| `error-nginx.log` | Nginx | `DIR_USER:root` | Nginx `error_log` directive |

## LOG_ROOT Environment Variable

Both systemd service files set `LOG_ROOT` so the application knows where to write:

```ini
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
```

Locally, `LOG_ROOT` defaults to `{repo_root}/logs` if not set.

## Directory Setup & Permissions

During deployment, the logs directory must be created with shared ownership:

```python
c.run(f"mkdir -p {remote_base}/logs")
c.run(f"sudo chown {dir_user}:{dir_group} {remote_base}/logs")
c.run(f"sudo chmod g+rw {remote_base}/logs")
```

The logs directory is owned by `DIR_USER:DIR_GROUP`, which allows:
- The API service (runs as `DIR_USER`) to write `api.log`, gunicorn logs
- The worker service (runs as `DIR_GROUP`) to write `worker.log`
- Nginx (runs as `DIR_USER`, root for error log) to write nginx logs

## Service Users

| Service | User | Group | Configured in |
|---------|------|-------|---------------|
| API (gunicorn) | `DIR_USER` | `DIR_USER` | API service file |
| Worker | `DIR_GROUP` | `DIR_GROUP` | Worker service file |
| Nginx | `DIR_USER` | root (for error log) | System default |

## Nginx Logs

Configured in the nginx site config:

```nginx
access_log {{REMOTE_BASE}}/logs/access-nginx.log;
error_log {{REMOTE_BASE}}/logs/error-nginx.log;
```

No built-in rotation; relies on system logrotate.

## Troubleshooting Remote Logs

```bash
# Via systemd journal
sudo journalctl -u {{SERVICE_NAME}} -n 50 --no-pager
sudo journalctl -u {{WORKER_SERVICE_NAME}} -n 50 --no-pager

# Direct log files
tail -f {{REMOTE_BASE}}/logs/api.log
tail -f {{REMOTE_BASE}}/logs/worker.log
```

### Common issues

- **Permission denied writing logs**: Ensure logs dir is `chown DIR_USER:DIR_GROUP` with `chmod g+rw`
- **Gunicorn workers don't log**: Missing `force_reconfigure=True` on worker start causes stale file handles after fork
- **Logs go to stdout instead of file**: `LOG_ROOT` not set or directory not writable; file logger falls back to console with a stderr warning
