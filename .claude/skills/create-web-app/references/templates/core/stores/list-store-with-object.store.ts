import { Signal } from '@angular/core';
import { ListStore } from './list.store';
import { ObjectStore } from './object.store';

interface ObjectWithId {
  id: string;
}

export class ListStoreWithObject<T extends ObjectWithId, O> {
  private listData = new ListStore<T>();
  private objectData = new ObjectStore<O>();

  getAllKeys() {
    return this.listData.getAllKeys();
  }

  has(key: string): boolean {
    return this.listData.has(key);
  }

  isInitialized(key: string): boolean {
    return this.listData.isInitialized(key);
  }

  getList(key: string): Signal<T[] | null> {
    return this.listData.get(key);
  }

  getObject(key: string): Signal<O | null> {
    return this.objectData.get(key);
  }

  set(key: string, items: T[], object: O): void {
    this.listData.set(key, items);
    this.objectData.set(key, object);
  }

  append(key: string, additionalItems: T[], object?: O, sort?: (a: T, b: T) => number): void {
    if (!this.listData.has(key)) {
      throw new Error(`Key "${key}" does not exist. Use set() to create initial data.`);
    }
    const existingItems = this.listData.get(key)();
    if (!existingItems) {
      this.listData.set(key, additionalItems);
    } else {
      if (sort) {
        this.listData.set(key, [...existingItems, ...additionalItems].sort(sort));
      } else {
        this.listData.set(key, [...existingItems, ...additionalItems]);
      }
    }
    if (object) {
      this.objectData.set(key, object);
    }
  }

  remove(key: string): void {
    this.listData.remove(key);
    this.objectData.remove(key);
  }

  clear(): void {
    this.listData.clear();
    this.objectData.clear();
  }

  nullify(key: string): void {
    this.listData.nullify(key);
    this.objectData.nullify(key);
  }

  // Item methods (delegate to list)

  hasItem(key: string, id: string): boolean {
    return this.listData.hasItem(key, id);
  }

  getItem(key: string, id: string): Signal<T | null | undefined> {
    return this.listData.getItem(key, id);
  }

  setItem(key: string, item: T, object: O | null): void {
    this.listData.setItem(key, item);
    if (object !== null) {
      this.objectData.set(key, object);
    }
  }

  removeItem(key: string, id: string, object: O | null): void {
    this.listData.removeItem(key, id);
    if (object !== null) {
      this.objectData.set(key, object);
    }
  }
}
