# Deploy Patterns (`mcc_deploy.py`)

## Overview

The deploy script runs on the remote server from within the build output directory. It receives a `--stage` argument and reads `config.yml` to determine what to do. It uses `typer` for CLI argument parsing.

**Critical**: The deploy script's working directory contains only what was placed in `output/` during build. No access to the full repository.

## Permission Model

The deploy script runs as `DIR_GROUP` (directory owner user). Key constraints:

- **Services (nginx, backend daemons) run as `DIR_USER`** (execution user), not `DIR_GROUP`
- `DIR_GROUP` is the directory owner who owns the deployment base path
- `DIR_GROUP` **cannot** edit systemd unit files or nginx configs — these must be set up manually or via a separate privileged process
- `DIR_GROUP` **can** restart services via visudo-allowed `sudo /bin/systemctl restart <service>`
- `DIR_GROUP` **can** `chown` and `chmod` files within the deployment directory
- Files are owned by `DIR_USER:DIR_GROUP` with group read/write so both the service and deploy user can access them

**mcc_deploy.py cannot deploy service definitions or nginx configs.** It can only deploy application code, run migrations, deploy cron jobs, and restart existing services.

## Stage Routing via `config.yml`

Top-level key is `deploy`. Each child is a stage name with these keys:

- `allow_branches` - regex: which branches are allowed to deploy this stage
- `auto_branches` - regex: which branches auto-trigger this stage (`"-"` = never)
- `parameters` - **free-form key-value bag** (any keys you want, visible in MCC pipeline UI)
- `link` - optional URL shown in MCC pipeline UI for this stage (e.g. link to the deployed environment)

The deploy script reads `config["deploy"][stage]["parameters"]` and uses whatever keys it needs.

```yaml
deploy:
  prod:
    allow_branches: "^main$"
    auto_branches: "^main$"
    link: "https://myapp.example.com" # optional: shown in MCC UI
    parameters: # free-form: put whatever your deploy script needs
      conf: conf-prod.yml # convention: which conf file to load
      keep_builds: 10 # convention: how many old versions to keep
  dev:
    allow_branches: ".*"
    auto_branches: ".*"
    link: "https://dev.myapp.example.com"
    parameters:
      conf: conf-dev.yml
      keep_builds: 5
  clone-prod-to-dev: # non-deployment stage
    allow_branches: ".*"
    auto_branches: "-" # never auto-trigger
    parameters:
      conf-source: conf-prod.yml
      conf-target: conf-dev.yml
```

## Stage Configuration (`conf-{stage}.yml`)

```yaml
# Server connection
REMOTE_USER: deploy_user
REMOTE_HOST: server.example.com
REMOTE_BASE: /home/deploy_user/live/myapp-prod

# File ownership
DIR_USER: www-data # execution user: runs nginx and backend service daemons
DIR_GROUP: deploy_user # directory owner: the user who owns the deployment base

# Services to restart (single service)
SERVICE_NAME: myapp-prod.service

# Or multiple services
# SERVICES:
#   - myapp-prod-api.service
#   - myapp-prod-worker.service

# Stage identifier
STAGE: prod
API_PORT: 8000
WORKERS: 4

# Domain configuration (multi-tenant)
DOMAINS:
  - app.example.com
  - app.client2.com

# Or single-tenant (no DOMAINS key, or empty)
# DOMAINS: []

# Backup configuration (optional)
BACKUP_ENABLED: true
BACKUP_PATH: "{{REMOTE_BASE}}/backups"
BACKUP_RETENTION_DAILY: 7
BACKUP_RETENTION_WEEKLY: 4
```

## Deployment Flow

### 1. Version Directory Creation

Use timestamped versioned directories for zero-downtime deployments:

```python
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")
version_name = f"vrs-{timestamp}"

api_builds_dir = deployment_path / "api"
api_version_dir = api_builds_dir / version_name
api_version_dir.mkdir(parents=True, exist_ok=True)
```

Result on disk:

