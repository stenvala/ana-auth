---
name: frontend-component
description: Create Angular standalone components as route, presentational, or shared types
---

# Frontend Component Creation

Create Angular standalone components following the controller/view pattern.

## Component Types

### 1. Route Components (Controllers)
- Handle routing, loading states, pagination, and navigation
- **Naming**: `route-<name>` selector, `Route<Name>Component` class
- Location: the feature's `components/route-<name>/` directory

### 2. Presentational Components (Views)
- Receive data via `input()`, emit events via `output()`
- **Naming**: `app-<feature>-<name>` selector, `<Feature><Name>Component` class
- **CRITICAL**: The `<feature>` prefix MUST match the feature folder name exactly (plural/singular as-is)
- Location: the feature's `components/<feature>-<name>/` directory

### 3. Shared Components
- Reusable across the entire application, prefix `shared-`
- Location: the shared module's `components/shared-<name>/` directory
- Must be registered in `SHARED_COMPONENTS` array in the shared module
- **No SharedModule import**: Only import `[CoreModule, MaterialModule]` to avoid circular dependency

## Scaffolding Scripts

```bash
# Route component
uv run .claude/skills/frontend-component/scripts/init_frontend_route.py <feature> <name>

# Presentational or shared component
uv run .claude/skills/frontend-component/scripts/init_frontend_component.py <feature> <name>
```

## Instructions

### Route Components
1. Run the scaffolding script
2. Add path constants and route configuration
3. Verify build

### Presentational Components
1. Run the scaffolding script
2. Export from feature's `components/index.ts`
3. Import in parent route component
4. Verify build

### Shared Components
1. Create files in the shared module's components directory
2. Import component in the shared module and add to `SHARED_COMPONENTS` array
3. Verify build

### Verify Build

```bash
source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development 2>&1 | head -20
```

## Key Rules (All Components)

1. **Module imports**: Always use `[CoreModule, MaterialModule, SharedModule]` — never import Mat\* separately. Exception: shared components omit SharedModule
2. **Standalone**: Always `standalone: true`
3. **OnPush**: Always `ChangeDetectionStrategy.OnPush`
4. **Computed signals**: Use `computed()` for all reactive data
5. **No subscriptions**: Never subscribe in components
6. **Separate template**: Always put HTML in separate `.html` file
7. **Global styles**: Use classes from the global styles directory — minimize custom SCSS. See `/frontend-design-system`
8. **data-test-id**: MANDATORY on all interactive/content elements for E2E testing — see `resources/component-rules.md`

## Prerequisites

Business logic service must exist (use `/frontend-service`).

## Design System

For layout, CSS classes, button types, card patterns, and responsive design, use `/frontend-design-system`.

## Resources

| Resource | Contents |
|----------|----------|
| `resources/component-rules.md` | data-test-id rules, route/presentational/shared component rules, loading state patterns |
| `resources/route-component-template.md` | Paginated list, detail view, polling lifecycle templates |
| `resources/presentational-component-template.md` | Input/output pattern, computed from inputs, content projection |
| `resources/shared-component-template.md` | SharedModule registration, no-SharedModule-import rule |
| `resources/view-template.md` | Loading/data/empty-state HTML patterns |
| `resources/routing-template.md` | Path constants, route config, navigation usage |

