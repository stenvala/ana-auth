# Technical Specification: Frontend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21
**Status**: Accepted
**Generated with**: as-techify

## Overview

Scaffold an Angular 21 application with Angular Material v3 using a custom sci-fi theme (deep violet primary, electric cyan tertiary, dark mode default). Includes a landing page, routing setup, API proxy configuration, and the design system foundation using Material Design 3 color tokens.

## Relevant Skills

| Skill | Why Relevant |
|-------|-------------|
| create-web-app | Angular scaffold structure, shared modules, proxy config |
| frontend-component | Angular standalone component patterns -- OnPush, data-test-id |
| frontend-store | Signal-based state management patterns (establish for future use) |

## Architecture

```
src/ui/
  angular.json              # Angular CLI configuration
  package.json              # Node dependencies
  tsconfig.json             # TypeScript configuration
  proxy.conf.json           # API proxy to localhost:6784
  src/
    index.html              # Root HTML with color-scheme: dark
    main.ts                 # Bootstrap application
    styles.scss             # Global styles, Material theme
    app/
      app.component.ts      # Root component
      app.component.html    # Router outlet
      app.component.scss    # Global layout styles
      app.routes.ts         # Route definitions
      core/
        core.module.ts      # CommonModule, RouterModule re-exports
        material.module.ts  # Material component imports
      shared/
        shared.module.ts    # Shared components module
      features/
        landing/
          landing.component.ts    # Landing page
          landing.component.html  # Landing page template
          landing.component.scss  # Landing page styles
```

### Theming Approach

1. Generate custom color palette using `npx ng generate @angular/material:theme-color` with deep violet (#4A0E78) as the source color
2. Use `mat.theme()` mixin in `styles.scss` with the generated palette
3. Set `color-scheme: dark` as default on `html` element
4. Support light mode via `@media (prefers-color-scheme: light)` or manual toggle
5. Use CSS custom properties from Material Design 3 tokens (`--mat-sys-primary`, `--mat-sys-tertiary`, `--mat-sys-surface`, etc.)

### Color Palette

- **Primary**: Deep violet/indigo (#4A0E78 range) -- space depth
- **Tertiary**: Electric cyan (#00BCD4 range) -- neon glow
- **Secondary**: Cool grey-blue (auto-generated from primary)
- **Error**: Warm neon red (#FF5252 range)

## Data Model Changes

None.

## API Changes

None -- the frontend proxies to the backend's API.

## Implementation Approach

1. **Create .nvmrc** at project root with `20.19.2`
2. **Scaffold Angular project**: `nvm use 20.19.2 && npx @angular/cli@latest new ui --directory src/ui --style scss --routing --ssr=false`
3. **Add Angular Material**: `cd src/ui && npx ng add @angular/material` -- select custom theme, dark mode
4. **Generate custom palette**: `npx ng generate @angular/material:theme-color` with violet source color
5. **Configure theme in styles.scss**: Apply `mat.theme()` with custom palette, set dark mode default
6. **Create proxy.conf.json**: Proxy `/api/*` to `http://localhost:6784`
7. **Create core modules**: CoreModule (CommonModule, RouterModule), MaterialModule (Material component imports)
8. **Create shared module**: SharedModule for shared components
9. **Create landing component**: Standalone component with sci-fi styled landing page
10. **Configure routing**: Default route to landing page, wildcard redirect to landing
11. **Update angular.json**: Set dev server port to 6785, add proxy config
12. **Verify build**: `npx ng build --configuration=development`

## Testing Strategy

### Automated Tests

- E2E test: Navigate to root URL, verify landing page loads and displays ana-auth branding

### Manual Testing

- `nvm use 20.19.2 && cd src/ui && npx ng serve --port 6785`
- Verify dark theme renders with violet/cyan color scheme
- Verify light mode toggle or system preference switch works
- Check `npx ng build` produces production assets

## Out of Scope

- Admin UI pages
- SSO sign-in form
- Complex animations or particle effects
- Custom icon set

## Migration / Deployment Notes

- Frontend build output goes to `src/ui/dist/` and is served by nginx in production
- Production build: `npx ng build` (defaults to production configuration)
- Dev server runs on port 6785 with proxy to backend on port 6784

## Security Considerations

- No sensitive data in the frontend skeleton
- CSP headers should be configured in nginx (story 06)
