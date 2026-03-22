# Tasks: Frontend Application Skeleton

**Status**: Accepted
**Generated with**: as-taskify
**Story**: 03-frontend-skeleton

## Prerequisites

- None (can be implemented in parallel with 02-backend-skeleton)
- .nvmrc from 02 (P01.T003) should exist, but can be created here if not

---

## Phase 1: Setup

### P01.T001 -- Scaffold Angular 21 project

**Mandatory to use skills: /create-web-app**

Scaffold Angular 21 application:
- `nvm use 20.19.2 && npx @angular/cli@latest new ui --directory src/ui --style scss --routing --ssr=false`
- Verify scaffold succeeds

Files:
- Create `src/ui/` directory with full Angular scaffold

Verify: `nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development` succeeds.

- [x] P01.T001

### P01.T002 -- Add Angular Material v3

**Mandatory to use skills: /create-web-app**

Add Angular Material to the project:
- `cd src/ui && npx ng add @angular/material`
- Select custom theme, dark mode

Files:
- Modified `src/ui/package.json`
- Modified `src/ui/angular.json`

- [x] P01.T002

---

## Phase 2: Implementation

### UI Changes

### P02.T001 -- Configure Material Design 3 custom sci-fi theme

**Mandatory to use skills: /create-web-app, /frontend-component**

Set up the custom theme in `src/ui/src/styles.scss`:
- Generate custom palette with `npx ng generate @angular/material:theme-color` using deep violet (#4A0E78)
- Apply `mat.theme()` mixin with custom palette
- Set `color-scheme: dark` as default on `html` element
- Support light mode via `@media (prefers-color-scheme: light)`
- Color palette: deep violet primary, electric cyan tertiary

Files:
- Modify `src/ui/src/styles.scss`
- Modify `src/ui/src/index.html` (add color-scheme: dark)

- [x] P02.T001

### P02.T002 -- Create API proxy configuration

**Mandatory to use skills: /create-web-app**

Create proxy config for development to forward API calls to backend:
- Proxy `/api/*` to `http://localhost:6784`

Files:
- Create `src/ui/proxy.conf.json`
- Modify `src/ui/angular.json` (add proxy config to serve target, set port to 6785)

- [x] P02.T002

### P02.T003 -- Create core and shared modules

**Mandatory to use skills: /frontend-component**

Create the module structure:
- CoreModule: CommonModule, RouterModule re-exports
- MaterialModule: Angular Material component imports for shared use
- SharedModule: Shared components module

Files:
- Create `src/ui/src/app/core/core.module.ts`
- Create `src/ui/src/app/core/material.module.ts`
- Create `src/ui/src/app/shared/shared.module.ts`

- [x] P02.T003

### P02.T004 -- Create landing page component

**Mandatory to use skills: /frontend-component**

Create standalone landing page component:
- Sci-fi styled landing page showing ana-auth branding
- Display project name and brief description
- Use Material Design 3 tokens for styling
- OnPush change detection, data-test-id attributes

Files:
- Create `src/ui/src/app/features/landing/landing.component.ts`
- Create `src/ui/src/app/features/landing/landing.component.html`
- Create `src/ui/src/app/features/landing/landing.component.scss`

- [x] P02.T004

### P02.T005 -- Configure routing

**Mandatory to use skills: /frontend-component**

Set up route definitions:
- Default route (`''`) to landing page (lazy loaded)
- Wildcard redirect to landing
- Update app.component.html with router-outlet

Files:
- Modify `src/ui/src/app/app.routes.ts`
- Modify `src/ui/src/app/app.component.html`
- Modify `src/ui/src/app/app.component.ts`

Verify: `nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development` succeeds.

- [x] P02.T005

---

## Phase 3: Test Automation

No automated tests for this story. E2E test for landing page is covered in story 05-test-infrastructure.

---

## Phase 4: Manual Verification

- Run `nvm use 20.19.2 && cd src/ui && npx ng serve --port 6785`
- Verify dark theme renders with violet/cyan color scheme
- Verify landing page displays ana-auth branding
- Toggle system color scheme to light mode and verify theme switches
- Run `npx ng build` and verify production build succeeds
