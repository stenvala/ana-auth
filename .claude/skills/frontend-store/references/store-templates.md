# State Service Templates

## Pattern 1: ListStore with Summary + ObjectStore with Full Items (PREFERRED)

This is the **preferred pattern** for most use cases. It separates:
- **listItemsStore** (ListStore): Contains summary/subset DTOs for list views (e.g., `FeatureSummaryDTO`)
- **itemStore** (ObjectStore): Contains full DTOs for detail views (e.g., `FeatureDTO`)

This pattern is ideal when:
- List views only need a subset of fields (name, status, dates)
- Detail views need the full object with all relationships
- You want to minimize data transfer for list endpoints

```typescript
import { Injectable, Signal } from '@angular/core';
import { ListStore, ObjectStore } from '@core/stores';
import { FeatureDTO, FeatureSummaryDTO } from '@api/index';

@Injectable({ providedIn: 'root' })
export class FeatureStateService {
  /**
   * LIST STORE: Contains summary objects for list views.
   * - Keyed by search criteria (e.g., fiscalYearId, or 'all')
   * - Contains FeatureSummaryDTO which is a subset of FeatureDTO
   * - Used by list components to display tables/cards
   * - Does NOT contain full object data
   */
  readonly listItemsStore = new ListStore<FeatureSummaryDTO>();

  /**
   * OBJECT STORE: Contains full objects for detail views.
   * - Keyed by item ID
   * - Contains FeatureDTO with all fields and relationships
   * - Used by detail/edit components
   * - Single source of truth for individual items
   */
  readonly itemStore = new ObjectStore<FeatureDTO>();

  /**
   * Get list items for a search key.
   * Returns summary DTOs suitable for list views.
   */
  getListItems(searchKey: string): Signal<FeatureSummaryDTO[] | null> {
    return this.listItemsStore.get(searchKey);
  }

  /**
   * Get full item by ID.
   * Returns complete DTO for detail views.
   */
  getItem(id: string): Signal<FeatureDTO | null> {
    return this.itemStore.get(id);
  }

  /**
   * Store list items from search results.
   */
  setListItems(searchKey: string, items: FeatureSummaryDTO[]): void {
    this.listItemsStore.set(searchKey, items);
  }

  /**
   * Store a full item.
   * IMPORTANT: When updating an item, you may need to also update or clear
   * the listItemsStore depending on your use case:
   * - Option A: Clear all list caches (simple, always correct)
   * - Option B: Update the item in all lists where it exists (complex, more efficient)
   */
  setItem(id: string, item: FeatureDTO): void {
    this.itemStore.set(id, item);
    // Option A: Clear list caches to force refresh
    // this.listItemsStore.clear();

    // Option B: Update in lists (if summary fields changed)
    // this.updateItemInLists(id, item);
  }

  /**
   * Update item in all list stores where it exists.
   * Use this when you want to keep list caches valid after an update.
   */
  private updateItemInLists(id: string, item: FeatureDTO): void {
    this.listItemsStore.getAllKeys().forEach(searchKey => {
      const items = this.listItemsStore.get(searchKey)();
      if (items) {
        const index = items.findIndex(i => i.id === id);
        if (index !== -1) {
          // Map full DTO to summary DTO
          const summary: FeatureSummaryDTO = {
            id: item.id,
            name: item.name,
            status: item.status,
            // ... other summary fields
          };
          const updated = [...items];
          updated[index] = summary;
          this.listItemsStore.set(searchKey, updated);
        }
      }
    });
  }

  /**
   * Remove an item from both stores.
   */
  removeItem(id: string): void {
    this.itemStore.remove(id);

    // Remove from all list caches
    this.listItemsStore.getAllKeys().forEach(searchKey => {
      const items = this.listItemsStore.get(searchKey)();
      if (items) {
        const filtered = items.filter(i => i.id !== id);
        if (filtered.length !== items.length) {
          this.listItemsStore.set(searchKey, filtered);
        }
      }
    });
  }

  clearAll(): void {
    this.listItemsStore.clear();
    this.itemStore.clear();
  }

  /**
   * Clear list caches only (items remain for detail views).
   */
  clearListCaches(): void {
    this.listItemsStore.clear();
  }
}
```

---

## Pattern 2: ID List + Entity Store (Normalized Pattern)

This pattern stores full objects in ObjectStore and only IDs in ListStore.
Use when list and detail views use the same DTO (no summary variant).

