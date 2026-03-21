# Implementation Order: 1.init-project

**Created**: 2026-03-21
**Generated with**: as-taskify

## Implementation Sequence

| Order | Story | Depends On | Rationale |
|-------|-------|-----------|-----------|
| 1 | 02-backend-skeleton | None | Foundation: project structure, pyproject.toml, Docker, shared modules, DB context, middleware, health endpoint. Everything else builds on this. |
| 2 | 04-database-schema | 02 | Requires shared/db modules from 02. Creates tables and setup_db.py needed by tests and deploy. |
| 3 | 03-frontend-skeleton | None (parallel with 02/04) | Independent Angular scaffold. No backend dependency for creation, only for proxy at runtime. |
| 4 | 05-test-infrastructure | 02, 04 | Requires backend code to test and database schema for integration tests. |
| 5 | 06-mcc-pipeline | 02, 03, 04, 05 | Build script runs tests (05), builds frontend (03), packages backend (02) and DB scripts (04). Deploy script uses setup_db.py (04). |
| 6 | 07-database-backup | 04, 06 | Backup script depends on schema conventions (04). Cron deployment integrates with mcc_deploy.py (06). |
| 7 | 01-project-readme | 02, 03, 04 | Written last so it accurately describes the actual project structure and setup steps. |

## Dependency Graph

```
02-backend-skeleton ──┬──> 04-database-schema ──┬──> 05-test-infrastructure ──> 06-mcc-pipeline ──> 07-database-backup
                      │                         │                                     │
03-frontend-skeleton ─┼─────────────────────────┘                                     │
                      │                                                               │
                      └───────────────────────────────────────────────────────────────> 01-project-readme
```

## Notes

- Stories 02 and 03 can be implemented in parallel (no shared dependencies).
- Story 01 (README) is last because it documents the actual project state.
- Story 07 is near the end because it integrates with the deploy pipeline.
