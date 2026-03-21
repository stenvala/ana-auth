---
name: frontend-service
description: Create Angular services that orchestrate API calls and state management
---

# Frontend Service Creation

Create business logic services that orchestrate API calls and state management.

## When to Use

- Creating service layer for a new feature
- Implementing CRUD operations with state updates
- Coordinating API service and state store

## Prerequisites

1. Store must exist (use `/frontend-store`)
2. API service auto-generated from backend

## File Location

Create service in the feature's `services/` directory, named `<feature>.service.ts`.

## Scaffolding Script

```bash
uv run .claude/skills/frontend-service/scripts/init_frontend_service.py <feature>
```

## Instructions

Choose the pattern that matches your feature's data needs, then follow the corresponding template in `resources/service-template.md`.

### Pattern 1: Paginated List + Detail

Use when the API returns paginated results with total counts.

Key elements:
- **Cache key functions** at module level (items key includes offset, total key does NOT)
- **`PAGE_SIZE`** constant exported for components
- **Signal accessors** with lazy loading (`items()`, `item()`, `total()`)
- **`search()`** stores both items AND total from paginated responses
- **Action methods** that return API response without updating list stores

### Pattern 2: Non-Paginated List + Detail

Use when the API returns all items at once (small collections).

Key elements:
- **`ALL_KEY`** constant for the single list cache key
- **Signal accessors** with lazy loading (`getAll()`, `getById()`)
- **`loadAll()`** with `refresh` parameter and `isInitialized` check
- **CRUD methods** that call `loadAll()` after mutation to reload from server

### Verify Build

```bash
source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development 2>&1 | head -20
```

## Key Rules

1. **Orchestration**: Coordinates API service and store — no direct API calls from components
2. **Signal accessors from store**: Return `this.store.someStore.get(key)` — the store's signal
3. **Untracked loading**: Use `untracked(() => { this.load(...); })` to trigger load if signal is null
4. **Load returns data**: Load methods return the data (Promise), not void
5. **Cache key functions**: Define at module level, not as class methods
6. **Total separate from items**: (Paginated only) Total key must NOT include offset
7. **CRUD reloads list**: After create/update/delete, call `loadAll()` to reload (non-paginated) or clear caches (paginated)
8. **Store updates on detail**: On create/update, also set the individual item in `itemStore`
9. **refresh parameter**: Defaults to `true`. Signal accessors don't pass it (use default)
10. **No notification in accessors**: Signal accessor methods don't show notifications — only action/CRUD methods may

## Resources

| Resource | Contents |
|----------|----------|
| `resources/service-template.md` | Complete templates for both patterns, polling, and related data loading |