```
/home/deploy_user/live/myapp-prod/
  api/
    vrs-2026-02-27T143000/   # previous
    vrs-2026-02-27T150000/   # new
  ui/
    vrs-2026-02-27T143000/
    vrs-2026-02-27T150000/
  current-api -> api/vrs-2026-02-27T150000   # symlink
  current-ui  -> ui/vrs-2026-02-27T150000    # symlink
  domains/          # multi-tenant data (per-domain DBs, configs)
  backups/          # database backups (daily/, weekly/)
  data/             # persistent application data
  logs/             # application and backup logs
  scripts/          # deployed scripts (backup, maintenance)
  .venv/            # shared virtual environment
  pyproject.toml
  uv.lock
```

### 2. Copy Build Artifacts

```python
def copy_api_files(cwd: Path, version_dir: Path):
    shutil.copytree(cwd / "api", version_dir / "api")
    shutil.copytree(cwd / "shared", version_dir / "shared")

def copy_ui_files(cwd: Path, version_dir: Path):
    shutil.copytree(cwd / "ui", version_dir, dirs_exist_ok=True)
```

### 3. Virtual Environment Sync

```python
def sync_virtual_environment(cwd: Path, deployment_path: Path):
    shutil.copy2(cwd / "pyproject.toml", deployment_path / "pyproject.toml")
    shutil.copy2(cwd / "uv.lock", deployment_path / "uv.lock")
    run(["uv", "sync", "--frozen"], cwd=deployment_path)
```

### 4. Symlink Update

```python
def update_symlinks(deployment_path, api_version_dir, ui_version_dir):
    for name, target in [("current-api", api_version_dir), ("current-ui", ui_version_dir)]:
        link = deployment_path / name
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(target)
```

### 5. Service Restart

```python
def restart_service(service_name: str):
    run(["sudo", "/bin/systemctl", "restart", service_name])
    time.sleep(5)
    run(["sudo", "/bin/systemctl", "status", service_name])
```

For multiple services:

```python
def restart_services(services: list[str]):
    for service_name in services:
        restart_service(service_name)
```

### 6. Version Cleanup

```python
def cleanup_old_versions(builds_dir: Path, keep_count: int):
    dirs = sorted(
        [d for d in builds_dir.iterdir() if d.is_dir() and d.name.startswith("vrs-")],
        key=lambda p: p.name, reverse=True,
    )
    for old_dir in dirs[keep_count:]:
        shutil.rmtree(old_dir)
```

### 7. Smoke Tests

```python
def smoke_test(domains: list[str]):
    for domain in domains:
        for url in [f"https://{domain}/", f"https://{domain}/api/public/health/health"]:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                raise RuntimeError(f"Smoke test failed: {url} returned {resp.status_code}")
```

### 8. Permissions

```python
def setup_permissions(deployment_path, builds_dir, dir_user, dir_group):
    run(["sudo", "chown", "-R", f"{dir_user}:{dir_group}", str(builds_dir)])
    run(["sudo", "chmod", "-R", "g+rw", str(builds_dir)])
    # Also handle .venv, domains, logs directories
```

## Database Migrations

### Multi-Tenant (Per-Domain Databases)

Each domain has its own database. Migrations run for every domain:

```python
def run_migrations(deployment_path, api_version_dir, domains):
    migrations_dir = api_version_dir / "shared" / "db" / "scripts" / "migrations"
    if not migrations_dir.exists():
        return

    for domain in domains:
        db_path = deployment_path / "domains" / domain / "data.db"
        # Ensure migrations tracking table
        run(["sqlite3", str(db_path),
             "CREATE TABLE IF NOT EXISTS migrations "
             "(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, "
             "applied_at INTEGER DEFAULT (strftime('%s', 'now')))"])

        for migration_file in sorted(migrations_dir.glob("*.sql")):
            name = migration_file.stem
            # Check if already applied
            result = run(["sqlite3", str(db_path),
                         f"SELECT COUNT(*) FROM migrations WHERE name='{name}'"],
                        capture_output=True, text=True)
            if int(result.stdout.strip()) > 0:
                continue
            # Apply
            run(["sqlite3", str(db_path), f".read {migration_file}"])
            run(["sqlite3", str(db_path),
                 f"INSERT INTO migrations (name) VALUES ('{name}')"])
```

