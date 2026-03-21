# Frontend Service Templates

## Template 1: Paginated List + Detail Service

For features with server-side pagination, total counts, and detail views.

```typescript
import { Injectable, Signal, inject, untracked, computed } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { PrivateFeatureApiService, FeatureDTO, FeatureDetailDTO } from '@api/index';
import { FeatureStoreService } from './feature.store';

export const PAGE_SIZE = 20;

// Cache key functions — defined at module level, not as class methods
function itemsKey(parentId?: string, status?: string, offset: number = 0): string {
  return `${parentId || ''}:${status || ''}:${offset}`;
}

function totalKey(parentId?: string, status?: string): string {
  return `${parentId || ''}:${status || ''}`;
}

@Injectable({ providedIn: 'root' })
export class FeatureService {
  private readonly api = inject(PrivateFeatureApiService);
  private readonly store = inject(FeatureStoreService);

  // ──────────────────────────────────────────────
  // Signal Accessors (components call these)
  // ──────────────────────────────────────────────

  items(parentId?: string, status?: string, offset: number = 0): Signal<FeatureDTO[] | null> {
    const key = itemsKey(parentId, status, offset);
    const signal = this.store.itemsStore.get(key);
    if (signal() === null) {
      untracked(() => {
        this.search(parentId, status, offset);
      });
    }
    return signal;
  }

  total(parentId?: string, status?: string): Signal<number> {
    const key = totalKey(parentId, status);
    const totalSignal = this.store.totalStore.get(key);
    return computed(() => totalSignal() ?? 0);
  }

  item(itemId: string): Signal<FeatureDetailDTO | null> {
    const signal = this.store.itemStore.get(itemId);
    if (signal() === null) {
      untracked(() => {
        this.loadById(itemId);
      });
    }
    return signal;
  }

  // ──────────────────────────────────────────────
  // Load Methods (async, update store, return data)
  // ──────────────────────────────────────────────

  async search(
    parentId?: string,
    status?: string,
    offset: number = 0,
    refresh: boolean = true,
  ): Promise<FeatureDTO[]> {
    const key = itemsKey(parentId, status, offset);
    if (!refresh && this.store.itemsStore.isInitialized(key)) {
      return this.store.itemsStore.get(key)()!;
    }
    const response = await firstValueFrom(
      this.api.listItems(parentId || undefined, status || undefined, offset, PAGE_SIZE),
    );
    this.store.itemsStore.set(key, response.items);
    this.store.totalStore.set(totalKey(parentId, status), response.total);
    return response.items;
  }

  async loadById(id: string, refresh: boolean = true): Promise<FeatureDetailDTO> {
    if (!refresh && this.store.itemStore.isInitialized(id)) {
      return this.store.itemStore.get(id)()!;
    }
    const response = await firstValueFrom(this.api.getItem(id));
    this.store.itemStore.set(id, response);
    return response;
  }

  // ──────────────────────────────────────────────
  // Action Methods (feature-specific operations)
  // ──────────────────────────────────────────────

  async triggerAction(itemId: string): Promise<ResponseDTO> {
    const response = await firstValueFrom(
      this.api.triggerAction({ itemId }),
    );
    return response;
  }
}
```

---

## Template 2: Non-Paginated List + Detail Service

For features where the API returns all items at once (no pagination). Uses `ALL_KEY` constant for the single list cache key.

```typescript
import { Injectable, Signal, inject, untracked } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { PrivateFeatureApiService, FeatureDTO, CreateFeatureDTO, UpdateFeatureDTO } from '@api/index';
import { FeatureStoreService } from './feature.store';

const ALL_KEY = 'all';

@Injectable({ providedIn: 'root' })
export class FeatureService {
  private readonly api = inject(PrivateFeatureApiService);
  private readonly store = inject(FeatureStoreService);

  // ──────────────────────────────────────────────
  // Signal Accessors
  // ──────────────────────────────────────────────

  getAll(): Signal<FeatureDTO[] | null> {
    const signal = this.store.itemsStore.get(ALL_KEY);
    if (signal() === null) {
      untracked(() => {
        this.loadAll();
      });
    }
    return signal;
  }

  getById(id: string): Signal<FeatureDTO | null> {
    const signal = this.store.itemStore.get(id);
    if (signal() === null) {
      untracked(() => {
        this.loadById(id);
      });
    }
    return signal;
  }

  // ──────────────────────────────────────────────
  // Load Methods
  // ──────────────────────────────────────────────

  async loadAll(refresh: boolean = true): Promise<FeatureDTO[]> {
    if (!refresh && this.store.itemsStore.isInitialized(ALL_KEY)) {
      return this.store.itemsStore.get(ALL_KEY)()!;
    }
    const response = await firstValueFrom(this.api.listItems());
    this.store.itemsStore.set(ALL_KEY, response.items);
    return response.items;
  }

  async loadById(id: string, refresh: boolean = true): Promise<FeatureDTO> {
    if (!refresh && this.store.itemStore.isInitialized(id)) {
      return this.store.itemStore.get(id)()!;
    }
    const response = await firstValueFrom(this.api.getItem(id));
    this.store.itemStore.set(id, response);
    return response;
  }

  // ──────────────────────────────────────────────
  // CRUD Methods
  // ──────────────────────────────────────────────

  async create(dto: CreateFeatureDTO): Promise<FeatureDTO> {
    const result = await firstValueFrom(this.api.createItem(dto));
    this.store.itemStore.set(result.id, result);
    await this.loadAll();
    return result;
  }

  async update(id: string, dto: UpdateFeatureDTO): Promise<FeatureDTO> {
    const result = await firstValueFrom(this.api.updateItem(id, dto));
    this.store.itemStore.set(id, result);
    await this.loadAll();
    return result;
  }

  async delete(id: string): Promise<void> {
    await firstValueFrom(this.api.deleteItem(id));
    this.store.itemStore.remove(id);
    await this.loadAll();
  }
}
```

---

## Side Note: Polling for Changes

For features with real-time updates (builds, deployments), add a `checkForUpdates()` method:

```typescript
async checkForUpdates(): Promise<boolean> {
  const key = totalKey(undefined, undefined);
  if (!this.store.totalStore.isInitialized(key)) {
    return false;
  }
  const currentTotal = this.store.totalStore.get(key)()!;
  const response = await firstValueFrom(this.api.listItems(undefined, undefined, 0, 1));
  if (response.total !== currentTotal) {
    this.store.itemsStore.clear();
    this.store.totalStore.clear();
    return true;
  }
  return false;
}
```

The component consumes this via polling — see the component skill for the polling lifecycle pattern.

---

## Side Note: Loading Related Data

For items with separately-loaded related data (e.g., logs, metrics), add additional signal accessors and load methods:

```typescript
// Signal accessor
logContent(itemId: string): Signal<string | null> {
  const signal = this.store.logContentStore.get(itemId);
  if (signal() === null) {
    untracked(() => { this.loadLog(itemId); });
  }
  return signal;
}

// Load method
async loadLog(itemId: string, refresh: boolean = true): Promise<string> {
  if (!refresh && this.store.logContentStore.isInitialized(itemId)) {
    return this.store.logContentStore.get(itemId)()!;
  }
  const response = await firstValueFrom(this.api.getItemLog(itemId));
  this.store.logContentStore.set(itemId, response.content);
  return response.content;
}
```
