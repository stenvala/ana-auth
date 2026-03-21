---
name: Multitenant deployment with dev and prod stages
description: ana-auth uses multitenant PostgreSQL schemas and two stages (dev/prod) on same server
type: project
---

ana-auth uses a multitenant approach with PostgreSQL schemas:
- Each tenant/stage gets its own schema (e.g., `ana-auth-main`, `ana-auth-dev`, `ana-auth-e2e`)
- Integration tests create a schema per test runner for isolation
- Two deployment stages on the same physical server:
  - `auth-dev.mathcodingclub.com` (dev stage)
  - `auth.mathcodingclub.com` (prod stage)

**Why:** Multitenancy via schemas enables isolated integration testing and running dev+prod on a single server.
**How to apply:** Database setup scripts must support schema suffix patterns. MCC deploy must auto-create database schema if it doesn't exist. Infrastructure configs need both dev and prod nginx/systemd entries.