### Single-Tenant (One Database)

```python
def run_migrations(deployment_path, api_version_dir):
    migrations_dir = api_version_dir / "migrations"
    db_path = deployment_path / "data.db"
    # Same migration logic, just no domain loop
```

### PostgreSQL Migrations

```python
def run_migrations(deployment_path, api_version_dir):
    migrations_dir = api_version_dir / "migrations"
    db_url = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/mydb")
    # Use psql or alembic
    run(["alembic", "upgrade", "head"], cwd=deployment_path,
        env={**os.environ, "DATABASE_URL": db_url})
```

## Cron Job Deployment

```python
def deploy_cron_jobs(deployment_path, scripts_dir, cron_entries):
    """Deploy cron jobs from configuration.

    cron_entries example:
    [
        {"schedule": "0 2 * * *", "script": "backup.sh", "log": "backup.log", "marker": "MCC-BACKUP"},
        {"schedule": "*/5 * * * *", "script": "health_check.sh", "log": "health.log", "marker": "MCC-HEALTH"},
    ]
    """
    log_dir = deployment_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    for entry in cron_entries:
        script_path = scripts_dir / entry["script"]
        run(["chmod", "+x", str(script_path)])

        cron_line = f'{entry["schedule"]} cd {scripts_dir} && ./{entry["script"]} >> {log_dir}/{entry["log"]} 2>&1'
        marker = f'# {entry["marker"]}'
        cron_cmd = (
            f'(crontab -l 2>/dev/null | grep -v "{marker}" || true; '
            f'echo "{marker}"; echo "{cron_line}") | crontab -'
        )
        run(["bash", "-c", cron_cmd])
```

## Non-Deployment Stages

Non-deployment stages use the same `--stage` routing but perform different operations instead of the standard deploy flow.

### Example: Clone Prod to Dev

```python
def main(stage: str = typer.Option(...)):
    config = yaml.safe_load(Path("config.yml").read_text())
    stage_config = config["deploy"][stage]
    params = stage_config.get("parameters", {})

    if stage == "clone-prod-to-dev":
        prod_conf = load_conf(cwd, params.get("conf-source", "conf-prod.yml"))
        dev_conf = load_conf(cwd, params.get("conf-target", "conf-dev.yml"))
        clone_prod_to_dev(prod_conf, dev_conf)
        return

    # Normal deployment
    conf = load_conf(cwd, params.get("conf", "conf.yml"))
    deploy(params.get("keep_builds", 10), conf)
```

Other possible non-deployment stages:

- `reset-dev`: wipe dev environment and redeploy
- `db-backup`: trigger manual backup
- `db-restore`: restore from backup
- `maintenance-on/off`: toggle maintenance mode

## Entry Point Pattern

```python
import typer

def main(
    stage: str = typer.Option(..., help="Deployment stage"),
) -> None:
    try:
        # ... stage routing and deployment logic
        pass
    except Exception as e:
        print(f"Deployment failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("Starting deployment", flush=True)
    app = typer.Typer()
    app.command()(main)
    app()
    print("Finished deployment", flush=True)
```

## `build_info.yml` Schema

This file is created by the MCC pipeline service at build time in the project root. Copy it to `output/` in the build script so it's available during deployment.

```yaml
build_number: 18
timestamp:
  start: 1772174260
  end: null
branch: main
commit_sha: 5807d5d45623363cc93902b99bb0a0991c77d8df
committer:
  name: Jane Doe
  email: jane@example.com
  commit_message: Some git commit message
```

Use at deploy time for logging:

```python
build_info_path = cwd / "build_info.yml"
if build_info_path.exists():
    info = yaml.safe_load(build_info_path.read_text())
    print(f"Deploying build #{info.get('build_number')} from {info.get('branch')} @ {info.get('commit_sha', '?')[:8]}")
```
