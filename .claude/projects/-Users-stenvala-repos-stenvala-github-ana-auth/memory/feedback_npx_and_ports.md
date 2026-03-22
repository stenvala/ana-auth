---
name: Use npx ng and custom ports
description: Angular CLI via npx ng, backend port 6784, frontend port 6785
type: feedback
---

All Angular CLI commands must use `npx ng`, not bare `ng`. Backend (uvicorn) runs on port 6784, frontend (Angular dev server) on port 6785. Do not use default ports.

**Why:** User preference for explicit npx usage and non-default ports to avoid conflicts with other services.
**How to apply:** In all scripts, docs, configs, and commands use `npx ng` instead of `ng`. Configure uvicorn/gunicorn to listen on 6784, Angular dev server on 6785. Proxy config points to localhost:6784.