```typescript
import { Injectable, Signal, computed } from '@angular/core';
import { ListStore, ObjectStore } from '@core/stores';
import { FeatureDTO } from '@api/index';

@Injectable({ providedIn: 'root' })
export class FeatureStateService {
  /**
   * ENTITY STORE: Single source of truth for all items.
   * - Keyed by item ID
   * - Contains full FeatureDTO
   * - Both list and detail views read from here
   */
  readonly itemEntities = new ObjectStore<FeatureDTO>();

  /**
   * ID LIST STORE: Contains only IDs for each search criteria.
   * - Keyed by serialized search criteria
   * - Contains { id: string }[] - just references, not actual data
   * - Used to know which items belong to which search result
   */
  readonly searchResults = new ListStore<{ id: string }>();

  /**
   * Get items for a search criteria key.
   * Returns computed signal that joins IDs to entities.
   * This pattern ensures all views see the same data.
   */
  getItemsBySearchKey(searchKey: string): Signal<FeatureDTO[] | null> {
    return computed(() => {
      const ids = this.searchResults.get(searchKey)();
      if (ids === null) return null;
      return ids
        .map(item => this.itemEntities.get(item.id)())
        .filter((doc): doc is FeatureDTO => !!doc);
    });
  }

  /**
   * Check if a search key exists in results
   */
  has(searchKey: string): boolean {
    return this.searchResults.isInitialized(searchKey);
  }

  /**
   * Store items and their search result IDs.
   * Items go to entity store, IDs go to search results.
   */
  setSearchResults(searchKey: string, items: FeatureDTO[]): void {
    const idList = items.map(item => {
      this.itemEntities.set(item.id, item);
      return { id: item.id };
    });
    this.searchResults.set(searchKey, idList);
  }

  /**
   * Update a single item.
   * Because list views use computed signals that read from itemEntities,
   * the update is automatically reflected everywhere.
   */
  setItem(id: string, item: FeatureDTO): void {
    this.itemEntities.set(id, item);
    // No need to update searchResults - computed signals handle it
  }

  /**
   * Remove an item from entity store and all search results.
   */
  removeItem(id: string): void {
    this.itemEntities.remove(id);

    this.searchResults.getAllKeys().forEach(searchKey => {
      const idList = this.searchResults.get(searchKey)();
      if (idList) {
        const filtered = idList.filter(i => i.id !== id);
        if (filtered.length !== idList.length) {
          this.searchResults.set(searchKey, filtered);
        }
      }
    });
  }

  clearAll(): void {
    this.itemEntities.clear();
    this.searchResults.clear();
  }

  clearSearchResults(): void {
    this.searchResults.clear();
  }
}
```

---

## Pattern 3: Simple ListStore (Basic Cases)

For simple resources where you always load all items and don't need separate detail fetching:

```typescript
import { Injectable } from '@angular/core';
import { ListStore } from '@core/stores';
import { FeatureDTO } from '@api/index';

@Injectable({ providedIn: 'root' })
export class FeatureStateService {
  /**
   * Store for lists of items keyed by a grouping key.
   * get(key) returns Signal<FeatureDTO[] | null>
   * null means not yet loaded, empty array means loaded but empty
   */
  readonly itemsStore = new ListStore<FeatureDTO>();

  /**
   * Clear all cached data.
   */
  clearAll(): void {
    this.itemsStore.clear();
  }
}
```

## ListStoreWithObject Pattern (Paginated Lists)

```typescript
import { Injectable } from "@angular/core";

import { ListStoreWithObject } from "@core/base-store/list-store-with-object.store";
import { FeatureItemDTO, FeatureListMetaDTO } from "@api/dto";

@Injectable({ providedIn: "root" })
export class FeatureStoreService {
  /**
   * Store for paginated lists with metadata.
   * getList(key) returns Signal<FeatureItemDTO[] | null>
   * getObject(key) returns Signal<FeatureListMetaDTO | null>
   */
  readonly itemsStore = new ListStoreWithObject<
    FeatureItemDTO,
    FeatureListMetaDTO
  >();
  // You can actually have mutliple store here, that is actually best practice!

  clearAll(): void {
    this.itemsStore.clear();
  }
}
```

## ValueStore Pattern (Single Global Value)

```typescript
import { Injectable } from "@angular/core";

import { ValueStore } from "@core/base-store/value.store";
import { CurrentUserDTO } from "@api/dto";

@Injectable({ providedIn: "root" })
export class UserStoreService {
  /**
   * Store for current user (no key needed).
   * get() returns Signal<CurrentUserDTO | null>
   */
  readonly currentUser = new ValueStore<CurrentUserDTO>();

  clear(): void {
    this.currentUser.clear();
  }
}
```

## Store API Reference

### ListStore<T>

```typescript
// Get signal for items at key (null = not loaded)
get(key: string): Signal<T[] | null>

// Set items at key
set(key: string, items: T[]): void

// Add single item to list at key
setItem(key: string, item: T): void

// Remove item by id from list at key
removeItem(key: string, id: string): void

// Check if key has been loaded
isInitialized(key: string): boolean

// Remove specific key
remove(key: string): void

// Clear all data
clear(): void
```

### ObjectStore<T>

```typescript
// Get signal for object at key (null = not loaded)
get(key: string): Signal<T | null>

// Set object at key
set(key: string, item: T): void

// Check if key has been loaded
isInitialized(key: string): boolean

// Remove specific key
remove(key: string): void

// Clear all data
clear(): void
```

### ValueStore<T>

```typescript
// Get signal for value (null = not loaded)
get(): Signal<T | null>

// Set value
set(value: T): void

// Check if value has been set
isInitialized(): boolean

// Clear value
clear(): void
```
