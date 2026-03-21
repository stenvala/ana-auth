# Store Templates

Stores are **pure data containers** — they expose store instances directly with no wrapper methods.
The service layer accesses stores directly (e.g., `this.store.buildsStore.get(key)`).

## Core Principle

Stores are pure data containers — just declare store instances, no wrapper methods. Services access stores directly: `this.store.itemsStore.get(key)`, `this.store.itemsStore.set(key, items)`.

**Key rule**: No `getItem()`, `setItem()`, `clearAll()` wrapper methods. Services call store methods directly.

---

## Pattern 1: Paginated List + Detail Store (PREFERRED for paginated data)

Use when the API returns paginated results with total counts and you have separate list/detail views.

```typescript
import { Injectable } from '@angular/core';
import { ListStore, ObjectStore } from '@core/stores';
import { FeatureDTO, FeatureDetailDTO } from '@api/dto';

@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  // Paginated list items keyed by composite search key (e.g., "repoId:status:offset")
  readonly itemsStore = new ListStore<FeatureDTO>();

  // Total counts keyed by search criteria WITHOUT offset (e.g., "repoId:status")
  readonly totalStore = new ObjectStore<number>();

  // Individual full items keyed by item ID
  readonly itemStore = new ObjectStore<FeatureDetailDTO>();
}
```

**Cache key strategy**: The service defines helper functions to build composite keys:
```typescript
// Used by the service, not the store
function itemsKey(parentId?: string, status?: string, offset: number = 0): string {
  return `${parentId || ''}:${status || ''}:${offset}`;
}

function totalKey(parentId?: string, status?: string): string {
  return `${parentId || ''}:${status || ''}`;
}
```

### When to add more stores

Add additional `ObjectStore` instances for related data loaded separately:

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStore<FeatureDTO>();
  readonly totalStore = new ObjectStore<number>();
  readonly itemStore = new ObjectStore<FeatureDetailDTO>();
  readonly logContentStore = new ObjectStore<string>();    // Logs loaded separately
  readonly metricsStore = new ObjectStore<MetricsDTO>();   // Metrics loaded separately
}
```

---

## Pattern 2: ListStore + ObjectStore (List/Detail with different DTOs)

Use when list views need summary data and detail views need full objects, but no server-side pagination.

```typescript
import { Injectable } from '@angular/core';
import { ListStore, ObjectStore } from '@core/stores';
import { FeatureSummaryDTO, FeatureDTO } from '@api/dto';

@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  // Summary items for list views, keyed by parent/group key (e.g., 'all', parentId)
  readonly listItemsStore = new ListStore<FeatureSummaryDTO>();

  // Full items for detail views, keyed by item ID
  readonly itemStore = new ObjectStore<FeatureDTO>();
}
```

---

## Pattern 3: Simple ListStore

For simple resources loaded all at once with no separate detail view:

```typescript
import { Injectable } from '@angular/core';
import { ListStore } from '@core/stores';
import { FeatureDTO } from '@api/dto';

@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  // Items keyed by grouping key ('all' for ungrouped, parentId for grouped)
  readonly itemsStore = new ListStore<FeatureDTO>();
}
```

---

## Pattern 4: ListStoreWithObject (Paginated Lists with Metadata)

```typescript
import { Injectable } from '@angular/core';
import { ListStoreWithObject } from '@core/base-store/list-store-with-object.store';
import { FeatureItemDTO, FeatureListMetaDTO } from '@api/dto';

@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStoreWithObject<FeatureItemDTO, FeatureListMetaDTO>();
}
```

---

## Pattern 5: ValueStore (Single Global Value)

```typescript
import { Injectable } from '@angular/core';
import { ValueStore } from '@core/base-store/value.store';
import { CurrentUserDTO } from '@api/dto';

@Injectable({ providedIn: 'root' })
export class UserStoreService {
  readonly currentUser = new ValueStore<CurrentUserDTO>();
}
```

---

## Store API Reference

### ListStore<T>

```typescript
get(key: string): Signal<T[] | null>        // Get signal (null = not loaded)
set(key: string, items: T[]): void           // Set items at key
setItem(key: string, item: T): void          // Add single item to list at key
removeItem(key: string, id: string): void    // Remove item by id from list at key
isInitialized(key: string): boolean          // Check if key has been loaded
remove(key: string): void                    // Remove specific key
clear(): void                                // Clear all data
getAllKeys(): string[]                        // Get all initialized keys
```

### ObjectStore<T>

```typescript
get(key: string): Signal<T | null>           // Get signal (null = not loaded)
set(key: string, item: T): void              // Set object at key
isInitialized(key: string): boolean          // Check if key has been loaded
remove(key: string): void                    // Remove specific key
clear(): void                                // Clear all data
```

### ValueStore<T>

```typescript
get(): Signal<T | null>                      // Get signal (null = not loaded)
set(value: T): void                          // Set value
isInitialized(): boolean                     // Check if value has been set
clear(): void                                // Clear value
```
