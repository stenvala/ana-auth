# Technical Specification: MCC Pipeline and Deployment

**Domain**: auth/deployment
**Last updated**: 2026-03-24

## Overview

Custom build/deploy pipeline following MCC patterns. Build runs locally; deploy runs on the remote server from a packaged output directory.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| mcc-pipeline | Governs mcc_build.py and mcc_deploy.py patterns, stage configuration, deployment stages |
| mcc-infra | Governs systemd, nginx, SSL, and server infrastructure setup |
| mcc-ci-cd | Governs deployment with nginx, systemd, and rsync |

## Architecture

```
mcc_build.py        # Build orchestrator (quality, tests, package)
mcc_deploy.py       # Deploy orchestrator (database, app, infra)
mcc_common.py       # Shared utilities
mcc_config.py       # Configuration loading and template substitution
lint.py             # Linting wrapper
run_tests.py        # Test runner
start_services.py   # Local service starter
mcc/
  conf-prod.yml     # Production stage config
  conf-dev.yml      # Development stage config
  deploy_server.py  # Remote server operations (Fabric/SSH)
  daemon.template   # Systemd service template
  nginx.template    # nginx config template
```

## Key Implementation Patterns

1. **Two-script architecture**: Build runs locally and packages into an output directory; deploy runs on the remote server from that output.
2. **Versioned deployment**: Each deployment creates a timestamped directory with a symlink for the active version.
3. **Template rendering**: Single daemon.template and nginx.template rendered per stage with variable substitution and cycle detection.
4. **Stage configs**: YAML files with `{{PLACEHOLDER}}` variables resolved at deploy time.
5. **Cron management**: Marker-based entries (`MCC-AUTH-START`/`MCC-AUTH-END`) allow safe re-deployment of cron jobs.
6. **Smoke test**: Post-deploy health check to the `/api/health` endpoint confirms successful deployment.
