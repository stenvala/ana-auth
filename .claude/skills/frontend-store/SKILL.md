---
name: frontend-store
description: Create Angular store services using base stores for signal-based state
---

# Frontend Store Creation

Create store services using base stores for key-based signal storage.

## When to Use

- Adding state management for a new feature
- Creating stores to cache API responses
- Implementing reactive data patterns with signals

## Prerequisites

1. Backend API must be ready
2. TypeScript DTOs generated via `uv run after_api_change.py`

## File Location

Create store in the feature's `services/` directory, named `<feature>-<optional-kind>.store.ts`.

## Scaffolding Script

```bash
uv run .claude/skills/frontend-store/scripts/init_frontend_store.py <feature>
```

## Instructions

1. Choose appropriate store type(s) based on data needs
2. Create store service using templates from `resources/store-templates.md`
3. Verify build:
   ```bash
   source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development 2>&1 | head -20
   ```

## Available Base Stores

Located in the core base-store module:

| Store                      | Purpose                        | Example Use       |
| -------------------------- | ------------------------------ | ----------------- |
| `ListStore<T>`             | Collections keyed by string    | Items by parentId |
| `ObjectStore<T>`           | Single objects keyed by string | Item by id        |
| `ValueStore<T>`            | Single value (not keyed)       | Current user      |
| `ListStoreWithObject<T,O>` | List + metadata with same key  | Paginated lists   |

## Recommended Patterns

### Pattern 1: Paginated List + Detail Store
Use when API returns paginated results with total counts and you have separate list/detail views. Uses `ListStore` for lists, `ObjectStore` for totals and individual items.

### Pattern 2: Non-Paginated List + Detail Store
Use when all items are loaded at once (small collections). Uses `ALL_KEY = 'all'` in the service, `ListStore` for items, `ObjectStore` for individual items.

### Pattern 3: Simple ListStore
For simple resources loaded all at once with no separate detail view.

### When to Add More Stores
Add additional `ObjectStore` instances for related data loaded separately (e.g., logs, metrics).

## Key Rules

1. **Pure data container**: NO wrapper methods. Services access store instances directly
2. **Use base stores**: Choose appropriate store type for your data
3. **Key-based access**: Stores use string keys to organize data
4. **Null = not loaded**: `get(key)` returns `Signal<T | null>` — null means not yet loaded
5. **Invalidation**: Use store's `clear()` or `remove(key)` methods directly from the service
6. **Composite keys**: For paginated/filtered data, the service builds composite string keys — the store doesn't know about key structure

## Resources

| Resource | Contents |
|----------|----------|
| `resources/store-templates.md` | Complete implementation examples for all patterns and the full Store API reference |

