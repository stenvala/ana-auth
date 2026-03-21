import { Injectable, inject, Signal, untracked } from "@angular/core";
import { firstValueFrom } from "rxjs";

import { FeatureApiService } from "@api/services";
import { FeatureDTO, FeatureListItemDTO, CreateDTO, UpdateDTO } from "@api/dto";
import { FeatureStateService } from "./feature-state.service";
import { CoreNotificationService } from "@core/services";

/**
 * Business service for feature operations.
 * Handles API integration and state management.
 */
@Injectable({ providedIn: "root" })
export class FeatureService {
  private api = inject(FeatureApiService);
  private state = inject(FeatureStateService);
  private notificationService = inject(CoreNotificationService);

  /**
   * Get items by key (e.g., parentId).
   * Returns signal from store - triggers load if null.
   */
  getItems(key: string): Signal<FeatureListItemDTO[] | null> {
    const signal = this.state.itemsStore.get(key);
    if (signal() === null) {
      untracked(() => this.loadItems(key));
    }
    return signal;
  }

  /**
   * Get single item by ID.
   * Returns signal from store - triggers load if null.
   */
  getItem(parentKey: string, id: string): Signal<FeatureDTO | null> {
    const signal = this.state.itemStore.get(id);
    if (signal() === null) {
      untracked(() => this.loadItem(parentKey, id));
    }
    return signal;
  }

  /**
   * Load items from API.
   * Returns the loaded data.
   */
  async loadItems(key: string, refresh = false): Promise<FeatureListItemDTO[]> {
    if (!refresh && this.state.itemsStore.isInitialized(key)) {
      return this.state.itemsStore.get(key)()!;
    }
    const response = await firstValueFrom(this.api.getItems(key));
    this.state.itemsStore.set(key, response.items);
    return response.items;
  }

  /**
   * Load single item from API.
   * Returns the loaded data.
   */
  async loadItem(parentKey: string, id: string, refresh = false): Promise<FeatureDTO> {
    if (!refresh && this.state.itemStore.isInitialized(id)) {
      return this.state.itemStore.get(id)()!;
    }
    const response = await firstValueFrom(this.api.getItem(parentKey, id));
    this.state.itemStore.set(id, response);
    return response;
  }

  /**
   * Create new item. Returns created item on success, null on failure.
   */
  async create(parentKey: string, data: CreateDTO): Promise<FeatureDTO | null> {
    try {
      const created = await firstValueFrom(this.api.create(parentKey, data));
      // Add to individual item store
      this.state.itemStore.set(created.id, created);
      // Add to list store
      const listItem: FeatureListItemDTO = {
        id: created.id,
        name: created.name,
        createdAt: created.createdAt,
        updatedAt: created.updatedAt,
      };
      this.state.itemsStore.setItem(parentKey, listItem);
      this.notificationService.showSuccess("Created successfully");
      return created;
    } catch (error) {
      this.notificationService.showError("Creation failed", (error as any).error?.message);
      return null;
    }
  }

  /**
   * Update existing item. Returns true on success.
   */
  async update(parentKey: string, id: string, data: UpdateDTO): Promise<boolean> {
    try {
      const updated = await firstValueFrom(this.api.update(parentKey, id, data));
      // Update individual item store
      this.state.itemStore.set(id, updated);
      // Update in list store
      const listItem: FeatureListItemDTO = {
        id: updated.id,
        name: updated.name,
        createdAt: updated.createdAt,
        updatedAt: updated.updatedAt,
      };
      this.state.itemsStore.setItem(parentKey, listItem);
      this.notificationService.showSuccess("Updated successfully");
      return true;
    } catch (error) {
      this.notificationService.showError("Update failed", (error as any).error?.message);
      return false;
    }
  }

  /**
   * Delete item. Returns true on success.
   */
  async delete(parentKey: string, id: string): Promise<boolean> {
    await firstValueFrom(this.api.delete(parentKey, id));
    // Remove from individual item store
    this.state.itemStore.remove(id);
    // Remove from list store
    this.state.itemsStore.removeItem(parentKey, id);
    this.notificationService.showSuccess("Deleted successfully");
    return true;
  }

  /**
   * Clear all cached data.
   */
  clearCache(): void {
    this.state.clearAll();
  }
}
