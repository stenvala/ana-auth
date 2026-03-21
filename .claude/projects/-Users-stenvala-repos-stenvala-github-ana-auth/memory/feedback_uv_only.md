---
name: Always use uv, never bare python
description: All Python commands must use uv run, never python directly
type: feedback
---

Never run `python something` -- always `uv run something`. uv is the package manager for all projects.

**Why:** User standardizes on uv for package management across all projects.
**How to apply:** In all scripts, docs, proposals, and commands, use `uv run` prefix. Build/deploy scripts use `uv run pytest`, `uv run` etc.
