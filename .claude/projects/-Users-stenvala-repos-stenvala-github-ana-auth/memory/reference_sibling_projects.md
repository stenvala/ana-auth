---
name: Sibling project references for MCC patterns
description: events.3rdb.com project has reference implementations for MCC scripts and infrastructure
type: reference
---

The sibling folder `events.3rdb.com` (relative to the repo parent) contains reference implementations for:
- `lint.py`, `run_tests.py`, `mcc_build.py`, `mcc_deploy.py`, `mcc_common.py`, `config.py` (should be renamed to `mcc_config.py` in new projects), `start_services.py`, `mcc/deploy_server.py`

The `trials-race-calendar` project has a database setup script pattern using PostgreSQL schemas for multitenancy (schema per environment/test runner).

**How to apply:** When creating MCC pipeline, infrastructure, or database setup scripts, reference these sibling projects for patterns and conventions.
