---
name: Node.js 20.19 via nvm required
description: Angular 21 requires Node.js 20.19, must use nvm use before any node/npm/npx commands
type: feedback
---

Must use Node.js 20.19 via `nvm use` before any node/npm/npx commands. Angular 21 does not compile with lower versions. Build scripts and docs must include `nvm use` step.

**Why:** Angular 21 has a minimum Node.js version requirement of 20.19.
**How to apply:** Include `.nvmrc` with `20.19` in the project root. Build scripts must run `nvm use` before `npx ng build`. README must mention nvm requirement.
