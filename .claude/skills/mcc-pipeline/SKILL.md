---
name: mcc-pipeline
description: "Create and maintain MCC pipeline build and deploy scripts (mcc_build.py and mcc_deploy.py) for Python web applications. Two-script architecture: build script runs tests, builds, and packages into output directory; deploy script runs on remote server from that output. Use when: creating mcc_build.py or mcc_deploy.py, adding deployment stages, configuring multi-tenant or single-tenant deployments, adding database migrations, setting up cron jobs, adding worker services, creating non-deployment stages like clone-prod-to-dev, or adding test artifacts for build quality tracking. Triggers: mcc_build, mcc_deploy, build script, deploy script, deployment stage, pipeline scripts, test artifacts."
---

# MCC Pipeline

## Architecture

Two Python scripts orchestrate the CI/CD pipeline:

- **`mcc_build.py`** - Runs in project root (CI server or local). Produces `output/` directory.
- **`mcc_deploy.py`** - Runs on remote server from within the transferred `output/` directory.

Shared utility **`mcc_common.py`** must exist in both locations. Copy from `scripts/mcc_common.py` in this skill.

**Critical rule**: Only contents of `output/` are available at deploy time. The deploy script, its dependencies, config files, migration scripts - everything must be copied to `output/` during build.

**Permission model**: The deploy script runs as `stenvala` (DIR_GROUP — directory owner). Services (nginx, backend daemons) run as `www-data` (DIR_USER — execution user). `stenvala` cannot edit systemd unit files or nginx configs — only restart existing services via `sudo /bin/systemctl restart <service>` (visudo-allowed). Files are owned `DIR_USER:DIR_GROUP` with group rw. Service definitions and nginx configs must be set up separately.

## Build Script Workflow

1. Clean and create `output/` and `test-artifacts/`
2. Run tests (fail-fast - build stops on failure), writing JUnit XML and coverage JSON to `test-artifacts/`
3. Build frontend (if applicable)
4. Copy backend source to `output/`
5. Copy all deployment-time files to `output/`

The pipeline worker automatically collects `test-artifacts/` after the build script finishes (whether it succeeds or fails), parses the files, and stores summaries in the database for display in the UI.

See [references/build-patterns.md](references/build-patterns.md) for complete examples, patterns, and test artifact integration.

## Deploy Script Workflow

1. Parse `--stage` argument via typer
2. Read `config.yml` to get stage parameters
3. Route to deployment or non-deployment handler
4. For deployments:
   - Create versioned directory (`vrs-TIMESTAMP`)
   - Copy artifacts to version directory
   - Sync virtual environment (`uv sync --frozen`)
   - Update symlinks (`current-api`, `current-ui`)
   - Run database migrations (per-domain for multi-tenant)
   - Deploy cron jobs (if any)
   - Set file permissions
   - Restart systemd service(s)
   - Cleanup old versions
   - Run smoke tests

See [references/deploy-patterns.md](references/deploy-patterns.md) for complete examples and patterns.

## Configuration Files

- **`config.yml`** - Stage routing. Top-level `deploy` key, each child is a stage with `allow_branches`, `auto_branches`, a free-form `parameters` bag, and an optional `link` URL shown in the MCC pipeline UI.
- **`conf-{stage}.yml`** - Per-stage config: server connection, file ownership, services, domains, backup settings.
- **`build_info.yml`** - Created by MCC pipeline service at project root before build. Copy to `output/` for deploy-time reference.

See [references/deploy-patterns.md](references/deploy-patterns.md) for full schemas and examples.

## Key Decisions

| Concern         | Multi-tenant                         | Single-tenant                   |
| --------------- | ------------------------------------ | ------------------------------- |
| **Database**    | Per-domain DB in `domains/{domain}/` | Single DB at `deployment_path/` |
| **Migrations**  | Loop over all domains                | Run once                        |
| **Config**      | Per-domain `config.yml`              | Single config                   |
| **DOMAINS key** | List of domain names                 | Empty or absent                 |

| Concern               | Options                                                     |
| --------------------- | ----------------------------------------------------------- |
| **Services**          | Single `SERVICE_NAME` or list of `SERVICES`                 |
| **Cron jobs**         | Deploy backup scripts, health checks, cleanup tasks         |
| **Non-deploy stages** | clone-prod-to-dev, db-backup, reset-dev, maintenance-toggle |
| **Database type**     | SQLite (direct file), PostgreSQL (alembic/psql)             |

## Resources

- **`scripts/mcc_common.py`** - Copy this to project root. Required by both build and deploy scripts.
- **[references/build-patterns.md](references/build-patterns.md)** - Build script examples and patterns.
- **[references/deploy-patterns.md](references/deploy-patterns.md)** - Deploy script examples, migration patterns, cron deployment, non-deployment stages.

