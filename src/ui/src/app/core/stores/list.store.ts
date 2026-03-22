import { computed, Signal, signal, WritableSignal } from '@angular/core';

interface ObjectWithId {
  id: string;
}

export class ListStore<T extends ObjectWithId> {
  private data: Record<string, WritableSignal<T[] | null>> = {};

  getAllKeys() {
    return Object.keys(this.data);
  }

  has(key: string): boolean {
    return !!this.data[key];
  }

  isInitialized(key: string): boolean {
    return !!(this.data[key] && this.data[key]!());
  }

  get(key: string): Signal<T[] | null> {
    if (!this.data[key]) {
      this.data[key] = signal<T[] | null>(null);
    }
    return this.data[key]!.asReadonly();
  }

  set(key: string, value: T[]) {
    if (!this.data[key]) {
      this.data[key] = signal<T[] | null>(value);
    } else {
      this.data[key]!.set(value);
    }
  }

  remove(key: string) {
    delete this.data[key];
  }

  clear() {
    this.data = {};
  }

  nullify(key: string) {
    if (this.data[key]) {
      this.data[key]!.set(null);
    }
  }

  getInitializedKeys(): string[] {
    return Object.keys(this.data).filter((key) => this.isInitialized(key));
  }

  // Item methods

  hasItem(key: string, id: string): boolean {
    if (!this.data[key]) {
      return false;
    }
    return !!(this.data[key]!() || []).find((item) => item.id == id);
  }

  getItem(key: string, id: string): Signal<T | null | undefined> {
    if (!this.data[key]) {
      this.data[key] = signal<T[] | null>(null);
    }
    return computed(() => {
      const value = this.data[key]();
      if (!value) {
        return null;
      }
      return value.find((item) => item.id == id) ?? undefined;
    });
  }

  setItem(key: string, item: T) {
    if (!this.data[key]) {
      this.data[key] = signal<T[] | null>([]);
    }
    let items = this.data[key]();
    if (!items) {
      items = [];
    }
    const doesItemExist = items.find((i) => i.id == item.id);
    if (!doesItemExist) {
      this.data[key]!.set([...items, item]);
    } else {
      this.data[key]!.set(items.map((i) => (i.id == item.id ? item : i)));
    }
  }

  removeItem(key: string, id: string) {
    if (!this.data[key]) {
      this.data[key] = signal<T[] | null>(null);
    }
    let items = this.data[key]();
    if (!items) {
      items = [];
    }
    const doesItemExist = items.find((i) => i.id == id);
    if (!doesItemExist) {
      return;
    }
    this.data[key]!.set(items.filter((i) => i.id != id));
  }
}
