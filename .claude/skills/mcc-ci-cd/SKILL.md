---
name: mcc-ci-cd
description: Deploy Python/Angular apps to Linux with nginx, systemd, and rsync
---

# MCC CI/CD Deployment Skill

This skill provides CI/CD deployment scripts and configurations for Python (FastAPI/uvicorn) + Angular web applications deployed to Linux servers with nginx reverse proxy and systemd service management.

## Directory Structure

The deployment scripts should be placed in a `mcc/` directory at the project root:

```
project/
├── src/
│   ├── api/           # FastAPI backend
│   ├── ui/            # Angular frontend
│   └── shared/        # Shared code including DB scripts
├── dist/              # Build output (generated)
├── mcc/               # Deployment scripts
│   ├── conf.yml       # Configuration
│   ├── config_loader.py
│   ├── build.py
│   ├── deploy_api.py
│   ├── deploy_ui.py
│   ├── deploy_database.py
│   ├── deploy_server.py
│   ├── deploy_scripts.py
│   ├── {service}.service
│   ├── {domain}       # nginx config(s)
│   ├── domains/       # Per-domain configs (multi-domain SQLite)
│   └── scripts/       # Remote scripts (backups, etc.)
├── all.sh             # Master deployment script
└── pyproject.toml
```

## Database Support

This skill supports two database configurations:

### SQLite (Multi-tenant, Multi-domain)
- Each domain has its own SQLite database in `domains/{domain}/data.db`
- Schema migrations tracked in `migrations` table
- Demo data seeding for new domains
- Used for CMS-style applications serving multiple domains

### PostgreSQL (Single-tenant)
- Centralized PostgreSQL database with named schemas
- SSH tunneling for remote database access from external networks
- Schema versioning via checksums in `_deployment_log` table
- Used for applications with complex data relationships

## Configuration

Copy `conf.yml.template` to `conf.yml` and customize:

```yaml
# Server connection
REMOTE_USER: username
REMOTE_HOST: server.example.com
REMOTE_BASE: /home/username/live/myapp

# File ownership (web server user)
DIR_USER: www-data
DIR_GROUP: username

# Build paths (relative to mcc/)
LOCAL_API_DIR: "../dist/api"
LOCAL_UI_DIR: "../dist/ui"

# Remote paths (use templates)
API_REMOTE_BUILDS: "{{REMOTE_BASE}}/api"
API_SYMLINK: "{{REMOTE_BASE}}/current-api"
UI_REMOTE_BUILDS: "{{REMOTE_BASE}}/ui"
UI_SYMLINK: "{{REMOTE_BASE}}/current-ui"

# Deployment settings
KEEP_BUILDS: 10
SERVICE_NAME: myapp.service
EMAIL: admin@example.com

# Single domain (PostgreSQL mode)
DOMAIN: "myapp.example.com"
NGINX_CONF: "{{DOMAIN}}"

# OR Multi-domain (SQLite mode)
DOMAINS:
  - domain1.example.com
  - domain2.example.com

# PostgreSQL settings (if using PostgreSQL)
DB_HOST: 192.168.0.150
DB_PORT: 5432
DB_NAME: postgres
DB_USER: postgres
DB_PASSWORD: postgres
DB_SCHEMA_SUFFIX: main
DB_LOCAL_NETWORK: 192.168.0.0/24
```

## Scripts Overview

### build.py
Builds the Angular UI and prepares API files for deployment:
- Uses nvm for consistent Node.js version
- Smart npm ci detection (skips if node_modules up-to-date)
- Copies API, shared code, and dependency files to dist/

### deploy_api.py
Deploys the API backend:
- Creates timestamped release directory
- Uploads via rsync
- Syncs virtual environment with `uv sync --frozen`
- Updates symlink atomically
- Sets up permissions for www-data
- Restarts systemd service
- Cleans up old releases

For SQLite mode, also handles:
- Schema refresh for all domains
- Running pending migrations
- Seeding demo data for new domains

### deploy_ui.py
Deploys the Angular frontend:
- Creates timestamped release directory
- Uploads via rsync
- Updates symlink atomically
- Sets permissions
- Cleans up old releases

### deploy_database.py (PostgreSQL mode only)
Deploys PostgreSQL schema:
- Detects network and uses SSH tunneling if needed
- Version tracking via schema file checksums
- Idempotent deployment (skips if already deployed)
- Creates system admin user

### deploy_server.py
Initial server configuration:
- Uploads systemd service file
- Uploads nginx configuration(s)
- Generates SSL certificates via Certbot
- Enables and starts services

### deploy_scripts.py
Deploys utility scripts and cron jobs:
- Syncs scripts directory to remote
- Sets up crontab for automated tasks (backups, etc.)
- Configures log files

### all.sh
Master deployment script with:
- Test execution (optional with --no-tests)
- Build step
- API deployment
- UI deployment
- Timing summary
- Full logging to .cicd/ directory

## Usage

### Full deployment with tests:
```bash
./all.sh
```

### Skip tests:
```bash
./all.sh --no-tests
```

### Individual deployments:
```bash
cd mcc
uv run build.py
uv run deploy_api.py
uv run deploy_ui.py
uv run deploy_database.py  # PostgreSQL only
uv run deploy_server.py    # Initial setup only
uv run deploy_scripts.py
```

## Nginx Configuration

### Single Domain
Standard configuration with:
- Rate limiting (10r/s, burst 20)
- Security headers
- API proxy to backend port
- WebSocket support
- Static asset caching (1 year)
- No-cache for index.html
- HTTP to HTTPS redirect
- Let's Encrypt SSL

### Multi-Domain
Additional features:
- Per-domain X-Domain header
- Social bot detection for OpenGraph
- Domain-specific SSL certificates
- Shared rate limiting zone

## Systemd Service

Template provides:
- User/group configuration (www-data)
- Gunicorn with Uvicorn workers
- Environment variables (ENV_TYPE, LOG_ROOT)
- Auto-restart on failure
- 10 second restart delay



