# Technical Specification: Frontend Skeleton

**Domain**: auth/frontend-skeleton
**Last updated**: 2026-03-24

## Overview

Angular 21 standalone application with Angular Material v3 custom theme, configured for development proxying to the FastAPI backend.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| frontend-component | Governs Angular standalone component patterns |
| frontend-service | Governs Angular service patterns for API calls |
| frontend-store | Governs signal-based state management |
| frontend-dialog | Governs dialog component patterns |
| frontend-forms | Governs form component patterns |

## Architecture

- `src/ui/` -- Angular project root
- Standalone components with Angular 21 signal-based patterns
- M3 theme with custom palette: source color #4A0E78 (deep violet primary, electric cyan tertiary)
- Dark mode default on `html` element, light mode via `prefers-color-scheme` media query
- `proxy.conf.json` proxies `/api/*` to `localhost:6784`
- Build output: `src/ui/dist/`

## Key Implementation Patterns

1. **Color scheme**: Dark by default using CSS `color-scheme: dark` on html element. Light mode supported via `light-dark()` CSS function.
2. **Proxy configuration**: Development proxy (`proxy.conf.json`) routes all `/api/*` requests to the backend port.
3. **Standalone components**: All components are standalone (Angular 21 default).
