# Frontend Service Template

## Normalized State Pattern

The recommended pattern separates entity storage (ObjectStore) from search results (ListStore with IDs).
This avoids fetching all items when only one is needed.

```typescript
import { Injectable, inject, Signal, untracked, computed } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import {
  FeatureDTO,
  FeatureCreateDTO,
  FeatureUpdateDTO,
  PrivateFeatureApiService,
} from '@api/index';
import { FeatureStateService } from './feature-state.service';
import { SharedNotificationService } from '@shared/index';

export interface FeatureSearchCriteria {
  fiscalYearId: string | null;
  type?: string | null;
}

@Injectable({ providedIn: 'root' })
export class FeatureService {
  private readonly api = inject(PrivateFeatureApiService);
  private readonly state = inject(FeatureStateService);
  private readonly notification = inject(SharedNotificationService);

  /**
   * Get a single item by ID.
   * Uses ObjectStore for individual items - does NOT fetch all items.
   */
  getById(id: string): Signal<FeatureDTO | null> {
    const item = this.state.itemEntities.get(id);
    if (!item()) {
      untracked(() => this.loadById(id));
    }
    return item;
  }

  async loadById(id: string, refresh = false): Promise<FeatureDTO> {
    const current = this.state.itemEntities.get(id)();
    if (!refresh && current) {
      return current;
    }
    const response = await firstValueFrom(this.api.getItem(id));
    this.state.itemEntities.set(response.id, response);
    return response;
  }

  /**
   * Get items matching search criteria.
   * Returns a computed signal that joins IDs to entities.
   */
  getSearchResults(criteria: FeatureSearchCriteria): Signal<FeatureDTO[] | null> {
    const searchKey = this.serializeCriteria(criteria);
    if (!this.state.searchResults.has(searchKey)) {
      untracked(() => this.loadSearchResults(criteria, searchKey));
    }
    return this.state.getItemsBySearchKey(searchKey);
  }

  private serializeCriteria(criteria: FeatureSearchCriteria): string {
    return JSON.stringify({
      fiscalYearId: criteria.fiscalYearId,
      type: criteria.type || null,
    });
  }

  async loadSearchResults(
    criteria: FeatureSearchCriteria,
    searchKey: string = '',
    refresh = false
  ): Promise<FeatureDTO[]> {
    if (!criteria.fiscalYearId) {
      throw new Error('Fiscal year must be provided');
    }
    if (!searchKey) {
      searchKey = this.serializeCriteria(criteria);
    }
    if (!refresh && this.state.searchResults.has(searchKey)) {
      return this.state.getItemsBySearchKey(searchKey)()!;
    }
    const response = await firstValueFrom(
      this.api.listItems(criteria.fiscalYearId, criteria.type || undefined)
    );
    this.state.setSearchResults(searchKey, response.items);
    return response.items;
  }

  /**
   * Invalidate all search caches (forces re-fetch on next access)
   */
  invalidateSearchCache(): void {
    this.state.clearSearchResults();
  }

  async create(dto: FeatureCreateDTO): Promise<FeatureDTO | null> {
    try {
      const result = await firstValueFrom(this.api.createItem(dto));
      this.state.itemEntities.set(result.id, result);
      this.state.clearSearchResults();
      this.notification.success('Luotu onnistuneesti');
      return result;
    } catch (error: any) {
      const message = error?.error?.detail?.message || 'Luonti epäonnistui';
      this.notification.error(message);
      return null;
    }
  }

  async update(id: string, dto: FeatureUpdateDTO): Promise<FeatureDTO | null> {
    try {
      const result = await firstValueFrom(this.api.updateItem(id, dto));
      this.state.itemEntities.set(result.id, result);
      this.notification.success('Päivitetty onnistuneesti');
      return result;
    } catch (error: any) {
      const message = error?.error?.detail?.message || 'Päivitys epäonnistui';
      this.notification.error(message);
      return null;
    }
  }

  async delete(id: string): Promise<boolean> {
    try {
      const response = await firstValueFrom(this.api.deleteItem(id));
      this.state.removeItem(id);
      this.notification.success(response.message);
      return true;
    } catch (error: any) {
      const message = error?.error?.detail?.message || 'Poisto epäonnistui';
      this.notification.error(message);
      return false;
    }
  }
}
```

## Simple List-Only Pattern

For simple resources that don't need normalized state:

```typescript
import { Injectable, inject, Signal, untracked } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { FeatureDTO, PrivateFeatureApiService } from '@api/index';
import { FeatureStateService } from './feature-state.service';
import { SharedNotificationService } from '@shared/index';

const ALL_KEY = 'all';

@Injectable({ providedIn: 'root' })
export class FeatureService {
  private readonly api = inject(PrivateFeatureApiService);
  private readonly state = inject(FeatureStateService);
  private readonly notification = inject(SharedNotificationService);

  getAll(): Signal<FeatureDTO[] | null> {
    const signal = this.state.itemsStore.get(ALL_KEY);
    if (signal() === null) {
      untracked(() => this.loadAll());
    }
    return signal;
  }

  isLoaded(): boolean {
    return this.state.itemsStore.isInitialized(ALL_KEY);
  }

  async loadAll(refresh = false): Promise<FeatureDTO[]> {
    if (!refresh && this.state.itemsStore.isInitialized(ALL_KEY)) {
      return this.state.itemsStore.get(ALL_KEY)() || [];
    }
    try {
      const response = await firstValueFrom(this.api.listItems());
      this.state.itemsStore.set(ALL_KEY, response.items);
      return response.items;
    } catch (error) {
      this.notification.error('Lataus epäonnistui');
      return [];
    }
  }

  async create(dto: FeatureCreateDTO): Promise<FeatureDTO | null> {
    try {
      const result = await firstValueFrom(this.api.createItem(dto));
      this.state.itemsStore.setItem(ALL_KEY, result);
      this.notification.success('Luotu onnistuneesti');
      return result;
    } catch (error: any) {
      const message = error?.error?.detail?.message || 'Luonti epäonnistui';
      this.notification.error(message);
      return null;
    }
  }
}
```
